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
    # Confirmado en vivo contra elmercadodebebidas.com.ar (Odoo 17): el
    # buscador de catálogo usa este patrón y devuelve resultados server-side.
    "odoo": "{base}/shop?search={query}",
    # Confirmado en vivo contra jcpsommelier.com.ar: plataforma de e-commerce
    # sin identificar (clases "block-products-feed__*", no es ninguna de
    # las 6 de arriba), pero con este mismo patrón de búsqueda por query.
    "search_generico": "{base}/search?q={query}",
    # jcpsommelier.com.ar tiene un buscador propio, pero devuelve los
    # resultados por JavaScript del lado del cliente (el HTML estático no
    # trae productos). En vez de descartar la fuente entera, se usa la
    # portada como catálogo — siempre trae los mismos productos
    # destacados, así que el filtro de relevancia igual hace su trabajo.
    "vitrina_home": "{base}/",
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
        "div.oe_product",  # Odoo
        "div.block-products-feed__product",  # plataforma de JCP Sommelier
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
        ".js-item-name",  # algunos temas de Tiendanube lo ponen en un span/div, no un <a>
        ".item-name",
        ".vtex-product-summary-2-x-productNameContainer",
        "a.full-unstyled-link",
        "h3.product-name",
        ".product-title",
        ".o_wsale_products_item_title",  # Odoo
        ".block-products-feed__product-name",  # plataforma de JCP Sommelier
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
        ".oe_currency_value",  # Odoo
        ".block-products-feed__product-price",  # plataforma de JCP Sommelier
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
        "a.oe_product_image_link",  # Odoo
        "a.block-products-feed__product-link",  # plataforma de JCP Sommelier
        "a",
    ]
)


def patrones_para(plataformas):
    """Devuelve la lista de plantillas de URL (con {base} y {query}) para
    las plataformas indicadas, en orden de prioridad."""
    return [PATRONES_BUSQUEDA[p] for p in plataformas]
