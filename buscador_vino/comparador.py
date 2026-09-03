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
    # OJO: no usar "with ThreadPoolExecutor(...) as pool" acá. Al salir del
    # bloque "with" llama a pool.shutdown(wait=True), que bloquea hasta que
    # TODOS los hilos terminen — incluidos los que ya dejamos de esperar
    # más abajo por el timeout. Si un solo sitio queda con una conexión
    # colgada (más lenta que el timeout por request pero sin cortarse
    # nunca del todo), esa espera "por las dudas" terminaba haciendo que
    # `timeout_total` no sirviera de nada y la búsqueda entera se
    # congelara. Por eso se cierra el pool a mano con wait=False.
    pool = ThreadPoolExecutor(max_workers=max(1, len(fuentes)))
    try:
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
    finally:
        pool.shutdown(wait=False, cancel_futures=True)

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


def agrupar_mas_barato_por_vino(resultados: List[ResultadoPrecio]) -> List[ResultadoPrecio]:
    """Agrupa `resultados` por nombre de vino (normalizado, sin tildes ni
    mayúsculas) y se queda con el más barato de cada uno, devueltos
    ordenados de menor a mayor precio.

    Un favorito puede ser un vino puntual ("Rutini Malbec") o una bodega
    ("Bodega Chacra"): buscar el nombre de una bodega como texto libre
    encuentra todos los vinos de esa bodega que venden las fuentes (cada
    uno con su propio nombre), no un solo producto. Sin agrupar, nos
    quedábamos solo con el más barato de TODOS esos vinos mezclados y
    descartábamos el resto — con esto, cada vino/línea distinto que
    vende la bodega aparece con su propio más barato, en vez de mostrar
    uno solo "elegido al azar". Para un vino puntual esto da un único
    grupo, así que el comportamiento no cambia en ese caso.
    """
    mejores: dict = {}
    for r in resultados:
        clave = normalizar(r.vino)
        actual = mejores.get(clave)
        if actual is None or r.precio < actual.precio:
            mejores[clave] = r

    agrupados = list(mejores.values())
    agrupados.sort(key=lambda r: r.precio)
    return agrupados


def buscar_favoritos(
    favoritos: List[str], fuentes: List[FuenteBase], timeout_total: int = 20
) -> List[Tuple[str, List[ResultadoPrecio]]]:
    """Busca cada nombre de `favoritos` en `fuentes` y devuelve, para cada
    uno, un resultado por cada vino/línea distinto encontrado (el más
    barato de cada uno — ver `agrupar_mas_barato_por_vino`), ordenados de
    menor a mayor precio.

    Los favoritos se buscan uno por uno, no todos en simultáneo: cada
    búsqueda ya dispara un pedido HTTP a cada fuente en paralelo, así que
    lanzar varios favoritos a la vez multiplicaría esa carga sobre los
    mismos sitios (ver "Uso responsable" en el README).
    """
    return [
        (nombre, agrupar_mas_barato_por_vino(comparar_precios(nombre, fuentes, timeout_total)))
        for nombre in favoritos
    ]
