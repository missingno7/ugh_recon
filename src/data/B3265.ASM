; RAW data debt. Bootstrap: tools/datagen.py; edit this source thereafter.
.286
BANK_3265 segment para public 'FAR_DATA'
public ext_3265
ext_3265 label far
    db 'ADLX'
    db 000h, 000h, 000h
    db 'IAHDR'
    db 000h, 000h, 000h, 00Ah, 002h, 000h, 001h, 000h, 083h, 07Eh, 0A4h, 001h, 08Dh, 005h
    db 'IMAP'
    db 000h, 000h, 000h, 000h
    db 'TRCKI'
    db 000h, 000h, 000h, 040h, 00Eh, 000h, 061h, 06Fh, 000h, 000h, 0C0h, 037h, 042h, 000h, 00Eh, 030h
    db 0DAh, 010h, 002h, 032h, 010h, 002h, 032h, 060h, 005h, 08Dh, 000h, 002h, 0BBh, 020h, 0E9h, 030h
    db 0DAh, 010h, 002h, 032h, 000h, 006h, 0C8h, 020h, 04Dh, 077h
    db 15 dup (000h)
BANK_3265 ends
end
