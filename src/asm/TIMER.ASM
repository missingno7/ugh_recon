; Maintained reconstruction; asmgen.py is the bootstrap, asmverify.py is the gate.
; Image contribution 0A326..0A661 (end exclusive).
.286
JUMPS
TIMERSEG segment word public 'CODE'
assume cs:TIMERSEG
public ext_0A32
ext_0A32 label far
TIMER_BASE label byte
public _InstallTimerInterrupt
_InstallTimerInterrupt equ TIMER_BASE+02h
public _RestoreTimerInterrupt
_RestoreTimerInterrupt equ TIMER_BASE+09Ah
public _fn_0A32_01AA
_fn_0A32_01AA equ TIMER_BASE+01A4h
public _fn_0A32_021B
_fn_0A32_021B equ TIMER_BASE+0215h
public _fn_0A32_02C1
_fn_0A32_02C1 equ TIMER_BASE+02BBh
ds_7A4C equ 07A4Ch
ds_7A4E equ 07A4Eh
ds_7A6E equ 07A6Eh
ds_7A8E equ 07A8Eh
ds_7AAE equ 07AAEh
ds_7ACE equ 07ACEh
ds_7AEE equ 07AEEh
ds_7B0E equ 07B0Eh
ds_7B2E equ 07B2Eh
ds_7B30 equ 07B30h
ds_7B6E equ 07B6Eh
ds_7B70 equ 07B70h
ds_7B72 equ 07B72h
ds_7B74 equ 07B74h
ds_7B76 equ 07B76h
ds_7B78 equ 07B78h
ds_7B7A equ 07B7Ah
byte_0006 equ TIMER_BASE+00h
byte_data_0006:
    db 00h, 00h ; data 0006..0008
; CONTRACT (tools/apply.py)
; Install the INT 08h callback dispatcher once, saving the preceding DOS vector.
; In: no arguments; CS flag at 0006h determines whether installation is skipped.
; Out: dispatcher state in DGROUP initialized; INT 08h points to TIMER:00D2.
; Effects: DOS INT 21h/AH=35h and AH=25h; preserves DS, changes ES, AX, BX, DX, SI.
; Quirk: initializes 16 slots; the saved-vector callback enables interrupts before chaining.
; END CONTRACT
InstallTimerInterrupt:
    test word ptr cs:[byte_0006], 0FFFFh ; @0008
    jne loc_0098 ; @000F JUMPS expansion
loc_0014:
    mov word ptr cs:[byte_0006], 1 ; @0014
    push ds ; @001B
    mov ax, seg ext_5C09 ; @001C
    mov ds, ax ; @001F
    mov ax, 03508h ; @0021
    int 021h ; @0024
    mov word ptr ds:[ds_7B72], bx ; @0026
    mov word ptr ds:[ds_7B74], es ; @002A
    mov ax, offset loc_0099 ; @002E
    mov word ptr ds:[ds_7B2E], ax ; @0031
    mov ax, seg TIMERSEG ; @0034
    mov word ptr ds:[ds_7B30], ax ; @0037
    mov word ptr ds:[ds_7B6E], 0 ; @003A
    mov word ptr ds:[ds_7B70], 1 ; @0040
    mov word ptr ds:[ds_7B76], 0 ; @0046
    mov word ptr ds:[ds_7B78], 1 ; @004C
    mov word ptr ds:[ds_7A4E], 0 ; @0052
    mov word ptr ds:[ds_7A6E], 1 ; @0058
    mov word ptr ds:[ds_7A8E], 0 ; @005E
    mov word ptr ds:[ds_7AAE], 1 ; @0064
    mov si, 01Eh ; @006A
loc_006D:
    mov word ptr [si + ds_7AEE], 08000h ; @006D
    sub si, 2 ; @0073
    jns short loc_006D ; @0076
    mov word ptr ds:[ds_7AEE], 0 ; @0078
    mov word ptr ds:[ds_7B0E], 0 ; @007E
    mov word ptr ds:[ds_7A4C], 0 ; @0084
    mov ax, seg TIMERSEG ; @008A
    mov ds, ax ; @008D
    mov dx, offset loc_00D2 ; @008F
    mov ax, 02508h ; @0092
    int 021h ; @0095
    pop ds ; @0097
loc_0098:
    retf ; @0098
loc_0099:
    sti ; @0099
    pushf ; @009A
    call dword ptr ds:[ds_7B72] ; @009B
    retf ; @009F
; CONTRACT (tools/apply.py)
; Restore the saved INT 08h vector and the PIT channel 0 mode/divisor after installation.
; In: no arguments; CS flag at 0006h gates all work.
; Out: installation flag cleared; DS preserved; AX and DX changed on the active path.
; Effects: DOS INT 21h/AH=25h; sends 36h to port 43h and two zero bytes to port 40h.
; Quirk: a zero divisor means 65536 PIT clocks; an inactive call performs no I/O.
; END CONTRACT
RestoreTimerInterrupt:
    test word ptr cs:[byte_0006], 0FFFFh ; @00A0
    je loc_00D1 ; @00A7
    mov word ptr cs:[byte_0006], 0 ; @00AC
    push ds ; @00B3
    mov ax, seg ext_5C09 ; @00B4
    mov ds, ax ; @00B7
    mov dx, word ptr ds:[ds_7B72] ; @00B9
    mov ds, word ptr ds:[ds_7B74] ; @00BD
    mov ax, 02508h ; @00C1
    int 021h ; @00C4
    mov al, 036h ; @00C6
    out 043h, al ; @00C8
    xor al, al ; @00CA
    out 040h, al ; @00CC
    out 040h, al ; @00CE
    pop ds ; @00D0
loc_00D1:
    retf ; @00D1
loc_00D2:
    push ax ; @00D2
    push bx ; @00D3
    push cx ; @00D4
    push dx ; @00D5
    push si ; @00D6
    push di ; @00D7
    push ds ; @00D8
    push es ; @00D9
    push bp ; @00DA
    mov ax, seg ext_5C09 ; @00DB
    mov ds, ax ; @00DE
    mov si, word ptr ds:[ds_7A4C] ; @00E0
loc_00E4:
    mov ax, word ptr ds:[ds_7B6E] ; @00E4
    mov dx, word ptr ds:[ds_7B70] ; @00E7
    sub word ptr [si + ds_7A8E], ax ; @00EB
    sbb word ptr [si + ds_7AAE], dx ; @00EF
    js loc_0105 ; @00F3
    mov ax, word ptr [si + ds_7A8E] ; @00F8
    or ax, word ptr [si + ds_7AAE] ; @00FC
    jne loc_011B ; @0100
loc_0105:
    mov word ptr [si + ds_7ACE], 08000h ; @0105
    mov ax, word ptr [si + ds_7A4E] ; @010B
    mov dx, word ptr [si + ds_7A6E] ; @010F
    add word ptr [si + ds_7A8E], ax ; @0113
    adc word ptr [si + ds_7AAE], dx ; @0117
loc_011B:
    sub si, 2 ; @011B
    jns short loc_00E4 ; @011E
    mov ax, word ptr ds:[ds_7B76] ; @0120
    mov word ptr ds:[ds_7B6E], ax ; @0123
    mov ax, word ptr ds:[ds_7B78] ; @0126
    mov word ptr ds:[ds_7B70], ax ; @0129
    mov si, word ptr ds:[ds_7A4C] ; @012C
loc_0130:
    test word ptr [si + ds_7ACE], 08000h ; @0130
    je loc_014B ; @0136
    mov word ptr [si + ds_7ACE], 0 ; @013B
    push ds ; @0141
    push si ; @0142
    shl si, 1 ; @0143
    call dword ptr [si + ds_7B2E] ; @0145
    pop si ; @0149
    pop ds ; @014A
loc_014B:
    sub si, 2 ; @014B
    jns short loc_0130 ; @014E
    mov al, 020h ; @0150
    out 020h, al ; @0152
    mov ax, word ptr ds:[ds_7B7A] ; @0154
    cmp ax, word ptr ds:[ds_7B76] ; @0157
    je loc_019A ; @015B
    jmp loc_0165 ; @0160
    nop ; @0163
    nop ; @0164
loc_0165:
    jmp loc_016A ; @0165
    nop ; @0168
    nop ; @0169
loc_016A:
    jmp loc_016F ; @016A
    nop ; @016D
    nop ; @016E
loc_016F:
    mov al, 036h ; @016F
    out 043h, al ; @0171
    jmp loc_0178 ; @0173
    nop ; @0176
    nop ; @0177
loc_0178:
    jmp loc_017D ; @0178
    nop ; @017B
    nop ; @017C
loc_017D:
    jmp loc_0182 ; @017D
    nop ; @0180
    nop ; @0181
loc_0182:
    mov ax, word ptr ds:[ds_7B76] ; @0182
    out 040h, al ; @0185
    jmp loc_018C ; @0187
    nop ; @018A
    nop ; @018B
loc_018C:
    jmp loc_0191 ; @018C
    nop ; @018F
    nop ; @0190
loc_0191:
    jmp loc_0196 ; @0191
    nop ; @0194
    nop ; @0195
loc_0196:
    mov al, ah ; @0196
    out 040h, al ; @0198
loc_019A:
    mov ax, word ptr ds:[ds_7B76] ; @019A
    mov word ptr ds:[ds_7B7A], ax ; @019D
    pop bp ; @01A0
    pop es ; @01A1
    pop ds ; @01A2
    pop di ; @01A3
    pop si ; @01A4
    pop dx ; @01A5
    pop cx ; @01A6
    pop bx ; @01A7
    pop ax ; @01A8
    iret ; @01A9
loc_01AA:
    push di ; @01AA
    push ds ; @01AB
    push si ; @01AC
    mov di, seg ext_5C09 ; @01AD
    mov ds, di ; @01B0
    pushf ; @01B2
    mov si, word ptr ds:[ds_7A4C] ; @01B3
    add si, 2 ; @01B7
    mov word ptr [si + ds_7A4E], bx ; @01BA
    mov word ptr [si + ds_7A6E], cx ; @01BE
    mov word ptr [si + ds_7A8E], bx ; @01C2
    mov word ptr [si + ds_7AAE], cx ; @01C6
    shl si, 1 ; @01CA
    mov word ptr [si + ds_7B2E], ax ; @01CC
    mov word ptr [si + ds_7B30], dx ; @01D0
    shr si, 1 ; @01D4
    cmp cx, word ptr ds:[ds_7B78] ; @01D6
    ja loc_01F6 ; @01DA
    jb loc_01ED ; @01DF
    cmp bx, word ptr ds:[ds_7B76] ; @01E4
    jae loc_01F6 ; @01E8
loc_01ED:
    cli ; @01ED
    mov word ptr ds:[ds_7B76], bx ; @01EE
    mov word ptr ds:[ds_7B78], cx ; @01F2
loc_01F6:
    mov di, si ; @01F6
loc_01F8:
    test word ptr [di + ds_7AEE], 08000h ; @01F8
    jne loc_0208 ; @01FE
    sub di, 2 ; @0203
    jmp short loc_01F8 ; @0206
loc_0208:
    mov word ptr [si + ds_7B0E], di ; @0208
    mov word ptr [di + ds_7AEE], si ; @020C
    mov ax, di ; @0210
    mov word ptr ds:[ds_7A4C], si ; @0212
    popf ; @0216
    pop si ; @0217
    pop ds ; @0218
    pop di ; @0219
    retf ; @021A
loc_021B:
    push si ; @021B
    push di ; @021C
    pushf ; @021D
    mov si, seg ext_5C09 ; @021E
    mov ds, si ; @0221
    cli ; @0223
    mov di, ax ; @0224
    mov si, word ptr ds:[ds_7A4C] ; @0226
    sub word ptr ds:[ds_7A4C], 2 ; @022A
    cmp si, word ptr [di + ds_7AEE] ; @022F
    je loc_0282 ; @0233
    mov bx, word ptr [di + ds_7AEE] ; @0238
    mov ax, word ptr [si + ds_7A4E] ; @023C
    mov word ptr [bx + ds_7A4E], ax ; @0240
    mov ax, word ptr [si + ds_7A6E] ; @0244
    mov word ptr [bx + ds_7A6E], ax ; @0248
    mov ax, word ptr [si + ds_7A8E] ; @024C
    mov word ptr [bx + ds_7A8E], ax ; @0250
    mov ax, word ptr [si + ds_7AAE] ; @0254
    mov word ptr [bx + ds_7AAE], ax ; @0258
    mov ax, word ptr [si + ds_7B2E] ; @025C
    mov word ptr [bx + ds_7B2E], ax ; @0260
    mov ax, word ptr [si + ds_7B30] ; @0264
    mov word ptr [bx + ds_7B30], ax ; @0268
    mov ax, word ptr [si + ds_7ACE] ; @026C
    mov word ptr [bx + ds_7ACE], ax ; @0270
    mov ax, word ptr [si + ds_7B0E] ; @0274
    mov word ptr [si + ds_7B0E], ax ; @0278
    mov si, ax ; @027C
    mov word ptr ds:[ds_7AEE], si ; @027E
loc_0282:
    mov word ptr [di + ds_7AEE], 08000h ; @0282
    mov cx, 1 ; @0288
    xor bx, bx ; @028B
    mov si, word ptr ds:[ds_7A4C] ; @028D
loc_0291:
    cmp cx, word ptr [si + ds_7A6E] ; @0291
    ja loc_02A8 ; @0295
    jb loc_02B0 ; @029A
    cmp bx, word ptr [si + ds_7A4E] ; @029F
    jb loc_02B0 ; @02A3
loc_02A8:
    mov bx, word ptr [si + ds_7A4E] ; @02A8
    mov cx, word ptr [si + ds_7A6E] ; @02AC
loc_02B0:
    sub si, 2 ; @02B0
    jns short loc_0291 ; @02B3
    mov word ptr ds:[ds_7B76], bx ; @02B5
    mov word ptr ds:[ds_7B78], cx ; @02B9
    popf ; @02BD
    pop di ; @02BE
    pop si ; @02BF
    retf ; @02C0
loc_02C1:
    push di ; @02C1
    push ds ; @02C2
    push si ; @02C3
    pushf ; @02C4
    mov di, seg ext_5C09 ; @02C5
    mov ds, di ; @02C8
    mov si, ax ; @02CA
    mov si, word ptr [si + ds_7AEE] ; @02CC
    cli ; @02D0
    mov word ptr [si + ds_7A4E], bx ; @02D1
    mov word ptr [si + ds_7A6E], cx ; @02D5
    mov si, word ptr ds:[ds_7A4C] ; @02D9
loc_02DD:
    cmp cx, word ptr [si + ds_7A6E] ; @02DD
    ja loc_02F4 ; @02E1
    jb loc_02FC ; @02E6
    cmp bx, word ptr [si + ds_7A4E] ; @02EB
    jb loc_02FC ; @02EF
loc_02F4:
    mov bx, word ptr [si + ds_7A4E] ; @02F4
    mov cx, word ptr [si + ds_7A6E] ; @02F8
loc_02FC:
    sub si, 2 ; @02FC
    jns short loc_02DD ; @02FF
    mov word ptr ds:[ds_7B76], bx ; @0301
    mov word ptr ds:[ds_7B78], cx ; @0305
    popf ; @0309
    pop si ; @030A
    pop ds ; @030B
    pop di ; @030C
    retf ; @030D
loc_030E:
    push bp ; @030E
    mov bp, sp ; @030F
    mov ax, word ptr [bp + 6] ; @0311
    mov dx, word ptr [bp + 8] ; @0314
    mov bx, word ptr [bp + 0Ah] ; @0317
    mov cx, word ptr [bp + 0Ch] ; @031A
    call far ptr loc_01AA ; @031D same-segment far call
    pop bp ; @0321
    retf ; @0322
loc_0323:
    push bp ; @0323
    mov bp, sp ; @0324
    mov ax, word ptr [bp + 6] ; @0326
    call far ptr loc_021B ; @0329 same-segment far call
    pop bp ; @032D
    retf ; @032E
loc_032F:
    push bp ; @032F
    mov bp, sp ; @0330
    mov ax, word ptr [bp + 6] ; @0332
    mov bx, word ptr [bp + 8] ; @0335
    mov cx, word ptr [bp + 0Ah] ; @0338
    call far ptr loc_021B ; @033B same-segment far call
    pop bp ; @033F
    retf ; @0340
TIMERSEG ends
extrn ext_5C09:far
end