import json
import os
import sys
import winreg

APP_NAME = 'ColorPicker'


def _exe_dir() -> str:
    """Folder containing the exe (frozen) or this source file."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def is_portable() -> bool:
    """Portable mode if a 'portable.txt' marker sits next to the exe."""
    return os.path.exists(os.path.join(_exe_dir(), 'portable.txt'))


def get_data_dir() -> str:
    """Storage dir: exe folder (portable) or %APPDATA%\\ColorPicker (installed)."""
    if is_portable():
        path = _exe_dir()
    else:
        base = os.environ.get('APPDATA') or os.path.expanduser('~')
        path = os.path.join(base, APP_NAME)
    os.makedirs(path, exist_ok=True)
    return path


SETTINGS_FILE = os.path.join(get_data_dir(), 'settings.json')

DEFAULTS = {
    'startup': False,
    'hotkey': 'ctrl+shift+c',
    'history_count': 7,
    'quick_copy_format': 'HEX',  # 'HEX', 'RGB', 'HSL', 'None'
}


class Settings:
    def __init__(self):
        self._data = dict(DEFAULTS)
        self.load()

    def load(self):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                self._data.update(json.load(f))
        except (FileNotFoundError, json.JSONDecodeError):
            pass

    def save(self):
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self._data, f, indent=2, ensure_ascii=False)

    def __getattr__(self, name):
        if name.startswith('_'):
            raise AttributeError(name)
        return self._data.get(name)

    def __setattr__(self, name, value):
        if name.startswith('_'):
            super().__setattr__(name, value)
        else:
            self._data[name] = value

    def get_startup_state(self) -> bool:
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r'Software\Microsoft\Windows\CurrentVersion\Run',
                0, winreg.KEY_READ
            )
            winreg.QueryValueEx(key, APP_NAME)
            winreg.CloseKey(key)
            return True
        except FileNotFoundError:
            return False

    def set_startup(self, enabled: bool):
        if getattr(sys, 'frozen', False):
            # Running as a bundled .exe — register the exe itself
            launch_cmd = f'"{sys.executable}"'
        else:
            # Running from source — register python + main.py
            script_path = os.path.abspath(
                os.path.join(os.path.dirname(__file__), 'main.py')
            )
            launch_cmd = f'"{sys.executable}" "{script_path}"'
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r'Software\Microsoft\Windows\CurrentVersion\Run',
                0, winreg.KEY_SET_VALUE
            )
            if enabled:
                winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, launch_cmd)
            else:
                try:
                    winreg.DeleteValue(key, APP_NAME)
                except FileNotFoundError:
                    pass
            winreg.CloseKey(key)
        except Exception as e:
            print(f"Startup registry error: {e}")
        self._data['startup'] = enabled
        self.save()
