; VRAM_SCENES.INC - Origenes HMMM de las escenas de animacion.
;
; Cada registro contiene cuatro WORD, en este orden:
;   SX, SY_GLOBAL, NX, NY
;
; SX y NX son siempre pares para SCREEN 5. SY_GLOBAL ya incluye la pagina:
;   pagina 1 = Y local + 256
;   pagina 2 = Y local + 512
;   pagina 3 = Y local + 768
;
; Los identificadores son indices de registro (base 0). Para obtener la
; direccion: VRAM_SCENE_TABLE + identificador * VRAM_SCENE_RECORD_SIZE.

VRAM_SCENE_RECORD_SIZE       equ 8
VRAM_SCENE_COUNT             equ 55

SC_V1_CABEZA_01              equ 0
SC_V1_CABEZA_02              equ 1
SC_V1_CABEZA_03              equ 2
SC_V1_CABEZA_04              equ 3
SC_V1_CUCHILLO_01            equ 4
SC_V1_LADRON_VERDE_CORRE_01  equ 5
SC_V1_LADRON_VERDE_CORRE_02  equ 6
SC_V1_LADRON_VERDE_CORRE_03  equ 7
SC_V1_LADRON_VERDE_CORRE_04  equ 8
SC_V1_LADRON_VERDE_CORRE_05  equ 9
SC_V1_LADRON_VERDE_CORRE_06  equ 10
SC_V1_LADRON_VERDE_CORRE_07  equ 11
SC_V1_LADRON_VERDE_CORRE_08  equ 12
SC_V1_HACHA_01               equ 13
SC_V1_HACHA_02               equ 14
SC_V1_HACHA_03               equ 15
SC_V1_LADRON_VERDE_MIMO_01   equ 16
SC_V1_LADRON_VERDE_MIMO_02   equ 17
SC_V1_LADRON_VERDE_MIMO_03   equ 18
SC_V1_LADRON_VERDE_MIMO_04   equ 19
SC_V1_LADRON_VERDE_MIMO_05   equ 20
SC_V1_PISTOLA_01             equ 21
SC_V1_PISTOLA_02             equ 22
SC_V1_PISTOLA_03             equ 23
SC_V2_CAPTURA_01             equ 24
SC_V2_CAPTURA_02             equ 25
SC_V2_CAPTURA_03             equ 26
SC_V2_CAPTURA_04             equ 27
SC_V2_CAPTURA_05             equ 28
SC_V2_CAPTURA_06             equ 29
SC_V2_POLICIAS_01            equ 30
SC_V2_POLICIAS_02            equ 31
SC_V2_POLICIAS_03            equ 32
SC_V2_POLICIAS_04            equ 33
SC_V2_POLICIAS_05            equ 34
SC_V2_DETECTIVE_MARRON_01    equ 35
SC_V2_DETECTIVE_MARRON_02    equ 36
SC_V2_DETECTIVE_MARRON_03    equ 37
SC_V2_DETECTIVE_MARRON_04    equ 38
SC_V2_DETECTIVE_MARRON_05    equ 39
SC_V2_DETECTIVE_MARRON_06    equ 40
SC_V2_DETECTIVE_MARRON_07    equ 41
SC_V2_DETECTIVE_MARRON_08    equ 42
SC_LADRON_AZUL_01            equ 43
SC_LADRON_AZUL_02            equ 44
SC_LADRON_AZUL_03            equ 45
SC_LADRON_AZUL_04            equ 46
SC_LADRON_AZUL_05            equ 47
SC_LADRON_AZUL_06            equ 48
SC_LADRON_AZUL_07            equ 49
SC_LADRON_AZUL_08            equ 50
SC_LADRON_AZUL_09            equ 51
SC_LADRON_AZUL_10            equ 52
SC_V1_HACHA_04               equ 53
SC_V3_MAPA_MUNDO             equ 54

VRAM_SCENE_TABLE:
        ; VRAM1: cabezas, cuchillo y carrera del ladron verde.
        word 0,256,42,32       ; 00 SC_V1_CABEZA_01
        word 42,256,42,32      ; 01 SC_V1_CABEZA_02
        word 84,256,42,32      ; 02 SC_V1_CABEZA_03
        word 126,256,42,32     ; 03 SC_V1_CABEZA_04
        word 188,256,60,16     ; 04 SC_V1_CUCHILLO_01
        word 0,288,46,41       ; 05 SC_V1_LADRON_VERDE_CORRE_01
        word 46,288,46,41      ; 06 SC_V1_LADRON_VERDE_CORRE_02
        word 92,288,46,41      ; 07 SC_V1_LADRON_VERDE_CORRE_03
        word 92+46,288,46,41     ; 08 SC_V1_LADRON_VERDE_CORRE_04
        word 92+46+46,288,46,41     ; 09 SC_V1_LADRON_VERDE_CORRE_05
        word 0,329,46,41       ; 10 SC_V1_LADRON_VERDE_CORRE_06
        word 46,329,46,41      ; 11 SC_V1_LADRON_VERDE_CORRE_07
        word 92,329,46,41      ; 12 SC_V1_LADRON_VERDE_CORRE_08

        ; VRAM1: armas y mimo del ladron verde.
        word 0,371,44,44       ; 13 SC_V1_HACHA_01
        word 45,371,44,44      ; 14 SC_V1_HACHA_02
        word 90,371,44,44      ; 15 SC_V1_HACHA_03
        word 0,415,46,42       ; 16 SC_V1_LADRON_VERDE_MIMO_01
        word 46,415,46,42      ; 17 SC_V1_LADRON_VERDE_MIMO_02
        word 92,415,46,42      ; 18 SC_V1_LADRON_VERDE_MIMO_03
        word 0,457,46,42       ; 19 SC_V1_LADRON_VERDE_MIMO_04
        word 46,457,46,42      ; 20 SC_V1_LADRON_VERDE_MIMO_05
        word 94,457,52,29      ; 21 SC_V1_PISTOLA_01
        word 94,484,52,29      ; 22 SC_V1_PISTOLA_02
        word 146,460,52,29     ; 23 SC_V1_PISTOLA_03

        ; VRAM2: captura (6 fotogramas) y grupo de policias (5).
        word 0,512,48,49       ; 24 SC_V2_CAPTURA_01
        word 48,512,48,49      ; 25 SC_V2_CAPTURA_02
        word 96,512,48,49      ; 26 SC_V2_CAPTURA_03
        word 144,512,48,49     ; 27 SC_V2_CAPTURA_04
        word 192,512,48,49     ; 28 SC_V2_CAPTURA_05
        word 0,561,50,50       ; 29 SC_V2_CAPTURA_06
        word 48,561,50,50      ; 30 SC_V2_POLICIAS_01
        word 98,561,50,50      ; 31 SC_V2_POLICIAS_02
        word 148,561,50,50     ; 32 SC_V2_POLICIAS_03
        word 198,561,50,50     ; 33 SC_V2_POLICIAS_04
        word 0,611,50,49       ; 34 SC_V2_POLICIAS_05

        ; VRAM2: detective marron (8 fotogramas).
        word 50,611,52,49      ; 35 SC_V2_DETECTIVE_MARRON_01
        word 100,611,52,49     ; 36 SC_V2_DETECTIVE_MARRON_02
        word 152,611,50,49     ; 37 SC_V2_DETECTIVE_MARRON_03
        word 202,611,52,49     ; 38 SC_V2_DETECTIVE_MARRON_04
        word 0,660,50,50       ; 39 SC_V2_DETECTIVE_MARRON_05
        word 50,660,50,50      ; 40 SC_V2_DETECTIVE_MARRON_06
        word 100,660,50,50     ; 41 SC_V2_DETECTIVE_MARRON_07
        word 150,660,40,50     ; 42 SC_V2_DETECTIVE_MARRON_08

        ; Ladron azul: 7 fotogramas en VRAM2 y 3 en VRAM3.
        word 190,660,42,50     ; 43 SC_LADRON_AZUL_01
        word 0,710,40,45       ; 44 SC_LADRON_AZUL_02
        word 38,710,40,45      ; 45 SC_LADRON_AZUL_03
        word 78,710,40,45      ; 46 SC_LADRON_AZUL_04
        word 116,710,40,45     ; 47 SC_LADRON_AZUL_05
        word 156,710,40,45     ; 48 SC_LADRON_AZUL_06
        word 194,710,40,45     ; 49 SC_LADRON_AZUL_07
        word 0,768,40,45       ; 50 SC_LADRON_AZUL_08
        word 38,768,40,45      ; 51 SC_LADRON_AZUL_09
        word 78,768,40,45      ; 52 SC_LADRON_AZUL_10
        word 120,768,44,44     ; 53 SC_V1_HACHA_04

        ; VRAM3: mapa del mundo, Y local 45..151.
        word 0,813,256,107      ; 54 SC_V3_MAPA_MUNDO

VRAM_SCENE_TABLE_END:
