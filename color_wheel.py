import tkinter as tk
from PIL import Image, ImageDraw, ImageTk
import numpy as np
import math
import colorsys

WHEEL_SIZE = 260
CENTER = WHEEL_SIZE // 2
OUTER_R = 118
INNER_R = 90
SQ_HALF = int(INNER_R / math.sqrt(2)) - 4  # largest square fitting inside inner circle


def _hsv_to_rgb_array(h: np.ndarray, s: np.ndarray, v: np.ndarray):
    """Vectorized HSV→RGB. All inputs 0-1 float32 arrays of same shape."""
    i = (h * 6).astype(np.int32) % 6
    f = h * 6 - np.floor(h * 6)
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)
    r = np.select([i==0, i==1, i==2, i==3, i==4, i==5], [v, q, p, p, t, v])
    g = np.select([i==0, i==1, i==2, i==3, i==4, i==5], [t, v, v, q, p, p])
    b = np.select([i==0, i==1, i==2, i==3, i==4, i==5], [p, p, t, v, v, q])
    return r, g, b


def _build_ring() -> tuple:
    """Pre-render hue ring. Returns (base_array, ring_mask)."""
    y_g, x_g = np.mgrid[0:WHEEL_SIZE, 0:WHEEL_SIZE].astype(np.float32)
    dx = x_g - CENTER
    dy = y_g - CENTER
    dist = np.sqrt(dx * dx + dy * dy)
    angle = np.arctan2(dy, dx)
    hue = ((angle / (2 * math.pi)) % 1.0).astype(np.float32)

    mask = (dist >= INNER_R) & (dist <= OUTER_R)

    base = np.full((WHEEL_SIZE, WHEEL_SIZE, 3), 38, dtype=np.uint8)  # 0x26 = window BG
    h_r = hue[mask]
    ones = np.ones_like(h_r)
    r, g, b = _hsv_to_rgb_array(h_r, ones, ones)
    base[mask] = np.stack([r, g, b], axis=1) * 255
    return base, mask


# Compute once at import time
_RING_BASE, _RING_MASK = _build_ring()

# Precompute pixel coordinates for SV square
_y_g_sq, _x_g_sq = np.mgrid[0:WHEEL_SIZE, 0:WHEEL_SIZE].astype(np.float32)
_dx_sq = _x_g_sq - CENTER
_dy_sq = _y_g_sq - CENTER
_SQ_MASK = (np.abs(_dx_sq) <= SQ_HALF) & (np.abs(_dy_sq) <= SQ_HALF)
_S_VALS = (((_x_g_sq[_SQ_MASK] - (CENTER - SQ_HALF)) / (2 * SQ_HALF))
           .clip(0, 1).astype(np.float32))
_V_VALS = ((1.0 - (_y_g_sq[_SQ_MASK] - (CENTER - SQ_HALF)) / (2 * SQ_HALF))
           .clip(0, 1).astype(np.float32))


def _build_sv_square(hue: float) -> np.ndarray:
    h_arr = np.full_like(_S_VALS, hue)
    r, g, b = _hsv_to_rgb_array(h_arr, _S_VALS, _V_VALS)
    rgb = np.stack([r, g, b], axis=1)
    return (rgb * 255).astype(np.uint8)


BG = '#262626'


class ColorWheel(tk.Frame):
    def __init__(self, parent, on_color_change=None, **kwargs):
        kwargs.setdefault('bg', BG)
        super().__init__(parent, **kwargs)
        self.on_color_change = on_color_change
        self.hue = 0.0
        self.sat = 1.0
        self.val = 1.0
        self._dragging = None
        self._photo = None

        self.canvas = tk.Canvas(self, width=WHEEL_SIZE, height=WHEEL_SIZE,
                                bg=BG, highlightthickness=0)
        self.canvas.pack(padx=10, pady=(10, 4))

        bottom = tk.Frame(self, bg=BG)
        bottom.pack(fill='x', padx=14, pady=(0, 10))

        self._preview = tk.Label(bottom, width=4, bg='#ffffff', relief='flat')
        self._preview.pack(side='left', ipady=7)

        self._hex_var = tk.StringVar(value='#FFFFFF')
        tk.Label(bottom, textvariable=self._hex_var, bg=BG, fg='white',
                 font=('Consolas', 11)).pack(side='left', padx=10)

        self.canvas.bind('<Button-1>', self._on_press)
        self.canvas.bind('<B1-Motion>', self._on_drag)
        self.canvas.bind('<ButtonRelease-1>', self._on_release)

        self._redraw()

    def set_color(self, r: int, g: int, b: int):
        h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        self.hue, self.sat, self.val = h, s, v
        self._redraw()

    def get_rgb(self) -> tuple:
        r, g, b = colorsys.hsv_to_rgb(self.hue, self.sat, self.val)
        return round(r * 255), round(g * 255), round(b * 255)

    def _redraw(self):
        arr = _RING_BASE.copy()
        arr[_SQ_MASK] = _build_sv_square(self.hue)

        img = Image.fromarray(arr, 'RGB')
        draw = ImageDraw.Draw(img)

        # Hue indicator on ring
        angle = self.hue * 2 * math.pi
        ring_r = (INNER_R + OUTER_R) / 2
        ix = int(CENTER + ring_r * math.cos(angle))
        iy = int(CENTER + ring_r * math.sin(angle))
        draw.ellipse([ix-8, iy-8, ix+8, iy+8], outline='white', width=2)
        draw.ellipse([ix-6, iy-6, ix+6, iy+6], outline='black', width=1)

        # SV indicator in square
        sx = int((CENTER - SQ_HALF) + self.sat * 2 * SQ_HALF)
        sy = int((CENTER - SQ_HALF) + (1 - self.val) * 2 * SQ_HALF)
        draw.ellipse([sx-7, sy-7, sx+7, sy+7], outline='white', width=2)
        draw.ellipse([sx-5, sy-5, sx+5, sy+5], outline='black', width=1)

        self._photo = ImageTk.PhotoImage(img)
        self.canvas.create_image(0, 0, anchor='nw', image=self._photo)

        r, g, b = self.get_rgb()
        hex_str = f'#{r:02X}{g:02X}{b:02X}'
        self._hex_var.set(hex_str)
        self._preview.config(bg=hex_str)

    def _on_press(self, event):
        dx = event.x - CENTER
        dy = event.y - CENTER
        dist = math.sqrt(dx * dx + dy * dy)
        if INNER_R <= dist <= OUTER_R:
            self._dragging = 'ring'
        elif abs(dx) <= SQ_HALF and abs(dy) <= SQ_HALF:
            self._dragging = 'square'
        self._update_from_pos(event.x, event.y)

    def _on_drag(self, event):
        self._update_from_pos(event.x, event.y)

    def _on_release(self, event):
        self._dragging = None
        if self.on_color_change:
            self.on_color_change(*self.get_rgb())

    def _update_from_pos(self, x: int, y: int):
        if self._dragging == 'ring':
            angle = math.atan2(y - CENTER, x - CENTER)
            self.hue = (angle / (2 * math.pi)) % 1.0
            self._redraw()
        elif self._dragging == 'square':
            self.sat = max(0.0, min(1.0, (x - (CENTER - SQ_HALF)) / (2 * SQ_HALF)))
            self.val = max(0.0, min(1.0, 1.0 - (y - (CENTER - SQ_HALF)) / (2 * SQ_HALF)))
            self._redraw()
