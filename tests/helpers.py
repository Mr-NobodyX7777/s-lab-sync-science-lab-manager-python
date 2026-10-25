def luminance(rgb):
    def channel(c):
        c = c / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = (channel(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(rgb_a, rgb_b):
    hi, lo = sorted((luminance(rgb_a), luminance(rgb_b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def hex_to_rgb(value):
    value = value.lstrip('#')
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))
