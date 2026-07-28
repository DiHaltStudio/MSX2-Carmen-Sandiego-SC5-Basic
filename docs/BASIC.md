# Estructura de CARMEN5.BAS

`src/CARMEN5.BAS` es la fuente ASCII principal para MSX BASIC 2.0. Usa
finales CR/LF, lineas numeradas y nombres de variable cortos por la
significancia limitada de los identificadores de MSX BASIC.

`src/autoexec.bas` es un lanzador tokenizado independiente que ejecuta
`CARMEN5.BAS` al arrancar el disco.

## Arranque y memoria

Las lineas 10..100:

1. Reservan 5000 bytes para cadenas y fijan `CLEAR 5000,&HD7FF`. Esto deja
   1000 bytes adicionales al area general de BASIC, necesarios para variables
   temporales que se crean durante la lectura del mapa.
2. Entran en SCREEN 5 y abren `GRP:` como fichero 2.
3. Deshabilitan sprites hardware con el bit SPD de R#8.
4. Cargan `FONT6.BIN` en `&HD800` y asignan `DEFUSR`.
5. Muestran `OPENING.SC5`.
6. Cargan los bancos VRAM y `GAMEPAL.SC5`.
7. Leen los indices de ciudades y sospechosos.
8. Muestran la introduccion y generan el primer caso.

Disk BASIC puede mantener como maximo dos ficheros abiertos (`MAXFILES=2`).
El manejador de error empieza en 3170, restaura la pagina activa 0 y cierra
ambos canales antes de presentar el error.

## Mapa de rutinas

| Lineas | Funcion |
|---:|---|
| 10..280 | Arranque y menu principal |
| 290..540 | Investigar |
| 550..700 | Viajar y mostrar mapa |
| 710..780 | Lista de sospechosos |
| 790..950 | Filtros y emision de orden |
| 960..1190 | Estado del caso y pausa inferior |
| 1200..1290 | Arrestar o abandonar |
| 1300..1470 | Carga de indices iniciales |
| 1480..1550 | Carga de ciudad y cache de imagen |
| 1560..1720 | Generacion de caso |
| 1730..1860 | Generacion de vuelos |
| 1870..1990 | Lectura de `CITYxxx.DAT` |
| 2000..2170 | Eleccion de filtro desde `ATTRS.DAT` |
| 2180..2450 | Calculo de orden y comparacion |
| 2460..2700 | Pistas y atributos del objetivo |
| 2710..2910 | Pausas, tiempo e introduccion |
| 2920..3210 | Caso resuelto, derrotas y errores |
| 3220..3400 | Menu generico con cursor |
| 3410..3520 | Imagen y cache de ciudad |
| 3530..3650 | Apertura, bancos y paleta |
| 3660..3700 | Texto blanco y verde 6x6 |
| 3710..4180 | Movimiento y animaciones generales |
| 4190..4390 | Mapa y rotulos de viaje |
| 4400..4570 | Ciudad final, captura y derrota |
| 4580..4650 | Musica de apertura |

Toda entrada llamada con `GOSUB` comienza en una linea `REM`. La pausa inferior
usa la entrada 1180 y ejecuta su cuerpo en 1190.

## Renumerado

El listado se entrega con 465 lineas consecutivas, desde 10 hasta 4650 y con
incrementos de 10. Para repetir el equivalente a `RENUM` sobre la fuente ASCII:

```bash
python3 tools/renumber_basic.py src/CARMEN5.BAS
```

La utilidad conserva CR/LF, cadenas y comentarios, y actualiza destinos de
`GOTO`, `GOSUB`, `ON ... GOTO/GOSUB`, `THEN`, `ELSE`, `RESTORE`, `RESUME`,
`RETURN` y `RUN`. Falla si encuentra numeracion duplicada, desordenada o un
destino inexistente.

## Variables principales

| Variable | Uso |
|---|---|
| `CP` | Indice de ciudad actual |
| `R%(1..RL)` | Ruta correcta del caso |
| `ST` | Posicion alcanzada en la ruta |
| `TH` | Sospechoso objetivo |
| `CS` | Indice de Carmen Sandiego |
| `WA` | Sospechoso indicado por la orden, o 0 |
| `AR` | Detenciones conseguidas |
| `TM` / `TL` | Tiempo consumido y limite |
| `IC` | Ciudad cuya imagen esta en la cache VRAM |
| `FA` | Primera pista pendiente tras un viaje correcto |
| `O$()`, `MN`, `MY`, `OP` | Opciones y estado del menu generico |
| `TX`, `TY`, `T$` | Posicion y cadena para el texto 6x6 |
| `AF`, `AN`, `AD`, `AJ` | Primer frame, numero de frames, ticks y avance |

## Tiempo y casos

Cada caso usa una ruta de cinco ciudades sin repeticiones. El limite se calcula
al generarlo:

```basic
TL=72-(AR*4+2)
```

Investigar suma 2 horas, viajar 6, calcular una orden 1 y arrestar en una
ciudad incorrecta 2. `NO VIAJAR` y un intento sin orden no consumen horas. El
juego termina al superar el limite (`TM>TL`) o tras una orden contra la persona
equivocada. Siete detenciones correctas completan la partida. Carmen Sandiego
se excluye del sorteo de los seis primeros casos y es siempre el objetivo del
septimo. Tras la pantalla de victoria y su pausa, `RUN` reinicia el programa
desde la apertura y limpia todo el estado de la partida anterior. Una orden
contra la persona equivocada o agotar el tiempo hacen el mismo reinicio despues
de mostrar su derrota y esperar una tecla.

## Orden y datos en disco

Al arrancar solo se conservan en RAM los nombres de ciudades y sospechosos.
Las fichas `CITYxxx.DAT`, las categorias de `ATTRS.DAT`, las fichas completas
de `SUSPECT.DAT` y las coordenadas de `CITYPOS.DAT` se leen cuando hacen falta.
Antes de recorrer `CITYPOS.DAT`, la rutina del mapa ejecuta `FRE("")` para
compactar el area de cadenas y recuperar temporales ya abandonados.

La orden acepta filtros parciales. Se emite solo cuando exactamente un
sospechoso no detenido coincide con todos los filtros introducidos. La lista
de sospechosos muestra `*` junto a cada detenido.

## Graficos

- `3410` copia la imagen de ciudad cacheada con `Z=USR(0)`.
- `3470` carga un nuevo `IMGxxx.SC5` en la pagina activa 1.
- `3660` dibuja texto con el atlas blanco.
- `3690` dibuja destinos del mapa con el atlas verde y HMMM opaco.
- `4190` copia el mapa y dibuja la ruta y los cuatro nombres.
- `3710` y `3770..4570` controlan las animaciones descritas en
  `docs/VRAM_SCENES.md`.

Los sprites permanecen deshabilitados durante todo el juego.

## Sonido

La apertura llama a la rutina 4580, que reproduce la melodia de introduccion
con varias cadenas MML de `PLAY`. Las animaciones iniciales, la captura correcta
y la derrota tienen efectos breves en sus propias rutinas. Todo usa el PSG y
no carga audio digital; `res/carmensandiegointrodos.wav` es solo una referencia
de trabajo y no se copia al disco.
