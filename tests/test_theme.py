import pytest
from helpers import contrast, hex_to_rgb

import theme

TEXT_PAIRS = [
    ('text', 'app_bg'),
    ('text', 'card_bg'),
    ('text', 'input_bg'),
    ('muted', 'app_bg'),
    ('muted', 'card_bg'),
    ('text', 'header_bg'),
    ('select_fg', 'select_bg'),
    ('btn_fg', 'btn_bg'),
    ('sidebar_text', 'sidebar_bg'),
    ('sidebar_muted', 'sidebar_bg'),
    ('sidebar_sub', 'sidebar_bg'),
]


def test_palettes_define_the_same_keys():
    assert theme.LIGHT.keys() == theme.DARK.keys()


def test_palette_selector():
    assert theme.palette(False) is theme.LIGHT
    assert theme.palette(True) is theme.DARK


@pytest.mark.parametrize('name', ['LIGHT', 'DARK'])
@pytest.mark.parametrize('fg,bg', TEXT_PAIRS)
def test_text_is_readable(name, fg, bg):
    pal = getattr(theme, name)
    ratio = contrast(hex_to_rgb(pal[fg]), hex_to_rgb(pal[bg]))
    assert ratio >= 4.5, f'{name}: {fg} on {bg} is only {ratio:.2f}:1'


def test_dark_surfaces_are_actually_dark():
    for key in ('app_bg', 'card_bg', 'sidebar_bg', 'input_bg'):
        assert sum(hex_to_rgb(theme.DARK[key])) < 3 * 90
