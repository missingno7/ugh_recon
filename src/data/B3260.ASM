; RAW data debt. Bootstrap: tools/datagen.py; edit this source thereafter.
.286
BANK_3260 segment para public 'FAR_DATA'
public ext_3260
ext_3260 label far
    db 'ADLX'
    db 000h, 000h, 000h
    db '?AHDR'
    db 000h, 000h, 000h, 00Ah, 002h, 000h, 001h, 000h, 083h, 07Eh, 0A4h, 001h, 01Eh, 005h
    db 'IMAP'
    db 000h, 000h, 000h, 000h
    db 'TRCK?'
    db 000h, 000h, 000h, 040h, 04Eh, 000h, 0F0h, 090h, 000h, 05Eh, 04Eh, 04Ah, 096h, 003h, 00Eh, 030h
    db 0F4h, 010h, 087h, 032h, 010h, 087h, 032h, 060h, 005h, 01Eh, 000h, 003h, 0A4h, 020h, 04Dh, 077h
    db 9 dup (000h)
BANK_3260 ends
end
