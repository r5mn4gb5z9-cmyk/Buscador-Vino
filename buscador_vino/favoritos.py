"""Persistencia simple de "mis favoritos": nombres de vino/bodega que el
usuario quiere volver a chequear en cada corrida, sin tener que escribirlos
de nuevo cada vez.

Se guardan en un archivo JSON local (`favoritos.json` en la raíz del
proyecto por default, fuera de git — ver `.gitignore`) en vez de una base
de datos: es una lista chica que edita un solo usuario desde su
compu/celu, no hace falta más que eso.

La ruta se puede pisar con la variable de entorno `FAVORITOS_PATH` — hace
falta en plataformas como Railway, donde el disco del contenedor es
efímero (se borra en cada redeploy) salvo que se monte un volumen
persistente en otra ruta.
"""
import json
import os
from pathlib import Path
from typing import List

from .texto import normalizar

RUTA_FAVORITOS = Path(
    os.environ.get("FAVORITOS_PATH", str(Path(__file__).resolve().parent.parent / "favoritos.json"))
)


def cargar_favoritos() -> List[str]:
    if not RUTA_FAVORITOS.exists():
        return []
    try:
        with open(RUTA_FAVORITOS, encoding="utf-8") as f:
            datos = json.load(f)
    except (json.JSONDecodeError, OSError):
        return []
    return [str(n) for n in datos if str(n).strip()]


def _guardar(favoritos: List[str]) -> None:
    with open(RUTA_FAVORITOS, "w", encoding="utf-8") as f:
        json.dump(favoritos, f, ensure_ascii=False, indent=2)


def agregar_favorito(nombre: str) -> bool:
    """Agrega `nombre` a favoritos si no estaba ya (comparación sin
    distinguir mayúsculas/tildes). Devuelve True si lo agregó, False si ya
    estaba."""
    nombre = nombre.strip()
    if not nombre:
        return False
    favoritos = cargar_favoritos()
    if normalizar(nombre) in {normalizar(f) for f in favoritos}:
        return False
    favoritos.append(nombre)
    _guardar(favoritos)
    return True


def quitar_favorito(nombre: str) -> bool:
    """Saca `nombre` de favoritos (comparación sin distinguir
    mayúsculas/tildes). Devuelve True si lo sacó, False si no estaba."""
    favoritos = cargar_favoritos()
    objetivo = normalizar(nombre)
    restantes = [f for f in favoritos if normalizar(f) != objetivo]
    if len(restantes) == len(favoritos):
        return False
    _guardar(restantes)
    return True
