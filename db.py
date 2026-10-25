# importing the necessary shit required for the database connection :) Mr.NobodyX7777
import json
import os

import mysql.connector

DB_NAME = 'lab_management'
ALLOWED_TABLES = {'students', 'teachers', 'equipment', 'chemicals', 'experiments'}
DEFAULT_LOGIN = {'user': 'Master', 'pass': '7777'}

SCHEMA = [
    """
    CREATE TABLE IF NOT EXISTS teachers (
        teacher_id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        subject VARCHAR(100),
        phone VARCHAR(20),
        email VARCHAR(100)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS students (
        student_id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        class_grade VARCHAR(30),
        roll_no VARCHAR(30),
        phone VARCHAR(20)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS equipment (
        equipment_id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(150) NOT NULL,
        category VARCHAR(100),
        quantity INT DEFAULT 0,
        location VARCHAR(150),
        condition_status VARCHAR(50),
        last_maintenance DATE
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS chemicals (
        chemical_id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(150) NOT NULL,
        formula VARCHAR(100),
        quantity DOUBLE DEFAULT 0,
        unit VARCHAR(20),
        location VARCHAR(150),
        expiry_date DATE,
        hazard_level VARCHAR(50)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS experiments (
        experiment_id INT AUTO_INCREMENT PRIMARY KEY,
        title VARCHAR(200) NOT NULL,
        description VARCHAR(500),
        exp_date DATE,
        start_time VARCHAR(20),
        end_time VARCHAR(20),
        teacher_id INT,
        status VARCHAR(30) DEFAULT 'Scheduled',
        color_hex VARCHAR(7) DEFAULT '#2EC4B6',
        FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id) ON DELETE SET NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS experiment_students (
        experiment_id INT NOT NULL,
        student_id INT NOT NULL,
        PRIMARY KEY (experiment_id, student_id),
        FOREIGN KEY (experiment_id) REFERENCES experiments(experiment_id) ON DELETE CASCADE,
        FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
    )
    """,
]

OVERVIEW_SQL = """
    SELECT e.title, e.exp_date, e.start_time, t.name AS teacher_name, e.status,
           (SELECT COUNT(*) FROM experiment_students es
             WHERE es.experiment_id = e.experiment_id) AS student_count
      FROM experiments e
      LEFT JOIN teachers t ON e.teacher_id = t.teacher_id
     ORDER BY e.exp_date DESC, e.experiment_id DESC
"""


class CredentialStore:
    """Stores and retrieves master login credentials"""

    @staticmethod
    def path():
        return os.path.join(os.path.expanduser('~'), '.labmanager', 'credentials.json')

    @classmethod
    def load(cls):
        try:
            with open(cls.path(), 'r', encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, dict) and data.get('user') and data.get('pass'):
                return data
        except (OSError, ValueError):
            pass
        return dict(DEFAULT_LOGIN)  # Default

    @classmethod
    def save(cls, user, password):
        p = cls.path()
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, 'w', encoding='utf-8') as f:
            json.dump({'user': user, 'pass': password}, f)
        try:
            os.chmod(p, 0o600)
        except OSError:
            pass


class ConfigStore:
    @staticmethod
    def path():
        return os.path.join(os.path.expanduser('~'), '.labmanager', 'python_db.json')

    @classmethod
    def load(cls):
        try:
            with open(cls.path(), 'r', encoding='utf-8') as f:
                return json.load(f)
        except (OSError, ValueError):
            return None

    @classmethod
    def save(cls, cfg):
        p = cls.path()
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, 'w', encoding='utf-8') as f:
            json.dump(cfg, f)
        try:
            os.chmod(p, 0o600)
        except OSError:
            pass


class LabDatabase:
    def __init__(self, cfg):
        self.cfg = {**cfg, 'port': int(cfg.get('port') or 3306)}

    @staticmethod
    def _require_table(table):
        if table not in ALLOWED_TABLES:
            raise ValueError('Invalid table')

    def connect(self, with_db=True):
        opts = {
            'host': self.cfg.get('host') or 'localhost',
            'port': self.cfg['port'],
            'user': self.cfg.get('user') or '',
            'password': self.cfg.get('password') or '',
            'connection_timeout': 8,
            'charset': 'utf8mb4',
            'use_unicode': True,
        }
        if with_db:
            opts['database'] = DB_NAME
        return mysql.connector.connect(**opts)

    def test(self):
        c = self.connect(False)
        c.close()

    def initialize(self):
        c = self.connect(False)
        cur = c.cursor()
        cur.execute(
            f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` "
            "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )
        cur.close()
        c.close()
        c = self.connect()
        cur = c.cursor()
        try:
            for sql in SCHEMA:
                cur.execute(sql)
            try:
                cur.execute(
                    "ALTER TABLE experiments ADD COLUMN color_hex VARCHAR(7) DEFAULT '#2EC4B6'"
                )
            except mysql.connector.Error as e:
                if e.errno != 1060:
                    raise
            c.commit()
        finally:
            cur.close()
            c.close()

    def count(self, table):
        self._require_table(table)
        c = self.connect()
        cur = c.cursor()
        try:
            cur.execute(f'SELECT COUNT(*) FROM `{table}`')
            return cur.fetchone()[0]
        finally:
            cur.close()
            c.close()

    def fetch_all(self, table):
        self._require_table(table)
        c = self.connect()
        cur = c.cursor(dictionary=True)
        try:
            cur.execute(f'SELECT * FROM `{table}` ORDER BY 1 DESC')
            return cur.fetchall()
        finally:
            cur.close()
            c.close()

    def fetch_one(self, table, pk, ident):
        self._require_table(table)
        c = self.connect()
        cur = c.cursor(dictionary=True)
        try:
            cur.execute(f'SELECT * FROM `{table}` WHERE `{pk}`=%s', (ident,))
            return cur.fetchone()
        finally:
            cur.close()
            c.close()

    def insert(self, table, data):
        self._require_table(table)
        if not data:
            raise ValueError('No data to save')
        keys = list(data)
        columns = ','.join(f'`{k}`' for k in keys)
        placeholders = ','.join(['%s'] * len(keys))
        sql = f'INSERT INTO `{table}` ({columns}) VALUES ({placeholders})'
        c = self.connect()
        cur = c.cursor()
        try:
            cur.execute(sql, [data[k] for k in keys])
            c.commit()
            return cur.lastrowid
        except Exception:
            c.rollback()
            raise
        finally:
            cur.close()
            c.close()

    def update(self, table, pk, ident, data):
        self._require_table(table)
        keys = list(data)
        assignments = ','.join(f'`{k}`=%s' for k in keys)
        sql = f'UPDATE `{table}` SET {assignments} WHERE `{pk}`=%s'
        c = self.connect()
        cur = c.cursor()
        try:
            cur.execute(sql, [data[k] for k in keys] + [ident])
            c.commit()
        except Exception:
            c.rollback()
            raise
        finally:
            cur.close()
            c.close()

    def delete(self, table, pk, ident):
        self._require_table(table)
        c = self.connect()
        cur = c.cursor()
        try:
            cur.execute(f'DELETE FROM `{table}` WHERE `{pk}`=%s', (ident,))
            c.commit()
        except Exception:
            c.rollback()
            raise
        finally:
            cur.close()
            c.close()

    def experiments_overview(self):
        c = self.connect()
        cur = c.cursor(dictionary=True)
        try:
            cur.execute(OVERVIEW_SQL)
            return cur.fetchall()
        finally:
            cur.close()
            c.close()

    def student_ids_for_experiment(self, ident):
        c = self.connect()
        cur = c.cursor()
        try:
            cur.execute(
                'SELECT student_id FROM experiment_students WHERE experiment_id=%s', (ident,)
            )
            return [r[0] for r in cur.fetchall()]
        finally:
            cur.close()
            c.close()

    def set_experiment_students(self, ident, ids):
        c = self.connect()
        cur = c.cursor()
        try:
            c.start_transaction()
            cur.execute('DELETE FROM experiment_students WHERE experiment_id=%s', (ident,))
            if ids:
                cur.executemany(
                    'INSERT INTO experiment_students(experiment_id,student_id) VALUES(%s,%s)',
                    [(ident, i) for i in ids],
                )
            c.commit()
        except Exception:
            c.rollback()
            raise
        finally:
            cur.close()
            c.close()
