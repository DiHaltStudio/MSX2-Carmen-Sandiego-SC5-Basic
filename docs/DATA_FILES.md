# Ficheros de datos

Todos los `.DAT` de `src/` son ASCII con finales de linea CR/LF. No deben
contener acentos ni caracteres fuera de ASCII. El juego los lee desde Disk
BASIC para mantener baja la ocupacion de RAM.

## CITIES.DAT

Indice de ciudades:

```text
NUM_CIUDADES
CIUDAD_1
CIUDAD_2
...
```

Hay 50 entradas. El numero de ciudad es su posicion y enlaza `CITYxxx.DAT`,
`IMGxxx.SC5`, `CITYPOS.DAT` y la lista interna de fuentes fotograficas.

## CITYxxx.DAT

Cada ciudad tiene exactamente 10 lineas:

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

Solo se carga la ficha de la ciudad necesaria. Las descripciones deben caber
en el ancho de texto del juego.

## CITYPOS.DAT

Empieza con el numero de ciudades y contiene una linea CSV por ciudad:

```text
NOMBRE,LABEL_X,LABEL_Y,POINT_X,POINT_Y
```

Debe conservar el orden de `CITIES.DAT`. Vease `docs/CITYPOS.md` para el
sistema de coordenadas.

## SUSPECT.DAT

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

Hay 15 sospechosos. Cada uno ocupa una linea de nombre y cinco codigos. Al
arrancar solo se guarda el nombre; los codigos se vuelven a leer al calcular
una orden o preparar las pistas del objetivo.

## ATTRS.DAT

Reune las cinco categorias que antiguamente podrian haberse separado en varios
ficheros:

```text
5
NUM_VALORES_SEXO
VALORES_SEXO...
NUM_VALORES_PELO
VALORES_PELO...
NUM_VALORES_VEHICULO
VALORES_VEHICULO...
NUM_VALORES_RASGO
VALORES_RASGO...
NUM_VALORES_AFICION
VALORES_AFICION...
```

Los codigos de `SUSPECT.DAT` empiezan en 1 y seleccionan una entrada dentro de
la categoria correspondiente. El valor 0 se reserva en BASIC para indicar que
el jugador no ha introducido ese filtro.

## Sintaxis Disk BASIC

La lectura usada por el proyecto es:

```basic
OPEN "CITY001.DAT" FOR INPUT AS #1
LINE INPUT #1,A$
CLOSE #1
```

No se usa la forma `OPEN "I",#1,"CITY001.DAT"`, que no es la sintaxis elegida
para MSX Disk BASIC en este proyecto.
