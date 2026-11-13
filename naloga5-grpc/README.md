# Naloga 5 – gRPC

RouteMate prek gRPC povezave pridobi vozila in potovanja (podatki iz Naloge 1), izračuna strošek goriva za izbrano potovanje in vozilo ter v realnem času prikaže simulacijo vožnje.

## Arhitektura

```text
Brskalnik  --HTTP-->  app.py (Flask, gRPC odjemalec)  --gRPC-->  server.py (gRPC strežnik)
                                                                   bere XML iz naloga1-xml-json/data
```

Brskalnik ne more neposredno komunicirati prek gRPC, zato je vmes Flask aplikacija, ki je gRPC odjemalec.

## Protokol (`routemate.proto`)

**Storitev:** `RouteMate`

| RPC klic | Zahtevek | Odgovor | Tip |
|---|---|---|---|
| `PridobiVozila` | `Prazno` | `SeznamVozil` | preprost RPC |
| `PridobiPotovanja` | `Prazno` | `SeznamPotovanj` | preprost RPC |
| `IzracunajStrosek` | `ZahtevekStrosek` | `Strosek` | preprost RPC |
| `SimulirajVoznjo` | `ZahtevekStrosek` | `stream Napredek` | server-side streaming |

**Sporočila s podatkovnimi tipi:** `Vozilo`, `Potovanje`, `Strosek`, `Napredek`, `ZahtevekStrosek`, `SeznamVozil`, `SeznamPotovanj`, `Prazno`.

## Delovanje

1. Ob odprtju strani se prek `PridobiPotovanja` in `PridobiVozila` napolnita spustna seznama.
2. Uporabnik izbere potovanje in vozilo.
3. **Izračunaj strošek** pokliče `IzracunajStrosek`, strežnik izračuna porabo (razdalja × poraba / 100) in strošek.
4. **Simuliraj vožnjo** pokliče `SimulirajVoznjo`. Strežnik pošlje 10 sporočil `Napredek` (vsakih 0,5 s), Flask vsako takoj posreduje brskalniku (Server-Sent Events), ki sproti posodablja vrstico napredka, km, litre in strošek.

Cene goriva so poenostavljene in fiksne (bencin in hibrid 1,45 €/l, dizel 1,50 €/l).

## Struktura

```text
naloga5-grpc/
├── routemate.proto          # definicija storitve in sporočil
├── routemate_pb2.py         # generirano: sporočila
├── routemate_pb2_grpc.py    # generirano: nastavek (stub) in osnova strežnika
├── server.py                # gRPC strežnik
├── app.py                   # Flask spletna aplikacija = gRPC odjemalec
├── templates/
│   └── index.html           # uporabniški vmesnik
├── requirements.txt
└── README.md
```

## Zagon

```bash
cd naloga5-grpc
pip install -r requirements.txt

# generiranje kode iz .proto (samo ob spremembi routemate.proto)
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. routemate.proto

# terminal 1
python server.py

# terminal 2
python app.py
```

Nato odpri http://127.0.0.1:5000