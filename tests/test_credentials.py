import json

import pytest

import db


@pytest.fixture
def home(tmp_path, monkeypatch):
    monkeypatch.setenv('HOME', str(tmp_path))
    monkeypatch.setenv('USERPROFILE', str(tmp_path))
    return tmp_path


def test_defaults_when_no_file(home):
    assert db.CredentialStore.load() == {'user': 'Master', 'pass': '7777'}


def test_save_then_load(home):
    db.CredentialStore.save('admin', 's3cret')
    assert db.CredentialStore.load() == {'user': 'admin', 'pass': 's3cret'}


def test_corrupt_file_falls_back_to_default(home):
    path = db.CredentialStore.path()
    db.CredentialStore.save('admin', 'x')
    with open(path, 'w', encoding='utf-8') as f:
        f.write('{not json')
    assert db.CredentialStore.load() == db.DEFAULT_LOGIN


def test_file_missing_keys_falls_back_to_default(home):
    db.CredentialStore.save('admin', 'x')
    with open(db.CredentialStore.path(), 'w', encoding='utf-8') as f:
        json.dump({'user': 'only-user'}, f)
    assert db.CredentialStore.load() == db.DEFAULT_LOGIN


def test_default_login_is_not_mutated_by_callers(home):
    creds = db.CredentialStore.load()
    creds['user'] = 'changed'
    assert db.DEFAULT_LOGIN['user'] == 'Master'


def test_config_store_roundtrip(home):
    assert db.ConfigStore.load() is None
    cfg = {'host': 'h', 'port': '3307', 'user': 'u', 'password': 'p'}
    db.ConfigStore.save(cfg)
    assert db.ConfigStore.load() == cfg
