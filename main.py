#!/usr/bin/env python3
"""CLI: compara el precio de un vino entre vinotecas, bodegas e importadores.

Ejemplos:
    python main.py "Rutini Malbec"
    python main.py "Rutini Malbec" --demo
    python main.py "Rutini Malbec" --csv resultados.csv -v
"""
import argparse
import csv
import logging
import sys

from buscador_vino.comparador import comparar_precios
from buscador_vino.fuentes.config import FUENTES_DEMO, FUENTES_REALES
from buscador_vino.tabla import imprimir_mejor_precio, imprimir_tabla


def main() -> int:
    parser = argparse.ArgumentParser(description="Compara precios de un vino en varias fuentes.")
    parser.add_argument("vino", help="Nombre del vino a buscar, ej: 'Rutini Malbec'")
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Usa fuentes simuladas (sin conexión a internet) para ver el programa funcionando",
    )
    parser.add_argument("--csv", metavar="ARCHIVO", help="Exporta los resultados a un CSV")
    parser.add_argument(
        "--timeout", type=int, default=20, help="Timeout total en segundos (default: 20)"
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Muestra logs detallados")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(levelname)s %(name)s: %(message)s",
    )

    fuentes = FUENTES_DEMO if args.demo else FUENTES_REALES
    if not args.demo:
        print(
            "Nota: las fuentes reales usan scraping HTML con selectores CSS que\n"
            "pueden requerir ajuste si el sitio cambió de diseño (ver\n"
            "buscador_vino/fuentes/config.py). Probá con --demo para ver el\n"
            "programa funcionando sin depender de la red.\n",
            file=sys.stderr,
        )

    resultados = comparar_precios(args.vino, fuentes, timeout_total=args.timeout)

    print(imprimir_mejor_precio(resultados))
    if resultados:
        print("\nTodas las opciones:")
        print(imprimir_tabla(resultados))

    if args.csv:
        with open(args.csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Vino", "Precio", "Moneda", "Fuente", "Tipo"])
            for r in resultados:
                writer.writerow([r.vino, r.precio, r.moneda, r.fuente, r.tipo_fuente])
        print(f"\nResultados exportados a {args.csv}")

    return 0 if resultados else 1


if __name__ == "__main__":
    sys.exit(main())
