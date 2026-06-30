import tkinter as tk
import json
import os
import ctypes
from color_utils import rgb_to_hex, rgb_to_hsl, format_color
from screen_picker import ScreenPicker
from color_wheel import ColorWheel
from settings import get_data_dir

BG   = '#262626'
BG2  = '#2f2f2f'
BG3  = '#383838'
FG   = '#ffffff'
FG2  = '#888888'
SEP  = '#3a3a3a'
BLUE = '#0078d4'
FONT      = ('Segoe UI', 10)
FONT_MONO = ('Consolas', 13)

HISTORY_FILE = os.path.join(get_data_dir(), 'history.json')
WINDOW_WIDTH = 370


def _apply_dark_titlebar(hwnd: int):
    """Dark title bar + close-only via Windows DWM & Win32 APIs."""
    user32 = ctypes.windll.user32

    # winfo_id() returns a child widget HWND; we need the actual top-level window
    GA_ROOT = 2
    root_hwnd = user32.GetAncestor(hwnd, GA_ROOT)
    if root_hwnd:
        hwnd = root_hwnd

    # Dark title bar (Windows 10 1903+, try both known attribute IDs)
    for attr in (20, 19):
        try:
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, attr,
                ctypes.byref(ctypes.c_int(1)), ctypes.sizeof(ctypes.c_int)
            )
        except Exception:
            pass

    # Remove minimize button
    try:
        GWL_STYLE       = -16
        WS_MINIMIZEBOX  = 0x00020000
        style = user32.GetWindowLongW(hwnd, GWL_STYLE)
        user32.SetWindowLongW(hwnd, GWL_STYLE, style & ~WS_MINIMIZEBOX)
        user32.SetWindowPos(hwnd, None, 0, 0, 0, 0, 0x0027)
    except Exception:
        pass


class PickerWindow(tk.Toplevel):
    def __init__(self, root, settings, on_hotkey_change=None):
        super().__init__(root)
        self.settings = settings
        self.on_hotkey_change = on_hotkey_change
        self.title('Color Picker')
        self.configure(bg=BG)
        self.resizable(False, False)
        self.protocol('WM_DELETE_WINDOW', self.withdraw)

        self._r, self._g, self._b = 100, 100, 100
        self._history: list = []
        self._wheel_open = False

        self._load_history()
        self._build()
        self._update_values()
        self._refresh_history()

        # Apply dark title bar + remove minimize after window is fully rendered
        self.bind('<Map>', lambda e: self.after(300, lambda: _apply_dark_titlebar(self.winfo_id())))

    # ── Build UI ────────────────────────────────────────────────────

    def _build(self):
        # ── Controls bar ──────────────────────────────────────────
        top = tk.Frame(self, bg=BG, padx=8, pady=7)
        top.pack(fill='x')

        self._pick_btn = tk.Button(
            top, text='✏  Pick', bg=BG3, fg=FG,
            font=FONT, relief='flat', padx=10, pady=4,
            activebackground='#484848', activeforeground=FG,
            cursor='hand2', command=self._start_pick
        )
        self._pick_btn.pack(side='left')

        self._hist_frame = tk.Frame(top, bg=BG)
        self._hist_frame.pack(side='left', padx=(8, 0))

        self._gear_btn = tk.Button(
            top, text='⚙', bg=BG, fg=FG2,
            font=('Segoe UI', 13), relief='flat', padx=4, pady=2,
            activebackground=BG2, activeforeground=FG,
            cursor='hand2', command=self._open_settings
        )
        self._gear_btn.pack(side='right')

        # ── Separator ─────────────────────────────────────────────
        tk.Frame(self, bg=SEP, height=1).pack(fill='x')

        # ── Color values ──────────────────────────────────────────
        vals = tk.Frame(self, bg=BG, padx=14, pady=10)
        vals.pack(fill='x')

        self._hex_var = tk.StringVar()
        self._rgb_var = tk.StringVar()
        self._hsl_var = tk.StringVar()

        for lbl, var in (('HEX', self._hex_var), ('RGB', self._rgb_var), ('HSL', self._hsl_var)):
            row = tk.Frame(vals, bg=BG, pady=5)
            row.pack(fill='x')
            tk.Label(row, text=lbl, bg=BG, fg=FG2, font=('Segoe UI', 10),
                     width=5, anchor='w').pack(side='left')
            tk.Label(row, textvariable=var, bg=BG, fg=FG,
                     font=FONT_MONO, anchor='w').pack(side='left', fill='x', expand=True)
            _v = var
            _is_hex = (lbl == 'HEX')
            tk.Button(
                row, text='⧉', bg=BG, fg=FG2, relief='flat',
                font=('Segoe UI', 13), padx=2,
                activebackground=BG2, activeforeground=FG,
                cursor='hand2',
                command=lambda v=_v, h=_is_hex: self._copy(f"#{v.get()}" if h else v.get())
            ).pack(side='right')

        # ── Accordion toggle ──────────────────────────────────────
        acc = tk.Frame(self, bg=BG, pady=2)
        acc.pack(fill='x')
        tk.Frame(acc, bg=SEP, height=1).pack(fill='x', padx=12)
        self._toggle_btn = tk.Button(
            acc, text='▼', bg=BG, fg=FG2, relief='flat',
            font=('Segoe UI', 8), padx=8, pady=2,
            activebackground=BG, activeforeground=FG,
            cursor='hand2', command=self._toggle_wheel
        )
        self._toggle_btn.pack()

        # ── Color wheel (hidden initially) ────────────────────────
        self._wheel_frame = tk.Frame(self, bg=BG)
        self._wheel = ColorWheel(self._wheel_frame, on_color_change=self._on_wheel_color)
        self._wheel.pack()

        self.update_idletasks()
        self.geometry(f'{WINDOW_WIDTH}x{self.winfo_reqheight()}')

    # ── History ─────────────────────────────────────────────────────

    def _refresh_history(self):
        for w in self._hist_frame.winfo_children():
            w.destroy()
        count = self.settings.history_count or 7
        items = list(reversed(self._history[-count:]))
        for i in range(count):
            if i < len(items):
                r, g, b = items[i]
                color = f'#{r:02X}{g:02X}{b:02X}'
                btn = tk.Button(
                    self._hist_frame, bg=color, width=2, height=1,
                    relief='flat', cursor='hand2', activebackground=color,
                    command=lambda c=(r, g, b): self._set_color(*c)
                )
                _Tooltip(btn, color)
            else:
                btn = tk.Button(
                    self._hist_frame, bg=BG3, width=2, height=1,
                    relief='flat', state='disabled'
                )
            btn.pack(side='left', padx=2)

    def _add_history(self, r: int, g: int, b: int):
        entry = (r, g, b)
        if entry in self._history:
            self._history.remove(entry)
        self._history.append(entry)
        max_h = self.settings.history_count or 7
        self._history = self._history[-max_h:]
        self._refresh_history()
        self._save_history()

    def _load_history(self):
        try:
            with open(HISTORY_FILE, 'r') as f:
                self._history = [tuple(c) for c in json.load(f)]
        except (FileNotFoundError, json.JSONDecodeError):
            self._history = []

    def _save_history(self):
        try:
            with open(HISTORY_FILE, 'w') as f:
                json.dump(self._history, f)
        except Exception:
            pass

    # ── Color ────────────────────────────────────────────────────────

    def _update_values(self):
        r, g, b = self._r, self._g, self._b
        h, s, l = rgb_to_hsl(r, g, b)
        self._hex_var.set(rgb_to_hex(r, g, b))
        self._rgb_var.set(f'rgb({r}, {g}, {b})')
        self._hsl_var.set(f'hsl({h}, {s}%, {l}%)')

    def _set_color(self, r: int, g: int, b: int, add_history=True):
        self._r, self._g, self._b = r, g, b
        self._update_values()
        if self._wheel_open:
            self._wheel.set_color(r, g, b)
        if add_history:
            self._add_history(r, g, b)

    def _on_wheel_color(self, r: int, g: int, b: int):
        self._set_color(r, g, b, add_history=True)

    # ── Screen picker ────────────────────────────────────────────────

    def _start_pick(self):
        self.withdraw()
        self.after(200, lambda: ScreenPicker(self, self._on_picked).start())

    def _on_picked(self, r: int, g: int, b: int):
        self.deiconify()
        self.lift()
        self._set_color(r, g, b)
        fmt = self.settings.quick_copy_format
        if fmt and fmt != 'None':
            self._copy(format_color(r, g, b, fmt))

    # ── Accordion ────────────────────────────────────────────────────

    def _toggle_wheel(self):
        self._wheel_open = not self._wheel_open
        if self._wheel_open:
            self._wheel.set_color(self._r, self._g, self._b)
            self._wheel_frame.pack(fill='x')
            self._toggle_btn.config(text='▲')
        else:
            self._wheel_frame.pack_forget()
            self._toggle_btn.config(text='▼')
        self.update_idletasks()
        self.geometry(f'{WINDOW_WIDTH}x{self.winfo_reqheight()}')

    # ── Clipboard ────────────────────────────────────────────────────

    def _copy(self, text: str):
        self.clipboard_clear()
        self.clipboard_append(text)
        self.update()

    # ── Settings ─────────────────────────────────────────────────────

    def _open_settings(self):
        SettingsDialog(self, self.settings, self._on_settings_saved)

    def _on_settings_saved(self, hotkey_changed: bool):
        max_h = self.settings.history_count or 7
        self._history = self._history[-max_h:]
        self._refresh_history()
        if hotkey_changed and self.on_hotkey_change:
            self.on_hotkey_change()


# ── Tooltip ──────────────────────────────────────────────────────────

class _Tooltip:
    def __init__(self, widget, text: str):
        self._widget = widget
        self._text = text
        self._tip = None
        widget.bind('<Enter>', self._show)
        widget.bind('<Leave>', self._hide)

    def _show(self, _=None):
        x = self._widget.winfo_rootx() + 16
        y = self._widget.winfo_rooty() + 24
        self._tip = tk.Toplevel(self._widget)
        self._tip.overrideredirect(True)
        self._tip.geometry(f'+{x}+{y}')
        tk.Label(self._tip, text=self._text, bg='#333', fg='white',
                 font=('Segoe UI', 8), padx=4, pady=2).pack()

    def _hide(self, _=None):
        if self._tip:
            self._tip.destroy()
            self._tip = None


# ── Settings dialog ──────────────────────────────────────────────────

class SettingsDialog(tk.Toplevel):
    def __init__(self, parent, settings, on_save=None):
        super().__init__(parent)
        self.settings = settings
        self._on_save = on_save
        self.title('Settings')
        self.configure(bg=BG)
        self.resizable(False, False)
        self.grab_set()
        self.transient(parent)
        self._build()
        self.update_idletasks()
        px = parent.winfo_x() + parent.winfo_width() // 2 - self.winfo_width() // 2
        py = parent.winfo_y() + parent.winfo_height() // 2 - self.winfo_height() // 2
        self.geometry(f'+{px}+{py}')
        self.bind('<Map>', lambda e: self.after(10, lambda: _apply_dark_titlebar(self.winfo_id())))

    def _build(self):
        tk.Label(self, text='Settings', bg=BG, fg=FG,
                 font=('Segoe UI', 12, 'bold')).pack(anchor='w', padx=16, pady=(14, 8))
        tk.Frame(self, bg=SEP, height=1).pack(fill='x')

        body = tk.Frame(self, bg=BG, padx=18, pady=14)
        body.pack(fill='both', expand=True)
        body.columnconfigure(0, weight=0)
        body.columnconfigure(1, weight=1)

        row = 0

        def label(text):
            return tk.Label(body, text=text, bg=BG, fg=FG2, font=FONT, anchor='w')

        # Startup
        self._startup_var = tk.BooleanVar(value=self.settings.get_startup_state())
        label('Run at startup').grid(row=row, column=0, sticky='w', pady=8)
        tk.Checkbutton(body, variable=self._startup_var, bg=BG, activebackground=BG,
                       fg=FG, selectcolor=BG3, cursor='hand2').grid(
            row=row, column=1, sticky='w', padx=(14, 0))
        row += 1

        # Hotkey
        self._hotkey_var = tk.StringVar(value=self.settings.hotkey or 'ctrl+shift+c')
        label('Hotkey').grid(row=row, column=0, sticky='w', pady=8)
        tk.Entry(body, textvariable=self._hotkey_var, bg=BG3, fg=FG,
                 insertbackground=FG, relief='flat', font=('Consolas', 10),
                 width=18).grid(row=row, column=1, sticky='w', padx=(14, 0), ipady=3)
        row += 1
        tk.Label(body, text='* Takes effect after restart', bg=BG, fg=FG2,
                 font=('Segoe UI', 8)).grid(row=row, column=1, sticky='w', padx=(14, 0))
        row += 1

        # History count
        self._hist_var = tk.IntVar(value=self.settings.history_count or 7)
        label('History size').grid(row=row, column=0, sticky='w', pady=8)
        tk.Spinbox(body, from_=3, to=20, textvariable=self._hist_var,
                   bg=BG3, fg=FG, buttonbackground=BG3, relief='flat',
                   font=FONT, width=5).grid(row=row, column=1, sticky='w', padx=(14, 0))
        row += 1

        # Quick copy format
        label('Quick copy format').grid(row=row, column=0, sticky='w', pady=8)
        self._qcopy_var = tk.StringVar(value=self.settings.quick_copy_format or 'HEX')
        fmt_row = tk.Frame(body, bg=BG)
        fmt_row.grid(row=row, column=1, sticky='w', padx=(14, 0))
        for fmt in ('HEX', 'RGB', 'HSL', 'None'):
            tk.Radiobutton(fmt_row, text=fmt, variable=self._qcopy_var, value=fmt,
                           bg=BG, fg=FG, selectcolor=BG3, activebackground=BG,
                           cursor='hand2').pack(side='left', padx=(0, 10))

        # Buttons
        tk.Frame(self, bg=SEP, height=1).pack(fill='x')
        btn_row = tk.Frame(self, bg=BG)
        btn_row.pack(fill='x', padx=16, pady=10)
        tk.Button(btn_row, text='Save', bg=BLUE, fg=FG, relief='flat',
                  font=FONT, padx=18, pady=4, cursor='hand2',
                  activebackground='#006cc1', activeforeground=FG,
                  command=self._save).pack(side='right')
        tk.Button(btn_row, text='Cancel', bg=BG3, fg=FG, relief='flat',
                  font=FONT, padx=12, pady=4, cursor='hand2',
                  activebackground='#484848', activeforeground=FG,
                  command=self.destroy).pack(side='right', padx=(0, 8))

    def _save(self):
        new_startup = self._startup_var.get()
        if new_startup != self.settings.get_startup_state():
            self.settings.set_startup(new_startup)

        old_hotkey = self.settings.hotkey
        new_hotkey = self._hotkey_var.get().strip()
        self.settings.hotkey = new_hotkey
        self.settings.history_count = self._hist_var.get()
        self.settings.quick_copy_format = self._qcopy_var.get()
        self.settings.save()

        hotkey_changed = old_hotkey != new_hotkey
        self.destroy()
        if self._on_save:
            self._on_save(hotkey_changed)
