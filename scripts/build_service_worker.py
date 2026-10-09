#!/usr/bin/env python3
"""Construit le service worker avec toutes les ressources statiques existantes."""
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
FILES = [
    "./", "./index.html", "./manifest.webmanifest", "./icon-192.png", "./icon-512.png",
    "./credits.html", "./assets/crest-overrides.js", "./assets/player-portraits.js",
    "./assets/legends-data.js", "./assets/legend-photo-map.js",
    "./assets/academy-enhancements.js", "./assets/academy.css",
]
for folder in ("player-portraits", "legends", "club-crests"):
    for path in sorted((ASSETS / folder).rglob("*")):
        if path.is_file():
            FILES.append("./" + path.relative_to(ROOT).as_posix())

missing = [p for p in FILES if not (ROOT / p.removeprefix("./")).is_file() and p != "./"]
if missing:
    raise SystemExit("Missing service-worker resources: " + ", ".join(missing))

digest = sha256()
for rel in FILES:
    digest.update(rel.encode())
    path = ROOT / rel.removeprefix("./")
    if path.is_file():
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                digest.update(chunk)
cache = "hv-foot-" + digest.hexdigest()[:12]
file_json = json.dumps(FILES, ensure_ascii=False, separators=(",", ":"))
worker = f'''const CACHE={json.dumps(cache)};
const FILES={file_json};
self.addEventListener("install",event=>{{event.waitUntil(caches.open(CACHE).then(cache=>cache.addAll(FILES)).then(()=>self.skipWaiting()));}});
self.addEventListener("activate",event=>{{event.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(key=>key.startsWith("hv-foot-")&&key!==CACHE).map(key=>caches.delete(key)))).then(()=>self.clients.claim()));}});
self.addEventListener("fetch",event=>{{if(event.request.method!=="GET")return;const url=new URL(event.request.url);if(url.hostname==="cdnjs.cloudflare.com"||url.hostname.endsWith("gstatic.com")||url.hostname==="fonts.googleapis.com"){{event.respondWith(caches.match(event.request).then(hit=>hit||fetch(event.request).then(response=>{{const copy=response.clone();caches.open(CACHE).then(cache=>cache.put(event.request,copy));return response;}})));return;}}if(url.origin!==location.origin)return;event.respondWith(fetch(event.request).then(response=>{{const copy=response.clone();caches.open(CACHE).then(cache=>cache.put(event.request,copy));return response;}}).catch(()=>caches.match(event.request).then(hit=>hit||caches.match("./index.html"))));}});
'''
(ROOT / "sw.js").write_text(worker, encoding="utf-8")
print(f"Generated sw.js: {len(FILES)} resources, cache {cache}")
