# Buscador de Vinos — Comparador de precios

Programa en Python que busca un vino por nombre en varias fuentes (vinotecas,
bodegas, importador) y muestra una tabla con: **vino, precio, moneda, fuente
y tipo de fuente**.

## Instalación

```bash
pip install -r requirements.txt
```

## Uso

```bash
python main.py "Rutini Malbec"
```

Salida:

```
Vino          | Precio    | Moneda | Fuente          | Tipo
--------------+-----------+--------+-----------------+----------
Rutini Malbec | 12.500,00 | ARS    | Bodega Norton   | bodega
Rutini Malbec | 13.200,00 | ARS    | 1000 Vinos      | vinoteca
...
```

Opciones:

- `--demo` — usa fuentes simuladas (sin red), útil para probar el programa
  de punta a punta o para desarrollo/CI.
- `--csv resultados.csv` — exporta la tabla a CSV.
- `--timeout N` — timeout total en segundos para esperar a todas las fuentes
  en paralelo (default 20).
- `-v` / `--verbose` — muestra logs de qué fuente falló y por qué.

Probá primero con `--demo`:

```bash
python main.py "Rutini Malbec" --demo
```

## Fuentes configuradas

En `buscador_vino/fuentes/config.py`:

| Fuente | Tipo |
|---|---|
| 1000 Vinos | vinoteca |
| La Vinoteca | vinoteca |
| Bodega Norton | bodega |
| Familia Zuccardi | bodega |
| Otto Wein | importador |

## ⚠️ Importante: ajustar selectores antes de usar en modo real

Cada fuente real (`FuenteScraping`) hace scraping HTML de la página de
resultados de búsqueda del sitio, usando selectores CSS para extraer nombre
y precio de cada producto.

**Estos selectores son una aproximación basada en las plataformas de
e-commerce típicas (Magento, WooCommerce, Shopify) que suelen usar estos
sitios, pero no se pudieron verificar en vivo**: el entorno donde se
desarrolló este programa tiene la salida de red restringida a un proxy que
bloquea el acceso a estos dominios, así que nunca se llegó a inspeccionar
el HTML real de cada uno.

Antes de usarlo en serio:

1. Corré `python main.py "algún vino" -v` y mirá los warnings — te dicen
   qué fuente no devolvió resultados.
2. Abrí la página de búsqueda de esa fuente en el navegador (ej.
   `https://www.1000vinos.com/catalogsearch/result/?q=malbec`).
3. Con F12 → inspeccionar, fijate las clases CSS que envuelven cada
   producto, su nombre y su precio.
4. Actualizá `selector_item`, `selector_nombre`, `selector_precio` (y
   `selector_link` si hace falta) de esa fuente en
   `buscador_vino/fuentes/config.py`.

No hace falta tocar ningún otro archivo: la lógica de scraping es genérica.

## Agregar una fuente nueva

Sumá una entrada más a `FUENTES_REALES` en `buscador_vino/fuentes/config.py`:

```python
FuenteScraping(
    nombre="Nombre a mostrar",
    tipo="vinoteca",  # o "bodega" / "importador"
    url_busqueda="https://ejemplo.com/buscar?q={query}",
    base_url="https://ejemplo.com",
    selector_item="...",     # contenedor de cada resultado
    selector_nombre="...",   # dentro del item, el nombre del vino
    selector_precio="...",   # dentro del item, el precio
),
```

Si el sitio no se puede scrapear por HTML (todo se renderiza con
JavaScript, tiene una API, etc.), se puede implementar una fuente distinta
heredando de `FuenteBase` (ver `buscador_vino/fuentes/base.py`) e
implementando `buscar(consulta) -> List[ResultadoPrecio]` como quieras
(requests a una API, Selenium/Playwright, lo que corresponda).

## Arquitectura

```
buscador_vino/
  models.py           # ResultadoPrecio (vino, precio, moneda, fuente, tipo, url)
  parsing.py           # normaliza texto de precio ("$ 15.990,50") a float
  comparador.py         # ejecuta todas las fuentes en paralelo y ordena por precio
  tabla.py             # arma la tabla de texto
  fuentes/
    base.py            # interfaz FuenteBase
    scraping.py         # FuenteScraping: scraping HTML genérico y configurable
    mock.py            # FuenteSimulada: fuente de demo sin red
    config.py           # instancia las fuentes reales y las de demo
main.py                # CLI (argparse)
tests/                 # pytest, corren con --demo (sin red)
```

Cada fuente corre en su propio hilo (`ThreadPoolExecutor`) y si una falla
(sitio caído, selector desactualizado, timeout) se ignora sin afectar a las
demás — el resultado es parcial, no un crash.

## Tests

```bash
pip install pytest
pytest
```

Los tests usan `FuenteSimulada`, así que corren sin conexión a internet.

## Uso responsable

Este programa hace pedidos HTTP normales (no headless browser, no bypass de
protecciones) a páginas públicas de búsqueda. Si lo vas a correr seguido o
sobre muchas fuentes:

- Revisá el `robots.txt` y los términos de uso de cada sitio.
- No lo corras en loops ajustados ni con muchos vinos en simultáneo contra
  el mismo sitio — agregá una pausa entre búsquedas si vas a iterar una
  lista.
- Usalo para consulta personal/comparación de precios, no para scraping
  masivo o reventa de datos.
