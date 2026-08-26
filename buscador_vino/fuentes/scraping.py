import logging
import unicodedata
from typing import List, Optional
from urllib.parse import quote_plus

import requests
from bs4 import BeautifulSoup

from ..models import ResultadoPrecio
from ..parsing import normalizar_precio
from .base import FuenteBase

logger = logging.getLogger(__name__)

_USER_AGENT = (
    "Mozilla/5.0 (compatible; ComparadorDePreciosDeVino/1.0; "
    "uso personal, no automatizado en masa)"
)

# Precios de una botella de vino real en ARS: fuera de este rango es casi
# seguro un error de parseo (varios precios pegados sin separador, un
# combo/caja, o un elemento que no era un precio) y se descarta.
_PRECIO_MIN = 500
_PRECIO_MAX = 2_000_000

_STOPWORDS = {"de", "del", "la", "el", "los", "las", "y", "vino", "vinos", "bodega"}


def _normalizar_texto(s: str) -> str:
    s = unicodedata.normalize("NFKD", s.lower())
    return "".join(c for c in s if not unicodedata.combining(c))


def _tokens_relevantes(consulta: str) -> List[str]:
    return [
        t
        for t in _normalizar_texto(consulta).split()
        if len(t) >= 3 and t not in _STOPWORDS
    ]


class FuenteScraping(FuenteBase):
    """Fuente que busca en la página de resultados de un e-commerce y
    extrae nombre + precio con selectores CSS.

    Como no sabemos con certeza qué plataforma corre cada sitio real
    (ver `fuentes/config.py`), cada fuente puede traer más de un patrón
    de URL de búsqueda (`patrones_busqueda`, ej. uno para Magento y otro
    para Tiendanube): se prueban en orden y se usa el primero que
    devuelva productos reconocibles con los selectores dados.

    Que un patrón de URL "matchee" un ítem con los selectores no alcanza:
    hay sitios donde ese patrón termina cayendo en el catálogo genérico o
    la home en vez de una búsqueda real, y ahí aparecen productos que no
    tienen nada que ver (una botella de agua para "malbec"). Por eso cada
    ítem encontrado se filtra además por relevancia: el nombre tiene que
    compartir al menos una palabra con lo buscado. Si ningún ítem pasa el
    filtro, se prueba el siguiente patrón de URL antes de rendirse.
    """

    def __init__(
        self,
        nombre: str,
        tipo: str,
        base_url: str,
        patrones_busqueda: List[str],  # plantillas con "{base}" y "{query}"
        selector_item: str,
        selector_nombre: str,
        selector_precio: str,
        selector_link: Optional[str] = None,
        timeout: int = 10,
        max_resultados: int = 12,
    ):
        self.nombre = nombre
        self.tipo = tipo
        self.base_url = base_url.rstrip("/")
        self.patrones_busqueda = patrones_busqueda
        self.selector_item = selector_item
        self.selector_nombre = selector_nombre
        self.selector_precio = selector_precio
        self.selector_link = selector_link or selector_nombre
        self.timeout = timeout
        self.max_resultados = max_resultados

    def buscar(self, consulta: str) -> List[ResultadoPrecio]:
        query = quote_plus(consulta)
        tokens = _tokens_relevantes(consulta)

        for patron in self.patrones_busqueda:
            url = patron.format(base=self.base_url, query=query)
            resultados = self._probar_url(url, tokens)
            if resultados:
                return resultados

        logger.info(
            "%s: sin resultados relevantes para %r tras probar %d patrón(es) de URL",
            self.nombre,
            consulta,
            len(self.patrones_busqueda),
        )
        return []

    def _probar_url(self, url: str, tokens: List[str]) -> List[ResultadoPrecio]:
        try:
            resp = requests.get(
                url, headers={"User-Agent": _USER_AGENT}, timeout=self.timeout
            )
            resp.raise_for_status()
        except requests.RequestException as exc:
            logger.debug("%s: error de red en %s (%s)", self.nombre, url, exc)
            return []

        soup = BeautifulSoup(resp.text, "html.parser")
        items = soup.select(self.selector_item)[: self.max_resultados]
        if not items:
            logger.debug("%s: %s no matcheó ningún ítem", self.nombre, url)
            return []

        descartados_por_precio = 0
        descartados_por_relevancia = 0
        resultados: List[ResultadoPrecio] = []

        for item in items:
            nombre_el = item.select_one(self.selector_nombre)
            precio_el = item.select_one(self.selector_precio)
            if nombre_el is None or precio_el is None:
                continue

            nombre_vino = nombre_el.get_text(strip=True)
            if not nombre_vino:
                continue

            if tokens and not any(t in _normalizar_texto(nombre_vino) for t in tokens):
                descartados_por_relevancia += 1
                continue

            precio = normalizar_precio(precio_el.get_text(" ", strip=True))
            if precio is None or not (_PRECIO_MIN <= precio <= _PRECIO_MAX):
                descartados_por_precio += 1
                continue

            link_el = item.select_one(self.selector_link)
            href = link_el.get("href", "") if link_el else ""
            if href.startswith("/"):
                href = self.base_url + href

            resultados.append(
                ResultadoPrecio(
                    vino=nombre_vino,
                    precio=precio,
                    moneda="ARS",
                    fuente=self.nombre,
                    tipo_fuente=self.tipo,
                    url=href or url,
                )
            )

        if not resultados:
            logger.debug(
                "%s: %s matcheó %d ítem(s) pero ninguno quedó "
                "(%d por relevancia, %d por precio fuera de rango)",
                self.nombre,
                url,
                len(items),
                descartados_por_relevancia,
                descartados_por_precio,
            )
        return resultados
