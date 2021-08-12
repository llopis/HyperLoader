 INCLUDE "Config.asm"

SCREEN_ADDRESS EQU #C000
SCREEN_SIZE EQU #4000

SYNCHRONIZATION_BYTE EQU #AC

 ORG #4000

Main:
	di

	call	PrepareScreen

	ld	bc, #F610		; cassette motor on
	out	(c),c

	ld	ix, SCREEN_ADDRESS
	call	LoadBlock

	ld	bc, #F600		; cassette motor off
	out	(c),c

	;; Border color red
	ld	bc, #7F10
	ld	a, #4C
	out	(c),c
	out	(c),a

	halt


ColorTable:
	defb #54, #40, #4B, #4A, #43, #56, #4E, #57, #53, #44, #55, #4C, #5C, #4D, #45, #54


PrepareScreen:
	ld	hl, SCREEN_ADDRESS
	ld	bc, SCREEN_SIZE	
	ld	(hl), 0
	ld	e,l
	ld	d,h
	inc	de
	ldir

	;; Mode 0 and disable upper/lower ROM
	ld	bc, #7F00
	ld	a, %10001100
	out	(c), a

	;; Black border
	ld	bc, #7F10
	ld	a, #54
	out	(c),c
	out	(c),a

	;; Set ink colors
	ld	bc, #7F00
	ld	hl, ColorTable
	ld	d, 0
InkLoop:
	ld	a, d
	out	(c), a	
	ld	a, (hl)
	or	%01000000
	out	(c), a

	inc	hl
	inc	d
	ld	a, d
	cp	#10
	jr	nz, InkLoop

	ret	


;; Based on TurboLoader by Mert Boru  http://mertboru.com/?p=962
LoadBlock:
	ld	bc, #F500		; I/O port PPI 8255 port B
	ld	d, 0

	;------ Load pilot #1 (50 pulses) ------------------------
PP1:	ld	h, 50
PP1x:	call	GetPulse
	cp	70
	jp	c, PP1
	dec	h
	jp	nz, PP1x

	;------ Load pilot #2 (10 pulses) ------------------------
PP2:	ld	h, 10
PP2x:	call	GetPulse
	cp	70
	jp	nc, PP2
	dec	h
	jp	nz, PP2x

	;; Load 32 bytes * 8 = 256 pulses of zero length
	exx
	ld	h,0
	ld	l,0
	ld	d,0
	exx

PWidth:	call	GetPulse
	exx
	ld	e,a
	add	hl,de
	ld	a,h
	exx
	dec	h
	jp	nz, PWidth

	;; Save measured time for future comparison
	ld	(cTime+1), a

	;; Load synchronization byte to make sure everything is OK
	call	LoadOneByte
	cp	SYNCHRONIZATION_BYTE
	ret	nz

	;; Main loop
MainLoop:
	call	LoadOneByte
	ld	(ix), a
	inc	ix
	jp	MainLoop

	ret


;; OUT: A = loaded byte
LoadOneByte:
	ld	e,1
nByte:	call	GetPulse
cTime:	cp	0			; = measured time!
	ccf
	rl	e
	jp	nc, nByte
	ld	a, e
	ret




 IFDEF READ_CASSETTE
;; Read from cassette port, on bit 7
;; IN: BC = I/O port PPI 8255 port B, 
;;	D = 0
;; OUT: A = duration of the pulse
GetPulse:
	ld	c, d

	;; Keep reading from cassette port until we get a low read
waitWhileLow:
	in	a, (c)
	jp	m, waitWhileLow

	;; And how count how many times we get a high bit
waitWhileHigh:
	inc	c			
	in	a, (c)
	jp	p, waitWhileHigh
	ld	a, c
	ret
 ENDIF



 IFDEF READ_BUSY
;; Read from busy signal port, on bit 6
;; IN: BC = I/O port PPI 8255 port B, 
;;	D = 0
;; OUT: A = duration of the pulse
GetPulse:
	ld	c, d

	;; Keep reading from cassette port until we get a low read
waitWhileLow:
	in	a, (c)
	add	a, a
	jp	m, waitWhileLow

	;; And how count how many times we get a high bit
waitWhileHigh:
	inc	c			
	in	a, (c)
	add	a, a
	jp	p, waitWhileHigh
	ld	a, c
	ret
 ENDIF

 
