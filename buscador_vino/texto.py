import unicodedata


def normalizar(s: str) -> str:
    """Minúsculas y sin acentos, para comparar texto de forma tolerante a
    mayúsculas/tildes (ej. "Torrontés" == "torrontes")."""
    s = unicodedata.normalize("NFKD", s.lower())
    return "".join(c for c in s if not unicodedata.combining(c))


# Palabras sin peso propio en una búsqueda de vino (artículos, "vino",
# "bodega"): se ignoran tanto al armar los tokens de relevancia del
# scraping como al adivinar la variedad de uva de una búsqueda.
PALABRAS_VACIAS_VINO = {"de", "del", "la", "el", "los", "las", "y", "vino", "vinos", "bodega"}
