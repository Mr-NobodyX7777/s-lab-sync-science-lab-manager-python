import os

import mysql.connector
import pytest

import db

pytestmark = pytest.mark.skipif(
    os.environ.get('SLAB_TEST_MYSQL') != '1',
    reason='set SLAB_TEST_MYSQL=1 and SLAB_TEST_MYSQL_* to test against a real MySQL server',
)

TEST_DB = 'lab_management_test'


def _cfg():
    return {
        'host': os.environ.get('SLAB_TEST_MYSQL_HOST', 'localhost'),
        'port': os.environ.get('SLAB_TEST_MYSQL_PORT', '3306'),
        'user': os.environ.get('SLAB_TEST_MYSQL_USER', 'root'),
        'password': os.environ.get('SLAB_TEST_MYSQL_PASSWORD', ''),
    }


def _drop_test_db(lab):
    conn = lab.connect(with_db=False)
    cur = conn.cursor()
    cur.execute(f'DROP DATABASE IF EXISTS `{TEST_DB}`')
    cur.close()
    conn.close()


@pytest.fixture
def lab(monkeypatch):
    monkeypatch.setattr(db, 'DB_NAME', TEST_DB)
    lab = db.LabDatabase(_cfg())
    _drop_test_db(lab)
    lab.initialize()
    yield lab
    _drop_test_db(lab)


def test_initialize_is_idempotent(lab):
    lab.initialize()
    lab.initialize()
    assert lab.count('students') == 0


def test_old_database_gets_color_hex_column(monkeypatch):
    monkeypatch.setattr(db, 'DB_NAME', TEST_DB)
    lab = db.LabDatabase(_cfg())
    _drop_test_db(lab)
    conn = lab.connect(with_db=False)
    cur = conn.cursor()
    cur.execute(f'CREATE DATABASE `{TEST_DB}`')
    cur.execute(f'USE `{TEST_DB}`')
    cur.execute(db.SCHEMA[0])
    cur.execute(
        'CREATE TABLE experiments (experiment_id INT AUTO_INCREMENT PRIMARY KEY,'
        ' title VARCHAR(200) NOT NULL, description VARCHAR(500), exp_date DATE,'
        ' start_time VARCHAR(20), end_time VARCHAR(20), teacher_id INT,'
        " status VARCHAR(30) DEFAULT 'Scheduled')"
    )
    conn.commit()
    cur.close()
    conn.close()
    try:
        lab.initialize()
        conn = lab.connect()
        cur = conn.cursor()
        cur.execute("SHOW COLUMNS FROM experiments LIKE 'color_hex'")
        assert cur.fetchone() is not None
        cur.close()
        conn.close()
    finally:
        _drop_test_db(lab)


def test_crud_roundtrip(lab):
    sid = lab.insert('students', {'name': 'Asha', 'class_grade': '11-B', 'roll_no': '14'})
    row = lab.fetch_one('students', 'student_id', sid)
    assert row['name'] == 'Asha' and row['class_grade'] == '11-B' and row['phone'] is None

    lab.update('students', 'student_id', sid, {'name': 'Asha K', 'phone': '123'})
    row = lab.fetch_one('students', 'student_id', sid)
    assert (row['name'], row['phone']) == ('Asha K', '123')

    lab.delete('students', 'student_id', sid)
    assert lab.fetch_one('students', 'student_id', sid) is None


def test_typed_columns_roundtrip(lab):
    eid = lab.insert(
        'equipment',
        {'name': 'Scope', 'quantity': 4, 'last_maintenance': '2026-05-01'},
    )
    cid = lab.insert('chemicals', {'name': 'HCl', 'quantity': 2.5, 'expiry_date': '2027-01-01'})
    assert lab.fetch_one('equipment', 'equipment_id', eid)['quantity'] == 4
    assert lab.fetch_one('chemicals', 'chemical_id', cid)['quantity'] == 2.5


def test_fetch_all_is_newest_first(lab):
    first = lab.insert('teachers', {'name': 'A'})
    second = lab.insert('teachers', {'name': 'B'})
    assert [r['teacher_id'] for r in lab.fetch_all('teachers')] == [second, first]
    assert lab.count('teachers') == 2


def test_values_with_sql_metacharacters_are_stored_literally(lab):
    nasty = "Robert'); DROP TABLE students;--"
    sid = lab.insert('students', {'name': nasty})
    assert lab.fetch_one('students', 'student_id', sid)['name'] == nasty
    assert lab.count('students') == 1


def test_student_assignment_replaces_and_overview_counts(lab):
    tid = lab.insert('teachers', {'name': 'Dr. Rao'})
    ids = [lab.insert('students', {'name': n}) for n in ('a', 'b', 'c')]
    eid = lab.insert(
        'experiments', {'title': 'Titration', 'teacher_id': tid, 'exp_date': '2026-09-20'}
    )

    lab.set_experiment_students(eid, ids)
    assert sorted(lab.student_ids_for_experiment(eid)) == sorted(ids)

    lab.set_experiment_students(eid, ids[:1])
    assert lab.student_ids_for_experiment(eid) == ids[:1]

    row = lab.experiments_overview()[0]
    assert row['title'] == 'Titration'
    assert row['teacher_name'] == 'Dr. Rao'
    assert row['student_count'] == 1

    lab.set_experiment_students(eid, [])
    assert lab.student_ids_for_experiment(eid) == []


def test_deleting_a_student_removes_their_assignment(lab):
    sid = lab.insert('students', {'name': 'a'})
    eid = lab.insert('experiments', {'title': 'E'})
    lab.set_experiment_students(eid, [sid])
    lab.delete('students', 'student_id', sid)
    assert lab.student_ids_for_experiment(eid) == []


def test_deleting_a_teacher_keeps_the_experiment(lab):
    tid = lab.insert('teachers', {'name': 'T'})
    eid = lab.insert('experiments', {'title': 'E', 'teacher_id': tid})
    lab.delete('teachers', 'teacher_id', tid)
    row = lab.fetch_one('experiments', 'experiment_id', eid)
    assert row is not None and row['teacher_id'] is None


def test_bad_values_are_rejected_and_nothing_is_saved(lab):
    with pytest.raises(mysql.connector.Error):
        lab.insert('equipment', {'name': 'x', 'last_maintenance': 'not-a-date'})
    assert lab.count('equipment') == 0


def test_wrong_password_fails_fast():
    bad = db.LabDatabase({**_cfg(), 'password': 'definitely-wrong-password'})
    with pytest.raises(mysql.connector.Error):
        bad.test()
