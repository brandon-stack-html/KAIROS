"""In-memory file storage adapter — for tests only."""

import uuid

from src.application.shared.file_storage import IFileStorage


class InMemoryFileStorage(IFileStorage):
    """Stores files in-memory. Does NOT persist between instances."""

    def __init__(self) -> None:
        self._store: dict[str, bytes] = {}

    async def save(self, file_content: bytes, filename: str) -> str:
        storage_path = f"memory://{uuid.uuid4()}_{filename}"
        self._store[storage_path] = file_content
        return storage_path

    async def delete(self, storage_path: str) -> None:
        self._store.pop(storage_path, None)
