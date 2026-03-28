"""Local filesystem file storage adapter."""

import uuid
from pathlib import Path

from src.application.shared.file_storage import IFileStorage


class LocalFileStorage(IFileStorage):
    def __init__(self, upload_dir: str = "./uploads") -> None:
        self._upload_dir = Path(upload_dir)
        self._upload_dir.mkdir(parents=True, exist_ok=True)

    async def save(self, file_content: bytes, filename: str) -> str:
        unique_name = f"{uuid.uuid4()}_{filename}"
        file_path = self._upload_dir / unique_name
        file_path.write_bytes(file_content)
        return str(file_path)

    async def delete(self, storage_path: str) -> None:
        path = Path(storage_path)
        if path.exists():
            path.unlink()
