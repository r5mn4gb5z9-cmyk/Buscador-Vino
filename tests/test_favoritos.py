import tempfile
from pathlib import Path

import buscador_vino.favoritos as favoritos_mod


def _con_archivo_temporal(fn):
    """Corre fn() con RUTA_FAVORITOS apuntando a un archivo temporal, para
    no tocar los favoritos reales del usuario mientras corren los tests."""
    original = favoritos_mod.RUTA_FAVORITOS
    with tempfile.TemporaryDirectory() as tmp:
        favoritos_mod.RUTA_FAVORITOS = Path(tmp) / "favoritos.json"
        try:
            fn()
        finally:
            favoritos_mod.RUTA_FAVORITOS = original


def test_cargar_favoritos_sin_archivo_devuelve_vacio():
    def _test():
        assert favoritos_mod.cargar_favoritos() == []

    _con_archivo_temporal(_test)


def test_agregar_y_cargar_favorito():
    def _test():
        assert favoritos_mod.agregar_favorito("Rutini Malbec") is True
        assert favoritos_mod.cargar_favoritos() == ["Rutini Malbec"]

    _con_archivo_temporal(_test)


def test_agregar_favorito_duplicado_sin_distinguir_tildes_ni_mayusculas():
    def _test():
        favoritos_mod.agregar_favorito("Rutini Malbec")
        assert favoritos_mod.agregar_favorito("rutini malbec") is False
        assert favoritos_mod.agregar_favorito("RUTINI MALBEC") is False
        assert favoritos_mod.cargar_favoritos() == ["Rutini Malbec"]

    _con_archivo_temporal(_test)


def test_agregar_favorito_vacio_no_hace_nada():
    def _test():
        assert favoritos_mod.agregar_favorito("   ") is False
        assert favoritos_mod.cargar_favoritos() == []

    _con_archivo_temporal(_test)


def test_quitar_favorito():
    def _test():
        favoritos_mod.agregar_favorito("Rutini Malbec")
        favoritos_mod.agregar_favorito("Bodega Chacra")
        assert favoritos_mod.quitar_favorito("rutini malbec") is True
        assert favoritos_mod.cargar_favoritos() == ["Bodega Chacra"]

    _con_archivo_temporal(_test)


def test_quitar_favorito_inexistente():
    def _test():
        assert favoritos_mod.quitar_favorito("no existe") is False

    _con_archivo_temporal(_test)
