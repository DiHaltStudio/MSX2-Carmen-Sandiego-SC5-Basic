#!/usr/bin/env python3
import csv
import argparse
import json
import struct
import sys
import time
import re
import urllib.parse
import urllib.request
import urllib.error
from pathlib import Path

from PIL import Image, ImageOps


ROOT = Path(__file__).resolve().parent.parent
GAME_DIR = ROOT / "src"
OUT_DIR = GAME_DIR
SRC_DIR = ROOT / "image_src"
CREDITS = ROOT / "IMG_CREDITS.CSV"
CREDIT_FIELDS = ["index", "city", "wikidata", "source_title", "label", "commons_file", "license", "author", "page"]

WIKI_TITLES = [
    "Paris",
    "London",
    "Rome",
    "Tokyo",
    "Buenos Aires",
    "New York City",
    "Oslo",
    "Cairo",
    "Madrid",
    "Berlin",
    "Moscow",
    "Beijing",
    "Sydney",
    "Rio de Janeiro",
    "Mexico City",
    "Toronto",
    "Delhi",
    "Mumbai",
    "Istanbul",
    "Athens",
    "Amsterdam",
    "Brussels",
    "Lisbon",
    "Vienna",
    "Prague",
    "Budapest",
    "Stockholm",
    "Copenhagen",
    "Helsinki",
    "Reykjavik",
    "Dublin",
    "Edinburgh",
    "Z\u00fcrich",
    "A Coru\u00f1a",
    "Marrakesh",
    "Nairobi",
    "Cape Town",
    "Lagos",
    "Dakar",
    "Dubai",
    "Doha",
    "Bangkok",
    "Singapore",
    "Hong Kong",
    "Seoul",
    "Hanoi",
    "Jakarta",
    "Auckland",
    "Lima",
    "Santiago",
]

SOURCE_TITLES = [
    "Eiffel Tower",
    "Big Ben",
    "Colosseum",
    "Mount Fuji",
    "Obelisco de Buenos Aires",
    "Statue of Liberty",
    "Oslofjord",
    "Great Pyramid of Giza",
    "Museo del Prado",
    "Brandenburg Gate",
    "Kremlin",
    "Forbidden City",
    "Sydney Opera House",
    "Christ the Redeemer (statue)",
    "Angel of Independence",
    "CN Tower",
    "Red Fort",
    "Gateway of India",
    "Hagia Sophia",
    "Parthenon",
    "Canals of Amsterdam",
    "Atomium",
    "Bel\u00e9m Tower",
    "Vienna State Opera",
    "Charles Bridge",
    "Sz\u00e9chenyi Chain Bridge",
    "Vasa Museum",
    "The Little Mermaid (statue)",
    "Helsinki Cathedral",
    "Blue Lagoon (geothermal spa)",
    "Trinity College Dublin",
    "Edinburgh Castle",
    "Lake Zurich",
    "Tower of Hercules",
    "Jemaa el-Fnaa",
    "Nairobi National Park",
    "Table Mountain",
    "National Arts Theatre",
    "African Renaissance Monument",
    "Burj Khalifa",
    "Doha Corniche",
    "Grand Palace",
    "Merlion",
    "Victoria Peak",
    "Gyeongbokgung",
    "Hoan Kiem Lake",
    "National Monument (Indonesia)",
    "Sky Tower (Auckland)",
    "Machu Picchu",
    "Andes",
]

# Default MSX palette, RGB approximations. Keep index 4 blue for the screen bg.
MSX_PALETTE = [
    (0, 0, 0),
    (0, 0, 0),
    (33, 200, 66),
    (94, 220, 120),
    (84, 85, 237),
    (125, 118, 252),
    (212, 82, 77),
    (66, 235, 245),
    (252, 85, 84),
    (255, 121, 120),
    (212, 193, 84),
    (230, 206, 128),
    (33, 176, 59),
    (201, 91, 186),
    (204, 204, 204),
    (255, 255, 255),
]

DITHER_MODES = {
    "none": Image.Dither.NONE,
    "floyd": Image.Dither.FLOYDSTEINBERG,
}


def fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "MSX2 Carmen asset builder"})
    for n in range(5):
        try:
            with urllib.request.urlopen(req, timeout=30) as res:
                return json.load(res)
        except urllib.error.HTTPError as exc:
            if exc.code != 429 or n == 4:
                raise
            time.sleep(30 + n * 30)


def download(url, path, force=False):
    if not force and path.exists() and path.stat().st_size > 0:
        return
    req = urllib.request.Request(url, headers={"User-Agent": "MSX2 Carmen asset builder"})
    for n in range(5):
        try:
            with urllib.request.urlopen(req, timeout=60) as res:
                path.write_bytes(res.read())
            return
        except urllib.error.HTTPError as exc:
            if exc.code != 429 or n == 4:
                raise
            time.sleep(30 + n * 30)


def wiki_entity_for_title(title):
    params = urllib.parse.urlencode(
        {
            "action": "wbgetentities",
            "format": "json",
            "sites": "enwiki",
            "titles": title,
            "props": "claims|labels",
            "languages": "en",
        }
    )
    data = fetch_json("https://www.wikidata.org/w/api.php?" + params)
    entities = data["entities"]
    entity = next(iter(entities.values()))
    if "missing" in entity:
        params = urllib.parse.urlencode(
            {
                "action": "wbsearchentities",
                "format": "json",
                "language": "en",
                "search": title,
                "limit": "1",
            }
        )
        data = fetch_json("https://www.wikidata.org/w/api.php?" + params)
        if not data.get("search"):
            raise RuntimeError(f"Wikidata entity not found for {title}")
        qid = data["search"][0]["id"]
        params = urllib.parse.urlencode(
            {
                "action": "wbgetentities",
                "format": "json",
                "ids": qid,
                "props": "claims|labels",
                "languages": "en",
            }
        )
        data = fetch_json("https://www.wikidata.org/w/api.php?" + params)
        entity = data["entities"][qid]
    image = entity.get("claims", {}).get("P18", [{}])[0].get("mainsnak", {}).get("datavalue", {}).get("value")
    if not image:
        raise RuntimeError(f"No P18 image for {title}")
    label = entity.get("labels", {}).get("en", {}).get("value", title)
    return entity["id"], label, image


def commons_info(filename):
    params = urllib.parse.urlencode(
        {
            "action": "query",
            "format": "json",
            "titles": "File:" + filename,
            "prop": "imageinfo",
            "iiprop": "url|extmetadata",
            "iiurlwidth": "500",
        }
    )
    data = fetch_json("https://commons.wikimedia.org/w/api.php?" + params)
    page = next(iter(data["query"]["pages"].values()))
    info = page["imageinfo"][0]
    meta = info.get("extmetadata", {})
    return {
        "thumburl": info.get("thumburl") or info["url"],
        "pageurl": info.get("descriptionurl", ""),
        "license": meta.get("LicenseShortName", {}).get("value", ""),
        "artist": meta.get("Artist", {}).get("value", ""),
        "credit": meta.get("Credit", {}).get("value", ""),
    }


def palette_image():
    pal = Image.new("P", (1, 1))
    flat = []
    for rgb in MSX_PALETTE:
        flat.extend(rgb)
    flat.extend([0, 0, 0] * (256 - len(MSX_PALETTE)))
    pal.putpalette(flat)
    return pal


def existing_source_file(source_dir, idx):
    matches = sorted(source_dir.glob(f"IMG{idx:03d}.*"))
    if not matches:
        raise FileNotFoundError(f"Missing source image for IMG{idx:03d} in {source_dir}")
    return matches[0]


def write_sc5_copy_file(src, dst, dither):
    img = Image.open(src).convert("RGB")
    img = ImageOps.fit(img, (100, 100), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
    img = img.quantize(palette=palette_image(), dither=dither)
    pix = list(img.getdata())
    data = bytearray(struct.pack("<HH", 100, 100))
    for y in range(100):
        row = pix[y * 100 : (y + 1) * 100]
        for x in range(0, 100, 2):
            data.append(((row[x] & 15) << 4) | (row[x + 1] & 15))
    dst.write_bytes(data)


def city_names():
    lines = (GAME_DIR / "CITIES.DAT").read_text(encoding="ascii").splitlines()
    return lines[1:]


def clean_html(value):
    value = re.sub("<[^<]+?>", "", value or "")
    return " ".join(value.split())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=len(WIKI_TITLES))
    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--source-dir", type=Path, default=SRC_DIR)
    parser.add_argument("--credits", type=Path, default=CREDITS)
    parser.add_argument("--force-download", action="store_true")
    parser.add_argument("--force-sc5", action="store_true")
    parser.add_argument("--local-only", action="store_true")
    parser.add_argument("--dither", choices=sorted(DITHER_MODES), default="none")
    parser.add_argument("--sleep", type=float, default=0.0)
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    args.source_dir.mkdir(parents=True, exist_ok=True)
    rows_by_index = {}
    if args.credits.exists():
        with args.credits.open("r", newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                row = {key: row.get(key, "") for key in CREDIT_FIELDS}
                rows_by_index[row["index"]] = row
    names = city_names()
    if len(names) != len(SOURCE_TITLES):
        raise RuntimeError("CITIES.DAT count does not match SOURCE_TITLES")

    for idx, (game_name, title) in enumerate(zip(names, SOURCE_TITLES), 1):
        if idx < args.start:
            continue
        if idx > args.limit:
            break
        print(f"{idx:03d} {game_name} -> {title}", flush=True)
        row = rows_by_index.get(f"{idx:03d}", {})
        out = OUT_DIR / f"IMG{idx:03d}.SC5"
        if args.local_only:
            src = existing_source_file(args.source_dir, idx)
            if not (args.force_sc5 or not out.exists()):
                continue
            write_sc5_copy_file(src, out, DITHER_MODES[args.dither])
            continue
        if row.get("commons_file"):
            qid = row.get("wikidata", "")
            label = row.get("label", "")
            image_name = row["commons_file"]
        else:
            qid, label, image_name = wiki_entity_for_title(title)
        info = commons_info(image_name)
        src = args.source_dir / f"IMG{idx:03d}{Path(urllib.parse.urlparse(info['thumburl']).path).suffix or '.jpg'}"
        download(info["thumburl"], src, args.force_download)
        if args.force_sc5 or not out.exists():
            write_sc5_copy_file(src, out, DITHER_MODES[args.dither])
        rows_by_index[f"{idx:03d}"] = {
            "index": f"{idx:03d}",
            "city": game_name,
            "wikidata": qid,
            "source_title": title,
            "label": label,
            "commons_file": image_name,
            "license": info["license"],
            "author": clean_html(info["artist"])[:160],
            "page": info["pageurl"],
        }
        rows = [rows_by_index[k] for k in sorted(rows_by_index)]
        with args.credits.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CREDIT_FIELDS)
            writer.writeheader()
            writer.writerows(rows)
        if args.sleep > 0:
            time.sleep(args.sleep)

    rows = [rows_by_index[k] for k in sorted(rows_by_index)]
    with args.credits.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CREDIT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
