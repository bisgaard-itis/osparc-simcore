import logging
from pathlib import Path

import aiofiles
import httpx
from aiohttp.typedefs import StrOrURL
from aws_library.s3 import UploadID

from ..constants import MAX_CHUNK_SIZE, S3_UNDEFINED_OR_EXTERNAL_MULTIPART_ID
from ..models import FileMetaData, FileMetaDataAtDB

logger = logging.getLogger(__name__)


def convert_db_to_model(x: FileMetaDataAtDB) -> FileMetaData:
    model: FileMetaData = FileMetaData.model_validate(
        x.model_dump()
        | {
            "file_uuid": x.file_id,
            "file_name": x.file_id.split("/")[-1],
        }
    )
    return model


async def download_to_file_or_raise(
    session: httpx.AsyncClient,
    url: StrOrURL,
    destination_path: Path,
    *,
    chunk_size=MAX_CHUNK_SIZE,
) -> int:
    """
    Downloads content from url into destination_path

    Returns downloaded file size

    May raise aiohttp.ClientErrors:
     - aiohttp.ClientResponseError if not 2XX
     - aiohttp.ClientPayloadError while streaming chunks
    """
    # SEE Streaming API: https://docs.aiohttp.org/en/stable/streams.html

    dest_file = Path(destination_path)

    total_size = 0
    response = await session.get(f"{url}")
    response.raise_for_status()
    dest_file.parent.mkdir(parents=True, exist_ok=True)
    async with aiofiles.open(dest_file, mode="wb") as fh:
        async for chunk in response.aiter_bytes(chunk_size):
            await fh.write(chunk)
            total_size += len(chunk)

    return total_size


def is_file_entry_valid(file_metadata: FileMetaData | FileMetaDataAtDB) -> bool:
    """checks if the file_metadata is valid"""
    return (
        file_metadata.entity_tag is not None
        and file_metadata.file_size > 0
        and file_metadata.upload_id is None
        and file_metadata.upload_expires_at is None
    )


def is_valid_managed_multipart_upload(upload_id: UploadID | None) -> bool:
    """the upload ID is valid (created by storage service) AND internally managed by storage (e.g. PRESIGNED multipart upload)

    :type upload_id: Optional[UploadID]
    :rtype: bool
    """
    return upload_id is not None and upload_id != S3_UNDEFINED_OR_EXTERNAL_MULTIPART_ID
