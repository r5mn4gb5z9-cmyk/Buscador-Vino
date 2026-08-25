from dataclasses import dataclass


@dataclass
class ResultadoPrecio:
    """Un precio encontrado para un vino en una fuente puntual."""

    vino: str
    precio: float
    moneda: str
    fuente: str
    tipo_fuente: str  # "vinoteca" | "bodega" | "importador"
    url: str = ""
