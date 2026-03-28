from abc import ABC, abstractmethod


class IFileStorage(ABC):
    @abstractmethod
    async def save(self, file_content: bytes, filename: str) -> str:
        """Save file, return storage_path."""

    @abstractmethod
    async def delete(self, storage_path: str) -> None:
        """Delete file from storage."""
