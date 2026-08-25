import re
from typing import Optional


def normalizar_precio(texto: str) -> Optional[float]:
    """Convierte un texto de precio (con $, espacios, separadores AR/US) a float.

    Ejemplos: "$ 15.990,00" -> 15990.0 | "USD 25.50" -> 25.5 | "$12.500" -> 12500.0
    """
    if not texto:
        return None

    limpio = re.sub(r"[^\d.,]", "", texto).strip(".,")
    if not limpio:
        return None

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
