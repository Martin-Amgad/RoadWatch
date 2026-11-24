import os
from collections.abc import Iterable
from uuid import UUID

from infra.db.validation import (
    validate_coordinates,
    validate_limit_offset,
    validate_radius,
    validate_severity,
    validate_status,
    validate_uuid,
)


class RoadWatchRepository:
    def __init__(self, database_url=None, sslmode=None):
        self.database_url = database_url or os.getenv('DATABASE_URL')
        self.sslmode = sslmode or os.getenv('DB_SSLMODE', 'require')
        if not self.database_url:
            raise ValueError('DATABASE_URL is required')

    def _connect(self):
        import psycopg
        from psycopg.rows import dict_row

        return psycopg.connect(
            self.database_url,
            sslmode=self.sslmode,
            connect_timeout=10,
            row_factory=dict_row,
        )

    def insert_report(
        self,
        *,
        image_path: str,
        latitude: float,
        longitude: float,
        detections: list[dict] | None = None,
        model_version: str = 'unknown',
        description: str | None = None,
        category: str | None = None,
        severity: str = 'none',
        severity_score: float | None = None,
        status: str = 'submitted',
        cluster_label: int | None = None,
    ) -> dict:
        from psycopg.types.json import Jsonb

        validate_coordinates(latitude, longitude)
        validate_severity(severity)
        validate_status(status)
        if not isinstance(image_path, str) or not image_path.startswith('reports/'):
            raise ValueError('image_path must start with reports/')
        if description is not None and len(description) > 1000:
            raise ValueError('description is too long')
        if category is not None and len(category) > 80:
            raise ValueError('category is too long')
        if detections is not None and not isinstance(detections, list):
            raise ValueError('detections must be a list')
        if not isinstance(model_version, str) or not model_version:
            raise ValueError('model_version must be a nonempty string')
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    '''
                    INSERT INTO public.reports (
                        image_path, latitude, longitude, description,
                        category, severity, severity_score, status, cluster_label
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id, image_path, latitude, longitude, description,
                              category, severity, severity_score, severity_rank,
                              status, cluster_label, created_at
                    ''',
                    (
                        image_path, latitude, longitude, description,
                        category, severity, severity_score, status, cluster_label,
                    ),
                )
                report = cursor.fetchone()
                cursor.execute(
                    '''
                    INSERT INTO public.analyses (report_id, detections, model_version)
                    VALUES (%s, %s, %s)
                    ''',
                    (report['id'], Jsonb(detections if detections is not None else []), model_version),
                )
                return report

    def get_report(self, report_id: str | UUID) -> dict | None:
        report_id = validate_uuid(report_id)
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    '''
                    SELECT r.id, r.image_path, r.latitude, r.longitude,
                           r.description, r.category, r.severity,
                           r.severity_score, r.severity_rank, r.status,
                           r.cluster_label, r.created_at,
                           a.detections, a.model_version
                    FROM public.reports r
                    LEFT JOIN public.analyses a ON a.report_id = r.id
                    WHERE r.id = %s
                    ''',
                    (report_id,),
                )
                return cursor.fetchone()

    def get_reports(
        self,
        *,
        status: str | None = None,
        category: str | None = None,
        cluster_label: int | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict]:
        validate_limit_offset(limit, offset)
        if status is not None:
            validate_status(status)
        query = '''
            SELECT r.id, r.image_path, r.latitude, r.longitude,
                   r.description, r.category, r.severity, r.severity_score,
                   r.severity_rank, r.status, r.cluster_label, r.created_at,
                   a.detections, a.model_version
            FROM public.reports r
            LEFT JOIN public.analyses a ON a.report_id = r.id
            WHERE 1 = 1
        '''
        params = []
        if status is not None:
            query += ' AND r.status = %s'
            params.append(status)
        if category is not None:
            query += ' AND r.category = %s'
            params.append(category)
        if cluster_label is not None:
            query += ' AND r.cluster_label = %s'
            params.append(cluster_label)
        query += ' ORDER BY r.severity_rank DESC, r.created_at DESC, r.id ASC LIMIT %s OFFSET %s'
        params.extend((limit, offset))
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()

    def update_status(self, report_id: str | UUID, status: str) -> dict | None:
        report_id = validate_uuid(report_id)
        validate_status(status)
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    '''
                    UPDATE public.reports
                    SET status = %s
                    WHERE id = %s
                    RETURNING id, status, created_at
                    ''',
                    (status, report_id),
                )
                return cursor.fetchone()

    def bulk_update_clusters(self, labels: Iterable[tuple[str | UUID, int | None]]) -> int:
        updates = list(labels)
        if not updates:
            return 0
        normalized = []
        seen = set()
        for report_id, label in updates:
            uid = validate_uuid(report_id)
            if uid in seen:
                raise ValueError('duplicate report id in cluster updates')
            seen.add(uid)
            if label is not None and (isinstance(label, bool) or not isinstance(label, int)):
                raise ValueError('cluster label must be an integer or None')
            normalized.append((label, uid))
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.executemany(
                    'UPDATE public.reports SET cluster_label = %s WHERE id = %s',
                    normalized,
                    returning=False,
                )
                return cursor.rowcount

    def get_nearby_reports(
        self,
        latitude: float,
        longitude: float,
        *,
        radius_m: float = 100,
        limit: int = 100,
    ) -> list[dict]:
        validate_coordinates(latitude, longitude)
        validate_radius(radius_m)
        validate_limit_offset(limit, 0)
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    '''
                    WITH center AS (
                        SELECT extensions.ST_SetSRID(
                            extensions.ST_MakePoint(%s, %s), 4326
                        )::extensions.geography AS point
                    )
                    SELECT r.id, r.latitude, r.longitude, r.category,
                           r.severity, r.status, r.cluster_label,
                           extensions.ST_Distance(r.location, center.point) AS distance_m
                    FROM public.reports r
                    CROSS JOIN center
                    WHERE extensions.ST_DWithin(r.location, center.point, %s)
                    ORDER BY distance_m ASC, r.id ASC
                    LIMIT %s
                    ''',
                    (longitude, latitude, radius_m, limit),
                )
                return cursor.fetchall()

    def get_cluster_groups(self) -> list[dict]:
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    '''
                    SELECT cluster_label, COUNT(*) AS report_count,
                           ARRAY_AGG(id ORDER BY created_at DESC) AS report_ids
                    FROM public.reports
                    WHERE cluster_label >= 0
                    GROUP BY cluster_label
                    HAVING COUNT(*) >= 2
                    ORDER BY report_count DESC, cluster_label ASC
                    ''',
                )
                return cursor.fetchall()
