import httpx

from .adapters.ml import MlClusterer, MlDetector, MlSeverityScorer
from .adapters.postgres import PostgresRepository
from .adapters.storage import REQUEST_TIMEOUT_SECONDS, SupabaseStorage
from .app_services import AppServices
from .config import Settings
from .services.analysis_service import AnalysisService
from .services.report_service import ReportService


def build_production_services(settings: Settings) -> AppServices:
    detector = MlDetector(settings.model_version)
    severity_scorer = MlSeverityScorer()
    clusterer = MlClusterer()
    http_client = httpx.Client(timeout=REQUEST_TIMEOUT_SECONDS)
    storage = SupabaseStorage(
        settings.supabase_url,
        settings.supabase_service_key,
        settings.supabase_bucket,
        http_client,
    )
    repository = PostgresRepository.from_url(settings.database_url)

    def shutdown() -> None:
        http_client.close()
        repository.close()

    return AppServices(
        analysis_service=AnalysisService(
            detector, severity_scorer, storage, repository
        ),
        report_service=ReportService(repository, repository, storage, clusterer),
        detector=detector,
        shutdown=shutdown,
    )
