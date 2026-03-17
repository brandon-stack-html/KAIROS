"""JwtTokenGenerator — infrastructure adapter for ITokenGenerator.

Implements the application port using PyJWT.
The application layer never imports from this module.
"""
from datetime import datetime, timedelta, timezone

import jwt

from src.application.login_user.ports import ITokenGenerator
from src.infrastructure.config.settings import settings


class JwtTokenGenerator(ITokenGenerator):
    def generate(self, user_id: str, email: str) -> str:
        now = datetime.now(timezone.utc)
        payload = {
            "sub": user_id,
            "email": email,
            "iat": now,
            "exp": now + timedelta(minutes=settings.jwt_expire_minutes),
        }
        return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)
