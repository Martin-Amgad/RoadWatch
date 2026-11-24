from uuid import uuid4

import pytest

from infra.db.repository import RoadWatchRepository


def test_missing_database_url(monkeypatch):
    monkeypatch.delenv('DATABASE_URL', raising=False)
    with pytest.raises(ValueError):
        RoadWatchRepository()


def test_invalid_report_uuid_rejected_before_connection():
    repo = RoadWatchRepository('postgresql://not-used')
    with pytest.raises(ValueError):
        repo.update_status('invalid-id', 'submitted')


def test_invalid_status_rejected_before_connection():
    repo = RoadWatchRepository('postgresql://not-used')
    with pytest.raises(ValueError):
        repo.update_status(uuid4(), 'wrong')


def test_invalid_cluster_ids_and_labels_rejected():
    repo = RoadWatchRepository('postgresql://not-used')
    uid = uuid4()
    with pytest.raises(ValueError):
        repo.bulk_update_clusters([(uid, 1), (uid, 2)])
    with pytest.raises(ValueError):
        repo.bulk_update_clusters([(uid, 'one')])


def test_invalid_get_reports_parameters_rejected():
    repo = RoadWatchRepository('postgresql://not-used')
    with pytest.raises(ValueError):
        repo.get_reports(limit=0)
    with pytest.raises(ValueError):
        repo.get_reports(status='archived')


def test_invalid_location_query_rejected():
    repo = RoadWatchRepository('postgresql://not-used')
    with pytest.raises(ValueError):
        repo.get_nearby_reports(999, 12)


def test_empty_cluster_update_is_noop():
    repo = RoadWatchRepository('postgresql://not-used')
    assert repo.bulk_update_clusters([]) == 0
