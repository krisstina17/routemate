# Naloga 2: Parser dogodkov

Program samodejno zbere prihajajoče dogodke s spletne strani [dogodki-slovenija.si](https://dogodki-slovenija.si) in jih shrani v datoteko `dogodki.json`.

## Zahteve

- Python 3.9 ali novejši
- knjižnici `requests` in `beautifulsoup4`

```
pip install requests beautifulsoup4
```

## Zagon

```
python scraper.py
```

Datoteka `dogodki.json` se ustvari v mapi, iz katere zaženemo program. Zagon traja nekaj minut, ker program med zahtevami namenoma čaka 1,5 sekunde.

## Delovanje

1. **Zbiranje povezav:** program sestavi naslove vseh kombinacij kraja/pokrajine in kategorije (npr. `/dogodki/maribor/koncerti/`), prenese te strani in z njih zbere povezave do posameznih dogodkov. Podvojene povezave se odstranijo.
2. **Branje dogodkov:** za vsako povezavo prenese stran dogodka in podatke prebere iz bloka JSON-LD (`<script type="application/ld+json">`). Kategorijo prebere iz HTML oznake `span.badge`.
3. **Shranjevanje:** obdrži samo dogodke, ki še niso minili, jih razvrsti po datumu, uri in nazivu ter shrani v `dogodki.json`.

## Oblika izhoda

Primer zapisa iz `dogodki.json`:

```json
[
  {
    "naziv": "Planica 2027: smučarski poleti, posamična tekma (M)",
    "datum": "2027-03-19",
    "ura": "14:00",
    "kraj": "Planica (Kranjska Gora)",
    "lokacija": "Nordijski center Planica",
    "pokrajina": "Gorenjska",
    "kategorija": "Šport",
    "url": "https://dogodki-slovenija.si/dogodek/planica-2027-smucarski-poleti-posamicna-tekma-m/"
  }
]
```

Če podatek ni na voljo, ima polje vrednost `null` (npr. `"ura": null`, kadar ura dogodka ni objavljena).

## Osveževanje podatkov

`dogodki.json` je posnetek stanja na dan zagona. Program shrani samo dogodke, ki še niso minili, poleg tega pa spletna stran pretekle dogodke sčasoma odstrani in njihove strani niso več dostopne. Že naslednji dan je zato del podatkov zastarel.

V praksi bi program zato zaganjali samodejno, na primer enkrat dnevno:

- **Linux / macOS (cron)**, vsak dan ob 6:00:
  ```
  0 6 * * * cd /pot/do/naloga2-parser && python3 scraper.py
  ```
- **Windows**: z *Razporejevalnikom opravil* (Task Scheduler) nastavimo dnevni zagon ukaza `python scraper.py` v mapi projekta.

Ob vsakem zagonu se `dogodki.json` prepiše z novim, posodobljenim seznamom.

## Odgovorno zbiranje podatkov

med zahtevami je premor 1,5 s, da strežnika ne preobremenimo
