; FONT6.ASM - Texto 6x6 para SCREEN 5 mediante comandos HMMM del V9938.
; Ensamblador: Sjasm clasico (probado con Sjasm 0.42c, compatible con 0.39).
;
; Entrada USR desde MSX BASIC:
;   A  = 3 (tipo cadena)
;   DE = descriptor de cadena
;   texto = CHR$(X)+CHR$(Y)+texto
;   escena = CHR$(255)+CHR$(1)+CHR$(ID)+CHR$(X)+CHR$(Y)
;   borrar = CHR$(255)+CHR$(2)+CHR$(X)+CHR$(Y)+CHR$(W)+CHR$(H)
;   mover  = CHR$(255)+CHR$(3)+CHR$(ID)+CHR$(NX)+CHR$(NY)
;            +CHR$(OX)+CHR$(OY)+CHR$(W)+CHR$(H)
;   verde  = CHR$(255)+CHR$(5)+CHR$(X)+CHR$(Y)+texto
;
; La fuente esta en VRAM pagina 3, coordenada local (0,152), y contiene
; ASCII 32..93 en celdas 6x6: 42 glifos en la primera fila y 20 en la
; segunda. ASCII 92 representa ENE. Las minusculas pasan a mayusculas.
;
; Salida: los dos primeros bytes de la cadena quedan en X=0 e Y igual a
; la siguiente linea. Los caracteres que no caben saltan a X=0,Y=Y+6.

        byte    0FEh
        word    START, CODE_END-1, START

        org     0D800h

VDP_CTRL        equ     099h
VDP_INDIRECT    equ     09Bh

START:
        cp      2
        jr      nz,CHECK_STRING
        ld      e,0
        jp      COPY_CITY
CHECK_STRING:
        cp      3
        ret     nz
        push    de
        pop     ix
        ld      b,(ix+0)
        ld      l,(ix+1)
        ld      h,(ix+2)
        ld      a,b
        cp      5
        jr      c,PREPARE_TEXT
        ld      a,(hl)
        cp      255
        jr      nz,PREPARE_TEXT
        inc     hl
        ld      a,(hl)
        cp      1
        jp      z,DRAW_SCENE_PACKET
        cp      2
        jp      z,CLEAR_RECT_PACKET
        cp      3
        jp      z,REPLACE_SCENE_PACKET
        cp      5
        jp      z,GREEN_TEXT_PACKET
        ret

PREPARE_TEXT:
        ld      a,b
        cp      2
        ret     c
        sub     2
        push    af
        ld      de,920
        ld      (FONT_ROW1),de
        ld      de,926
        ld      (FONT_ROW2),de
        ld      a,0D0h          ; HMMM opaco
        ld      (CMD_COMMAND),a
        xor     a
        ld      (CMD_ARGUMENT),a
        pop     af
        jr      PREPARE_TEXT_COMMON

GREEN_TEXT_PACKET:
        ld      a,b
        cp      5
        ret     c
        inc     hl              ; X, despues del comando 5
        sub     4               ; 255, comando, X, Y
        push    af
        ld      de,932
        ld      (FONT_ROW1),de
        ld      de,938
        ld      (FONT_ROW2),de
        ld      a,0D0h          ; HMMM opaco (prueba de rotulos del mapa)
        ld      (CMD_COMMAND),a
        xor     a
        ld      (CMD_ARGUMENT),a
        pop     af

PREPARE_TEXT_COMMON:
        ld      (REMAIN),a
        ld      (HEADER),hl
        ld      a,(hl)
        ld      (DEST_X),a
        inc     hl
        ld      a,(hl)
        ld      (DEST_Y),a
        inc     hl
        ld      (TEXT_PTR),hl

CHAR_LOOP:
        ld      a,(REMAIN)
        or      a
        jr      z,TEXT_DONE

        ld      a,(DEST_X)
        cp      251             ; un glifo de 6 px debe terminar en X<=255
        jr      c,CHECK_Y
        xor     a
        ld      (DEST_X),a
        ld      a,(DEST_Y)
        add     a,6
        ld      (DEST_Y),a

CHECK_Y:
        ld      a,(DEST_Y)
        cp      207             ; pantalla visible 0..211
        jr      nc,TEXT_DONE

        ld      hl,(TEXT_PTR)
        ld      a,(hl)
        inc     hl
        ld      (TEXT_PTR),hl
        ld      hl,REMAIN
        dec     (hl)

        cp      97
        jr      c,VALIDATE
        cp      123
        jr      nc,VALIDATE
        sub     32
VALIDATE:
        cp      32
        jr      c,USE_SPACE
        cp      94
        jr      c,GLYPH_INDEX
USE_SPACE:
        ld      a,32
GLYPH_INDEX:
        sub     32
        cp      42
        jr      c,FIRST_ROW
        sub     42
        ld      hl,(FONT_ROW2)
        jr      SET_SOURCE
FIRST_ROW:
        ld      hl,(FONT_ROW1)
SET_SOURCE:
        ld      (CMD_SY),hl
        ld      e,a
        ld      d,0
        ld      h,d
        ld      l,e
        add     hl,hl
        add     hl,de
        add     hl,hl           ; indice * 6
        ld      (CMD_SX),hl

        ld      a,(DEST_X)
        ld      (CMD_DX),a
        xor     a
        ld      (CMD_DX+1),a
        ld      a,(DEST_Y)
        ld      (CMD_DY),a
        xor     a
        ld      (CMD_DY+1),a
        call    START_HMMM

        ld      a,(DEST_X)
        add     a,6
        ld      (DEST_X),a
        jr      CHAR_LOOP

TEXT_DONE:
        call    WAIT_VDP
        ld      hl,(HEADER)
        xor     a
        ld      (hl),a
        inc     hl
        ld      a,(DEST_Y)
        add     a,6
        ld      (hl),a
        ret

COPY_CITY:
        ; Cache -> pantalla.
        ld      a,0D0h          ; la cache siempre usa HMMM opaco
        ld      (CMD_COMMAND),a
        xor     a
        ld      (CMD_ARGUMENT),a
        ld      hl,156
        ld      (CMD_SX),hl
        ld      hl,330           ; pagina 1, Y local 74: 256+74
        ld      (CMD_SY),hl
        ld      hl,150
        ld      (CMD_DX),hl
        ld      hl,54
        ld      (CMD_DY),hl
        ld      hl,100
        ld      (CMD_NX),hl
        ld      (CMD_NY),hl
        call    START_HMMM
        call    WAIT_VDP
        ld      hl,6             ; texto vuelve a usar bloques 6x6
        ld      (CMD_NX),hl
        ld      (CMD_NY),hl
        ret

DRAW_SCENE_PACKET:
        inc     hl              ; ID
        ld      a,(hl)
        cp      VRAM_SCENE_COUNT
        ret     nc
        ld      (SCENE_ID),a
        inc     hl              ; DX
        ld      a,(hl)
        ld      (SCENE_DX),a
        inc     hl              ; DY
        ld      a,(hl)
        ld      (SCENE_DY),a
        call    LOAD_SCENE_COMMAND
        call    WAIT_VBLANK
        call    START_HMMM
        call    WAIT_VDP
        jp      RESTORE_TEXT_COMMAND

LOAD_SCENE_COMMAND:
        ld      a,(SCENE_DX)
        ld      (CMD_DX),a
        xor     a
        ld      (CMD_DX+1),a
        ld      a,(SCENE_DY)
        ld      (CMD_DY),a
        xor     a
        ld      (CMD_DY+1),a
        ld      a,(SCENE_ID)
        ld      l,a
        ld      h,0
        add     hl,hl
        add     hl,hl
        add     hl,hl           ; ID * 8
        ld      de,VRAM_SCENE_TABLE
        add     hl,de
        ld      e,(hl)
        inc     hl
        ld      d,(hl)
        inc     hl
        ld      (CMD_SX),de
        ld      e,(hl)
        inc     hl
        ld      d,(hl)
        inc     hl
        ld      (CMD_SY),de
        ld      e,(hl)
        inc     hl
        ld      d,(hl)
        inc     hl
        ld      (CMD_NX),de
        ld      e,(hl)
        inc     hl
        ld      d,(hl)
        ld      (CMD_NY),de
        ld      a,0D0h          ; HMMM
        ld      (CMD_COMMAND),a
        ret

CLEAR_RECT_PACKET:
        ld      a,b
        cp      6
        ret     c
        inc     hl              ; DX
        ld      a,(hl)
        ld      (CMD_DX),a
        xor     a
        ld      (CMD_DX+1),a
        inc     hl              ; DY
        ld      a,(hl)
        ld      (CMD_DY),a
        xor     a
        ld      (CMD_DY+1),a
        inc     hl              ; NX
        ld      a,(hl)
        ld      (CMD_NX),a
        xor     a
        ld      (CMD_NX+1),a
        inc     hl              ; NY
        ld      a,(hl)
        ld      (CMD_NY),a
        xor     a
        ld      (CMD_NY+1),a
        ld      (CMD_COLOR),a   ; negro
        ld      a,0C0h          ; HMMV
        ld      (CMD_COMMAND),a
        call    WAIT_VBLANK
        call    START_HMMM
        call    WAIT_VDP
        jp      RESTORE_TEXT_COMMAND

REPLACE_SCENE_PACKET:
        ld      a,b
        cp      9
        ret     c
        inc     hl              ; ID del nuevo frame
        ld      a,(hl)
        cp      VRAM_SCENE_COUNT
        ret     nc
        ld      (SCENE_ID),a
        inc     hl              ; nuevo DX
        ld      a,(hl)
        ld      (SCENE_DX),a
        inc     hl              ; nuevo DY
        ld      a,(hl)
        ld      (SCENE_DY),a
        inc     hl              ; anterior DX
        ld      a,(hl)
        ld      (CMD_DX),a
        xor     a
        ld      (CMD_DX+1),a
        inc     hl              ; anterior DY
        ld      a,(hl)
        ld      (CMD_DY),a
        xor     a
        ld      (CMD_DY+1),a
        inc     hl              ; ancho a borrar
        ld      a,(hl)
        ld      (CMD_NX),a
        xor     a
        ld      (CMD_NX+1),a
        inc     hl              ; alto a borrar
        ld      a,(hl)
        ld      (CMD_NY),a
        xor     a
        ld      (CMD_NY+1),a
        ld      (CMD_COLOR),a   ; negro
        ld      a,0C0h          ; HMMV
        ld      (CMD_COMMAND),a

        call    WAIT_VBLANK
        call    START_HMMM
        call    WAIT_VDP
        call    LOAD_SCENE_COMMAND
        call    START_HMMM
        call    WAIT_VDP

RESTORE_TEXT_COMMAND:
        ld      hl,6
        ld      (CMD_NX),hl
        ld      (CMD_NY),hl
        ld      a,0D0h
        ld      (CMD_COMMAND),a
        ret

WAIT_VBLANK:
        ei                      ; la interrupcion periodica del VDP es el VBlank
        halt
        ret

START_HMMM:
        call    WAIT_VDP
        di
        ld      a,32
        out     (VDP_CTRL),a
        ld      a,091h          ; R#17=32, autoincremento activo
        out     (VDP_CTRL),a
        ld      hl,COMMAND
        ld      bc,15*256+VDP_INDIRECT
        otir
        ei
        ret

WAIT_VDP:
        di
        ld      a,2
        out     (VDP_CTRL),a
        ld      a,08Fh          ; seleccionar S#2 mediante R#15
        out     (VDP_CTRL),a
        in      a,(VDP_CTRL)
        push    af
        xor     a
        out     (VDP_CTRL),a
        ld      a,08Fh          ; restaurar S#0
        out     (VDP_CTRL),a
        pop     af
        ei
        and     1               ; CE=1 mientras el comando sigue activo
        jr      nz,WAIT_VDP
        ret

COMMAND:
CMD_SX: word    0               ; R#32-33 SX
CMD_SY: word    920             ; R#34-35 SY global (pagina 3)
CMD_DX: word    0               ; R#36-37 DX, siempre pagina 0
CMD_DY: word    0               ; R#38-39 DY
CMD_NX: word    6               ; R#40-41 NX
CMD_NY: word    6               ; R#42-43 NY
CMD_COLOR:
        byte    0               ; R#44 color (no usado por HMMM)
CMD_ARGUMENT:
        byte    0               ; R#45 argumento, copia IMP
CMD_COMMAND:
        byte    0D0h            ; R#46 HMMM/HMMV

TEXT_PTR:       word    0
HEADER:         word    0
REMAIN:         byte    0
DEST_X:         byte    0
DEST_Y:         byte    0
FONT_ROW1:      word    920
FONT_ROW2:      word    926
SCENE_ID:       byte    0
SCENE_DX:       byte    0
SCENE_DY:       byte    0

        include "VRAM_SCENES.INC"

CODE_END:
