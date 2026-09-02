"""Bodegas y vinotecas boutique que NO tienen tienda online propia (solo
venden por WhatsApp, Instagram u otro contacto directo) y por eso no
pueden participar del scraping de precios. En vez de dejarlas afuera del
comparador, se listan acá para mostrarlas igual, marcadas como "contactar
directo" (ver `ContactoDirecto` en `..models` y la sección correspondiente
en el CLI/web).

Todos los nombres, regiones y contactos salen de búsquedas e inspección de
sitios reales (WebSearch + WebFetch), no están inventados. Reglas que se
siguieron para construir el link de contacto (`url`):

- Si se encontró un número de WhatsApp con el prefijo de país completo
  ("+54 9 ...", o ya en formato wa.me/54...), se arma el link `wa.me/...`.
- Si el número encontrado no traía el código de país o el "9" de celular
  de forma inequívoca, se prefiere linkear a Instagram en su lugar (más
  confiable que adivinar el formato del teléfono) y el teléfono se deja
  solo como texto en `contacto` si hace falta.
- Si solo hay página de Facebook (sin slug de URL confirmado), se deja
  como texto sin `url` para no linkear a algo no verificado.
"""

from typing import List

from ..models import ContactoDirecto

DIRECTORIO_INFO = [
    # --- Córdoba (Colonia Caroya / Traslasierra) ---------------------------
    {"nombre": "Bodega La Caroyense", "tipo": "bodega", "region": "Córdoba", "medio": "whatsapp", "contacto": "+54 9 3525 48-8151", "url": "https://wa.me/5493525488151"},
    {"nombre": "Terra Camiare", "tipo": "bodega", "region": "Córdoba", "medio": "instagram", "contacto": "@terracamiare", "url": "https://instagram.com/terracamiare"},
    {"nombre": "Achala – Bodega Exótica", "tipo": "bodega", "region": "Córdoba", "medio": "instagram", "contacto": "@achala.wine", "url": "https://instagram.com/achala.wine"},
    # --- Entre Ríos ----------------------------------------------------------
    {"nombre": "Las Magnolias – Bodega Boutique", "tipo": "bodega", "region": "Entre Ríos (Gualeguaychú)", "medio": "whatsapp", "contacto": "+54 9 3446 52-7114", "url": "https://wa.me/5493446527114"},
    {"nombre": "Le Garage Vinos", "tipo": "vinoteca", "region": "Entre Ríos (Gualeguaychú)", "medio": "instagram", "contacto": "@legaragevinos", "url": "https://instagram.com/legaragevinos"},
    {"nombre": "Varietal Almacén de Vinos", "tipo": "vinoteca", "region": "Entre Ríos (Paraná)", "medio": "instagram", "contacto": "@varietalalmacendevinos", "url": "https://instagram.com/varietalalmacendevinos"},
    # --- La Pampa ------------------------------------------------------------
    {"nombre": "Bodega Quietud", "tipo": "bodega", "region": "La Pampa (Santa Rosa)", "medio": "telefono", "contacto": "2954-666127", "url": ""},
    {"nombre": "ByB Vinotecas Boutique", "tipo": "vinoteca", "region": "La Pampa (Santa Rosa)", "medio": "instagram", "contacto": "@bybvinotecas", "url": "https://instagram.com/bybvinotecas"},
    # --- Salta (Cafayate / Molinos) -------------------------------------------
    {"nombre": "Bodega Nanni", "tipo": "bodega", "region": "Salta (Cafayate)", "medio": "whatsapp", "contacto": "+54 9 386 863-8465", "url": "https://wa.me/5493868638465"},
    {"nombre": "Domingo Hermanos", "tipo": "bodega", "region": "Salta (Cafayate)", "medio": "whatsapp", "contacto": "+54 9 386 845-2870", "url": "https://wa.me/5493868452870"},
    {"nombre": "Vasija Secreta", "tipo": "bodega", "region": "Salta (Cafayate)", "medio": "instagram", "contacto": "@vasijasecreta", "url": "https://instagram.com/vasijasecreta"},
    {"nombre": "Bodega Tacuil", "tipo": "bodega", "region": "Salta (Molinos)", "medio": "whatsapp", "contacto": "+54 9 387 210-6076", "url": "https://wa.me/5493872106076"},
    {"nombre": "Finca Quara", "tipo": "bodega", "region": "Salta (Cafayate)", "medio": "whatsapp", "contacto": "+54 9 386 863-9030", "url": "https://wa.me/5493868639030"},
    # --- La Rioja --------------------------------------------------------------
    {"nombre": "Bodega Chañarmuyo", "tipo": "bodega", "region": "La Rioja (Valle de Famatina)", "medio": "whatsapp", "contacto": "+54 9 380 427-8010", "url": "https://wa.me/5493804278010"},
    {"nombre": "Valle de la Puerta", "tipo": "bodega", "region": "La Rioja (Chilecito)", "medio": "instagram", "contacto": "@bodegavalledelapuerta", "url": "https://instagram.com/bodegavalledelapuerta"},
    # --- Catamarca ---------------------------------------------------------------
    {"nombre": "Finca Don Diego", "tipo": "bodega", "region": "Catamarca (Fiambalá)", "medio": "instagram", "contacto": "@fincadondiego", "url": "https://instagram.com/fincadondiego"},
    {"nombre": "Cabernet de los Andes (Bodega Tizac)", "tipo": "bodega", "region": "Catamarca (Fiambalá)", "medio": "instagram", "contacto": "@tizacjorgescharf", "url": "https://instagram.com/tizacjorgescharf"},
    {"nombre": "La Vinoteca Selección", "tipo": "vinoteca", "region": "Catamarca (capital)", "medio": "instagram", "contacto": "@la.vinoteca", "url": "https://instagram.com/la.vinoteca"},
    # --- Neuquén -------------------------------------------------------------------
    {"nombre": "Bodega Patritti", "tipo": "bodega", "region": "Neuquén (San Patricio del Chañar)", "medio": "instagram", "contacto": "@bodegapatritti", "url": "https://instagram.com/bodegapatritti"},
    # --- Río Negro / Viedma -----------------------------------------------------------
    {"nombre": "Bodega Chacra", "tipo": "bodega", "region": "Río Negro (Mainqué)", "medio": "facebook", "contacto": "Facebook: Bodega Chacra", "url": ""},
    {"nombre": "Bodega Favretto", "tipo": "bodega", "region": "Río Negro (Villa Regina)", "medio": "telefono", "contacto": "11-6618-5997 (Gustavo Favretto)", "url": ""},
    {"nombre": "Río Tinto Vinoteca", "tipo": "vinoteca", "region": "Río Negro (Viedma)", "medio": "instagram", "contacto": "@riotintovinoteca", "url": "https://instagram.com/riotintovinoteca"},
    {"nombre": "Vinoteca Vinopolitan", "tipo": "vinoteca", "region": "Río Negro (Viedma)", "medio": "telefono", "contacto": "+54 2920 27-1820", "url": ""},
    # --- Buenos Aires: Costa y Sierra de la Ventana ---------------------------------
    {"nombre": "Costa & Pampa (Bodega Trapiche)", "tipo": "bodega", "region": "Buenos Aires (Chapadmalal)", "medio": "email", "contacto": "info@cyptrapiche.com.ar · tel. (54 223) 464-4312", "url": "mailto:info@cyptrapiche.com.ar"},
    {"nombre": "Bodega Saldungaray", "tipo": "bodega", "region": "Buenos Aires (Sierra de la Ventana)", "medio": "instagram", "contacto": "@bodegasaldungaray", "url": "https://instagram.com/bodegasaldungaray"},
    {"nombre": "Bodega MYL Colores", "tipo": "bodega", "region": "Buenos Aires (Coronel Pringles)", "medio": "instagram", "contacto": "@mylcolores", "url": "https://instagram.com/mylcolores"},
    # --- Mendoza (boutique sin tienda online) -----------------------------------------
    {"nombre": "Bodega Vistandes", "tipo": "bodega", "region": "Mendoza (Maipú)", "medio": "whatsapp", "contacto": "+54 9 261 655-7466", "url": "https://wa.me/5492616557466"},
    {"nombre": "Bodega Riglos", "tipo": "bodega", "region": "Mendoza (Tupungato)", "medio": "instagram", "contacto": "@huarpe_riglos", "url": "https://instagram.com/huarpe_riglos"},
    {"nombre": "Casarena Bodega y Viñedos", "tipo": "bodega", "region": "Mendoza (Luján de Cuyo)", "medio": "instagram", "contacto": "@casarenabodega", "url": "https://instagram.com/casarenabodega"},
    {"nombre": "Alma Austral", "tipo": "bodega", "region": "Mendoza (Chacras de Coria)", "medio": "instagram", "contacto": "@almaaustral", "url": "https://instagram.com/almaaustral"},
    # --- San Juan (boutique sin tienda online) ----------------------------------------
    {"nombre": "Casa Montes", "tipo": "bodega", "region": "San Juan (Caucete)", "medio": "instagram", "contacto": "@casamontesok", "url": "https://instagram.com/casamontesok"},
]

BODEGAS_SIN_TIENDA: List[ContactoDirecto] = [
    ContactoDirecto(
        nombre=info["nombre"],
        tipo=info["tipo"],
        region=info["region"],
        medio=info["medio"],
        contacto=info["contacto"],
        url=info["url"],
    )
    for info in DIRECTORIO_INFO
]
