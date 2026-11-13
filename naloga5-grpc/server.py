"""
RouteMate - Naloga 5: gRPC STREŽNIK
Podatke prebere iz XML datotek Naloge 1 in jih ponuja prek gRPC.
Zagon: python server.py  (posluša na portu 50051)
"""
import time
import xml.etree.ElementTree as ET
from concurrent import futures
from pathlib import Path

import grpc

import routemate_pb2 as pb             # generirano: sporočila
import routemate_pb2_grpc as pb_grpc   # generirano: nastavek (stub) in osnova strežnika

DATA = Path(__file__).parent.parent / "naloga1-xml-json" / "data"
CENE = {"bencin": 1.45, "dizel": 1.50, "hibrid": 1.45}  # €/l, poenostavljeno


def preberi_vozila():
    koren = ET.parse(DATA / "vozila.xml").getroot()
    return {
        v.get("id"): pb.Vozilo(
            id=v.get("id"),
            znamka=v.findtext("znamka"),
            model=v.findtext("model"),
            vrsta_goriva=v.findtext("vrstaGoriva"),
            poraba=float(v.findtext("poraba")),
        )
        for v in koren.findall("vozilo")
    }


def preberi_potovanja():
    koren = ET.parse(DATA / "potovanja.xml").getroot()
    return {
        p.get("id"): pb.Potovanje(
            id=p.get("id"),
            zacetek=p.findtext("zacetek"),
            cilj=p.findtext("cilj"),
            razdalja_km=float(p.findtext("razdaljaKm")),
            trajanje_min=int(p.findtext("trajanjeMin")),
        )
        for p in koren.findall("potovanje")
    }


VOZILA = preberi_vozila()
POTOVANJA = preberi_potovanja()


class RouteMateStoritev(pb_grpc.RouteMateServicer):
    """Vsaka metoda = en rpc iz routemate.proto (enako ime)."""

    def PridobiVozila(self, request, context):
        return pb.SeznamVozil(vozila=VOZILA.values())

    def PridobiPotovanja(self, request, context):
        return pb.SeznamPotovanj(potovanja=POTOVANJA.values())

    def IzracunajStrosek(self, request, context):
        potovanje = POTOVANJA.get(request.potovanje_id)
        vozilo = VOZILA.get(request.vozilo_id)
        if not potovanje or not vozilo:
            context.abort(grpc.StatusCode.NOT_FOUND, "Potovanje ali vozilo ne obstaja.")

        litri = potovanje.razdalja_km * vozilo.poraba / 100
        cena = CENE[vozilo.vrsta_goriva]
        return pb.Strosek(litri=round(litri, 2), cena_litra=cena,
                          skupaj_eur=round(litri * cena, 2))

    def SimulirajVoznjo(self, request, context):
        """Streaming: namesto return uporabimo yield -> pošljemo 10 sporočil, eno za drugim."""
        potovanje = POTOVANJA.get(request.potovanje_id)
        vozilo = VOZILA.get(request.vozilo_id)
        if not potovanje or not vozilo:
            context.abort(grpc.StatusCode.NOT_FOUND, "Potovanje ali vozilo ne obstaja.")

        cena = CENE[vozilo.vrsta_goriva]
        for korak in range(1, 11):
            km = potovanje.razdalja_km * korak / 10
            litri = km * vozilo.poraba / 100
            yield pb.Napredek(odstotek=korak * 10, prevozeni_km=round(km, 1),
                              porabljeni_litri=round(litri, 2),
                              strosek_eur=round(litri * cena, 2))
            time.sleep(0.5)


def zazeni():
    streznik = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb_grpc.add_RouteMateServicer_to_server(RouteMateStoritev(), streznik)
    streznik.add_insecure_port("[::]:50051")
    streznik.start()
    print("gRPC strežnik teče na portu 50051 ...")
    streznik.wait_for_termination()


if __name__ == "__main__":
    zazeni()