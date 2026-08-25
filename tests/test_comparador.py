from buscador_vino.comparador import comparar_precios
from buscador_vino.fuentes.mock import FuenteSimulada
from buscador_vino.tabla import imprimir_tabla


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
