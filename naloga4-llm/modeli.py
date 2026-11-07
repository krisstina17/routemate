"""
RouteMate - Naloga 4: razredi, v katere deserializiramo JSON odgovor modela.
"""
from pydantic import BaseModel, Field


class Destinacija(BaseModel):
    kraj: str = Field(description="Ime resničnega kraja v Sloveniji, npr. 'Bled'.")
    regija: str = Field(description="Statistična ali turistična regija, npr. 'Gorenjska'.")
    priblizna_razdalja_km: int = Field(description="Približna razdalja z avtom od začetne lokacije v km.")
    zakaj_primerno: str = Field(description="1-2 stavka, zakaj je kraj primeren za tega uporabnika.")
    aktivnosti: list[str] = Field(description="2-4 konkretne aktivnosti v kraju.")
    primerno_za_sezono: bool = Field(description="Ali je izlet primeren za letni čas potovanja.")


class PredlogIzleta(BaseModel):
    povzetek: str = Field(description="En stavek, ki povzame predloge.")
    destinacije: list[Destinacija] = Field(description="Natanko 3 predlagane destinacije.")