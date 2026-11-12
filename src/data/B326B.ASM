; RAW data debt. Bootstrap: tools/datagen.py; edit this source thereafter.
.286
BANK_326B segment para public 'FAR_DATA'
public ext_326B
ext_326B label far
    db 'ADLX'
    db 000h, 000h, 000h
    db '|AHDR'
    db 000h, 000h, 000h, 00Ah, 002h, 000h, 002h, 000h, 0D2h, 052h, 0A4h, 001h, 08Dh, 005h
    db 'IMAP'
    db 000h, 000h, 000h, 000h
    db 'TRCK|'
    db 000h, 000h, 000h, 040h, 005h, 04Eh, 0DAh, 025h, 000h, 001h, 000h, 0F9h, 015h, 000h, 00Ah, 041h
    db 085h, 04Eh, 0DAh, 015h, 000h, 081h, 080h, 0F9h, 013h, 000h, 00Ah, 060h, 005h, 08Dh, 030h, 0BEh
    db 010h, 057h, 031h, 031h, 0BEh, 0E9h, 020h, 010h, 041h, 02Eh, 011h, 057h, 031h, 0E9h, 020h, 021h
    db 010h, 002h, 02Eh, 011h, 041h, 02Eh, 0E9h, 020h, 021h, 010h, 0B0h, 02Dh, 011h, 002h, 02Eh, 0E9h
    db 020h, 021h, 010h, 057h, 02Dh, 011h, 0B0h, 02Dh, 0E9h, 021h, 011h, 057h, 02Dh, 0E9h, 020h, 021h
    db 010h, 057h, 02Dh, 011h, 057h, 02Dh, 000h, 001h, 0D2h
    db ' !Mw'
    db 12 dup (000h)
BANK_326B ends
end
