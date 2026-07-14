#!/usr/bin/env python3
"""Renumber an ASCII MSX BASIC listing and all of its line references."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


LINE_RE = re.compile(r"^(\d+)(?:\s(.*))?$")
BRANCH_RE = re.compile(
    r"(?i)\b(GOTO|GOSUB|RESTORE|RESUME|RETURN|RUN)\s*"
    r"(\d+(?:\s*,\s*\d+)*)"
)
THEN_RE = re.compile(r"(?i)\b(THEN|ELSE)\s*(\d+)\b")


def replace_numbers(text: str, mapping: dict[int, int]) -> str:
    def replace_list(match: re.Match[str]) -> str:
        values = re.sub(
            r"\d+",
            lambda number: str(mapping.get(int(number.group()), int(number.group()))),
            match.group(2),
        )
        return match.group(1) + " " + values

    text = BRANCH_RE.sub(replace_list, text)
    return THEN_RE.sub(
        lambda match: match.group(1)
        + " "
        + str(mapping.get(int(match.group(2)), int(match.group(2)))),
        text,
    )


def renumber_body(body: str, mapping: dict[int, int]) -> str:
    """Rewrite code while leaving quoted strings and comments untouched."""
    result: list[str] = []
    code: list[str] = []
    index = 0

    def flush_code() -> None:
        if code:
            result.append(replace_numbers("".join(code), mapping))
            code.clear()

    while index < len(body):
        char = body[index]
        if char == '"':
            flush_code()
            end = index + 1
            while end < len(body):
                if body[end] == '"':
                    end += 1
                    break
                end += 1
            result.append(body[index:end])
            index = end
            continue
        if char == "'":
            flush_code()
            result.append(body[index:])
            return "".join(result)
        if (
            body[index:index + 3].upper() == "REM"
            and (index == 0 or not (body[index - 1].isalnum() or body[index - 1] in "_$"))
            and (index + 3 == len(body) or not body[index + 3].isalnum())
        ):
            flush_code()
            result.append(body[index:])
            return "".join(result)
        code.append(char)
        index += 1

    flush_code()
    return "".join(result)


def executable_code(body: str) -> str:
    """Return only code outside quoted strings and trailing comments."""
    result: list[str] = []
    index = 0
    while index < len(body):
        char = body[index]
        if char == '"':
            index += 1
            while index < len(body) and body[index] != '"':
                index += 1
            if index < len(body):
                index += 1
            result.append(" ")
            continue
        if char == "'":
            break
        if (
            body[index:index + 3].upper() == "REM"
            and (index == 0 or not (body[index - 1].isalnum() or body[index - 1] in "_$"))
            and (index + 3 == len(body) or not body[index + 3].isalnum())
        ):
            break
        result.append(char)
        index += 1
    return "".join(result)


def parse_listing(data: bytes) -> tuple[list[tuple[int, str]], bytes]:
    data.decode("ascii")
    newline = b"\r\n" if b"\r\n" in data else b"\n"
    text = data.replace(b"\r\n", b"\n").decode("ascii")
    rows: list[tuple[int, str]] = []
    for physical, row in enumerate(text.splitlines(), 1):
        match = LINE_RE.fullmatch(row)
        if not match:
            raise ValueError(f"physical line {physical}: invalid BASIC line: {row!r}")
        rows.append((int(match.group(1)), match.group(2) or ""))
    numbers = [number for number, _ in rows]
    if numbers != sorted(numbers) or len(numbers) != len(set(numbers)):
        raise ValueError("BASIC line numbers must be unique and ascending")
    return rows, newline


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("listing", type=Path)
    parser.add_argument("--start", type=int, default=10)
    parser.add_argument("--step", type=int, default=10)
    parser.add_argument("--output", type=Path, help="default: replace the input listing")
    args = parser.parse_args()
    if args.start < 0 or args.step < 1:
        parser.error("--start must be non-negative and --step must be positive")

    rows, newline = parse_listing(args.listing.read_bytes())
    mapping = {
        old: args.start + index * args.step for index, (old, _) in enumerate(rows)
    }
    new_numbers = set(mapping.values())
    output_rows = [
        f"{mapping[old]} {renumber_body(body, mapping)}".rstrip()
        for old, body in rows
    ]

    # A second pass detects branch targets that did not exist in the source.
    for old, body in rows:
        rewritten = executable_code(renumber_body(body, mapping))
        for pattern in (BRANCH_RE, THEN_RE):
            for match in pattern.finditer(rewritten):
                group = match.group(2)
                for value in re.findall(r"\d+", group):
                    target = int(value)
                    if target not in new_numbers:
                        raise ValueError(f"line {old}: unresolved target {value}")

    destination = args.output or args.listing
    encoded_newline = newline.decode("ascii")
    destination.write_bytes(
        (encoded_newline.join(output_rows) + encoded_newline).encode("ascii")
    )
    print(
        f"Renumbered {len(rows)} lines: {rows[0][0]}..{rows[-1][0]} -> "
        f"{mapping[rows[0][0]]}..{mapping[rows[-1][0]]}"
    )


if __name__ == "__main__":
    main()
