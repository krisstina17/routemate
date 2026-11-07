"""
RouteMate - Naloga 4: Uporaba LLM
Predlog destinacij za izlet po Sloveniji (Gemini, odgovor v JSON).
Zagon: python app.py  ->  http://127.0.0.1:5000
"""
import os
from datetime import date

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from google import genai

from modeli import PredlogIzleta

load_dotenv()  # prebere GEMINI_API_KEY iz datoteke .env

MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash")

app = Flask(__name__)
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))


def letni_cas(datum):
    """Iz datuma določi letni čas."""
    m = datum.month
    if m in (12, 1, 2):
        return "zima"
    if m in (3, 4, 5):
        return "pomlad"
    if m in (6, 7, 8):
        return "poletje"
    return "jesen"


def sestavi_prompt(vnos):
    """Prompt sestavimo dinamično iz podatkov, ki jih je vnesel uporabnik."""
    datum = date.fromisoformat(vnos["datum"])
    interesi = ", ".join(vnos["interesi"]) or "karkoli"
    return (
        f"Si turistični svetovalec za Slovenijo. "
        f"Uporabnik začne pot v kraju {vnos['zacetek']} in želi z avtom voziti "
        f"največ {vnos['max_km']} km v eno smer. "
        f"Potuje {datum.strftime('%d. %m. %Y')} (letni čas: {letni_cas(datum)}), "
        f"družba: {vnos['druzba']}, proračun: {vnos['proracun']}. "
        f"Zanimajo ga: {interesi}. "
        f"Predlagaj natanko 3 različne resnične kraje v Sloveniji, ki niso {vnos['zacetek']} "
        f"in so od začetka oddaljeni največ {vnos['max_km']} km. "
        f"Aktivnosti naj bodo primerne za ta letni čas. "
        f"Odgovori v slovenščini, samo v JSON obliki po podani shemi."
    )


def vprasaj_llm(prompt):
    """Pošlje prompt modelu in JSON odgovor pretvori v objekt razreda PredlogIzleta."""
    odgovor = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config={
            "response_mime_type": "application/json",                  # model naj vrne JSON
            "response_json_schema": PredlogIzleta.model_json_schema(),  # po naši shemi
        },
    )
    return PredlogIzleta.model_validate_json(odgovor.text)  # JSON besedilo -> objekt


@app.route("/")
def index():
    return render_template("index.html", danes=date.today().isoformat())


@app.route("/api/predlog", methods=["POST"])
def predlog():
    vnos = request.get_json()        # JSON iz brskalnika -> Python slovar
    prompt = sestavi_prompt(vnos)

    try:
        rezultat = vprasaj_llm(prompt)
    except Exception as e:
        return jsonify({"napaka": f"Napaka pri klicu modela: {e}"}), 502

    # objekt -> slovar -> JSON za brskalnik
    return jsonify({"prompt": prompt, "predlog": rezultat.model_dump()})


if __name__ == "__main__":
    app.run(debug=True)