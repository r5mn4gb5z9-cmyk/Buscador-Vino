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
