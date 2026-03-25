#!/usr/bin/env python3
"""
svg-icon-gen: Convert SVG files into production-ready icon sets.

Usage:
  Single file:  svg-icon-gen logo.svg
  Batch:        svg-icon-gen icon1.svg icon2.svg icon3.svg
  Glob:         svg-icon-gen assets/*.svg
  Watch mode:   svg-icon-gen logo.svg --watch

Options:
  --ico-only      Generate ICO files only
  --icns-only     Generate ICNS files only
  --mac-only      Generate macOS Template icons only
  --png-only      Generate PNG files only
  --no-dark       Skip dark theme variants
  --png-sizes     Comma-separated PNG sizes (default: 16,32,64,128,256,512)
  --out-dir       Root output directory (default: same directory as SVG)
  --watch         Watch SVG files for changes and regenerate automatically
"""

import argparse
import io
import os
import sys
import tempfile
import time

import cairosvg
import numpy as np
from PIL import Image, ImageOps

# ICNS requires all these sizes (Apple spec)
ICNS_SIZES = [16, 32, 64, 128, 256, 512, 1024]


def svg_to_pil(svg_path: str, size: tuple[int, int]) -> Image.Image:
    """Rasterize an SVG at the given size and return a PIL RGBA image."""
    png_data = cairosvg.svg2png(
        url=svg_path,
        output_width=size[0],
        output_height=size[1],
    )
    return Image.open(io.BytesIO(png_data)).convert("RGBA")


def make_inverted(img: Image.Image) -> Image.Image:
    """Invert RGB channels while preserving the original alpha channel."""
    r, g, b, a = img.split()
    inv = ImageOps.invert(Image.merge("RGB", (r, g, b)))
    ir, ig, ib = inv.split()
    return Image.merge("RGBA", (ir, ig, ib, a))

def make_ico(img: Image.Image, output_path: str) -> None:
    """Save a multi-resolution ICO file from a single source image."""
    sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    frames = [img.resize(s, Image.Resampling.LANCZOS) for s in sizes]
    frames[0].save(
        output_path,
        format="ICO",
        append_images=frames[1:],
        sizes=sizes,
    )


def make_icns(svg_path: str, output_path: str) -> None:
    """
    Generate a macOS ICNS app icon file.

    Uses icnsutil (pure Python, cross-platform) when available,
    falling back to macOS iconutil if running on macOS.
    """
    try:
        import icnsutil

        img = icnsutil.IcnsFile()
        for size in ICNS_SIZES:
            pil_img = svg_to_pil(svg_path, (size, size))
            buf = io.BytesIO()
            pil_img.save(buf, format="PNG")
            buf.seek(0)
            # icnsutil uses string keys like 'ic07' (128px), etc.
            img.add_media(file=buf, filename=f"icon_{size}x{size}.png")
        img.write(output_path)

    except ImportError:
        # Fallback: use macOS iconutil (only works on macOS)
        if sys.platform != "darwin":
            print("  ⚠  icnsutil not installed and not on macOS — skipping ICNS")
            print("     Install with: pip install icnsutil")
            return

        with tempfile.TemporaryDirectory(suffix=".iconset") as iconset:
            # Apple requires these exact filenames
            spec = [
                (16,   "icon_16x16.png"),
                (32,   "icon_16x16@2x.png"),
                (32,   "icon_32x32.png"),
                (64,   "icon_32x32@2x.png"),
                (128,  "icon_128x128.png"),
                (256,  "icon_128x128@2x.png"),
                (256,  "icon_256x256.png"),
                (512,  "icon_256x256@2x.png"),
                (512,  "icon_512x512.png"),
                (1024, "icon_512x512@2x.png"),
            ]
            for px, fname in spec:
                img = svg_to_pil(svg_path, (px, px))
                img.save(os.path.join(iconset, fname))

            os.system(f'iconutil -c icns "{iconset}" -o "{output_path}"')


def make_mac_template(
    svg_path: str,
    mac_size: tuple[int, int],
    inner_size: tuple[int, int],
    output_path: str,
    dark: bool = False,
) -> None:
    """
    Generate a macOS menu bar Template icon.

    dark=False → black pixels (system auto-adapts via *Template.png naming)
    dark=True  → white pixels (for Electron/Tauri explicit dark variant)
    """
    rendered = svg_to_pil(svg_path, inner_size)
    canvas = Image.new("RGBA", mac_size, (0, 0, 0, 0))
    offset = (
        (mac_size[0] - inner_size[0]) // 2,
        (mac_size[1] - inner_size[1]) // 2,
    )
    canvas.paste(rendered, offset, rendered)

    arr = np.array(canvas, dtype=np.uint8)
    avg = arr[..., :3].mean(axis=2)
    mask = (avg >= 128) if dark else (avg < 128)

    fill = (255, 255, 255) if dark else (0, 0, 0)
    arr[..., 0] = fill[0]
    arr[..., 1] = fill[1]
    arr[..., 2] = fill[2]
    arr[..., 3] = np.where(mask, arr[..., 3], 0)

    Image.fromarray(arr, "RGBA").save(output_path)


def process_svg(svg_path: str, args: argparse.Namespace) -> None:
    """Convert a single SVG file into all requested icon formats."""
    if not os.path.exists(svg_path):
        print(f"  ✗ File not found: {svg_path}")
        return

    stem = os.path.splitext(os.path.basename(svg_path))[0]
    base_root = args.out_dir if args.out_dir else os.path.dirname(os.path.abspath(svg_path))
    out_dir = os.path.join(base_root, stem)
    os.makedirs(out_dir, exist_ok=True)

    print(f"\n▶ {svg_path}  →  {out_dir}/")

    base_light = svg_to_pil(svg_path, (1024, 1024))
    base_dark = make_inverted(base_light) if not args.no_dark else None

    only_flags = [args.ico_only, args.icns_only, args.mac_only, args.png_only]

    def should(flag: bool) -> bool:
        """Show this format if its flag is set, or if no --*-only flag is set."""
        return flag or not any(only_flags)

    # ICO
    if should(args.ico_only):
        make_ico(base_light, os.path.join(out_dir, f"{stem}.ico"))
        print(f"  ✅ {stem}.ico")
        if base_dark is not None:
            make_ico(base_dark, os.path.join(out_dir, f"{stem}_dark.ico"))
            print(f"  ✅ {stem}_dark.ico")

    # ICNS
    if should(args.icns_only):
        make_icns(svg_path, os.path.join(out_dir, f"{stem}.icns"))
        print(f"  ✅ {stem}.icns")

    # macOS Template
    if should(args.mac_only):
        for suffix, dark_flag in [("", False), ("_dark", True)]:
            if dark_flag and args.no_dark:
                continue
            for scale, mac_sz, inner_sz in [
                ("",    (22, 22), (18, 18)),
                ("@2x", (44, 44), (36, 36)),
            ]:
                fname = f"{stem}_mac_template{suffix}{scale}.png"
                make_mac_template(svg_path, mac_sz, inner_sz,
                                  os.path.join(out_dir, fname), dark=dark_flag)
            label = "white (dark)" if dark_flag else "black (auto-adapt)"
            print(f"  ✅ macOS template {label} × 2  (1x + @2x)")

    # PNG
    if should(args.png_only):
        png_sizes = [int(s) for s in args.png_sizes.split(",")]
        for theme, img in [("light", base_light), ("dark", base_dark)]:
            if img is None:
                continue
            theme_dir = os.path.join(out_dir, "png", theme)
            os.makedirs(theme_dir, exist_ok=True)
            for s in png_sizes:
                img.resize((s, s), Image.Resampling.LANCZOS).save(
                    os.path.join(theme_dir, f"{stem}_{s}x{s}.png")
                )
        sizes_str = ", ".join(str(s) for s in png_sizes)
        themes = "light + dark" if not args.no_dark else "light only"
        print(f"  ✅ PNG {themes}  [{sizes_str}]")


# Watch mode

def watch(svgs: list[str], args: argparse.Namespace) -> None:
    """Poll SVG files for mtime changes and re-run process_svg on changes."""
    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler

        abs_svgs = {os.path.abspath(p): p for p in svgs}

        class Handler(FileSystemEventHandler):
            def on_modified(self, event):
                if event.src_path in abs_svgs:
                    print(f"\n🔄 Changed: {abs_svgs[event.src_path]}")
                    try:
                        process_svg(abs_svgs[event.src_path], args)
                    except Exception as e:
                        print(f"  ✗ Error: {e}")

        observer = Observer()
        watched_dirs = {os.path.dirname(p) or "." for p in abs_svgs}
        for d in watched_dirs:
            observer.schedule(Handler(), d, recursive=False)

        observer.start()
        print(f"\n👁  Watching {len(svgs)} file(s) — Ctrl+C to stop\n")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

    except ImportError:
        # watchdog not installed — fall back to simple mtime polling
        print("watchdog not installed, using polling (install watchdog for better performance)")
        mtimes = {p: os.path.getmtime(p) for p in svgs if os.path.exists(p)}
        print(f"\n👁  Watching {len(svgs)} file(s) — Ctrl+C to stop\n")
        try:
            while True:
                time.sleep(1)
                for svg in svgs:
                    if not os.path.exists(svg):
                        continue
                    mtime = os.path.getmtime(svg)
                    if mtime != mtimes.get(svg):
                        mtimes[svg] = mtime
                        print(f"\n🔄 Changed: {svg}")
                        try:
                            process_svg(svg, args)
                        except Exception as e:
                            print(f"  ✗ Error: {e}")
        except KeyboardInterrupt:
            print("\n👋 Watch stopped")


# CLI

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Batch SVG converter: ICO / ICNS / macOS Template / PNG",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("svgs", nargs="+", metavar="FILE.svg")
    p.add_argument("--ico-only",  action="store_true", help="Generate ICO files only")
    p.add_argument("--icns-only", action="store_true", help="Generate ICNS files only")
    p.add_argument("--mac-only",  action="store_true", help="Generate macOS Template icons only")
    p.add_argument("--png-only",  action="store_true", help="Generate PNG files only")
    p.add_argument("--no-dark",   action="store_true", help="Skip dark theme variants")
    p.add_argument("--png-sizes", default="16,32,64,128,256,512", metavar="SIZES")
    p.add_argument("--out-dir",   default=None, metavar="DIR")
    p.add_argument("--watch",     action="store_true",
                   help="Watch files for changes and regenerate automatically")
    return p


def main() -> None:
    if len(sys.argv) == 1:
        build_parser().print_help()
        sys.exit(0)

    args = build_parser().parse_args()

    only_flags = [args.ico_only, args.icns_only, args.mac_only, args.png_only]
    if sum(only_flags) > 1:
        print("Error: --ico-only, --icns-only, --mac-only, --png-only are mutually exclusive.")
        sys.exit(1)

    # Initial pass
    print(f"{len(args.svgs)} file(s) to process")
    for svg in args.svgs:
        try:
            process_svg(svg, args)
        except Exception as e:
            print(f"  ✗ {svg}: {e}")

    print("\n🎉 Done")

    if args.watch:
        watch(args.svgs, args)


if __name__ == "__main__":
    main()