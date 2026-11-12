; RAW data debt. Bootstrap: tools/datagen.py; edit this source thereafter.
.286
BANK_3274 segment para public 'FAR_DATA'
public ext_3274
ext_3274 label far
    db 'ADLX'
    db 000h, 000h, 000h
    db 'FAHDR'
    db 000h, 000h, 000h, 00Ah, 002h, 000h, 001h, 000h, 083h, 07Eh, 0A4h, 001h, 08Dh, 005h
    db 'IMAP'
    db 000h, 000h, 000h, 000h
    db 'TRCKF'
    db 000h, 000h, 000h, 040h, 0C0h, 053h, 033h, 081h, 002h, 042h, 040h, 0F6h, 057h, 002h, 00Eh, 030h
    db 0DEh, 010h, 002h, 02Ah, 010h, 002h, 02Ah, 060h, 005h, 08Dh, 000h, 001h, 0D2h, 020h, 010h, 002h
    db 02Ah, 000h, 001h, 0D2h, 020h, 04Dh, 077h, 000h, 000h
BANK_3274 ends
end
