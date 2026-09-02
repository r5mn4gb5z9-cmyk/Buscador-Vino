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

from buscador_vino.comparador import buscar_favoritos, comparar_precios, elegir_similares
from buscador_vino.favoritos import agregar_favorito, cargar_favoritos, quitar_favorito
from buscador_vino.fuentes.config import FUENTES_DEMO, FUENTES_REALES
from buscador_vino.fuentes.directorio import BODEGAS_SIN_TIENDA
from buscador_vino.tabla import (
    imprimir_directorio,
    imprimir_favoritos,
    imprimir_mejor_precio,
    imprimir_tabla,
)
from buscador_vino.variedades import detectar_variedad


def _filtrar_fuentes(args) -> list:
    fuentes = FUENTES_DEMO if args.demo else FUENTES_REALES
    if args.tipo:
        fuentes = [f for f in fuentes if f.tipo == args.tipo]
    if args.region:
        fuentes = [f for f in fuentes if args.region.lower() in f.region.lower()]
    if args.envio_nacional:
        fuentes = [f for f in fuentes if f.envio_nacional is True]
    return fuentes


def main() -> int:
    parser = argparse.ArgumentParser(description="Compara precios de un vino en varias fuentes.")
    parser.add_argument(
        "vino",
        nargs="?",
        help="Nombre del vino a buscar, ej: 'Rutini Malbec' (no hace falta con --directorio/--favoritos*)",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Usa fuentes simuladas (sin conexión a internet) para ver el programa funcionando",
    )
    parser.add_argument("--csv", metavar="ARCHIVO", help="Exporta los resultados a un CSV")
    parser.add_argument(
        "--tipo",
        choices=["vinoteca", "bodega", "importador"],
        help="Buscar solo en un tipo de fuente (por default busca en todas)",
    )
    parser.add_argument(
        "--region",
        help="Buscar solo en fuentes de esta región (ej. 'Mendoza', 'Salta'); coincide por substring, sin distinguir mayúsculas",
    )
    parser.add_argument(
        "--envio-nacional",
        action="store_true",
        help="Mostrar solo fuentes que declaran envío a todo el país en su propia web",
    )
    parser.add_argument(
        "--directorio",
        action="store_true",
        help="En vez de buscar un precio, lista bodegas/vinotecas boutique sin tienda online (usar junto con --region para filtrar)",
    )
    parser.add_argument(
        "--favoritos",
        action="store_true",
        help="Busca el precio más barato de cada favorito guardado (no hace falta pasar un vino)",
    )
    parser.add_argument(
        "--favoritos-agregar", metavar="NOMBRE", help="Agrega NOMBRE a favoritos y termina"
    )
    parser.add_argument(
        "--favoritos-quitar", metavar="NOMBRE", help="Saca NOMBRE de favoritos y termina"
    )
    parser.add_argument(
        "--favoritos-listar",
        action="store_true",
        help="Lista los favoritos guardados (sin buscar precios) y termina",
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

    if args.favoritos_agregar:
        if agregar_favorito(args.favoritos_agregar):
            print(f"Agregado a favoritos: {args.favoritos_agregar}")
        else:
            print(f"Ya estaba en favoritos: {args.favoritos_agregar}")
        return 0

    if args.favoritos_quitar:
        if quitar_favorito(args.favoritos_quitar):
            print(f"Sacado de favoritos: {args.favoritos_quitar}")
        else:
            print(f"No estaba en favoritos: {args.favoritos_quitar}")
        return 0

    if args.favoritos_listar:
        favoritos = cargar_favoritos()
        if not favoritos:
            print('No tenés favoritos guardados. Agregá uno con --favoritos-agregar "nombre".')
        else:
            for nombre in favoritos:
                print(f"- {nombre}")
        return 0

    if args.directorio:
        bodegas = BODEGAS_SIN_TIENDA
        if args.region:
            bodegas = [b for b in bodegas if args.region.lower() in b.region.lower()]
        print(imprimir_directorio(bodegas))
        return 0 if bodegas else 1

    if args.favoritos:
        favoritos = cargar_favoritos()
        if not favoritos:
            print('No tenés favoritos guardados. Agregá uno con --favoritos-agregar "nombre".')
            return 1
        fuentes = _filtrar_fuentes(args)
        print(
            f"Buscando el precio más barato de {len(favoritos)} favorito(s) en "
            f"{len(fuentes)} fuentes (uno por uno, puede tardar)...\n",
            file=sys.stderr,
        )
        resultados_por_favorito = buscar_favoritos(favoritos, fuentes, timeout_total=args.timeout)
        print(imprimir_favoritos(resultados_por_favorito))
        return 0 if any(res for _, res in resultados_por_favorito) else 1

    if not args.vino:
        parser.error(
            "hace falta el nombre de un vino para buscar (o usar --directorio / --favoritos)"
        )

    fuentes = _filtrar_fuentes(args)

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
            writer.writerow(["Vino", "Precio", "Moneda", "Fuente", "Tipo", "EnvioNacional", "Link"])
            for r in resultados:
                writer.writerow(
                    [r.vino, r.precio, r.moneda, r.fuente, r.tipo_fuente, r.envio_nacional, r.url]
                )
        print(f"\nResultados exportados a {args.csv}")

    return 0 if resultados else 1


if __name__ == "__main__":
    sys.exit(main())
