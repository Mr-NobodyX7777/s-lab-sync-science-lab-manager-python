import pytest

import db


@pytest.fixture
def lab():
    return db.LabDatabase({})


@pytest.mark.parametrize(
    'call',
    [
        lambda d: d.count('users'),
        lambda d: d.fetch_all('users'),
        lambda d: d.fetch_one('users', 'id', 1),
        lambda d: d.insert('users', {'name': 'x'}),
        lambda d: d.update('users', 'id', 1, {'name': 'x'}),
        lambda d: d.delete('users', 'id', 1),
        lambda d: d.insert('students`; DROP TABLE students; --', {'name': 'x'}),
    ],
)
def test_unknown_tables_are_rejected_before_any_connection(lab, call):
    with pytest.raises(ValueError, match='Invalid table'):
        call(lab)


def test_insert_requires_data(lab):
    with pytest.raises(ValueError, match='No data'):
        lab.insert('students', {})


def test_port_defaults_and_coerces():
    assert db.LabDatabase({}).cfg['port'] == 3306
    assert db.LabDatabase({'port': '3307'}).cfg['port'] == 3307


def test_schema_covers_every_table():
    sql = ' '.join(db.SCHEMA)
    for table in (*db.ALLOWED_TABLES, 'experiment_students'):
        assert f'CREATE TABLE IF NOT EXISTS {table} ' in sql
