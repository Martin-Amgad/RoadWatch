import pytest

from services.api.app.config import DEFAULT_MODEL_VERSION, ConfigError, Settings

COMPLETE_ENVIRONMENT = {
    "DATABASE_URL": "postgresql://db",
    "SUPABASE_URL": "https://project.supabase.co/",
    "SUPABASE_SERVICE_KEY": "service-key",
    "SUPABASE_BUCKET": "bucket",
    "STAFF_API_KEY": "staff-key",
    "DASHBOARD_ORIGIN": "https://dashboard.example/",
}


def test_missing_variables_are_listed_by_name() -> None:
    incomplete = {**COMPLETE_ENVIRONMENT}
    del incomplete["STAFF_API_KEY"]
    del incomplete["DATABASE_URL"]

    with pytest.raises(ConfigError) as error:
        Settings.from_env(incomplete)

    assert "DATABASE_URL" in str(error.value)
    assert "STAFF_API_KEY" in str(error.value)


def test_trailing_slashes_are_removed_from_urls() -> None:
    settings = Settings.from_env(COMPLETE_ENVIRONMENT)

    assert settings.supabase_url == "https://project.supabase.co"
    assert settings.dashboard_origin == "https://dashboard.example"


def test_model_version_defaults_when_unset() -> None:
    assert (
        Settings.from_env(COMPLETE_ENVIRONMENT).model_version == DEFAULT_MODEL_VERSION
    )


def test_model_version_is_read_when_set() -> None:
    settings = Settings.from_env(
        {**COMPLETE_ENVIRONMENT, "MODEL_VERSION": "yolov8n-r2"}
    )

    assert settings.model_version == "yolov8n-r2"
