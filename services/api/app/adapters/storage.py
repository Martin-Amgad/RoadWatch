from collections.abc import Sequence

import httpx

from ..constants import SIGNED_URL_TTL_SECONDS

REQUEST_TIMEOUT_SECONDS = 30.0


class StorageError(RuntimeError):
    pass


class SupabaseStorage:
    def __init__(
        self,
        base_url: str,
        service_key: str,
        bucket: str,
        client: httpx.Client | None = None,
    ) -> None:
        self._storage_url = f"{base_url}/storage/v1"
        self._bucket = bucket
        self._client = client or httpx.Client(timeout=REQUEST_TIMEOUT_SECONDS)
        self._headers = {
            "Authorization": f"Bearer {service_key}",
            "apikey": service_key,
        }

    def upload(self, path: str, content: bytes, content_type: str) -> None:
        response = self._client.post(
            f"{self._storage_url}/object/{self._bucket}/{path}",
            content=content,
            headers={**self._headers, "Content-Type": content_type},
        )
        _raise_for_failure(response, f"upload {path}")

    def move(self, source_path: str, destination_path: str) -> None:
        response = self._client.post(
            f"{self._storage_url}/object/move",
            json={
                "bucketId": self._bucket,
                "sourceKey": source_path,
                "destinationKey": destination_path,
            },
            headers=self._headers,
        )
        _raise_for_failure(response, f"move {source_path} to {destination_path}")

    def delete(self, path: str) -> None:
        response = self._client.delete(
            f"{self._storage_url}/object/{self._bucket}/{path}",
            headers=self._headers,
        )
        _raise_for_failure(response, f"delete {path}")

    def signed_urls(self, paths: Sequence[str]) -> dict[str, str]:
        if not paths:
            return {}
        response = self._client.post(
            f"{self._storage_url}/object/sign/{self._bucket}",
            json={"expiresIn": SIGNED_URL_TTL_SECONDS, "paths": list(paths)},
            headers=self._headers,
        )
        _raise_for_failure(response, "sign urls")
        return {
            entry["path"]: f"{self._storage_url}{entry['signedURL']}"
            for entry in response.json()
            if entry.get("signedURL")
        }


def _raise_for_failure(response: httpx.Response, action: str) -> None:
    if response.is_error:
        raise StorageError(
            f"Storage {action} failed: {response.status_code} {response.text}"
        )
