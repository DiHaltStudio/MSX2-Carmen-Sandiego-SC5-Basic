; FONT6.ASM - Texto 6x6 para SCREEN 5 mediante comandos HMMM del V9938.
; Ensamblador: Sjasm clasico (probado con Sjasm 0.42c, compatible con 0.39).
;
; Entrada USR desde MSX BASIC:
;   A  = 3 (tipo cadena)
;   DE = descriptor de cadena
;   cadena = CHR$(X)+CHR$(Y)+texto
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
        ld      a,(ix+0)
        cp      2
        ret     c
        sub     2
        ld      (REMAIN),a
        ld      l,(ix+1)
        ld      h,(ix+2)
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
        ld      hl,926
        jr      SET_SOURCE
FIRST_ROW:
        ld      hl,920
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
        byte    0               ; R#44 color (no usado por HMMM)
        byte    0               ; R#45 argumento, copia IMP
        byte    0D0h            ; R#46 HMMM

TEXT_PTR:       word    0
HEADER:         word    0
REMAIN:         byte    0
DEST_X:         byte    0
DEST_Y:         byte    0

CODE_END:
