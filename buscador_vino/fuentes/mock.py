import hashlib
from typing import List

from ..models import ResultadoPrecio
from .base import FuenteBase


class FuenteSimulada(FuenteBase):
    """Fuente de demostración: genera un precio simulado pero determinista
    (mismo vino -> mismo precio siempre) a partir de un hash del nombre.

    Sirve para probar toda la tubería (búsqueda en paralelo, tabla
    comparativa, export a CSV) sin depender de la conexión a internet ni
    de la estructura HTML real de cada sitio.
    """

    def __init__(self, nombre: str, tipo: str, factor: float = 1.0):
        self.nombre = nombre
        self.tipo = tipo
        self.factor = factor

    def buscar(self, consulta: str) -> List[ResultadoPrecio]:
        base = int(hashlib.sha256(consulta.strip().lower().encode()).hexdigest(), 16)
        precio_base = 5000 + (base % 40000)
        precio = round(precio_base * self.factor, 2)
        return [
            ResultadoPrecio(
                vino=consulta.strip().title(),
                precio=precio,
                moneda="ARS",
                fuente=self.nombre,
                tipo_fuente=self.tipo,
                url="https://ejemplo.local/demo",
            )
        ]
