from tkinter import ttk

# And yeah don't think i'm smart, the whole ui side of this program was mady by AI
# just like the java program :) Mr.NobodyX7777
TEAL = '#17A99A'
ACCENT_BLUE = '#4A90E2'
ACCENT_GREEN = '#47B881'
ACCENT_ORANGE = '#F59E42'
ACCENT_RED = '#E74C3C'
ACCENT_PURPLE = '#9B70C9'

LIGHT = {
    'app_bg': '#F5F7FA',
    'card_bg': '#FFFFFF',
    'input_bg': '#FFFFFF',
    'text': '#132238',
    'muted': '#5B6B80',
    'border': '#E1E8ED',
    'header_bg': '#EAF0F8',
    'select_bg': '#E0F8F4',
    'select_fg': '#132238',
    'btn_bg': '#E7EDF5',
    'btn_fg': '#132238',
    'btn_active': '#DCE5EF',
    'sidebar_bg': '#132238',
    'sidebar_hover': '#1F3A52',
    'sidebar_text': '#EAF0F8',
    'sidebar_muted': '#AFC1D7',
    'sidebar_sub': '#9EB1C9',
    'sidebar_divider': '#233040',
}

DARK = {
    'app_bg': '#111827',
    'card_bg': '#1F2937',
    'input_bg': '#0F172A',
    'text': '#F3F4F6',
    'muted': '#A7B4C8',
    'border': '#374151',
    'header_bg': '#263449',
    'select_bg': '#115E59',
    'select_fg': '#F3F4F6',
    'btn_bg': '#334155',
    'btn_fg': '#F3F4F6',
    'btn_active': '#475569',
    'sidebar_bg': '#0B1220',
    'sidebar_hover': '#1F3A52',
    'sidebar_text': '#F3F4F6',
    'sidebar_muted': '#CBD5E1',
    'sidebar_sub': '#A7B4C8',
    'sidebar_divider': '#233040',
}
# yeah I don't even know how the colour choosing option is getting spawned ha ha


def palette(dark):
    return DARK if dark else LIGHT


def apply_ttk_styles(root, p):
    s = ttk.Style(root)
    s.theme_use('clam')
    s.configure(
        'Treeview',
        background=p['card_bg'],
        fieldbackground=p['card_bg'],
        foreground=p['text'],
        rowheight=36,
        borderwidth=0,
        font=('Segoe UI', 10),
        relief='flat',
        bordercolor=p['border'],
        lightcolor=p['border'],
        darkcolor=p['border'],
    )
    s.configure(
        'Treeview.Heading',
        background=p['header_bg'],
        foreground=p['text'],
        font=('Segoe UI Semibold', 11),
        padding=12,
        relief='flat',
        borderwidth=0,
    )
    s.map(
        'Treeview',
        background=[('selected', p['select_bg'])],
        foreground=[('selected', p['select_fg'])],
    )
    s.map('Treeview.Heading', background=[('active', p['header_bg'])])
    s.configure(
        'TButton',
        font=('Segoe UI', 10),
        padding=(14, 10),
        relief='flat',
        borderwidth=0,
        background=p['btn_bg'],
        foreground=p['btn_fg'],
    )
    s.map('TButton', background=[('active', p['btn_active'])])
    s.configure('Accent.TButton', background=TEAL, foreground='white', borderwidth=0)
    s.map('Accent.TButton', background=[('active', '#128A80'), ('pressed', '#0D6B61')])
    s.configure('Action.TButton', background=ACCENT_GREEN, foreground='white', borderwidth=0)
    s.map('Action.TButton', background=[('active', '#3D9A6D')])
    s.configure('Danger.TButton', background=ACCENT_RED, foreground='white', borderwidth=0)
    s.map('Danger.TButton', background=[('active', '#C0392B')])
    s.configure('TFrame', background=p['app_bg'])
    s.configure('Card.TFrame', background=p['card_bg'])
    s.configure('TLabel', background=p['app_bg'], foreground=p['text'], font=('Segoe UI', 10))
    s.configure('Card.TLabel', background=p['card_bg'], foreground=p['text'], font=('Segoe UI', 10))
    s.configure(
        'Title.TLabel', background=p['app_bg'], foreground=p['text'], font=('Segoe UI Semibold', 20)
    )
    s.configure(
        'Subtitle.TLabel', background=p['app_bg'], foreground=p['muted'], font=('Segoe UI', 11)
    )
    s.configure('Card.TCheckbutton', background=p['card_bg'], foreground=p['text'])
    s.map('Card.TCheckbutton', background=[('active', p['card_bg'])])
    s.configure(
        'TEntry',
        padding=10,
        font=('Segoe UI', 10),
        fieldbackground=p['input_bg'],
        foreground=p['text'],
        insertcolor=p['text'],
        borderwidth=1,
        relief='solid',
        bordercolor=p['border'],
        lightcolor=p['border'],
        darkcolor=p['border'],
    )
    s.map(
        'TEntry',
        bordercolor=[('focus', TEAL)],
        lightcolor=[('focus', TEAL)],
        darkcolor=[('focus', TEAL)],
    )
    s.configure(
        'TCombobox',
        fieldbackground=p['input_bg'],
        background=p['btn_bg'],
        foreground=p['text'],
        arrowcolor=p['text'],
        bordercolor=p['border'],
        lightcolor=p['border'],
        darkcolor=p['border'],
        padding=6,
    )
    s.map(
        'TCombobox',
        fieldbackground=[('readonly', p['input_bg'])],
        foreground=[('readonly', p['text'])],
        selectbackground=[('readonly', p['input_bg'])],
        selectforeground=[('readonly', p['text'])],
    )
    for orient in ('Vertical', 'Horizontal'):
        s.configure(
            f'{orient}.TScrollbar',
            background=p['btn_bg'],
            troughcolor=p['app_bg'],
            arrowcolor=p['text'],
            bordercolor=p['border'],
            lightcolor=p['btn_bg'],
            darkcolor=p['btn_bg'],
        )
        s.map(
            f'{orient}.TScrollbar',
            background=[('active', p['btn_active']), ('!active', p['btn_bg'])],
        )
    root.option_add('*TCombobox*Listbox.background', p['input_bg'])
    root.option_add('*TCombobox*Listbox.foreground', p['text'])
    root.option_add('*TCombobox*Listbox.selectBackground', TEAL)
    root.option_add('*TCombobox*Listbox.selectForeground', 'white')


# Yeah i'm not gonna worry about this much
# I don't even want to know how this file works :( Mr.NobodyX7777
