import argparse
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]


def parse_time(raw):
    if not isinstance(raw, str):
        return None
    try:
        parsed = datetime.fromisoformat(raw.replace('Z', '+00:00'))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(timezone.utc)


def expired_paths(entries, now, max_age_hours=24):
    cutoff = now - timedelta(hours=max_age_hours)
    expired = []
    for item in entries:
        if not isinstance(item, dict):
            continue
        name = item.get('name')
        created = parse_time(item.get('created_at'))
        if not isinstance(name, str) or '/' in name or not name or created is None:
            continue
        if not item.get('id') or created >= cutoff:
            continue
        expired.append(f'pending/{name}')
    return expired


def list_pending(storage):
    all_items = []
    offset = 0
    while True:
        batch = storage.list(path='pending', options={
            'limit': 100,
            'offset': offset,
            'sortBy': {'column': 'name', 'order': 'asc'},
        })
        if not batch:
            break
        all_items.extend(batch)
        if len(batch) < 100:
            break
        offset += len(batch)
    return all_items


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    load_dotenv(ROOT / '.env')
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SECRET_KEY')
    bucket = os.getenv('SUPABASE_BUCKET', 'road-images')
    if not url or not key:
        raise SystemExit('SUPABASE_URL and SUPABASE_SECRET_KEY must be set')
    from supabase import create_client

    client = create_client(url, key)
    storage = client.storage.from_(bucket)
    objects = list_pending(storage)
    expired = expired_paths(objects, datetime.now(timezone.utc))
    print(f'Scanned {len(objects)} pending entries, found {len(expired)} older than 24 hours')
    for path in expired:
        print(path)
    if not args.apply:
        print('Dry run only. Use --apply to delete these objects.')
        return
    for start in range(0, len(expired), 100):
        storage.remove(expired[start:start + 100])
    print(f'Deleted {len(expired)} old pending images')


if __name__ == '__main__':
    main()
