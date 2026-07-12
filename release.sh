#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_DIR="${1:-"$ROOT_DIR/src"}"
DIST_DIR="${2:-"$ROOT_DIR/dist"}"
DSK_FILE="${3:-"$DIST_DIR/CARMENSANDIEGO_MSX2.dsk"}"

for tool in mcopy mdel mdir sjasm; do
    if ! command -v "$tool" >/dev/null 2>&1; then
        echo "Missing required tool: $tool" >&2
        exit 1
    fi
done

(
    cd "$ROOT_DIR"
    sjasm tools/FONT6.ASM "$SRC_DIR/FONT6.BIN" /dev/null
    rm -f "$SRC_DIR/FONT6.lst"
)

if [ ! -d "$SRC_DIR" ]; then
    echo "Source directory not found: $SRC_DIR" >&2
    exit 1
fi

if [ ! -f "$DSK_FILE" ]; then
    echo "Disk image not found: $DSK_FILE" >&2
    exit 1
fi

mdel -i "$DSK_FILE" ::* >/dev/null 2>&1 || true
mcopy -i "$DSK_FILE" "$SRC_DIR"/* ::

echo "Updated $DSK_FILE"
mdir -i "$DSK_FILE" ::
