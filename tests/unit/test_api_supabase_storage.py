import json

import httpx
import pytest

from services.api.app.adapters.storage import StorageError, SupabaseStorage
from services.api.app.constants import SIGNED_URL_TTL_SECONDS

BASE_URL = "https://supabase.test"
STORAGE_URL = f"{BASE_URL}/storage/v1"
BUCKET = "bucket"
SERVICE_KEY = "service-key"


def build_storage(
    handler: httpx.MockTransport,
) -> SupabaseStorage:
    return SupabaseStorage(
        BASE_URL, SERVICE_KEY, BUCKET, httpx.Client(transport=handler)
    )


def recording_transport(
    response: httpx.Response, requests: list[httpx.Request]
) -> httpx.MockTransport:
    def handle(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return response

    return httpx.MockTransport(handle)


def test_upload_posts_bytes_with_content_type_and_credentials() -> None:
    requests: list[httpx.Request] = []
    storage = build_storage(recording_transport(httpx.Response(200, json={}), requests))

    storage.upload("pending/a.jpg", b"image-bytes", "image/jpeg")

    request = requests[0]
    assert request.method == "POST"
    assert str(request.url) == f"{STORAGE_URL}/object/{BUCKET}/pending/a.jpg"
    assert request.content == b"image-bytes"
    assert request.headers["content-type"] == "image/jpeg"
    assert request.headers["authorization"] == f"Bearer {SERVICE_KEY}"


def test_move_sends_bucket_and_both_keys() -> None:
    requests: list[httpx.Request] = []
    storage = build_storage(recording_transport(httpx.Response(200, json={}), requests))

    storage.move("pending/a.jpg", "reports/b.jpg")

    assert str(requests[0].url) == f"{STORAGE_URL}/object/move"
    assert json.loads(requests[0].content) == {
        "bucketId": BUCKET,
        "sourceKey": "pending/a.jpg",
        "destinationKey": "reports/b.jpg",
    }


def test_delete_uses_delete_method() -> None:
    requests: list[httpx.Request] = []
    storage = build_storage(recording_transport(httpx.Response(200, json={}), requests))

    storage.delete("pending/a.jpg")

    assert requests[0].method == "DELETE"
    assert str(requests[0].url) == f"{STORAGE_URL}/object/{BUCKET}/pending/a.jpg"


def test_signed_urls_are_absolute_and_failed_entries_are_skipped() -> None:
    requests: list[httpx.Request] = []
    response = httpx.Response(
        200,
        json=[
            {
                "path": "reports/a.jpg",
                "signedURL": f"/object/sign/{BUCKET}/reports/a.jpg?token=t",
            },
            {
                "path": "reports/missing.jpg",
                "signedURL": None,
                "error": "Object not found",
            },
        ],
    )
    storage = build_storage(recording_transport(response, requests))

    urls = storage.signed_urls(["reports/a.jpg", "reports/missing.jpg"])

    assert urls == {
        "reports/a.jpg": f"{STORAGE_URL}/object/sign/{BUCKET}/reports/a.jpg?token=t"
    }
    assert json.loads(requests[0].content) == {
        "expiresIn": SIGNED_URL_TTL_SECONDS,
        "paths": ["reports/a.jpg", "reports/missing.jpg"],
    }


def test_signed_urls_for_no_paths_makes_no_request() -> None:
    requests: list[httpx.Request] = []
    storage = build_storage(recording_transport(httpx.Response(200, json=[]), requests))

    assert storage.signed_urls([]) == {}
    assert requests == []


def test_error_response_raises_storage_error() -> None:
    requests: list[httpx.Request] = []
    storage = build_storage(
        recording_transport(httpx.Response(400, text="bad"), requests)
    )

    with pytest.raises(StorageError):
        storage.upload("pending/a.jpg", b"x", "image/jpeg")
