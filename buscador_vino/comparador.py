import logging
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError, as_completed
from typing import List

from .fuentes.base import FuenteBase
from .models import ResultadoPrecio

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
