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
from concurrent.futures import ThreadPoolExecutor

from buscador_vino.comparador import comparar_precios, elegir_similares
from buscador_vino.fuentes.config import FUENTES_DEMO, FUENTES_REALES
from buscador_vino.tabla import imprimir_mejor_precio, imprimir_tabla
from buscador_vino.variedades import detectar_variedad


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
        "--tipo",
        choices=["vinoteca", "bodega", "importador"],
        help="Buscar solo en un tipo de fuente (por default busca en las 30)",
    )
    parser.add_argument(
        "--timeout", type=int, default=30, help="Timeout total en segundos (default: 30)"
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Muestra logs detallados")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(levelname)s %(name)s: %(message)s",
    )

    fuentes = FUENTES_DEMO if args.demo else FUENTES_REALES
    if args.tipo:
        fuentes = [f for f in fuentes if f.tipo == args.tipo]

    if not args.demo:
        print(
            f"Buscando en {len(fuentes)} fuentes reales (scraping HTML, puede tardar "
            "un rato). Si una fuente no encuentra nada, puede que necesite ajuste de\n"
            "selectores (ver buscador_vino/fuentes/config.py y "
            "scripts/verificar_fuentes.py). Probá con --demo para ver el programa\n"
            "funcionando sin depender de la red.\n",
            file=sys.stderr,
        )

    variedad = detectar_variedad(args.vino)
    with ThreadPoolExecutor(max_workers=2) as pool:
        futuro_principal = pool.submit(comparar_precios, args.vino, fuentes, args.timeout)
        futuro_variedad = (
            pool.submit(comparar_precios, variedad, fuentes, args.timeout) if variedad else None
        )
        resultados = futuro_principal.result()
        pool_variedad = futuro_variedad.result() if futuro_variedad else []

    similares = elegir_similares(resultados, pool_variedad) if resultados else []

    print(imprimir_mejor_precio(resultados))
    if resultados:
        print("\nTodas las opciones:")
        print(imprimir_tabla(resultados))

    if similares:
        print(f"\nTambién te puede gustar ({variedad}, precio parecido):")
        print(imprimir_tabla(similares))

    if args.csv:
        with open(args.csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Vino", "Precio", "Moneda", "Fuente", "Tipo", "Link"])
            for r in resultados:
                writer.writerow([r.vino, r.precio, r.moneda, r.fuente, r.tipo_fuente, r.url])
        print(f"\nResultados exportados a {args.csv}")

    return 0 if resultados else 1


if __name__ == "__main__":
    sys.exit(main())
