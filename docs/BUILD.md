# Construccion y regeneracion de recursos

## Dependencias

Para generar el disco final:

- Bash.
- `mtools`: `mcopy`, `mdel` y `mdir`.
- Sjasm clasico disponible como `sjasm`; no SjasmPlus.

Para regenerar recursos graficos tambien se necesita Python 3 con Pillow.

## Flujo completo

### 1. Actualizar los atlas de fuente

```bash
python3 tools/insert_round_font.py res/round_6x6.png res/VRAM3.bmp
```

La utilidad escribe ASCII 32..93 en Y local 152 de `VRAM3.bmp`. El codigo 92
representa la ENE espanola mediante el caracter `\`.

### 2. Regenerar bancos y paleta

```bash
python3 tools/bmp_to_bload_sc5.py \
  res/VRAM1.bmp res/VRAM2.bmp res/VRAM3.bmp \
  --output-dir src
```

Este paso genera los tres bancos completos y `src/GAMEPAL.SC5`. Vease
`docs/PALETTE.md`.

### 3. Regenerar las imagenes de ciudad

```bash
python3 tools/fetch_city_images.py \
  --local-only --force-sc5 --dither none
```

Las fuentes locales estan en `image_src/`. El modo actual usa la paleta de
`res/VRAM1.bmp` y no aplica tramado. Vease `docs/CITY_IMAGES.md`.

### 4. Renumerar el listado BASIC

El fichero entregado ya esta renumerado. Tras insertar o eliminar lineas puede
normalizarse otra vez sin depender de un emulador:

```bash
python3 tools/renumber_basic.py src/CARMEN5.BAS
```

La utilidad actualiza referencias de control, conserva ASCII con CR/LF y
rechaza destinos inexistentes. No modifica numeros dentro de cadenas ni
comentarios.

### 5. Generar la imagen de disco

```bash
./release.sh
```

El script ensambla `tools/FONT6.ASM` como `src/FONT6.BIN`, vacia el directorio
raiz de `dist/CARMENSANDIEGO_MSX2.dsk` y copia todos los ficheros de `src/`.

La imagen usa actualmente las 112 entradas disponibles en el directorio raiz
del disquete. No se debe anadir otro fichero a `src/` sin retirar o agrupar
otro recurso, porque `mcopy` fallaria con `No directory slots`.

## Comprobaciones

```bash
file src/CARMEN5.BAS src/*.DAT src/*.SC5
python3 -m py_compile \
  tools/bmp_to_bload_sc5.py \
  tools/fetch_city_images.py \
  tools/insert_round_font.py \
  tools/renumber_basic.py
./release.sh
```

Requisitos de formato:

- `src/CARMEN5.BAS` y todos los `.DAT`: ASCII con CR/LF.
- `src/autoexec.bas`: lanzador tokenizado de MSX BASIC.
- `.SC5`, `FONT6.BIN` y la imagen `.dsk`: binarios.

`release.sh` no regenera los PNG, BMP ni `IMGxxx.SC5`; solo ensambla la rutina
Z80 y actualiza el disco con el contenido actual de `src/`.

## Portabilidad de rutas

No hay rutas absolutas fijas del equipo en los scripts ni en la documentacion.
`release.sh` cambia al directorio donde se encuentra y trabaja con `src/` y
`dist/` relativos. Las utilidades Python reciben rutas por argumentos o
calculan la raiz desde su propio fichero, de modo que el repositorio puede
moverse completo a otro directorio.
