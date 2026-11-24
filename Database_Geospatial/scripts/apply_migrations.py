import hashlib
import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
MIGRATIONS = ROOT / 'infra' / 'db' / 'migrations'


def main():
    load_dotenv(ROOT / '.env')
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        raise SystemExit('DATABASE_URL is missing. Copy .env.example to .env and fill it in.')
    files = sorted(MIGRATIONS.glob('*.sql'))
    if not files:
        raise SystemExit('No migration SQL files found')
    with psycopg.connect(
        database_url,
        sslmode=os.getenv('DB_SSLMODE', 'require'),
        connect_timeout=10,
        autocommit=True,
    ) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS public.schema_migrations (
                filename TEXT PRIMARY KEY,
                sha256 TEXT NOT NULL,
                applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
        ''')
        conn.execute('ALTER TABLE public.schema_migrations ENABLE ROW LEVEL SECURITY')
        conn.execute('REVOKE ALL ON TABLE public.schema_migrations FROM anon, authenticated')
        for path in files:
            content = path.read_text(encoding='utf-8')
            checksum = hashlib.sha256(content.encode('utf-8')).hexdigest()
            existing = conn.execute(
                'SELECT sha256 FROM public.schema_migrations WHERE filename = %s',
                (path.name,),
            ).fetchone()
            if existing:
                if existing[0] != checksum:
                    raise SystemExit(f'Migration changed after application: {path.name}')
                print(f'Already applied: {path.name}')
                continue
            with conn.transaction():
                conn.execute(content)
                conn.execute(
                    'INSERT INTO public.schema_migrations(filename, sha256) VALUES (%s, %s)',
                    (path.name, checksum),
                )
            print(f'Applied: {path.name}')
    print('Database migrations complete')


if __name__ == '__main__':
    main()
