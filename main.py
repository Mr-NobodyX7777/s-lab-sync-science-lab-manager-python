# S Lab Sync - Python Version
# This feels like it's a complete waste of time , since the java version does the same thing
# Eh well then this is a product of me being unemployed i guess ;) Mr.NobodyX7777
import tkinter as tk
import traceback
from datetime import date
from tkinter import colorchooser, messagebox, ttk

from db import ConfigStore, CredentialStore, LabDatabase
from theme import (
    ACCENT_BLUE,
    ACCENT_GREEN,
    ACCENT_ORANGE,
    ACCENT_PURPLE,
    ACCENT_RED,
    TEAL,
    apply_ttk_styles,
    palette,
)

_creds = CredentialStore.load()
MASTER_USER, MASTER_PASS = _creds['user'], _creds['pass']

TABLES = {
    'Students': {
        'table': 'students',
        'pk': 'student_id',
        'fields': [
            ('name', 'Name', 'text', True),
            ('class_grade', 'Class / Grade', 'text', False),
            ('roll_no', 'Roll No.', 'text', False),
            ('phone', 'Phone', 'text', False),
        ],
    },
    'Teachers': {
        'table': 'teachers',
        'pk': 'teacher_id',
        'fields': [
            ('name', 'Name', 'text', True),
            ('subject', 'Subject', 'text', False),
            ('phone', 'Phone', 'text', False),
            ('email', 'Email', 'text', False),
        ],
    },
    'Equipment': {
        'table': 'equipment',
        'pk': 'equipment_id',
        'fields': [
            ('name', 'Equipment name', 'text', True),
            ('category', 'Category', 'text', False),
            ('quantity', 'Quantity', 'int', False),
            ('location', 'Location', 'text', False),
            ('condition_status', 'Condition', 'text', False),
            ('last_maintenance', 'Last maintenance (YYYY-MM-DD)', 'date', False),
        ],
    },
    'Chemicals': {
        'table': 'chemicals',
        'pk': 'chemical_id',
        'fields': [
            ('name', 'Chemical name', 'text', True),
            ('formula', 'Formula', 'text', False),
            ('quantity', 'Quantity', 'float', False),
            ('unit', 'Unit', 'text', False),
            ('location', 'Location', 'text', False),
            ('expiry_date', 'Expiry date (YYYY-MM-DD)', 'date', False),
            ('hazard_level', 'Hazard level', 'text', False),
        ],
    },
    'Experiments': {
        'table': 'experiments',
        'pk': 'experiment_id',
        'fields': [
            ('title', 'Title', 'text', True),
            ('description', 'Description', 'text', False),
            ('exp_date', 'Date (YYYY-MM-DD)', 'date', False),
            ('start_time', 'Start time', 'text', False),
            ('end_time', 'End time', 'text', False),
            ('teacher_id', 'Teacher ID (optional)', 'int_optional', False),
            ('status', 'Status', 'text', False),
            ('color_hex', 'Color hex', 'text', False),
        ],
    },
}

PAGE_DESCRIPTIONS = {
    'Students': 'Manage student records and class details.',
    'Teachers': 'Manage teachers and contact details.',
    'Equipment': 'Track instruments, condition, maintenance, and location.',
    'Chemicals': 'Track chemical quantities, expiry dates, and hazard levels.',
    'Experiments': 'Schedule lab sessions and assign supervising teachers and students.',
}


# everything till now made sense, but here on out i'm also learning new things in python :) Mr.NobodyX7777
# let's hope it won't be really long :(
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('S Lab Sync | Science Lab Management')
        self.geometry('1240x760')
        self.minsize(1000, 620)
        self.db = None
        self.active = 'Overview'
        self.dark = False
        self._style()
        self.withdraw()
        self.after(100, self.startup)

    def _style(self):
        self.p = palette(self.dark)
        self.configure(bg=self.p['app_bg'])
        apply_ttk_styles(self, self.p)

    def _dialog(self, title, bg=None, transient=False):
        w = tk.Toplevel(self)
        w.title(title)
        w.configure(bg=bg or self.p['card_bg'])
        if transient:
            w.transient(self)
        else:
            w.resizable(False, False)
        w.grab_set()
        return w

    @staticmethod
    def _center(w):
        w.update_idletasks()
        x = (w.winfo_screenwidth() - w.winfo_width()) // 2
        y = (w.winfo_screenheight() - w.winfo_height()) // 2
        w.geometry(f'+{x}+{y}')

    def startup(self):
        cfg = ConfigStore.load()
        if not cfg:
            cfg = self.db_setup_dialog()
        if not cfg:
            self.destroy()
            return
        try:
            self.db = LabDatabase(cfg)
            self.db.initialize()
        except Exception as e:
            messagebox.showerror(
                'MySQL connection failed',
                f'Could not connect to MySQL or initialize tables.\n\n{e}\n\n'
                'Check that MySQL is running and that this account can create '
                'the lab_management database.',
            )
            cfg = self.db_setup_dialog()
            if not cfg:
                self.destroy()
                return
            try:
                self.db = LabDatabase(cfg)
                self.db.initialize()
            except Exception as e2:
                messagebox.showerror('Connection failed', str(e2))
                self.destroy()
                return
        self.deiconify()
        self.login()

    def db_setup_dialog(self):
        w = self._dialog('Connect to MySQL')
        box = ttk.Frame(w, padding=24, style='Card.TFrame')
        box.pack(fill='both', expand=True)
        ttk.Label(
            box, text='Connect to MySQL', font=('Segoe UI Semibold', 18), style='Card.TLabel'
        ).grid(row=0, column=0, columnspan=2, sticky='w', pady=(0, 4))
        ttk.Label(
            box,
            text='Database lab_management and its tables are created automatically.',
            style='Card.TLabel',
        ).grid(row=1, column=0, columnspan=2, sticky='w', pady=(0, 18))
        fields = {}
        rows = [
            ('host', 'Host', 'localhost'),
            ('port', 'Port', '3306'),
            ('user', 'MySQL username', 'root'),
            ('password', 'MySQL password', ''),
        ]
        for i, (key, label, default) in enumerate(rows, 2):
            ttk.Label(box, text=label, style='Card.TLabel').grid(
                row=i, column=0, sticky='w', pady=5
            )
            e = ttk.Entry(box, width=30, show='●' if key == 'password' else '')
            e.insert(0, default)
            e.grid(row=i, column=1, sticky='ew', pady=5)
            fields[key] = e
        remember = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            box,
            text='Remember connection on this computer',
            variable=remember,
            style='Card.TCheckbutton',
        ).grid(row=6, column=0, columnspan=2, sticky='w', pady=8)
        result = {'cfg': None}

        def connect():
            cfg = {k: v.get().strip() for k, v in fields.items()}
            cfg['password'] = fields['password'].get()
            try:
                test = LabDatabase(cfg)
                test.test()
                result['cfg'] = cfg
                if remember.get():
                    ConfigStore.save(cfg)
                w.destroy()
            except Exception as e:
                messagebox.showerror('Could not connect', str(e), parent=w)

        ttk.Button(box, text='Test & Connect', style='Accent.TButton', command=connect).grid(
            row=7, column=0, columnspan=2, sticky='ew', pady=(12, 0)
        )
        w.bind('<Return>', lambda event: connect())
        w.after(100, fields['password'].focus_force)
        self._center(w)
        w.wait_window()
        return result['cfg']

    # like i said earlier learning new things in python, but it's gettng out of hand now :( Mr.NobodyX7777
    def login(self):
        p = self.p
        w = self._dialog('S Lab Sync — Master Login', bg=p['sidebar_bg'])
        card = tk.Frame(w, bg=p['card_bg'], padx=48, pady=48)
        card.pack(padx=28, pady=28)
        header = tk.Frame(card, bg=p['card_bg'])
        header.pack(anchor='w', pady=(0, 28))
        tk.Label(header, text='🔬', font=('Segoe UI', 40), bg=p['card_bg'], fg=p['text']).pack(
            side='left', padx=(0, 12)
        )
        tk.Label(
            header,
            text='S LAB SYNC',
            font=('Segoe UI', 24, 'bold'),
            fg=p['text'],
            bg=p['card_bg'],
        ).pack(anchor='w')
        tk.Label(
            header,
            text='Science Lab Management System',
            font=('Segoe UI', 10),
            fg=p['muted'],
            bg=p['card_bg'],
        ).pack(anchor='w', pady=(4, 0))
        tk.Frame(card, bg=p['border'], height=1).pack(fill='x', pady=(0, 28))
        tk.Label(
            card, text='USERNAME', bg=p['card_bg'], fg=p['muted'], font=('Segoe UI', 9, 'bold')
        ).pack(anchor='w', pady=(0, 6))
        u = ttk.Entry(card, width=36)
        u.pack(pady=(0, 16), fill='x')
        u.insert(0, 'Master')
        tk.Label(
            card, text='PASSWORD', bg=p['card_bg'], fg=p['muted'], font=('Segoe UI', 9, 'bold')
        ).pack(anchor='w', pady=(0, 6))
        pw = ttk.Entry(card, width=36, show='●')
        pw.pack(pady=(0, 8), fill='x')
        status = tk.Label(card, text='', bg=p['card_bg'], fg=ACCENT_RED, font=('Segoe UI', 9))
        status.pack(anchor='w', pady=(0, 18))

        def check(event=None):
            if u.get().strip() == MASTER_USER and pw.get() == MASTER_PASS:
                w.destroy()
                self.build_ui()
            else:
                status.config(text='✗ Invalid username or password.')

        ttk.Button(card, text='🔓 UNLOCK DASHBOARD', style='Accent.TButton', command=check).pack(
            fill='x', pady=(18, 0)
        )
        pw.bind('<Return>', check)
        w.protocol('WM_DELETE_WINDOW', self.destroy)
        self._center(w)
        w.wait_window()

    def _nav_button(
        self, parent, text, command, fg, pady, gap=2, size=10, bold=False, active_fg=None
    ):
        p = self.p
        font = ('Segoe UI', size, 'bold') if bold else ('Segoe UI', size)
        b = tk.Button(
            parent,
            text=text,
            anchor='w',
            font=font,
            bg=p['sidebar_bg'],
            fg=fg,
            activebackground=p['sidebar_hover'],
            activeforeground=active_fg or TEAL,
            relief='flat',
            bd=0,
            padx=20,
            pady=pady,
            command=command,
            highlightthickness=0,
        )
        b.pack(fill='x', padx=8, pady=gap)
        return b

    def build_ui(self):
        p = self.p
        for x in self.winfo_children():
            if isinstance(x, (tk.Frame, ttk.Frame)):
                x.destroy()
        shell = tk.Frame(self, bg=p['app_bg'])
        shell.pack(fill='both', expand=True)
        nav = tk.Frame(shell, bg=p['sidebar_bg'], width=240)
        nav.pack(side='left', fill='y')
        nav.pack_propagate(False)
        tk.Label(nav, text='🔬', font=('Segoe UI', 28), bg=p['sidebar_bg'], fg=TEAL).pack(
            anchor='w', padx=22, pady=(24, 8)
        )
        tk.Label(
            nav,
            text='S LAB SYNC',
            bg=p['sidebar_bg'],
            fg=p['sidebar_text'],
            font=('Segoe UI', 16, 'bold'),
        ).pack(anchor='w', padx=22, pady=(0, 2))
        tk.Label(
            nav,
            text='Science Lab Management',
            bg=p['sidebar_bg'],
            fg=p['sidebar_sub'],
            font=('Segoe UI', 8),
        ).pack(anchor='w', padx=22, pady=(0, 24))
        tk.Frame(nav, bg=p['sidebar_divider'], height=1).pack(fill='x', padx=16, pady=(0, 12))
        self.content = tk.Frame(shell, bg=p['app_bg'])
        self.content.pack(side='left', fill='both', expand=True)
        nav_items = [
            ('📊 Overview', 'Overview'),
            ('👥 Students', 'Students'),
            ('👨‍🏫 Teachers', 'Teachers'),
            ('⚙️ Equipment', 'Equipment'),
            ('🧪 Chemicals', 'Chemicals'),
            ('🔬 Experiments', 'Experiments'),
        ]
        for icon_label, name in nav_items:
            self._nav_button(
                nav,
                icon_label,
                lambda n=name: self.show_page(n),
                p['sidebar_text'],
                pady=14,
                gap=3,
                size=11,
            )
        tk.Frame(nav, bg=p['sidebar_divider'], height=1).pack(fill='x', padx=16, pady=(16, 12))
        self._nav_button(
            nav,
            '☀  Light Mode' if self.dark else '🌙 Dark Mode',
            self.toggle_theme,
            p['sidebar_muted'],
            pady=10,
        )
        self._nav_button(
            nav, '🔐 Change Password', self.change_password, p['sidebar_muted'], pady=10
        )
        self._nav_button(nav, '🗄️ MySQL Settings', self.change_db, p['sidebar_muted'], pady=10)
        self._nav_button(
            nav,
            '🚪 Log Out',
            self.logout,
            '#E17055',
            pady=10,
            bold=True,
            active_fg='#FF6B6B',
        )
        self.show_page(self.active)

    def toggle_theme(self):
        self.dark = not self.dark
        self._style()
        self.build_ui()

    def change_password(self):
        """Dialog to change master username and password"""
        w = self._dialog('Change Master Password')
        box = ttk.Frame(w, padding=24, style='Card.TFrame')
        box.pack(fill='both', expand=True)
        ttk.Label(
            box, text='Change Master Login', font=('Segoe UI Semibold', 18), style='Card.TLabel'
        ).grid(row=0, column=0, columnspan=2, sticky='w', pady=(0, 18))
        ttk.Label(box, text='New Username', style='Card.TLabel').grid(
            row=1, column=0, sticky='w', pady=5
        )
        u = ttk.Entry(box, width=30)
        u.insert(0, MASTER_USER)
        u.grid(row=1, column=1, sticky='ew', pady=5)
        ttk.Label(box, text='New Password', style='Card.TLabel').grid(
            row=2, column=0, sticky='w', pady=5
        )
        pw = ttk.Entry(box, width=30, show='●')
        pw.grid(row=2, column=1, sticky='ew', pady=5)
        ttk.Label(box, text='Confirm Password', style='Card.TLabel').grid(
            row=3, column=0, sticky='w', pady=5
        )
        c = ttk.Entry(box, width=30, show='●')
        c.grid(row=3, column=1, sticky='ew', pady=5)
        status = tk.Label(box, text='', bg=self.p['card_bg'], fg=ACCENT_RED)
        status.grid(row=4, column=0, columnspan=2, sticky='w', pady=(12, 0))
        box.grid_columnconfigure(1, weight=1)

        def save_password():
            global MASTER_USER, MASTER_PASS
            user_new = u.get().strip()
            pass_new = pw.get()
            pass_conf = c.get()
            if not user_new or not pass_new:
                status.config(text='Username and password cannot be empty.')
                return
            if pass_new != pass_conf:
                status.config(text='Passwords do not match.')
                return
            if len(pass_new) < 4:
                status.config(text='Password must be at least 4 characters.')
                return
            try:
                CredentialStore.save(user_new, pass_new)
                MASTER_USER, MASTER_PASS = user_new, pass_new
                messagebox.showinfo(
                    'Success', 'Master login updated. You will need to log in again.', parent=w
                )
                w.destroy()
                self.logout()
            except Exception as e:
                status.config(text=f'Error: {str(e)}')

        ttk.Button(box, text='Update Password', style='Accent.TButton', command=save_password).grid(
            row=5, column=0, columnspan=2, sticky='ew', pady=(12, 0)
        )
        self._center(w)

    def change_db(self):
        cfg = self.db_setup_dialog()
        if cfg:
            try:
                db = LabDatabase(cfg)
                db.initialize()
                self.db = db
                messagebox.showinfo('Connected', 'MySQL connection updated.')
                self.show_page(self.active)
            except Exception as e:
                messagebox.showerror('Connection failed', str(e))

    def logout(self):
        for x in self.winfo_children():
            x.destroy()
        self.login()

    def show_page(self, name):
        self.active = name
        for x in self.content.winfo_children():
            x.destroy()
        if name == 'Overview':
            self.overview()
            return
        self.table_page(name)

    def page_header(self, title, subtitle):
        p = self.p
        head = tk.Frame(self.content, bg=p['app_bg'])
        head.pack(fill='x', padx=32, pady=(24, 16))
        top = tk.Frame(head, bg=p['app_bg'])
        top.pack(fill='x')
        tk.Label(top, text=title, font=('Segoe UI', 28, 'bold'), fg=p['text'], bg=p['app_bg']).pack(
            side='left', anchor='w'
        )
        status = tk.Label(
            top,
            text='✓ MYSQL CONNECTED',
            font=('Segoe UI', 9, 'bold'),
            fg=ACCENT_GREEN,
            bg=p['app_bg'],
        )
        status.pack(side='right', anchor='e', pady=6)
        tk.Label(head, text=subtitle, font=('Segoe UI', 11), fg=p['muted'], bg=p['app_bg']).pack(
            anchor='w', pady=(4, 0)
        )
        sep = tk.Frame(head, bg=TEAL, height=3)
        sep.pack(anchor='w', pady=(14, 0), padx=0)
        sep.config(width=64)

    def overview(self):
        p = self.p
        self.page_header('Lab Dashboard', 'A live snapshot of your science laboratory.')
        wrap = tk.Frame(self.content, bg=p['app_bg'])
        wrap.pack(fill='x', padx=28, pady=(8, 24))
        counts = []
        stats = [
            ('Students', 'students'),
            ('Teachers', 'teachers'),
            ('Equipment', 'equipment'),
            ('Chemicals', 'chemicals'),
            ('Experiments', 'experiments'),
        ]
        for title, table in stats:
            try:
                n = self.db.count(table)
            except Exception:
                n = '—'
            counts.append((title, n))

        icons = ['👥', '👨‍🏫', '⚙️', '🧪', '🔬']
        colors = [TEAL, ACCENT_BLUE, ACCENT_ORANGE, ACCENT_GREEN, ACCENT_PURPLE]

        for i, (title, n) in enumerate(counts):
            c = tk.Frame(
                wrap,
                bg=p['card_bg'],
                highlightbackground=p['border'],
                highlightthickness=1,
                padx=20,
                pady=18,
            )
            c.grid(row=0, column=i, sticky='nsew', padx=8)
            wrap.grid_columnconfigure(i, weight=1)
            # Color bar at top
            tk.Frame(c, bg=colors[i], height=5).pack(fill='x', pady=(0, 14))
            # Icon and title
            label_frame = tk.Frame(c, bg=p['card_bg'])
            label_frame.pack(anchor='w', pady=(0, 8))
            tk.Label(
                label_frame, text=icons[i], font=('Segoe UI', 18), bg=p['card_bg'], fg=p['text']
            ).pack(side='left', padx=(0, 6))
            tk.Label(
                label_frame,
                text=title.upper(),
                bg=p['card_bg'],
                fg=p['muted'],
                font=('Segoe UI', 8, 'bold'),
            ).pack(anchor='w')
            # Number
            tk.Label(
                c, text=str(n), bg=p['card_bg'], fg=p['text'], font=('Segoe UI', 32, 'bold')
            ).pack(anchor='w', pady=(6, 0))

        frame = tk.Frame(
            self.content, bg=p['card_bg'], highlightbackground=p['border'], highlightthickness=1
        )
        frame.pack(fill='both', expand=True, padx=28, pady=22)

        header_frame = tk.Frame(frame, bg=p['header_bg'])
        header_frame.pack(fill='x', padx=1, pady=1)
        tk.Label(
            header_frame,
            text='🔬 Upcoming / Recent Experiments',
            font=('Segoe UI', 14, 'bold'),
            bg=p['header_bg'],
            fg=p['text'],
        ).pack(anchor='w', padx=18, pady=12)
        cols = ('title', 'exp_date', 'start_time', 'teacher_name', 'status', 'student_count')
        tree = ttk.Treeview(frame, columns=cols, show='headings')
        labels = ['Experiment', 'Date', 'Start', 'Supervising teacher', 'Status', 'Students']
        widths = {'title': 200, 'teacher_name': 190}
        for col, label in zip(cols, labels):
            tree.heading(col, text=label)
            tree.column(col, width=widths.get(col, 130), anchor='w')
        tree.pack(fill='both', expand=True, padx=14, pady=(0, 14))
        try:
            for row in self.db.experiments_overview():
                tree.insert('', 'end', values=tuple(row.get(k, '') for k in cols))
        except Exception as e:
            messagebox.showerror('Database error', str(e))

    def table_page(self, name):
        p = self.p
        spec = TABLES[name]
        self.page_header(name, PAGE_DESCRIPTIONS[name])
        bar = tk.Frame(self.content, bg=p['app_bg'])
        bar.pack(fill='x', padx=28, pady=(0, 16))
        ttk.Button(
            bar, text='➕ Add New', style='Accent.TButton', command=lambda: self.edit_record(name)
        ).pack(side='left', padx=(0, 8))
        ttk.Button(
            bar,
            text='✏️ Edit Selected',
            style='Action.TButton',
            command=lambda: self.edit_selected(name),
        ).pack(side='left', padx=8)
        ttk.Button(
            bar,
            text='🗑️ Delete Selected',
            style='Danger.TButton',
            command=lambda: self.delete_selected(name),
        ).pack(side='left', padx=8)
        ttk.Button(bar, text='🔄 Refresh', command=lambda: self.refresh(name)).pack(side='right')
        if name == 'Experiments':
            ttk.Button(bar, text='Assign students', command=self.assign_students).pack(
                side='left', padx=8
            )
        area = tk.Frame(
            self.content, bg=p['card_bg'], highlightbackground=p['border'], highlightthickness=1
        )
        area.pack(fill='both', expand=True, padx=30, pady=(0, 24))
        cols = [spec['pk']] + [f[0] for f in spec['fields']]
        self.tree = ttk.Treeview(area, columns=cols, show='headings')
        self.tree._lab_cols = cols
        self.tree._lab_name = name
        headers = {spec['pk']: 'ID'}
        headers.update({f[0]: f[1].split(' (')[0] for f in spec['fields']})
        for c in cols:
            self.tree.heading(c, text=headers.get(c, c))
            self.tree.column(c, width=130, minwidth=80, anchor='w')
        sy = ttk.Scrollbar(area, orient='vertical', command=self.tree.yview)
        sx = ttk.Scrollbar(area, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)
        self.tree.grid(row=0, column=0, sticky='nsew')
        sy.grid(row=0, column=1, sticky='ns')
        sx.grid(row=1, column=0, sticky='ew')
        area.grid_rowconfigure(0, weight=1)
        area.grid_columnconfigure(0, weight=1)
        self.refresh(name)

    # This is getting too long for my comfort :) Mr.NobodyX7777
    def refresh(self, name):
        if not hasattr(self, 'tree') or getattr(self.tree, '_lab_name', None) != name:
            return
        for i in self.tree.get_children():
            self.tree.delete(i)
        spec = TABLES[name]
        try:
            rows = self.db.fetch_all(spec['table'])
            cols = self.tree._lab_cols
            for row in rows:
                self.tree.insert(
                    '',
                    'end',
                    iid=str(row[spec['pk']]),
                    values=[row.get(c, '') if row.get(c) is not None else '' for c in cols],
                )
        except Exception as e:
            messagebox.showerror('Could not load records', str(e))

    def selected_id(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning('Select a record', 'Please select a row first.')
            return None
        return int(sel[0])

    def edit_selected(self, name):
        ident = self.selected_id()
        if ident is None:
            return
        row = self.db.fetch_one(TABLES[name]['table'], TABLES[name]['pk'], ident)
        if row:
            self.edit_record(name, row)

    def edit_record(self, name, row=None):
        spec = TABLES[name]
        w = self._dialog(('Edit ' if row else 'Add ') + name.rstrip('s'), transient=True)
        outer = ttk.Frame(w, padding=22, style='Card.TFrame')
        outer.pack(fill='both', expand=True)
        ttk.Label(
            outer,
            text=('Edit record' if row else 'New record'),
            font=('Segoe UI Semibold', 17),
            style='Card.TLabel',
        ).grid(row=0, column=0, columnspan=2, sticky='w', pady=(0, 14))
        widgets = {}
        for i, (key, label, kind, required) in enumerate(spec['fields'], 1):
            ttk.Label(outer, text=label + (' *' if required else ''), style='Card.TLabel').grid(
                row=i, column=0, sticky='w', padx=(0, 18), pady=6
            )
            if key == 'status':
                v = tk.StringVar(value=(row or {}).get(key) or 'Scheduled')
                e = ttk.Combobox(
                    outer,
                    textvariable=v,
                    values=['Scheduled', 'In Progress', 'Completed', 'Cancelled'],
                    state='readonly',
                    width=32,
                )
                e.grid(row=i, column=1, sticky='ew', pady=6)
                widgets[key] = (e, v)
            elif key == 'color_hex':
                v = tk.StringVar(value=(row or {}).get(key) or '#2EC4B6')
                line = ttk.Frame(outer, style='Card.TFrame')
                line.grid(row=i, column=1, sticky='ew', pady=6)
                e = ttk.Entry(line, textvariable=v, width=24)
                e.pack(side='left', fill='x', expand=True)
                ttk.Button(line, text='Pick', command=lambda vv=v: self.pick_color(vv)).pack(
                    side='left', padx=5
                )
                widgets[key] = (e, v)
            else:
                e = ttk.Entry(outer, width=36)
                e.grid(row=i, column=1, sticky='ew', pady=6)
                val = (row or {}).get(key)
                e.insert(0, '' if val is None else str(val))
                widgets[key] = (e, None)
        outer.grid_columnconfigure(1, weight=1)

        def save():
            data = {}
            try:
                for key, label, kind, required in spec['fields']:
                    e, v = widgets[key]
                    value = (v.get() if v is not None else e.get()).strip()
                    if required and not value:
                        raise ValueError(label + ' is required.')
                    if value == '':
                        value = None
                    elif kind == 'int' or kind == 'int_optional':
                        value = int(value)
                    elif kind == 'float':
                        value = float(value)
                    elif kind == 'date':
                        if value:
                            date.fromisoformat(value)
                    data[key] = value
                if name == 'Experiments' and not data.get('color_hex'):
                    data['color_hex'] = '#2EC4B6'
                if row:
                    self.db.update(spec['table'], spec['pk'], row[spec['pk']], data)
                else:
                    self.db.insert(spec['table'], data)
                w.destroy()
                self.refresh(name)
            except Exception as e:
                messagebox.showerror('Check your entries', str(e), parent=w)

        ttk.Button(outer, text='Save record', style='Accent.TButton', command=save).grid(
            row=len(spec['fields']) + 1, column=0, columnspan=2, sticky='ew', pady=(16, 0)
        )
        self._center(w)

    def pick_color(self, var):
        c = colorchooser.askcolor(color=var.get(), title='Experiment color')
        if c and c[1]:
            var.set(c[1].upper())

    def delete_selected(self, name):
        ident = self.selected_id()
        if ident is None:
            return
        if not messagebox.askyesno(
            'Delete record', 'Delete the selected record? This cannot be undone.'
        ):
            return
        try:
            self.db.delete(TABLES[name]['table'], TABLES[name]['pk'], ident)
            self.refresh(name)
        except Exception as e:
            messagebox.showerror('Could not delete', str(e))

    def assign_students(self):
        ident = self.selected_id()
        if ident is None:
            return
        p = self.p
        w = self._dialog('Assign students to experiment', transient=True)
        outer = ttk.Frame(w, padding=20, style='Card.TFrame')
        outer.pack(fill='both', expand=True)
        ttk.Label(
            outer, text='Choose students', font=('Segoe UI Semibold', 16), style='Card.TLabel'
        ).pack(anchor='w')
        ttk.Label(
            outer, text='Use Ctrl or Shift to select multiple students.', style='Card.TLabel'
        ).pack(anchor='w', pady=(4, 10))
        students = self.db.fetch_all('students')
        current = set(self.db.student_ids_for_experiment(ident))
        lb = tk.Listbox(
            outer,
            selectmode='extended',
            width=55,
            height=18,
            exportselection=False,
            font=('Segoe UI', 10),
            bg=p['input_bg'],
            fg=p['text'],
            selectbackground=TEAL,
            selectforeground='white',
            highlightbackground=p['border'],
            relief='flat',
        )
        lb.pack(fill='both', expand=True)
        for s in students:
            lb.insert(
                'end',
                f"{s['student_id']}  |  {s['name']}  |  {s.get('class_grade') or ''}"
                f"  |  Roll: {s.get('roll_no') or ''}",
            )
        for i, s in enumerate(students):
            if s['student_id'] in current:
                lb.selection_set(i)

        def save():
            ids = [students[i]['student_id'] for i in lb.curselection()]
            try:
                self.db.set_experiment_students(ident, ids)
                w.destroy()
                self.refresh('Experiments')
                messagebox.showinfo('Saved', f'{len(ids)} student(s) assigned.')
            except Exception as e:
                messagebox.showerror('Could not assign students', str(e), parent=w)

        ttk.Button(
            outer, text='Save student assignments', style='Accent.TButton', command=save
        ).pack(fill='x', pady=(12, 0))


if __name__ == '__main__':
    try:
        App().mainloop()
    except Exception as exc:
        traceback.print_exc()
        messagebox.showerror('S Lab Sync error', str(exc))
# Yeah, i'm also as surprised as you are                                  _   _
# i Didn't think it would be so many lines of code, but it is what it is  O , O   Mr.NobodyX7777
#                                                                         \___/
