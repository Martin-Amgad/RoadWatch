import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]


def main():
    load_dotenv(ROOT / '.env')
    from infra.db.repository import RoadWatchRepository

    repo = RoadWatchRepository()
    with repo._connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT extname, extnamespace::regnamespace::text AS schema FROM pg_extension WHERE extname = 'postgis'")
            postgis = cursor.fetchone()
            cursor.execute('SELECT COUNT(*) AS count FROM public.reports')
            report_count = cursor.fetchone()['count']
            cursor.execute('SELECT COUNT(*) AS count FROM public.analyses')
            analysis_count = cursor.fetchone()['count']
            cursor.execute('SELECT COUNT(*) AS count FROM public.schema_migrations')
            migration_count = cursor.fetchone()['count']
    print('PostGIS:', postgis)
    print('Reports:', report_count)
    print('Analyses:', analysis_count)
    print('Migrations:', migration_count)
    nearby = repo.get_nearby_reports(
        float(os.getenv('DEMO_BASE_LAT', '30.0444')),
        float(os.getenv('DEMO_BASE_LON', '31.2357')),
        radius_m=3000,
    )
    print('Nearby example results:', len(nearby))
    print('Top priority reports:', len(repo.get_reports(limit=5)))
    print('Database connection and queries OK')


if __name__ == '__main__':
    import sys

    sys.path.insert(0, str(ROOT))
    main()
