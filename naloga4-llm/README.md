# Naloga 4 – Uporaba LLM

RouteMate uporabniku, ki še ne ve, kam bi šel, s pomočjo velikega jezikovnega modela (Google Gemini) predlaga 3 destinacije za izlet z avtom po Sloveniji. To je prvi korak pred glavno funkcionalnostjo aplikacije: ko uporabnik izbere destinacijo, jo RouteMate kasneje uporabi kot cilj poti (izračun poti, črpalke, strošek goriva).

## Delovanje

1. Uporabnik v obrazec vnese začetno lokacijo, največjo razdaljo v km, datum izleta, družbo, proračun in interese.
2. Strežnik iz teh podatkov **dinamično sestavi prompt**. Iz datuma samodejno določi tudi letni čas, da model ne predlaga npr. kopanja novembra.
3. Prompt pošlje modelu Gemini in zahteva odgovor v obliki **JSON po vnaprej določeni shemi** (`response_mime_type: application/json`, `response_json_schema`).
4. Prejeti JSON se **deserializira v razred** `PredlogIzleta` (Pydantic). Če JSON ni veljaven, aplikacija vrne napako.
5. Aplikacija dodatno odstrani predloge, ki precej presegajo želeno razdaljo, in prikaže destinacije kot kartice.

## Primer dinamičnega prompta

Za vnos *Maribor, 100 km, 21. 11. 2026, par, srednji proračun, narava + kulinarika*:

```text
Si turistični svetovalec za Slovenijo. Uporabnik začne pot v kraju Maribor in želi z avtom voziti
največ 100 km v eno smer. Potuje 21. 11. 2026 (letni čas: jesen), družba: par, proračun: srednji.
Zanimajo ga: narava, kulinarika. Predlagaj natanko 3 različne resnične kraje v Sloveniji, ki niso
Maribor in so od začetka oddaljeni največ 100 km. Aktivnosti naj bodo primerne za ta letni čas.
Odgovori v slovenščini, samo v JSON obliki po podani shemi.
```

Poslani prompt je viden tudi v aplikaciji (razdelek »Prompt, poslan modelu«).

## Oblika JSON odgovora

```json
{
  "povzetek": "Trije jesenski izleti z naravo in dobro hrano.",
  "destinacije": [
    {
      "kraj": "Ptuj",
      "regija": "Podravska",
      "priblizna_razdalja_km": 30,
      "zakaj_primerno": "Najstarejše mesto v Sloveniji z vinsko kletjo in gradom.",
      "aktivnosti": ["Ptujski grad", "Ptujska klet", "Sprehod ob Dravi"],
      "primerno_za_sezono": true
    }
  ]
}
```

## Razredi za deserializacijo (`modeli.py`)

| Razred | Polja |
|---|---|
| `PredlogIzleta` | `povzetek: str`, `destinacije: list[Destinacija]` |
| `Destinacija` | `kraj: str`, `regija: str`, `priblizna_razdalja_km: int`, `zakaj_primerno: str`, `aktivnosti: list[str]`, `primerno_za_sezono: bool` |

Iz istih razredov se ustvari tudi JSON shema, ki jo pošljemo modelu (`PredlogIzleta.model_json_schema()`), zato se oblika odgovora in razred vedno ujemata.

## Struktura

```text
naloga4-llm/
├── app.py              # Flask strežnik, sestavljanje prompta, klic modela
├── modeli.py           # razreda PredlogIzleta in Destinacija
├── templates/
│   └── index.html      # obrazec in prikaz rezultatov
├── requirements.txt
├── README.md
└── .env                # API ključ (ni v repozitoriju)
```

## Nastavitve

| Spremenljivka | Opis |
|---|---|
| `GEMINI_API_KEY` | API ključ za Gemini (brezplačno v Google AI Studio) |
| `GEMINI_MODEL` | neobvezno, privzeto `gemini-flash-latest` |

Ključ se shrani v datoteko `.env` v mapi `naloga4-llm`, ki jo aplikacija prebere ob zagonu (knjižnica `python-dotenv`). Datoteka `.env` je v `.gitignore` in ni del repozitorija:

```text
GEMINI_API_KEY=tvoj_kljuc
```

## Zagon

```bash
cd naloga4-llm
pip install -r requirements.txt
python app.py
```

Nato odpri http://127.0.0.1:5000

## Omejitve

- Model razdalje oceni le približno. Točno razdaljo in čas vožnje bo v glavni aplikaciji izračunal OpenRouteService.
- Model lahko občasno predlaga manj primeren kraj, zato so rezultati predlog, ne preverjen podatek.