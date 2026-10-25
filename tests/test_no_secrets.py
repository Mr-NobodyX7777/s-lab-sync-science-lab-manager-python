import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

LITERAL_SECRET = re.compile(r"""(?ix)
    (password|passwd|pwd|secret|token)\w*   # a name that suggests a secret
    ['"]?\s*[:=]\s*                          # followed by : or =
    ['"][^'"\s]+['"]                         # and a non-empty quoted literal
    """)


FIELD_DEFAULT = re.compile(r"""['"]password['"]\s*,\s*['"][^'"]*['"]\s*,\s*['"][^'"]+['"]""")


def _source_files():
    return sorted(ROOT.glob('*.py')) + sorted(ROOT.glob('*.bat'))


def test_there_are_source_files_to_scan():
    names = {p.name for p in _source_files()}
    assert {'main.py', 'db.py', 'theme.py'} <= names


def test_no_password_or_secret_is_hardcoded_in_the_source():
    problems = []
    for path in _source_files():
        for number, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
            if LITERAL_SECRET.search(line) or FIELD_DEFAULT.search(line):
                problems.append(f'{path.name}:{number}: {line.strip()}')
    assert problems == []


def test_saved_settings_files_are_never_committed():
    ignored = (ROOT / '.gitignore').read_text(encoding='utf-8').splitlines()
    for name in ('python_db.json', 'credentials.json', 'db.properties', '.labmanager/'):
        assert name in ignored
