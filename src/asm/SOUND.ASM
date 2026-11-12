; Maintained reconstruction; asmgen.py is the bootstrap, asmverify.py is the gate.
; Image contribution 0664C..08783 (end exclusive).
.286
JUMPS
extrn _fn_013B_001F:far
extrn _fn_0A32_0008:far
extrn _fn_0A32_00A0:far
extrn _fn_0A32_01AA:far
extrn _fn_0A32_021B:far
extrn _fn_0A32_02C1:far
extrn _fn_0003:far
extrn _fn_1128:far
extrn _fn_1768:far
extrn _fn_1943:far
SOUNDSEG segment word public 'CODE'
assume cs:SOUNDSEG
public ext_0664
ext_0664 label far
SOUND_BASE label byte
public _g_0236
_g_0236 equ SOUND_BASE+022Ah
public _g_0256
_g_0256 equ SOUND_BASE+024Ah
public _g_025C
_g_025C equ SOUND_BASE+0250h
public _g_026A
_g_026A equ SOUND_BASE+025Eh
public _fn_0664_1331
_fn_0664_1331 equ SOUND_BASE+01325h
public _fn_0664_20B9
_fn_0664_20B9 equ SOUND_BASE+020ADh
public _fn_0664_1A65
_fn_0664_1A65 equ SOUND_BASE+01A59h
public _g_0014
_g_0014 equ SOUND_BASE+08h
public _g_0238
_g_0238 equ SOUND_BASE+022Ch
public _g_023A
_g_023A equ SOUND_BASE+022Eh
public _g_023E
_g_023E equ SOUND_BASE+0232h
public _g_000E
_g_000E equ SOUND_BASE+02h
public _g_024E
_g_024E equ SOUND_BASE+0242h
public _g_0252
_g_0252 equ SOUND_BASE+0246h
public _g_026E
_g_026E equ SOUND_BASE+0262h
public _g_0270
_g_0270 equ SOUND_BASE+0264h
public _fn_0664_112B
_fn_0664_112B equ SOUND_BASE+0111Fh
public _fn_0664_205C
_fn_0664_205C equ SOUND_BASE+02050h
public _fn_0664_1C39
_fn_0664_1C39 equ SOUND_BASE+01C2Dh
public _fn_0664_1A89
_fn_0664_1A89 equ SOUND_BASE+01A7Dh
public _fn_0664_1E97
_fn_0664_1E97 equ SOUND_BASE+01E8Bh
public _g_0212
_g_0212 equ SOUND_BASE+0206h
public _g_0216
_g_0216 equ SOUND_BASE+020Ah
public _g_022E
_g_022E equ SOUND_BASE+0222h
public _g_0242
_g_0242 equ SOUND_BASE+0236h
public _g_0246
_g_0246 equ SOUND_BASE+023Ah
public _g_0248
_g_0248 equ SOUND_BASE+023Ch
public _g_024A
_g_024A equ SOUND_BASE+023Eh
public _g_024C
_g_024C equ SOUND_BASE+0240h
public _g_0258
_g_0258 equ SOUND_BASE+024Ch
public _g_025A
_g_025A equ SOUND_BASE+024Eh
public _g_0266
_g_0266 equ SOUND_BASE+025Ah
public _g_026C
_g_026C equ SOUND_BASE+0260h
public _g_0274
_g_0274 equ SOUND_BASE+0268h
public _g_0278
_g_0278 equ SOUND_BASE+026Ch
public _g_032C
_g_032C equ SOUND_BASE+0320h
public _g_03E0
_g_03E0 equ SOUND_BASE+03D4h
public _fn_0664_134E
_fn_0664_134E equ SOUND_BASE+01342h
public _fn_0664_1A37
_fn_0664_1A37 equ SOUND_BASE+01A2Bh
public _fn_0664_1211
_fn_0664_1211 equ SOUND_BASE+01205h
public _fn_0664_14B1
_fn_0664_14B1 equ SOUND_BASE+014A5h
public _fn_0664_1377
_fn_0664_1377 equ SOUND_BASE+0136Bh
public _fn_0664_1503
_fn_0664_1503 equ SOUND_BASE+014F7h
public _g_021C
_g_021C equ SOUND_BASE+0210h
public _g_025E
_g_025E equ SOUND_BASE+0252h
public _g_0262
_g_0262 equ SOUND_BASE+0256h
byte_000C equ SOUND_BASE+00h
byte_000E equ SOUND_BASE+02h
byte_0010 equ SOUND_BASE+04h
byte_0012 equ SOUND_BASE+06h
byte_0018 equ SOUND_BASE+0Ch
byte_001A equ SOUND_BASE+0Eh
byte_001E equ SOUND_BASE+012h
byte_0024 equ SOUND_BASE+018h
byte_0030 equ SOUND_BASE+024h
byte_003A equ SOUND_BASE+02Eh
byte_003C equ SOUND_BASE+030h
byte_0210 equ SOUND_BASE+0204h
byte_0212 equ SOUND_BASE+0206h
byte_0214 equ SOUND_BASE+0208h
byte_021C equ SOUND_BASE+0210h
byte_021E equ SOUND_BASE+0212h
byte_022A equ SOUND_BASE+021Eh
byte_022C equ SOUND_BASE+0220h
byte_0234 equ SOUND_BASE+0228h
byte_0236 equ SOUND_BASE+022Ah
byte_023A equ SOUND_BASE+022Eh
byte_023C equ SOUND_BASE+0230h
byte_023E equ SOUND_BASE+0232h
byte_0240 equ SOUND_BASE+0234h
byte_0246 equ SOUND_BASE+023Ah
byte_0248 equ SOUND_BASE+023Ch
byte_024A equ SOUND_BASE+023Eh
byte_024C equ SOUND_BASE+0240h
byte_0256 equ SOUND_BASE+024Ah
byte_0258 equ SOUND_BASE+024Ch
byte_025C equ SOUND_BASE+0250h
byte_0262 equ SOUND_BASE+0256h
byte_026A equ SOUND_BASE+025Eh
byte_026C equ SOUND_BASE+0260h
byte_026E equ SOUND_BASE+0262h
byte_0270 equ SOUND_BASE+0264h
byte_0274 equ SOUND_BASE+0268h
byte_0279 equ SOUND_BASE+026Dh
byte_027E equ SOUND_BASE+0272h
byte_0282 equ SOUND_BASE+0276h
byte_0284 equ SOUND_BASE+0278h
byte_0286 equ SOUND_BASE+027Ah
byte_0288 equ SOUND_BASE+027Ch
byte_028A equ SOUND_BASE+027Eh
byte_028B equ SOUND_BASE+027Fh
byte_0338 equ SOUND_BASE+032Ch
byte_033A equ SOUND_BASE+032Eh
byte_033E equ SOUND_BASE+0332h
byte_0494 equ SOUND_BASE+0488h
byte_0495 equ SOUND_BASE+0489h
byte_0497 equ SOUND_BASE+048Bh
byte_04A1 equ SOUND_BASE+0495h
byte_04A2 equ SOUND_BASE+0496h
byte_04A5 equ SOUND_BASE+0499h
byte_04A7 equ SOUND_BASE+049Bh
byte_04A9 equ SOUND_BASE+049Dh
byte_04AB equ SOUND_BASE+049Fh
byte_04AD equ SOUND_BASE+04A1h
byte_08B1 equ SOUND_BASE+08A5h
byte_08B3 equ SOUND_BASE+08A7h
byte_08B5 equ SOUND_BASE+08A9h
byte_08B7 equ SOUND_BASE+08ABh
byte_10C7 equ SOUND_BASE+010BBh
byte_10CB equ SOUND_BASE+010BFh
byte_10CD equ SOUND_BASE+010C1h
byte_10CF equ SOUND_BASE+010C3h
byte_10D1 equ SOUND_BASE+010C5h
byte_10EF equ SOUND_BASE+010E3h
byte_10F5 equ SOUND_BASE+010E9h
byte_1122 equ SOUND_BASE+01116h
byte_1124 equ SOUND_BASE+01118h
byte_1126 equ SOUND_BASE+0111Ah
byte_1127 equ SOUND_BASE+0111Bh
byte_1129 equ SOUND_BASE+0111Dh
byte_174B equ SOUND_BASE+0173Fh
byte_1919 equ SOUND_BASE+0190Dh
byte_2058 equ SOUND_BASE+0204Ch
byte_data_000C:
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 000C..001C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 001C..002C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 002C..003C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 003C..004C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 004C..005C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 005C..006C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 006C..007C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 007C..008C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 008C..009C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 009C..00AC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 00AC..00BC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 00BC..00CC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 00CC..00DC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 00DC..00EC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 00EC..00FC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 00FC..010C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 010C..011C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 011C..012C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 012C..013C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 013C..014C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 014C..015C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 015C..016C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 016C..017C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 017C..018C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 018C..019C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 019C..01AC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 01AC..01BC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 01BC..01CC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 01CC..01DC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 01DC..01EC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 01EC..01FC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 01FC..020C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 020C..021C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 021C..022C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 022C..023C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 023C..024C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 024C..025C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 025C..026C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 026C..027C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 027C..028C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 028C..029C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 029C..02AC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 02AC..02BC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 02BC..02CC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 02CC..02DC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 02DC..02EC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 02EC..02FC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 02FC..030C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 030C..031C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 031C..032C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 032C..033C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 033C..034C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 034C..035C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 035C..036C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 036C..037C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 037C..038C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 038C..039C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 039C..03AC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 03AC..03BC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 03BC..03CC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 03CC..03DC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 03DC..03EC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 03EC..03FC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 03FC..040C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 040C..041C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 041C..042C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 042C..043C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 043C..044C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 044C..045C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 045C..046C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 046C..047C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 047C..048C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 0A6h, 014h, 00h ; data 048C..049C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 049C..04AC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 04AC..04BC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 04BC..04CC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 04CC..04DC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 04DC..04EC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 04EC..04FC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 04FC..050C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 050C..051C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 051C..052C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 052C..053C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 053C..054C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 054C..055C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 055C..056C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 056C..057C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 057C..058C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 058C..059C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 059C..05AC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 05AC..05BC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 05BC..05CC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 05CC..05DC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 05DC..05EC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 05EC..05FC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 05FC..060C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 060C..061C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 061C..062C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 062C..063C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 063C..064C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 064C..065C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 065C..066C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 066C..067C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 067C..068C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 068C..069C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 069C..06AC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 06AC..06BC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 06BC..06CC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 06CC..06DC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 06DC..06EC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 06EC..06FC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 06FC..070C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 070C..071C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 071C..072C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 072C..073C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 073C..074C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 074C..075C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 075C..076C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 076C..077C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 077C..078C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 078C..079C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 079C..07AC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 07AC..07BC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 07BC..07CC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 07CC..07DC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 07DC..07EC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 07EC..07FC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 07FC..080C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 080C..081C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 081C..082C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 082C..083C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 083C..084C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 084C..085C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 085C..086C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 086C..087C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 087C..088C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 088C..089C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 089C..08AC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 08AC..08BC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 08BC..08CC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 08CC..08DC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 08DC..08EC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 08EC..08FC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 08FC..090C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 090C..091C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 091C..092C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 092C..093C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 093C..094C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 094C..095C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 095C..096C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 096C..097C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 097C..098C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 098C..099C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 099C..09AC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 09AC..09BC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 09BC..09CC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 09CC..09DC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 09DC..09EC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 09EC..09FC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 09FC..0A0C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0A0C..0A1C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0A1C..0A2C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0A2C..0A3C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0A3C..0A4C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0A4C..0A5C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0A5C..0A6C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0A6C..0A7C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0A7C..0A8C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0A8C..0A9C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0A9C..0AAC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0AAC..0ABC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0ABC..0ACC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0ACC..0ADC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0ADC..0AEC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0AEC..0AFC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0AFC..0B0C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0B0C..0B1C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0B1C..0B2C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0B2C..0B3C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0B3C..0B4C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0B4C..0B5C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0B5C..0B6C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0B6C..0B7C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0B7C..0B8C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0B8C..0B9C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0B9C..0BAC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0BAC..0BBC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0BBC..0BCC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0BCC..0BDC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0BDC..0BEC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0BEC..0BFC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0BFC..0C0C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0C0C..0C1C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0C1C..0C2C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0C2C..0C3C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0C3C..0C4C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0C4C..0C5C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0C5C..0C6C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0C6C..0C7C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0C7C..0C8C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0C8C..0C9C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0C9C..0CAC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0CAC..0CBC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0CBC..0CCC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0CCC..0CDC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0CDC..0CEC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0CEC..0CFC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0CFC..0D0C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0D0C..0D1C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0D1C..0D2C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0D2C..0D3C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0D3C..0D4C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0D4C..0D5C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0D5C..0D6C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0D6C..0D7C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0D7C..0D8C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0D8C..0D9C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0D9C..0DAC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0DAC..0DBC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0DBC..0DCC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0DCC..0DDC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0DDC..0DEC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0DEC..0DFC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0DFC..0E0C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0E0C..0E1C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0E1C..0E2C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0E2C..0E3C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0E3C..0E4C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0E4C..0E5C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0E5C..0E6C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0E6C..0E7C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0E7C..0E8C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0E8C..0E9C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0E9C..0EAC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0EAC..0EBC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0EBC..0ECC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0ECC..0EDC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0EDC..0EEC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0EEC..0EFC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0EFC..0F0C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0F0C..0F1C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0F1C..0F2C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0F2C..0F3C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0F3C..0F4C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0F4C..0F5C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0F5C..0F6C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0F6C..0F7C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0F7C..0F8C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0F8C..0F9C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0F9C..0FAC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0FAC..0FBC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0FBC..0FCC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0FCC..0FDC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0FDC..0FEC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0FEC..0FFC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0FFC..100C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 100C..101C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 101C..102C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 102C..103C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 103C..104C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 104C..105C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 105C..106C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 106C..107C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 107C..108C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 108C..109C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 109C..10AC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 10AC..10BC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 10BC..10CC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 10CC..10DC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 10DC..10EC
    db 00h, 00h, 09h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 01h, 02h, 08h, 09h, 0Ah, 010h ; data 10EC..10FC
    db 011h, 012h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 10FC..110C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 110C..111C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 111C..112B
loc_112B:
    push es ; @112B
    push di ; @112C
    mov ax, cs ; @112D
    mov es, ax ; @112F
    mov di, 0Ch ; @1131
    mov cx, 0488h ; @1134
    cld ; @1137
    xor ax, ax ; @1138
    rep stosb ; @113A
    pop di ; @113C
    pop es ; @113D
    retf ; @113E
loc_113F:
    push ax ; @113F
    push bx ; @1140
    push cx ; @1141
    push dx ; @1142
    push ds ; @1143
    push es ; @1144
    mov ax, 03508h ; @1145
    int 021h ; @1148
    mov word ptr cs:[byte_10CB], bx ; @114A
    mov word ptr cs:[byte_10CD], es ; @114F
    mov ax, seg SOUNDSEG ; @1154
    mov ds, ax ; @1157
    mov dx, offset loc_1179 ; @1159
    mov ax, 02508h ; @115C
    int 021h ; @115F
    xor ax, ax ; @1161
loc_1163:
    cmp ah, 1 ; @1163
    jne short loc_1163 ; @1166
loc_1168:
    mov cx, 0 ; @1168
loc_116B:
    loop loc_116B ; @116B
    inc dx ; @116D
    cmp al, 1 ; @116E
    jne short loc_1168 ; @1170
    pop es ; @1172
    pop ds ; @1173
    pop dx ; @1174
    pop cx ; @1175
    pop bx ; @1176
    pop ax ; @1177
    retf ; @1178
loc_1179:
    push dx ; @1179
    push ds ; @117A
    mov al, 020h ; @117B
    out 020h, al ; @117D
    mov ax, seg SOUNDSEG ; @117F
    mov ds, ax ; @1182
    mov dx, offset loc_1193 ; @1184
    mov ax, 02508h ; @1187
    int 021h ; @118A
    pop ds ; @118C
    pop dx ; @118D
    mov ah, 1 ; @118E
    xor al, al ; @1190
    iret ; @1192
loc_1193:
    push ds ; @1193
    push dx ; @1194
    mov al, 020h ; @1195
    out 020h, al ; @1197
    lds dx, dword ptr cs:[byte_10CB] ; @1199
    mov ax, 02508h ; @119E
    int 021h ; @11A1
    mov word ptr cs:[byte_1127], cx ; @11A3
    pop dx ; @11A8
    mov word ptr cs:[byte_1129], dx ; @11A9
    mov cx, 1 ; @11AE
    mov al, 1 ; @11B1
    pop ds ; @11B3
    iret ; @11B4
loc_11B5:
    push ax ; @11B5
    push cx ; @11B6
    mul byte ptr cs:[byte_1129] ; @11B7
    mov cx, ax ; @11BC
loc_11BE:
    loop loc_11BE ; @11BE
    pop cx ; @11C0
    pop ax ; @11C1
    retf ; @11C2
loc_11C3:
    inc word ptr cs:[byte_023A] ; @11C3
    jne loc_11D2 ; @11C8
    inc word ptr cs:[byte_023C] ; @11CD
loc_11D2:
    test word ptr cs:[byte_0236], 1 ; @11D2
    jne loc_11F1 ; @11D9
    mov word ptr cs:[byte_0236], 1 ; @11DE
    call far ptr loc_1939 ; @11E5 same-segment far call
    mov word ptr cs:[byte_0236], 0 ; @11EA
loc_11F1:
    retf ; @11F1
loc_11F2:
    push dx ; @11F2
    push ax ; @11F3
    mov dx, 0388h ; @11F4
    mov al, bh ; @11F7
    out dx, al ; @11F9
    mov ax, 1 ; @11FA
    call far ptr loc_11B5 ; @11FD same-segment far call
    mov dx, 0389h ; @1201
    mov al, bl ; @1204
    out dx, al ; @1206
    mov ax, 4 ; @1207
    call far ptr loc_11B5 ; @120A same-segment far call
    pop ax ; @120E
    pop dx ; @120F
    retf ; @1210
loc_1211:
    enter 0, 0 ; @1211
    push si ; @1215
    push ax ; @1216
    push bx ; @1217
    push cx ; @1218
    push dx ; @1219
    mov bl, byte ptr [bp + 6] ; @121A
    mov dl, byte ptr [bp + 8] ; @121D
    cmp bl, 9 ; @1220
    jae loc_12DE ; @1223 JUMPS expansion
loc_1228:
    mov ax, 014h ; @1228
    mul bl ; @122B
    mov si, ax ; @122D
    test word ptr cs:[byte_0256], 1 ; @122F
    je loc_126D ; @1236
    cmp word ptr cs:[byte_0274], 0Ch ; @123B
    jb loc_126D ; @1241
    test word ptr cs:[byte_026C], 0Fh ; @1246
    je loc_126D ; @124D
    mov ax, 9 ; @1252
    sub al, byte ptr cs:[byte_026C] ; @1255
    cmp bl, al ; @125A
    jb loc_126D ; @125C
    mov byte ptr cs:[si + byte_0338], dl ; @1261
    pop dx ; @1266
    pop cx ; @1267
    pop bx ; @1268
    pop ax ; @1269
    pop si ; @126A
    leave ; @126B
    retf ; @126C
loc_126D:
    mov byte ptr cs:[si + byte_0284], dl ; @126D
    mov cl, byte ptr cs:[si + byte_0286] ; @1272
    xor bh, bh ; @1277
    mov ch, byte ptr cs:[bx + byte_10F5] ; @1279
    mov al, byte ptr cs:[si + byte_027E] ; @127E
    mov dh, al ; @1283
    and dh, 0C0h ; @1285
    and al, 03Fh ; @1288
    neg al ; @128A
    add al, 03Fh ; @128C
    mul cl ; @128E
    mov al, ah ; @1290
    mul dl ; @1292
    neg ah ; @1294
    add ah, 03Fh ; @1296
    mov al, ah ; @1299
    or al, dh ; @129B
    mov bh, ch ; @129D
    add bh, 043h ; @129F
    mov bl, al ; @12A2
    call far ptr loc_11F2 ; @12A4 same-segment far call
    test word ptr cs:[si + byte_0282], 1 ; @12A8
    je loc_12DE ; @12AF
    mov al, byte ptr cs:[si + byte_0279] ; @12B4
    mov dh, al ; @12B9
    and dh, 0C0h ; @12BB
    and al, 03Fh ; @12BE
    neg al ; @12C0
    add al, 03Fh ; @12C2
    mul cl ; @12C4
    mov al, ah ; @12C6
    mul dl ; @12C8
    neg ah ; @12CA
    add ah, 03Fh ; @12CC
    mov al, ah ; @12CF
    or al, dh ; @12D1
    mov bh, ch ; @12D3
    add bh, 040h ; @12D5
    mov bl, al ; @12D8
    call far ptr loc_11F2 ; @12DA same-segment far call
loc_12DE:
    pop dx ; @12DE
    pop cx ; @12DF
    pop bx ; @12E0
    pop ax ; @12E1
    pop si ; @12E2
    leave ; @12E3
    retf ; @12E4
loc_12E5:
    push ax ; @12E5
    push bx ; @12E6
    push cx ; @12E7
    push dx ; @12E8
    mov dx, word ptr cs:[byte_0246] ; @12E9
    inc dx ; @12EE
    mov word ptr cs:[byte_0246], dx ; @12EF
    mov bx, word ptr cs:[byte_0248] ; @12F4
    cmp dx, bx ; @12F9
    ja loc_131F ; @12FB
    mov cx, word ptr cs:[byte_024A] ; @1300
    mov ax, word ptr cs:[byte_024C] ; @1305
    sub ax, cx ; @1309
    imul dx ; @130B
    idiv bx ; @130D
    add ax, cx ; @130F
    push ax ; @1311
    call far ptr _fn_1128 ; @1312
    add sp, 2 ; @1317
loc_131A:
    pop dx ; @131A
    pop cx ; @131B
    pop bx ; @131C
    pop ax ; @131D
    retf ; @131E
loc_131F:
    mov ax, word ptr cs:[byte_1124] ; @131F
    call far ptr _fn_0A32_021B ; @1323
    mov word ptr cs:[byte_0258], 0 ; @1328
    jmp short loc_131A ; @132F
loc_1331:
    test word ptr cs:[byte_0258], 1 ; @1331
    je loc_134D ; @1338
    mov ax, word ptr cs:[byte_1124] ; @133D
    call far ptr _fn_0A32_021B ; @1341
    mov word ptr cs:[byte_0258], 0 ; @1346
loc_134D:
    retf ; @134D
loc_134E:
    test word ptr cs:[byte_0258], 1 ; @134E
    jne loc_1376 ; @1355
    mov bx, 0D1EBh ; @135A
    mov cx, 1 ; @135D
    mov ax, offset loc_12E5 ; @1360
    mov dx, seg SOUNDSEG ; @1363
    call far ptr _fn_0A32_01AA ; @1366
    mov word ptr cs:[byte_1124], ax ; @136B
    mov word ptr cs:[byte_0258], 1 ; @136F
loc_1376:
    retf ; @1376
loc_1377:
    enter 0, 0 ; @1377
    push es ; @137B
    push ds ; @137C
    push si ; @137D
    push di ; @137E
    push cx ; @137F
    push dx ; @1380
    mov cx, word ptr [bp + 6] ; @1381
    xor ch, ch ; @1384
    cmp cx, 9 ; @1386
    jae loc_14A9 ; @1389 JUMPS expansion
loc_138E:
    lds si, dword ptr [bp + 8] ; @138E
    mov ax, cs ; @1391
    mov es, ax ; @1393
    mov ax, 014h ; @1395
    mul cl ; @1398
    mov di, ax ; @139A
    cmp word ptr cs:[byte_0274], 0Ch ; @139C
    jne loc_13D3 ; @13A2
    test word ptr cs:[byte_026C], 0Fh ; @13A7
    je loc_13D3 ; @13AE
    mov al, 9 ; @13B3
    sub al, byte ptr cs:[byte_026C] ; @13B5
    cmp cl, al ; @13BA
    jb loc_13D3 ; @13BC
    add di, word ptr 032Ch ; @13C1
    cld ; @13C5
    mov cx, 0Ch ; @13C6
    rep movsb ; @13C9
    pop dx ; @13CB
    pop cx ; @13CC
    pop di ; @13CD
    pop si ; @13CE
    pop ds ; @13CF
    pop es ; @13D0
    leave ; @13D1
    retf ; @13D2
loc_13D3:
    add di, word ptr 0278h ; @13D3
    mov al, cl ; @13D7
    cld ; @13D9
    mov cx, 0Ch ; @13DA
    rep movsb ; @13DD
    sub si, 0Ch ; @13DF
    mov cl, al ; @13E2
    xor ah, ah ; @13E4
    mov bx, ax ; @13E6
    mov ch, byte ptr cs:[bx + byte_10F5] ; @13E8
    mov bl, byte ptr [si] ; @13ED
    inc si ; @13EF
    mov bh, ch ; @13F0
    add bh, 020h ; @13F2
    call far ptr loc_11F2 ; @13F5 same-segment far call
    mov bl, byte ptr [si] ; @13F9
    inc si ; @13FB
    mov bh, ch ; @13FC
    add bh, 040h ; @13FE
    test byte ptr [si + 8], 1 ; @1401
    je loc_140D ; @1405
    or bl, 03Fh ; @140A
loc_140D:
    call far ptr loc_11F2 ; @140D same-segment far call
    mov bl, byte ptr [si] ; @1411
    inc si ; @1413
    mov bh, ch ; @1414
    add bh, 060h ; @1416
    call far ptr loc_11F2 ; @1419 same-segment far call
    mov bl, byte ptr [si] ; @141D
    inc si ; @141F
    mov bh, ch ; @1420
    add bh, 080h ; @1422
    call far ptr loc_11F2 ; @1425 same-segment far call
    mov bl, byte ptr [si] ; @1429
    inc si ; @142B
    mov bh, ch ; @142C
    add bh, 0E0h ; @142E
    call far ptr loc_11F2 ; @1431 same-segment far call
    add ch, 3 ; @1435
    mov bl, byte ptr [si] ; @1438
    inc si ; @143A
    mov bh, ch ; @143B
    add bh, 020h ; @143D
    call far ptr loc_11F2 ; @1440 same-segment far call
    mov bl, byte ptr [si] ; @1444
    inc si ; @1446
    mov bh, ch ; @1447
    add bh, 040h ; @1449
    or bl, 03Fh ; @144C
    call far ptr loc_11F2 ; @144F same-segment far call
    mov bl, byte ptr [si] ; @1453
    inc si ; @1455
    mov bh, ch ; @1456
    add bh, 060h ; @1458
    call far ptr loc_11F2 ; @145B same-segment far call
    mov bl, byte ptr [si] ; @145F
    inc si ; @1461
    mov bh, ch ; @1462
    add bh, 080h ; @1464
    call far ptr loc_11F2 ; @1467 same-segment far call
    mov bx, 0120h ; @146B
    call far ptr loc_11F2 ; @146E same-segment far call
    mov bl, byte ptr [si] ; @1472
    inc si ; @1474
    mov bh, ch ; @1475
    add bh, 0E0h ; @1477
    call far ptr loc_11F2 ; @147A same-segment far call
    mov bl, byte ptr [si] ; @147E
    inc si ; @1480
    mov bh, cl ; @1481
    add bh, 0C0h ; @1483
    call far ptr loc_11F2 ; @1486 same-segment far call
    mov ax, 014h ; @148A
    mul cl ; @148D
    mov bx, ax ; @148F
    mov ax, word ptr cs:[byte_0274] ; @1491
    mov word ptr cs:[bx + byte_0288], ax ; @1495
    push word ptr cs:[bx + byte_0284] ; @149A
    push word ptr [bp + 6] ; @149F
    call far ptr loc_1211 ; @14A2 same-segment far call
    add sp, 4 ; @14A6
loc_14A9:
    pop dx ; @14A9
    pop cx ; @14AA
    pop di ; @14AB
    pop si ; @14AC
    pop ds ; @14AD
    pop es ; @14AE
    leave ; @14AF
    retf ; @14B0
loc_14B1:
    enter 0, 0 ; @14B1
    push ax ; @14B5
    push bx ; @14B6
    push dx ; @14B7
    mov bx, word ptr [bp + 6] ; @14B8
    cmp bl, 9 ; @14BB
    jae loc_14FE ; @14BE
    mov ah, bl ; @14C3
    push ax ; @14C5
    mov ax, 014h ; @14C6
    mul bl ; @14C9
    mov bx, ax ; @14CB
    mov dl, byte ptr cs:[bx + byte_028B] ; @14CD
    and dl, 0DFh ; @14D2
    mov byte ptr cs:[bx + byte_028B], dl ; @14D5
    pop ax ; @14DA
    mov bh, ah ; @14DB
    add bh, 0B0h ; @14DD
    mov ah, dl ; @14E0
    mov dx, 0388h ; @14E2
    mov al, bh ; @14E5
    out dx, al ; @14E7
    mov bh, ah ; @14E8
    mov ax, 1 ; @14EA
    call far ptr loc_11B5 ; @14ED same-segment far call
    mov dx, 0389h ; @14F1
    mov al, bh ; @14F4
    out dx, al ; @14F6
    mov ax, 2 ; @14F7
    call far ptr loc_11B5 ; @14FA same-segment far call
loc_14FE:
    pop dx ; @14FE
    pop bx ; @14FF
    pop ax ; @1500
    leave ; @1501
    retf ; @1502
loc_1503:
    enter 0, 0 ; @1503
    push ax ; @1507
    push bx ; @1508
    push cx ; @1509
    push dx ; @150A
    mov cl, byte ptr [bp + 6] ; @150B
    cmp cl, 9 ; @150E
    jae loc_156B ; @1511
    mov ax, 014h ; @1516
    mul cl ; @1519
    mov bx, ax ; @151B
    mov ax, word ptr [bp + 8] ; @151D
    mov word ptr cs:[bx + byte_028A], ax ; @1520
    cli ; @1525
    mov bh, cl ; @1526
    add bh, 0A0h ; @1528
    mov bl, al ; @152B
    push ax ; @152D
    mov dx, 0388h ; @152E
    mov al, bh ; @1531
    out dx, al ; @1533
    mov ax, 1 ; @1534
    call far ptr loc_11B5 ; @1537 same-segment far call
    mov dx, 0389h ; @153B
    mov al, bl ; @153E
    out dx, al ; @1540
    mov ax, 3 ; @1541
    call far ptr loc_11B5 ; @1544 same-segment far call
    pop ax ; @1548
    mov bl, ah ; @1549
    mov bh, cl ; @154B
    add bh, 0B0h ; @154D
    mov dx, 0388h ; @1550
    mov al, bh ; @1553
    out dx, al ; @1555
    mov ax, 1 ; @1556
    call far ptr loc_11B5 ; @1559 same-segment far call
    mov dx, 0389h ; @155D
    mov al, bl ; @1560
    out dx, al ; @1562
    sti ; @1563
    mov ax, 2 ; @1564
    call far ptr loc_11B5 ; @1567 same-segment far call
loc_156B:
    pop dx ; @156B
    pop cx ; @156C
    pop bx ; @156D
    pop ax ; @156E
    leave ; @156F
    retf ; @1570
loc_1571:
    enter 0, 0 ; @1571
    push cx ; @1575
    push dx ; @1576
    push si ; @1577
    mov cl, byte ptr [bp + 6] ; @1578
    cmp cl, 9 ; @157B
    jae loc_15B7 ; @157E
    mov dl, byte ptr [bp + 8] ; @1583
    mov ax, 014h ; @1586
    mul cl ; @1589
    mov si, ax ; @158B
    cmp word ptr cs:[byte_0274], 0Ch ; @158D
    jb loc_15BC ; @1593
    test word ptr cs:[byte_026C], 0Fh ; @1598
    je loc_15BC ; @159F
    mov bl, 9 ; @15A4
    sub bl, byte ptr cs:[byte_026C] ; @15A6
    cmp cl, bl ; @15AB
    jb loc_15BC ; @15AD
    mov byte ptr cs:[si + byte_033A], dl ; @15B2
loc_15B7:
    pop si ; @15B7
    pop dx ; @15B8
    pop cx ; @15B9
    leave ; @15BA
    retf ; @15BB
loc_15BC:
    mov byte ptr cs:[si + byte_0286], dl ; @15BC
    push word ptr cs:[si + byte_0284] ; @15C1
    push cx ; @15C6
    call far ptr loc_1211 ; @15C7 same-segment far call
    add sp, 4 ; @15CB
    pop si ; @15CE
    pop dx ; @15CF
    pop cx ; @15D0
    leave ; @15D1
    retf ; @15D2
loc_15D3:
    mov al, byte ptr es:[di] ; @15D3
    inc di ; @15D6
    xor ah, ah ; @15D7
    mov bx, ax ; @15D9
    shr bx, 3 ; @15DB
    and bx, 0FFFEh ; @15DE
    add bx, offset byte_174B ; @15E1
    jmp word ptr cs:[bx] ; @15E5
loc_15E8:
    push dx ; @15E8
    mov dl, byte ptr es:[di] ; @15E9
    inc di ; @15EC
    mov dh, al ; @15ED
    and dh, 0Fh ; @15EF
    shl dx, 7 ; @15F2
    add word ptr cs:[byte_022A], dx ; @15F5
    adc word ptr cs:[byte_022C], 0 ; @15FA
    mov word ptr cs:[byte_021C], di ; @1600
    pop dx ; @1605
    retf ; @1606
loc_1607:
    and al, 0Fh ; @1607
    cmp al, 9 ; @1609
    jae loc_1639 ; @160B
    push dx ; @1610
    push cx ; @1611
    push si ; @1612
    mov cl, al ; @1613
    mov ax, word ptr es:[di] ; @1615
    add di, 2 ; @1618
    mov bl, 9 ; @161B
    sub bl, byte ptr cs:[byte_026C] ; @161D
    cmp cl, bl ; @1622
    jb loc_163B ; @1624
    push ax ; @1629
    mov ax, 014h ; @162A
    mul cl ; @162D
    mov bx, ax ; @162F
    pop word ptr cs:[bx + byte_033E] ; @1631
    pop si ; @1636
    pop cx ; @1637
    pop dx ; @1638
loc_1639:
    jmp short loc_15D3 ; @1639
loc_163B:
    push ax ; @163B
    push cx ; @163C
    call far ptr loc_1503 ; @163D same-segment far call
    add sp, 4 ; @1641
    pop si ; @1644
    pop cx ; @1645
    pop dx ; @1646
    jmp short loc_15D3 ; @1647
loc_1649:
    and al, 0Fh ; @1649
    cmp al, 9 ; @164B
    jae loc_166F ; @164D
    mov bl, 9 ; @1652
    sub bl, byte ptr cs:[byte_026C] ; @1654
    cmp al, bl ; @1659
    jb loc_1672 ; @165B
    mov bl, al ; @1660
    mov ax, 014h ; @1662
    mul bl ; @1665
    mov bx, ax ; @1667
    and word ptr cs:[bx + byte_033E], 0FFDFh ; @1669
loc_166F:
    jmp near ptr loc_15D3 ; @166F
loc_1672:
    push ax ; @1672
    call far ptr loc_14B1 ; @1673 same-segment far call
    add sp, 2 ; @1677
    jmp near ptr loc_15D3 ; @167A
loc_167D:
    and al, 0Fh ; @167D
    cmp al, 9 ; @167F
    jae loc_1692 ; @1681
    mov bl, byte ptr es:[di] ; @1686
    push bx ; @1689
    push ax ; @168A
    call far ptr loc_1571 ; @168B same-segment far call
    add sp, 4 ; @168F
loc_1692:
    inc di ; @1692
    jmp near ptr loc_15D3 ; @1693
loc_1696:
    and al, 0Fh ; @1696
    cmp al, 9 ; @1698
    jae loc_16AC ; @169A
    push es ; @169F
    push di ; @16A0
    push ax ; @16A1
    call far ptr loc_1377 ; @16A2 same-segment far call
    add sp, 6 ; @16A6
    add di, 0Bh ; @16A9
loc_16AC:
    jmp near ptr loc_15D3 ; @16AC
loc_16AF:
    jmp near ptr loc_15D3 ; @16AF
loc_16B2:
    push cx ; @16B2
    mov bx, word ptr es:[di] ; @16B3
    xchg bl, bh ; @16B6
    mov word ptr cs:[byte_000C], bx ; @16B8
    mov ax, word ptr cs:[byte_1122] ; @16BD
    xor cx, cx ; @16C1
    call far ptr _fn_0A32_02C1 ; @16C3
    inc di ; @16C8
    inc di ; @16C9
    pop cx ; @16CA
    jmp near ptr loc_15D3 ; @16CB
loc_16CE:
    cmp al, 077h ; @16CE
    je loc_16F1 ; @16D0
    mov ah, byte ptr es:[di] ; @16D5
    inc di ; @16D8
    and al, 0Fh ; @16D9
    cmp al, 0 ; @16DB
    je loc_16EB ; @16DD
    mov al, ah ; @16E2
    xor ah, ah ; @16E4
    add di, ax ; @16E6
    jmp near ptr loc_15D3 ; @16E8
loc_16EB:
    add di, 2 ; @16EB
    jmp near ptr loc_15D3 ; @16EE
loc_16F1:
    test word ptr cs:[byte_0234], 2 ; @16F1
    jne loc_170E ; @16F8
    dec word ptr cs:[byte_0210] ; @16FD
    jg loc_170E ; @1702
    and word ptr cs:[byte_0234], 0FFFEh ; @1707
    retf ; @170D
loc_170E:
    mov ax, word ptr cs:[byte_0214] ; @170E
    mov word ptr cs:[byte_021E], ax ; @1712
    mov ax, word ptr cs:[byte_0212] ; @1716
    mov word ptr cs:[byte_021C], ax ; @171A
    mov ax, word ptr cs:[byte_023A] ; @171E
    mov word ptr cs:[byte_022A], ax ; @1722
    mov word ptr cs:[byte_023E], ax ; @1726
    mov ax, word ptr cs:[byte_023C] ; @172A
    mov word ptr cs:[byte_022C], ax ; @172E
    mov word ptr cs:[byte_0240], ax ; @1732
    retf ; @1736
loc_1737:
    and ax, word ptr 07Fh ; @1737
    add word ptr cs:[byte_022A], ax ; @173A
    adc word ptr cs:[byte_022C], 0 ; @173F
    mov word ptr cs:[byte_021C], di ; @1745
    retf ; @174A
byte_data_174B:
    dw offset loc_15E8
    dw offset loc_1607
    dw offset loc_1649
    dw offset loc_167D
    dw offset loc_1696
    dw offset loc_16AF
    dw offset loc_16B2
    dw offset loc_16CE
    dw offset loc_1737
    dw offset loc_1737
    dw offset loc_1737
    dw offset loc_1737
    dw offset loc_1737
    dw offset loc_1737
    dw offset loc_1737
    dw offset loc_1737
loc_176B:
    mov al, byte ptr es:[di] ; @176B
    inc di ; @176E
    xor ah, ah ; @176F
    mov bx, ax ; @1771
    shr bx, 3 ; @1773
    and bx, 0FFFEh ; @1776
    add bx, offset byte_1919 ; @1779
    jmp word ptr cs:[bx] ; @177D
loc_1780:
    push dx ; @1780
    mov dl, byte ptr es:[di] ; @1781
    inc di ; @1784
    mov dh, al ; @1785
    and dh, 0Fh ; @1787
    shl dx, 7 ; @178A
    mov bx, word ptr cs:[byte_10EF] ; @178D
    mov ax, dx ; @1792
    xor dx, dx ; @1794
    mul word ptr cs:[bx + 026h] ; @1796
    mov al, ah ; @179A
    mov ah, dl ; @179C
    mov dl, dh ; @179E
    xor dh, dh ; @17A0
    add word ptr cs:[bx + 01Eh], ax ; @17A2
    adc word ptr cs:[bx + 020h], dx ; @17A6
    mov word ptr cs:[bx + 010h], di ; @17AA
    pop dx ; @17AE
    retf ; @17AF
loc_17B0:
    and al, 0Fh ; @17B0
    mov bx, word ptr cs:[byte_10EF] ; @17B2
    add al, byte ptr cs:[bx + 024h] ; @17B7
    cmp al, 9 ; @17BB
    jae loc_17D0 ; @17BD
    push word ptr es:[di] ; @17C2
    push ax ; @17C5
    call far ptr loc_1503 ; @17C6 same-segment far call
    add sp, 4 ; @17CA
    add di, 2 ; @17CD
loc_17D0:
    jmp short loc_176B ; @17D0
loc_17D2:
    and al, 0Fh ; @17D2
    mov bx, word ptr cs:[byte_10EF] ; @17D4
    add al, byte ptr cs:[bx + 024h] ; @17D9
    cmp al, 9 ; @17DD
    jae loc_17EC ; @17DF
    push ax ; @17E4
    call far ptr loc_14B1 ; @17E5 same-segment far call
    add sp, 2 ; @17E9
loc_17EC:
    jmp near ptr loc_176B ; @17EC
loc_17EF:
    and al, 0Fh ; @17EF
    mov bx, word ptr cs:[byte_10EF] ; @17F1
    add al, byte ptr cs:[bx + 024h] ; @17F6
    cmp al, 9 ; @17FA
    jae loc_180C ; @17FC
    push word ptr es:[di] ; @1801
    push ax ; @1804
    call far ptr loc_1571 ; @1805 same-segment far call
    add sp, 4 ; @1809
loc_180C:
    inc di ; @180C
    jmp near ptr loc_176B ; @180D
loc_1810:
    and al, 0Fh ; @1810
    mov bx, word ptr cs:[byte_10EF] ; @1812
    add al, byte ptr cs:[bx + 024h] ; @1817
    cmp al, 9 ; @181B
    ja loc_1844 ; @181D
    push ax ; @1822
    push word ptr cs:[byte_0274] ; @1823
    mov bl, al ; @1828
    mov ax, 014h ; @182A
    mul bl ; @182D
    mov bx, ax ; @182F
    pop word ptr cs:[bx + byte_0288] ; @1831
    pop ax ; @1836
    push es ; @1837
    push di ; @1838
    push ax ; @1839
    call far ptr loc_1377 ; @183A same-segment far call
    add sp, 6 ; @183E
    add di, 0Bh ; @1841
loc_1844:
    jmp near ptr loc_176B ; @1844
loc_1847:
    jmp near ptr loc_176B ; @1847
loc_184A:
    push cx ; @184A
    push dx ; @184B
    test word ptr cs:[byte_0256], 1 ; @184C
    jne loc_187C ; @1853
    test word ptr cs:[byte_000C], 0FFFFh ; @1858
    jne loc_187C ; @185F
    mov bx, word ptr es:[di] ; @1864
    xchg bl, bh ; @1867
    mov word ptr cs:[byte_000C], bx ; @1869
    mov ax, word ptr cs:[byte_1122] ; @186E
    xor cx, cx ; @1872
    call far ptr _fn_0A32_02C1 ; @1874
    jmp loc_1895 ; @1879
loc_187C:
    xor dx, dx ; @187C
    mov bx, word ptr cs:[byte_000C] ; @187E
    mov ax, word ptr es:[di] ; @1883
    mov dl, al ; @1886
    xor al, al ; @1888
    div bx ; @188A
    mov bx, word ptr cs:[byte_10EF] ; @188C
    mov word ptr cs:[bx + 026h], ax ; @1891
loc_1895:
    inc di ; @1895
    inc di ; @1896
    pop dx ; @1897
    pop cx ; @1898
    jmp near ptr loc_176B ; @1899
loc_189C:
    cmp al, 077h ; @189C
    je loc_18BF ; @189E
    mov ah, byte ptr es:[di] ; @18A3
    inc di ; @18A6
    and al, 0Fh ; @18A7
    cmp al, 0 ; @18A9
    je loc_18B9 ; @18AB
    mov al, ah ; @18B0
    xor ah, ah ; @18B2
    add di, ax ; @18B4
    jmp near ptr loc_176B ; @18B6
loc_18B9:
    add di, 2 ; @18B9
    jmp near ptr loc_176B ; @18BC
loc_18BF:
    mov bx, word ptr cs:[byte_10EF] ; @18BF
    test word ptr cs:[bx + 028h], 2 ; @18C4
    jne loc_18E6 ; @18CA
    dec word ptr cs:[bx + 4] ; @18CF
    jg loc_18E6 ; @18D3
    push word ptr cs:[byte_0274] ; @18D8
    call far ptr _fn_1768 ; @18DD
    add sp, 2 ; @18E2
    retf ; @18E5
loc_18E6:
    mov ax, word ptr cs:[bx + 8] ; @18E6
    mov word ptr cs:[bx + 012h], ax ; @18EA
    mov ax, word ptr cs:[bx + 6] ; @18EE
    mov word ptr cs:[bx + 010h], ax ; @18F2
    retf ; @18F6
loc_18F7:
    push dx ; @18F7
    and ax, word ptr 07Fh ; @18F8
    xor dx, dx ; @18FB
    mov bx, word ptr cs:[byte_10EF] ; @18FD
    mul word ptr cs:[bx + 026h] ; @1902
    mov al, ah ; @1906
    mov ah, dl ; @1908
    add word ptr cs:[bx + 01Eh], ax ; @190A
    adc word ptr cs:[bx + 020h], 0 ; @190E
    mov word ptr cs:[bx + 010h], di ; @1913
    pop dx ; @1917
    retf ; @1918
byte_data_1919:
    dw offset loc_1780
    dw offset loc_17B0
    dw offset loc_17D2
    dw offset loc_17EF
    dw offset loc_1810
    dw offset loc_1847
    dw offset loc_184A
    dw offset loc_189C
    dw offset loc_18F7
    dw offset loc_18F7
    dw offset loc_18F7
    dw offset loc_18F7
    dw offset loc_18F7
    dw offset loc_18F7
    dw offset loc_18F7
    dw offset loc_18F7
loc_1939:
    inc word ptr cs:[byte_023A] ; @1939
    jne loc_1948 ; @193E
    inc word ptr cs:[byte_023C] ; @1943
loc_1948:
    test word ptr cs:[byte_0236], 1 ; @1948
    jne loc_1A36 ; @194F JUMPS expansion
loc_1954:
    mov word ptr cs:[byte_0236], 1 ; @1954
    push ax ; @195B
    push bx ; @195C
    push dx ; @195D
    test word ptr cs:[byte_0256], 1 ; @195E
    je loc_19C9 ; @1965
    mov dx, word ptr cs:[byte_023C] ; @196A
    cmp dx, word ptr cs:[byte_022C] ; @196F
    jb loc_19C9 ; @1974
    ja loc_198C ; @1979
    mov ax, word ptr cs:[byte_023A] ; @197E
    cmp ax, word ptr cs:[byte_022A] ; @1982
    jb loc_19C9 ; @1987
loc_198C:
    mov word ptr cs:[byte_10EF], 020Ch ; @198C
    mov word ptr cs:[byte_0274], 0Ch ; @1993
    push es ; @199A
    push di ; @199B
    push bx ; @199C
    les di, dword ptr cs:[byte_021C] ; @199D
    test word ptr cs:[byte_025C], 1 ; @19A2
    je loc_19C2 ; @19A9
    cmp di, word ptr cs:[byte_0262] ; @19AE
    jb loc_19C2 ; @19B3
    call far ptr _fn_1943 ; @19B8
    les di, dword ptr cs:[byte_021C] ; @19BD
loc_19C2:
    call far ptr loc_15D3 ; @19C2 same-segment far call
    pop bx ; @19C6
    pop di ; @19C7
    pop es ; @19C8
loc_19C9:
    test word ptr cs:[byte_026C], 0Fh ; @19C9
    je loc_1A2C ; @19D0
    mov bx, 0164h ; @19D5
    mov word ptr cs:[byte_0274], 8 ; @19D8
loc_19DF:
    mov al, byte ptr cs:[bx + 028h] ; @19DF
    and al, 5 ; @19E3
    cmp al, 5 ; @19E5
    jne loc_1A1E ; @19E7
    mov ax, word ptr cs:[byte_023C] ; @19EC
    cmp ax, word ptr cs:[bx + 020h] ; @19F0
    jb loc_1A1E ; @19F4
    ja loc_1A0B ; @19F9
    mov ax, word ptr cs:[byte_023A] ; @19FE
    cmp ax, word ptr cs:[bx + 01Eh] ; @1A02
    jb loc_1A1E ; @1A06
loc_1A0B:
    mov word ptr cs:[byte_10EF], bx ; @1A0B
    push es ; @1A10
    push di ; @1A11
    push bx ; @1A12
    les di, dword ptr cs:[bx + 010h] ; @1A13
    call far ptr loc_176B ; @1A17 same-segment far call
    pop bx ; @1A1B
    pop di ; @1A1C
    pop es ; @1A1D
loc_1A1E:
    inc word ptr cs:[byte_0274] ; @1A1E
    add bx, 02Ah ; @1A23
    cmp bx, word ptr 020Ch ; @1A26
    jb short loc_19DF ; @1A2A
loc_1A2C:
    mov word ptr cs:[byte_0236], 0 ; @1A2C
    pop dx ; @1A33
    pop bx ; @1A34
    pop ax ; @1A35
loc_1A36:
    retf ; @1A36
loc_1A37:
    push si ; @1A37
    mov bx, 0100h ; @1A38
    call far ptr loc_11F2 ; @1A3B same-segment far call
    mov bx, 0120h ; @1A3F
    call far ptr loc_11F2 ; @1A42 same-segment far call
    mov cx, 9 ; @1A46
    xor si, si ; @1A49
loc_1A4B:
    mov bh, byte ptr cs:[si + byte_10F5] ; @1A4B
    add bh, 040h ; @1A50
    mov bl, 03Fh ; @1A53
    call far ptr loc_11F2 ; @1A55 same-segment far call
    add bh, 3 ; @1A59
    call far ptr loc_11F2 ; @1A5C same-segment far call
    inc si ; @1A60
    loop loc_1A4B ; @1A61
    pop si ; @1A63
    retf ; @1A64
loc_1A65:
    cmp byte ptr cs:[byte_1126], 0 ; @1A65
    je loc_1A79 ; @1A6B
    mov ax, word ptr cs:[byte_1122] ; @1A70
    call far ptr _fn_0A32_021B ; @1A74
loc_1A79:
    call far ptr _fn_0A32_00A0 ; @1A79
    mov byte ptr cs:[byte_1126], 0 ; @1A7E
    call far ptr loc_1A37 ; @1A84 same-segment far call
    retf ; @1A88
loc_1A89:
    push es ; @1A89
    push di ; @1A8A
    push si ; @1A8B
    cmp byte ptr cs:[byte_1126], 0 ; @1A8C
    jne loc_1B2D ; @1A92 JUMPS expansion
loc_1A97:
    mov byte ptr cs:[byte_1126], 1 ; @1A97
    call far ptr loc_113F ; @1A9D same-segment far call
    mov bx, 0100h ; @1AA1
    call far ptr loc_11F2 ; @1AA4 same-segment far call
    mov bx, 0460h ; @1AA8
    call far ptr loc_11F2 ; @1AAB same-segment far call
    mov al, 014h ; @1AAF
    call far ptr loc_11B5 ; @1AB1 same-segment far call
    mov bx, 0480h ; @1AB5
    call far ptr loc_11F2 ; @1AB8 same-segment far call
    mov al, 014h ; @1ABC
    call far ptr loc_11B5 ; @1ABE same-segment far call
    mov dx, 0388h ; @1AC2
    in al, dx ; @1AC5
    test al, 0E0h ; @1AC6
    jne loc_1B34 ; @1AC8
    mov bx, 02FFh ; @1ACD
    call far ptr loc_11F2 ; @1AD0 same-segment far call
    mov al, 014h ; @1AD4
    call far ptr loc_11B5 ; @1AD6 same-segment far call
    mov bx, 0421h ; @1ADA
    call far ptr loc_11F2 ; @1ADD same-segment far call
    mov al, 0FFh ; @1AE1
    call far ptr loc_11B5 ; @1AE3 same-segment far call
    in al, dx ; @1AE7
    test al, 0E0h ; @1AE8
    je loc_1B34 ; @1AEA
    mov bx, 0460h ; @1AEF
    call far ptr loc_11F2 ; @1AF2 same-segment far call
    mov al, 014h ; @1AF6
    call far ptr loc_11B5 ; @1AF8 same-segment far call
    mov bx, 0480h ; @1AFC
    call far ptr loc_11F2 ; @1AFF same-segment far call
    mov al, 014h ; @1B03
    call far ptr loc_11B5 ; @1B05 same-segment far call
    call far ptr loc_1A37 ; @1B09 same-segment far call
    mov bx, 0120h ; @1B0D
    call far ptr loc_11F2 ; @1B10 same-segment far call
    call far ptr _fn_0A32_0008 ; @1B14
    mov bx, 01843h ; @1B19
    xor cx, cx ; @1B1C
    mov ax, offset loc_1939 ; @1B1E
    mov dx, seg SOUNDSEG ; @1B21
    call far ptr _fn_0A32_01AA ; @1B24
    mov word ptr cs:[byte_1122], ax ; @1B29
loc_1B2D:
    mov ax, 1 ; @1B2D
    pop si ; @1B30
    pop di ; @1B31
    pop es ; @1B32
    retf ; @1B33
loc_1B34:
    xor ax, ax ; @1B34
    pop si ; @1B36
    pop di ; @1B37
    pop es ; @1B38
    retf ; @1B39
loc_1B3A:
    push dx ; @1B3A
    push bx ; @1B3B
    mov bx, 02Ah ; @1B3C
    mul bx ; @1B3F
    mov bx, ax ; @1B41
    mov word ptr cs:[bx + byte_0024], 0 ; @1B43
    pop bx ; @1B4A
    pop dx ; @1B4B
    retf ; @1B4C
loc_1B4D:
    push dx ; @1B4D
    push ax ; @1B4E
    push cx ; @1B4F
    mov ah, al ; @1B50
    mov dx, word ptr cs:[byte_0010] ; @1B52
    add dx, 0Ch ; @1B57
    xor cx, cx ; @1B5A
loc_1B5C:
    jmp loc_1B61 ; @1B5C
    nop ; @1B5F
    nop ; @1B60
loc_1B61:
    jmp loc_1B66 ; @1B61
    nop ; @1B64
    nop ; @1B65
loc_1B66:
    jmp loc_1B6B ; @1B66
    nop ; @1B69
    nop ; @1B6A
loc_1B6B:
    in al, dx ; @1B6B
    test al, 080h ; @1B6C
    loopne loc_1B5C ; @1B6E
    mov al, ah ; @1B70
    out dx, al ; @1B72
    pop cx ; @1B73
    pop ax ; @1B74
    pop dx ; @1B75
    retf ; @1B76
loc_1B77:
    push cx ; @1B77
    dec bx ; @1B78
    mov al, 5 ; @1B79
    out 0Ah, al ; @1B7B
    jmp loc_1B82 ; @1B7D
    nop ; @1B80
    nop ; @1B81
loc_1B82:
    jmp loc_1B87 ; @1B82
    nop ; @1B85
    nop ; @1B86
loc_1B87:
    jmp loc_1B8C ; @1B87
    nop ; @1B8A
    nop ; @1B8B
loc_1B8C:
    mov al, 0 ; @1B8C
    out 0Ch, al ; @1B8E
    jmp loc_1B95 ; @1B90
    nop ; @1B93
    nop ; @1B94
loc_1B95:
    jmp loc_1B9A ; @1B95
    nop ; @1B98
    nop ; @1B99
loc_1B9A:
    jmp loc_1B9F ; @1B9A
    nop ; @1B9D
    nop ; @1B9E
loc_1B9F:
    mov al, 049h ; @1B9F
    out 0Bh, al ; @1BA1
    jmp loc_1BA8 ; @1BA3
    nop ; @1BA6
    nop ; @1BA7
loc_1BA8:
    jmp loc_1BAD ; @1BA8
    nop ; @1BAB
    nop ; @1BAC
loc_1BAD:
    jmp loc_1BB2 ; @1BAD
    nop ; @1BB0
    nop ; @1BB1
loc_1BB2:
    mov al, dl ; @1BB2
    out 2, al ; @1BB4
    jmp loc_1BBB ; @1BB6
    nop ; @1BB9
    nop ; @1BBA
loc_1BBB:
    jmp loc_1BC0 ; @1BBB
    nop ; @1BBE
    nop ; @1BBF
loc_1BC0:
    jmp loc_1BC5 ; @1BC0
    nop ; @1BC3
    nop ; @1BC4
loc_1BC5:
    mov al, dh ; @1BC5
    out 2, al ; @1BC7
    jmp loc_1BCE ; @1BC9
    nop ; @1BCC
    nop ; @1BCD
loc_1BCE:
    jmp loc_1BD3 ; @1BCE
    nop ; @1BD1
    nop ; @1BD2
loc_1BD3:
    jmp loc_1BD8 ; @1BD3
    nop ; @1BD6
    nop ; @1BD7
loc_1BD8:
    mov al, ch ; @1BD8
    out 083h, al ; @1BDA
    jmp loc_1BE1 ; @1BDC
    nop ; @1BDF
    nop ; @1BE0
loc_1BE1:
    jmp loc_1BE6 ; @1BE1
    nop ; @1BE4
    nop ; @1BE5
loc_1BE6:
    jmp loc_1BEB ; @1BE6
    nop ; @1BE9
    nop ; @1BEA
loc_1BEB:
    mov al, bl ; @1BEB
    out 3, al ; @1BED
    jmp loc_1BF4 ; @1BEF
    nop ; @1BF2
    nop ; @1BF3
loc_1BF4:
    jmp loc_1BF9 ; @1BF4
    nop ; @1BF7
    nop ; @1BF8
loc_1BF9:
    jmp loc_1BFE ; @1BF9
    nop ; @1BFC
    nop ; @1BFD
loc_1BFE:
    mov al, bh ; @1BFE
    out 3, al ; @1C00
    jmp loc_1C07 ; @1C02
    nop ; @1C05
    nop ; @1C06
loc_1C07:
    jmp loc_1C0C ; @1C07
    nop ; @1C0A
    nop ; @1C0B
loc_1C0C:
    jmp loc_1C11 ; @1C0C
    nop ; @1C0F
    nop ; @1C10
loc_1C11:
    mov al, 1 ; @1C11
    out 0Ah, al ; @1C13
    jmp loc_1C1A ; @1C15
    nop ; @1C18
    nop ; @1C19
loc_1C1A:
    jmp loc_1C1F ; @1C1A
    nop ; @1C1D
    nop ; @1C1E
loc_1C1F:
    jmp loc_1C24 ; @1C1F
    nop ; @1C22
    nop ; @1C23
loc_1C24:
    mov al, 014h ; @1C24
    call far ptr loc_1B4D ; @1C26 same-segment far call
    mov al, bl ; @1C2A
    call far ptr loc_1B4D ; @1C2C same-segment far call
    mov al, bh ; @1C30
    call far ptr loc_1B4D ; @1C32 same-segment far call
    inc bx ; @1C36
    pop cx ; @1C37
    retf ; @1C38
loc_1C39:
    enter 0, 0 ; @1C39
    push ax ; @1C3D
    push bx ; @1C3E
    push dx ; @1C3F
    test word ptr cs:[byte_026A], 2 ; @1C40
    je loc_1C6F ; @1C47
    cmp word ptr [bp + 6], word ptr 03E8h ; @1C4C
    jb loc_1C6F ; @1C51
    mov dx, 0Fh ; @1C56
    mov ax, 04240h ; @1C59
    div word ptr [bp + 6] ; @1C5C
    neg ax ; @1C5F
    mov bx, ax ; @1C61
    mov al, 040h ; @1C63
    call far ptr loc_1B4D ; @1C65 same-segment far call
    mov al, bl ; @1C69
    call far ptr loc_1B4D ; @1C6B same-segment far call
loc_1C6F:
    pop dx ; @1C6F
    pop bx ; @1C70
    pop ax ; @1C71
    leave ; @1C72
    retf ; @1C73
loc_1C74:
    mov ax, seg SOUNDSEG ; @1C74
    mov cx, ax ; @1C77
    shr ch, 4 ; @1C79
    shl ax, 4 ; @1C7C
    add ax, word ptr 04AFh ; @1C7F
    adc ch, 0 ; @1C82
    mov word ptr cs:[byte_04AB], ax ; @1C85
    mov word ptr cs:[byte_04AD], 04AFh ; @1C89
    mov byte ptr cs:[byte_04A9], ch ; @1C90
    add ax, word ptr 0400h ; @1C95
    jae loc_1CB6 ; @1C98
    sub ax, word ptr 0400h ; @1C9D
    add ax, word ptr 0814h ; @1CA0
    adc ch, 0 ; @1CA3
    mov byte ptr cs:[byte_04A9], ch ; @1CA6
    mov word ptr cs:[byte_04AB], ax ; @1CAB
    mov word ptr cs:[byte_04AD], 0CC3h ; @1CAF
loc_1CB6:
    mov ax, seg SOUNDSEG ; @1CB6
    mov cx, ax ; @1CB9
    shr ch, 4 ; @1CBB
    shl ax, 4 ; @1CBE
    add ax, word ptr 08B9h ; @1CC1
    adc ch, 0 ; @1CC4
    mov word ptr cs:[byte_08B5], ax ; @1CC7
    mov word ptr cs:[byte_08B7], 08B9h ; @1CCB
    mov byte ptr cs:[byte_08B3], ch ; @1CD2
    add ax, word ptr 0400h ; @1CD7
    jae loc_1CF8 ; @1CDA
    sub ax, word ptr 0400h ; @1CDF
    add ax, word ptr 040Ah ; @1CE2
    adc ch, 0 ; @1CE5
    mov byte ptr cs:[byte_08B3], ch ; @1CE8
    mov word ptr cs:[byte_08B5], ax ; @1CED
    mov word ptr cs:[byte_08B7], 0CC3h ; @1CF1
loc_1CF8:
    retf ; @1CF8
loc_1CF9:
    xor ax, ax ; @1CF9
    cmp word ptr cs:[byte_026E], 0 ; @1CFB
    je loc_1DD5 ; @1D01 JUMPS expansion
loc_1D06:
    mov word ptr cs:[byte_000E], 1 ; @1D06
    pusha ; @1D0D
    push ds ; @1D0E
    shr bx, 1 ; @1D0F
    mov word ptr cs:[byte_10C7], bx ; @1D11
    mov di, dx ; @1D16
    xor bp, bp ; @1D18
    mov word ptr cs:[byte_10CF], 0 ; @1D1A
    mov word ptr cs:[byte_10D1], 0 ; @1D21
    mov cl, 1 ; @1D28
loc_1D2A:
    test byte ptr cs:[byte_0270], cl ; @1D2A
    je loc_1D7D ; @1D2F
    lds bx, dword ptr cs:[bp + byte_001A] ; @1D34
    mov ax, word ptr cs:[bp + byte_0024] ; @1D39
    mul word ptr cs:[bp + byte_003A] ; @1D3E
    mov al, ah ; @1D43
    mov ah, dl ; @1D45
    cmp ax, word ptr cs:[bp + byte_001E] ; @1D47
    jae loc_1DD6 ; @1D4C JUMPS expansion
loc_1D51:
    add ax, bx ; @1D51
    mov si, ax ; @1D53
    mov ch, byte ptr cs:[bp + byte_0030] ; @1D55
    shr ch, 1 ; @1D5A
    mov dx, word ptr [si] ; @1D5C
    mov al, dl ; @1D5E
    imul ch ; @1D60
    mov al, ah ; @1D62
    cbw ; @1D64
    add word ptr cs:[byte_10CF], ax ; @1D65
    mov al, dh ; @1D6A
    imul ch ; @1D6C
    mov al, ah ; @1D6E
    cbw ; @1D70
    add word ptr cs:[byte_10D1], ax ; @1D71
    inc word ptr cs:[bp + byte_0024] ; @1D76
    sub si, bx ; @1D7B
loc_1D7D:
    add bp, 02Ah ; @1D7D
    shl cl, 1 ; @1D80
    jae short loc_1D2A ; @1D82
    mov ax, word ptr cs:[byte_10CF] ; @1D84
    cwd ; @1D88
    idiv word ptr cs:[byte_026E] ; @1D89
    add ax, word ptr 07Fh ; @1D8E
    mov byte ptr cs:[di], al ; @1D91
    inc di ; @1D94
    mov ax, word ptr cs:[byte_10D1] ; @1D95
    cwd ; @1D99
    idiv word ptr cs:[byte_026E] ; @1D9A
    add ax, word ptr 07Fh ; @1D9F
    mov byte ptr cs:[di], al ; @1DA2
    inc di ; @1DA5
    dec word ptr cs:[byte_10C7] ; @1DA6
    jle loc_1DC5 ; @1DAB
    mov word ptr cs:[byte_10CF], 0 ; @1DB0
    mov word ptr cs:[byte_10D1], 0 ; @1DB7
    mov cl, 1 ; @1DBE
    xor bp, bp ; @1DC0
    jmp near ptr loc_1D2A ; @1DC2
loc_1DC5:
    mov word ptr cs:[byte_000E], 0 ; @1DC5
    pop ds ; @1DCC
    popa ; @1DCD
    mov ax, bx ; @1DCE
    sub ax, word ptr cs:[byte_10C7] ; @1DD0
loc_1DD5:
    retf ; @1DD5
loc_1DD6:
    test word ptr cs:[bp + byte_003C], 2 ; @1DD6
    jne loc_1DEC ; @1DDD
    dec word ptr cs:[bp + byte_0018] ; @1DE2
    jle loc_1DF5 ; @1DE7
loc_1DEC:
    mov word ptr cs:[bp + byte_0024], 0 ; @1DEC
    jmp short loc_1D7D ; @1DF3
loc_1DF5:
    xor byte ptr cs:[byte_0270], cl ; @1DF5
    dec word ptr cs:[byte_026E] ; @1DFA
    jle short loc_1DC5 ; @1DFF
    jmp near ptr loc_1D7D ; @1E01
loc_1E04:
    push ax ; @1E04
    mov al, 020h ; @1E05
    out 020h, al ; @1E07
    pop ax ; @1E09
    test byte ptr cs:[byte_04A2], 1 ; @1E0A
    je loc_1E16 ; @1E10
    iret ; @1E15
loc_1E16:
    mov byte ptr cs:[byte_04A2], 1 ; @1E16
    pusha ; @1E1C
    push es ; @1E1D
    push ds ; @1E1E
    mov dx, word ptr cs:[byte_0010] ; @1E1F
    add dx, 0Eh ; @1E24
    in al, dx ; @1E27
    xor si, si ; @1E28
    test byte ptr cs:[byte_04A5], 1 ; @1E2A
    jne loc_1E38 ; @1E30
    mov si, 040Ah ; @1E35
loc_1E38:
    mov bx, word ptr cs:[si + byte_04A7] ; @1E38
    cmp bx, 028h ; @1E3D
    jb loc_1E7D ; @1E40
    xor byte ptr cs:[byte_04A5], 1 ; @1E45
    mov dx, word ptr cs:[si + byte_04AB] ; @1E4B
    mov ch, byte ptr cs:[si + byte_04A9] ; @1E50
    call far ptr loc_1B77 ; @1E55 same-segment far call
    mov word ptr cs:[si + byte_04A7], 0 ; @1E59
    neg si ; @1E60
    mov dx, word ptr cs:[si + byte_08B7] ; @1E62
    mov bx, 0400h ; @1E67
    call far ptr loc_1CF9 ; @1E6A same-segment far call
    mov word ptr cs:[si + byte_08B1], ax ; @1E6E
loc_1E73:
    pop ds ; @1E73
    pop es ; @1E74
    popa ; @1E75
    mov byte ptr cs:[byte_04A2], 0 ; @1E76
    iret ; @1E7C
loc_1E7D:
    in al, 021h ; @1E7D
    or al, byte ptr cs:[byte_0494] ; @1E7F
    jmp loc_1E89 ; @1E84
    nop ; @1E87
    nop ; @1E88
loc_1E89:
    jmp loc_1E8E ; @1E89
    nop ; @1E8C
    nop ; @1E8D
loc_1E8E:
    jmp loc_1E93 ; @1E8E
    nop ; @1E91
    nop ; @1E92
loc_1E93:
    out 021h, al ; @1E93
    jmp short loc_1E73 ; @1E95
loc_1E97:
    test word ptr cs:[byte_026A], 2 ; @1E97
    je loc_1EF4 ; @1E9E
loc_1EA3:
    test word ptr cs:[byte_000E], 1 ; @1EA3
    jne short loc_1EA3 ; @1EAA
    cmp word ptr cs:[byte_026E], 0 ; @1EAC
    jle loc_1EF4 ; @1EB2
    mov al, 0D0h ; @1EB7
    call far ptr loc_1B4D ; @1EB9 same-segment far call
    mov dx, word ptr cs:[byte_04AD] ; @1EBD
    mov bx, 0400h ; @1EC2
    call far ptr loc_1CF9 ; @1EC5 same-segment far call
    mov word ptr cs:[byte_04A7], ax ; @1EC9
    mov byte ptr cs:[byte_04A5], 1 ; @1ECD
    in al, 021h ; @1ED3
    mov ah, byte ptr cs:[byte_0494] ; @1ED5
    not ah ; @1EDA
    and al, ah ; @1EDC
    jmp loc_1EE3 ; @1EDE
    nop ; @1EE1
    nop ; @1EE2
loc_1EE3:
    jmp loc_1EE8 ; @1EE3
    nop ; @1EE6
    nop ; @1EE7
loc_1EE8:
    jmp loc_1EED ; @1EE8
    nop ; @1EEB
    nop ; @1EEC
loc_1EED:
    out 021h, al ; @1EED
    pushf ; @1EEF
    call far ptr loc_1E04 ; @1EF0 same-segment far call
loc_1EF4:
    retf ; @1EF4
loc_1EF5:
    mov al, 020h ; @1EF5
    out 020h, al ; @1EF7
    mov byte ptr cs:[byte_04A1], 1 ; @1EF9
    iret ; @1EFF
loc_1F00:
    push es ; @1F00
    push ds ; @1F01
    call far ptr loc_1C74 ; @1F02 same-segment far call
    mov word ptr cs:[byte_0012], 1 ; @1F06
    mov word ptr cs:[byte_0010], 0200h ; @1F0D
loc_1F14:
    call far ptr _fn_013B_001F ; @1F14
    call far ptr _fn_013B_001F ; @1F19
    cmp word ptr cs:[byte_0010], word ptr 0260h ; @1F1E
    jae loc_2044 ; @1F25 JUMPS expansion
loc_1F2A:
    add word ptr cs:[byte_0010], 010h ; @1F2A
    call far ptr loc_2114 ; @1F30 same-segment far call
    jb short loc_1F14 ; @1F35
    mov byte ptr cs:[byte_04A1], 0 ; @1F37
    mov al, 0D3h ; @1F3D
    call far ptr loc_1B4D ; @1F3F same-segment far call
    call far ptr _fn_013B_001F ; @1F43
    call far ptr _fn_013B_001F ; @1F48
    xor bx, bx ; @1F4D
loc_1F4F:
    mov cl, byte ptr cs:[bx + byte_2058] ; @1F4F
    push bx ; @1F54
    mov al, cl ; @1F55
    add al, 8 ; @1F57
    mov byte ptr cs:[byte_0012], al ; @1F59
    mov al, 1 ; @1F5D
    shl al, cl ; @1F5F
    mov byte ptr cs:[byte_0494], al ; @1F61
    mov ah, 035h ; @1F65
    mov al, byte ptr cs:[byte_0012] ; @1F67
    int 021h ; @1F6B
    mov ax, es ; @1F6D
    mov word ptr cs:[byte_0497], ax ; @1F6F
    mov word ptr cs:[byte_0495], bx ; @1F73
    call far ptr _fn_013B_001F ; @1F78
    call far ptr _fn_013B_001F ; @1F7D
    in al, 021h ; @1F82
    or al, byte ptr cs:[byte_0494] ; @1F84
    jmp loc_1F8E ; @1F89
    nop ; @1F8C
    nop ; @1F8D
loc_1F8E:
    jmp loc_1F93 ; @1F8E
    nop ; @1F91
    nop ; @1F92
loc_1F93:
    jmp loc_1F98 ; @1F93
    nop ; @1F96
    nop ; @1F97
loc_1F98:
    out 021h, al ; @1F98
    call far ptr _fn_013B_001F ; @1F9A
    call far ptr _fn_013B_001F ; @1F9F
    mov bx, seg SOUNDSEG ; @1FA4
    mov dx, offset loc_1EF5 ; @1FA7
    mov ah, 025h ; @1FAA
    mov al, byte ptr cs:[byte_0012] ; @1FAC
    mov ds, bx ; @1FB0
    int 021h ; @1FB2
    call far ptr _fn_013B_001F ; @1FB4
    call far ptr _fn_013B_001F ; @1FB9
    in al, 021h ; @1FBE
    xor al, byte ptr cs:[byte_0494] ; @1FC0
    jmp loc_1FCA ; @1FC5
    nop ; @1FC8
    nop ; @1FC9
loc_1FCA:
    jmp loc_1FCF ; @1FCA
    nop ; @1FCD
    nop ; @1FCE
loc_1FCF:
    jmp loc_1FD4 ; @1FCF
    nop ; @1FD2
    nop ; @1FD3
loc_1FD4:
    out 021h, al ; @1FD4
    mov ch, byte ptr cs:[byte_04A9] ; @1FD6
    mov dx, word ptr cs:[byte_04AB] ; @1FDB
    mov bx, 3 ; @1FE0
    call far ptr loc_1B77 ; @1FE3 same-segment far call
    mov cx, 01000h ; @1FE7
loc_1FEA:
    test byte ptr cs:[byte_04A1], 1 ; @1FEA
    loope loc_1FEA ; @1FF0
    in al, 021h ; @1FF2
    or al, byte ptr cs:[byte_0494] ; @1FF4
    jmp loc_1FFE ; @1FF9
    nop ; @1FFC
    nop ; @1FFD
loc_1FFE:
    jmp loc_2003 ; @1FFE
    nop ; @2001
    nop ; @2002
loc_2003:
    jmp loc_2008 ; @2003
    nop ; @2006
    nop ; @2007
loc_2008:
    out 021h, al ; @2008
    call far ptr _fn_013B_001F ; @200A
    call far ptr _fn_013B_001F ; @200F
    mov ah, 025h ; @2014
    mov al, byte ptr cs:[byte_0012] ; @2016
    lds dx, dword ptr cs:[byte_0495] ; @201A
    int 021h ; @201F
    call far ptr _fn_013B_001F ; @2021
    call far ptr _fn_013B_001F ; @2026
    cmp cx, 0 ; @202B
    jne loc_2051 ; @202E
    pop bx ; @2033
    inc bx ; @2034
    cmp bx, 3 ; @2035
    jbe loc_1F4F ; @2038 JUMPS expansion
loc_203D:
    mov word ptr cs:[byte_0012], 0 ; @203D
loc_2044:
    mov word ptr cs:[byte_0010], 0 ; @2044
    mov ax, 0 ; @204B
    pop ds ; @204E
    pop es ; @204F
    retf ; @2050
loc_2051:
    pop bx ; @2051
    mov ax, 1 ; @2052
    pop ds ; @2055
    pop es ; @2056
    retf ; @2057
byte_data_2058:
    db 07h, 05h, 03h, 02h ; data 2058..205C
loc_205C:
    push ds ; @205C
    push es ; @205D
    call far ptr loc_113F ; @205E same-segment far call
    call far ptr loc_1F00 ; @2062 same-segment far call
    test ax, 1 ; @2066
    je loc_20B6 ; @2069
    mov ah, 035h ; @206E
    mov al, byte ptr cs:[byte_0012] ; @2070
    int 021h ; @2074
    mov ax, es ; @2076
    mov word ptr cs:[byte_0497], ax ; @2078
    mov word ptr cs:[byte_0495], bx ; @207C
    mov ax, seg SOUNDSEG ; @2081
    mov ds, ax ; @2084
    mov dx, offset loc_1E04 ; @2086
    mov ah, 025h ; @2089
    mov al, byte ptr cs:[byte_0012] ; @208B
    int 021h ; @208F
    in al, 021h ; @2091
    mov ah, byte ptr cs:[byte_0494] ; @2093
    not ah ; @2098
    and al, ah ; @209A
    jmp loc_20A1 ; @209C
    nop ; @209F
    nop ; @20A0
loc_20A1:
    jmp loc_20A6 ; @20A1
    nop ; @20A4
    nop ; @20A5
loc_20A6:
    jmp loc_20AB ; @20A6
    nop ; @20A9
    nop ; @20AA
loc_20AB:
    out 021h, al ; @20AB
    mov al, 0D1h ; @20AD
    call far ptr loc_1B4D ; @20AF same-segment far call
    mov ax, 1 ; @20B3
loc_20B6:
    pop es ; @20B6
    pop ds ; @20B7
    retf ; @20B8
loc_20B9:
    push ds ; @20B9
    mov al, 0D3h ; @20BA
    call far ptr loc_1B4D ; @20BC same-segment far call
    call far ptr _fn_013B_001F ; @20C0
    call far ptr _fn_013B_001F ; @20C5
    in al, 021h ; @20CA
    or al, byte ptr cs:[byte_0494] ; @20CC
    jmp loc_20D6 ; @20D1
    nop ; @20D4
    nop ; @20D5
loc_20D6:
    jmp loc_20DB ; @20D6
    nop ; @20D9
    nop ; @20DA
loc_20DB:
    jmp loc_20E0 ; @20DB
    nop ; @20DE
    nop ; @20DF
loc_20E0:
    out 021h, al ; @20E0
    call far ptr _fn_013B_001F ; @20E2
    call far ptr _fn_013B_001F ; @20E7
    mov ah, 025h ; @20EC
    mov al, byte ptr cs:[byte_0012] ; @20EE
    lds dx, dword ptr cs:[byte_0495] ; @20F2
    int 021h ; @20F7
    call far ptr _fn_013B_001F ; @20F9
    call far ptr _fn_013B_001F ; @20FE
    call far ptr loc_2114 ; @2103 same-segment far call
    call far ptr _fn_013B_001F ; @2108
    call far ptr _fn_013B_001F ; @210D
    pop ds ; @2112
    retf ; @2113
loc_2114:
    mov dx, word ptr cs:[byte_0010] ; @2114
    add dx, 6 ; @2119
    mov al, 1 ; @211C
    out dx, al ; @211E
    mov ax, 3 ; @211F
    call far ptr loc_11B5 ; @2122 same-segment far call
    xor al, al ; @2126
    out dx, al ; @2128
    add dx, 8 ; @2129
    mov cx, 064h ; @212C
loc_212F:
    in al, dx ; @212F
    test al, 080h ; @2130
    loope loc_212F ; @2132
    sub dx, 4 ; @2134
    in al, dx ; @2137
    cmp al, 0AAh ; @2138
    jne loc_2141 ; @213A
    clc ; @213F
    retf ; @2140
loc_2141:
    stc ; @2141
    retf ; @2142
SOUNDSEG ends
end
