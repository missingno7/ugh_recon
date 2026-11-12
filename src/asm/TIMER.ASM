; Maintained reconstruction; asmgen.py is the bootstrap, asmverify.py is the gate.
; Image contribution 0A326..0A661 (end exclusive).
.286
JUMPS
; Real DGROUP storage; independent addresses are bound in asm-map.json.
extrn LastActiveTimerSlotOffset:byte
extrn TimerIntervalLowBySlot:byte
extrn TimerIntervalHighBySlot:byte
extrn TimerRemainingLowBySlot:byte
extrn TimerRemainingHighBySlot:byte
extrn TimerCallbackDueBySlot:byte
extrn TimerSlotOffsetByHandle:byte
extrn TimerHandleBySlot:byte
extrn TimerCallbackOffsetBySlot:byte
extrn TimerCallbackSegmentBySlot:byte
extrn NextPitQuantumLow:byte
extrn NextPitQuantumHigh:byte
extrn PreviousInt08Offset:byte
extrn PreviousInt08Segment:byte
extrn EarliestTimerIntervalLow:byte
extrn EarliestTimerIntervalHigh:byte
extrn ProgrammedPitDivisor:byte
TIMERSEG segment word public 'CODE'
assume cs:TIMERSEG
public ext_0A32
ext_0A32 label far
TIMER_BASE label byte
public _InstallTimerInterrupt
_InstallTimerInterrupt equ TIMER_BASE+02h
public _RestoreTimerInterrupt
_RestoreTimerInterrupt equ TIMER_BASE+09Ah
public _RegisterTimerCallback
_RegisterTimerCallback equ TIMER_BASE+01A4h
public _RemoveTimerCallback
_RemoveTimerCallback equ TIMER_BASE+0215h
public _SetTimerCallbackInterval
_SetTimerCallbackInterval equ TIMER_BASE+02BBh
TimerInterruptInstalled equ TIMER_BASE+00h
byte_data_0006:
    db 00h, 00h ; data 0006..0008
; CONTRACT (tools/apply.py)
; Install the INT 08h dispatcher once and initialize the timer-slot tables.
; In: no arguments; CS:0006 word suppresses repeat installation.
; Out: saves the old INT 08h vector, installs TIMER:00D2, clears slot state.
; Effects: DOS INT 21h/AH=35h and AH=25h; changes ES and working registers.
; Quirk: saved-vector chaining executes STI before calling the prior handler.
; END CONTRACT
InstallTimerInterrupt:
    test word ptr cs:[TimerInterruptInstalled], 0FFFFh ; @0008
    jne loc_0098 ; @000F JUMPS expansion
loc_0014:
    mov word ptr cs:[TimerInterruptInstalled], 1 ; @0014
    push ds ; @001B
    mov ax, seg ext_5C09 ; @001C
    mov ds, ax ; @001F
    mov ax, 03508h ; @0021
    int 021h ; @0024
    mov word ptr ds:[PreviousInt08Offset], bx ; @0026
    mov word ptr ds:[PreviousInt08Segment], es ; @002A
    mov ax, offset ChainSavedTimerInterrupt ; @002E
    mov word ptr ds:[TimerCallbackOffsetBySlot], ax ; @0031
    mov ax, seg TIMERSEG ; @0034
    mov word ptr ds:[TimerCallbackSegmentBySlot], ax ; @0037
    mov word ptr ds:[NextPitQuantumLow], 0 ; @003A
    mov word ptr ds:[NextPitQuantumHigh], 1 ; @0040
    mov word ptr ds:[EarliestTimerIntervalLow], 0 ; @0046
    mov word ptr ds:[EarliestTimerIntervalHigh], 1 ; @004C
    mov word ptr ds:[TimerIntervalLowBySlot], 0 ; @0052
    mov word ptr ds:[TimerIntervalHighBySlot], 1 ; @0058
    mov word ptr ds:[TimerRemainingLowBySlot], 0 ; @005E
    mov word ptr ds:[TimerRemainingHighBySlot], 1 ; @0064
    mov si, 01Eh ; @006A
loc_006D:
    mov word ptr [si + TimerSlotOffsetByHandle], 08000h ; @006D
    sub si, 2 ; @0073
    jns short loc_006D ; @0076
    mov word ptr ds:[TimerSlotOffsetByHandle], 0 ; @0078
    mov word ptr ds:[TimerHandleBySlot], 0 ; @007E
    mov word ptr ds:[LastActiveTimerSlotOffset], 0 ; @0084
    mov ax, seg TIMERSEG ; @008A
    mov ds, ax ; @008D
    mov dx, offset HandleTimerInterrupt ; @008F
    mov ax, 02508h ; @0092
    int 021h ; @0095
    pop ds ; @0097
loc_0098:
    retf ; @0098
; CONTRACT (tools/apply.py)
; Chain to the saved INT 08h vector through a far call, then return to the dispatcher.
; In: DS addresses the saved offset and segment at DGROUP:7B72/7B74.
; Effects: STI enables interrupts before PUSHF and the far call to the prior handler.
; END CONTRACT
ChainSavedTimerInterrupt:
    sti ; @0099
    pushf ; @009A
    call dword ptr ds:[PreviousInt08Offset] ; @009B
    retf ; @009F
; CONTRACT (tools/apply.py)
; Restore the saved INT 08h vector and reset PIT channel 0 to divisor zero.
; In: no arguments; CS:0006 word gates all work.
; Out: clears the installation flag; restores DS on the active path.
; Effects: DOS INT 21h/AH=25h; writes command 36h and two zero bytes to ports 43h/40h.
; Quirk: divisor zero represents 65536 PIT clocks; inactive calls perform no I/O.
; END CONTRACT
RestoreTimerInterrupt:
    test word ptr cs:[TimerInterruptInstalled], 0FFFFh ; @00A0
    je loc_00D1 ; @00A7
    mov word ptr cs:[TimerInterruptInstalled], 0 ; @00AC
    push ds ; @00B3
    mov ax, seg ext_5C09 ; @00B4
    mov ds, ax ; @00B7
    mov dx, word ptr ds:[PreviousInt08Offset] ; @00B9
    mov ds, word ptr ds:[PreviousInt08Segment] ; @00BD
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
; CONTRACT (tools/apply.py)
; Advance timer-slot countdowns, call due handlers, acknowledge IRQ0, and update PIT channel 0.
; In: hardware INT 08h context; DGROUP state contains slot times and callbacks.
; Out: expired flags are cleared before their far callbacks are invoked; returns with IRET.
; Effects: writes EOI to port 20h and may program PIT ports 43h/40h.
; Quirk: callbacks run in interrupt context; the service period is a 32-bit value,
; but only its low word is sent to the PIT (zero encodes 65536 clocks).
; END CONTRACT
HandleTimerInterrupt:
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
    mov si, word ptr ds:[LastActiveTimerSlotOffset] ; @00E0
loc_00E4:
    mov ax, word ptr ds:[NextPitQuantumLow] ; @00E4
    mov dx, word ptr ds:[NextPitQuantumHigh] ; @00E7
    sub word ptr [si + TimerRemainingLowBySlot], ax ; @00EB
    sbb word ptr [si + TimerRemainingHighBySlot], dx ; @00EF
    js loc_0105 ; @00F3
    mov ax, word ptr [si + TimerRemainingLowBySlot] ; @00F8
    or ax, word ptr [si + TimerRemainingHighBySlot] ; @00FC
    jne loc_011B ; @0100
loc_0105:
    mov word ptr [si + TimerCallbackDueBySlot], 08000h ; @0105
    mov ax, word ptr [si + TimerIntervalLowBySlot] ; @010B
    mov dx, word ptr [si + TimerIntervalHighBySlot] ; @010F
    add word ptr [si + TimerRemainingLowBySlot], ax ; @0113
    adc word ptr [si + TimerRemainingHighBySlot], dx ; @0117
loc_011B:
    sub si, 2 ; @011B
    jns short loc_00E4 ; @011E
    mov ax, word ptr ds:[EarliestTimerIntervalLow] ; @0120
    mov word ptr ds:[NextPitQuantumLow], ax ; @0123
    mov ax, word ptr ds:[EarliestTimerIntervalHigh] ; @0126
    mov word ptr ds:[NextPitQuantumHigh], ax ; @0129
    mov si, word ptr ds:[LastActiveTimerSlotOffset] ; @012C
loc_0130:
    test word ptr [si + TimerCallbackDueBySlot], 08000h ; @0130
    je loc_014B ; @0136
    mov word ptr [si + TimerCallbackDueBySlot], 0 ; @013B
    push ds ; @0141
    push si ; @0142
    shl si, 1 ; @0143
    call dword ptr [si + TimerCallbackOffsetBySlot] ; @0145
    pop si ; @0149
    pop ds ; @014A
loc_014B:
    sub si, 2 ; @014B
    jns short loc_0130 ; @014E
    mov al, 020h ; @0150
    out 020h, al ; @0152
    mov ax, word ptr ds:[ProgrammedPitDivisor] ; @0154
    cmp ax, word ptr ds:[EarliestTimerIntervalLow] ; @0157
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
    mov ax, word ptr ds:[EarliestTimerIntervalLow] ; @0182
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
    mov ax, word ptr ds:[EarliestTimerIntervalLow] ; @019A
    mov word ptr ds:[ProgrammedPitDivisor], ax ; @019D
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
; CONTRACT (tools/apply.py)
; Allocate a callback slot and add its interval to the active timer set.
; In: AX:DX callback offset:segment; CX:BX is the interval high:low pair.
;     BX is low and CX is high. Existing callers pass PIT-clock counts.
; Out: AX is the allocated handle; updates the earliest active interval when smaller.
; Clobbers/preserves: saves DI, DS, SI and restores FLAGS; AX returns the handle.
; END CONTRACT
RegisterTimerCallback:
    push di ; @01AA
    push ds ; @01AB
    push si ; @01AC
    mov di, seg ext_5C09 ; @01AD
    mov ds, di ; @01B0
    pushf ; @01B2
    mov si, word ptr ds:[LastActiveTimerSlotOffset] ; @01B3
    add si, 2 ; @01B7
    mov word ptr [si + TimerIntervalLowBySlot], bx ; @01BA
    mov word ptr [si + TimerIntervalHighBySlot], cx ; @01BE
    mov word ptr [si + TimerRemainingLowBySlot], bx ; @01C2
    mov word ptr [si + TimerRemainingHighBySlot], cx ; @01C6
    shl si, 1 ; @01CA
    mov word ptr [si + TimerCallbackOffsetBySlot], ax ; @01CC
    mov word ptr [si + TimerCallbackSegmentBySlot], dx ; @01D0
    shr si, 1 ; @01D4
    cmp cx, word ptr ds:[EarliestTimerIntervalHigh] ; @01D6
    ja loc_01F6 ; @01DA
    jb loc_01ED ; @01DF
    cmp bx, word ptr ds:[EarliestTimerIntervalLow] ; @01E4
    jae loc_01F6 ; @01E8
loc_01ED:
    cli ; @01ED
    mov word ptr ds:[EarliestTimerIntervalLow], bx ; @01EE
    mov word ptr ds:[EarliestTimerIntervalHigh], cx ; @01F2
loc_01F6:
    mov di, si ; @01F6
loc_01F8:
    test word ptr [di + TimerSlotOffsetByHandle], 08000h ; @01F8
    jne loc_0208 ; @01FE
    sub di, 2 ; @0203
    jmp short loc_01F8 ; @0206
loc_0208:
    mov word ptr [si + TimerHandleBySlot], di ; @0208
    mov word ptr [di + TimerSlotOffsetByHandle], si ; @020C
    mov ax, di ; @0210
    mov word ptr ds:[LastActiveTimerSlotOffset], si ; @0212
    popf ; @0216
    pop si ; @0217
    pop ds ; @0218
    pop di ; @0219
    retf ; @021A
; CONTRACT (tools/apply.py)
; Remove the timer identified by AX, compact the active slot prefix, and rescan its minimum.
; In: AX is a timer handle returned by RegisterTimerCallback.
; Out: marks the handle free and updates the earliest interval from remaining slots.
; Effects: CLI protects the table update; POPF restores the caller's interrupt flags.
; Quirk: the moved-slot path stores through the fixed TimerSlotOffsetByHandle base;
; it also self-stores TimerHandleBySlot at the old tail. Preserve these literal writes.
; END CONTRACT
RemoveTimerCallback:
    push si ; @021B
    push di ; @021C
    pushf ; @021D
    mov si, seg ext_5C09 ; @021E
    mov ds, si ; @0221
    cli ; @0223
    mov di, ax ; @0224
    mov si, word ptr ds:[LastActiveTimerSlotOffset] ; @0226
    sub word ptr ds:[LastActiveTimerSlotOffset], 2 ; @022A
    cmp si, word ptr [di + TimerSlotOffsetByHandle] ; @022F
    je loc_0282 ; @0233
    mov bx, word ptr [di + TimerSlotOffsetByHandle] ; @0238
    mov ax, word ptr [si + TimerIntervalLowBySlot] ; @023C
    mov word ptr [bx + TimerIntervalLowBySlot], ax ; @0240
    mov ax, word ptr [si + TimerIntervalHighBySlot] ; @0244
    mov word ptr [bx + TimerIntervalHighBySlot], ax ; @0248
    mov ax, word ptr [si + TimerRemainingLowBySlot] ; @024C
    mov word ptr [bx + TimerRemainingLowBySlot], ax ; @0250
    mov ax, word ptr [si + TimerRemainingHighBySlot] ; @0254
    mov word ptr [bx + TimerRemainingHighBySlot], ax ; @0258
    mov ax, word ptr [si + TimerCallbackOffsetBySlot] ; @025C
    mov word ptr [bx + TimerCallbackOffsetBySlot], ax ; @0260
    mov ax, word ptr [si + TimerCallbackSegmentBySlot] ; @0264
    mov word ptr [bx + TimerCallbackSegmentBySlot], ax ; @0268
    mov ax, word ptr [si + TimerCallbackDueBySlot] ; @026C
    mov word ptr [bx + TimerCallbackDueBySlot], ax ; @0270
    mov ax, word ptr [si + TimerHandleBySlot] ; @0274
    mov word ptr [si + TimerHandleBySlot], ax ; @0278
    mov si, ax ; @027C
    mov word ptr ds:[TimerSlotOffsetByHandle], si ; @027E
loc_0282:
    mov word ptr [di + TimerSlotOffsetByHandle], 08000h ; @0282
    mov cx, 1 ; @0288
    xor bx, bx ; @028B
    mov si, word ptr ds:[LastActiveTimerSlotOffset] ; @028D
loc_0291:
    cmp cx, word ptr [si + TimerIntervalHighBySlot] ; @0291
    ja loc_02A8 ; @0295
    jb loc_02B0 ; @029A
    cmp bx, word ptr [si + TimerIntervalLowBySlot] ; @029F
    jb loc_02B0 ; @02A3
loc_02A8:
    mov bx, word ptr [si + TimerIntervalLowBySlot] ; @02A8
    mov cx, word ptr [si + TimerIntervalHighBySlot] ; @02AC
loc_02B0:
    sub si, 2 ; @02B0
    jns short loc_0291 ; @02B3
    mov word ptr ds:[EarliestTimerIntervalLow], bx ; @02B5
    mov word ptr ds:[EarliestTimerIntervalHigh], cx ; @02B9
    popf ; @02BD
    pop di ; @02BE
    pop si ; @02BF
    retf ; @02C0
; CONTRACT (tools/apply.py)
; Replace a timer's interval and recompute the earliest active interval.
; In: AX is a timer handle; BX is the new low interval word and CX the high word.
; Effects: CLI protects the table update; POPF restores the caller's interrupt flags.
; END CONTRACT
SetTimerCallbackInterval:
    push di ; @02C1
    push ds ; @02C2
    push si ; @02C3
    pushf ; @02C4
    mov di, seg ext_5C09 ; @02C5
    mov ds, di ; @02C8
    mov si, ax ; @02CA
    mov si, word ptr [si + TimerSlotOffsetByHandle] ; @02CC
    cli ; @02D0
    mov word ptr [si + TimerIntervalLowBySlot], bx ; @02D1
    mov word ptr [si + TimerIntervalHighBySlot], cx ; @02D5
    mov si, word ptr ds:[LastActiveTimerSlotOffset] ; @02D9
loc_02DD:
    cmp cx, word ptr [si + TimerIntervalHighBySlot] ; @02DD
    ja loc_02F4 ; @02E1
    jb loc_02FC ; @02E6
    cmp bx, word ptr [si + TimerIntervalLowBySlot] ; @02EB
    jb loc_02FC ; @02EF
loc_02F4:
    mov bx, word ptr [si + TimerIntervalLowBySlot] ; @02F4
    mov cx, word ptr [si + TimerIntervalHighBySlot] ; @02F8
loc_02FC:
    sub si, 2 ; @02FC
    jns short loc_02DD ; @02FF
    mov word ptr ds:[EarliestTimerIntervalLow], bx ; @0301
    mov word ptr ds:[EarliestTimerIntervalHigh], cx ; @0305
    popf ; @0309
    pop si ; @030A
    pop ds ; @030B
    pop di ; @030C
    retf ; @030D
; CONTRACT (tools/apply.py)
; Adapt four far-stack words to RegisterTimerCallback's register interface.
; In: caller stack has callback offset, callback segment, interval low, interval high.
; Out: AX is the allocated timer handle; caller removes arguments after RETF.
; END CONTRACT
RegisterTimerCallbackFromStack:
    push bp ; @030E
    mov bp, sp ; @030F
    mov ax, word ptr [bp + 6] ; @0311
    mov dx, word ptr [bp + 8] ; @0314
    mov bx, word ptr [bp + 0Ah] ; @0317
    mov cx, word ptr [bp + 0Ch] ; @031A
    call far ptr RegisterTimerCallback ; @031D same-segment far call
    pop bp ; @0321
    retf ; @0322
; CONTRACT (tools/apply.py)
; Adapt one far-stack handle word to RemoveTimerCallback's register interface.
; In: caller stack word at BP+6 is the handle; caller removes it after RETF.
; END CONTRACT
RemoveTimerCallbackFromStack:
    push bp ; @0323
    mov bp, sp ; @0324
    mov ax, word ptr [bp + 6] ; @0326
    call far ptr RemoveTimerCallback ; @0329 same-segment far call
    pop bp ; @032D
    retf ; @032E
; CONTRACT (tools/apply.py)
; Load a handle and two additional words, then call RemoveTimerCallback with AX only.
; In: far-stack words at BP+6, BP+8, BP+0Ah; only the first is consumed by the callee.
; Effects: BX and CX receive the trailing words but RemoveTimerCallback ignores them.
; Quirk: retained mechanically because this unreferenced entry resembles an interval setter,
; but its actual target is the removal routine and its trailing arguments have no effect.
; END CONTRACT
loc_032F:
    push bp ; @032F
    mov bp, sp ; @0330
    mov ax, word ptr [bp + 6] ; @0332
    mov bx, word ptr [bp + 8] ; @0335
    mov cx, word ptr [bp + 0Ah] ; @0338
    call far ptr RemoveTimerCallback ; @033B same-segment far call
    pop bp ; @033F
    retf ; @0340
TIMERSEG ends
extrn ext_5C09:far
end