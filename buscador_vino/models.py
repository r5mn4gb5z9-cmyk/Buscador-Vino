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


@dataclass
class ContactoDirecto:
    """Una bodega/vinoteca boutique que no tiene tienda online (solo
    WhatsApp, Instagram u otro contacto directo), para listarla igual en
    vez de dejarla afuera del comparador."""

    nombre: str
    tipo: str  # "bodega" | "vinoteca" | "distribuidor"
    region: str
    medio: str  # "whatsapp" | "instagram" | "telefono" | "email" | "facebook"
    contacto: str  # tal cual se muestra: número, @usuario, dirección, etc.
    url: str = ""  # link directo si existe (wa.me/..., instagram.com/..., mailto:)
