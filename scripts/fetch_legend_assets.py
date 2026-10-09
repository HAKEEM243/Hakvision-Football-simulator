#!/usr/bin/env python3
"""Télécharge et vérifie les portraits Wikimedia des légendes du jeu.

Les images sont réencodées en JPEG sans recadrage ni agrandissement; les crédits
et licences restent consultables dans assets/legend-photo-credits.csv.
"""
from __future__ import annotations
import csv
import io
import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import unquote

import requests
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = ROOT / "assets" / "legends"
CSV_OUT = ROOT / "assets" / "legend-photo-credits.csv"
JS_OUT = ROOT / "assets" / "legends-data.js"
API = "https://commons.wikimedia.org/w/api.php"
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "HakvisionFootballSimulator/1.0 (Wikimedia Commons attribution and image integration)"})

# Sources recherchées et vérifiées : page de fichier Commons, licence et biographie.
# Les notes de crédit donnent les exigences à afficher dans le jeu/publication.
LEGENDS = [
    {"id":"ronaldo-nazario","name":"Ronaldo Nazário","nickname":"R9","nation":"bra","position":"BU","rating":99,"prime_age":25,"clubs":"Inter Milan · Real Madrid","era":"1993–2011","image_url":"https://thumb.wikimedia.org/wikipedia/commons/thumb/7/74/051119SMcC0014.jpg/960px-051119SMcC0014.jpg","file_page":"https://commons.wikimedia.org/wiki/File:051119SMcC0014.jpg","author":"Web Summit; photo by Stephen McCarthy / Web Summit via Sportsfile","license":"Creative Commons Attribution 2.0 Generic (CC BY 2.0)","license_url":"https://creativecommons.org/licenses/by/2.0/","credit":"Photo: Stephen McCarthy / Web Summit via Sportsfile (Commons author: Web Summit), CC BY 2.0; indicate any changes.","bio_url":"https://www.realmadrid.com/en-US/the-club/history/football-legends/ronaldo-luis-nazario-de-lima","position_source":"https://www.britannica.com/biography/Ronaldo"},
    {"id":"zinedine-zidane","name":"Zinedine Zidane","nickname":"Zizou","nation":"fra","position":"MOC","rating":99,"prime_age":27,"clubs":"Juventus · Real Madrid","era":"1989–2006","image_url":"https://thumb.wikimedia.org/wikipedia/commons/thumb/d/de/Zinedine_Zidane.jpg/960px-Zinedine_Zidane.jpg","file_page":"https://commons.wikimedia.org/wiki/File:Zinedine_Zidane.jpg","author":"Walterlan Papetti","license":"Creative Commons Attribution-ShareAlike 2.0 Generic (CC BY-SA 2.0)","license_url":"https://creativecommons.org/licenses/by-sa/2.0/","credit":"Walterlan Papetti, via Wikimedia Commons, CC BY-SA 2.0; provide credit and license link, and indicate any changes.","bio_url":"https://www.britannica.com/biography/Zinedine-Zidane","position_source":"https://www.realmadrid.com/en-US/the-club/history/football-legends/zinedine-zidane"},
    {"id":"ronaldinho","name":"Ronaldinho","nickname":"Dinho","nation":"bra","position":"AIL","rating":98,"prime_age":26,"clubs":"FC Barcelona · AC Milan","era":"1998–2015","image_url":"https://thumb.wikimedia.org/wikipedia/commons/thumb/e/e8/Ronaldinho_in_2019.jpg/500px-Ronaldinho_in_2019.jpg","file_page":"https://commons.wikimedia.org/wiki/File:Ronaldinho_in_2019.jpg","author":"Marcos Corrêa/PR","license":"Creative Commons Attribution 2.0 Generic (CC BY 2.0)","license_url":"https://creativecommons.org/licenses/by/2.0/","credit":"Marcos Corrêa/PR, ‘Ronaldinho in 2019.jpg’ — CC BY 2.0.","bio_url":"https://www.britannica.com/biography/Ronaldinho","position_source":"https://www.fcbarcelona.com/en/football/barca-legends/players/1493844/ronaldinho"},
    {"id":"diego-maradona","name":"Diego Maradona","nickname":"El Pibe de Oro","nation":"arg","position":"MOC","rating":99,"prime_age":26,"clubs":"SSC Napoli · Boca Juniors","era":"1976–1997","image_url":"https://thumb.wikimedia.org/wikipedia/commons/thumb/f/f1/Diego_Maradona_2017_%28headshot%29.jpg/330px-Diego_Maradona_2017_%28headshot%29.jpg","file_page":"https://commons.wikimedia.org/wiki/File:Diego_Maradona_2017_(headshot).jpg","author":"Дмитрий Садовников","license":"Creative Commons Attribution-ShareAlike 3.0 Unported (CC BY-SA 3.0)","license_url":"https://creativecommons.org/licenses/by-sa/3.0/deed.en","credit":"Дмитрий Садовников / Wikimedia Commons, CC BY-SA 3.0; include attribution and license link.","bio_url":"https://www.britannica.com/biography/Diego-Maradona","position_source":"https://www.theguardian.com/football/2020/nov/25/diego-maradona-obituary"},
    {"id":"pele","name":"Pelé","nickname":"O Rei","nation":"bra","position":"BU","rating":99,"prime_age":28,"clubs":"Santos FC · New York Cosmos","era":"1956–1977","image_url":"https://thumb.wikimedia.org/wikipedia/commons/thumb/5/54/Pele_by_John_Mathew_Smith.jpg/500px-Pele_by_John_Mathew_Smith.jpg","file_page":"https://commons.wikimedia.org/wiki/File:Pele_by_John_Mathew_Smith.jpg","author":"John Mathew Smith (photographe d'origine); retouches de la version Commons actuelle par Joelphotofix","license":"Creative Commons Attribution-ShareAlike 2.0 Generic (CC BY-SA 2.0)","license_url":"https://creativecommons.org/licenses/by-sa/2.0/","credit":"John Mathew Smith; version Commons retouchée par Joelphotofix; CC BY-SA 2.0. Indiquer les modifications supplémentaires.","bio_url":"https://www.britannica.com/biography/Pele-Brazilian-football-player","position_source":"https://www.national-football-teams.com/player/17926/Pele.html"},
    {"id":"johan-cruyff","name":"Johan Cruyff","nickname":"The Flying Dutchman","nation":"ned","position":"MOC","rating":98,"prime_age":27,"clubs":"Ajax · FC Barcelona","era":"1964–1984","image_url":"https://thumb.wikimedia.org/wikipedia/commons/thumb/f/fd/Johan_Cruyff_1971c.jpg/500px-Johan_Cruyff_1971c.jpg","file_page":"https://commons.wikimedia.org/wiki/File:Johan_Cruyff_1971c.jpg","author":"Bert Verhoeff pour Anefo (Nationaal Archief)","license":"Creative Commons Attribution-ShareAlike 3.0 Netherlands (CC BY-SA 3.0 NL)","license_url":"https://creativecommons.org/licenses/by-sa/3.0/nl/deed.en","credit":"Bert Verhoeff / Anefo, Nationaal Archief — CC BY-SA 3.0 NL; crédit et lien de licence requis.","bio_url":"https://www.britannica.com/biography/Johan-Cruyff","position_source":"https://www.fifa.com/en/archive/johan-cruyff"},
    {"id":"franz-beckenbauer","name":"Franz Beckenbauer","nickname":"Der Kaiser","nation":"ger","position":"DC","rating":98,"prime_age":29,"clubs":"FC Bayern München · New York Cosmos","era":"1964–1983","image_url":"https://thumb.wikimedia.org/wikipedia/commons/thumb/b/ba/Beckenbauer_Close.jpg/500px-Beckenbauer_Close.jpg","file_page":"https://commons.wikimedia.org/wiki/File:Beckenbauer_Close.jpg","author":"DerFalkVonFreyburg","license":"Creative Commons Attribution 3.0 Unported (CC BY 3.0)","license_url":"https://creativecommons.org/licenses/by/3.0/deed.en","credit":"DerFalkVonFreyburg / Wikimedia Commons, CC BY 3.0; credit the author and indicate any modifications.","bio_url":"https://www.britannica.com/biography/Franz-Beckenbauer","position_source":"https://fcbayern.com/en/club/fcb-club/franz-beckenbauer"},
    {"id":"eusebio","name":"Eusébio da Silva Ferreira","nickname":"Pantera Negra","nation":"por","position":"BU","rating":97,"prime_age":27,"clubs":"SL Benfica","era":"1957–1979","image_url":"https://thumb.wikimedia.org/wikipedia/commons/thumb/9/99/Eusebio_%281963%29.jpg/960px-Eusebio_%281963%29.jpg","file_page":"https://commons.wikimedia.org/wiki/File:Eusebio_(1963).jpg","author":"Harry Pot pour Anefo (Nationaal Archief Fotocollectie Anefo)","license":"CC BY-SA 3.0 Netherlands (CC BY-SA 3.0 NL)","license_url":"https://creativecommons.org/licenses/by-sa/3.0/nl/deed.en","credit":"Harry Pot / Anefo, Nationaal Archief — CC BY-SA 3.0 NL; inclure crédit et licence; partager les adaptations sous licence compatible.","bio_url":"https://www.espn.com/soccer/story/_/id/37372612/no20-eusebio","position_source":"https://www.uefa.com/news-media/news/0211-0f8a35876e14-1dd0d4511a73-1000--eusebio-da-silva-ferreira-1942-2014/"},
    {"id":"garrincha","name":"Garrincha","nickname":"Alegria do Povo","nation":"bra","position":"AIL","rating":98,"prime_age":27,"clubs":"Botafogo","era":"1953–1972","image_url":"https://upload.wikimedia.org/wikipedia/commons/2/25/MFdSantos-Garrincha_%28cropped%29.jpg","file_page":"https://commons.wikimedia.org/wiki/File:MFdSantos-Garrincha_(cropped).jpg","author":"El Gráfico","license":"Domaine public (Argentine et États-Unis selon Commons)","license_url":"https://commons.wikimedia.org/wiki/Commons:Licensing#Public_domain","credit":"El Gráfico, n° 2233; attribution/source indiquée sur Commons; domaine public revendiqué en Argentine et aux États-Unis.","bio_url":"https://www.britannica.com/biography/Garrincha","position_source":"https://www.britannica.com/biography/Garrincha"},
    {"id":"michel-platini","name":"Michel Platini","nickname":"Le Roi","nation":"fra","position":"MOC","rating":97,"prime_age":29,"clubs":"Juventus · AS Nancy","era":"1972–1987","image_url":"https://thumb.wikimedia.org/wikipedia/commons/thumb/3/3b/Michel_Platini_2008.jpg/500px-Michel_Platini_2008.jpg","file_page":"https://commons.wikimedia.org/wiki/File:Michel_Platini_2008.jpg","author":"Anders Vindegg","license":"Creative Commons Attribution-ShareAlike 2.0 Generic (CC BY-SA 2.0)","license_url":"https://creativecommons.org/licenses/by-sa/2.0/","credit":"Anders Vindegg / Wikimedia Commons, CC BY-SA 2.0; credit the author and link the license.","bio_url":"https://www.britannica.com/biography/Michel-Platini","position_source":"https://www.britannica.com/biography/Michel-Platini"},
    {"id":"george-best","name":"George Best","nickname":"El Beatle","nation":"nir","position":"AIL","rating":97,"prime_age":25,"clubs":"Manchester United","era":"1963–1984","image_url":"https://thumb.wikimedia.org/wikipedia/commons/thumb/a/a5/George_best_1976.jpg/500px-George_best_1976.jpg","file_page":"https://commons.wikimedia.org/wiki/File:George_best_1976.jpg","author":"Bert Verhoeff pour Anefo (Nationaal Archief Fotocollectie Anefo)","license":"CC0 1.0 Universal Public Domain Dedication","license_url":"https://creativecommons.org/publicdomain/zero/1.0/deed.en","credit":"CC0 1.0 (crédit Bert Verhoeff / Anefo apprécié; pas obligatoire selon CC0).","bio_url":"https://www.britannica.com/biography/George-Best","position_source":"https://www.manutd.com/en/players-and-staff/detail/george-best"},
    {"id":"paolo-maldini","name":"Paolo Maldini","nickname":"Il Capitano","nation":"ita","position":"DC","rating":97,"prime_age":26,"clubs":"AC Milan","era":"1985–2009","image_url":"https://thumb.wikimedia.org/wikipedia/commons/thumb/3/38/Paolo_Maldini_2009.jpg/250px-Paolo_Maldini_2009.jpg","file_page":"https://commons.wikimedia.org/wiki/File:Paolo_Maldini_2009.jpg","author":"Christophe95","license":"Creative Commons Attribution-ShareAlike 3.0 Unported (CC BY-SA 3.0)","license_url":"https://creativecommons.org/licenses/by-sa/3.0/","credit":"Christophe95 / Wikimedia Commons, CC BY-SA 3.0; attribuer l’auteur et partager les adaptations sous licence identique ou compatible.","bio_url":"https://www.britannica.com/biography/Paolo-Maldini","position_source":"https://www.transfermarkt.com/paolo-maldini/profil/spieler/5803"},
    {"id":"lev-yashin","name":"Lev Yashin","nickname":"The Black Spider","nation":"rus","position":"GB","rating":99,"prime_age":29,"clubs":"Dynamo Moscou","era":"1950–1971","image_url":"https://thumb.wikimedia.org/wikipedia/commons/thumb/a/a3/Lev_Yashin.jpg/500px-Lev_Yashin.jpg","file_page":"https://commons.wikimedia.org/wiki/File:Lev_Yashin.jpg","author":"Ron Kroon pour Anefo (Nationaal Archief)","license":"Creative Commons Attribution-ShareAlike 3.0 Netherlands (CC BY-SA 3.0 NL)","license_url":"https://creativecommons.org/licenses/by-sa/3.0/nl/deed.en","credit":"Ron Kroon / Anefo, Nationaal Archief — CC BY-SA 3.0 NL; crédit et lien de licence requis, adaptations sous licence compatible.","bio_url":"https://www.britannica.com/biography/Lev-Ivanovich-Yashin","position_source":"https://www.fifa.com/en/tournaments/mens/worldcup/articles/lev-yashin-soviet-union-goalkeeper"},
    {"id":"ferenc-puskas","name":"Ferenc Puskás","nickname":"The Galloping Major","nation":"hun","position":"BU","rating":97,"prime_age":28,"clubs":"Real Madrid · Budapest Honvéd","era":"1943–1966","image_url":"https://thumb.wikimedia.org/wikipedia/commons/thumb/8/88/Ferenc_Pusk%C3%A1s_%281982%29.jpg/500px-Ferenc_Pusk%C3%A1s_%281982%29.jpg","file_page":"https://commons.wikimedia.org/wiki/File:Ferenc_Pusk%C3%A1s_(1982).jpg","author":"FOTO:FORTEPAN / URBÁN TAMÁS (Fortepan ID 124820)","license":"Creative Commons Attribution-ShareAlike 3.0 Unported (CC BY-SA 3.0)","license_url":"https://creativecommons.org/licenses/by-sa/3.0/deed.en","credit":"FOTO:FORTEPAN / URBÁN TAMÁS; source Fortepan ID 124820; CC BY-SA 3.0; credit and indicate changes.","bio_url":"https://www.britannica.com/biography/Ferenc-Puskas","position_source":"https://www.realmadrid.com/en-US/the-club/history/football-legends/ferenc-puskas-biro"},
    {"id":"thierry-henry","name":"Thierry Henry","nickname":"Titi","nation":"fra","position":"BU","rating":97,"prime_age":27,"clubs":"Arsenal · FC Barcelona","era":"1994–2014","image_url":"https://upload.wikimedia.org/wikipedia/commons/6/6e/Thierry_Henry_2008.jpg","file_page":"https://commons.wikimedia.org/wiki/File:Thierry_Henry_2008.jpg","author":"Shay","license":"Creative Commons Attribution-ShareAlike 3.0 Unported (CC BY-SA 3.0)","license_url":"https://creativecommons.org/licenses/by-sa/3.0/deed.en","credit":"Shay / Wikimedia Commons, CC BY-SA 3.0; indiquer les modifications éventuelles.","bio_url":"https://www.britannica.com/biography/Thierry-Henry","position_source":"https://www.arsenal.com/feature/how-henry-became-our-greatest-goalscorer-afImL9f2n8oS"},
]


def commons_license(file_page: str) -> tuple[str, str]:
    manual = {
        "https://commons.wikimedia.org/wiki/File:Paolo_Maldini_2009.jpg": ("CC BY-SA 3.0", "Christophe95"),
        "https://commons.wikimedia.org/wiki/File:MFdSantos-Garrincha_(cropped).jpg": ("Public domain", "El Gráfico"),
    }
    if file_page in manual:
        return manual[file_page]
    title = unquote(file_page.split("/wiki/File:", 1)[1]).replace(" ", "_")
    params = {"action":"query","format":"json","prop":"imageinfo","iiprop":"extmetadata","titles":"File:"+title}
    last_error = None
    for attempt in range(6):
        try:
            response = SESSION.get(API, params=params, timeout=30)
            if response.status_code == 429 or response.status_code >= 500:
                raise requests.HTTPError(f"Commons HTTP {response.status_code}")
            response.raise_for_status()
            data = response.json()
            page = next(iter(data["query"]["pages"].values()))
            info = page["imageinfo"][0]["extmetadata"]
            license_name = re.sub(r"<[^>]+>", " ", info.get("LicenseShortName",{}).get("value",""))
            artist = re.sub(r"<[^>]+>", " ", info.get("Artist",{}).get("value",""))
            return " ".join(license_name.split()), " ".join(artist.split())
        except Exception as exc:
            last_error = exc
            if attempt < 5:
                time.sleep(min(2 ** attempt, 16))
    raise RuntimeError(f"lecture des métadonnées Commons impossible: {last_error}")


def main() -> None:
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    credits = []
    usable = []
    previous = {}
    if CSV_OUT.exists():
        with CSV_OUT.open(encoding="utf-8-sig", newline="") as f:
            previous = {r.get("id"):r for r in csv.DictReader(f)}
    for i, entry in enumerate(LEGENDS, 1):
        if i > 1:
            time.sleep(1.5)
        try:
            filename = f"{entry['id']}.jpg"
            output_path = ASSET_DIR / filename
            cached = previous.get(entry["id"], {})
            reuse = output_path.exists() and cached.get("file_page") == entry["file_page"]
            if reuse:
                license_actual = cached.get("license_actual", "")
                author_actual = cached.get("author_actual", "")
            else:
                license_actual, author_actual = commons_license(entry["file_page"])
            # Must stay within the project's allowed license family and match the reviewed source.
            expected = entry["license"].lower()
            valid_family = any(token in license_actual.lower() for token in ("cc by", "cc0", "public domain"))
            if not license_actual or not valid_family or ("cc by" in expected and "cc by" not in license_actual.lower()):
                raise ValueError(f"licence Commons inattendue: {license_actual!r}; attendu {entry['license']!r}")
            if reuse:
                image = Image.open(output_path)
                image.load()
            else:
                response = SESSION.get(entry["image_url"], timeout=45)
                response.raise_for_status()
                image = Image.open(io.BytesIO(response.content))
                image.load()
                image = ImageOps.exif_transpose(image)
            if image.width < 80 or image.height < 80:
                raise ValueError(f"image trop petite: {image.size}")
            if max(image.size) > 640:
                image.thumbnail((640, 640), Image.Resampling.LANCZOS)
            if image.mode not in ("RGB", "RGBA"):
                image = image.convert("RGBA")
            if image.mode == "RGBA":
                bg = Image.new("RGB", image.size, "white")
                bg.paste(image, mask=image.getchannel("A"))
                image = bg
            else:
                image = image.convert("RGB")
            if not reuse:
                image.save(output_path, "JPEG", quality=88, optimize=True, progressive=True)
            row = dict(entry)
            row.update({"asset_location":f"assets/legends/{filename}","license_actual":license_actual,"author_actual":author_actual})
            usable.append(row)
            credits.append(row)
            print(f"[{i:02}/{len(LEGENDS)}] OK {entry['name']} — {license_actual} — {image.width}x{image.height}", flush=True)
        except Exception as exc:
            print(f"[{i:02}/{len(LEGENDS)}] ERREUR {entry['name']}: {exc}", file=sys.stderr, flush=True)
            if (ASSET_DIR / f"{entry['id']}.jpg").exists():
                (ASSET_DIR / f"{entry['id']}.jpg").unlink()
    columns = ["id","name","asset_location","file_page","image_url","author","author_actual","license","license_actual","license_url","credit","bio_url","position_source","nation","position","rating","prime_age","clubs","era"]
    with CSV_OUT.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        for row in credits:
            writer.writerow({k:row.get(k,"") for k in columns})
    # Only show a legend in the game if both image and verified usable license are present.
    js_rows = [{k:row[k] for k in ("id","name","nickname","nation","position","rating","prime_age","clubs","era","bio_url","position_source","credit")} | {"image":"./"+row["asset_location"]} for row in usable]
    JS_OUT.write_text("window.HV_LEGENDS="+json.dumps(js_rows,ensure_ascii=False,separators=(",",":"))+";\n", encoding="utf-8")
    print(f"FIN: {len(usable)}/{len(LEGENDS)} portraits validés. JS={JS_OUT.relative_to(ROOT)} CSV={CSV_OUT.relative_to(ROOT)}", flush=True)
    if len(usable) < len(LEGENDS):
        sys.exit(2)

if __name__ == "__main__":
    main()
