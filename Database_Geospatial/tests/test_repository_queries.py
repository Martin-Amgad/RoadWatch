from uuid import uuid4

from infra.db.repository import RoadWatchRepository


class FakeCursor:
    def __init__(self):
        self.queries = []
        self.rowcount = 2

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def execute(self, sql, params=None):
        self.queries.append((sql, params))

    def executemany(self, sql, params, returning=False):
        self.queries.append((sql, params))

    def fetchall(self):
        return [{'id': 'demo'}]

    def fetchone(self):
        return {'id': 'demo'}


class FakeConnection:
    def __init__(self):
        self.cur = FakeCursor()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def cursor(self):
        return self.cur


def fake_repository():
    repository = RoadWatchRepository('postgresql://not-used')
    connection = FakeConnection()
    repository._connect = lambda: connection
    return repository, connection


def test_filters_are_bound_parameters_and_priority_sorted():
    repository, connection = fake_repository()
    result = repository.get_reports(
        status='submitted', category='D40', cluster_label=3, limit=20, offset=10
    )
    query, params = connection.cur.queries[0]
    assert result == [{'id': 'demo'}]
    assert 'ORDER BY r.severity_rank DESC, r.created_at DESC' in query
    assert 'r.category = %s' in query
    assert params == ['submitted', 'D40', 3, 20, 10]
    assert 'D40' not in query


def test_nearby_query_uses_longitude_first_and_meters():
    repository, connection = fake_repository()
    repository.get_nearby_reports(30.0444, 31.2357, radius_m=150, limit=5)
    query, params = connection.cur.queries[0]
    assert 'extensions.ST_DWithin' in query
    assert 'extensions.ST_Distance' in query
    assert params == (31.2357, 30.0444, 150, 5)


def test_cluster_writeback_uses_parameterized_values():
    repository, connection = fake_repository()
    first, second = uuid4(), uuid4()
    count = repository.bulk_update_clusters([(first, 9), (second, -1)])
    sql, params = connection.cur.queries[0]
    assert 'SET cluster_label = %s' in sql
    assert params == [(9, first), (-1, second)]
    assert count == 2
