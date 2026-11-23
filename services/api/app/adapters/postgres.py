from collections.abc import Mapping
from typing import Any
from uuid import UUID

from psycopg.rows import dict_row
from psycopg.types.json import Jsonb
from psycopg_pool import ConnectionPool

from ..detections import detections_from_json, detections_to_json
from ..domain import (
    Analysis,
    NewAnalysis,
    NewReport,
    Report,
    ReportCoordinate,
    ReportPage,
    ReportQuery,
    ReportStatus,
    SeverityLabel,
    SeverityResult,
)

POOL_MAX_SIZE = 5

LATITUDE_SQL = "ST_Y(location::geometry)"
LONGITUDE_SQL = "ST_X(location::geometry)"

REPORT_COLUMNS = (
    "id, created_at, updated_at, image_path, "
    f"{LATITUDE_SQL} AS latitude, {LONGITUDE_SQL} AS longitude, "
    "description, damage_category, confidence, detections, "
    "severity_label, severity_score, status, cluster_id"
)
ANALYSIS_COLUMNS = (
    "id, created_at, image_path, image_width, image_height, detections, "
    "damage_category, confidence, severity_label, severity_score"
)
REPORT_ORDER = "ORDER BY severity_score DESC, created_at DESC"


class PostgresRepository:
    """Implements AnalysisRepository and ReportRepository on PostgreSQL + PostGIS."""

    def __init__(self, pool: ConnectionPool) -> None:
        self._pool = pool

    @classmethod
    def from_url(cls, database_url: str) -> "PostgresRepository":
        pool = ConnectionPool(
            database_url,
            max_size=POOL_MAX_SIZE,
            kwargs={"row_factory": dict_row, "prepare_threshold": None},
            open=True,
        )
        return cls(pool)

    def close(self) -> None:
        self._pool.close()

    def save_analysis(self, analysis: NewAnalysis) -> Analysis:
        with self._pool.connection() as connection:
            row = connection.execute(
                f"""
                INSERT INTO analyses (id, image_path, image_width, image_height,
                    detections, damage_category, confidence,
                    severity_label, severity_score)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING {ANALYSIS_COLUMNS}
                """,
                (
                    analysis.id,
                    analysis.image_path,
                    analysis.image_width,
                    analysis.image_height,
                    Jsonb(detections_to_json(analysis.detections)),
                    analysis.damage_category,
                    analysis.confidence,
                    analysis.severity.label.value,
                    analysis.severity.score,
                ),
            ).fetchone()
        return _to_analysis(row)

    def get_analysis(self, analysis_id: UUID) -> Analysis | None:
        with self._pool.connection() as connection:
            row = connection.execute(
                f"SELECT {ANALYSIS_COLUMNS} FROM analyses WHERE id = %s",
                (analysis_id,),
            ).fetchone()
        return _to_analysis(row) if row else None

    def create_report(self, report: NewReport, consumed_analysis_id: UUID) -> Report:
        with self._pool.connection() as connection:
            row = connection.execute(
                f"""
                INSERT INTO reports (id, image_path, location, description,
                    damage_category, confidence, detections,
                    severity_label, severity_score)
                VALUES (%s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography,
                    %s, %s, %s, %s, %s, %s)
                RETURNING {REPORT_COLUMNS}
                """,
                (
                    report.id,
                    report.image_path,
                    report.longitude,
                    report.latitude,
                    report.description,
                    report.damage_category,
                    report.confidence,
                    Jsonb(detections_to_json(report.detections)),
                    report.severity_label.value,
                    report.severity_score,
                ),
            ).fetchone()
            connection.execute(
                "DELETE FROM analyses WHERE id = %s", (consumed_analysis_id,)
            )
        return _to_report(row)

    def list_reports(self, query: ReportQuery) -> ReportPage:
        where_sql, parameters = _build_filters(query)
        with self._pool.connection() as connection:
            total = connection.execute(
                f"SELECT count(*) AS total FROM reports {where_sql}", parameters
            ).fetchone()["total"]
            rows = connection.execute(
                f"""
                SELECT {REPORT_COLUMNS} FROM reports {where_sql}
                {REPORT_ORDER} LIMIT %s OFFSET %s
                """,
                [*parameters, query.limit, query.offset],
            ).fetchall()
        return ReportPage(
            items=[_to_report(row) for row in rows],
            total=total,
            limit=query.limit,
            offset=query.offset,
        )

    def get_report(self, report_id: UUID) -> Report | None:
        with self._pool.connection() as connection:
            row = connection.execute(
                f"SELECT {REPORT_COLUMNS} FROM reports WHERE id = %s", (report_id,)
            ).fetchone()
        return _to_report(row) if row else None

    def list_cluster_mates(
        self, cluster_id: int, excluding_report_id: UUID
    ) -> list[Report]:
        with self._pool.connection() as connection:
            rows = connection.execute(
                f"""
                SELECT {REPORT_COLUMNS} FROM reports
                WHERE cluster_id = %s AND id <> %s {REPORT_ORDER}
                """,
                (cluster_id, excluding_report_id),
            ).fetchall()
        return [_to_report(row) for row in rows]

    def update_status(self, report_id: UUID, status: ReportStatus) -> Report | None:
        with self._pool.connection() as connection:
            row = connection.execute(
                f"""
                UPDATE reports SET status = %s, updated_at = now()
                WHERE id = %s RETURNING {REPORT_COLUMNS}
                """,
                (status.value, report_id),
            ).fetchone()
        return _to_report(row) if row else None

    def get_all_report_coordinates(self) -> list[ReportCoordinate]:
        with self._pool.connection() as connection:
            rows = connection.execute(f"""
                SELECT id, {LATITUDE_SQL} AS latitude, {LONGITUDE_SQL} AS longitude
                FROM reports ORDER BY created_at, id
                """).fetchall()
        return [
            ReportCoordinate(
                report_id=row["id"],
                latitude=row["latitude"],
                longitude=row["longitude"],
            )
            for row in rows
        ]

    def write_cluster_labels(self, labels: Mapping[UUID, int | None]) -> None:
        parameters = [(label, report_id) for report_id, label in labels.items()]
        with self._pool.connection() as connection, connection.cursor() as cursor:
            cursor.executemany(
                "UPDATE reports SET cluster_id = %s WHERE id = %s", parameters
            )


def _build_filters(query: ReportQuery) -> tuple[str, list[Any]]:
    conditions: list[str] = []
    parameters: list[Any] = []
    if query.category is not None:
        conditions.append("damage_category = %s")
        parameters.append(query.category)
    if query.status is not None:
        conditions.append("status = %s")
        parameters.append(query.status.value)
    where_sql = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    return where_sql, parameters


def _to_analysis(row: Mapping[str, Any]) -> Analysis:
    return Analysis(
        id=row["id"],
        created_at=row["created_at"],
        image_path=row["image_path"],
        image_width=row["image_width"],
        image_height=row["image_height"],
        detections=detections_from_json(row["detections"]),
        damage_category=row["damage_category"],
        confidence=row["confidence"],
        severity=SeverityResult(
            label=SeverityLabel(row["severity_label"]), score=row["severity_score"]
        ),
    )


def _to_report(row: Mapping[str, Any]) -> Report:
    return Report(
        id=row["id"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
        image_path=row["image_path"],
        latitude=row["latitude"],
        longitude=row["longitude"],
        description=row["description"],
        damage_category=row["damage_category"],
        confidence=row["confidence"],
        detections=detections_from_json(row["detections"]),
        severity_label=SeverityLabel(row["severity_label"]),
        severity_score=row["severity_score"],
        status=ReportStatus(row["status"]),
        cluster_id=row["cluster_id"],
    )
