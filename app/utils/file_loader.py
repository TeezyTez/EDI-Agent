from pathlib import Path

from fastapi import UploadFile


async def save_upload(file: UploadFile, destination: Path) -> Path:
    """Persist a FastAPI upload to disk and return its path."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    content = await file.read()
    destination.write_bytes(content)
    return destination
