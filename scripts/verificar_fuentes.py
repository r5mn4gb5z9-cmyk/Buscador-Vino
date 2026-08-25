#!/usr/bin/env python3
"""Diagnóstico: prueba cada fuente real una por una y muestra si

devolvió resultados o no, para saber rápido cuáles hay que ajustar.

Este script pega contra los 30 sitios reales (no el modo demo), así que
hace falta correrlo con conexión a internet real, no funciona desde un
sandbox con salida de red restringida.

Uso:
    python scripts/verificar_fuentes.py
    python scripts/verificar_fuentes.py "malbec"
    python scripts/verificar_fuentes.py "malbec" -v   # ver qué URL probó cada una
"""
import logging
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from buscador_vino.fuentes.config import FUENTES_REALES

CONSULTA_DEFAULT = "malbec"


def main() -> int:
    args = sys.argv[1:]
    verbose = "-v" in args or "--verbose" in args
    args = [a for a in args if a not in ("-v", "--verbose")]
    consulta = args[0] if args else CONSULTA_DEFAULT

    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.ERROR,
        format="  %(levelname)s %(message)s",
    )

    print(f'Probando {len(FUENTES_REALES)} fuentes con la búsqueda "{consulta}"...\n')

    ok, fallidas = 0, []
    ancho_nombre = max(len(f.nombre) for f in FUENTES_REALES)

    for fuente in FUENTES_REALES:
        inicio = time.time()
        try:
            resultados = fuente.buscar(consulta)
        except Exception as exc:  # noqa: BLE001 - queremos ver cualquier fuente rota
            resultados = []
            print(f"  {fuente.nombre.ljust(ancho_nombre)}  ERROR: {exc}")
            fallidas.append(fuente.nombre)
            continue

        tardo = time.time() - inicio
        estado = "OK  " if resultados else "VACÍO"
        linea = f"  [{estado}] {fuente.nombre.ljust(ancho_nombre)}  ({fuente.tipo}, {tardo:.1f}s)"
        if resultados:
            linea += f" -> {len(resultados)} resultado(s), ej: {resultados[0].vino!r} ${resultados[0].precio}"
            ok += 1
        else:
            fallidas.append(fuente.nombre)
        print(linea)

    print(f"\n{ok}/{len(FUENTES_REALES)} fuentes devolvieron resultados.")
    if fallidas:
        print("\nSin resultados (ajustar selectores/patrón de URL en fuentes/config.py):")
        for nombre in fallidas:
            print(f"  - {nombre}")
        print(
            "\nTip: corré con -v para ver, por fuente, qué URLs se probaron y por qué "
            "no matchearon (selector vacío, error de red, etc)."
        )

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
