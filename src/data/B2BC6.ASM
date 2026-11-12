; RAW data debt. Bootstrap: tools/datagen.py; edit this source thereafter.
.286
BANK_2BC6 segment para public 'FAR_DATA'
public ext_2BC6
ext_2BC6 label far
    db 000h, 000h, 000h, 010h, 00Ch, 008h, 014h, 010h, 00Ch, 018h, 014h, 00Ch, 01Ch, 014h, 00Ch, 020h
    db 018h, 00Ch, 024h, 01Ch, 010h, 028h, 020h, 014h, 02Ch, 024h, 018h, 030h, 028h, 01Ch
    db '4, 80$'
    db 010h, 010h, 008h, 010h, 014h, 008h
    db ',$ 8,(8<<'
    db 00Ch, 00Ch, 010h, 010h, 010h, 014h, 010h, 014h, 018h, 014h, 018h, 01Ch, 018h, 01Ch, 020h, 01Ch
    db ' $ $(((,,,0004448'
    db 014h, 01Ch, 00Ch, 01Ch, 024h, 014h, 024h, 02Ch, 01Ch
    db ',4$?9'
    db 00Eh, 03Ch, 02Fh, 00Ch, 039h, 026h, 00Ah, 036h, 01Dh, 009h, 033h, 015h, 008h, 030h, 00Dh, 006h
    db 02Dh, 006h, 005h, 02Ah, 004h, 009h, 027h, 003h, 00Ch, 024h, 002h, 010h, 021h, 001h, 012h, 01Eh
    db 001h, 015h, 01Bh, 000h, 016h, 018h, 000h, 017h, 012h, 000h, 015h, 00Dh, 000h, 012h
    db ';6&;9&8;&4;&0;&-;&);&&;'
    db 027h
    db '&;+&;/&;3&;7&;;&<<'
    db 027h, 03Bh, 03Eh, 027h, 006h, 03Eh, 000h, 000h, 000h, 00Ch, 00Ch, 010h, 010h, 010h, 014h, 014h
    db 014h, 018h, 014h, 014h, 01Ch, 018h, 018h, 01Ch, 01Ch, 01Ch
    db '   $$$(((,,,0004'
    db 010h, 010h, 010h, 010h, 014h, 010h
    db '( $4,08<<'
    db 000h, 00Ch, 010h, 004h, 010h, 014h, 008h, 014h, 018h, 00Ch, 018h, 01Ch, 010h, 01Ch, 020h, 014h
    db 020h, 024h, 018h, 024h, 028h, 01Ch
    db '(, ,0$04(48'
    db 014h, 01Ch, 018h, 01Ch
    db '$ $,(,40'
    db 477 dup (000h)
    db 03Fh, 03Fh, 03Fh
BANK_2BC6 ends
end
