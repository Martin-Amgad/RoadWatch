import os
from collections.abc import Mapping
from dataclasses import dataclass

DEFAULT_MODEL_VERSION = "unversioned"

REQUIRED_VARIABLES = (
    "DATABASE_URL",
    "SUPABASE_URL",
    "SUPABASE_SERVICE_KEY",
    "SUPABASE_BUCKET",
    "STAFF_API_KEY",
    "DASHBOARD_ORIGIN",
)


class ConfigError(RuntimeError):
    pass


@dataclass(frozen=True)
class Settings:
    database_url: str
    supabase_url: str
    supabase_service_key: str
    supabase_bucket: str
    staff_api_key: str
    dashboard_origin: str
    model_version: str

    @classmethod
    def from_env(cls, environ: Mapping[str, str] | None = None) -> "Settings":
        env = os.environ if environ is None else environ
        missing = [name for name in REQUIRED_VARIABLES if not env.get(name)]
        if missing:
            raise ConfigError(f"Missing environment variables: {', '.join(missing)}")
        return cls(
            database_url=env["DATABASE_URL"],
            supabase_url=env["SUPABASE_URL"].rstrip("/"),
            supabase_service_key=env["SUPABASE_SERVICE_KEY"],
            supabase_bucket=env["SUPABASE_BUCKET"],
            staff_api_key=env["STAFF_API_KEY"],
            dashboard_origin=env["DASHBOARD_ORIGIN"].rstrip("/"),
            model_version=env.get("MODEL_VERSION") or DEFAULT_MODEL_VERSION,
        )
