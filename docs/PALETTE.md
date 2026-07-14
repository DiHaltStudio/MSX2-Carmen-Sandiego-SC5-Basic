# Paleta y bancos SCREEN 5

`res/VRAM1.bmp`, `res/VRAM2.bmp` y `res/VRAM3.bmp` son imagenes indexadas de
256x256 y comparten exactamente la misma paleta de 16 entradas. Los indices
se conservan al convertirlos a `src/VRAM1.SC5`, `src/VRAM2.SC5` y
`src/VRAM3.SC5`.

## Conversion de los bancos

La utilidad valida dimensiones, modo indexado, indices 0..15 y que las tres
paletas sean identicas:

```bash
python3 tools/bmp_to_bload_sc5.py \
  res/VRAM1.bmp res/VRAM2.bmp res/VRAM3.bmp \
  --output-dir src
```

Cada banco generado mide 32775 bytes:

- 7 bytes de cabecera binaria MSX (`FE`, inicio `0000`, fin `7FFF`, ejecucion
  `0000`).
- 32768 bytes de pixeles SCREEN 5, dos pixeles por byte.

## GAMEPAL.SC5

En SCREEN 5, MSX BASIC espera la copia usada por `COLOR=RESTORE` en la
direccion local de VRAM `&H7680`, que corresponde a Y=237. Insertarla dentro
de cada banco sustituiria 32 bytes de imagen, visibles en un visor como 64
pixeles.

Por eso los bancos conservan todos los pixeles originales y la utilidad genera
por separado `src/GAMEPAL.SC5`:

- 7 bytes de cabecera, inicio `&H7680` y fin `&H769F`.
- 32 bytes de paleta, dos por cada una de las 16 entradas del V9938.
- Tamano total: 39 bytes.

Al terminar la apertura, BASIC carga los bancos en las paginas activas 1, 2 y
3. Despues selecciona la pagina activa 0, carga `GAMEPAL.SC5` y ejecuta
`COLOR=RESTORE`:

```basic
SET PAGE 0,1:BLOAD"VRAM1.SC5",S
SET PAGE 0,2:BLOAD"VRAM2.SC5",S
SET PAGE 0,3:BLOAD"VRAM3.SC5",S
SET PAGE 0,0:BLOAD"GAMEPAL.SC5",S:COLOR=RESTORE
```

La tabla queda solo en la pagina 0, fuera de las 212 lineas visibles. Las
paginas 1, 2 y 3 quedan disponibles como bancos graficos completos.

## Recursos que dependen de esta paleta

- Las escenas catalogadas en `tools/VRAM_SCENES.INC` usan directamente los
  indices de los bancos.
- Los atlas blanco y verde de la fuente viven dentro de `VRAM3.bmp`.
- Las miniimagenes `IMGxxx.SC5` se cuantizan con las primeras 16 entradas de
  `res/VRAM1.bmp` y no incluyen una paleta propia.
- `OPENING.SC5` puede tener su propia tabla durante la pantalla de apertura;
  la paleta del juego se restaura despues con `GAMEPAL.SC5`.

No hay que volver a escribir una tabla de paleta dentro de los bancos completos
ni borrar sus bytes en Y=237.
