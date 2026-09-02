import unicodedata


def normalizar(s: str) -> str:
    """Minúsculas y sin acentos, para comparar texto de forma tolerante a
    mayúsculas/tildes (ej. "Torrontés" == "torrontes")."""
    s = unicodedata.normalize("NFKD", s.lower())
    return "".join(c for c in s if not unicodedata.combining(c))
