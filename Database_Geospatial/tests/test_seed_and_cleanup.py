from datetime import datetime, timedelta, timezone

from scripts.cleanup_pending import expired_paths, parse_time
from scripts.seed_reports import make_demo_rows


def test_seed_has_twenty_deterministic_reports():
    first = make_demo_rows()
    second = make_demo_rows()
    assert len(first) == 20
    assert [item['id'] for item in first] == [item['id'] for item in second]
    assert len({item['id'] for item in first}) == 20
    assert all(item['image_path'].startswith('reports/demo/') for item in first)
    assert all('SYNTHETIC DEMO' in item['description'] for item in first)


def test_parse_time():
    assert parse_time('2026-11-18T10:00:00Z').tzinfo == timezone.utc
    assert parse_time('not-date') is None
    assert parse_time(None) is None
    assert parse_time('2026-11-18T10:00:00') is None


def test_expired_paths_only_pending_old_files():
    now = datetime(2026, 11, 18, 12, tzinfo=timezone.utc)
    old = (now - timedelta(hours=25)).isoformat()
    recent = (now - timedelta(hours=3)).isoformat()
    found = expired_paths([
        {'id': 'a', 'name': 'one.png', 'created_at': old},
        {'id': 'b', 'name': 'two.png', 'created_at': recent},
        {'id': None, 'name': 'folder', 'created_at': old},
        {'id': 'c', 'name': '../reports/bad.png', 'created_at': old},
    ], now)
    assert found == ['pending/one.png']
