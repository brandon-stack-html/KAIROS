"""JwtTokenGenerator — infrastructure adapter for ITokenGenerator.

Implements the application port using PyJWT.
The application layer never imports from this module.
"""
from datetime import UTC, datetime, timedelta

import jwt

from src.application.login_user.ports import ITokenGenerator
from src.infrastructure.config.settings import settings


class JwtTokenGenerator(ITokenGenerator):
    def generate(self, user_id: str, email: str, tenant_id: str) -> str:
        now = datetime.now(UTC)
        payload = {
            "sub": user_id,
            "email": email,
            "tid": tenant_id,  # tenant claim — read by TenantMiddleware
            "iat": now,
            "exp": now + timedelta(minutes=settings.jwt_expire_minutes),
        }
        return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict:
    """Decode and validate a JWT. Raises jwt.InvalidTokenError on failure."""
    return jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
