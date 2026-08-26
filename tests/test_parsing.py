from buscador_vino.parsing import normalizar_precio


def test_formato_argentino_con_decimales():
    assert normalizar_precio("$ 15.990,50") == 15990.50


def test_formato_argentino_sin_decimales():
    assert normalizar_precio("$12.500") == 12500.0


def test_formato_con_decimal_punto():
    assert normalizar_precio("USD 25.50") == 25.50


def test_texto_vacio():
    assert normalizar_precio("") is None


def test_sin_digitos():
    assert normalizar_precio("Consultar precio") is None


def test_precios_pegados_sin_separador_toma_el_primero():
    # Bug real visto en producción: precio tachado + oferta pegados sin
    # espacio ni "$" entre medio terminaban mezclándose en un solo número
    # gigante sin sentido (ej. $7.600.050.000 para una botella de vino).
    assert normalizar_precio("7.600050.000") == 7600.0


def test_dos_precios_con_simbolo_pesos_toma_el_primero():
    assert normalizar_precio("$76.000,00$50.700,00") == 76000.0
