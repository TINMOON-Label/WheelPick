
# WheelPick

A tiny system-tray color picker for Windows — with a built-in color wheel.

Pick any color on screen with the eyedropper, fine-tune it on the wheel, and copy the exact value. Built for the moment you want to tell someone — or an AI — **"make it this color: `#2B2B2A`"**, precisely, not approximately.

<!-- TODO: demo GIF here -->
<!-- ![WheelPick demo](docs/demo.gif) -->

## Why?

Picking colors while building things with an AI gets old fast. *"A bit more blue." "No, too bright." "Actually, the previous one…"* — the more you describe a color in words, the more it slips away, and somehow the whole afternoon is gone to tiny tweaks.

The only thing that *actually* works is handing over an exact value (`#2B2B2A`), not an adjective. But knowing the HEX of whatever's on your screen — and nudging it to the shade you really want — usually means juggling two tools. Windows utilities like PowerToys have a great eyedropper and history, but no color wheel; adjusting a hue or lightness means opening a separate app.

WheelPick puts both in one window: grab it, tweak it on the wheel, copy the exact value, done. No more losing the day to color tweaks.

## Features

- 🎯 Screen eyedropper with a magnified loupe — pixel-accurate picking
- 🎨 Color wheel (hue ring + saturation/value square) for manual tweaking
- 📋 HEX / RGB / HSL values, one-click copy each (HEX copies with `#`)
- 🕘 History of recent colors
- ⚙️ Settings: run at startup, global hotkey, history size, quick-copy format
- 🪟 Lives in the system tray — click the tray icon to start picking instantly

## Download

Grab the latest from the [Releases](https://github.com/TINMOON-Label/WheelPick/releases) page:

- `WheelPick-Setup.exe` — installer (adds Start Menu entry, optional startup & desktop icon, clean uninstaller)
- `WheelPick-Portable.zip` — no install; unzip and run. Settings are saved next to the exe, so the whole folder is portable (USB-friendly).

> **SmartScreen note:** the exe isn't code-signed yet, so Windows may show *"Windows protected your PC."* Click **More info → Run anyway.**

## Usage

1. Launch the app — a color-wheel icon appears in the system tray.
2. Click the tray icon (or press the hotkey, default `Ctrl+Shift+C`) to start the eyedropper.
3. Click any pixel to capture its color. The value is copied automatically (configurable).
4. Open the window and click the ▼ to expand the color wheel for fine adjustment.

## Build from source

Requires Python 3.

```
pip install -r requirements.txt
python main.py
```

Build the standalone exe (PyInstaller):

```
pyinstaller --onefile --windowed --name WheelPick --icon app.ico --hidden-import keyboard --hidden-import mss main.py
```

## License

[MIT](https://github.com/TINMOON-Label/WheelPick/blob/main/LICENSE) — free to use, modify, and distribute.

---

# WheelPick（日本語）

Windows のシステムトレイに常駐する、小さなカラーピッカー。カラーホイール内蔵。

スポイトで画面のどこからでも色を吸い取り、ホイールで微調整して、正確な値をコピーできます。誰かに——あるいは AI に——**「この色にして：`#2B2B2A`」** と、“だいたい” ではなく “正確に” 伝えたいときのための道具です。

https://github.com/user-attachments/assets/72b9a30c-cc84-4eab-bb71-1de231f942bb"


## なぜ作ったか

AI と一緒に開発していると、色を決める作業がとにかく面倒です。
*「もう少し青く」「いや、明るすぎ」「やっぱりさっきの方が…」* ——
言葉で伝えようとするほど色は逃げていって、気づけば微調整だけで午後がまるごと溶ける…。

結局、AI に色を正確に伝える唯一の方法は、形容詞ではなく具体的な値（`#2B2B2A`）を渡すことです。でも、画面に映っている色の HEX 値なんて普通は分からないし、そこから「本当に欲しい色」へ寄せていくとなると、たいていツールを2つ行き来する羽目になります。Windows の PowerToys などは優秀なスポイトと履歴を持っていますが、カラーホイールがありません。色相を回したり明度を少し動かすには、別アプリを開くことになる。

WheelPick は、その両方を1つのウィンドウにまとめました。吸って、ホイールで整えて、正確な値をコピーして、おしまい。もう、色の微調整で一日を溶かさない。

## 主な機能

- 🎯 拡大ルーペ付きのスポイト — ピクセル単位で正確に拾える
- 🎨 カラーホイール（色相リング＋彩度／明度の四角）で手動微調整
- 📋 HEX / RGB / HSL を表示、それぞれワンクリックでコピー（HEX は `#` 付き）
- 🕘 最近使った色の履歴
- ⚙️ 設定：起動時に自動実行、グローバルホットキー、履歴の数、クイックコピーの形式
- 🪟 システムトレイに常駐 — トレイアイコンをクリックすればすぐにスポイト開始

## ダウンロード

[Releases](https://github.com/TINMOON-Label/WheelPick/releases) ページから最新版を入手してください。

- `WheelPick-Setup.exe` — インストーラー（スタートメニュー登録、起動時実行・デスクトップアイコンは任意、アンインストーラー付き）
- `WheelPick-Portable.zip` — インストール不要。解凍して実行するだけ。設定は exe の隣に保存されるので、フォルダごと持ち運べます（USB でも使えます）。

> **SmartScreen について：** exe はまだコード署名していないため、Windows が *「WindowsによってPCが保護されました」* と表示することがあります。**詳細情報 → 実行** で起動できます。

## 使い方

1. アプリを起動すると、システムトレイにカラーホイールのアイコンが出ます。
2. トレイアイコンをクリック（またはホットキー、初期設定は `Ctrl+Shift+C`）でスポイト開始。
3. 任意のピクセルをクリックして色を取得。値は自動でコピーされます（設定で変更可）。
4. ウィンドウを開いて ▼ を押すと、カラーホイールが展開して微調整できます。

## ソースからビルド

Python 3 が必要です。

```
pip install -r requirements.txt
python main.py
```

単体 exe をビルド（PyInstaller）：

```
pyinstaller --onefile --windowed --name WheelPick --icon app.ico --hidden-import keyboard --hidden-import mss main.py
```

## ライセンス

[MIT](https://github.com/TINMOON-Label/WheelPick/blob/main/LICENSE) — 自由に使用・改変・再配布できます。
