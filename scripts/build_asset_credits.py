#!/usr/bin/env python3
"""Génère une page de crédits à partir des manifestes d’images du jeu."""
import csv
import html
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAYER_CSV = ROOT / "assets/player-photo-credits.csv"
LEGEND_CSV = ROOT / "assets/legend-photo-credits.csv"
CREST_CSV = ROOT / "assets/club-crest-credits.csv"
OUT = ROOT / "credits.html"


def e(value):
    return html.escape(str(value or ""), quote=True)


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def link(url, text):
    if not url:
        return e(text)
    return f'<a href="{e(url)}" target="_blank" rel="noopener noreferrer">{e(text)}</a>'


players = read_csv(PLAYER_CSV)
legends = read_csv(LEGEND_CSV)
crests = read_csv(CREST_CSV)

player_rows = []
for row in players:
    image = "./" + row["image_file"].lstrip("./")
    player_rows.append(
        "<tr>"
        f'<td>{int(row["index"]):03d}</td>'
        f'<td><img class="portrait" src="{e(image)}" loading="lazy" alt="Portrait de {e(row["player"])}"></td>'
        f'<td><strong>{e(row["player"])}</strong><br><small>{e(row.get("game_team"))}</small></td>'
        f'<td>{e(row.get("attribution") or row.get("author") or "Auteur non indiqué")}</td>'
        f'<td>{link(row.get("license_url"), row.get("license") or "Licence")}</td>'
        f'<td>{link(row.get("source_url"), "Fichier source")}<br><small>{e(row.get("commons_title"))}</small></td>'
        "</tr>"
    )

legend_rows = []
for row in legends:
    image = "./" + row["asset_location"].lstrip("./")
    legend_rows.append(
        "<tr>"
        f'<td><img class="portrait legend-portrait" src="{e(image)}" loading="lazy" alt="Portrait de {e(row["name"])}"></td>'
        f'<td><strong>{e(row["name"])}</strong><br><small>{e(row.get("position"))} · GEN {e(row.get("rating"))} · {e(row.get("clubs"))}</small></td>'
        f'<td>{e(row.get("credit") or row.get("author_actual") or "Auteur non indiqué")}</td>'
        f'<td>{link(row.get("license_url"), row.get("license_actual") or row.get("license") or "Licence")}</td>'
        f'<td>{link(row.get("file_page"), "Fichier Commons")}<br>{link(row.get("bio_url"), "Biographie")}</td>'
        "</tr>"
    )

crest_rows = []
for row in crests:
    source = link(row.get("source_profile_url") or row.get("source_url"), "Page source")
    direct = link(row.get("source_url"), "Fichier") if row.get("source_profile_url") else ""
    crest_rows.append(
        "<tr>"
        f'<td>{e(row.get("position_grille"))}</td>'
        f'<td><strong>{e(row.get("club_demande"))}</strong><br><small>{e(row.get("club_source"))}</small></td>'
        f'<td>{e(row.get("asset_location"))}</td>'
        f'<td>{source} {direct}</td>'
        f'<td>{e(row.get("license_or_rights_note"))}<br><small>{e(row.get("verification_status"))}</small></td>'
        "</tr>"
    )

page = f'''<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Crédits des images — Hak Vision Football Simulator</title>
<style>
:root{{--bg:#081414;--panel:#102222;--line:#34504a;--text:#edf1e8;--muted:#aab8b0;--gold:#e9c75c}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.5 system-ui,-apple-system,Segoe UI,sans-serif}}
main{{max-width:1280px;margin:0 auto;padding:26px 18px 60px}}h1,h2{{line-height:1.2}}h1{{color:var(--gold)}}h2{{margin-top:36px}}p,li{{color:var(--muted)}}a{{color:#b6dcff}}.notice{{background:#302a13;border:1px solid #86743a;border-radius:10px;padding:14px 16px;color:#f1e3aa}}
.table-wrap{{overflow:auto;border:1px solid var(--line);border-radius:10px;background:var(--panel)}}table{{border-collapse:collapse;width:100%;min-width:800px}}th,td{{padding:9px 10px;text-align:left;vertical-align:middle;border-bottom:1px solid #ffffff12}}th{{position:sticky;top:0;background:#19302e;color:var(--gold);font-size:12px}}td small{{color:var(--muted)}}tr:last-child td{{border-bottom:0}}.portrait{{width:42px;height:50px;object-fit:cover;border-radius:6px;display:block}}.legend-portrait{{width:52px;height:66px}}
.back{{display:inline-block;margin-bottom:16px}}footer{{margin-top:28px;color:var(--muted);font-size:13px}}
</style></head><body><main>
<a class="back" href="./index.html">← Retour au jeu</a>
<h1>Crédits des images et des écussons</h1>
<p>{len(players)} portraits de joueurs du jeu, {len(legends)} portraits de légendes et {len(crests)} écussons de clubs sont consignés dans les manifestes.</p>
<div class="notice"><strong>À retenir :</strong> une licence de droit d’auteur ne garantit pas à elle seule le droit d’utiliser commercialement le nom ou l’image personnelle d’un joueur, ni un écusson de club. Vérifier les règles locales, les droits à l’image et les marques avant toute publication commerciale ou diffusion sur une boutique.</div>
<h2>Portraits des joueurs</h2>
<p>Les auteurs, URL de source et licences indiqués dans le tableau proviennent du manifeste des portraits. Les images peuvent aussi rester soumises au droit à l’image des personnes représentées.</p>
<div class="table-wrap"><table><thead><tr><th>#</th><th>Photo</th><th>Joueur / club dans le jeu</th><th>Crédit</th><th>Licence</th><th>Source</th></tr></thead><tbody>{''.join(player_rows)}</tbody></table></div>
<h2>Légendes</h2>
<p>Les fiches des légendes affichent leurs postes et notes de jeu; les sources, auteurs et licences des portraits sont détaillés ci-dessous.</p>
<div class="table-wrap"><table><thead><tr><th>Photo</th><th>Légende</th><th>Crédit</th><th>Licence</th><th>Source / biographie</th></tr></thead><tbody>{''.join(legend_rows)}</tbody></table></div>
<h2>Écussons des clubs</h2>
<p>Les écussons historiques embarqués sont conservés; Estudiantes, Botafogo et Al Ahli sont ajoutés comme fichiers séparés. Les notes indiquent les limites de vérification et les avertissements de marque.</p>
<div class="table-wrap"><table><thead><tr><th>#</th><th>Club</th><th>Emplacement</th><th>Source</th><th>Licence / réserve de droits</th></tr></thead><tbody>{''.join(crest_rows)}</tbody></table></div>
<footer>Manifestes : <code>assets/player-photo-credits.csv</code>, <code>assets/legend-photo-credits.csv</code> et <code>assets/club-crest-credits.csv</code>. Voir aussi <code>assets/licenses/verified-sources.md</code>.</footer>
</main></body></html>'''
OUT.write_text(page, encoding="utf-8")
print(f"Generated {OUT}: {len(players)} player portraits, {len(legends)} legends, {len(crests)} crests")
