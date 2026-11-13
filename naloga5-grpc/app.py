"""
RouteMate - Naloga 5: gRPC ODJEMALEC (Flask spletna aplikacija)
Brskalnik kliče Flask, Flask pa prek gRPC kliče strežnik (server.py).
Zagon: python app.py  ->  http://127.0.0.1:5000
"""
import json

import grpc
from flask import Flask, Response, jsonify, render_template, request
from google.protobuf.json_format import MessageToDict

import routemate_pb2 as pb
import routemate_pb2_grpc as pb_grpc

app = Flask(__name__)

# povezava na gRPC strežnik in nastavek (stub), prek katerega kličemo rpc-je
kanal = grpc.insecure_channel("localhost:50051")
stub = pb_grpc.RouteMateStub(kanal)


def v_slovar(sporocilo):
    """protobuf sporočilo -> Python slovar (za JSON brskalniku)"""
    return MessageToDict(sporocilo, preserving_proto_field_name=True)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/vozila")
def vozila():
    odgovor = stub.PridobiVozila(pb.Prazno())                 # RPC 1
    return jsonify(v_slovar(odgovor))


@app.route("/api/potovanja")
def potovanja():
    odgovor = stub.PridobiPotovanja(pb.Prazno())              # RPC 2
    return jsonify(v_slovar(odgovor))


@app.route("/api/strosek")
def strosek():
    zahtevek = pb.ZahtevekStrosek(potovanje_id=request.args["potovanje"],
                                  vozilo_id=request.args["vozilo"])
    try:
        odgovor = stub.IzracunajStrosek(zahtevek)             # RPC 3
    except grpc.RpcError as e:
        return jsonify({"napaka": e.details()}), 404
    return jsonify(v_slovar(odgovor))


@app.route("/api/voznja")
def voznja():
    zahtevek = pb.ZahtevekStrosek(potovanje_id=request.args["potovanje"],
                                  vozilo_id=request.args["vozilo"])

    def tok():
        # RPC 4 (streaming): vsak korak takoj posredujemo brskalniku (Server-Sent Events)
        for korak in stub.SimulirajVoznjo(zahtevek):
            yield f"data: {json.dumps(v_slovar(korak))}\n\n"
        yield "data: KONEC\n\n"

    return Response(tok(), mimetype="text/event-stream")


if __name__ == "__main__":
    app.run(debug=True)