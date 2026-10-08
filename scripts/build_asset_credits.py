#!/usr/bin/env python3
"""Build a human-readable HTML credits page from the asset manifests."""
import csv
import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAYERS = ROOT / "assets/player-photo-credits.csv"
CRESTS = ROOT / "assets/club-crest-credits.csv"
OUT = ROOT / "credits.html"


def e(value):
    return html.escape(str(value or ""), quote=True)


def read_csv(path):
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def canon(value):
    return re.sub(r"[^a-z0-9]+", "", (value or "").casefold())


def player_credit(row):
    author = (row.get("author") or "").strip()
    attribution = (row.get("attribution") or "").strip()
    if attribution.casefold() in {"", "own work", "unknown author", "unknown"}:
        return author or "Aucun auteur indiqué"
    if canon(author) and canon(author) not in canon(attribution):
        if author.casefold().startswith("unknown author"):
            return attribution
        return f"{attribution} — {author}"
    return attribution


def link(url, text):
    if not url:
        return e(text)
    return f'<a href="{e(url)}" target="_blank" rel="noopener noreferrer">{e(text)}</a>'


players = read_csv(PLAYERS)
crests = read_csv(CRESTS)
player_rows = []
for row in players:
    image = "./" + row["image_file"].lstrip("./")
    source = link(row.get("source_url"), "Fichier source")
    license_link = link(row.get("license_url"), row.get("license") or "Licence")
    player_rows.append(
        "<tr>"
        f'<td>{int(row["index"]):03d}</td>'
        f'<td><img class="portrait" src="{e(image)}" loading="lazy" alt="Portrait de {e(row["player"])}"></td>'
        f'<td><strong>{e(row["player"])}</strong><br><small>{e(row["game_team"])}</small></td>'
        f'<td>{e(player_credit(row))}<br><small>Auteur Commons : {e(row.get("author") or "non indiqué")}</small></td>'
        f'<td>{license_link}</td>'
        f'<td>{source}<br><small>{e(row.get("commons_title"))}</small></td>'
        "</tr>"
    )

crest_rows = []
for row in crests:
    source = link(row.get("source_url"), "Source")
    profile = link(row.get("source_profile_url"), "Fiche source") if row.get("source_profile_url") else ""
    crest_rows.append(
        "<tr>"
        f'<td>{e(row.get("position_grille"))}</td>'
        f'<td><strong>{e(row.get("club_demande"))}</strong><br><small>{e(row.get("club_source"))}</small></td>'
        f'<td>{e(row.get("asset_location"))}</td>'
        f'<td>{source} {profile}</td>'
        f'<td>{e(row.get("license_or_rights_note"))}<br><small>{e(row.get("verification_status"))}</small></td>'
        "</tr>"
    )

page = f'''<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Crédits des portraits et écussons — Hak Vision</title>
<style>
:root{{color-scheme:dark;--bg:#081414;--panel:#102222;--line:#34504a;--text:#edf1e8;--muted:#aab8b0;--gold:#e9c75c}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.5 system-ui,-apple-system,Segoe UI,sans-serif}}
main{{max-width:1200px;margin:0 auto;padding:26px 18px 60px}}h1,h2{{line-height:1.2}}h1{{color:var(--gold)}}h2{{margin-top:36px}}p,li{{color:var(--muted)}}a{{color:#b6dcff}}.notice{{background:#302a13;border:1px solid #86743a;border-radius:10px;padding:14px 16px;color:#f1e3aa}}
.table-wrap{{overflow:auto;border:1px solid var(--line);border-radius:10px;background:var(--panel)}}table{{border-collapse:collapse;width:100%;min-width:800px}}th,td{{padding:9px 10px;text-align:left;vertical-align:middle;border-bottom:1px solid #ffffff12}}th{{position:sticky;top:0;background:#19302e;color:var(--gold);font-size:12px}}td small{{color:var(--muted)}}tr:last-child td{{border-bottom:0}}.portrait{{width:42px;height:50px;object-fit:cover;border-radius:6px;display:block}}
.back{{display:inline-block;margin-bottom:16px}}footer{{margin-top:28px;color:var(--muted);font-size:13px}}
</style></head><body><main>
<a class="back" href="./index.html">← Retour au jeu</a>
<h1>Crédits des portraits et des écussons</h1>
<p>{len(players)} portraits de joueurs et {len(crests)} écussons figurent dans cette sélection du jeu.</p>
<div class="notice"><strong>À retenir :</strong> une licence de droit d’auteur ne garantit pas à elle seule le droit d’utiliser commercialement l’image d’un joueur, son nom, son image personnelle ou un écusson de club. Vérifier les règles locales et les autorisations nécessaires avant toute publication commerciale ou diffusion sur une boutique.</div>
<h2>Portraits des joueurs</h2>
<p>Les portraits ont été redimensionnés sans recadrage supplémentaire. Les licences CC BY-SA imposent de conserver la licence de partage à l’identique ou une licence compatible pour les adaptations concernées.</p>
<div class="table-wrap"><table><thead><tr><th>#</th><th>Photo</th><th>Joueur / club dans le jeu</th><th>Crédit</th><th>Licence</th><th>Source</th></tr></thead><tbody>{''.join(player_rows)}</tbody></table></div>
<h2>Écussons des clubs</h2>
<p>Les 99 écussons historiques sont intégrés au code du jeu; celui d’Estudiantes de La Plata est fourni comme fichier séparé. Les liens et réserves de droits ci-dessous correspondent aux sources consignées dans le manifeste.</p>
<div class="table-wrap"><table><thead><tr><th>#</th><th>Club</th><th>Emplacement</th><th>Source</th><th>Licence / état des droits</th></tr></thead><tbody>{''.join(crest_rows)}</tbody></table></div>
<footer>Manifeste source : <code>assets/player-photo-credits.csv</code> et <code>assets/club-crest-credits.csv</code>. Consultez aussi <code>assets/licenses/verified-sources.md</code>.</footer>
</main></body></html>'''
OUT.write_text(page, encoding="utf-8")
print(f"Generated {OUT} with {len(players)} portraits and {len(crests)} crests")
