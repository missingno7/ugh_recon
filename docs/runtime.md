# Borland runtime attribution

The expanded executable's runtime was reproduced with the pinned Borland C++
3.0 huge-model `C0H.OBJ`, `CH.LIB`, TASM 3.0, and TLINK 5.0. `tools/libmatch.py`
rebuilds the probe and checks its map, code, fixups, and runtime DGROUP
contributions against `build/oracle/UGH_X.EXE`.

## `_TEXT` member order

The TLINK `/s` map yields this order after removing the probe caller's own
`_TEXT` contribution (`P.ASM`, 29h bytes). Ranges are half-open offsets in the
original image. All bytes and resolved fixups match; the zero-length `_TEXT`
members are still present in the link map and contribute data or symbols.

| Link order | Member | Frame 0000 image range | Code bytes |
|---:|---|---:|---:|
| 1 | C0H.OBJ (`C0.ASM`) | 0000–0257 | 599 |
| 2 | ATEXIT | 0257–028B | 52 |
| 3 | EXIT | 028B–035B | 208 |
| 4 | FILES | 035B–035B | 0 |
| 5 | FILES2 | 035B–035B | 0 |
| 6 | F_LXMUL | 035B–0372 | 23 |
| 7 | F_PCMP | 0372–0393 | 33 |
| 8 | H_LDIV | 0393–0441 | 174 |
| 9 | H_LLSH | 0441–0462 | 33 |
| 10 | H_PADA | 0462–04EA | 136 |
| 11 | H_PADD | 04EA–054A | 96 |
| 12 | H_PINA | 054A–05B0 | 102 |
| 13 | IOERROR | 05B0–060F | 95 |
| 14 | ISATTY | 060F–0627 | 24 |
| 15 | LSEEK | 0627–065D | 54 |
| 16 | N_PCMP | 065D–067E | 33 |
| 17 | SETUPIO | 067E–0779 | 251 |
| 18 | STKLEN | 0779–0779 | 0 |
| 19 | TELL | 0779–0798 | 31 |
| 20 | FARHEAP | 0798–0BCA | 1074 |
| 21 | FBRK | 0BCA–0D89 | 447 |
| 22 | SETBLOCK | 0D89–0DAC | 35 |
| 23 | FFLUSH | 0DAC–0E80 | 212 |
| 24 | FLUSHALL | 0E80–0ED1 | 81 |
| 25 | FSEEK | 0ED1–1040 | 367 |
| 26 | MEMSET | 1040–1091 | 81 |
| 27 | SETVBUF | 1091–11BA | 297 |
| 28 | WRITE | 11BA–1328 | 366 |
| 29 | WRITEA | 1328–1377 | 79 |
| 30 | XFFLUSH | 1377–13B8 | 65 |

The complete linked `_TEXT` ends at 13B8, eight bytes after the frame boundary
13B0 inferred from the next segment value. Those bytes, 13B0–13B7, match the
tail of XFFLUSH. The game entry is 013B:0008, linear offset 13B8, so game code
starts exactly after runtime `_TEXT`; 013B:0000–0007 are not game instructions.
Thus the metadata's 5040-byte frame-0000 span is a frame-boundary measure, not
the full `_TEXT` segment length. No `_TEXT` byte is UNKNOWN.

## TLINK far-call rewrite and startup

TLINK converts same-segment far calls (`9A off16 seg16`) to `90 0E E8 rel16`
and removes the segment relocation. The matcher resolves targets through the
probe map and checks this rewrite at every such FIXUPP site in C0H and the
selected library members. It verified 26 rewrites, including the startup calls
at 0000:013D and 0000:024E. Their apparent `9A` versus `90` differences from
the raw C0H object are linker transformations, not source differences.

The probe confirms the startup's initialized `_TEXT` contribution: all 599
bytes, including all 57 FIXUPP records, match after TLINK resolves the targets.
The earlier direct comparison that treated 013D/024E as disagreements omitted
the far-to-near rewrite and was incorrect.

## Game references that pull members

The frame-0878 far calls resolve to these huge-model public entry points:

| Public called | Frame 0000 target |
|---|---:|
| `F_PINA@` / `PINA@` | 054D |
| `F_PCMP@` / `PCMP@` | 0372 |
| `F_PADD@` / `PADD@` | 04ED |
| `F_PADA@` / `PADA@` | 0465 |
| `LXLSH@` / `F_LXLSH@` | 0444 |
| `F_LXMUL@` / `LXMUL@` | 035B |
| `_memset` | 106B |
| `F_LUDIV@` / `LUDIV@` | 039D |

The aliases in the selected members are also shown in the link map (`PINA@`,
`PCMP@`, `PADD@`, `PADA@`, `LXMUL@`, and `LUDIV@`). `_memset` selects MEMSET;
the earlier raw-byte collision with FMEMSET is resolved by the actual link map.
Relocation inspection found no far call from frames 013B, 0664, or 0A32 into
frame 0000. Frames 013B and 0A32 have DGROUP segment fixups; frame 0664 has
none. The probe adds a size-only DGROUP contribution for those game-owned data
contributions, rather than inventing runtime function references for them.

## DGROUP layout

The probe first links with no application-data placeholder. The FILES `_DATA`
bytes have one unique match in the original DGROUP at 7C0A. TLINK's baseline
map places FILES at 0120, so a 7AEA-byte placeholder after startup data moves
the runtime library contributions to their measured original offsets. The
final map ends at 7E2E, exactly the original DGROUP size (32302 bytes). The
runtime data bytes and fixups all match at these positions.

| Contribution | Original DGROUP byte range | Notes |
|---|---:|---|
| C0H `_DATA` | 0000–0091 | startup data, 145 bytes |
| one-byte alignment | 0091–0092 | word alignment before following data |
| game-owned DGROUP span | 0092–7B7C | 7AEA bytes; placeholder establishes size, not contents |
| ATEXIT `_DATA` | 7B7C–7BFE | 130 bytes |
| EXIT `_DATA` | 7BFE–7C0A | 12 bytes |
| FILES `_DATA` | 7C0A–7D9A | 400 bytes; unique byte anchor |
| FILES2 `_DATA` | 7D9A–7DC4 | 42 bytes |
| IOERROR `_DATA` | 7DC4–7E1F | 91 bytes |
| alignment | 7E1F–7E20 | one byte |
| STKLEN `_DATA` | 7E20–7E22 | 2 bytes |
| FBRK `_DATA` | 7E22–7E24 | 2 bytes |
| SETVBUF `_DATA` | 7E24–7E28 | 4 bytes |
| SETUPIO `_INIT_` | 7E28–7E2E | 6-byte initialization table |

`_CVTSEG`, `_SCNSEG`, `_CONST`, `_EXIT_`, and their end markers have zero
length in the map. The runtime therefore surrounds the game's DGROUP data:
startup data occupies the prefix and library data/tables occupy the tail. The
game's exact individual DGROUP object contributions within 0092–7B7C were not
reconstructed, but that interval and its size are fixed by the unique FILES
anchor, TLINK module order, and exact group end.

The selected members add no nonzero far-data or code contribution outside
`_TEXT` and DGROUP in the TLINK map.

## Probe and checker

`build/workers/runtime/makeprobe.py` stages the pinned C0H/CH inputs and builds
a TASM reference module. Its `_main` lives in a separate segment so the
startup's call remains far. The `_TEXT` trampoline references the eight public
entry points above; C0H startup dependencies pull the remaining listed
members. `/m /s` supplies the member-level ranges and public symbol addresses.
The probe's trampoline bytes are removed by their map range before comparing
runtime offsets. The DGROUP placeholder size is calculated from the unique
FILES match on each run.

`python tools/libmatch.py` rebuilds both the baseline and calibrated probes,
prints every mapped member, checks all 5048 runtime `_TEXT` bytes including
resolved fixups and all mapped runtime DGROUP contributions, verifies every
same-segment far-call rewrite, and exits nonzero on any mismatch or uncovered
`_TEXT` byte. The game-data placeholder's contents are explicitly excluded
from runtime-byte claims.

## Region proposal

The current census has one region per frame and cannot express the 8-byte
runtime tail that occupies frame 013B offsets 0000–0007 before game code starts
at offset 0008. Add optional `start` / `end` offsets within each frame (or use
`frame:start-end` keys). Suggested exact bounded entries:

```json
{"frame":"0000","start":"0000","end":"13B8","class":"RUNTIME","name":"Borland startup and CH.LIB","evidence":"TLINK 5.0 /s member map and libmatch fixup verification"}
{"frame":"013B","start":"0008","end":"5290","class":"ASM","name":"game","evidence":"game entry is 013B:0008; preceding eight bytes finish runtime XFFLUSH"}
{"frame":"0664","start":"0000","end":"2140","class":"ASM","name":"sound","evidence":"next frame 0878 begins at linear 0878:0000"}
{"frame":"5C09","start":"0000","end":"0091","class":"DATA","name":"C0H startup DGROUP data","evidence":"TLINK map; bytes compare at group offset 0"}
{"frame":"5C09","start":"0092","end":"7B7C","class":"DATA","name":"game DGROUP contributions","evidence":"span between C0H startup data and first runtime library data member"}
{"frame":"5C09","start":"7B7C","end":"7E2E","class":"RUNTIME","name":"CH.LIB DGROUP data and init table","evidence":"TLINK map anchored by unique FILES data match; bytes/fixups verified"}
```

The schema must also represent the one-byte alignments at 0091 and 7E1F. Keep
the full game-data block as DATA until its individual assembly owners are known.
