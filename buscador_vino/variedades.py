"""Detección de la variedad/varietal de uva mencionada en una búsqueda,
para poder armar una sección "también te puede gustar" a partir de
nuestras propias fuentes (ver la nota grande en `comparador.py` sobre por
qué no se usa Vivino para esto).

La detección tiene dos niveles:

1. Una lista de variedades/frases conocidas (`_VARIEDADES`), para
   reconocer con precisión los casos más comunes y devolver un nombre
   "lindo" (ej. "cabernet sauvignon" completo en vez de cortarlo en
   "cabernet"). Se prueba primero.
2. Si nada de la lista matchea, no nos rendimos: en vez de depender
   solo de una lista fija que nunca puede tener TODAS las cepas del
   mundo, se adivina la variedad a partir del nombre buscado — se
   descartan el año, palabras vacías ("bodega", "vino", etc.) y
   palabras de línea/calidad típicas ("reserva", "gran", "premium", ...)
   y se toma la última palabra que queda. En un nombre de vino
   argentino típico ("Bodega X Variedad [Año/Línea]") eso suele ser
   justo la variedad, así que esto funciona igual de bien para Malbec
   que para Carmenere, Torrontés, o cualquier cepa que no esté en la
   lista de arriba.
"""

import re
from typing import List, Optional

from .texto import PALABRAS_VACIAS_VINO, normalizar

# Varietales y estilos más comunes en las vinotecas/bodegas argentinas.
# Las frases de dos palabras van primero para que "cabernet sauvignon" se
# reconozca entero y no se corte en "cabernet".
_VARIEDADES: List[str] = [
    "cabernet sauvignon",
    "cabernet franc",
    "sauvignon blanc",
    "pinot noir",
    "pinot grigio",
    "chenin blanc",
    "malbec",
    "bonarda",
    "syrah",
    "shiraz",
    "merlot",
    "torrontes",
    "chardonnay",
    "tempranillo",
    "cabernet",
    "tannat",
    "viognier",
    "sangiovese",
    "semillon",
    "riesling",
    "espumante",
]

# Palabras que suelen aparecer junto a la variedad en el nombre de un
# vino sin ser la variedad en sí (línea, calidad, tipo de guarda, color,
# formato/envase). A diferencia de `_VARIEDADES`, esta lista es chica y
# estable: no hace falta agregar una entrada nueva cada vez que aparece
# una cepa que no conocíamos, porque el objetivo no es reconocer
# variedades sino descartar lo que claramente NO es una.
_NO_ES_VARIEDAD = {
    "reserva", "reserve", "gran", "grand", "crianza", "roble", "clasico",
    "joven", "seleccion", "selection", "single", "vineyard", "estate",
    "blend", "corte", "tinto", "blanco", "rosado", "rose", "dulce",
    "seco", "organico", "organic", "biodinamico", "premium", "edicion",
    "limitada", "cosecha", "especial", "viejo", "old", "vines", "barrel",
    "aged", "winemaker", "ml", "cc", "lt", "litro", "magnum", "caja",
    "estuche", "pack", "botella", "bottle", "importado", "nacional",
}

_ANIO_O_FORMATO = re.compile(r"^\d+(ml|cc|lt|l)?$")  # "2022", "750ml", "6" (de "x6")


def detectar_variedad(consulta: str) -> Optional[str]:
    """Devuelve la variedad/varietal más específica mencionada en
    `consulta`, o `None` si no encuentra ninguna candidata razonable."""
    texto = normalizar(consulta)

    for variedad in _VARIEDADES:
        if variedad in texto:
            return variedad

    candidatos = [
        t
        for t in texto.split()
        if len(t) >= 4 and t not in PALABRAS_VACIAS_VINO and t not in _NO_ES_VARIEDAD
        and not _ANIO_O_FORMATO.match(t)
    ]
    return candidatos[-1] if candidatos else None
