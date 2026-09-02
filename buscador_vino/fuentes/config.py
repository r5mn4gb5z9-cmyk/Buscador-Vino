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

# Ampliación de cobertura a bodegas boutique/chicas y vinotecas regionales
# fuera de las grandes marcas de arriba, investigadas y verificadas en vivo
# (WebSearch + WebFetch + requests reales, no son dominios inventados) para
# cubrir Mendoza, San Juan, Salta, Catamarca, La Rioja, Neuquén, Río Negro,
# Córdoba, La Pampa y la "Costa y Sierra de la Ventana" bonaerense (Chapadmalal,
# Balcarce, Sierra de la Ventana, Médanos, Coronel Pringles). No se encontró
# ninguna bodega/vinoteca con e-commerce propio verificable en Entre Ríos,
# Catamarca capital, Viedma ni Chapadmalal — esas regiones solo aportaron
# resultados para BODEGAS_SIN_TIENDA (ver fuentes/directorio.py).
#
# Cada una tiene "region" para poder filtrar (--region en el CLI, selector en
# la web). Se probaron todas contra la red real antes de sumarlas: algunas
# devuelven vacío para consultas genéricas como "malbec" porque son bodegas
# de varietales fríos (Pinot Noir, Sauvignon Blanc, Chardonnay) típicos de
# Patagonia/costa bonaerense, no porque el scraping esté roto — correr
# scripts/verificar_fuentes.py con una consulta acorde (ej. "pinot") lo
# confirma. Xumek (San Juan) tiene el certificado SSL vencido del lado de
# ellos: va a arrancar a andar solo cuando lo renueven.
FUENTES_INFO_REGIONALES = [
    # --- Mendoza (bodegas boutique + 1 vinoteca de autor) -----------------
    {"nombre": "Alpasión", "tipo": "bodega", "region": "Mendoza", "base_url": "https://shop.alpasion.com", "plataformas": ["woocommerce", "tiendanube"]},
    {"nombre": "Familia Cassone", "tipo": "bodega", "region": "Mendoza", "base_url": "https://familiacassone.com.ar", "plataformas": ["tiendanube", "woocommerce"]},
    {"nombre": "Altos Las Hormigas", "tipo": "bodega", "region": "Mendoza", "base_url": "https://www.tiendaaltoslashormigas.com.ar", "plataformas": ["tiendanube", "woocommerce"]},
    {"nombre": "Clos de Chacras", "tipo": "bodega", "region": "Mendoza", "base_url": "https://closdechacras.mitiendanube.com", "plataformas": ["tiendanube"]},
    {"nombre": "Bodega Piedra Negra", "tipo": "bodega", "region": "Mendoza", "base_url": "https://tienda.bodegapiedranegra.com", "plataformas": ["shopify"]},
    {"nombre": "Durigutti Family Winemakers", "tipo": "bodega", "region": "Mendoza", "base_url": "https://tienda.durigutti.com", "plataformas": ["woocommerce"]},
    {"nombre": "DonVino", "tipo": "vinoteca", "region": "Mendoza", "base_url": "https://donvino.com.ar", "plataformas": ["woocommerce"]},
    # --- San Juan (bodegas boutique) --------------------------------------
    {"nombre": "Bodega Merced del Estero", "tipo": "bodega", "region": "San Juan", "base_url": "https://merceddelestero.com.ar", "plataformas": ["tiendanube", "woocommerce"]},
    {"nombre": "Fabril Alto Verde", "tipo": "bodega", "region": "San Juan", "base_url": "https://www.fabrilaltoverde.com.ar", "plataformas": ["woocommerce"]},
    {"nombre": "Xumek", "tipo": "bodega", "region": "San Juan", "base_url": "https://xumek.com.ar", "plataformas": ["woocommerce"]},
    {"nombre": "Bodega Putruele", "tipo": "bodega", "region": "San Juan", "base_url": "https://bodegaputruele.com", "plataformas": ["woocommerce"]},
    # --- Salta (bodegas boutique de altura, Cafayate) ----------------------
    {"nombre": "Bodega El Tránsito", "tipo": "bodega", "region": "Salta", "base_url": "https://shop.bodegaeltransito.com", "plataformas": ["tiendanube"]},
    {"nombre": "Casa Tukma", "tipo": "bodega", "region": "Salta", "base_url": "https://casatukma.com", "plataformas": ["shopify"]},
    # --- Catamarca (bodega boutique, Tinogasta) ----------------------------
    {"nombre": "Bodega Veralma", "tipo": "bodega", "region": "Catamarca", "base_url": "https://www.tiendaveralma.com.ar", "plataformas": ["tiendanube"]},
    # --- Neuquén (bodega boutique, San Patricio del Chañar) ----------------
    {"nombre": "Bodega Malma", "tipo": "bodega", "region": "Neuquén", "base_url": "https://shop.bodegamalma.com.ar", "plataformas": ["shopify"]},
    # --- Río Negro (bodegas boutique/regionales, Alto Valle) ---------------
    {"nombre": "Bodega Humberto Canale", "tipo": "bodega", "region": "Río Negro", "base_url": "https://shop.bodegahcanale.com", "plataformas": ["tiendanube"]},
    {"nombre": "Bodega y Viñedos Agrestis", "tipo": "bodega", "region": "Río Negro", "base_url": "https://www.bodegaagrestis.com.ar", "plataformas": ["tiendanube"]},
    # --- Córdoba (bodega boutique, Traslasierra) ----------------------------
    {"nombre": "Comarca La Matilde", "tipo": "bodega", "region": "Córdoba", "base_url": "https://www.comarcalamatilde.com.ar", "plataformas": ["woocommerce"]},
    # --- La Pampa (bodega boutique, 25 de Mayo) -----------------------------
    {"nombre": "Bodega del Desierto", "tipo": "bodega", "region": "La Pampa", "base_url": "https://store.bodegadeldesierto.com.ar", "plataformas": ["tiendanube"]},
    # --- Buenos Aires: Costa y Sierra de la Ventana -------------------------
    {"nombre": "Bodegas y Viñedos Balcarce", "tipo": "bodega", "region": "Buenos Aires (Balcarce)", "base_url": "https://bodegasbalcarce.com.ar", "plataformas": ["woocommerce"]},
    {"nombre": "Bodega Puerta del Abra", "tipo": "bodega", "region": "Buenos Aires (Balcarce)", "base_url": "https://tienda.puertadelabra.com.ar", "plataformas": ["tiendanube"]},
    {"nombre": "Bodega Al Este (Terrasabbia)", "tipo": "bodega", "region": "Buenos Aires (Médanos)", "base_url": "https://terrasabbia.mitiendanube.com", "plataformas": ["tiendanube"]},
    # --- Buenos Aires provincia (vinotecas/distribuidores fuera de CABA/GBA) -
    {"nombre": "El Mercado de Bebidas", "tipo": "vinoteca", "region": "Buenos Aires (Mar del Plata)", "base_url": "https://www.elmercadodebebidas.com.ar", "plataformas": ["odoo"]},
    {"nombre": "Musa Vinos de Autor", "tipo": "vinoteca", "region": "Buenos Aires (Bahía Blanca)", "base_url": "https://musavinos2.mitiendanube.com", "plataformas": ["tiendanube"]},
    {"nombre": "Aromas del Tonel", "tipo": "vinoteca", "region": "Buenos Aires (Bahía Blanca)", "base_url": "https://aromasdeltonel.mitiendanube.com", "plataformas": ["tiendanube"]},
]

FUENTES_INFO = FUENTES_INFO + FUENTES_INFO_REGIONALES


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
        region=info.get("region", ""),
    )
    for info in FUENTES_INFO
]

FUENTES_DEMO = [
    FuenteSimulada(
        f"{info['nombre']} (demo)",
        info["tipo"],
        factor=_factor_demo(info["nombre"]),
        region=info.get("region", ""),
    )
    for info in FUENTES_INFO
]
