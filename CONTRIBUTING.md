# Contributing to S Lab Sync (Python edition)

Thanks for helping out! This is a small Tkinter + MySQL desktop app, so the workflow is simple.

## Set up

```bash
git clone <your fork>
cd <your fork>
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
python main.py
```

You need a MySQL server to run the app itself (see the README).

## Before you open a pull request

```bash
ruff check .
black --check .
pytest                            # Linux: xvfb-run -a pytest
```

If you changed anything that touches the database, also run the integration tests against a
throwaway MySQL server (they only create and drop `lab_management_test`):

```bash
SLAB_TEST_MYSQL=1 SLAB_TEST_MYSQL_USER=root SLAB_TEST_MYSQL_PASSWORD=secret pytest
```

## Guidelines

- **Colours live in `theme.py`.** Use the named palette entries (`p['text']`, `p['card_bg']`,
  ...) instead of hard-coded hex values, so every widget works in both light and dark mode.
  If you add a palette entry, add it to both `LIGHT` and `DARK`.
- **Schema changes go in `db.py`.** Add the table or column to `SCHEMA` and, for existing
  databases, a safe migration in `LabDatabase.initialize()`. Add a test for the migration.
- **Always use parameterised queries** for values, and the `ALLOWED_TABLES` whitelist for
  table names.
- Keep user-facing messages friendly: show failures in a message box rather than letting an
  exception escape to the console.
- Please don't commit personal settings from `~/.labmanager/`.

## Pull requests

Describe what changed and why, and mention how you tested it (for example: light and dark
mode, fresh database vs. existing database).
