import logging
import os
import shutil
import uuid

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from ..models import FileMetadata

logger = logging.getLogger(__name__)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {".csv"}


def validate_upload_file(file: UploadFile) -> None:
    """Validate uploaded file before processing."""
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No file selected"
        )

    extension = os.path.splitext(file.filename)[1].lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File type not allowed. Only CSV files are supported",
        )

    if getattr(file, "size", None) and file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size exceeds maximum allowed size of 10MB",
        )


def save_file_to_disk(file: UploadFile) -> tuple[str, int]:
    """Persist uploaded file to disk and return its path and size."""
    extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_size = os.path.getsize(file_path)
    logger.debug("Saved upload %s (%s bytes)", unique_filename, file_size)
    return file_path, file_size


def save_file_metadata(
    db: Session,
    original_filename: str,
    file_path: str,
    file_size: int,
    user_id: int | None = None,
) -> FileMetadata:
    """Persist file metadata in the database."""
    file_metadata = FileMetadata(
        filename=original_filename,
        file_path=file_path,
        file_size=file_size,
        user_id=user_id,
    )
    db.add(file_metadata)
    db.commit()
    db.refresh(file_metadata)
    return file_metadata


def cleanup_file(file_path: str) -> None:
    """Remove a file from disk if it exists."""
    if file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
        except OSError as exc:
            logger.warning("Failed to remove temp file %s: %s", file_path, exc)






