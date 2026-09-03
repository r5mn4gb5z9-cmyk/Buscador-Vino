from bs4 import BeautifulSoup

from buscador_vino.fuentes.scraping import _esta_sin_stock, _texto_precio_vigente
from buscador_vino.parsing import normalizar_precio


def test_esta_sin_stock_detecta_agotado():
    assert _esta_sin_stock("Rutini Malbec $15.000 Agotado")
    assert _esta_sin_stock("Sin stock")
    assert _esta_sin_stock("SIN STOCK")
    assert _esta_sin_stock("No disponible por el momento")


def test_esta_sin_stock_no_da_falso_positivo_con_stock_disponible():
    assert not _esta_sin_stock("Rutini Malbec $15.000 Agregar al carrito")
    assert not _esta_sin_stock("Hay 3 unidades disponibles")


def test_texto_precio_vigente_ignora_precio_tachado():
    html = '<p class="price"><del>$164.700,00</del> $127.700,00</p>'
    precio_el = BeautifulSoup(html, "html.parser").select_one("p")

    texto = _texto_precio_vigente(precio_el)

    assert "164.700" not in texto
    assert normalizar_precio(texto) == 127700.0


def test_texto_precio_vigente_sin_tachado_no_cambia_nada():
    html = '<span class="price">$15.990,50</span>'
    precio_el = BeautifulSoup(html, "html.parser").select_one("span")

    assert normalizar_precio(_texto_precio_vigente(precio_el)) == 15990.50
