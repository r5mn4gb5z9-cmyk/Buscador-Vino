"""Definición de las fuentes de precios a comparar.

FUENTES_REALES apunta a sitios reales de Argentina: dos vinotecas online,
una bodega y un importador. Los selectores CSS son la mejor aproximación
posible a partir de las plataformas de e-commerce que suelen usar estos
sitios (Magento / WooCommerce / Shopify), pero **no fueron verificados
contra el HTML en vivo**: esta sesión de desarrollo corre en un entorno
con salida de red restringida (proxy) que bloquea el acceso a estos
dominios, así que no se pudo confirmar la estructura real de cada página.

Si al correr el programa una fuente no devuelve resultados, lo más
probable es que haya que ajustar `selector_item` / `selector_nombre` /
`selector_precio` de esa fuente inspeccionando la página en el navegador
(F12 -> "Inspeccionar" sobre un resultado de búsqueda).

FUENTES_DEMO no depende de internet: sirve para probar la comparación y
la tabla de salida de punta a punta ahora mismo (`--demo`).
"""

from .mock import FuenteSimulada
from .scraping import FuenteScraping

FUENTES_REALES = [
    # --- Vinotecas -----------------------------------------------------
    FuenteScraping(
        nombre="1000 Vinos",
        tipo="vinoteca",
        url_busqueda="https://www.1000vinos.com/catalogsearch/result/?q={query}",
        base_url="https://www.1000vinos.com",
        selector_item="li.product-item",
        selector_nombre="a.product-item-link",
        selector_precio="span.price",
    ),
    FuenteScraping(
        nombre="La Vinoteca",
        tipo="vinoteca",
        url_busqueda="https://www.lavinoteca.com.ar/catalogsearch/result/?q={query}",
        base_url="https://www.lavinoteca.com.ar",
        selector_item="li.product-item",
        selector_nombre="a.product-item-link",
        selector_precio="span.price",
    ),
    # --- Bodega ----------------------------------------------------------
    FuenteScraping(
        nombre="Bodega Norton",
        tipo="bodega",
        url_busqueda="https://www.bodeganorton.com/tienda/?s={query}&post_type=product",
        base_url="https://www.bodeganorton.com",
        selector_item="li.product",
        selector_nombre="h2.woocommerce-loop-product__title",
        selector_precio="span.price",
        selector_link="a.woocommerce-LoopProduct-link",
    ),
    FuenteScraping(
        nombre="Familia Zuccardi",
        tipo="bodega",
        url_busqueda="https://www.familiazuccardi.com/search?q={query}&type=product",
        base_url="https://www.familiazuccardi.com",
        selector_item=".product-card, .card-wrapper",
        selector_nombre=".card__heading, .product-card__title",
        selector_precio=".price-item--regular, .price-item",
    ),
    # --- Importador ------------------------------------------------------
    FuenteScraping(
        nombre="Otto Wein (importador)",
        tipo="importador",
        url_busqueda="https://www.ottowein.com.ar/?s={query}&post_type=product",
        base_url="https://www.ottowein.com.ar",
        selector_item="li.product",
        selector_nombre="h2.woocommerce-loop-product__title",
        selector_precio="span.price",
        selector_link="a.woocommerce-LoopProduct-link",
    ),
]

FUENTES_DEMO = [
    FuenteSimulada("1000 Vinos (demo)", "vinoteca", factor=1.00),
    FuenteSimulada("La Vinoteca (demo)", "vinoteca", factor=1.08),
    FuenteSimulada("Bodega Norton (demo)", "bodega", factor=0.92),
    FuenteSimulada("Familia Zuccardi (demo)", "bodega", factor=0.97),
    FuenteSimulada("Otto Wein (demo, importador)", "importador", factor=1.15),
]
