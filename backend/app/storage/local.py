import os
import uuid
from pathlib import Path

from app.config import settings


class LocalStorage:
    def __init__(self, base_dir: str = settings.UPLOAD_DIR):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    async def save(self, filename: str, content: bytes) -> str:
        ext = Path(filename).suffix
        unique_name = f"{uuid.uuid4()}{ext}"
        file_path = self.base_dir / unique_name
        file_path.write_bytes(content)
        return str(file_path)

    def delete(self, file_path: str) -> None:
        p = Path(file_path)
        if p.exists():
            p.unlink()


storage = LocalStorage()
