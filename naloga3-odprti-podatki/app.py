"""
RouteMate - Naloga 3: Odprti podatki (PC-Axis)
Zagon: python app.py  ->  http://127.0.0.1:5000
"""
import pandas as pd
from flask import Flask, jsonify, render_template, request
from pyaxis import pyaxis

# PX datoteka SURS (objavljena na podatki.gov.si)
PX_URL = "https://pxweb.stat.si/SiStatData/Resources/PX/Databases/Data/2164466S.PX"

app = Flask(__name__)
podatki = None  # tabela v pomnilniku


def nalozi_podatke():
    """Prebere najnovejšo PX datoteko neposredno z URL-ja (ob zagonu in ob kliku na 'Osveži')."""
    global podatki
    px = pyaxis.parse(uri=PX_URL, encoding="windows-1250", timeout=120)
    df = px["DATA"]

    # obdržimo samo prenočitve
    df = df[df["MERITVE"] == "Prenočitve turistov"].copy()
    # "-" in ".." (ni podatka / zaupno) -> NaN, ostalo v številke
    df["DATA"] = pd.to_numeric(df["DATA"], errors="coerce")
    # "2025M08" -> LETO 2025, MES 8
    df["LETO"] = df["MESEC"].str[:4].astype(int)
    df["MES"] = df["MESEC"].str[5:].astype(int)
    # "2.1 Avstrija" -> "Avstrija"
    df["DRŽAVA"] = df["DRŽAVA"].str.replace(r"^[\d.]+\s*", "", regex=True)

    podatki = df
    print("Podatki naloženi.")


def zadnje_polno_leto(df):
    """Zadnje leto z vsemi 12 meseci (ni zapisano na trdo)."""
    meseci = df.dropna(subset=["DATA"]).groupby("LETO")["MES"].nunique()
    return int(meseci[meseci == 12].index.max())


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/obcine")
def obcine():
    seznam = sorted(o for o in podatki["OBČINE"].unique() if o != "SLOVENIJA")
    return jsonify({
        "obcine": seznam,
        "zadnje_leto": int(podatki.dropna(subset=["DATA"])["LETO"].max()),
        "polno_leto": zadnje_polno_leto(podatki),
    })


@app.route("/api/gneca")
def gneca():
    obcina = request.args.get("obcina")
    mesec = int(request.args.get("mesec"))
    leto = zadnje_polno_leto(podatki)

    # FILTRIRANJE: samo izbrana občina
    d = podatki[podatki["OBČINE"] == obcina]
    skupaj = d[d["DRŽAVA"].str.contains("SKUPAJ")]   # vse države skupaj

    # prenočitve po mesecih v zadnjem polnem letu
    po_mesecih = (skupaj[skupaj["LETO"] == leto]
                  .groupby("MES")["DATA"].sum()
                  .reindex(range(1, 13), fill_value=0))
    povprecje = po_mesecih.mean()
    razmerje = po_mesecih[mesec] / povprecje if povprecje else 0

    if povprecje == 0:
        stopnja = "ni podatkov"          # SURS jih ne objavlja (zaupno)
    elif razmerje < 0.75:
        stopnja = "nizka"
    elif razmerje <= 1.25:
        stopnja = "srednja"
    else:
        stopnja = "visoka"

    # TOP 5 držav v izbranem mesecu
    drzave = d[(d["LETO"] == leto) & (d["MES"] == mesec)
               & ~d["DRŽAVA"].str.contains("SKUPAJ|DOMAČI|TUJI")]
    top = drzave.dropna(subset=["DATA"]).nlargest(5, "DATA")

    # AGREGACIJA: skupne prenočitve po letih (vsota 12 mesecev)
    polna_leta = skupaj[skupaj["LETO"] <= leto]          # samo polna leta
    trend = polna_leta.groupby("LETO")["DATA"].sum()

    return jsonify({
        "leto": leto,
        "stopnja": stopnja,
        "razmerje": round(float(razmerje), 2),
        "nocitve": int(po_mesecih[mesec]),
        "povprecje": round(float(povprecje)),
        "po_mesecih": [int(x) for x in po_mesecih],
        "top_drzave": [str(x) for x in top["DRŽAVA"]],
        "top_nocitve": [int(x) for x in top["DATA"]],
        "trend_leta": [int(x) for x in trend.index],
        "trend_nocitve": [int(x) for x in trend],
    })


@app.route("/api/osvezi", methods=["POST"])
def osvezi():
    nalozi_podatke()   # ponovno prenese PX datoteko s SURS
    return jsonify({"ok": True})


if __name__ == "__main__":
    nalozi_podatke()   # dinamičen prenos ob vsakem zagonu
    app.run()