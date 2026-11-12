; RAW data debt. Bootstrap: tools/datagen.py; edit this source thereafter.
.286
BANK_2F9E segment para public 'FAR_DATA'
public ext_2F9E
ext_2F9E label far
    db 'ICE!'
    db 000h, 000h, 001h, 081h, 000h, 000h, 0FDh, 000h, 004h, 0FFh, 07Fh, 0C1h, 0FFh, 05Fh, 0F0h, 0FFh
    db 017h, 0FCh, 0FFh, 005h, 0FFh, 07Fh, 0C1h, 0FFh, 05Fh, 0F0h, 0FFh, 017h, 0FCh, 0FFh, 005h, 0FFh
    db 07Fh, 0C1h, 0FFh, 05Fh, 0F0h, 0FFh, 017h, 0FCh, 0FFh, 005h, 0FFh, 07Fh, 0C1h, 0FFh, 05Fh, 0F0h
    db 0FFh, 017h, 0FCh, 0FFh, 005h, 0FFh, 07Fh, 0C1h, 0FFh, 05Fh, 0F0h, 0FFh, 017h, 0FCh, 0FFh, 005h
    db 0FFh, 07Fh, 0C0h, 0FEh, 0DFh, 096h, 05Dh, 01Eh, 070h, 0A6h, 017h, 09Eh, 003h, 0F0h, 0DAh, 0F6h
    db 00Dh, 0DFh, 071h, 077h, 001h, 00Bh, 0F0h, 09Ch, 0E7h, 002h, 01Eh, 03Bh, 001h, 01Eh, 051h, 00Ch
    db 0C0h, 0B3h, 080h, 007h, 078h, 0B5h, 0B3h, 001h, 08Fh, 0D4h, 09Eh, 0E7h, 071h, 0C0h, 0BBh, 0A6h
    db 000h, 0AFh, 0F0h, 096h, 0E0h, 049h, 0C0h, 039h, 06Eh, 09Ch, 09Dh, 0F7h, 004h, 023h, 0F0h, 06Ah
    db 065h, 09Dh, 004h, 05Ch, 0C0h, 083h, 09Eh, 077h, 0DFh, 00Eh, 078h, 01Ch, 0B0h, 000h, 0CFh, 009h
    db 04Eh, 0E8h, 0C9h, 0D8h, 003h, 0BCh, 06Bh, 00Fh, 0BCh, 006h, 00Ah, 03Dh, 067h, 000h, 0CFh, 09Fh
    db 006h, 0E0h, 001h, 003h, 078h, 09Ah, 071h, 03Fh, 0CFh, 05Fh, 006h, 08Fh, 077h, 0DEh, 039h, 00Fh
    db 078h, 019h, 0FCh, 079h, 0CAh, 05Ch, 010h, 080h, 0C7h, 01Ch, 0E0h, 0E1h, 0C9h, 000h, 0BCh, 0A7h
    db 001h, 0CFh
    db 'C>OA'
    db 003h, 0AFh, 029h, 0C0h, 083h, 00Ah, 0F0h, 0ACh, 03Bh, 06Ah, 00Ah, 0BCh, 0B0h, 0F8h, 09Ch, 087h
    db 005h, 003h, 0F0h, 082h, 0E2h, 003h, 09Eh, 033h, 080h, 0A7h, 0DDh, 005h
    db 'sA\E,'
    db 0C0h, 033h, 080h, 001h, 078h, 0EEh, 01Ah, 08Dh, 071h, 01Eh, 071h, 027h, 03Ch, 01Bh, 0F0h, 09Eh
    db 000h, 03Ch, 02Dh, 001h, 06Fh, 074h, 0DEh, 05Dh, 0CEh, 000h, 0BCh, 0C8h, 059h, 027h, 02Ah, 09Bh
    db 0F3h, 082h, 036h, 0BDh, 011h, 0D8h, 0A6h, 057h, 0A4h, 0E9h, 001h, 001h, 071h, 083h, 0FFh, 0BFh
    db 0E0h, 0FFh, 02Fh, 0F8h, 0FFh, 00Bh, 0FEh, 0FFh, 082h, 0FFh, 0BFh, 0E0h, 0FFh, 02Fh, 0F8h, 0FFh
    db 00Bh, 0FEh, 0FFh, 082h, 0FFh, 0BFh, 0E0h, 0FFh, 02Fh, 0F8h, 0FFh, 00Bh, 0FEh, 0FFh, 082h, 0FFh
    db 0BFh, 0E0h, 0FFh, 02Fh, 0F8h, 0FFh, 00Bh, 0FEh, 0FFh, 082h, 0FFh, 0BFh, 0E0h, 0FFh, 02Fh, 0F8h
    db 0FFh, 00Bh, 0FEh, 0FFh, 082h, 0FFh, 0BFh, 0E0h, 0FFh, 02Fh, 0F8h, 0FFh, 00Bh, 0FEh, 0FFh, 082h
    db 0FFh, 0BFh, 0E0h, 0FFh, 02Fh, 0F8h, 0FFh, 00Bh, 0FEh, 0FFh, 082h, 0FFh, 0BFh, 0E0h, 0FFh, 02Fh
    db 0F8h, 0FFh, 00Bh, 0FEh, 0FFh, 082h, 0FFh, 03Fh, 060h, 0FFh, 00Fh, 0C8h, 0F8h, 000h, 00Bh, 03Fh
    db 020h, 0D0h, 0DDh, 000h, 000h, 0CFh
    db 15 dup (000h)
BANK_2F9E ends
end
