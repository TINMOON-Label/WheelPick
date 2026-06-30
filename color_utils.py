import colorsys


def rgb_to_hex(r: int, g: int, b: int) -> str:
    return f"{r:02X}{g:02X}{b:02X}"


def hex_to_rgb(hex_str: str) -> tuple:
    hex_str = hex_str.lstrip('#')
    return int(hex_str[0:2], 16), int(hex_str[2:4], 16), int(hex_str[4:6], 16)


def rgb_to_hsl(r: int, g: int, b: int) -> tuple:
    h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
    return round(h * 360), round(s * 100), round(l * 100)


def rgb_to_hsv(r: int, g: int, b: int) -> tuple:
    return colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)


def hsv_to_rgb(h: float, s: float, v: float) -> tuple:
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return round(r * 255), round(g * 255), round(b * 255)


def format_color(r: int, g: int, b: int, fmt: str) -> str:
    if fmt == 'HEX':
        return f"#{rgb_to_hex(r, g, b)}"
    elif fmt == 'RGB':
        return f"rgb({r}, {g}, {b})"
    elif fmt == 'HSL':
        h, s, l = rgb_to_hsl(r, g, b)
        return f"hsl({h}, {s}%, {l}%)"
    return rgb_to_hex(r, g, b)
