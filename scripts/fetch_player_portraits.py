#!/usr/bin/env python3
"""Download 100 reusable player portraits from Wikimedia Commons for Hak Vision.

The selection is deterministic: requested stars first, then the highest-rated
player of each club that already has a real roster, then further roster players
round-robin until the target is met. Only images with CC BY, CC BY-SA, CC0, or
Public Domain metadata are accepted. Every image is recorded in a credit CSV.
"""
from __future__ import annotations
import argparse
import csv
import html
import io
import json
import re
import time
import unicodedata
from pathlib import Path
from urllib.parse import quote

import requests
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
OUT = ROOT / "assets" / "player-portraits"
API = "https://commons.wikimedia.org/w/api.php"
USER_AGENT = "HakVisionFootballSimulator/1.0 (https://github.com/HAKEEM243/Hakvision-Football-simulator)"
STARS = [
    "Lionel Messi",
    "Cristiano Ronaldo",
    "Neymar",
    "Kylian Mbappé",
    "Vinícius Júnior",
    "Erling Haaland",
]
# For the six requested stars, pin Commons file pages that visibly name the subject.
PINNED = {
    "Erling Haaland": "File:Erling Haaland 2023 (cropped).jpg",
    "Lionel Messi": "File:Lionel-Messi-Argentina-2022-FIFA-World-Cup (cropped).jpg",
    "Cristiano Ronaldo": "File:Cristiano Ronaldo Croatia v Portugal 2 July 2026-075 (cropped).jpg",
    "Neymar": "File:Neymar at 2026 FIFA World Cup by YantsImages (cropped).jpg",
    "Kylian Mbappé": "File:Kylian Mbappé (cropped).jpg",
    "Vinícius Júnior": "File:Vinícius Júnior - Real Madrid CF (2024-25).jpg",
}


def norm(value: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", value.casefold()) if c.isalnum())


def clean_html(value: str) -> str:
    value = re.sub(r"<br\s*/?>", " ", value or "", flags=re.I)
    value = re.sub(r"<[^>]*>", " ", value)
    return re.sub(r"\s+", " ", html.unescape(value)).strip()


def extract_template(text: str, name: str) -> str:
    marker = f"const {name}=`"
    start = text.index(marker) + len(marker)
    end = text.index("`;", start)
    return text[start:end]


def read_game_data():
    text = INDEX.read_text(encoding="utf-8")
    start = text.index("const CRESTS=") + len("const CRESTS=")
    crests, _ = json.JSONDecoder().raw_decode(text[start:])
    start = text.index("const ASSET_ALIAS=") + len("const ASSET_ALIAS=")
    aliases, _ = json.JSONDecoder().raw_decode(text[start:])
    players = []
    for key in ("PLAYERS_RAW", "PLAYERS_EXTRA"):
        team = ""
        for line in extract_template(text, key).splitlines():
            line = line.strip()
            if not line:
                continue
            if line.startswith("@"):
                team = line[1:].strip()
                continue
            fields = line.split("|")
            if len(fields) < 5 or not fields[2].isdigit():
                continue
            players.append({
                "team": team,
                "name": fields[0].strip(),
                "position": fields[1].strip(),
                "rating": int(fields[2]),
                "birth": fields[3].strip(),
                "nation": fields[4].strip(),
            })
    return list(crests), aliases, players


def build_candidates(crest_keys, aliases, players):
    by_team = {}
    by_name = {}
    for player in players:
        by_name.setdefault(norm(player["name"]), []).append(player)
        crest_key = aliases.get(player["team"], player["team"])
        if crest_key in crest_keys:
            by_team.setdefault(crest_key, []).append(player)
    for records in by_team.values():
        records.sort(key=lambda p: (-p["rating"], norm(p["name"])))

    ordered = []
    seen = set()
    # The specifically requested global stars are always considered first.
    for name in STARS:
        matches = by_name.get(norm(name), [])
        if matches:
            player = max(matches, key=lambda p: p["rating"])
            key = norm(player["name"])
            if key not in seen:
                ordered.append(player)
                seen.add(key)
        else:
            print(f"WARNING: requested star not found in game data: {name}")

    # Round-robin roster depth: first the best player at each crested club,
    # then each club's second-best, etc. This keeps the portraits diverse.
    max_depth = max((len(v) for v in by_team.values()), default=0)
    for depth in range(max_depth):
        for crest_key in crest_keys:
            records = by_team.get(crest_key, [])
            if depth >= len(records):
                continue
            player = records[depth]
            key = norm(player["name"])
            if key not in seen:
                ordered.append(player)
                seen.add(key)
    return ordered, len(by_team)


def license_ok(short_name: str) -> bool:
    s = short_name.casefold().strip()
    if any(x in s for x in ("-nc", " noncommercial", "-nd", " no derivatives")):
        return False
    return s == "cc0" or "public domain" in s or bool(re.match(r"cc by(?:-sa)?(?:\s|$)", s))


def license_url_from(short_name: str) -> str:
    value = short_name.strip()
    if value.casefold() == "cc0":
        return "https://creativecommons.org/publicdomain/zero/1.0/"
    if "public domain" in value.casefold():
        return "https://commons.wikimedia.org/wiki/Commons:Licensing"
    match = re.fullmatch(r"CC BY(-SA)?\s+(\d+(?:\.\d+)*)", value, flags=re.I)
    if match:
        license_type = "by-sa" if match.group(1) else "by"
        return f"https://creativecommons.org/licenses/{license_type}/{match.group(2)}/"
    return "https://commons.wikimedia.org/wiki/Commons:Licensing"


def image_info(session: requests.Session, title: str):
    params = {
        "action": "query", "titles": title, "prop": "imageinfo",
        "iiprop": "url|extmetadata", "iiurlwidth": 420,
        "format": "json", "formatversion": 2, "maxlag": 5,
    }
    response = session.get(API, params=params, timeout=30)
    response.raise_for_status()
    pages = response.json().get("query", {}).get("pages", [])
    return pages[0] if pages and pages[0].get("imageinfo") else None


def search_candidates(session: requests.Session, name: str):
    params = {
        "action": "query", "generator": "search",
        "gsrsearch": f"{name} football player", "gsrnamespace": 6,
        "gsrlimit": 20, "prop": "imageinfo", "iiprop": "url|extmetadata",
        "iiurlwidth": 420, "format": "json", "formatversion": 2,
        "maxlag": 5,
    }
    response = session.get(API, params=params, timeout=30)
    response.raise_for_status()
    return (response.json().get("query") or {}).get("pages", [])


def eligible_page(page, name: str):
    ii = (page.get("imageinfo") or [{}])[0]
    metadata = ii.get("extmetadata") or {}
    license_name = clean_html(metadata.get("LicenseShortName", {}).get("value", ""))
    artist = clean_html(metadata.get("Artist", {}).get("value", ""))
    attribution = clean_html(metadata.get("Attribution", {}).get("value", "")) or clean_html(metadata.get("Credit", {}).get("value", "")) or artist
    title = page.get("title", "")
    if not license_ok(license_name) or not artist:
        return None
    title_norm = norm(title)
    tokens = [norm(x) for x in name.split() if len(norm(x)) > 1]
    if not tokens or not all(token in title_norm for token in tokens):
        return None
    low = title.casefold()
    if any(word in low for word in ("statue", "wax figure", "figurine", "mural", "painting", "poster", "group photo", "team photo")):
        return None
    score = 100 + (25 if "cropped" in low or "portrait" in low else 0)
    score += 10 if "202" in low else 0
    info = {
        "title": title,
        "artist": artist,
        "attribution": attribution,
        "license": license_name,
        "license_url": clean_html(metadata.get("LicenseUrl", {}).get("value", "")) or license_url_from(license_name),
        "source_url": ii.get("descriptionurl", ""),
        "image_url": ii.get("thumburl") or ii.get("url", ""),
        "description": clean_html(metadata.get("ImageDescription", {}).get("value", "")),
        "score": score,
    }
    return info


def save_image(data: bytes, output: Path):
    with Image.open(io.BytesIO(data)) as raw:
        image = ImageOps.exif_transpose(raw)
        image.thumbnail((560, 560), Image.Resampling.LANCZOS)
        has_alpha = image.mode in ("RGBA", "LA") or "transparency" in image.info
        if has_alpha:
            image = image.convert("RGBA")
            output = output.with_suffix(".png")
            image.save(output, format="PNG", optimize=True)
        else:
            image = image.convert("RGB")
            output = output.with_suffix(".jpg")
            image.save(output, format="JPEG", quality=88, optimize=True, progressive=True)
    return output


def slug(value: str) -> str:
    s = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-") or "player"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--max-candidates", type=int, default=500)
    args = parser.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    crest_keys, aliases, players = read_game_data()
    candidates, covered_teams = build_candidates(set(crest_keys), aliases, players)
    print(f"Données du jeu: {len(players)} joueurs, {covered_teams} clubs avec roster et écusson; {len(candidates)} candidats ordonnés.")

    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT, "Accept": "application/json"})
    selected = []
    seen = set()
    attempts = 0
    for player in candidates:
        if len(selected) >= args.limit or attempts >= args.max_candidates:
            break
        player_key = norm(player["name"])
        if player_key in seen:
            continue
        seen.add(player_key)
        attempts += 1
        try:
            page = None
            pin = PINNED.get(player["name"])
            if pin:
                page = image_info(session, pin)
                info = eligible_page(page, player["name"]) if page else None
                pages = [page] if info else search_candidates(session, player["name"])
            else:
                pages = search_candidates(session, player["name"])
                info = None
            if not info:
                ranked = []
                for result in pages:
                    candidate = eligible_page(result, player["name"])
                    if candidate:
                        ranked.append((candidate["score"], candidate, result))
                if ranked:
                    _, info, page = max(ranked, key=lambda x: x[0])
            if not info:
                if attempts % 20 == 0:
                    print(f"Progression: {len(selected)}/{args.limit} retenus après {attempts} recherches")
                time.sleep(0.2)
                continue

            # Use the already selected image-search file for Haaland, otherwise
            # download the Commons thumbnail to a compact, aspect-preserving file.
            local_source = ROOT / "assets" / "player-portraits" / "erling-haaland.jpg"
            if player["name"] == "Erling Haaland" and local_source.exists():
                data = local_source.read_bytes()
            else:
                response = session.get(info["image_url"], timeout=40)
                response.raise_for_status()
                data = response.content
            filename = f"{len(selected)+1:03d}-{slug(player['name'])}"
            output = save_image(data, OUT / (filename + ".jpg"))
            record = {
                "index": len(selected) + 1,
                "player": player["name"],
                "game_team": player["team"],
                "rating": player["rating"],
                "nation": player["nation"],
                "image_file": output.relative_to(ROOT).as_posix(),
                "commons_title": info["title"],
                "author": info["artist"],
                "attribution": info["attribution"],
                "license": info["license"],
                "license_url": info["license_url"],
                "source_url": info["source_url"],
                "original_image_url": info["image_url"],
                "adaptation": "Redimensionné sans recadrage; proportions conservées.",
            }
            selected.append(record)
            print(f"OK {len(selected):03d}/{args.limit}: {player['name']} — {player['team']} — {info['license']}")
        except Exception as exc:
            print(f"SKIP {player['name']}: {exc}")
        time.sleep(0.2)

    # Keep only assets selected by this run (plus the source copy, removed once transformed).
    keep = {Path(r["image_file"]).name for r in selected}
    for path in OUT.iterdir():
        if path.is_file() and path.name not in keep:
            path.unlink()

    fields = ["index", "player", "game_team", "rating", "nation", "image_file", "commons_title", "author", "attribution", "license", "license_url", "source_url", "original_image_url", "adaptation"]
    with (ROOT / "assets" / "player-photo-credits.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(selected)

    mapping = {r["player"]: "./" + r["image_file"] for r in selected}
    (ROOT / "assets" / "player-portraits.js").write_text(
        "// Generated from the credited portrait files in player-photo-credits.csv.\n"
        "window.HV_PLAYER_PHOTOS = Object.freeze(" + json.dumps(mapping, ensure_ascii=False, indent=2) + ");\n",
        encoding="utf-8",
    )
    print(f"Finished: {len(selected)} licensed portraits selected from {attempts} candidates.")
    if len(selected) < args.limit:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
