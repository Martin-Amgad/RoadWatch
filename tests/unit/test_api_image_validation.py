import pytest

from services.api.app.errors import ApiError, ErrorCode
from services.api.app.image_validation import validate_image
from tests.support.builders import make_image_bytes


def test_valid_jpeg_reports_type_and_dimensions() -> None:
    image = validate_image(make_image_bytes("JPEG", size=(80, 60)))

    assert (image.content_type, image.extension) == ("image/jpeg", "jpg")
    assert (image.width, image.height) == (80, 60)


def test_valid_png_reports_type_and_dimensions() -> None:
    image = validate_image(make_image_bytes("PNG", size=(30, 20)))

    assert (image.content_type, image.extension) == ("image/png", "png")
    assert (image.width, image.height) == (30, 20)


def test_decodable_but_disallowed_format_is_rejected_as_type() -> None:
    with pytest.raises(ApiError) as error:
        validate_image(make_image_bytes("GIF"))

    assert error.value.code == ErrorCode.INVALID_IMAGE_TYPE


def test_bytes_that_are_not_an_image_are_unreadable() -> None:
    with pytest.raises(ApiError) as error:
        validate_image(b"this is not an image")

    assert error.value.code == ErrorCode.UNREADABLE_IMAGE


def test_truncated_image_is_unreadable() -> None:
    complete = make_image_bytes("JPEG", size=(400, 400))

    with pytest.raises(ApiError) as error:
        validate_image(complete[: len(complete) // 2])

    assert error.value.code == ErrorCode.UNREADABLE_IMAGE
