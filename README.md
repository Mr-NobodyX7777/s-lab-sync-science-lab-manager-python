# S Lab Sync — Python edition

![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB.svg)
![CI](https://github.com/Mr-NobodyX7777/s-lab-sync-science-lab-manager-python/actions/workflows/ci.yml/badge.svg)


<p align="center">
  <img src="assets/logo.png" alt="S Lab Sync logo" width="110">
</p>

A desktop application (Python + Tkinter + MySQL) for managing everything happening in a
school or college science lab: students, teachers, equipment, chemical inventory, and
experiments (who is doing what, supervised by which teacher, and when).

This is the Python version of S Lab Sync. It uses the same MySQL schema as the Java Swing
version, so both can work against the same `lab_management` database.

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Quick start (from source)](#quick-start-from-source)
- [Project layout](#project-layout)
- [Where settings are stored](#where-settings-are-stored)
- [Development](#development)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Dashboard** — live counts of students, teachers, equipment, chemicals and experiments,
  plus a table of experiments with their supervising teacher, status and student count.
- **Records for every area** — add, edit and delete students, teachers, equipment,
  chemicals and experiments, with input validation (required fields, numbers, dates).
- **Experiments** — assign a supervising teacher, set a colour, and assign any number of
  students to a session.
- **Light and dark mode** — one click in the sidebar; every screen and dialog follows the
  theme.
- **Zero-setup database** — creates the `lab_management` database and all tables on first
  run, and upgrades older databases that are missing the `color_hex` column.
- **Master login** — change the username and password from inside the app.
- **Remembered connection** — optionally saves the MySQL connection for the next launch.

## Requirements

| What | Why |
| --- | --- |
| Python 3.10 or newer (with Tkinter) | Runs the app. Tkinter is included with the python.org installers for Windows and macOS; on Linux install it separately (for example `sudo apt install python3-tk`). |
| A reachable MySQL server (5.7+/8.x) | Stores the data. Install locally or use a shared server. |
| A MySQL account that can `CREATE DATABASE` and create tables | Needed on first run only. |
| `mysql-connector-python` | Installed by `requirements.txt`. |

## Quick start (from source)

```bash
git clone https://github.com/Mr-NobodyX7777/s-lab-sync-science-lab-manager-python.git
cd REPO
pip install -r requirements.txt
python main.py
```

On Windows you can instead double-click `run_slab_sync.bat`. On macOS and Linux use `python3`,
ideally inside a virtual environment (`python3 -m venv .venv && source .venv/bin/activate`) because
newer systems refuse a plain `pip install`.

New to setting up Python or MySQL? Follow the step-by-step [Setup Guide](docs/Setup_Guide.pdf).

On first launch:

1. Enter the MySQL host, port, username and password and click **Test & Connect**.
2. Sign in with the default master login: **`Master`** / **`7777`**.
3. Change that login straight away via **Change Password** in the sidebar.

## Project layout

```
main.py                   the application: windows, dialogs, pages
db.py                     MySQL access (CRUD, schema creation) and local settings storage
theme.py                  light/dark colour palettes and ttk styling
tests/                    pytest suite (theme, credentials, database, UI smoke tests)
assets/                   the logo
docs/                     project report, setup guide and architecture diagram (PDF)
run_slab_sync.bat         starts the app from source on Windows
.github/workflows/ci.yml  lint + tests on every push and pull request
```

## Where settings are stored

Everything is kept in `~/.labmanager/` (your user profile folder):

| File | Contents |
| --- | --- |
| `python_db.json` | The saved MySQL connection (only if *Remember connection* is ticked) |
| `credentials.json` | The master username and password, after you change them |

> **Security note:** both files are plain JSON, so the MySQL password and the master password
> are readable by anyone who can read your user profile. The master login is a simple gate for
> a shared lab computer, not per-user authentication. Don't expose MySQL to the public
> internet; use a trusted LAN or VPN and a MySQL account with only the permissions it needs.

## Development

```bash
pip install -r requirements-dev.txt
ruff check .          # lint
black --check .       # formatting
pytest                # unit tests + UI smoke tests
```

The UI tests need a display. On Linux, run them under a virtual one:
`xvfb-run -a pytest`. They are skipped automatically when no display is available.

The database integration tests are skipped unless you point them at a MySQL server. They only
ever create and drop a separate `lab_management_test` database:

```bash
SLAB_TEST_MYSQL=1 SLAB_TEST_MYSQL_USER=root SLAB_TEST_MYSQL_PASSWORD=secret pytest
```

The suite includes colour-contrast checks and a "no invisible text" check that renders every
page and dialog in both themes, so theme regressions are caught automatically.

## Documentation

The [`docs/`](docs/) folder has more detail if you want it:

- **[Project Report](docs/Project_Report.pdf)** — what the app does, what it needs to run, its
  architecture, and what's good about it.
- **[Setup Guide](docs/Setup_Guide.pdf)** — a step-by-step walkthrough for getting a fresh
  machine ready to run the app (Python, MySQL, the driver), with troubleshooting.
- **[Architecture Diagram](docs/Architecture_Diagram.pdf)** — a schematic of how the app is put
  together, from launch to the MySQL database.

## Contributing

Contributions are welcome — see [CONTRIBUTING.md](CONTRIBUTING.md) for how to set up, run the
checks, and the general workflow.

## License


[MIT](LICENSE)
