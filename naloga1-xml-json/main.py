import xml.etree.ElementTree as ET      
from pathlib import Path          
import json    

BASE_DIR = Path(__file__).resolve().parent

xml_pot = BASE_DIR / "data" / "uporabniki.xml"

tree_uporabniki = ET.parse(xml_pot)
root_uporabniki = tree_uporabniki.getroot()  

uporabniki = []

for uporabnik in root_uporabniki.findall("uporabnik"):
    id = uporabnik.get("id")
    ime = uporabnik.findtext("ime")
    priimek = uporabnik.findtext("priimek")

    podatki = {
        "id" : id,
        "ime" : ime,
        "priimek" : priimek
    }

    uporabniki.append(podatki)

print("\nUPORABNIKI:")
for uporabnik in uporabniki:
    print(uporabnik)
# print(uporabniki[0]["ime"])


tree_vozila = ET.parse(BASE_DIR / "data" / "vozila.xml")
root_vozila = tree_vozila.getroot()

vozila = []

for vozilo in root_vozila.findall("vozilo"):
    podatki = {
        "id" : vozilo.get("id"),
        "uporabnikId" : vozilo.findtext("uporabnikId"),
        "znamka" : vozilo.findtext("znamka"),
        "model" : vozilo.findtext("model"),
        "vrstaGoriva" : vozilo.findtext("vrstaGoriva"),
        "poraba" : float(vozilo.findtext("poraba"))
    }
    vozila.append(podatki)

print("\nVOZILA:")
for vozilo in vozila:
    print(vozilo)


print("\nVOZILA IN NJIHOVI LASTNIKI:")

for vozilo in vozila:
    for uporabnik in uporabniki:
        if vozilo["uporabnikId"] == uporabnik["id"]:
            print(
                uporabnik["ime"],
                uporabnik["priimek"],
                " - ",
                vozilo["znamka"],
                vozilo["model"]
            )


tree_potovanja = ET.parse(BASE_DIR / "data" / "potovanja.xml")
root_potovanja = tree_potovanja.getroot()

potovanja = []

for potovanje in root_potovanja.findall("potovanje"):
    podatki = {
        "id": potovanje.get("id"),
        "uporabnikId": potovanje.findtext("uporabnikId"),
        "voziloId": potovanje.findtext("voziloId"),
        "zacetek": potovanje.findtext("zacetek"),
        "cilj": potovanje.findtext("cilj"),
        "datum": potovanje.findtext("datum"),
        "razdaljaKm": float(potovanje.findtext("razdaljaKm")),
        "trajanjeMin": int(potovanje.findtext("trajanjeMin")),
        "opomba": potovanje.findtext("opomba")
    }
    potovanja.append(podatki)

print("\nPOTOVANJA:")
for potovanje in potovanja:
    print(potovanje)

print("\nPOTOVANJA S PODATKI O UPORABNIKIH IN VOZILIH:")
for potovanje in potovanja:
    for uporabnik in uporabniki:
        for vozilo in vozila:
            if (potovanje["uporabnikId"] == uporabnik["id"] and 
                potovanje["voziloId"] == vozilo["id"] and 
                vozilo["uporabnikId"] == uporabnik["id"]):

                print(
                    potovanje["id"],
                    "-",
                    uporabnik["ime"],
                    uporabnik["priimek"],
                    "-",
                    vozilo["znamka"],
                    vozilo["model"],
                    "-",
                    potovanje["zacetek"],
                    "->",
                    potovanje["cilj"]
                )


# Meni za filtriranje potovanj

print("\n========== ROUTEMATE ==========")
print("1 - Filtriranje po cilju")
print("2 - Filtriranje po najvecji razdalji")
print("3 - Filtriranje po datumu")
print("0 - Izhod")

izbira = input("\nIzberite moznost: ")

filtrirana_potovanja = []

if izbira == "1":
    cilj = input("Vnesite cilj potovanja: ")

    for potovanje in potovanja:
        if potovanje["cilj"].lower() == cilj.lower():
            filtrirana_potovanja.append(potovanje)

elif izbira == "2":
    max_razdalja = float(input("Vnesite najvecjo razdaljo (km): "))

    for potovanje in potovanja:
        if potovanje["razdaljaKm"] <= max_razdalja:
            filtrirana_potovanja.append(potovanje)

elif izbira == "3":
    datum = input("Vnesite datum (YYYY-MM-DD): ")

    for potovanje in potovanja:
        if potovanje["datum"] == datum:
            filtrirana_potovanja.append(potovanje)

elif izbira == "0":
    print("Izhod iz programa.")

else:
    print("Napacna izbira.")

if izbira in ("1", "2", "3"):
    print("\nFILTRIRANA POTOVANJA:")

    for potovanje in filtrirana_potovanja:
        print(
            potovanje["id"],
            "-",
            potovanje["zacetek"],
            "->",
            potovanje["cilj"],
            "|",
            potovanje["razdaljaKm"],
            "km |",
            potovanje["datum"]
        )

    print("Stevilo najdenih potovanj:", len(filtrirana_potovanja))

    # Izvoz filtriranih potovanj v JSON
    json_pot = BASE_DIR / "filtrirano.json"
    
    with open(json_pot, "w", encoding="utf-8") as datoteka: 
        json.dump(filtrirana_potovanja, datoteka, indent=4, ensure_ascii=False)

    print("Podatki so izvozeni v filtrirano.json")

    # Izvoz filtriranih potovanj v XML

    xml_root = ET.Element("potovanja")

    for potovanje in filtrirana_potovanja:

        xml_potovanje = ET.SubElement(xml_root, "potovanje", id = potovanje["id"])

        for kljuc, vrednost in potovanje.items():

            if kljuc != "id":
                element = ET.SubElement(xml_potovanje, kljuc)

                if vrednost is not None:
                    element.text = str(vrednost)
                else:
                    element.text = ""

    xml_tree = ET.ElementTree(xml_root)

    ET.indent(xml_tree, space="   ")

    xml_izhod = BASE_DIR / "filtrirano.xml"

    xml_tree.write(xml_izhod, encoding="utf-8", xml_declaration=True)

    print("Podatki so izvozeni v filtrirano.xml")




    


