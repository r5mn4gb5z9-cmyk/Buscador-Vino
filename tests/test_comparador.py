from buscador_vino.comparador import comparar_precios, elegir_similares
from buscador_vino.fuentes.mock import FuenteSimulada
from buscador_vino.models import ResultadoPrecio
from buscador_vino.tabla import imprimir_tabla
from buscador_vino.variedades import detectar_variedad


def test_comparar_precios_ordena_y_agrega_todas_las_fuentes():
    fuentes = [
        FuenteSimulada("Vinoteca A", "vinoteca", factor=1.0),
        FuenteSimulada("Vinoteca B", "vinoteca", factor=0.5),
        FuenteSimulada("Bodega X", "bodega", factor=2.0),
    ]
    resultados = comparar_precios("Rutini Malbec", fuentes)

    assert len(resultados) == 3
    assert [r.fuente for r in resultados] == ["Vinoteca B", "Vinoteca A", "Bodega X"]
    assert resultados[0].precio <= resultados[1].precio <= resultados[2].precio


def test_fuente_que_explota_no_rompe_la_comparacion():
    class FuenteRota(FuenteSimulada):
        def buscar(self, consulta):
            raise RuntimeError("sitio caído")

    fuentes = [FuenteRota("Rota", "vinoteca"), FuenteSimulada("OK", "vinoteca")]
    resultados = comparar_precios("Malbec", fuentes)

    assert len(resultados) == 1
    assert resultados[0].fuente == "OK"


def test_imprimir_tabla_sin_resultados():
    assert imprimir_tabla([]) == "No se encontraron resultados."


def test_imprimir_tabla_incluye_columnas_clave():
    resultados = comparar_precios("Malbec", [FuenteSimulada("Vinoteca A", "vinoteca")])
    tabla = imprimir_tabla(resultados)
    assert "Vino" in tabla and "Precio" in tabla and "Fuente" in tabla
    assert "Vinoteca A" in tabla


def _resultado(vino, precio, fuente="F"):
    return ResultadoPrecio(vino=vino, precio=precio, moneda="ARS", fuente=fuente, tipo_fuente="vinoteca")


def test_detectar_variedad_reconoce_frase_de_dos_palabras():
    assert detectar_variedad("Rutini Cabernet Sauvignon 2019") == "cabernet sauvignon"


def test_detectar_variedad_no_corta_la_frase_por_la_palabra_suelta():
    # "cabernet" solo aparece en la lista después de "cabernet sauvignon" y
    # "cabernet franc": si el detector probara las frases en el orden
    # equivocado, devolvería "cabernet" en vez de la variedad completa.
    assert detectar_variedad("Cabernet Franc Reserva") == "cabernet franc"


def test_detectar_variedad_sin_match_devuelve_none():
    assert detectar_variedad("Champagne Rosado Importado") is None


def test_elegir_similares_excluye_los_ya_encontrados_y_ordena_por_precio():
    originales = [_resultado("Rutini Malbec", 10_000)]
    pool = [
        _resultado("Rutini Malbec", 10_000),  # ya está en originales, se descarta
        _resultado("Trapiche Malbec", 15_000),
        _resultado("Zuccardi Malbec", 9_000),
        _resultado("Luigi Bosca Malbec", 50_000),  # muy lejos en precio
    ]

    similares = elegir_similares(originales, pool, max_resultados=2)

    assert [r.vino for r in similares] == ["Zuccardi Malbec", "Trapiche Malbec"]


def test_elegir_similares_sin_pool_devuelve_vacio():
    originales = [_resultado("Rutini Malbec", 10_000)]
    assert elegir_similares(originales, []) == []
