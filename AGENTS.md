# CarmenSandiegoBAS SC5

## Objetivo

Crear una version simplificada tipo "Where in the World is Carmen Sandiego" para MSX2 BASIC. El juego usa una base textual con opciones por numero/cursor y apoyo grafico en `SCREEN 5`. Los datos de juego deben vivir en ficheros externos para evitar una base de datos interna grande en RAM.

## Estado Actual

- `src/CARMEN5.BAS` contiene la version fuente jugable con graficos SC5.
- `dist/CARMENSANDIEGO_MSX2.dsk` es la imagen de disco generada con `release.sh`.
- Usa `SCREEN 5`, `WIDTH 32`, salida a `GRP:`, menus genericos con cursor y pausa con `INPUT$(1)`.
- Los datos ya estan externalizados en ficheros `.DAT`.
- `CARMEN5.BAS` carga el indice de 50 ciudades y solo los nombres de 15 sospechosos al inicio.
- Cada ciudad se carga desde disco al llegar a ella mediante `CITYxxx.DAT`.
- Cada ciudad puede tener una imagen `IMGxxx.SC5` de 100x100 pixeles.
- La imagen de ciudad se carga desde disco una sola vez al entrar en la ciudad y queda cacheada en VRAM pagina 1.
- Los repintados del menu principal copian la imagen de ciudad desde VRAM pagina 1 a VRAM pagina 0, sin volver a leer disco.
- `OPENING.SC5` contiene la pantalla de apertura y se muestra con `BLOAD"OPENING.SC5",S`.
- Al cerrar la apertura se cargan `VRAM1.SC5`, `VRAM2.SC5` y `VRAM3.SC5` en las paginas 1, 2 y 3.
- Los tres bancos contienen la paleta del juego, que se activa con `COLOR=RESTORE`.
- La ruta de cada caso se genera al azar sin repetir ciudad.
- Las opciones de vuelo se generan al azar desde las ciudades de la BD, sin repetir opcion ni incluir la ciudad actual.
- Si el jugador se sale de la ruta correcta, una de las opciones de vuelo permite volver a la ciudad de la pista activa.
- La orden de arresto se calcula por filtros parciales, no por seleccion directa de sospechoso.
- La lista de sospechosos marca con `*` los detenidos y el calculo de orden ignora esos detenidos.
- Una partida completa requiere 5 detenciones correctas. Tras cada arresto correcto se genera un nuevo caso aleatorio.
- La dificultad sube reduciendo el tiempo limite de cada caso.

## Requisito De Formato

- `src/CARMEN5.BAS` debe conservar finales de linea DOS `CR/LF`.
- Los `.DAT` tambien se mantienen con `CR/LF` para facilitar uso en MSX/DOS.
- Mantener `.BAS` y `.DAT` en ASCII.
- Evitar acentos y caracteres especiales en `.BAS` y `.DAT`.
- Los `.SC5` son binarios y no deben normalizarse como texto.

Comprobacion recomendada tras editar:

```bash
file src/CARMEN5.BAS src/*.DAT src/*.SC5
```

Tras modificar ficheros en `src/`, regenerar el disco:

```bash
./release.sh
```

## Bucle De Juego

El jugador empieza en una ciudad aleatoria y debe seguir una ruta de pistas:

1. Investigar lugares de la ciudad actual.
2. Viajar a otra ciudad.
3. Revisar lista de sospechosos, donde `*` indica detenidos.
4. Introducir filtros de identidad en la orden.
5. Calcular orden de arresto.
6. Llegar a la ciudad final.
7. Arrestar con la orden correcta.
8. Repetir hasta lograr 5 detenciones.

Cada accion consume tiempo:

- Investigar: 2 horas.
- Viajar: 6 horas.
- Cancelar viaje con `NO VIAJAR`: 0 horas.
- Calcular orden: 1 hora.
- Arrestar en ciudad incorrecta: 2 horas.

El limite de cada caso se calcula al generarlo con:

```basic
TL=72-(AR*4+2)
```

`AR` contiene el numero de detenciones ya logradas. Por tanto, el primer caso
empieza con 70 horas y cada nueva detencion reduce el siguiente limite en 4:

- Caso 1: 70 horas.
- Caso 2: 66 horas.
- Caso 3: 62 horas.
- Caso 4: 58 horas.
- Caso 5: 54 horas.

## Orden De Arresto

La opcion `EMITIR ORDEN` permite elegir caracteristicas parciales:

- Sexo
- Pelo
- Vehiculo
- Rasgo
- Aficion

No es obligatorio rellenar todos los filtros. Al calcular:

- Si no coincide nadie, no se emite orden.
- Si coinciden varios sospechosos, se muestran nombres candidatos y no se emite orden.
- Si coincide exactamente uno, se emite orden contra ese sospechoso.
- Los sospechosos ya detenidos no cuentan como candidatos.

La opcion `VER SOSPECHOSOS` solo muestra nombres, no caracteristicas.

## Menus

Todas las opciones del juego usan la rutina generica `2300`.

- `O$(1..MN)` contiene los textos de opcion.
- `MN` contiene el numero de opciones.
- `MY` contiene la fila inicial de dibujo.
- La rutina devuelve la opcion seleccionada en `OP`.

Controles:

- Cursor abajo mueve el selector hacia abajo.
- Cursor arriba mueve el selector hacia arriba.
- Espacio o RETURN selecciona.
- Se mantiene entrada numerica como respaldo rapido de prueba.
- Al mover el selector solo se borra el `>` anterior y se dibuja el nuevo; no se repintan las opciones.
- El menu principal limpia solo su zona izquierda para no borrar la imagen de ciudad situada a la derecha.

En el menu `VIAJAR`, la ultima opcion debe ser siempre `NO VIAJAR`. Esa opcion vuelve al menu principal sin cambiar de ciudad y sin gastar tiempo.

## Estructura De Lineas

- `10-99`: arranque.
- `100-299`: menu principal.
- `300-399`: investigar.
- `400-499`: viajar.
- `500-599`: ver sospechosos.
- `600-699`: emitir orden.
- `700-799`: estado del caso.
- `800-899`: arrestar y salir.
- `900-999`: carga de datos iniciales.
- `1000-1099`: carga de ciudad actual.
- `1100-1199`: generacion de caso.
- `1200-1299`: generacion de vuelos.
- `1300-1399`: carga de ficha de ciudad.
- `1400-1499`: seleccion de filtro de orden.
- `1500-1599`: calculo de orden.
- `1600-1699`: comparacion de sospechoso.
- `1700-1799`: pista de identidad.
- `1800-1899`: pausa y comprobacion de tiempo.
- `1900-1999`: intro.
- `2000-2099`: finales.
- `2100-2199`: error de disco/datos.
- `2300-2399`: menu generico con cursor.
- `2400-2499`: imagen de ciudad y cache VRAM.
- `2500-2599`: apertura.
- `2600-2699`: texto 6x6 desde la fuente de VRAM pagina 3.
- `2700-2799`: animaciones de la pantalla inicial y espera por ticks.
- `2800-2899`: animacion de la primera pista tras un viaje correcto.

Cada rutina llamada por `GOSUB` debe empezar con una linea `REM` simple.

Las animaciones sustituyen cada frame con una sola llamada a codigo maquina:
esperan el VBlank, borran la posicion anterior con HMMV y dibujan la nueva con
HMMM. El intervalo `AD` incluye ese VBlank final.

## Graficos SC5

El juego trabaja en `SCREEN 5`. La pagina visible es la pagina 0. Las paginas 1, 2 y 3 contienen los bancos graficos `VRAM1.SC5` a `VRAM3.SC5`. La cache temporal de ciudad empieza en la coordenada VRAM global Y=330 y ocupa `(156,330)-(255,429)`, equivalente a `(156,74)-(255,173)` de la pagina 1. Los graficos originales de esa zona se moveran a otro lugar.

### Apertura

- `2500` muestra la apertura.
- Actualmente se usa `BLOAD"OPENING.SC5",S`.
- Despues de borrar la apertura se cargan los tres bancos VRAM sin hacer visibles sus paginas.
- No cambiar la paleta desde BASIC salvo que se restaure antes de continuar el juego.
- Si se experimenta con paletas, verificar en MSX2/emulador que la pantalla posterior vuelve a colores normales.

### Imagen De Ciudad

La rutina `2400` muestra la imagen de la ciudad en el menu principal.

- `IC` contiene el numero de ciudad cuya imagen esta cacheada.
- Si `IC=CP`, `2400` no lee disco.
- Si `IC<>CP`, `2400` llama a `2460` para cargar la imagen correcta.
- La copia visible se hace con:

```basic
Z=USR(0)
```

La rutina `2460` carga desde disco solo al entrar o cambiar de ciudad.

- Construye `FI$` como `IMGxxx.SC5`.
- Cambia la pagina activa con `SET PAGE 0,1` y carga directamente la imagen en `(156,74)`.
- Restaura siempre `SET PAGE 0,0`; la imagen no debe aparecer durante mensajes de viaje.
- Actualiza `IC=CP`.

La rutina `1000` llama a `2460` despues de cargar la ficha y generar vuelos, de forma que la imagen queda preparada antes del menu principal.

El manejador de error `2200` debe ejecutar `SET PAGE 0,0` antes de mostrar el error, porque un fallo de disco podria ocurrir mientras se esta usando la pagina 1.

### Fuente 6x6

- La fuente empieza en la coordenada VRAM global `(0,920)`, equivalente a `(0,152)` de la pagina 3.
- Contiene los caracteres ASCII 32 a 93 en celdas contiguas de 6x6.
- Hay 42 caracteres en la primera fila del atlas y 20 en la segunda.
- El codigo ASCII 92 (`\`) representa la letra `ENE` espanola.
- `FONT6.BIN` se carga en `&HD800`, reservado mediante `CLEAR 8000,&HD7FF`.
- La rutina `2600` llama a la funcion maquina con `USR` para escribir `T$` en `(TX,TY)` de la pagina 0.
- La funcion maquina usa comandos HMMM de 6x6 y continua en la linea inferior si el texto supera el borde derecho.
- Al terminar una cadena, devuelve `TX=0` y `TY` en la siguiente linea de 6 pixeles.
- Las letras minusculas de los datos se convierten a mayusculas al calcular el glifo.
- Los caracteres fuera del rango disponible se muestran como espacios.
- La apertura y el manejador de error usan la fuente ROM porque pueden ejecutarse antes de cargar `VRAM3.SC5`.
- El menu generico usa el caracter `>` como cursor, sin sprites.

### Escenas De Animacion

- `tools/VRAM_SCENES.INC` contiene 54 rectangulos de origen para futuras copias HMMM.
- Cada registro usa el orden `SX,SY_GLOBAL,NX,NY`; X y ancho son siempre pares.
- VRAM1 aporta 24 escenas y VRAM2 aporta 26.
- De VRAM3 solo se catalogan 4 escenas en Y local 0..44. Desde Y=45 empiezan el mapa y la fuente.
- `docs/VRAM_SCENES.md` documenta grupos, conversion de paginas y conflictos de memoria.
- La cache cruza solo margenes negros de `SC_V1_LADRON_VERDE_CORRE_04` y `05`; sus pixeles visibles y los cinco frames `MIMO` quedan intactos.
- La pantalla inicial mueve `SC_V2_DETECTIVE_MARRON_01..08` de izquierda a derecha en Y=100.
- Tras una pausa de 90 ticks mueve `SC_V2_POLICIAS_01..05` por la misma trayectoria.
- Ambos grupos cambian de fotograma cada 3 ticks y avanzan 4 pixeles por cambio.
- Cada grupo configura su propio valor `AD`; los tiempos de otros grupos se decidiran mas adelante.
- La rutina maquina dibuja escenas con HMMM y borra el rectangulo anterior en negro con HMMV.
- Tras un viaje correcto, la primera pista seleccionada reproduce en Y=154 un grupo aleatorio: cabeza fija en X=90 a 4 ticks, carrera verde a 1 tick o mimo verde a 1 tick.
- `SC_V1_LADRON_VERDE_MIMO_01..05` es un unico grupo formado por los antiguos grupos `PRESO` y `LADRON_VERDE_PARADO`.

## Ficheros De Datos

### `CITIES.DAT`

Formato:

```text
NUM_CIUDADES
CIUDAD_1
CIUDAD_2
...
```

El indice numerico de cada ciudad corresponde a su posicion en este fichero. Actualmente debe haber 50 ciudades y sus ficheros `CITY001.DAT` a `CITY050.DAT`.

### `CITYxxx.DAT`

Ejemplo: `CITY001.DAT`.

Formato fijo de 10 lineas:

```text
NOMBRE
PAIS
MONEDA
MONUMENTO
OBJETO_O_COMIDA
DESCRIPCION_1
DESCRIPCION_2
LUGAR_1
LUGAR_2
LUGAR_3
```

El programa carga este fichero cada vez que entra en una ciudad. Las descripciones deben ser cortas, ASCII y pensadas para pantalla de 40 columnas.

Sintaxis correcta en MSX Disk BASIC:

```basic
OPEN "CITY001.DAT" FOR INPUT AS #1
LINE INPUT #1,A$
CLOSE #1
```

No usar `OPEN "I",#1,"CITY001.DAT"` en MSX Disk BASIC.

### `SUSPECT.DAT`

Formato:

```text
NUM_SOSPECHOSOS
NOMBRE
CODIGO_SEXO
CODIGO_PELO
CODIGO_VEHICULO
CODIGO_RASGO
CODIGO_AFICION
...
```

Cada sospechoso ocupa 6 lineas despues del contador inicial. Actualmente hay 15 sospechosos.

Los codigos apuntan a `ATTR1.DAT` a `ATTR5.DAT`. El programa mantiene en RAM solo `S$(I)` con nombres y escanea `SUSPECT.DAT` desde disco al calcular la orden.

### `ATTR1.DAT` A `ATTR5.DAT`

Cada fichero contiene los valores posibles de una categoria de orden:

- `ATTR1.DAT`: sexo.
- `ATTR2.DAT`: pelo.
- `ATTR3.DAT`: vehiculo.
- `ATTR4.DAT`: rasgo.
- `ATTR5.DAT`: aficion.

Formato:

```text
NUM_VALORES
VALOR_1
VALOR_2
...
```

### `IMGxxx.SC5`

Cada ciudad puede tener una imagen `IMG001.SC5` a `IMG050.SC5`.

- Formato usado por `COPY "IMGxxx.SC5" TO (X,Y)`.
- Tamano actual: 100x100 pixeles, 4 bits por pixel, 5004 bytes.
- Los primeros 4 bytes indican ancho y alto.
- La imagen se muestra completa en `(150,54)-(249,153)` mediante una HMMM de la rutina maquina.
- No usar `COPY (156,156)-(255,255),1`: BASIC y el motor V9938 recortan en la linea logica Y=211 y solo muestran 56 filas.
- No se cargan todas las imagenes en RAM ni en VRAM; solo se cachea la ciudad actual.

### `OPENING.SC5`

Pantalla de apertura.

- Se carga con `BLOAD"OPENING.SC5",S`.
- Puede incluir datos de pantalla/paleta segun el formato generado.
- Si se cambia el formato de apertura, comprobar en emulador que la carga sigue siendo compatible con MSX2 BASIC.

## Restricciones MSX BASIC

- Mantener el fichero `.BAS` como texto ASCII con lineas numeradas.
- Mantener lineas razonablemente cortas.
- Preferir arrays simples y variables cortas.
- Evitar pares como `CD1$` y `CD2$`: en MSX BASIC pueden pisarse por la significancia corta de nombres. Usar `D1$` y `D2$`, `Z1$` y `Z2$`, etc.
- Evitar saltar fuera de bucles `FOR` con `GOTO`.
- Si se genera una version optimizada/release del BASIC, conservar lineas destino de `GOTO`, `GOSUB` y todos los destinos de listas `ON ... GOSUB`.
- No cargar fichas de todas las ciudades en RAM.
- No leer `IMGxxx.SC5` desde disco en cada repintado del menu principal; usar la cache VRAM de pagina 1.
- Tras usar `SET PAGE 0,1`, restaurar siempre `SET PAGE 0,0` antes de volver al flujo normal.
- No introducir dependencias externas.

## Siguientes Pasos Recomendados

1. Probar `CARMEN5.BAS` en MSX2 BASIC o emulador con los `.DAT` y `.SC5` en el mismo disco.
2. Ajustar cualquier incompatibilidad real de `LINE INPUT #`.
3. Mejorar las pistas de ciudad para que sean menos directas.
4. Optimizar el `.BAS` para ocupar menos RAM sin romper legibilidad minima.
5. Probar en maquina real la sensacion de teclado de la rutina de menus.
