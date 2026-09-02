import logging
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError, as_completed
from typing import List, Tuple

from .fuentes.base import FuenteBase
from .models import ResultadoPrecio
from .texto import normalizar

logger = logging.getLogger(__name__)


def comparar_precios(
    consulta: str, fuentes: List[FuenteBase], timeout_total: int = 20
) -> List[ResultadoPrecio]:
    """Busca `consulta` en todas las `fuentes` en paralelo y devuelve los
    resultados combinados, ordenados de menor a mayor precio.

    Si una fuente falla (red, parsing, timeout) se ignora y se sigue con
    las demás: un resultado parcial es preferible a que todo el programa
    se caiga por un solo sitio caído o con el HTML cambiado.
    """
    resultados: List[ResultadoPrecio] = []
    with ThreadPoolExecutor(max_workers=max(1, len(fuentes))) as pool:
        futuros = {pool.submit(f.buscar, consulta): f for f in fuentes}
        try:
            for futuro in as_completed(futuros, timeout=timeout_total):
                fuente = futuros[futuro]
                try:
                    resultados.extend(futuro.result())
                except Exception as exc:  # noqa: BLE001 - una fuente no debe tumbar todo
                    logger.warning("%s: fallo al buscar (%s)", fuente.nombre, exc)
        except FuturesTimeoutError:
            logger.warning("Tiempo de espera agotado; se muestran resultados parciales")

    resultados.sort(key=lambda r: r.precio)
    return resultados


def elegir_similares(
    resultados_originales: List[ResultadoPrecio],
    pool_variedad: List[ResultadoPrecio],
    max_resultados: int = 6,
) -> List[ResultadoPrecio]:
    """Arma una sección "también te puede gustar" a partir de datos
    propios en vez de Vivino: los términos de servicio de Vivino prohíben
    el scraping automatizado (y no tienen una API pública gratuita para
    esto), así que en su lugar comparamos por variedad de uva y precio
    parecido dentro de las mismas 30 fuentes que ya scrapeamos. Como
    contrapartida no hay rating ni descripción — esos datos no existen en
    nuestras fuentes propias.

    `pool_variedad` debe venir de buscar la variedad de uva sola (ver
    `buscador_vino.variedades.detectar_variedad`) en las mismas fuentes,
    para tener un universo más amplio de vinos que comparar. Se excluyen
    los vinos que ya aparecen en `resultados_originales` (mismo nombre
    normalizado) y se eligen los `max_resultados` con precio más cercano
    al del resultado más barato, devueltos ordenados de menor a mayor.
    """
    if not resultados_originales or not pool_variedad:
        return []

    ya_encontrados = {normalizar(r.vino) for r in resultados_originales}
    precio_referencia = resultados_originales[0].precio

    candidatos = [r for r in pool_variedad if normalizar(r.vino) not in ya_encontrados]
    candidatos.sort(key=lambda r: abs(r.precio - precio_referencia))

    similares = candidatos[:max_resultados]
    similares.sort(key=lambda r: r.precio)
    return similares


def buscar_favoritos(
    favoritos: List[str], fuentes: List[FuenteBase], timeout_total: int = 20
) -> List[Tuple[str, List[ResultadoPrecio]]]:
    """Busca cada nombre de `favoritos` en `fuentes` y devuelve, para cada
    uno, todos los resultados encontrados (ya ordenados de menor a mayor
    precio por `comparar_precios`; el primero es el más barato).

    Los favoritos se buscan uno por uno, no todos en simultáneo: cada
    búsqueda ya dispara un pedido HTTP a cada fuente en paralelo, así que
    lanzar varios favoritos a la vez multiplicaría esa carga sobre los
    mismos sitios (ver "Uso responsable" en el README).
    """
    return [(nombre, comparar_precios(nombre, fuentes, timeout_total)) for nombre in favoritos]
