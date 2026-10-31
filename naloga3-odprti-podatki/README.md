# Naloga 3 – Odprti podatki (PC-Axis)

RouteMate prikaže, kako polna je izbrana destinacija (občina) v mesecu potovanja.

## Vir podatkov
- Statistični urad RS (SURS), objavljeno na OPSI (podatki.gov.si):
  "Prihodi in prenočitve turistov po državah, občine, Slovenija, mesečno"
- Format: PC-Axis (.px)
- URL: https://pxweb.stat.si/SiStatData/Resources/PX/Databases/Data/2164466S.PX

Datoteka se ne hrani v projektu – aplikacija jo prebere neposredno z URL-ja
ob vsakem zagonu in ob kliku na gumb "Osveži podatke".

## Obdelava
- filtriranje: samo prenočitve, izbrana občina, vse države skupaj, zadnje polno leto, izbrani mesec
- agregacija: vsota prenočitev po letih (12 mesecev), povprečje mesecev, top 5 držav
- zadnje leto ni zapisano na trdo – določi se samodejno (zadnje leto z vsemi 12 meseci)

## Prikaz (Chart.js)
1. prenočitve po mesecih (izbrani mesec obarvan rdeče)
2. top 5 držav v izbranem mesecu
3. skupne prenočitve po letih

Turistična gneča: mesec / povprečje meseca → nizka (< 0,75), srednja (0,75–1,25), visoka (> 1,25).

## Zagon
pip install -r requirements.txt
python app.py
Odpri http://127.0.0.1:5000