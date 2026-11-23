import json
import sys
from pathlib import Path

from .app_services import AppServices
from .config import Settings
from .main import create_app

PLACEHOLDER = "export-only"


def _services_are_not_built_for_export(_: Settings) -> AppServices:
    raise RuntimeError("OpenAPI export never starts the application.")


def build_openapi_schema() -> dict:
    settings = Settings(
        database_url=PLACEHOLDER,
        supabase_url=PLACEHOLDER,
        supabase_service_key=PLACEHOLDER,
        supabase_bucket=PLACEHOLDER,
        staff_api_key=PLACEHOLDER,
        dashboard_origin=PLACEHOLDER,
        model_version=PLACEHOLDER,
    )
    return create_app(settings, _services_are_not_built_for_export).openapi()


def main(output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(build_openapi_schema(), indent=2) + "\n")


if __name__ == "__main__":
    main(Path(sys.argv[1]))
