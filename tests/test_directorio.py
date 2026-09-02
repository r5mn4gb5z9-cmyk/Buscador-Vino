from buscador_vino.fuentes.config import FUENTES_DEMO, FUENTES_REALES
from buscador_vino.fuentes.directorio import BODEGAS_SIN_TIENDA
from buscador_vino.fuentes.mock import FuenteSimulada
from buscador_vino.models import ContactoDirecto
from buscador_vino.tabla import imprimir_directorio


def test_todas_las_fuentes_reales_tienen_nombre_y_dominio_unico():
    nombres = [f.nombre for f in FUENTES_REALES]
    dominios = [f.base_url for f in FUENTES_REALES]
    assert len(nombres) == len(set(nombres)), "hay nombres de fuente repetidos"
    assert len(dominios) == len(set(dominios)), "hay dominios repetidos"


def test_fuentes_reales_y_demo_tienen_la_misma_cantidad():
    assert len(FUENTES_REALES) == len(FUENTES_DEMO)


def test_fuente_simulada_expone_region():
    f = FuenteSimulada("Bodega Test", "bodega", region="Salta")
    assert f.region == "Salta"


def test_imprimir_directorio_sin_bodegas():
    assert "No se encontraron" in imprimir_directorio([])


def test_imprimir_directorio_incluye_contacto_y_region():
    bodegas = [
        ContactoDirecto(
            nombre="Bodega Tacuil",
            tipo="bodega",
            region="Salta (Molinos)",
            medio="whatsapp",
            contacto="+54 9 387 210-6076",
            url="https://wa.me/5493872106076",
        )
    ]
    tabla = imprimir_directorio(bodegas)
    assert "Bodega Tacuil" in tabla
    assert "Salta (Molinos)" in tabla
    assert "wa.me" in tabla


def test_directorio_sin_dominios_repetidos_con_fuentes_reales():
    dominios_reales = {f.base_url for f in FUENTES_REALES}
    urls_directorio = {b.url for b in BODEGAS_SIN_TIENDA if b.url}
    assert dominios_reales.isdisjoint(urls_directorio)
