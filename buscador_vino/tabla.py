from typing import List

from .models import ResultadoPrecio


def _formatear_precio_ar(valor: float) -> str:
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def imprimir_tabla(resultados: List[ResultadoPrecio]) -> str:
    """Devuelve una tabla de texto con vino, precio, moneda, fuente y tipo."""
    if not resultados:
        return "No se encontraron resultados."

    encabezados = ["Vino", "Precio", "Moneda", "Fuente", "Tipo"]
    filas = [
        [
            r.vino,
            _formatear_precio_ar(r.precio),
            r.moneda,
            r.fuente,
            r.tipo_fuente,
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
