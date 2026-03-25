# 🏷️ svg-icon-gen

[![PyPI](https://img.shields.io/pypi/v/svg-icon-gen)](https://pypi.org/project/svg-icon-gen/)
[![License](https://img.shields.io/github/license/Kookiejarz/SVG_to_ICONS)](LICENSE)

A command-line tool that converts SVG files into production-ready icon sets for Windows and macOS, including automatic dark theme variants.

## Output

For each input SVG (e.g. `logo.svg`), a subfolder named `logo/` is created containing:

```
logo/
├── logo.ico                        # Windows light theme (multi-resolution: 16–256px)
├── logo_dark.ico                   # Windows dark theme
├── logo_mac_template.png           # macOS menu bar, black (system auto-adapts light/dark)
├── logo_mac_template@2x.png        # macOS menu bar, black, Retina
├── logo_mac_template_dark.png      # macOS menu bar, white (for Electron / non-native)
├── logo_mac_template_dark@2x.png   # macOS menu bar, white, Retina
└── png/
    ├── light/
    │   ├── logo_16x16.png
    │   ├── logo_32x32.png
    │   └── ...up to 512x512
    └── dark/
        └── ...same sizes, inverted
```

## Requirements

```bash
pip install cairosvg pillow
```

> **macOS**: if `cairosvg` fails to install, run `brew install cairo` first.
> **Windows**: install the [GTK3 runtime](https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer) for Cairo support, or use WSL.

## Usage

```bash
# Single file
python generate_icons.py logo.svg

# Multiple files
python generate_icons.py icon1.svg icon2.svg icon3.svg

# Glob (bash / zsh)
python generate_icons.py assets/*.svg
```

## Options

| Flag | Description |
|------|-------------|
| `--ico-only` | Generate ICO files only |
| `--mac-only` | Generate macOS Template icons only |
| `--png-only` | Generate PNG files only |
| `--no-dark` | Skip dark theme variants |
| `--png-sizes SIZES` | Comma-separated PNG sizes (default: `16,32,64,128,256,512`) |
| `--out-dir DIR` | Root output directory (default: same directory as each SVG) |

`--ico-only`, `--mac-only`, and `--png-only` are mutually exclusive.

## Examples

```bash
# Only ICO, no dark variant, output to ./dist
python generate_icons.py *.svg --ico-only --no-dark --out-dir ./dist

# Custom PNG sizes
python generate_icons.py logo.svg --png-only --png-sizes 32,64,128

# macOS icons only, all SVGs in a folder
python generate_icons.py assets/*.svg --mac-only
```

## Platform Notes

### macOS

Files named `*Template.png` are automatically rendered by the system to match the current menu bar appearance — no code changes needed for light/dark mode support. The `_dark` white variants are intended for frameworks that do not support the Template convention:

| Framework | Recommended file |
|-----------|-----------------|
| SwiftUI / AppKit | `*_mac_template.png` only |
| Electron | Switch between black and white versions on `nativeTheme.on('updated')` |
| Tauri | Switch on `tauri::api::app::appearance_changed` |

### Windows

The system tray does not automatically invert icons. Detect the active theme at runtime and swap accordingly:

- **Win32**: listen for `WM_SETTINGCHANGE`, read `HKCU\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize\AppsUseLightTheme`
- **Electron**: use `nativeTheme.shouldUseDarkColors` and call `tray.setImage()` on updates



## Star History

<a href="https://www.star-history.com/?repos=Kookiejarz%2Fsvg-icon-gen&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/image?repos=Kookiejarz/svg-icon-gen&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/image?repos=Kookiejarz/svg-icon-gen&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/image?repos=Kookiejarz/svg-icon-gen&type=date&legend=top-left" />
 </picture>
</a>
