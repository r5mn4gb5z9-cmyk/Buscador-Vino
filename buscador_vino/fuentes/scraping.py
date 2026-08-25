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
    """Fuente genérica que busca en la página de resultados de un
    e-commerce y extrae nombre + precio con selectores CSS.

    IMPORTANTE: cada sitio tiene su propio HTML y lo puede cambiar en
    cualquier momento. Los selectores se pasan por parámetro para que
    ajustarlos sea cuestión de editar `fuentes/config.py`, sin tocar
    esta clase. Para encontrar los selectores correctos de un sitio:
    abrí la página de resultados de búsqueda en el navegador, F12 ->
    inspeccionar un producto, y fijate qué clases envuelven el nombre
    y el precio.
    """

    def __init__(
        self,
        nombre: str,
        tipo: str,
        url_busqueda: str,  # debe incluir "{query}"
        selector_item: str,
        selector_nombre: str,
        selector_precio: str,
        base_url: str = "",
        selector_link: Optional[str] = None,
        timeout: int = 10,
        max_resultados: int = 5,
    ):
        self.nombre = nombre
        self.tipo = tipo
        self.url_busqueda = url_busqueda
        self.selector_item = selector_item
        self.selector_nombre = selector_nombre
        self.selector_precio = selector_precio
        self.selector_link = selector_link or selector_nombre
        self.base_url = base_url
        self.timeout = timeout
        self.max_resultados = max_resultados

    def buscar(self, consulta: str) -> List[ResultadoPrecio]:
        url = self.url_busqueda.format(query=quote_plus(consulta))
        try:
            resp = requests.get(
                url, headers={"User-Agent": _USER_AGENT}, timeout=self.timeout
            )
            resp.raise_for_status()
        except requests.RequestException as exc:
            logger.warning("%s: error de red al consultar %s (%s)", self.nombre, url, exc)
            return []

        soup = BeautifulSoup(resp.text, "html.parser")
        items = soup.select(self.selector_item)[: self.max_resultados]
        if not items:
            logger.info(
                "%s: no matchearon items para %r (selector %r puede estar desactualizado)",
                self.nombre,
                consulta,
                self.selector_item,
            )
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
            if href.startswith("/") and self.base_url:
                href = self.base_url.rstrip("/") + href

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
        return resultados
