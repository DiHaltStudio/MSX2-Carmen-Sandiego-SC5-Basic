# Coordenadas de ciudades en el mapa

`src/CITYPOS.DAT` contiene las posiciones editables de las 50 ciudades. Debe
mantener exactamente el mismo orden que `src/CITIES.DAT`.

Formato:

```text
NUM_CIUDADES
NOMBRE,LABEL_X,LABEL_Y,POINT_X,POINT_Y
...
```

- `LABEL_X,LABEL_Y`: esquina superior izquierda donde empieza el texto 6x6.
- `POINT_X,POINT_Y`: punto geografico usado como extremo de la linea de viaje.
- Todas las Y son locales al mapa. BASIC suma 40 al dibujar en pantalla.
- Un rotulo ocupa `LEN(NOMBRE)*6` pixeles de ancho y 6 de alto.
- El mapa mide 256x107, por lo que las coordenadas utiles son X=0..255 e
  Y=0..106. Conviene mantener `LABEL_Y` entre 0 y 101.

La primera tabla es una aproximacion geografica. Para ajustar visualmente un
nombre sin cambiar el recorrido de la linea, modifica solo `LABEL_X` y
`LABEL_Y`. Para mover la posicion geografica, modifica `POINT_X` y `POINT_Y`.

Para no agotar la RAM de Disk BASIC, el juego no conserva las 50 posiciones:
escanea el fichero al viajar y guarda temporalmente solo la ciudad de origen y
las tres opciones visibles.

Durante la transicion `HAS VIAJADO A`, el juego muestra el nombre de la ciudad
de origen y los nombres de las tres opciones que estaban disponibles. La linea
de color 7 une el punto de origen con la opcion elegida. El origen usa la
fuente blanca opaca; las tres opciones usan la fuente verde mediante LMMM con
color 0 transparente.
