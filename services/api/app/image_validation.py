import io
from dataclasses import dataclass

from fastapi import UploadFile
from PIL import Image

from .constants import ALLOWED_IMAGE_FORMATS, MAX_IMAGE_SIZE_BYTES
from .errors import ApiError, ErrorCode


@dataclass(frozen=True)
class ValidatedImage:
    content: bytes
    content_type: str
    extension: str
    width: int
    height: int


def read_upload_within_limit(upload: UploadFile) -> bytes:
    content = upload.file.read(MAX_IMAGE_SIZE_BYTES + 1)
    if len(content) > MAX_IMAGE_SIZE_BYTES:
        raise ApiError(
            ErrorCode.IMAGE_TOO_LARGE,
            f"Image exceeds the {MAX_IMAGE_SIZE_BYTES} byte limit.",
        )
    return content


def validate_image(content: bytes) -> ValidatedImage:
    try:
        with Image.open(io.BytesIO(content)) as image:
            image_format = image.format
            if image_format not in ALLOWED_IMAGE_FORMATS:
                raise ApiError(
                    ErrorCode.INVALID_IMAGE_TYPE,
                    f"Image format '{image_format}' is not allowed. Use JPEG or PNG.",
                )
            image.load()
            width, height = image.size
    except (OSError, ValueError, SyntaxError, Image.DecompressionBombError) as error:
        raise ApiError(
            ErrorCode.UNREADABLE_IMAGE, "Image is corrupt or cannot be decoded."
        ) from error

    content_type, extension = ALLOWED_IMAGE_FORMATS[image_format]
    return ValidatedImage(
        content=content,
        content_type=content_type,
        extension=extension,
        width=width,
        height=height,
    )
