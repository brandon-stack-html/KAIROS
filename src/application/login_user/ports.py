"""Ports (driven interfaces) required by the login use case.

The application layer defines what it needs; infrastructure provides it.
"""
from abc import ABC, abstractmethod


class ITokenGenerator(ABC):
    """Port for generating authentication tokens.

    Infrastructure adapters (e.g. JwtTokenGenerator) implement this.
    The handler never imports jwt, jose, or any crypto library.
    """

    @abstractmethod
    def generate(self, user_id: str, email: str, tenant_id: str) -> str:
        """Return a signed, self-contained access token.

        tenant_id is embedded as the 'tid' JWT claim so downstream
        middleware and services can enforce tenant isolation without
        an extra DB lookup.
        """
        ...
