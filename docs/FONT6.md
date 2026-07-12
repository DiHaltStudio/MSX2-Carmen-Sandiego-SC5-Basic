# Rutina de texto 6x6

`tools/FONT6.ASM` implementa el texto del juego con el motor de comandos del
V9938. Se ensambla con Sjasm clasico y genera `src/FONT6.BIN`, un binario MSX
cargable mediante `BLOAD`.

## Memoria

El binario ocupa `&HD800-&HD935`. BASIC reserva esa zona con:

```basic
CLEAR 8000,&HD7FF
BLOAD"FONT6.BIN"
DEFUSR=&HD800
```

El limite `&HD7FF` evita que programa, variables y cadenas puedan invadir el
codigo maquina. La direccion queda ademas separada del limite alto de Disk
BASIC. El binario no usa memoria fuera de su propio bloque.

## Llamada

La funcion recibe una sola cadena:

```basic
U$=CHR$(TX)+CHR$(TY)+T$
U$=USR(U$)
TX=ASC(U$):TY=ASC(MID$(U$,2,1))
```

- Byte 0: coordenada X inicial, de 0 a 255.
- Byte 1: coordenada Y inicial, de 0 a 206.
- Bytes 2 en adelante: texto.

La rutina escribe en la pagina 0 de SCREEN 5 usando copias HMMM de 6x6 desde
la fuente situada en la pagina 3, coordenada local `(0,152)`. Convierte ASCII
minuscula a mayuscula, acepta ASCII 32 a 93 y usa espacio para cualquier otro
codigo. ASCII 92 (`\`) selecciona la ENE espanola.

Cada glifo reinicia los dos bytes de DX y DY, por lo que una copia previa hacia
la cache de la pagina 1 no puede dejar activo un bit de pagina en el destino del
texto.

Cuando no cabe otro glifo, continua en `X=0,Y=Y+6`. Al volver, los dos primeros
bytes contienen `X=0` y la Y de la siguiente linea, de modo que llamadas
consecutivas siguen escribiendo debajo. No se dibuja fuera de las 212 lineas
visibles.

## Atlas de glifos

La imagen fuente editable es `res/round_6x6.png`, de 78x42 pixeles. La utilidad
`tools/insert_round_font.py` extrae y ordena ASCII 32..93, crea el espacio y la
ENE espanola y escribe el atlas en `(0,152)` de `res/VRAM3.bmp`:

```bash
python3 tools/insert_round_font.py res/round_6x6.png res/VRAM3.bmp
python3 tools/bmp_to_bload_sc5.py res/VRAM3.bmp --output-dir res
cp res/VRAM3.SC5 src/VRAM3.SC5
```

El atlas tiene 42 caracteres en la primera fila y 20 en la segunda. Cada celda
ocupa exactamente 6x6 y puede copiarse contigua a la siguiente.

## Menus

La rutina BASIC `2300` dibuja las opciones una sola vez. Al mover el selector
solo borra el caracter `>` anterior y dibuja el nuevo, evitando repintados y
accesos innecesarios al motor de comandos. El menu principal limpia en negro
solo su zona izquierda para no borrar la miniimagen de ciudad.

## Copia de la imagen de ciudad

La misma funcion acepta un entero para copiar la imagen cacheada:

```basic
Z=USR(0)
```

La cache empieza en la coordenada VRAM global Y=330 y ocupa
`(156,330)-(255,429)`, equivalente a `(156,74)-(255,173)` de la pagina 1. Se
mantiene dentro de las 212 lineas direccionables para que una sola HMMM
reconstruya las 100 filas en `(150,54)-(249,153)` de la pagina 0.

Para cargar una ciudad nueva se escribe directamente en la pagina 1:

```basic
SET PAGE 0,1
COPY FI$ TO (156,74)
SET PAGE 0,0
```

Como la cache termina en Y local 173, BASIC puede cargar las 100 filas sin
recorte. La pagina visible permanece siempre en 0, por lo que la imagen no
aparece durante mensajes de transicion como `HAS VIAJADO A`.

## Compilacion

`release.sh` ejecuta:

```bash
sjasm tools/FONT6.ASM src/FONT6.BIN /dev/null
```

Se requiere Sjasm clasico; no se usa sintaxis especifica de SjasmPlus.
