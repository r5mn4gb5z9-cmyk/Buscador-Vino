# Buscador de Vinos — dónde comprar más barato

Programa en Python que busca un vino o bodega por nombre en varias fuentes
(vinotecas, bodegas, importador) y te dice **dónde comprarlo más barato**,
con el link directo a la página del producto. También muestra el resto de
las opciones para comparar.

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
Más barato en Bodega Norton (bodega): $ 12.500,00 ARS
https://www.bodeganorton.com/tienda/producto/rutini-malbec

Todas las opciones:
Vino          | Precio    | Moneda | Fuente          | Tipo
--------------+-----------+--------+-----------------+----------
Rutini Malbec | 12.500,00 | ARS    | Bodega Norton   | bodega
Rutini Malbec | 13.200,00 | ARS    | 1000 Vinos      | vinoteca
...
```

Opciones:

- `--demo` — usa fuentes simuladas (sin red), útil para probar el programa
  de punta a punta o para desarrollo/CI.
- `--tipo vinoteca|bodega|importador` — busca solo en ese tipo de fuente en
  vez de en las 30.
- `--csv resultados.csv` — exporta la tabla a CSV.
- `--timeout N` — timeout total en segundos para esperar a todas las fuentes
  en paralelo (default 30).
- `-v` / `--verbose` — muestra logs de qué fuente falló y por qué.

Probá primero con `--demo`:

```bash
python main.py "Rutini Malbec" --demo
```

## Fuentes configuradas (30)

En `buscador_vino/fuentes/config.py`, agrupadas por tipo:

| Vinotecas (10) | Bodegas — venta directa (10) | Importadoras (10) |
|---|---|---|
| 1000 Vinos | Bodegas Bianchi | Enotek |
| Espaciovino | Cava Colomé | Lar de Vinos |
| Winery | Luigi Bosca | Armesto Almacén |
| Vinoteca BARI | Bodega Norton | Casa Dionisio Vinoteca |
| TiendaVinos | Rutini Wines | Rebellion House of Wines |
| Casa de Vinos Mendoza | Susana Balbo | Lo de Granado |
| Vinos x Caja | Escorihuela Gascón | Vinoteca Ligier |
| MercadoDeVinos | Familia Schroeder | Vinos Inc |
| La Viteca | Achaval Ferrer | Aldos Vinoteca |
| Bonvivir | Krontiras Wines | Grand Cru |

Los nombres y dominios salen de búsquedas reales (no están inventados),
pero leé la siguiente sección antes de asumir que las 30 andan de una.

## ⚠️ Importante: verificar las fuentes antes de usar en modo real

Cada fuente real (`FuenteScraping`) hace scraping HTML de la página de
resultados de búsqueda del sitio.

**No se pudo confirmar en vivo qué plataforma de e-commerce corre cada uno
de estos 30 sitios ni sus selectores CSS exactos**: el entorno donde se
desarrolló este programa tiene la salida de red restringida a un proxy que
bloquea el acceso a estos dominios, así que nunca se llegó a inspeccionar
el HTML real de ninguna búsqueda.

Para compensar eso, cada fuente prueba automáticamente hasta 2 patrones de
URL de búsqueda típicos de las plataformas más usadas en Argentina
(Magento, WooCommerce, Tiendanube, Shopify, VTEX), y en cada intento usa
selectores CSS "unión" que cubren las 5 plataformas a la vez (ver
`buscador_vino/fuentes/plataformas.py`). Esto hace que probablemente
varias fuentes anden de entrada sin tocar nada, pero no las 30.

Una corrida real (30 fuentes, búsqueda "malbec") dio 12/30 con resultados,
pero varios de esos 12 eran falsos positivos: el patrón de URL caía en el
catálogo genérico o la home en vez de una búsqueda real, y el selector
"unión" agarraba cualquier producto de ahí (una botella de agua, un
aceite de oliva) o un precio con la oferta y el precio tachado pegados sin
separador, dando números sin sentido. Por eso `FuenteScraping` ahora:

- Descarta un ítem si su nombre no comparte ninguna palabra con lo
  buscado (evita mostrar "aceite de oliva" como resultado de "malbec").
- Descarta un precio fuera de un rango razonable para una botella
  (500–2.000.000 ARS), y toma el primer número con forma de precio del
  texto en vez de mezclar varios precios pegados en uno solo.

Con esto, una fuente que antes daba OK con datos falsos ahora
correctamente da VACÍO (y prueba el siguiente patrón de URL) — es más
honesto, aunque el conteo de "fuentes OK" baje.

**Primer paso, con conexión a internet real (no en un sandbox restringido):**

```bash
python scripts/verificar_fuentes.py "malbec"
```

Te tira un check por fuente: cuáles devolvieron resultados y cuáles no.
Para una que dio VACÍO:

1. Corré `python scripts/verificar_fuentes.py "malbec" -v` y mirá los
   logs DEBUG de esa fuente — te dicen qué URLs probó y por qué no
   matchearon.
2. Abrí esa URL de búsqueda en el navegador.
3. Con F12 → inspeccionar, fijate las clases CSS que envuelven cada
   producto, su nombre y su precio.
4. Ajustá esa fuente en `buscador_vino/fuentes/config.py`: agregá su
   plataforma correcta a la lista `"plataformas"` (si es una de las 5
   conocidas), o si no encaja en ninguna, definile selectores propios
   pasándole `selector_item` / `selector_nombre` / `selector_precio`
   específicos en vez de los genéricos.

## Agregar una fuente nueva

Sumá una entrada más a `FUENTES_INFO` en `buscador_vino/fuentes/config.py`:

```python
{
    "nombre": "Nombre a mostrar",
    "tipo": "vinoteca",  # o "bodega" / "importador"
    "base_url": "https://ejemplo.com",
    "plataformas": ["tiendanube", "woocommerce"],  # orden de prioridad
},
```

`FUENTES_REALES` y `FUENTES_DEMO` se arman solos a partir de esa lista. Si
el sitio no encaja en ninguna de las 5 plataformas conocidas (todo se
renderiza con JavaScript, tiene una API propia, etc.), armá su
`FuenteScraping` a mano con selectores propios, o implementá una fuente
distinta heredando de `FuenteBase` (ver `buscador_vino/fuentes/base.py`).

## Arquitectura

```
buscador_vino/
  models.py           # ResultadoPrecio (vino, precio, moneda, fuente, tipo, url)
  parsing.py           # normaliza texto de precio ("$ 15.990,50") a float
  comparador.py         # ejecuta todas las fuentes en paralelo y ordena por precio
  tabla.py             # arma el resumen "más barato" + la tabla completa
  fuentes/
    base.py            # interfaz FuenteBase
    plataformas.py       # patrones de URL y selectores CSS comunes por plataforma
    scraping.py         # FuenteScraping: prueba patrones de URL hasta encontrar resultados
    mock.py            # FuenteSimulada: fuente de demo sin red
    config.py           # FUENTES_INFO (30 sitios) -> FUENTES_REALES / FUENTES_DEMO
main.py                # CLI (argparse)
scripts/verificar_fuentes.py  # diagnóstico: qué fuentes reales andan y cuáles no
tests/                 # pytest, corren con --demo (sin red)
```

Cada fuente corre en su propio hilo (`ThreadPoolExecutor`) y si una falla
(sitio caído, selector desactualizado, timeout) se ignora sin afectar a las
demás — el resultado es parcial, no un crash.

## Interfaz web (para abrir desde el celu)

Además del CLI hay una mini app web (Flask) en `web/app.py` con buscador y
tabla, pensada para verse bien en el navegador del celular.

```bash
pip install -r requirements.txt
python web/app.py
```

Se levanta en `http://0.0.0.0:5000`. Cómo abrirla desde el celu:

- **Corriéndola en tu compu:** fijate la IP local de la compu (`ipconfig`
  en Windows, `ifconfig`/`ip a` en Mac/Linux — algo como `192.168.0.15`) y
  entrá desde el celu (misma WiFi) a `http://192.168.0.15:5000`.
- **Corriéndola directo en el celu con Termux** (ver sección de arriba):
  abrí `http://127.0.0.1:5000` en el navegador del mismo celu.

Tiene un checkbox "Modo demo" para probarla sin depender de que los
selectores de scraping estén ajustados.

### Versión de solo-demo, sin instalar nada

Si sólo querés ver la interfaz funcionando ya, sin instalar Python ni nada,
hay una versión de demostración publicada como página web (con precios
simulados, igual que el modo `--demo`): pedísela a quien te compartió este
repo, o generá una nueva con Claude Code a partir de este proyecto.

## Tests

```bash
pip install pytest
pytest
```

Los tests usan `FuenteSimulada`, así que corren sin conexión a internet.

## Uso responsable

Este programa hace pedidos HTTP normales (no headless browser, no bypass de
protecciones) a páginas públicas de búsqueda. Con 30 fuentes y hasta 2
patrones de URL cada una, una sola búsqueda puede implicar hasta ~60
pedidos HTTP (bastantes menos en la práctica, porque se corta apenas un
patrón encuentra resultados). Si lo vas a correr seguido:

- Revisá el `robots.txt` y los términos de uso de cada sitio.
- No lo corras en loops ajustados ni con muchos vinos en simultáneo contra
  el mismo sitio — agregá una pausa entre búsquedas si vas a iterar una
  lista.
- Usalo para consulta personal/comparación de precios, no para scraping
  masivo o reventa de datos.
