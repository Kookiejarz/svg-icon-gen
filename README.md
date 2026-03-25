# svg-icon-gen

[![PyPI](https://img.shields.io/pypi/v/svg-icon-gen)](https://pypi.org/project/svg-icon-gen/)
[![License](https://img.shields.io/github/license/Kookiejarz/SVG_to_ICONS)](LICENSE)

Convert a single SVG into a complete icon set — ICO, ICNS, macOS menu bar templates, and PNG exports — in one command.

```bash
svg-icon-gen logo.svg
```

---

## 🔧 Installation

```bash
pip install svg-icon-gen
```

> **Note:** `svg-icon-gen` depends on [Cairo](https://www.cairographics.org/) via `cairosvg`. If the install fails, install Cairo first:
>
> | Platform | Command |
> |----------|---------|
> | macOS | `brew install cairo` |
> | Ubuntu / Debian | `sudo apt install libcairo2` |
> | Windows | Install [GTK for Windows](https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases) |

---

## ⬆️ Output

Running `svg-icon-gen logo.svg` produces:

```
logo/
├── logo.ico                          # Windows icon (16–256px, multi-res)
├── logo_dark.ico                     # Inverted variant
├── logo.icns                         # macOS app icon (16–1024px)
├── logo_mac_template.png             # Menu bar icon, black 1x
├── logo_mac_template@2x.png          # Menu bar icon, black 2x
├── logo_mac_template_dark.png        # Menu bar icon, white 1x
├── logo_mac_template_dark@2x.png     # Menu bar icon, white 2x
└── png/
    ├── light/
    │   ├── logo_16x16.png
    │   ├── logo_32x32.png
    │   └── ...
    └── dark/
        └── ...
```

---

## ⚙️ Usage

```bash
# Single file
svg-icon-gen logo.svg

# Multiple files
svg-icon-gen icon1.svg icon2.svg icon3.svg

# Glob
svg-icon-gen assets/*.svg

# Watch mode — regenerate on save
svg-icon-gen logo.svg --watch

# Custom output directory
svg-icon-gen logo.svg --out-dir ./dist/icons

# Custom PNG sizes
svg-icon-gen logo.svg --png-sizes 16,32,128,512
```

### 🚩 Flags

| Flag | Description |
|------|-------------|
| `--watch` | Watch for changes and regenerate automatically |
| `--ico-only` | Generate ICO only |
| `--icns-only` | Generate ICNS only |
| `--mac-only` | Generate macOS Template PNGs only |
| `--png-only` | Generate PNGs only |
| `--no-dark` | Skip dark/inverted variants |
| `--png-sizes SIZES` | Comma-separated sizes (default: `16,32,64,128,256,512`) |
| `--out-dir DIR` | Output directory root (default: same folder as SVG) |

---

## Platform Notes

### 🪟 Windows — ICO
Standard multi-resolution `.ico` containing 16, 32, 48, 64, 128, and 256px layers.

### 💻 macOS — ICNS
Full Apple-spec `.icns` for app icons, containing all required sizes from 16px to 1024px. Uses [`icnsutil`](https://pypi.org/project/icnsutil/) (pure Python, cross-platform). On macOS without `icnsutil`, falls back to the native `iconutil` CLI.

### 🍎 macOS — Menu Bar Template Icons
`*Template.png` files follow Apple's naming convention — the system automatically inverts them for light/dark menu bars. The `_dark` white variant is provided for frameworks that require an explicit white icon (Electron, Tauri, SwiftUI `NSStatusItem`).

| File | Use case |
|------|----------|
| `*Template.png` / `*Template@2x.png` | Native macOS apps, system auto-adapts |
| `*Template_dark.png` / `*Template_dark@2x.png` | Electron / Tauri explicit dark mode |

### 🔭 Watch Mode
Install [`watchdog`](https://pypi.org/project/watchdog/) for instant file-system event detection. Without it, `--watch` falls back to polling every second.

```bash
pip install watchdog
```
---

## Star History

<a href="https://www.star-history.com/?repos=Kookiejarz%2Fsvg-icon-gen&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/image?repos=Kookiejarz/svg-icon-gen&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/image?repos=Kookiejarz/svg-icon-gen&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/image?repos=Kookiejarz/svg-icon-gen&type=date&legend=top-left" />
 </picture>
</a>

---
## 📄 License

[MIT](/LICENSE)
