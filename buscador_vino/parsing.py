import re
from typing import Optional

# Antes esto limpiaba TODO el texto del elemento de precio y lo trataba como
# un solo número. En sitios reales el elemento de precio a veces trae varios
# precios pegados sin espacio (precio tachado + oferta, ej.
# "$76.000,00$50.700,00"), y esa limpieza global los mezclaba en un solo
# número gigante sin sentido (se vio en producción: $7.600.050.000 para una
# botella de vino). Ahora se busca el PRIMER número con pinta de precio y se
# ignora el resto.
_PATRON_PRECIO = re.compile(r"\d{1,3}(?:[.,]\d{3})+(?:[.,]\d{1,2})?|\d+(?:[.,]\d{1,2})?")


def normalizar_precio(texto: str) -> Optional[float]:
    """Convierte un texto de precio (con $, espacios, separadores AR/US) a
    float, tomando el primer número con forma de precio que aparece.

    Ejemplos: "$ 15.990,00" -> 15990.0 | "USD 25.50" -> 25.5 | "$12.500" -> 12500.0
    "$76.000,00$50.700,00" -> 76000.0 (toma el primero, ignora el resto)
    """
    if not texto:
        return None

    match = _PATRON_PRECIO.search(texto)
    if not match:
        return None

    limpio = match.group(0)
    tiene_coma = "," in limpio
    tiene_punto = "." in limpio

    if tiene_coma:
        # Formato AR: punto = miles, coma = decimales
        limpio = limpio.replace(".", "").replace(",", ".")
    elif tiene_punto:
        entero, _, decimales = limpio.rpartition(".")
        if len(decimales) == 3:
            # "15.990" -> son miles, no decimales
            limpio = limpio.replace(".", "")
        # si no, se asume que el punto ya es decimal ("25.50")

    try:
        return round(float(limpio), 2)
    except ValueError:
        return None
