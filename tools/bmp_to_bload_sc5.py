#!/usr/bin/env python3
"""Build complete SCREEN 5 banks plus a separate MSX BASIC palette file."""

from __future__ import annotations

import argparse
import struct
from pathlib import Path

from PIL import Image


WIDTH = 256
HEIGHT = 256
VRAM_SIZE = WIDTH * HEIGHT // 2
PALETTE_ADDRESS = 0x7680
PALETTE_ENTRIES = 16
PALETTE_FILENAME = "GAMEPAL.SC5"


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Convert indexed 256x256 BMP files sharing one 16-colour palette "
            'to BLOAD files without overwriting Y=237; also write GAMEPAL.SC5.'
        )
    )
    parser.add_argument("inputs", nargs="+", type=Path, help="indexed 256x256 BMP files")
    parser.add_argument(
        "-o", "--output-dir", type=Path, default=Path("res"),
        help="output directory (default: res)",
    )
    return parser.parse_args()


def load_bmp(path: Path) -> tuple[bytes, tuple[tuple[int, int, int], ...]]:
    with Image.open(path) as image:
        if image.format != "BMP":
            raise ValueError(f"{path}: not a BMP file")
        if image.mode != "P":
            raise ValueError(f"{path}: must be indexed (P mode), got {image.mode}")
        if image.size != (WIDTH, HEIGHT):
            raise ValueError(
                f"{path}: expected {WIDTH}x{HEIGHT}, got {image.width}x{image.height}"
            )
        raw_palette = image.getpalette()
        if raw_palette is None or len(raw_palette) < PALETTE_ENTRIES * 3:
            raise ValueError(f"{path}: does not contain a 16-colour palette")
        palette = tuple(
            tuple(raw_palette[index:index + 3])
            for index in range(0, PALETTE_ENTRIES * 3, 3)
        )
        pixels = image.tobytes()

    if max(pixels) >= PALETTE_ENTRIES:
        raise ValueError(f"{path}: contains a palette index greater than 15")
    return pixels, palette


def msx_level(channel: int) -> int:
    """Round an RGB8 channel to the nearest V9938 RGB3 level."""
    return (channel * 7 + 127) // 255


def encode_palette(palette: tuple[tuple[int, int, int], ...]) -> bytes:
    encoded = bytearray()
    for red, green, blue in palette:
        r, g, b = (msx_level(channel) for channel in (red, green, blue))
        encoded.extend(((r << 4) | b, g))  # V9938: 0RRR0BBB, 00000GGG
    return bytes(encoded)


def encode_vram(pixels: bytes) -> bytes:
    vram = bytearray(VRAM_SIZE)
    for source in range(0, len(pixels), 2):
        vram[source // 2] = (pixels[source] << 4) | pixels[source + 1]
    return bytes(vram)


def bload_data(data: bytes, start: int) -> bytes:
    header = struct.pack("<BHHH", 0xFE, start, start + len(data) - 1, 0x0000)
    return header + data


def main() -> int:
    args = arguments()
    loaded = [(path, *load_bmp(path)) for path in args.inputs]
    reference_palette = loaded[0][2]
    for path, _, palette in loaded[1:]:
        if palette != reference_palette:
            raise ValueError(f"{path}: palette differs from {loaded[0][0]}")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    for source, pixels, _palette in loaded:
        destination = args.output_dir / f"{source.stem}.SC5"
        destination.write_bytes(bload_data(encode_vram(pixels), 0x0000))
        print(f"{source} -> {destination} ({destination.stat().st_size} bytes)")

    palette_destination = args.output_dir / PALETTE_FILENAME
    palette_destination.write_bytes(
        bload_data(encode_palette(reference_palette), PALETTE_ADDRESS)
    )
    print(
        f"Shared palette -> {palette_destination} "
        f"({palette_destination.stat().st_size} bytes)"
    )

    print("Shared palette (BMP RGB8 -> V9938 RGB3):")
    for index, rgb in enumerate(reference_palette):
        rgb3 = tuple(msx_level(channel) for channel in rgb)
        print(f"  {index:2}: {rgb} -> {rgb3}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
