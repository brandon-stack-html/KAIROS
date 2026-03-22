"""RefreshTokenHandler — use case / application service.

Implements token rotation inside a single UoW transaction:
  1. Look up the existing refresh token.
  2. Validate: not revoked, not expired.
  3. Fetch the user (for email claim in the new access token).
  4. Revoke the old refresh token.
  5. Issue a new access token + new refresh token.
  6. Persist the new refresh token.
  7. Commit — all in one atomic write.

Raises InvalidRefreshTokenError for any invalid state so the caller
never learns whether the token was unknown, revoked, or expired.
"""
from src.application.login_user.ports import ITokenGenerator
from src.application.refresh_token.command import RefreshTokenCommand
from src.application.register_user.ports import IUserUnitOfWork
from src.domain.shared.errors import InvalidRefreshTokenError
from src.domain.shared.refresh_token import RefreshToken
from src.infrastructure.config.settings import settings


class RefreshTokenHandler:
    def __init__(
        self,
        uow: IUserUnitOfWork,
        token_generator: ITokenGenerator,
    ) -> None:
        self._uow = uow
        self._token_generator = token_generator

    async def handle(self, command: RefreshTokenCommand) -> tuple[str, str]:
        """Return (new_access_token, new_refresh_token_uuid)."""
        async with self._uow:
            existing = await self._uow.refresh_tokens.find_by_token(command.token)

            if existing is None or existing.is_revoked or existing.is_expired():
                raise InvalidRefreshTokenError(
                    "Refresh token is invalid, revoked, or expired."
                )

            user = await self._uow.users.find_by_id(existing.user_id)
            if user is None:
                raise InvalidRefreshTokenError(
                    "User associated with refresh token no longer exists."
                )

            # Revoke old token (single-use rotation)
            await self._uow.refresh_tokens.save(existing.revoke())

            # Issue new refresh token
            new_refresh = RefreshToken.issue(
                user_id=existing.user_id,
                tenant_id=existing.tenant_id,
                ttl_days=settings.refresh_token_ttl_days,
            )
            await self._uow.refresh_tokens.save(new_refresh)

        # Generate new access token (no DB needed, pure crypto)
        access_token = self._token_generator.generate(
            user_id=user.id.value,
            email=user.email.value,
            tenant_id=existing.tenant_id.value,
        )

        return access_token, new_refresh.token
