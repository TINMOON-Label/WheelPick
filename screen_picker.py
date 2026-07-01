import tkinter as tk
import ctypes
from PIL import Image, ImageTk
import mss

CAPTURE_SIZE = 15   # region to grab around cursor
MAG_PX = 160        # magnifier canvas size

_user32 = ctypes.windll.user32

# GetSystemMetrics indices for the full virtual desktop (all monitors)
_SM_XVIRTUALSCREEN = 76
_SM_YVIRTUALSCREEN = 77
_SM_CXVIRTUALSCREEN = 78
_SM_CYVIRTUALSCREEN = 79


def _virtual_screen() -> tuple:
    return (
        _user32.GetSystemMetrics(_SM_XVIRTUALSCREEN),
        _user32.GetSystemMetrics(_SM_YVIRTUALSCREEN),
        _user32.GetSystemMetrics(_SM_CXVIRTUALSCREEN),
        _user32.GetSystemMetrics(_SM_CYVIRTUALSCREEN),
    )


def _force_above_taskbar(child_hwnd: int, x: int, y: int, w: int, h: int):
    """Push the overlay above every window, including the always-on-top taskbar."""
    try:
        GA_ROOT = 2
        hwnd = _user32.GetAncestor(child_hwnd, GA_ROOT) or child_hwnd
        HWND_TOPMOST = -1
        SWP_SHOWWINDOW = 0x0040
        _user32.SetWindowPos(hwnd, HWND_TOPMOST, x, y, w, h, SWP_SHOWWINDOW)
    except Exception:
        pass


class ScreenPicker:
    def __init__(self, root, callback):
        self.root = root
        self.callback = callback
        self._overlay = None
        self._mag_win = None
        self._mag_canvas = None
        self._preview = None
        self._hex_lbl = None
        self._sct = None

    def start(self):
        self._sct = mss.mss()

        # Near-transparent overlay covering the ENTIRE virtual desktop, forced
        # above the taskbar so any pixel (taskbar / other topmost apps) is pickable.
        vx, vy, vw, vh = _virtual_screen()
        self._overlay = tk.Toplevel(self.root)
        self._overlay.overrideredirect(True)
        self._overlay.attributes('-alpha', 0.01)
        self._overlay.attributes('-topmost', True)
        self._overlay.config(cursor='crosshair', bg='black')
        self._overlay.geometry(f'{vw}x{vh}+{vx}+{vy}')
        self._overlay.update_idletasks()
        _force_above_taskbar(self._overlay.winfo_id(), vx, vy, vw, vh)

        # Magnifier floating window
        self._mag_win = tk.Toplevel(self.root)
        self._mag_win.overrideredirect(True)
        self._mag_win.attributes('-topmost', True)

        outer = tk.Frame(self._mag_win, bg='#3a3a3a', padx=1, pady=1)
        outer.pack()
        inner = tk.Frame(outer, bg='#1e1e1e')
        inner.pack()

        self._mag_canvas = tk.Canvas(inner, width=MAG_PX, height=MAG_PX,
                                     highlightthickness=0, bg='#1e1e1e')
        self._mag_canvas.pack()

        bottom = tk.Frame(inner, bg='#1e1e1e', height=34)
        bottom.pack(fill='x')

        self._preview = tk.Label(bottom, width=3, bg='#ffffff')
        self._preview.pack(side='left', padx=(6, 4), pady=4, ipady=3)

        self._hex_lbl = tk.Label(bottom, text='#FFFFFF', bg='#1e1e1e',
                                 fg='white', font=('Consolas', 12))
        self._hex_lbl.pack(side='left')

        self._overlay.bind('<Motion>', self._on_motion)
        self._overlay.bind('<Button-1>', self._on_click)
        self._overlay.bind('<Button-3>', self._cancel)   # right-click cancels
        self._overlay.bind('<Escape>', self._cancel)
        self._overlay.focus_force()

    def _pixel_at(self, x: int, y: int) -> tuple:
        mon = {'top': y, 'left': x, 'width': 1, 'height': 1}
        shot = self._sct.grab(mon)
        b, g, r = shot.raw[0], shot.raw[1], shot.raw[2]
        return r, g, b

    def _region_at(self, x: int, y: int) -> Image.Image:
        half = CAPTURE_SIZE // 2
        mon = {
            'top': max(0, y - half),
            'left': max(0, x - half),
            'width': CAPTURE_SIZE,
            'height': CAPTURE_SIZE,
        }
        shot = self._sct.grab(mon)
        return Image.frombytes('RGB', shot.size, shot.bgra, 'raw', 'BGRX')

    def _on_motion(self, event):
        x, y = event.x_root, event.y_root
        try:
            r, g, b = self._pixel_at(x, y)
            region = self._region_at(x, y)

            scaled = region.resize((MAG_PX, MAG_PX), Image.NEAREST)
            photo = ImageTk.PhotoImage(scaled)
            self._mag_canvas.delete('all')
            self._mag_canvas.create_image(0, 0, anchor='nw', image=photo)
            self._mag_canvas._photo = photo  # prevent GC

            # Crosshair
            cx = cy = MAG_PX // 2
            cell = MAG_PX // CAPTURE_SIZE
            self._mag_canvas.create_line(cx, 0, cx, MAG_PX, fill='white', width=1)
            self._mag_canvas.create_line(0, cy, MAG_PX, cy, fill='white', width=1)
            self._mag_canvas.create_rectangle(
                cx - cell, cy - cell, cx + cell, cy + cell,
                outline='white', width=1
            )

            hex_str = f'#{r:02X}{g:02X}{b:02X}'
            self._preview.config(bg=hex_str)
            self._hex_lbl.config(text=hex_str)

            sw = self._overlay.winfo_screenwidth()
            sh = self._overlay.winfo_screenheight()
            win_w, win_h = MAG_PX + 4, MAG_PX + 32
            mx = x + 20 if x + 20 + win_w < sw else x - win_w - 10
            my = y + 20 if y + 20 + win_h < sh else y - win_h - 10
            self._mag_win.geometry(f'+{mx}+{my}')
        except Exception:
            pass

    def _on_click(self, event):
        x, y = event.x_root, event.y_root
        try:
            r, g, b = self._pixel_at(x, y)
        except Exception:
            r, g, b = 0, 0, 0
        self._cleanup()
        self.callback(r, g, b)

    def _cancel(self, event=None):
        self._cleanup()

    def _cleanup(self):
        if self._sct:
            self._sct.close()
            self._sct = None
        if self._mag_win:
            self._mag_win.destroy()
            self._mag_win = None
        if self._overlay:
            self._overlay.destroy()
            self._overlay = None
