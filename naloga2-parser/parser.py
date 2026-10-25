import json
import re
import time
from datetime import date
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

# NASTAVITVE
OSNOVA = "https://dogodki-slovenija.si"   # osnovni naslov spletne strani
IZHOD = "dogodki.json"                    # datoteka, v katero shranimo rezultate
PAVZA = 1.5                               # sekunde cakanja med zahtevami

# deli naslovov, iz katerih sestavimo strani s seznami dogodkov
KATEGORIJE = ["koncerti", "veselice", "sport", "kultura", "dobrodelni", "zmenki"]
POKRAJINE = ["gorenjska", "koroska", "stajerska", "prekmurje", "dolenjska", "primorska", "notranjska"]
KRAJI = [
    "ljubljana", "maribor", "novo-mesto", "celje", "ptuj", "velenje",
    "sentjur", "kranj", "skofja-loka", "koper", "kamnik",
    "nova-gorica", "slovenske-konjice", "izola",
]

# prenese HTML z naslova; vrne besedilo ali None, ce ne uspe
def prenesi(seja, url):
    try:
        odgovor = seja.get(url, timeout=20)   # poslje zahtevo; po 20 s odneha
    except requests.RequestException as napaka:
        # napaka povezave (ni interneta, timeout ...)
        print(f"Napaka pri {url}: {napaka}")
        return None
    finally:
        time.sleep(PAVZA)   # vedno pocakamo, da ne preobremenimo streznika

    if odgovor.status_code in (403, 429):
        # 403 = prepovedano, 429 = prevec zahtev -> ustavimo celoten program
        raise RuntimeError(f"Strežnik je omejil dostop ({odgovor.status_code}). Ustavitev.")
    if odgovor.status_code != 200:
        # npr. 404 ali 500 -> preskocimo samo to stran in nadaljujemo
        print(f"Preskočeno ({odgovor.status_code}): {url}")
        return None
    return odgovor.text

# sestavi vse naslove oblike /dogodki/<kraj>/<kategorija>/ (vsak kraj x vsaka kategorija)
def strani_s_seznami():
    adrese = []
    for mesto in POKRAJINE + KRAJI:
        for kategorija in KATEGORIJE:
            adrese.append(f"{OSNOVA}/dogodki/{mesto}/{kategorija}/")
    return adrese

# preveri, ali je stran res prikazala zahtevano vsebino in nas ni tiho preusmerila drugam (npr. na domaco stran)
def je_prava_stran(soup, url):
    kanonicna = soup.find("link", rel="canonical")   # uradni naslov te strani
    if kanonicna is None or not kanonicna.get("href"):
        return True   # ni s cim primerjati -> stran sprejmemo
    dejanska = urlparse(kanonicna["href"]).path.rstrip("/")   # pot, ki jo navaja stran
    zahtevana = urlparse(url).path.rstrip("/")                # pot, ki smo jo zahtevali
    return dejanska == zahtevana

# zbere vse povezave do posameznih dogodkov (/dogodek/<ime>/)
def najdi_povezave_dogodkov(soup):
    povezave = set()   # mnozica -> brez podvojenih povezav
    for a in soup.find_all("a", href=True):   # samo povezave, ki imajo href
        polni = urljoin(OSNOVA, a["href"])          # relativna -> polna povezava
        polni = polni.split("#")[0].split("?")[0]   # odstranimo #... in ?..., da je isti dogodek vedno enak niz
        # obdrzimo samo povezave oblike https://dogodki-slovenija.si/dogodek/<ime>/
        if re.fullmatch(r"https://dogodki-slovenija\.si/dogodek/[^/]+/?", polni):
            povezave.add(polni)
    return povezave

# poisce podatke o dogodku v bloku JSON-LD na strani
def preberi_dogodek(html):
    soup = BeautifulSoup(html, "html.parser")

    for script in soup.find_all("script", type="application/ld+json"):
        try:
            podatki = json.loads(script.string or "")   # besedilo JSON -> slovar ali seznam
        except json.JSONDecodeError:
            continue   # blok ni veljaven JSON

        # JSON-LD je lahko en objekt ali seznam objektov
        if isinstance(podatki, dict):
            podatki = [podatki]
        if not isinstance(podatki, list):
            continue

        # med zapisi poiscemo tistega, ki je dogodek
        for zapis in podatki:
            if isinstance(zapis, dict) and zapis.get("@type") == "Event":
                return v_slovar(zapis, soup)

    return None   # dogodka nismo nasli

# iz zapisa JSON-LD naredi preprost slovar s polji, ki jih potrebujemo
def v_slovar(zapis, soup):
    # naslov je gnezden v lokaciji: zapis -> location -> address
    lokacija = zapis.get("location")
    if not isinstance(lokacija, dict):
        lokacija = {}   # prazen slovar, da .get() spodaj ne povzroci napake
    naslov = lokacija.get("address")
    if not isinstance(naslov, dict):
        naslov = {}

    zacetek = zapis.get("startDate")       # 2026-11-14T20:00:00+01:00
    if not isinstance(zacetek, str):
        zacetek = ""
    ura = re.search(r"T(\d{2}:\d{2})", zacetek)   # ura je za crko T

    oznaka = soup.select_one("span.badge")  # kategorija je samo v HTML

    return {
        "naziv": zapis.get("name"),
        "datum": zacetek[:10] or None,       # 2026-11-14
        "ura": ura.group(1) if ura else None,  # 20:00
        "kraj": naslov.get("addressLocality"),
        "lokacija": lokacija.get("name"),
        "pokrajina": naslov.get("addressRegion"),
        "kategorija": oznaka.get_text(strip=True) if oznaka else None,
        "url": zapis.get("url"),
    }

def main():
    # seja se uporablja za vse zahteve; User-Agent pove strezniku, kdo smo
    seja = requests.Session()
    seja.headers["User-Agent"] = "RouteMateStudentParser/1.0 (academic project)"

    # KORAK 1: pregledamo sezname in zberemo povezave do dogodkov
    vse_povezave = set()
    for url in strani_s_seznami():
        html = prenesi(seja, url)
        if html is None:
            continue
        soup = BeautifulSoup(html, "html.parser")
        if not je_prava_stran(soup, url):
            print(f"Nepodprta kombinacija: {url}")
            continue
        # razlika mnozic: odstranimo povezave, ki jih ze imamo
        nove = najdi_povezave_dogodkov(soup) - vse_povezave
        # nove povezave dodamo v skupno mnozico (unija)
        vse_povezave |= nove
        print(f"{url}  +{len(nove)} (skupaj {len(vse_povezave)})")

    print(f"Najdenih unikatnih povezav: {len(vse_povezave)}")

    # KORAK 2: odpremo vsak dogodek in preberemo podatke
    danes = date.today().isoformat()   # 2026-10-23
    dogodki = []
    # povezave uredimo, enumerate doda zaporedno stevilko (od 1 naprej)
    for i, url in enumerate(sorted(vse_povezave), start=1):
        html = prenesi(seja, url)
        if html is None:
            continue
        dogodek = preberi_dogodek(html)
        # obdrzimo samo dogodke, ki imajo datum in se niso minili
        if dogodek and dogodek["datum"] and dogodek["datum"] >= danes:
            dogodki.append(dogodek)
        print(f"[{i}/{len(vse_povezave)}] {url}")

    # KORAK 3: razvrstimo (datum, ura, naziv) in shranimo v dogodki.json
    # dogodki brez ure pridejo na konec dneva
    dogodki.sort(key=lambda d: (d["datum"], d["ura"] or "99:99", d["naziv"] or ""))
    with open(IZHOD, "w", encoding="utf-8") as f:
        # ensure_ascii=False ohrani sumnike, indent=2 za lepsi izpis
        json.dump(dogodki, f, ensure_ascii=False, indent=2)
    print(f"Shranjenih {len(dogodki)} dogodkov v {IZHOD}")


if __name__ == "__main__":
    main()
