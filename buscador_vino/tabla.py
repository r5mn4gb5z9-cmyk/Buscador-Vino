from typing import List

from .models import ContactoDirecto, ResultadoPrecio


def _formatear_precio_ar(valor: float) -> str:
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def imprimir_mejor_precio(resultados: List[ResultadoPrecio]) -> str:
    """Devuelve un encabezado con dónde comprar más barato.

    Asume que `resultados` ya viene ordenado de menor a mayor precio
    (así lo entrega `comparar_precios`), así que el primero es el más
    barato.
    """
    if not resultados:
        return "No se encontraron resultados."

    mejor = resultados[0]
    precio = _formatear_precio_ar(mejor.precio)
    linea = f"Más barato en {mejor.fuente} ({mejor.tipo_fuente}): $ {precio} {mejor.moneda}"
    if mejor.url:
        linea += f"\n{mejor.url}"
    return linea


def imprimir_tabla(resultados: List[ResultadoPrecio]) -> str:
    """Devuelve una tabla de texto con vino, precio, moneda, fuente, tipo
    y el link directo al producto, ordenada de menor a mayor precio (el
    orden lo define quien arma `resultados`, normalmente
    `comparar_precios`)."""
    if not resultados:
        return "No se encontraron resultados."

    encabezados = ["Vino", "Precio", "Moneda", "Fuente", "Tipo", "Link"]
    filas = [
        [
            r.vino,
            _formatear_precio_ar(r.precio),
            r.moneda,
            r.fuente,
            r.tipo_fuente,
            r.url or "-",
        ]
        for r in resultados
    ]

    anchos = [
        max(len(encabezados[i]), max((len(fila[i]) for fila in filas), default=0))
        for i in range(len(encabezados))
    ]

    def formatear_fila(valores):
        return " | ".join(v.ljust(anchos[i]) for i, v in enumerate(valores))

    separador = "-+-".join("-" * a for a in anchos)
    lineas = [formatear_fila(encabezados), separador]
    lineas.extend(formatear_fila(fila) for fila in filas)
    return "\n".join(lineas)


def imprimir_directorio(bodegas: List[ContactoDirecto]) -> str:
    """Devuelve una tabla de texto con bodegas/vinotecas boutique que no
    tienen tienda online, para mostrarlas igual con su contacto directo."""
    if not bodegas:
        return "No se encontraron bodegas/vinotecas sin tienda online para ese filtro."

    encabezados = ["Nombre", "Tipo", "Región", "Contacto", "Link"]
    filas = [
        [b.nombre, b.tipo, b.region, b.contacto, b.url or "-"]
        for b in bodegas
    ]

    anchos = [
        max(len(encabezados[i]), max((len(fila[i]) for fila in filas), default=0))
        for i in range(len(encabezados))
    ]

    def formatear_fila(valores):
        return " | ".join(v.ljust(anchos[i]) for i, v in enumerate(valores))

    separador = "-+-".join("-" * a for a in anchos)
    lineas = [formatear_fila(encabezados), separador]
    lineas.extend(formatear_fila(fila) for fila in filas)
    return "\n".join(lineas)
