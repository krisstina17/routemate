# RouteMate – Naloga 1: XML in JSON

## 1. Opis projekta

RouteMate je projekt pametnega načrtovalnika potovanj z avtomobilom. V okviru prve naloge je izdelana konzolna aplikacija v programskem jeziku Python, ki omogoča branje in obdelavo podatkov iz XML dokumentov, povezovanje podatkov prek identifikatorjev ID, filtriranje potovanj ter izvoz rezultatov v formata JSON in XML.

## 2. Struktura projekta

```text
naloga1-xml-json/
│
├── data/
│   ├── uporabniki.xml
│   ├── vozila.xml
│   └── potovanja.xml
│
├── main.py
├── filtrirano.json
├── filtrirano.xml
└── README.md
```

Aplikacija uporablja tri medsebojno povezane XML datoteke:

- **uporabniki.xml** – vsebuje 15 uporabnikov z enoličnimi identifikatorji, imeni in priimki.
- **vozila.xml** – vsebuje 15 vozil s podatki o znamki, modelu, vrsti goriva in porabi goriva.
- **potovanja.xml** – vsebuje 15 potovanj s podatki o začetni lokaciji, cilju, datumu, razdalji, trajanju in opombi.

Vsaka glavna entiteta ima enoličen atribut `id`.

Povezave med dokumenti so vzpostavljene prek naslednjih identifikatorjev:

- `uporabnikId` v datoteki `vozila.xml` povezuje vozilo z njegovim lastnikom.
- `uporabnikId` in `voziloId` v datoteki `potovanja.xml` povezujeta potovanje z ustreznim uporabnikom in vozilom.

XML dokumenti vsebujejo besedilna in številčna polja ter datume v obliki `YYYY-MM-DD`. Nekatera potovanja imajo prazno polje `opomba`, kar predstavlja primer manjkajočega podatka.

## 3. Delovanje aplikacije

Program `main.py` uporablja knjižnico `xml.etree.ElementTree` za branje XML dokumentov in pretvorbo podatkov v Pythonove sezname slovarjev (deserializacija).

Po nalaganju podatkov aplikacija poveže vozila z njihovimi lastniki ter potovanja z ustreznimi uporabniki in vozili na podlagi identifikatorjev ID. Povezane podatke izpiše v konzolo.

Uporabnik lahko nato izbere eno od treh možnosti filtriranja:

1. **Filtriranje po cilju** – izpiše potovanja v izbrano mesto.
2. **Filtriranje po največji razdalji** – izpiše potovanja, katerih razdalja je manjša ali enaka vneseni vrednosti.
3. **Filtriranje po datumu** – izpiše potovanja na izbrani datum.

Možnost `0` omogoča izhod iz programa.

Filtrirani rezultati se izpišejo v konzolo in shranijo v dve datoteki:

- **filtrirano.json** – izvoz filtriranih potovanj v obliki seznama objektov JSON.
- **filtrirano.xml** – izvoz istih filtriranih potovanj v obliki XML dokumenta.

Datoteki se ob vsakem novem filtriranju prepišeta.

## 4. Zagon aplikacije

Za zagon aplikacije je potreben Python 3.9 ali novejši. Dodatnih knjižnic ni treba nameščati, saj program uporablja standardno Pythonovo knjižnico.

### 4.1 Prenos projekta

Projekt lahko prenesemo z GitHub repozitorija:

```bash
git clone https://github.com/krisstina17/routemate.git
```

### 4.2 Premik v mapo naloge

```bash
cd routemate/naloga1-xml-json
```

### 4.3 Zagon aplikacije

```bash
python main.py
```

Po zagonu program prebere vse tri XML datoteke, izpiše podatke o uporabnikih, vozilih in potovanjih ter prikaže meni za filtriranje.

## 5. Primeri uporabe

Po zagonu aplikacije se v konzoli prikaže naslednji meni:

```text
========== ROUTEMATE ==========
1 - Filtriranje po cilju
2 - Filtriranje po najvecji razdalji
3 - Filtriranje po datumu
0 - Izhod
```

### 5.1 Filtriranje po cilju

Uporabnik izbere možnost `1` in vnese cilj `Ljubljana`.

```text
Izberite moznost: 1
Vnesite cilj potovanja: Ljubljana

FILTRIRANA POTOVANJA:
P001 - Maribor -> Ljubljana | 130.5 km | 2026-10-20
P006 - Celje -> Ljubljana | 75.0 km | 2026-10-28
P010 - Maribor -> Ljubljana | 130.5 km | 2026-11-22
P014 - Maribor -> Ljubljana | 130.5 km | 2026-12-15
Stevilo najdenih potovanj: 4
Podatki so izvozeni v filtrirano.json
Podatki so izvozeni v filtrirano.xml
```

Aplikacija najde štiri potovanja s ciljem Ljubljana.

### 5.2 Filtriranje po največji razdalji

Uporabnik izbere možnost `2` in vnese največjo razdaljo `100` km.

```text
Izberite moznost: 2
Vnesite najvecjo razdaljo (km): 100

FILTRIRANA POTOVANJA:
P002 - Maribor -> Graz | 70.0 km | 2026-10-22
P006 - Celje -> Ljubljana | 75.0 km | 2026-10-28
P008 - Ptuj -> Maribor | 30.0 km | 2026-10-30
P012 - Maribor -> Ptuj | 30.0 km | 2026-12-05
P013 - Ljubljana -> Bled | 55.0 km | 2026-12-10
P015 - Celje -> Maribor | 55.0 km | 2026-12-20
Stevilo najdenih potovanj: 6
Podatki so izvozeni v filtrirano.json
Podatki so izvozeni v filtrirano.xml
```

Aplikacija najde šest potovanj, katerih razdalja ne presega 100 km.

### 5.3 Filtriranje po datumu

Uporabnik izbere možnost `3` in vnese datum `2026-11-05`.

```text
Izberite moznost: 3
Vnesite datum (YYYY-MM-DD): 2026-11-05

FILTRIRANA POTOVANJA:
P003 - Celje -> Koper | 190.0 km | 2026-11-05
Stevilo najdenih potovanj: 1
Podatki so izvozeni v filtrirano.json
Podatki so izvozeni v filtrirano.xml
```

Aplikacija najde eno potovanje, ki je načrtovano na izbrani datum.

## 6. Izvoz rezultatov

Po izbiri filtra aplikacija samodejno ustvari oziroma posodobi datoteki:

- `filtrirano.json`
- `filtrirano.xml`

Obe datoteki vsebujeta iste filtrirane zapise, vendar v različnih formatih.

Datoteki, priloženi projektu, vsebujeta primer rezultatov filtriranja po cilju `Ljubljana`, torej štiri potovanja.

Ob ponovnem zagonu programa in izbiri drugega filtra se vsebina obeh datotek prepiše z novimi rezultati.

## 7. Uporabljene tehnologije

- **Python 3** – programski jezik za implementacijo konzolne aplikacije.
- **XML** – format za shranjevanje vhodnih podatkov.
- **JSON** – format za izvoz filtriranih rezultatov.
- **xml.etree.ElementTree** – branje, razčlenjevanje in ustvarjanje XML dokumentov.
- **json** – pretvorba in zapis podatkov v format JSON.
- **pathlib** – delo s potmi do datotek.

## 8. Datoteke za oddajo

Projektna mapa `naloga1-xml-json` vsebuje:

- Tri vhodne XML datoteke v mapi `data/`.
- Izvorno kodo aplikacije `main.py`.
- Primer filtriranih rezultatov v `filtrirano.json`.
- Primer filtriranih rezultatov v `filtrirano.xml`.
- Dokumentacijo in navodila za zagon v `README.md`.

Vse datoteke so del projekta RouteMate, ki je dostopen v GitHub repozitoriju:

https://github.com/krisstina17/routemate