from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from services.api.app.app_services import AppServices
from services.api.app.config import Settings
from services.api.app.main import create_app
from services.api.app.services.analysis_service import AnalysisService
from services.api.app.services.report_service import ReportService
from tests.support.backend import DASHBOARD_ORIGIN, STAFF_KEY, Backend
from tests.support.fakes import (
    FakeClusterer,
    FakeDetector,
    FakeSeverityScorer,
    InMemoryRepository,
    InMemoryStorage,
)


@pytest.fixture
def settings() -> Settings:
    return Settings(
        database_url="postgresql://unused",
        supabase_url="https://supabase.test",
        supabase_service_key="service-key",
        supabase_bucket="bucket",
        staff_api_key=STAFF_KEY,
        dashboard_origin=DASHBOARD_ORIGIN,
        model_version="test-model-1",
    )


@pytest.fixture
def backend(settings: Settings) -> Iterator[Backend]:
    detector = FakeDetector()
    clusterer = FakeClusterer()
    storage = InMemoryStorage()
    repository = InMemoryRepository()
    report_service = ReportService(repository, repository, storage, clusterer)
    services = AppServices(
        analysis_service=AnalysisService(
            detector, FakeSeverityScorer(), storage, repository
        ),
        report_service=report_service,
        detector=detector,
    )
    app = create_app(settings, lambda _: services)
    with TestClient(app, raise_server_exceptions=False) as client:
        yield Backend(client, detector, clusterer, storage, repository, report_service)
