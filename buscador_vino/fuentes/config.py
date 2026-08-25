"""Definición de las 30 fuentes de precios a comparar: 10 vinotecas,
10 bodegas (venta directa) y 10 importadoras/especialistas en vinos
importados, todas de Argentina.

Los nombres, rubros y dominios de `FUENTES_INFO` salen de resultados de
búsqueda reales (no están inventados), pero **la plataforma de e-commerce
de cada sitio y sus selectores CSS no se pudieron confirmar en vivo**:
esta sesión de desarrollo corre en un entorno con salida de red
restringida (proxy) que bloquea el acceso a estos dominios, así que nunca
se llegó a inspeccionar el HTML real de cada búsqueda.

Para compensar eso, cada fuente prueba 2 patrones de URL de búsqueda
típicos de las plataformas más usadas en Argentina (Magento, WooCommerce,
Tiendanube, Shopify, VTEX) y, en cada intento, selectores CSS "unión" que
cubren las 5 a la vez (ver `plataformas.py`). Así, aunque no sepamos con
certeza qué plataforma corre un sitio puntual, hay bastante más
probabilidad de que alguno de los intentos funcione tal cual.

Para saber qué fuentes están andando de verdad, corré:

    python scripts/verificar_fuentes.py

Si una fuente sigue sin devolver nada después de eso, hay que mirar el
HTML real de esa búsqueda (F12 en el navegador) y ajustar sus selectores
o patrón de URL a mano.

FUENTES_DEMO no depende de internet: sirve para probar la comparación y
la tabla/resumen de salida de punta a punta ahora mismo (`--demo`).
"""

import hashlib

from .mock import FuenteSimulada
from .plataformas import SELECTOR_ITEM, SELECTOR_LINK, SELECTOR_NOMBRE, SELECTOR_PRECIO, patrones_para
from .scraping import FuenteScraping

# Cada entrada: nombre, tipo, dominio base y hasta 2 plataformas candidatas
# (se prueban en ese orden). "plataformas" es una apuesta informada según
# patrones de URL vistos en resultados de búsqueda (ej. "/collections/"
# sugiere Shopify, "?map=ft" sugiere VTEX), no una confirmación.
FUENTES_INFO = [
    # --- Vinotecas (10) --------------------------------------------------
    {"nombre": "1000 Vinos", "tipo": "vinoteca", "base_url": "https://www.1000vinos.com", "plataformas": ["magento", "tiendanube"]},
    {"nombre": "Espaciovino", "tipo": "vinoteca", "base_url": "https://www.espaciovino.com.ar", "plataformas": ["vtex", "magento"]},
    {"nombre": "Winery", "tipo": "vinoteca", "base_url": "https://www.winery.com.ar", "plataformas": ["tiendanube", "woocommerce"]},
    {"nombre": "Vinoteca BARI", "tipo": "vinoteca", "base_url": "https://www.bari.com.ar", "plataformas": ["tiendanube", "woocommerce"]},
    {"nombre": "TiendaVinos", "tipo": "vinoteca", "base_url": "https://www.tiendavinos.com.ar", "plataformas": ["tiendanube", "woocommerce"]},
    {"nombre": "Casa de Vinos Mendoza", "tipo": "vinoteca", "base_url": "https://casadevinosmendoza.com.ar", "plataformas": ["tiendanube", "woocommerce"]},
    {"nombre": "Vinos x Caja", "tipo": "vinoteca", "base_url": "https://www.vinosxcaja.com.ar", "plataformas": ["tiendanube", "shopify"]},
    {"nombre": "MercadoDeVinos", "tipo": "vinoteca", "base_url": "https://www.mercadodevinos.com.ar", "plataformas": ["tiendanube", "woocommerce"]},
    {"nombre": "La Viteca", "tipo": "vinoteca", "base_url": "https://laviteca.com", "plataformas": ["tiendanube", "shopify"]},
    {"nombre": "Bonvivir", "tipo": "vinoteca", "base_url": "https://bonvivir.com", "plataformas": ["shopify", "tiendanube"]},
    # --- Bodegas: venta directa (10) --------------------------------------
    {"nombre": "Bodegas Bianchi", "tipo": "bodega", "base_url": "https://www.bodegasbianchi.com.ar", "plataformas": ["tiendanube", "woocommerce"]},
    {"nombre": "Cava Colomé", "tipo": "bodega", "base_url": "https://cavacolome.com", "plataformas": ["woocommerce", "shopify"]},
    {"nombre": "Luigi Bosca", "tipo": "bodega", "base_url": "https://shop.luigibosca.com", "plataformas": ["shopify", "tiendanube"]},
    {"nombre": "Bodega Norton", "tipo": "bodega", "base_url": "https://shop.norton.com.ar", "plataformas": ["shopify", "tiendanube"]},
    {"nombre": "Rutini Wines", "tipo": "bodega", "base_url": "https://tienda.rutiniwines.com", "plataformas": ["shopify", "tiendanube"]},
    {"nombre": "Susana Balbo", "tipo": "bodega", "base_url": "https://tienda.susanabalbowines.com.ar", "plataformas": ["shopify", "tiendanube"]},
    {"nombre": "Escorihuela Gascón", "tipo": "bodega", "base_url": "https://tienda.escorihuela.com", "plataformas": ["vtex", "shopify"]},
    {"nombre": "Familia Schroeder", "tipo": "bodega", "base_url": "https://tienda.familiaschroeder.com", "plataformas": ["shopify", "tiendanube"]},
    {"nombre": "Achaval Ferrer", "tipo": "bodega", "base_url": "https://tienda.achaval-ferrer.com", "plataformas": ["shopify", "tiendanube"]},
    {"nombre": "Krontiras Wines", "tipo": "bodega", "base_url": "https://www.krontiraswines.com/tienda-organica", "plataformas": ["woocommerce", "tiendanube"]},
    # --- Importadoras / especialistas en vinos importados (10) -----------
    {"nombre": "Enotek", "tipo": "importador", "base_url": "https://enotek.com.ar", "plataformas": ["tiendanube", "woocommerce"]},
    {"nombre": "Lar de Vinos", "tipo": "importador", "base_url": "https://www.lardevinos.com.ar", "plataformas": ["tiendanube", "woocommerce"]},
    {"nombre": "Armesto Almacén", "tipo": "importador", "base_url": "https://www.armestoalmacen.com.ar", "plataformas": ["tiendanube", "woocommerce"]},
    {"nombre": "Casa Dionisio Vinoteca", "tipo": "importador", "base_url": "https://www.tienda.dionisioonline.com.ar", "plataformas": ["vtex", "tiendanube"]},
    {"nombre": "Rebellion House of Wines", "tipo": "importador", "base_url": "https://www.rebellion.com.ar", "plataformas": ["tiendanube", "shopify"]},
    {"nombre": "Lo de Granado", "tipo": "importador", "base_url": "https://www.lodegranado.com.ar", "plataformas": ["tiendanube", "woocommerce"]},
    {"nombre": "Vinoteca Ligier", "tipo": "importador", "base_url": "https://vinotecaligier.com", "plataformas": ["tiendanube", "woocommerce"]},
    {"nombre": "Vinos Inc", "tipo": "importador", "base_url": "https://vinosinc.com.ar", "plataformas": ["woocommerce", "tiendanube"]},
    {"nombre": "Aldos Vinoteca", "tipo": "importador", "base_url": "https://tienda.aldosvinoteca.com", "plataformas": ["shopify", "tiendanube"]},
    {"nombre": "Grand Cru", "tipo": "importador", "base_url": "https://www.grandcru.com.ar", "plataformas": ["vtex", "tiendanube"]},
]


def _factor_demo(nombre: str) -> float:
    """Factor determinista (mismo nombre -> mismo factor) para que el modo
    demo dé precios distintos pero repetibles por fuente, sin tener que
    tipear 30 números a mano."""
    h = int(hashlib.sha256(nombre.encode()).hexdigest(), 16)
    return 0.85 + (h % 30) / 100  # entre 0.85 y 1.14


FUENTES_REALES = [
    FuenteScraping(
        nombre=info["nombre"],
        tipo=info["tipo"],
        base_url=info["base_url"],
        patrones_busqueda=patrones_para(info["plataformas"]),
        selector_item=SELECTOR_ITEM,
        selector_nombre=SELECTOR_NOMBRE,
        selector_precio=SELECTOR_PRECIO,
        selector_link=SELECTOR_LINK,
    )
    for info in FUENTES_INFO
]

FUENTES_DEMO = [
    FuenteSimulada(f"{info['nombre']} (demo)", info["tipo"], factor=_factor_demo(info["nombre"]))
    for info in FUENTES_INFO
]
