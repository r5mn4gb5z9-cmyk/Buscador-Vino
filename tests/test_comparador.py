import time

from buscador_vino.comparador import (
    agrupar_mas_barato_por_vino,
    buscar_favoritos,
    comparar_precios,
    elegir_similares,
)
from buscador_vino.fuentes.mock import FuenteSimulada
from buscador_vino.models import ResultadoPrecio
from buscador_vino.tabla import imprimir_favoritos, imprimir_tabla
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


def test_comparar_precios_no_espera_a_una_fuente_colgada():
    # Bug real: `with ThreadPoolExecutor(...) as pool` bloqueaba al salir
    # hasta que TODOS los hilos terminaran, aunque as_completed() ya
    # hubiera dejado de esperar por timeout_total. Una sola fuente con una
    # conexión colgada (más lenta que su propio timeout HTTP, ej. datos
    # llegando de a poquito sin cortarse nunca) hacía que timeout_total no
    # sirviera de nada y la búsqueda entera se congelara.
    class FuenteColgada(FuenteSimulada):
        def buscar(self, consulta):
            time.sleep(3)
            return super().buscar(consulta)

    fuentes = [FuenteSimulada("OK", "vinoteca"), FuenteColgada("Colgada", "vinoteca")]

    inicio = time.time()
    resultados = comparar_precios("Malbec", fuentes, timeout_total=0.5)
    transcurrido = time.time() - inicio

    assert transcurrido < 2, "comparar_precios no debería esperar a una fuente más lenta que el timeout"
    assert len(resultados) == 1
    assert resultados[0].fuente == "OK"


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


def test_detectar_variedad_sin_ninguna_palabra_candidata_devuelve_none():
    # "vino" y "reserva" se descartan (palabra vacía y descriptor de
    # línea), "2020" se descarta por ser un año: no queda ninguna
    # candidata razonable a variedad.
    assert detectar_variedad("Vino Reserva 2020") is None


def test_detectar_variedad_funciona_para_cepas_fuera_de_la_lista_conocida():
    # El pedido explícito era que esto funcione para CUALQUIER cepa que
    # aparezca en el nombre, no solo las de la lista fija (_VARIEDADES).
    # "Carmenere" no está en esa lista a propósito, para probar el
    # fallback: se descarta "bodega" (palabra vacía) y queda "carmenere"
    # como última palabra candidata.
    assert detectar_variedad("Bodega Chacra Carmenere") == "carmenere"


def test_detectar_variedad_ignora_anio_y_descriptores_de_linea():
    # "trapiche" y "torrontes" son candidatas, pero "reserva" y "2022" se
    # descartan — así que el resultado tiene que ser la variedad real
    # ("torrontes"), no el descriptor de línea que viene después.
    assert detectar_variedad("Trapiche Torrontés Reserva 2022") == "torrontes"


def test_detectar_variedad_ignora_formato_de_botella():
    # "750ml" no debería poder colarse como "variedad" solo por ser la
    # última palabra: es el tamaño de la botella, no la cepa. Se usa
    # "Carmenere" (fuera de la lista fija) para que la prueba pase por el
    # fallback en vez de resolverse ya en el primer nivel.
    assert detectar_variedad("Bodega Chacra Carmenere 750ml") == "carmenere"


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


def test_fuente_simulada_propaga_envio_nacional_al_resultado():
    f = FuenteSimulada("Bodega Test", "bodega", envio_nacional=True)
    resultados = f.buscar("Malbec")
    assert resultados[0].envio_nacional is True


def test_imprimir_tabla_muestra_columna_envio():
    resultados = comparar_precios("Malbec", [FuenteSimulada("Vinoteca A", "vinoteca")])
    tabla = imprimir_tabla(resultados)
    assert "Envío" in tabla
    assert "?" in tabla  # FuenteSimulada sin envio_nacional -> desconocido


def test_buscar_favoritos_devuelve_una_entrada_por_nombre_en_orden():
    fuentes = [FuenteSimulada("Vinoteca A", "vinoteca", factor=1.0)]
    resultados = buscar_favoritos(["Rutini Malbec", "Bonarda Reserva"], fuentes)

    assert [nombre for nombre, _ in resultados] == ["Rutini Malbec", "Bonarda Reserva"]
    assert all(res for _, res in resultados)


class _FuenteMultiVino(FuenteSimulada):
    """Simula una fuente que, para una bodega, devuelve varios vinos
    distintos (como pasaría de verdad al buscar el nombre de una bodega
    como texto libre)."""

    def buscar(self, consulta):
        return [
            ResultadoPrecio(
                vino="Chacra Pinot Noir",
                precio=30_000,
                moneda="ARS",
                fuente=self.nombre,
                tipo_fuente=self.tipo,
            ),
            ResultadoPrecio(
                vino="Chacra Sauvignon Blanc",
                precio=18_000,
                moneda="ARS",
                fuente=self.nombre,
                tipo_fuente=self.tipo,
            ),
        ]


def test_buscar_favoritos_de_una_bodega_agrupa_todos_sus_vinos():
    fuentes = [_FuenteMultiVino("Vinoteca A", "vinoteca")]
    resultados = buscar_favoritos(["Bodega Chacra"], fuentes)

    nombre, vinos = resultados[0]
    assert nombre == "Bodega Chacra"
    assert {v.vino for v in vinos} == {"Chacra Pinot Noir", "Chacra Sauvignon Blanc"}


def test_agrupar_mas_barato_por_vino_se_queda_con_el_mas_barato_de_cada_grupo():
    resultados = [
        _resultado("Chacra Pinot Noir", 30_000, fuente="Vinoteca A"),
        _resultado("Chacra Pinot Noir", 25_000, fuente="Vinoteca B"),  # mismo vino, más barato
        _resultado("Chacra Sauvignon Blanc", 18_000, fuente="Vinoteca A"),
    ]

    agrupados = agrupar_mas_barato_por_vino(resultados)

    assert len(agrupados) == 2
    pinot = next(r for r in agrupados if r.vino == "Chacra Pinot Noir")
    assert pinot.precio == 25_000
    assert pinot.fuente == "Vinoteca B"


def test_agrupar_mas_barato_por_vino_ordena_los_grupos_por_precio():
    resultados = [_resultado("Vino Caro", 50_000), _resultado("Vino Barato", 10_000)]
    agrupados = agrupar_mas_barato_por_vino(resultados)
    assert [r.vino for r in agrupados] == ["Vino Barato", "Vino Caro"]


def test_agrupar_mas_barato_por_vino_ignora_tildes_y_mayusculas():
    resultados = [_resultado("Torrontés", 12_000), _resultado("torrontes", 9_000)]
    agrupados = agrupar_mas_barato_por_vino(resultados)
    assert len(agrupados) == 1
    assert agrupados[0].precio == 9_000


def test_imprimir_favoritos_sin_ninguno_guardado():
    assert "favoritos" in imprimir_favoritos([]).lower()


def test_imprimir_favoritos_marca_los_que_no_tienen_resultados():
    tabla = imprimir_favoritos([("Vino Fantasma", [])])
    assert "Vino Fantasma" in tabla
    assert "sin resultados" in tabla


def test_imprimir_favoritos_muestra_todos_los_vinos_recibidos():
    # imprimir_favoritos no agrupa por su cuenta: espera recibir la lista
    # ya agrupada (agrupar_mas_barato_por_vino la arma antes de llegar
    # acá), así que si le pasan varios vinos distintos los muestra todos.
    resultados = [_resultado("Chacra Pinot Noir", 30_000), _resultado("Chacra Sauvignon Blanc", 18_000)]
    tabla = imprimir_favoritos([("Bodega Chacra", resultados)])
    assert "30.000" in tabla
    assert "18.000" in tabla
    assert "Chacra Pinot Noir" in tabla
    assert "Chacra Sauvignon Blanc" in tabla
