"""File storage.

The only module that knows files live on a disk. Everything else deals
in opaque key strings, so swapping local disk for MinIO/S3 later means
rewriting this file and nothing else.
"""

import uuid

from src.core.config import UPLOAD_DIR

def save_bytes(data: bytes, extension: str) -> str:

    """Write bytes to storage under a randomly generated key.

    Called twice in the pipeline: once for the uploaded document
    (-> documents.storage_key) and once per rendered page image
    (-> pages.image_key).

    Args:
        data: Raw file contents.
        extension: File extension without the dot, e.g. "pdf".

    Returns:
        The storage key, e.g. "3f2b1a9c-...-c9.pdf". This is what goes
        in the database — never the absolute path.
    """

    if not data:
        raise ValueError("No data to save")
    if not extension:
        raise ValueError("No extension provided")
    if not isinstance(data, bytes):
        raise TypeError("Data must be bytes")
    if not isinstance(extension, str):
        raise TypeError("Extension must be a string")

    
    key = f"{uuid.uuid4()}.{extension}"
    (UPLOAD_DIR / key).write_bytes(data)
    return key


def get_path(key: str) -> str:
    """Where the file for this storage key lives on disk.

    Args:
        key: A storage key from the database, e.g. "3f2b1a9c-...-c9.pdf".

    Returns:
        The full path as a plain string, ready to open.
    """

    if not key:
        raise ValueError("No key provided")

    return str(UPLOAD_DIR / key)