import logging
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


class FuenteScraping(FuenteBase):
    """Fuente que busca en la página de resultados de un e-commerce y
    extrae nombre + precio con selectores CSS.

    Como no sabemos con certeza qué plataforma corre cada sitio real
    (ver `fuentes/config.py`), cada fuente puede traer más de un patrón
    de URL de búsqueda (`patrones_busqueda`, ej. uno para Magento y otro
    para Tiendanube): se prueban en orden y se usa el primero que
    devuelva productos reconocibles con los selectores dados. Si ninguno
    encuentra nada, la fuente devuelve una lista vacía sin romper el
    resto de la comparación.
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
        max_resultados: int = 5,
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

        for patron in self.patrones_busqueda:
            url = patron.format(base=self.base_url, query=query)
            resultados = self._probar_url(url)
            if resultados:
                return resultados

        logger.info(
            "%s: sin resultados para %r tras probar %d patrón(es) de URL",
            self.nombre,
            consulta,
            len(self.patrones_busqueda),
        )
        return []

    def _probar_url(self, url: str) -> List[ResultadoPrecio]:
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

        resultados: List[ResultadoPrecio] = []
        for item in items:
            nombre_el = item.select_one(self.selector_nombre)
            precio_el = item.select_one(self.selector_precio)
            if nombre_el is None or precio_el is None:
                continue

            precio = normalizar_precio(precio_el.get_text())
            if precio is None:
                continue

            link_el = item.select_one(self.selector_link)
            href = link_el.get("href", "") if link_el else ""
            if href.startswith("/"):
                href = self.base_url + href

            resultados.append(
                ResultadoPrecio(
                    vino=nombre_el.get_text(strip=True),
                    precio=precio,
                    moneda="ARS",
                    fuente=self.nombre,
                    tipo_fuente=self.tipo,
                    url=href or url,
                )
            )

        if not resultados:
            logger.debug(
                "%s: %s matcheó ítems pero ninguno tenía nombre+precio parseables",
                self.nombre,
                url,
            )
        return resultados
