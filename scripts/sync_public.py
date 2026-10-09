#!/usr/bin/env python3
"""Synchronise les fichiers statiques du jeu vers le dossier Cloudflare public/."""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
ROOT_FILES = ["index.html", "credits.html", "manifest.webmanifest", "sw.js", "icon-192.png", "icon-512.png"]
for rel in ROOT_FILES:
    src, dst = ROOT / rel, PUBLIC / rel
    if not src.is_file():
        raise SystemExit(f"Fichier source manquant: {src}")
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)

source_assets = ROOT / "assets"
target_assets = PUBLIC / "assets"
target_assets.mkdir(parents=True, exist_ok=True)
for src in source_assets.rglob("*"):
    rel = src.relative_to(source_assets)
    dst = target_assets / rel
    if src.is_dir():
        dst.mkdir(parents=True, exist_ok=True)
    else:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
for dst in sorted(target_assets.rglob("*"), reverse=True):
    src = source_assets / dst.relative_to(target_assets)
    if not src.exists():
        if dst.is_dir():
            shutil.rmtree(dst)
        else:
            dst.unlink()
print(f"Synced {len(ROOT_FILES)} root files and {sum(1 for p in source_assets.rglob('*') if p.is_file())} asset files to public/")
