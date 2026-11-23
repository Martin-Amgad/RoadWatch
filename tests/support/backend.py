from dataclasses import dataclass

from fastapi.testclient import TestClient

from services.api.app.services.report_service import ReportService
from tests.support.fakes import (
    FakeClusterer,
    FakeDetector,
    InMemoryRepository,
    InMemoryStorage,
)

STAFF_KEY = "test-staff-key"
DASHBOARD_ORIGIN = "https://dashboard.test"


@dataclass
class Backend:
    client: TestClient
    detector: FakeDetector
    clusterer: FakeClusterer
    storage: InMemoryStorage
    repository: InMemoryRepository
    report_service: ReportService

    @property
    def staff_headers(self) -> dict[str, str]:
        return {"X-API-Key": STAFF_KEY}
