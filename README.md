# WheelPick

A tiny system-tray color picker for Windows — with a built-in **color wheel**.

Pick any color on screen with the eyedropper, then fine-tune it on the wheel and copy the exact value. Built for the moment you want to tell someone (or an AI) *"make it this color: `#2B2B2A`"* — precisely, not approximately.

> Why? Windows tools like PowerToys have a great eyedropper and history, but no color wheel — so adjusting a hue or nudging the lightness means opening a separate app. This puts both in one window.

## Features

- 🎯 **Screen eyedropper** with a magnified loupe — pixel-accurate picking
- 🎨 **Color wheel** (hue ring + saturation/value square) for manual tweaking
- 📋 **HEX / RGB / HSL** values, one-click copy each (HEX copies with `#`)
- 🕘 **History** of recent colors
- ⚙️ **Settings**: run at startup, global hotkey, history size, quick-copy format
- 🪟 Lives in the **system tray** — click the tray icon to start picking instantly


<img width="396" height="710" alt="2026-06-30_20-48-53" src="https://github.com/user-attachments/assets/3489198c-818d-4201-b1c6-a787f4727d44" />


<img width="799" height="698" alt="2026-07-01_10-40-24" src="https://github.com/user-attachments/assets/03f50fb3-6de0-49d4-a245-888e82142758" />


## Download

Grab the latest from the [**Releases**](../../releases) page:

- **`WheelPick-Setup.exe`** — installer (adds Start Menu entry, optional startup & desktop icon, clean uninstaller)
- **`WheelPick-Portable.zip`** — no install; unzip and run. Settings are saved next to the exe, so the whole folder is portable (USB-friendly).

> **SmartScreen note:** the exe isn't code-signed yet, so Windows may show *"Windows protected your PC."* Click **More info → Run anyway**.

## Usage

1. Launch the app — a color-wheel icon appears in the system tray.
2. **Click the tray icon** (or press the hotkey, default `Ctrl+Shift+C`) to start the eyedropper.
3. Click any pixel to capture its color. The value is copied automatically (configurable).
4. Open the window and click the **▼** to expand the color wheel for fine adjustment.

## Build from source

Requires Python 3.

```sh
pip install -r requirements.txt
python main.py
```

Build the standalone exe (PyInstaller):

```sh
pyinstaller --onefile --windowed --name WheelPick --icon app.ico --hidden-import keyboard --hidden-import mss main.py
```

## License

[MIT](LICENSE) — free to use, modify, and distribute.
