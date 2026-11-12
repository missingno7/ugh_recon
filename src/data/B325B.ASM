; RAW data debt. Bootstrap: tools/datagen.py; edit this source thereafter.
.286
BANK_325B segment para public 'FAR_DATA'
public ext_325B
ext_325B label far
    db 'ADLX'
    db 000h, 000h, 000h
    db '?AHDR'
    db 000h, 000h, 000h, 00Ah, 002h, 000h, 001h, 000h, 083h, 07Eh, 0A4h, 001h, 08Dh, 005h
    db 'IMAP'
    db 000h, 000h, 000h, 000h
    db 'TRCK?'
    db 000h, 000h, 000h, 040h, 00Eh, 0C0h, 0F0h, 092h, 001h, 09Eh, 040h, 04Ah, 076h, 002h, 006h, 030h
    db 0FCh, 010h, 002h, 02Eh, 010h, 002h, 02Eh, 060h, 005h, 08Dh, 000h, 003h, 0A4h, 020h, 04Dh, 077h
    db 9 dup (000h)
BANK_325B ends
end
