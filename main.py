import tkinter as tk
import threading
import sys
import os

from PIL import Image, ImageDraw
import pystray

from settings import Settings
from picker_window import PickerWindow


def _make_tray_icon() -> Image.Image:
    size = 64
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Color wheel-style icon: 6 pie slices
    colors = [
        (255, 80,  80),
        (255, 180,  0),
        (80,  200,  80),
        (0,   180, 255),
        (100,  80, 255),
        (255,  80, 180),
    ]
    for i, color in enumerate(colors):
        draw.pieslice([3, 3, 61, 61], i * 60 - 90, (i + 1) * 60 - 90, fill=color)
    # Dark center hole
    draw.ellipse([22, 22, 42, 42], fill=(20, 20, 20))
    return img


class App:
    def __init__(self):
        self.settings = Settings()
        self.root = tk.Tk()
        self.root.withdraw()
        self._window: PickerWindow | None = None
        self._tray: pystray.Icon | None = None

    # ── Window ───────────────────────────────────────────────────────

    def _ensure_window(self) -> PickerWindow:
        if self._window is None or not self._window.winfo_exists():
            self._window = PickerWindow(
                self.root, self.settings,
                on_hotkey_change=self._reregister_hotkey
            )
        return self._window

    def show(self):
        w = self._ensure_window()
        w.deiconify()
        w.lift()
        w.focus_force()

    def start_picker(self):
        """Start the eyedropper directly from tray click."""
        w = self._ensure_window()
        w._start_pick()

    def toggle(self):
        w = self._ensure_window()
        if w.winfo_viewable():
            w.withdraw()
        else:
            w.deiconify()
            w.lift()
            w.focus_force()

    # ── Tray ─────────────────────────────────────────────────────────

    def _setup_tray(self):
        menu = pystray.Menu(
            pystray.MenuItem(
                'Pick a color',
                lambda: self.root.after(0, self.start_picker),
                default=True
            ),
            pystray.MenuItem(
                'Open window',
                lambda: self.root.after(0, self.show),
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem('Exit', lambda: self.root.after(0, self._quit)),
        )
        self._tray = pystray.Icon('ColorPicker', _make_tray_icon(), 'Color Picker', menu)

    # ── Hotkey ───────────────────────────────────────────────────────

    def _register_hotkey(self):
        try:
            import keyboard
            hotkey = self.settings.hotkey or 'ctrl+shift+c'
            keyboard.add_hotkey(hotkey, lambda: self.root.after(0, self.start_picker))
        except Exception as e:
            print(f'Hotkey registration failed: {e}')

    def _reregister_hotkey(self):
        try:
            import keyboard
            keyboard.unhook_all()
            self._register_hotkey()
        except Exception:
            pass

    # ── Lifecycle ────────────────────────────────────────────────────

    def _quit(self):
        if self._tray:
            self._tray.stop()
        try:
            import keyboard
            keyboard.unhook_all()
        except Exception:
            pass
        self.root.quit()

    def run(self):
        self._setup_tray()

        tray_thread = threading.Thread(target=self._tray.run, daemon=True)
        tray_thread.start()

        self._register_hotkey()
        self.root.after(100, self.show)
        self.root.mainloop()


if __name__ == '__main__':
    app = App()
    app.run()
