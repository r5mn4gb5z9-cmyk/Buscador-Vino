from abc import ABC, abstractmethod
from typing import List, Optional

from ..models import ResultadoPrecio


class FuenteBase(ABC):
    """Interfaz que debe implementar cualquier fuente de precios
    (vinoteca, bodega, importador, o lo que sea)."""

    nombre: str = "Fuente"
    tipo: str = "otro"  # "vinoteca" | "bodega" | "importador"
    region: str = ""  # provincia/zona, ej. "Mendoza", "Salta" — "" si no se investigó
    # True/False si la propia web declara (o descarta) envío a todo el
    # país; None si no se encontró una declaración clara al investigar.
    envio_nacional: Optional[bool] = None

    @abstractmethod
    def buscar(self, consulta: str) -> List[ResultadoPrecio]:
        """Busca `consulta` en la fuente y devuelve los precios encontrados.

        Nunca debe lanzar una excepción que tumbe la comparación completa:
        errores de red o de parsing se deben resolver devolviendo una
        lista vacía (el llamador igual atrapa excepciones por las dudas).
        """
        raise NotImplementedError
