#!/usr/bin/env python3
"""Render the animated GitHub profile hero from a static background."""

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
FRAME_COUNT = 72
FRAME_MS = 90

CYAN = (54, 232, 255)
VIOLET = (152, 106, 255)
ORANGE = (255, 155, 70)
WHITE = (236, 247, 255)
MUTED = (143, 171, 199)


def find_font(size: int, *, bold: bool = False, mono: bool = False) -> ImageFont.FreeTypeFont:
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
    halo_draw = ImageDraw.Draw(halo)
    halo_draw.text(xy, text, font=font, fill=(*glow, 180))
    halo = halo.filter(ImageFilter.GaussianBlur(blur))
    image.alpha_composite(halo)
    ImageDraw.Draw(image).text(xy, text, font=font, fill=(*fill, 255))


def make_static_layer(background: Image.Image, name: str, role: str) -> Image.Image:
    image = background.copy()
    draw = ImageDraw.Draw(image, "RGBA")

    # Vignette and readable left-side command panel.
    shade = Image.new("RGBA", image.size, (0, 0, 0, 0))
    shade_draw = ImageDraw.Draw(shade)
    for x in range(650):
        alpha = max(0, int(150 * (1 - x / 650)))
        shade_draw.line((x, 0, x, HEIGHT), fill=(2, 7, 20, alpha))
    image.alpha_composite(shade)

    draw.rounded_rectangle((35, 34, 570, 354), radius=24, fill=(3, 11, 29, 176), outline=(70, 214, 255, 62), width=1)
    draw.rounded_rectangle((49, 48, 556, 340), radius=18, outline=(152, 106, 255, 38), width=1)

    # Window controls and status.
    for x, color in zip((62, 79, 96), ((255, 105, 100), (255, 190, 75), (66, 221, 126))):
        draw.ellipse((x - 4, 58, x + 4, 66), fill=(*color, 220))

    mono_11 = find_font(11, mono=True, bold=True)
    mono_13 = find_font(13, mono=True)
    mono_15 = find_font(15, mono=True, bold=True)
    sans_13 = find_font(13, bold=True)
    sans_18 = find_font(18, bold=True)
    sans_42 = find_font(42, bold=True)

    draw.text((116, 54), "PROFILE://COMMAND_CENTER", font=mono_11, fill=(*MUTED, 210))
    draw.ellipse((476, 57, 484, 65), fill=(*CYAN, 235))
    draw.text((491, 53), "ONLINE", font=mono_11, fill=(*CYAN, 235))

    draw.text((61, 90), "HELLO, WORLD. I'M", font=mono_13, fill=(*CYAN, 240))
    glow_text(image, (58, 110), name.upper(), sans_42, WHITE, CYAN, blur=11)
    draw.text((62, 164), role.upper(), font=sans_18, fill=(*MUTED, 245))

    draw.rounded_rectangle((60, 199, 544, 263), radius=11, fill=(5, 18, 43, 205), outline=(75, 197, 246, 78), width=1)
    draw.text((76, 211), "enes@portfolio", font=mono_13, fill=(*ORANGE, 245))
    draw.text((190, 211), ":~$", font=mono_13, fill=(*MUTED, 230))

    chips = (("UNITY", CYAN), ("C#", VIOLET), ("NODE.JS", ORANGE), ("FASTAPI", CYAN), ("PYTHON", VIOLET))
    x = 61
    for label, color in chips:
        bbox = draw.textbbox((0, 0), label, font=mono_11)
        width = bbox[2] - bbox[0] + 22
        draw.rounded_rectangle((x, 286, x + width, 314), radius=8, fill=(8, 24, 43, 255), outline=(*color, 255), width=1)
        draw.text((x + 11, 293), label, font=mono_11, fill=(*WHITE, 255))
        x += width + 9

    draw.line((61, 329, 392, 329), fill=(*MUTED, 55), width=1)
    draw.text((405, 321), "BUILD • MEASURE • POLISH", font=sans_13, fill=(*MUTED, 180))
    return image


def make_particles() -> list[tuple[float, float, float, float, int]]:
    rng = random.Random(22072004)
    particles = []
    for _ in range(18):
        particles.append(
            (
                rng.uniform(55, 545),
                rng.uniform(46, 332),
                rng.uniform(7, 22),
                rng.uniform(0, math.tau),
                rng.choice((1, 1, 1, 2)),
            )
        )
    return particles


def render_frames(background: Image.Image, name: str, role: str) -> list[Image.Image]:
    static = make_static_layer(background, name, role)
    particles = make_particles()
    mono_15 = find_font(15, mono=True, bold=True)
    messages = (
        "building Unity worlds",
        "shipping real-time APIs",
        "training curious agents",
    )
    frames: list[Image.Image] = []
    segment = FRAME_COUNT // len(messages)

    for frame_index in range(FRAME_COUNT):
        image = static.copy()
        draw = ImageDraw.Draw(image, "RGBA")
        progress = frame_index / FRAME_COUNT

        # Slow particles remain inside the command panel so GIF deltas stay compact.
        for x0, y0, speed, phase, radius in particles:
            x = x0 + math.sin(progress * math.tau + phase) * 5
            y = 46 + ((y0 - 46 - progress * speed) % 286)
            pulse = 0.5 + 0.5 * math.sin(progress * math.tau * 2 + phase)
            color = CYAN if int(phase * 10) % 2 == 0 else VIOLET
            draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(*color, int(32 + 85 * pulse)))

        # Holographic scan line.
        scan_y = 202 + int((frame_index % segment) / max(1, segment - 1) * 58)
        for offset, alpha in ((-2, 18), (-1, 35), (0, 105), (1, 35), (2, 18)):
            draw.line((64, scan_y + offset, 540, scan_y + offset), fill=(*CYAN, alpha), width=1)

        # Typewriter loop across three specialties.
        message_index = min(len(messages) - 1, frame_index // segment)
        local_frame = frame_index % segment
        message = messages[message_index]
        typing_frames = max(8, segment - 7)
        visible = round(len(message) * min(1, local_frame / typing_frames))
        command = message[:visible]
        draw.rectangle((75, 234, 525, 253), fill=(5, 18, 43, 245))
        draw.text((76, 234), command, font=mono_15, fill=(*WHITE, 250))
        if (frame_index // 5) % 2 == 0:
            cursor_x = 76 + draw.textlength(command, font=mono_15) + 2
            draw.rectangle((cursor_x, 236, cursor_x + 8, 252), fill=(*CYAN, 225))

        # Subtle pulse around the mascot's face without changing the illustration itself.
        pulse = (math.sin(progress * math.tau * 2) + 1) / 2
        glow = Image.new("RGBA", image.size, (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow)
        glow_draw.ellipse((625, 112, 759, 235), fill=(*CYAN, int(6 + 13 * pulse)))
        glow = glow.filter(ImageFilter.GaussianBlur(22))
        image.alpha_composite(glow)

        frames.append(image.convert("RGB"))
    return frames


def save_gif(frames: list[Image.Image], output: Path, preview: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    preview.parent.mkdir(parents=True, exist_ok=True)

    # One global palette avoids color flicker and allows compact delta frames.
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
    frames[18].save(preview, optimize=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", default="ENES YÜREKLİ")
    parser.add_argument("--role", default="GAME & BACKEND DEVELOPER")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--preview", type=Path, default=DEFAULT_PREVIEW)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    background = fit_background(args.input)
    frames = render_frames(background, args.name, args.role)
    save_gif(frames, args.output, args.preview)
    print(f"Rendered {len(frames)} frames to {args.output}")


if __name__ == "__main__":
    main()
