import bcrypt

from src.application.shared.password_hasher import AbstractPasswordHasher


class BcryptPasswordHasher(AbstractPasswordHasher):
    def hash(self, plain: str) -> str:
        return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()

    def verify(self, plain: str, hashed: str) -> bool:
        return bcrypt.checkpw(plain.encode(), hashed.encode())
