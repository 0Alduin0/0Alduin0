#!/usr/bin/env python3
"""Unity temalı GitHub profil kapağını güvenli ölçülerle animasyonlu üret."""

from __future__ import annotations

import argparse
import math
import random
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

CYAN = (65, 224, 255)
VIOLET = (148, 111, 255)
AMBER = (255, 178, 91)
WHITE = (239, 248, 255)
MUTED = (151, 174, 201)


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
    fill: tuple[int, int, int],
    glow: tuple[int, int, int],
    blur: int = 10,
) -> None:
    halo = Image.new("RGBA", image.size, (0, 0, 0, 0))
    ImageDraw.Draw(halo).text(xy, text, font=font, fill=(*glow, 170))
    image.alpha_composite(halo.filter(ImageFilter.GaussianBlur(blur)))
    ImageDraw.Draw(image).text(xy, text, font=font, fill=(*fill, 255))


def draw_chips(draw: ImageDraw.ImageDraw) -> None:
    chips = (("UNITY", CYAN), ("C#", VIOLET), ("OYUN SİSTEMLERİ", AMBER), ("PERFORMANS", CYAN))
    font = find_font(10, bold=True, mono=True)
    x, y = 61, 278
    limit = 536
    for label, color in chips:
        box = draw.textbbox((0, 0), label, font=font)
        chip_width = box[2] - box[0] + 20
        if x + chip_width > limit:
            x = 61
            y += 34
        draw.rounded_rectangle((x, y, x + chip_width, y + 27), radius=8, fill=(7, 19, 39, 238), outline=(*color, 230))
        draw.text((x + 10, y + 7), label, font=font, fill=(*WHITE, 255))
        x += chip_width + 8


def make_static_layer(background: Image.Image, name: str, role: str) -> Image.Image:
    image = background.copy()

    shade = Image.new("RGBA", image.size, (0, 0, 0, 0))
    shade_draw = ImageDraw.Draw(shade)
    for x in range(650):
        alpha = max(0, int(205 * (1 - x / 650)))
        shade_draw.line((x, 0, x, HEIGHT), fill=(2, 7, 18, alpha))
    image.alpha_composite(shade)

    draw = ImageDraw.Draw(image, "RGBA")
    draw.rounded_rectangle((34, 34, 568, 356), radius=22, fill=(3, 10, 25, 190), outline=(*CYAN, 78))
    draw.rounded_rectangle((46, 46, 556, 344), radius=16, outline=(*VIOLET, 48))

    mono_11 = find_font(11, bold=True, mono=True)
    mono_13 = find_font(13, mono=True)
    role_font = fitted_font(role.upper(), 18, 476, bold=True)
    name_font = fitted_font(name.upper(), 45, 476, bold=True)

    draw.ellipse((61, 60, 69, 68), fill=(*CYAN, 240))
    draw.text((79, 57), "UNITY://PLAY_MODE", font=mono_11, fill=(*MUTED, 225))
    status = "SAHNE HAZIR"
    status_font = fitted_font(status, 11, 110, bold=True, mono=True)
    draw.text((436, 57), status, font=status_font, fill=(*CYAN, 235))

    draw.text((61, 94), "MERHABA, BEN", font=mono_13, fill=(*CYAN, 245))
    glow_text(image, (58, 116), name.upper(), name_font, WHITE, CYAN, blur=11)
    draw.text((61, 171), role.upper(), font=role_font, fill=(*MUTED, 245))

    draw.rounded_rectangle((60, 207, 542, 260), radius=10, fill=(4, 16, 34, 225), outline=(*CYAN, 70))
    draw.text((75, 217), "oyun@gelistirme", font=mono_11, fill=(*AMBER, 250))
    draw.text((188, 217), ":~$", font=mono_11, fill=(*MUTED, 225))

    draw_chips(draw)
    return image


def make_particles() -> list[tuple[float, float, float, float, int]]:
    rng = random.Random(22072004)
    return [
        (rng.uniform(52, 548), rng.uniform(48, 340), rng.uniform(6, 18), rng.uniform(0, math.tau), rng.choice((1, 1, 2)))
        for _ in range(14)
    ]


def render_frames(background: Image.Image, name: str, role: str) -> list[Image.Image]:
    static = make_static_layer(background, name, role)
    particles = make_particles()
    command_font = find_font(14, bold=True, mono=True)
    messages = (
        "oyun mekaniği geliştiriyorum",
        "performansı ölçüyorum",
        "oyuncu hissini iyileştiriyorum",
    )
    frames: list[Image.Image] = []
    segment = FRAME_COUNT // len(messages)

    for frame_index in range(FRAME_COUNT):
        image = static.copy()
        draw = ImageDraw.Draw(image, "RGBA")
        progress = frame_index / FRAME_COUNT

        for x0, y0, speed, phase, radius in particles:
            x = x0 + math.sin(progress * math.tau + phase) * 4
            y = 48 + ((y0 - 48 - progress * speed) % 292)
            pulse = 0.5 + 0.5 * math.sin(progress * math.tau * 2 + phase)
            color = CYAN if int(phase * 10) % 2 == 0 else VIOLET
            draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(*color, int(25 + 65 * pulse)))

        message_index = min(len(messages) - 1, frame_index // segment)
        local_frame = frame_index % segment
        message = messages[message_index]
        typing_frames = max(8, segment - 5)
        visible = round(len(message) * min(1, local_frame / typing_frames))
        command = message[:visible]
        draw.rectangle((74, 237, 525, 254), fill=(4, 16, 34, 245))
        draw.text((75, 237), command, font=command_font, fill=(*WHITE, 250))
        if (frame_index // 4) % 2 == 0:
            cursor_x = min(525, 75 + draw.textlength(command, font=command_font) + 2)
            draw.rectangle((cursor_x, 239, min(533, cursor_x + 7), 253), fill=(*CYAN, 230))

        scan_x = 610 + int((frame_index % 30) / 29 * 330)
        glow = Image.new("RGBA", image.size, (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow)
        glow_draw.line((scan_x, 55, scan_x, 350), fill=(*CYAN, 28), width=2)
        image.alpha_composite(glow.filter(ImageFilter.GaussianBlur(8)))

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
