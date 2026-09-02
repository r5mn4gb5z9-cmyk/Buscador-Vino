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
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, request

from buscador_vino.comparador import comparar_precios, elegir_similares
from buscador_vino.fuentes.config import FUENTES_DEMO, FUENTES_REALES
from buscador_vino.fuentes.directorio import BODEGAS_SIN_TIENDA
from buscador_vino.variedades import detectar_variedad

app = Flask(__name__)

REGIONES = sorted({f.region for f in FUENTES_REALES if f.region})


@app.route("/", methods=["GET"])
def index():
    vino = request.args.get("vino", "").strip()
    modo_demo = request.args.get("demo") == "1"
    tipo = request.args.get("tipo", "").strip()
    if tipo not in ("vinoteca", "bodega", "importador"):
        tipo = ""
    region = request.args.get("region", "").strip()
    if region not in REGIONES:
        region = ""
    resultados = []
    similares = []
    variedad = None
    buscado = False

    if vino:
        buscado = True
        fuentes = FUENTES_DEMO if modo_demo else FUENTES_REALES
        if tipo:
            fuentes = [f for f in fuentes if f.tipo == tipo]
        if region:
            fuentes = [f for f in fuentes if f.region == region]

        variedad = detectar_variedad(vino)
        with ThreadPoolExecutor(max_workers=2) as pool:
            futuro_principal = pool.submit(comparar_precios, vino, fuentes, 30)
            futuro_variedad = (
                pool.submit(comparar_precios, variedad, fuentes, 30) if variedad else None
            )
            resultados = futuro_principal.result()
            pool_variedad = futuro_variedad.result() if futuro_variedad else []

        similares = elegir_similares(resultados, pool_variedad) if resultados else []

    return render_template(
        "index.html",
        vino=vino,
        modo_demo=modo_demo,
        tipo=tipo,
        region=region,
        regiones=REGIONES,
        resultados=resultados,
        similares=similares,
        variedad=variedad,
        buscado=buscado,
    )


@app.route("/directorio", methods=["GET"])
def directorio():
    region = request.args.get("region", "").strip()
    bodegas = BODEGAS_SIN_TIENDA
    if region:
        bodegas = [b for b in bodegas if b.region == region]

    return render_template(
        "directorio.html",
        bodegas=bodegas,
        region=region,
        regiones=sorted({b.region for b in BODEGAS_SIN_TIENDA}),
    )


if __name__ == "__main__":
    # Puerto configurable: en macOS el 5000 suele estar tomado por el
    # AirPlay Receiver de Control Center, así que el launcher de escritorio
    # (ver iniciar_buscador.command) lo levanta en otro puerto por default.
    puerto = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=puerto, debug=True)
