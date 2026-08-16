#!/usr/bin/env python3
"""Profesyonel Unity profil kapağını güvenli ölçülerle animasyonlu üret."""

from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "assets" / "base-scene.png"
DEFAULT_OUTPUT = ROOT / "assets" / "hero.gif"
DEFAULT_PREVIEW = ROOT / "assets" / "hero-preview.png"

WIDTH = 1000
HEIGHT = 400
FRAME_COUNT = 60
FRAME_MS = 85

CYAN = (75, 215, 244)
VIOLET = (139, 116, 245)
AMBER = (244, 169, 86)
WHITE = (240, 246, 252)
MUTED = (143, 163, 187)
INK = (4, 10, 22)


def find_font(size: int, *, bold: bool = False, mono: bool = False) -> ImageFont.ImageFont:
    if mono:
        candidates = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
            "C:/Windows/Fonts/consolab.ttf" if bold else "C:/Windows/Fonts/consola.ttf",
            "/System/Library/Fonts/Menlo.ttc",
        ]
    else:
        candidates = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        ]

    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size=size)
    return ImageFont.load_default()


def fitted_font(text: str, max_size: int, max_width: int, *, bold: bool = False, mono: bool = False) -> ImageFont.ImageFont:
    for size in range(max_size, 9, -1):
        font = find_font(size, bold=bold, mono=mono)
        box = font.getbbox(text)
        if box[2] - box[0] <= max_width:
            return font
    return find_font(10, bold=bold, mono=mono)


def fit_background(path: Path) -> Image.Image:
    image = Image.open(path).convert("RGB")
    source_ratio = image.width / image.height
    target_ratio = WIDTH / HEIGHT
    if source_ratio > target_ratio:
        crop_width = round(image.height * target_ratio)
        left = (image.width - crop_width) // 2
        image = image.crop((left, 0, left + crop_width, image.height))
    elif source_ratio < target_ratio:
        crop_height = round(image.width / target_ratio)
        top = (image.height - crop_height) // 2
        image = image.crop((0, top, image.width, top + crop_height))
    return image.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS).convert("RGBA")


def glow_text(
    image: Image.Image,
    xy: tuple[int, int],
    text: str,
    font: ImageFont.ImageFont,
    color: tuple[int, int, int],
) -> None:
    halo = Image.new("RGBA", image.size, (0, 0, 0, 0))
    ImageDraw.Draw(halo).text(xy, text, font=font, fill=(*CYAN, 105))
    image.alpha_composite(halo.filter(ImageFilter.GaussianBlur(10)))
    ImageDraw.Draw(image).text(xy, text, font=font, fill=(*color, 255))


def draw_chip(draw: ImageDraw.ImageDraw, x: int, y: int, label: str, color: tuple[int, int, int]) -> int:
    font = find_font(10, bold=True, mono=True)
    box = draw.textbbox((0, 0), label, font=font)
    width = box[2] - box[0] + 22
    draw.rounded_rectangle((x, y, x + width, y + 28), radius=7, fill=(8, 19, 36, 225), outline=(*color, 150))
    draw.text((x + 11, y + 7), label, font=font, fill=(*WHITE, 245))
    return width


def make_static_layer(background: Image.Image, name: str, role: str) -> Image.Image:
    image = background.copy()

    shade = Image.new("RGBA", image.size, (0, 0, 0, 0))
    shade_draw = ImageDraw.Draw(shade)
    for x in range(650):
        alpha = max(0, int(220 * (1 - x / 650)))
        shade_draw.line((x, 0, x, HEIGHT), fill=(*INK, alpha))
    image.alpha_composite(shade)

    draw = ImageDraw.Draw(image, "RGBA")
    draw.rounded_rectangle((34, 38, 560, 356), radius=18, fill=(3, 9, 20, 178), outline=(116, 147, 176, 42))
    draw.rectangle((34, 75, 37, 319), fill=(*CYAN, 215))

    mono_11 = find_font(11, bold=True, mono=True)
    mono_12 = find_font(12, mono=True)
    name_font = fitted_font(name.upper(), 45, 462, bold=True)
    role_font = fitted_font(role.upper(), 18, 462, bold=True)

    draw.text((61, 64), "UNITY / REAL-TIME 3D", font=mono_11, fill=(*CYAN, 240))
    draw.text((424, 64), "PORTFOLYO", font=mono_11, fill=(*MUTED, 210))

    glow_text(image, (58, 105), name.upper(), name_font, WHITE)
    draw.text((61, 165), role.upper(), font=role_font, fill=(*MUTED, 245))
    draw.line((61, 203, 518, 203), fill=(*MUTED, 45), width=1)

    descriptor = "Oynanış sistemleri · Teknik mimari · Performans"
    descriptor_font = fitted_font(descriptor, 13, 457, mono=True)
    draw.text((61, 221), descriptor, font=descriptor_font, fill=(*WHITE, 220))

    chip_x = 61
    for label, color in (("GAMEPLAY", CYAN), ("C#", VIOLET), ("OPTIMIZATION", AMBER)):
        chip_x += draw_chip(draw, chip_x, 253, label, color) + 9

    draw.text((328, 320), "KAPAĞA TIKLA", font=mono_11, fill=(*MUTED, 190))
    draw.text((452, 320), "↗", font=mono_12, fill=(*CYAN, 235))
    return image


def draw_cta(image: Image.Image, pulse: float) -> None:
    draw = ImageDraw.Draw(image, "RGBA")
    x1, y1, x2, y2 = 61, 302, 294, 340
    border_alpha = int(150 + 90 * pulse)
    fill_alpha = int(155 + 35 * pulse)

    halo = Image.new("RGBA", image.size, (0, 0, 0, 0))
    halo_draw = ImageDraw.Draw(halo)
    halo_draw.rounded_rectangle((x1 - 2, y1 - 2, x2 + 2, y2 + 2), radius=10, outline=(*CYAN, int(70 * pulse)), width=3)
    image.alpha_composite(halo.filter(ImageFilter.GaussianBlur(7)))

    draw.rounded_rectangle((x1, y1, x2, y2), radius=9, fill=(9, 28, 46, fill_alpha), outline=(*CYAN, border_alpha), width=1)
    label = "PROJELERİ İNCELE"
    font = fitted_font(label, 12, 175, bold=True, mono=True)
    draw.text((77, 314), label, font=font, fill=(*WHITE, 250))
    draw.line((257, 321, 276, 321), fill=(*CYAN, 240), width=2)
    draw.line((269, 315, 276, 321), fill=(*CYAN, 240), width=2)
    draw.line((269, 327, 276, 321), fill=(*CYAN, 240), width=2)


def render_frames(background: Image.Image, name: str, role: str) -> list[Image.Image]:
    static = make_static_layer(background, name, role)
    frames: list[Image.Image] = []

    for frame_index in range(FRAME_COUNT):
        image = static.copy()
        progress = frame_index / FRAME_COUNT
        pulse = (math.sin(progress * math.tau * 2) + 1) / 2
        draw_cta(image, pulse)

        draw = ImageDraw.Draw(image, "RGBA")
        status_alpha = int(125 + 120 * pulse)
        draw.ellipse((532, 63, 538, 69), fill=(*CYAN, status_alpha))

        scan_x = 603 + int((frame_index % 30) / 29 * 360)
        scan = Image.new("RGBA", image.size, (0, 0, 0, 0))
        scan_draw = ImageDraw.Draw(scan)
        scan_draw.line((scan_x, 54, scan_x, 350), fill=(*CYAN, 30), width=2)
        image.alpha_composite(scan.filter(ImageFilter.GaussianBlur(8)))

        warm_glow = Image.new("RGBA", image.size, (0, 0, 0, 0))
        warm_draw = ImageDraw.Draw(warm_glow)
        warm_draw.ellipse((684, 122, 810, 270), fill=(*AMBER, int(5 + 11 * pulse)))
        image.alpha_composite(warm_glow.filter(ImageFilter.GaussianBlur(28)))

        frames.append(image.convert("RGB"))
    return frames


def save_gif(frames: list[Image.Image], output: Path, preview: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    preview.parent.mkdir(parents=True, exist_ok=True)
    palette = frames[0].quantize(colors=192, method=Image.Quantize.MEDIANCUT)
    quantized = [frame.quantize(palette=palette, dither=Image.Dither.NONE) for frame in frames]
    quantized[0].save(
        output,
        save_all=True,
        append_images=quantized[1:],
        duration=FRAME_MS,
        loop=0,
        optimize=True,
        disposal=1,
    )
    frames[15].save(preview, optimize=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", default="ENES YÜREKLİ")
    parser.add_argument("--role", default="UNITY OYUN GELİŞTİRİCİSİ")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--preview", type=Path, default=DEFAULT_PREVIEW)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    background = fit_background(args.input)
    frames = render_frames(background, args.name, args.role)
    save_gif(frames, args.output, args.preview)
    print(f"{len(frames)} kare oluşturuldu: {args.output}")


if __name__ == "__main__":
    main()
