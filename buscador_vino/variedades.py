"""Detección de la variedad/varietal de uva mencionada en una búsqueda,
para poder armar una sección "también te puede gustar" a partir de
nuestras propias fuentes (ver la nota grande en `comparador.py` sobre por
qué no se usa Vivino para esto)."""

from typing import List, Optional

from .texto import normalizar

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


def detectar_variedad(consulta: str) -> Optional[str]:
    """Devuelve la variedad/varietal más específica mencionada en
    `consulta` (probando frases de dos palabras antes que de una), o
    `None` si no reconoce ninguna. Sin variedad no hay una forma
    confiable de armar sugerencias "similares"."""
    texto = normalizar(consulta)
    for variedad in _VARIEDADES:
        if variedad in texto:
            return variedad
    return None
