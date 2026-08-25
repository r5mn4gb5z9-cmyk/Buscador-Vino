"""Patrones de búsqueda y selectores CSS comunes a las plataformas de
e-commerce más usadas por vinotecas, bodegas e importadoras en Argentina
(Magento, WooCommerce, Tiendanube, Shopify, VTEX).

No se pudo confirmar en vivo qué plataforma corre cada uno de los 30 sitios
de `config.py` (ver la nota grande en ese archivo), así que en vez de
apostar a un único selector por sitio, cada fuente prueba un par de
patrones de URL de búsqueda típicos de su plataforma más probable, y en
cada intento usa selectores CSS "unión" que cubren las 5 plataformas a la
vez. Si el primer patrón no encuentra nada, se prueba el segundo antes de
darse por vencido.
"""

PATRONES_BUSQUEDA = {
    "magento": "{base}/catalogsearch/result/?q={query}",
    "woocommerce": "{base}/?s={query}&post_type=product",
    "tiendanube": "{base}/?q={query}",
    "shopify": "{base}/search?q={query}&type=product",
    "vtex": "{base}/{query}?map=ft",
}

SELECTOR_ITEM = ", ".join(
    [
        "li.product-item",
        "li.product",
        "div.product-card",
        "div.card-wrapper",
        "li.grid__item",
        "div.js-item-product",
        "li.js-item-product",
        "div.vtex-search-result-3-x-galleryItem",
        "div.vtex-product-summary-2-x-container",
        "article.product-item",
        "div.product",
        "li.item-product",
    ]
)

SELECTOR_NOMBRE = ", ".join(
    [
        "a.product-item-link",
        "h2.woocommerce-loop-product__title",
        "h3.woocommerce-loop-product__title",
        ".card__heading",
        ".product-card__title",
        "a.js-item-name",
        ".item-name",
        ".vtex-product-summary-2-x-productNameContainer",
        "a.full-unstyled-link",
        "h3.product-name",
        ".product-title",
    ]
)

SELECTOR_PRECIO = ", ".join(
    [
        "span.price",
        ".price-item--regular",
        ".price-item",
        ".price__regular",
        ".js-price-display",
        "span.price-actual",
        ".vtex-product-price-1-x-sellingPriceValue",
        ".vtex-store-components-3-x-sellingPriceValue",
        ".precio",
        ".product-price",
    ]
)

SELECTOR_LINK = ", ".join(
    [
        "a.product-item-link",
        "a.woocommerce-LoopProduct-link",
        "a.woocommerce-loop-product__link",
        "a.full-unstyled-link",
        "a.card__heading",
        "a.js-item-name",
        "a",
    ]
)


def patrones_para(plataformas):
    """Devuelve la lista de plantillas de URL (con {base} y {query}) para
    las plataformas indicadas, en orden de prioridad."""
    return [PATRONES_BUSQUEDA[p] for p in plataformas]
