#!/usr/bin/env python3
"""Insert ASCII 32..93 from round_6x6.png into indexed VRAM3.bmp."""

from __future__ import annotations

import argparse
import struct
from pathlib import Path

from PIL import Image


FIRST = 32
LAST = 93
CELL = 6
DEST_X = 0
DEST_Y = 152
DEST_COLUMNS = 42


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="78x42 round_6x6.png")
    parser.add_argument("destination", type=Path, help="indexed 256x256 4-bit BMP")
    return parser.parse_args()


def source_cells() -> dict[str, tuple[int, int]]:
    cells: dict[str, tuple[int, int]] = {}
    for index, char in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
        cells[char] = (index % 13, index // 13)
    for index, char in enumerate("abcdefghijklmnopqrstuvwxyz"):
        cells[char] = (index % 13, 2 + index // 13)
    for index, char in enumerate("0123456789"):
        cells[char] = (index, 4)
    cells.update(
        {
            "+": (10, 4), "-": (11, 4), "=": (12, 4),
            "(": (0, 5), ")": (1, 5), "[": (2, 5), "]": (3, 5),
            "{": (4, 5), "}": (5, 5), "<": (6, 5), ">": (7, 5),
            "/": (8, 5), "*": (9, 5), ":": (10, 5), "#": (11, 5),
            "%": (12, 5), "!": (0, 6), "?": (1, 6), ".": (2, 6),
            ",": (3, 6), "'": (4, 6), '"': (5, 6), "@": (6, 6),
            "&": (7, 6), "$": (8, 6),
        }
    )
    return cells


def read_glyph(source: Image.Image, cell: tuple[int, int]) -> list[list[int]]:
    cx, cy = cell
    return [
        [1 if source.getpixel((cx * CELL + x, cy * CELL + y)) != (0, 0, 0) else 0
         for x in range(CELL)]
        for y in range(CELL)
    ]


def glyphs(source: Image.Image) -> dict[str, list[list[int]]]:
    result = {char: read_glyph(source, cell) for char, cell in source_cells().items()}
    result[" "] = [[0] * CELL for _ in range(CELL)]

    # The source atlas has no semicolon or Spanish ENE.  In this game the
    # backslash character (ASCII 92) is deliberately used to encode ENE.
    result[";"] = [row[:] for row in result[":"]]
    result[";"][4] = result[","][4][:]
    result[";"][5] = result[","][5][:]
    result["\\"] = [[0, 1, 0, 1, 0, 0]] + [row[:] for row in result["N"][:5]]
    return result


def bmp_layout(data: bytearray) -> tuple[int, int, int, int]:
    if data[:2] != b"BM":
        raise ValueError("destination is not a BMP")
    pixel_offset = struct.unpack_from("<I", data, 10)[0]
    width, height = struct.unpack_from("<ii", data, 18)
    bits = struct.unpack_from("<H", data, 28)[0]
    if (width, height, bits) != (256, 256, 4):
        raise ValueError(f"expected a 256x256 4-bit BMP, got {width}x{height} {bits}-bit")
    stride = ((width * bits + 31) // 32) * 4
    return pixel_offset, width, height, stride


def set_index(data: bytearray, layout: tuple[int, int, int, int], x: int, y: int, value: int) -> None:
    pixel_offset, _, height, stride = layout
    offset = pixel_offset + (height - 1 - y) * stride + x // 2
    if x % 2 == 0:
        data[offset] = (data[offset] & 0x0F) | (value << 4)
    else:
        data[offset] = (data[offset] & 0xF0) | value


def main() -> int:
    args = arguments()
    with Image.open(args.source) as image:
        if image.size != (78, 42):
            raise ValueError(f"expected a 78x42 source atlas, got {image.size}")
        source = image.convert("RGB")
    font = glyphs(source)

    data = bytearray(args.destination.read_bytes())
    layout = bmp_layout(data)
    for code in range(FIRST, LAST + 1):
        char = chr(code)
        glyph = font[char]
        index = code - FIRST
        dx = DEST_X + (index % DEST_COLUMNS) * CELL
        dy = DEST_Y + (index // DEST_COLUMNS) * CELL
        for y, row in enumerate(glyph):
            for x, value in enumerate(row):
                set_index(data, layout, dx + x, dy + y, value)

    args.destination.write_bytes(data)
    print(f"Inserted ASCII {FIRST}..{LAST} at ({DEST_X},{DEST_Y}) in {args.destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
