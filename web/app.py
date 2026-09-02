#!/usr/bin/env python3
"""Interfaz web (Flask) para el comparador de precios de vino.

Correr:
    pip install -r requirements.txt
    python web/app.py

Después abrí http://127.0.0.1:5000 en el navegador. Si lo corrés en una
compu y querés abrirlo desde el celu por la misma WiFi, fijate la IP local
de la compu (ej. 192.168.0.15) y entrá a http://192.168.0.15:5000 desde el
celu. Si lo corrés directo en el celu con Termux, abrí esa misma URL
(127.0.0.1:5000) en el navegador del celu.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, request

from buscador_vino.comparador import comparar_precios
from buscador_vino.fuentes.config import FUENTES_DEMO, FUENTES_REALES

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    vino = request.args.get("vino", "").strip()
    modo_demo = request.args.get("demo") == "1"
    tipo = request.args.get("tipo", "").strip()
    if tipo not in ("vinoteca", "bodega", "importador"):
        tipo = ""
    resultados = []
    buscado = False

    if vino:
        buscado = True
        fuentes = FUENTES_DEMO if modo_demo else FUENTES_REALES
        if tipo:
            fuentes = [f for f in fuentes if f.tipo == tipo]
        resultados = comparar_precios(vino, fuentes, timeout_total=30)

    return render_template(
        "index.html",
        vino=vino,
        modo_demo=modo_demo,
        tipo=tipo,
        resultados=resultados,
        buscado=buscado,
    )


if __name__ == "__main__":
    # Puerto configurable: en macOS el 5000 suele estar tomado por el
    # AirPlay Receiver de Control Center, así que el launcher de escritorio
    # (ver iniciar_buscador.command) lo levanta en otro puerto por default.
    puerto = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=puerto, debug=True)
