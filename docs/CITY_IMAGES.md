# Imagenes de ciudad

El juego contiene 50 miniimagenes, `src/IMG001.SC5` a `src/IMG050.SC5`.
Cada fichero corresponde a la ciudad con el mismo indice en `src/CITIES.DAT`.
Las fotografias originales estan en `image_src/` y su procedencia se conserva
en `IMG_CREDITS.CSV`.

## Conversion actual

`tools/fetch_city_images.py` realiza estos pasos:

1. Abre la fotografia y la convierte a RGB.
2. Recorta y escala desde el centro a 100x100 con filtro Lanczos.
3. La cuantiza con los 16 colores de `res/VRAM1.bmp`.
4. Conserva los mismos indices 0..15 usados por los tres bancos VRAM.
5. Empaqueta dos pixeles por byte para SCREEN 5.

La configuracion incluida actualmente no usa tramado. Para reconstruir las 50
imagenes sin descargar nada:

```bash
python3 tools/fetch_city_images.py \
  --local-only --force-sc5 --dither none
```

La paleta predeterminada es `res/VRAM1.bmp`. Se puede probar otra imagen
indexada de 16 colores sin modificar el script:

```bash
python3 tools/fetch_city_images.py \
  --local-only --force-sc5 --dither none \
  --palette ruta/OTRA_PALETA.bmp
```

Como alternativa visual, `--dither floyd` activa Floyd-Steinberg. Esta opcion
no es la usada en los binarios actuales.

## Formato IMGxxx.SC5

Estos ficheros no son volcados completos creados con `BLOAD/BSAVE`. Son el
formato rectangular que entiende `COPY "IMGxxx.SC5" TO (X,Y)`:

```text
WORD ancho = 100
WORD alto  = 100
5000 bytes de pixeles SCREEN 5
```

Cada byte contiene el pixel par en el nibble alto y el impar en el bajo. El
tamano total es 5004 bytes. El fichero no guarda paleta: los indices se
interpretan con la paleta global cargada desde `GAMEPAL.SC5`.

## Carga y cache VRAM

La rutina BASIC `3470` cambia solo la pagina activa y carga la imagen en la
cache `(156,74)` de la pagina 1:

```basic
SET PAGE 0,1
COPY FI$ TO (156,74)
SET PAGE 0,0
```

La pagina visible permanece en 0. La rutina maquina se invoca con `Z=USR(0)`
y hace una HMMM de 100x100 desde la coordenada global `(156,330)` hasta
`(150,54)` de la pagina visible. `IC` recuerda la ciudad cacheada para no leer
el disco durante cada repintado del menu.

## Verificacion

Tras regenerar, deben existir exactamente 50 ficheros de 5004 bytes y sus
primeros cuatro bytes deben ser `64 00 64 00`:

```bash
find src -maxdepth 1 -name 'IMG???.SC5' | wc -l
stat -c '%s %n' src/IMG???.SC5
xxd -g1 -l4 src/IMG001.SC5
```

Finalmente hay que ejecutar `./release.sh` para copiarlos a la imagen de
disco.
