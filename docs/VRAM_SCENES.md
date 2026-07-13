# Catalogo de escenas en VRAM

Los bancos `VRAM1.SC5`, `VRAM2.SC5` y `VRAM3.SC5` se cargan en las paginas 1,
2 y 3 de SCREEN 5. El fichero `tools/VRAM_SCENES.INC` cataloga 55 rectangulos
de origen preparados para futuras copias HMMM.

Cada registro contiene:

```text
SX, SY_GLOBAL, NX, NY
```

- `SX`: X de origen.
- `SY_GLOBAL`: Y de origen incluyendo la pagina de VRAM.
- `NX`: ancho.
- `NY`: alto.

Todos los valores `SX` y `NX` son pares. Cuando un dibujo empieza en una X
impar o tiene ancho impar, el rectangulo incluye una columna negra adicional.
Algunos fotogramas muy juntos comparten una columna de margen; esto es
intencionado para mantener la alineacion requerida por SCREEN 5.

## Conversion de coordenadas

| Banco | Pagina | Suma para Y global |
|---|---:|---:|
| `VRAM1` | 1 | `Y local + 256` |
| `VRAM2` | 2 | `Y local + 512` |
| `VRAM3` | 3 | `Y local + 768` |

Ejemplo: el primer fotograma del ladron azul en VRAM3 empieza en `(0,0)`
local. Su origen HMMM es `(0,768)`.

## Grupos clasificados

| Grupo | Identificadores | Fotogramas | Banco |
|---|---|---:|---|
| Cabeza del ladron verde | `SC_V1_CABEZA_01..04` | 4 | VRAM1 |
| Cuchillo | `SC_V1_CUCHILLO_01` | 1 | VRAM1 |
| Ladron verde corriendo | `SC_V1_LADRON_VERDE_CORRE_01..08` | 8 | VRAM1 |
| Hacha | `SC_V1_HACHA_01..03`, `SC_HACHA_04` | 4 | VRAM1/VRAM3 |
| Ladron verde mimo | `SC_V1_LADRON_VERDE_MIMO_01..05` | 5 | VRAM1 |
| Pistola | `SC_V1_PISTOLA_01..03` | 3 | VRAM1 |
| Captura | `SC_V2_CAPTURA_01..06` | 6 | VRAM2 |
| Grupo de policias | `SC_V2_POLICIAS_01..05` | 5 | VRAM2 |
| Detective marron | `SC_V2_DETECTIVE_MARRON_01..08` | 8 | VRAM2 |
| Ladron azul agachado | `SC_LADRON_AZUL_01..10` | 10 | VRAM2/VRAM3 |

Los nombres describen visualmente las secuencias; todavia no fijan su funcion
argumental ni el orden temporal definitivo. Los destinos tampoco forman parte
de la tabla y se decidiran cuando se implementen las animaciones.

## Mapa en VRAM3

Las cuatro escenas iniciales de `VRAM3.bmp` ocupan Y local 0..44. El mapa del
mundo se cataloga aparte como `SC_V3_MAPA_MUNDO`: origen global `(0,813)`,
tamano 256x107. La fuente permanece en `(0,920)` y no forma parte de la tabla.

## Cache de ciudad y escenas cercanas

La cache de la miniimagen ocupa X=156..255 y Y local 74..173 de la pagina 1.
El rectangulo geometrico alcanza los margenes inferiores de
`SC_V1_LADRON_VERDE_CORRE_04` y `05`, pero en el BMP actual todos los pixeles
de esa interseccion son color 0. Por tanto, sus origenes manuales se conservan:

- `SC_V1_LADRON_VERDE_CORRE_04`: `(132,43)`, Y global 299.
- `SC_V1_LADRON_VERDE_CORRE_05`: `(176,32)`, Y global 288.

La cache solo sustituye fondo negro y no destruye pixeles visibles de esos
frames. Los cinco frames `MIMO`, incluidos `_04` y `_05`, quedan fuera del
rectangulo de cache.

## Uso futuro desde ensamblador

La tabla usa registros de 8 bytes. Un identificador permite localizar sus
datos con:

```text
VRAM_SCENE_TABLE + identificador * VRAM_SCENE_RECORD_SIZE
```

El orden de cada registro coincide con los campos de origen y tamano que se
necesitaran para preparar un comando HMMM; las coordenadas de destino se
aportaran en el momento de la copia.

## Primera animacion usada

La rutina BASIC `2700` utiliza dos grupos en la pantalla inicial, ambos sobre
Y=100 y sin clipping:

1. `SC_V2_DETECTIVE_MARRON_01..08` cruza de izquierda a derecha.
2. Espera 90 ticks, aproximadamente entre 1,5 y 1,8 segundos segun 60/50 Hz.
3. `SC_V2_POLICIAS_01..05` recorre la misma trayectoria.

Cada grupo mantiene su propio intervalo `AD`. Los dos grupos actuales cambian
de fotograma cada 3 ticks y avanzan 4 pixeles. Una unica llamada de codigo
maquina espera el VBlank, borra en negro la posicion anterior mediante HMMV y
dibuja la siguiente mediante HMMM, reduciendo el parpadeo entre operaciones.

## Animacion de la primera pista tras un viaje correcto

Al llegar a la siguiente ciudad correcta no se muestra ningun mensaje de
confirmacion adicional. La primera opcion valida elegida en `INVESTIGAR`
reproduce aleatoriamente uno de estos grupos en Y=154 y despues muestra la
pista normalmente:

- `SC_V1_CABEZA_01..04`: fija en X=90, repite dos veces la secuencia y usa
  5 ticks por frame.
- `SC_V1_LADRON_VERDE_CORRE_01..08`: recorre la pantalla de derecha a
  izquierda, con 1 tick por frame.
- `SC_V1_LADRON_VERDE_MIMO_01..05`: recorre la pantalla de izquierda a
  derecha, con 1 tick por frame.

La animacion solo se consume al seleccionar una pista valida. Viajar de nuevo
antes de investigar sustituye el estado de llegada anterior.
