import tkinter as tk

import pytest
from helpers import contrast

import theme

PAGES = ['Overview', 'Students', 'Teachers', 'Equipment', 'Chemicals', 'Experiments']


class FakeDB:
    def count(self, table):
        return 7

    def experiments_overview(self):
        return [
            {
                'title': 'Titration',
                'exp_date': '2026-09-20',
                'start_time': '10:00',
                'teacher_name': 'Dr. Rao',
                'status': 'Scheduled',
                'student_count': 2,
            }
        ]

    def fetch_all(self, table):
        rows = {
            'students': [
                {
                    'student_id': 1,
                    'name': 'Asha',
                    'class_grade': '11-B',
                    'roll_no': '14',
                    'phone': '99',
                }
            ],
            'teachers': [
                {'teacher_id': 1, 'name': 'Dr. Rao', 'subject': 'Chem', 'phone': '1', 'email': 'e'}
            ],
        }
        return rows.get(table, [])

    def fetch_one(self, table, pk, ident):
        return next((r for r in self.fetch_all(table) if r[pk] == ident), None)

    def student_ids_for_experiment(self, ident):
        return [1]


@pytest.fixture(scope='module')
def app():
    import main

    main.App.startup = lambda self: None
    try:
        window = main.App()
    except tk.TclError:
        pytest.skip('no display available (run under xvfb-run)')
    window.db = FakeDB()
    window.deiconify()
    yield window
    window.destroy()


def _walk(widget):
    yield widget
    for child in widget.winfo_children():
        yield from _walk(child)


def _rgb(widget, color):
    r, g, b = widget.winfo_rgb(color)
    return (r // 257, g // 257, b // 257)


def _invisible_text(root):
    problems = []
    for w in _walk(root):
        try:
            fg, bg, text = w.cget('fg'), w.cget('bg'), str(w.cget('text'))
        except tk.TclError:
            continue
        if not text.strip():
            continue
        ratio = contrast(_rgb(w, fg), _rgb(w, bg))
        if ratio < 2.0:
            problems.append(f'{w.winfo_class()} {text!r}: fg={fg} bg={bg} ({ratio:.2f}:1)')
    return problems


@pytest.mark.parametrize('dark', [False, True], ids=['light', 'dark'])
@pytest.mark.parametrize('page', PAGES)
def test_page_renders_with_no_invisible_text(app, dark, page):
    app.dark = dark
    app._style()
    app.active = page
    app.build_ui()
    app.update()
    p = theme.palette(dark)
    assert app.content.cget('bg') == p['app_bg']
    assert _invisible_text(app) == []


@pytest.mark.parametrize('dark', [False, True], ids=['light', 'dark'])
def test_dialogs_open_with_no_invisible_text(app, dark):
    app.dark = dark
    app._style()
    app.active = 'Students'
    app.build_ui()
    app.tree.selection_set('1')
    app.update()
    app.edit_record('Students')
    app.change_password()
    app.assign_students()
    app.update()
    dialogs = [w for w in app.winfo_children() if isinstance(w, tk.Toplevel)]
    assert len(dialogs) == 3
    for d in dialogs:
        assert _invisible_text(d) == []
        d.destroy()


def test_toggle_theme_round_trip(app):
    app.dark = False
    app._style()
    app.build_ui()
    app.toggle_theme()
    assert app.dark is True
    assert app.content.cget('bg') == theme.DARK['app_bg']
    app.toggle_theme()
    assert app.dark is False
    assert app.content.cget('bg') == theme.LIGHT['app_bg']


def _close_dialogs_later(app, milliseconds=4000):
    def close():
        for w in app.winfo_children():
            if isinstance(w, tk.Toplevel):
                w.destroy()

    app.after(milliseconds, close)


def _password_entry(dialog):
    return next(w for w in _walk(dialog) if w.winfo_class() == 'TEntry' and str(w.cget('show')))


def test_mysql_dialog_asks_for_the_password_and_never_prefills_it(app):
    seen = {}

    def probe():
        dialog = next(w for w in app.winfo_children() if isinstance(w, tk.Toplevel))
        entry = _password_entry(dialog)
        seen['value'] = entry.get()
        seen['focused'] = dialog.focus_get() is entry
        dialog.destroy()

    app.after(500, probe)
    _close_dialogs_later(app)
    assert app.db_setup_dialog() is None
    assert seen['value'] == ''
    assert seen['focused'] is True


def test_enter_key_connects_with_the_typed_password(app, monkeypatch):
    import main

    saved = []

    class FakeConnection:
        def __init__(self, cfg):
            self.cfg = cfg

        def test(self):
            pass

    monkeypatch.setattr(main, 'LabDatabase', FakeConnection)
    monkeypatch.setattr(main.ConfigStore, 'save', classmethod(lambda cls, cfg: saved.append(cfg)))

    def probe():
        dialog = next(w for w in app.winfo_children() if isinstance(w, tk.Toplevel))
        _password_entry(dialog).insert(0, 'typed-by-user')
        dialog.event_generate('<Return>')

    app.after(500, probe)
    _close_dialogs_later(app)
    cfg = app.db_setup_dialog()
    assert cfg is not None and cfg['password'] == 'typed-by-user'
    assert saved == [cfg]
