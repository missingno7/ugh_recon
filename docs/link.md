# Natural link (worker link)

Status: partial. `python tools/verify.py` exits **1**, at
`IMAGE_AND_RELOCATION_SET_DIAGNOSTIC`. The natural executable has the exact
409,278-byte load image, all MZ header fields, header gap/padding, and all 525
relocation entries as a multiset. **35 relocation table positions differ**.
PKLITE produces 139,685 bytes, with **39 differing bytes**, first at file
`021D74`. This is not packed-file equality. Full lists and ranges are in
`build/link/verify.json`; the natural executable is `build/link/UGH.EXE`.

## Build and acceptance

```
python tools/oracle.py
python tools/asmverify.py
python tools/cjudge.py
python tools/census.py
python tools/verify.py
```

The two contribution gates remain supported and pass; neither is replaced.
`build.py` removes generated objects/executables/listings from `build/link/`,
stages the hash-locked startup/library, assembles every listed source, compiles
the complete C translation unit, and invokes TLINK. It reads no executable
oracle. `datagen.py` is an explicit bootstrap, **never a build dependency**.
No cached object, extracted code blob, output patch, or trimming is used.
The source-byte audit from `asmverify.py` also runs on the fresh build listings.

`verify.py` checks both input hashes against the unchanged oracle lock, builds
fresh, compares every header field, the relocation tuples in order, physical
sites as set/multiset, every image byte, header gap/padding and overlay tail.
It records all differing relocation positions and image ranges, and first byte
differences per census region. It packs a copy using pinned PKLITE and compares
the complete result. Only full packed equality returns zero. Lesser levels are
explicitly named diagnostics; build/validation failure returns 2.

## Object order and commands

All commands run through `tools/dos.py` with pinned tools. Sources and tool inputs
are copied to `build/link/` using DOS-safe names. BCC command:

```
BCC -c -mh -2 -n. MODULE.C
```

Each assembly source uses:

```
TASM /kh8192 NAME.ASM,NAME.OBJ,NAME.LST
```

`TLINK @LINK.RSP`, where the complete maintained response line is:

```
/m /s C0H.OBJ+DGDATA.OBJ+GAME.OBJ+SOUND.OBJ+ZERO.OBJ+MODULE.OBJ+TIMER.OBJ+B1A38.OBJ+B1E1F.OBJ+B2BC6.OBJ+B2BF6.OBJ+B2D9A.OBJ+B2F9E.OBJ+B2FB7.OBJ+B325B.OBJ+B3260.OBJ+B3265.OBJ+B326B.OBJ+B3274.OBJ+B3279.OBJ+B3444.OBJ+B3629.OBJ+B3632.OBJ+B3637.OBJ+B37A7.OBJ+B438A.OBJ+B4E83.OBJ+B5B63.OBJ+RESERVE.OBJ,UGH.EXE,UGH.MAP,CH.LIB
```

The original library's natural pull order, verified by the fresh detailed map:

```
ATEXIT EXIT FILES FILES2 F_LXMUL F_PCMP H_LDIV H_LLSH H_PADA H_PADD
H_PINA IOERROR ISATTY LSEEK N_PCMP SETUPIO STKLEN TELL FARHEAP FBRK
SETBLOCK FFLUSH FLUSHALL FSEEK MEMSET SETVBUF WRITE WRITEA XFFLUSH
```

No library member is explicitly extracted or reordered for the build. Startup
and the C module's real references pull these members from CH.LIB. `_TEXT` is
**13B8h = 5,048 bytes**, including the eight bytes beyond the old paragraph
census boundary 13B0h. The complete runtime code and initialized runtime data
now match in the natural link, including TLINK's same-segment far-call rewrites.

## Segments and owners

| Contribution | Declaration / placement | Source owner |
|---|---|---|
| `_TEXT` | BYTE PUBLIC CODE, image 00000..013B8 | original C0H.OBJ + CH.LIB |
| GAMESEG | WORD PUBLIC CODE, 013B8..0664C | GAME.ASM |
| SOUNDSEG | WORD PUBLIC CODE, 0664C..08783 | SOUND.ASM |
| MODULE_TEXT | BYTE PUBLIC CODE, 08783..0A325 | BCC, MODULE.C |
| TIMERSEG | WORD PUBLIC CODE, 0A326..0A661 | TIMER.ASM |
| ZERODATA | PARA PUBLIC FAR_DATA, 0A670..1A370 | ZERO.ASM, RAW zero storage |
| MODULE_DATA | WORD PUBLIC FAR_DATA, 1A370..1A374 | initialized C globals |
| BANK_xxxx | PARA PUBLIC FAR_DATA, 1A380..5C090 | one Bxxxx.ASM per bank |
| `_DATA` | WORD PUBLIC DATA, grouped in DGROUP at 5C09 | startup, DGDATA, library |
| `_INIT_` | library INITDATA, DGROUP 7E28..7E2E | CH.LIB SETUPIO |
| `_STACK` | PARA STACK STACK, 63EC:0000..0080 | original C0H.OBJ |
| TAIL_RESERVE | PARA PUBLIC RESERVE, 63F4:0000..0080 | RAW virtual reservation |

All ranges have exclusive ends. The startup's empty standard segments remain
untouched. TLINK groups the CODE class first, FAR_DATA next, then the startup's
remaining standard classes and DGROUP, stack, and the trailing reserve. The 21
separate resource-bank sources follow the C data frame; their ends are the next
observed frame, including any indistinguishable asset alignment bytes as RAW.

DGROUP ownership is verified by naturally linking the original library:

| DGROUP range | Bytes | Owner |
|---|---:|---|
| 0000..0091 | 145 | C0H initialized `_DATA` |
| 0091..0092 | 1 | WORD alignment |
| 0092..7B7C | 31,466 | DGDATA.ASM, RAW game data |
| 7B7C..7BFE | 130 | ATEXIT |
| 7BFE..7C0A | 12 | EXIT |
| 7C0A..7D9A | 400 | FILES |
| 7D9A..7DC4 | 42 | FILES2 |
| 7DC4..7E1F | 91 | IOERROR |
| 7E1F..7E20 | 1 | WORD alignment |
| 7E20..7E22 | 2 | STKLEN |
| 7E22..7E24 | 2 | FBRK |
| 7E24..7E28 | 4 | SETVBUF |
| 7E28..7E2E | 6 | SETUPIO `_INIT_` |

The library span has 690 bytes, including one alignment byte. Excluding that
byte leaves 834 actual runtime data bytes (145 startup plus 689 library).
Both DGROUP alignment bytes are counted in linker padding.

The initialized-image end and startup stack alone yield min_alloc=9. The locked
expanded header requires 17. A trailing 128-byte uninitialized source reservation
reproduces all header fields without changing the initialized image or stack.
**Its historical segment, owner, and use are unknown.** This is a reproducing
memory reservation, not attribution of an original object or recovered BSS.
Its eight paragraphs are reported separately as RAW virtual debt. The exact
byte granularity inside that paragraph allocation cannot be inferred.

## Symbols

GAME exports `_main` and the five assembly hooks used by C. SOUND exports the
C-visible far globals and assembly hooks at their real offsets in SOUNDSEG.
TIMER exports the routines used by SOUND. Cross-code calls now use actual
`_fn_...` publics/externals, including compiler-generated C function publics.
All code/data segments are resolved by normal TLINK fixups. The `ext_xxxx`
data anchors are actual labels in the emitted data contributions, not absolute
dummy definitions. Numeric DS offsets remain where the exact DGROUP layout
already resolves their addressing; the task does not require converting all of
them to labels. `BIND:` and `OMF:` comments in module.c remain independent
object-judge expectations and are never consumed by the natural linker build.

The small `asmverify.py` adjustment resolves real function externals with their
proper **frame and offset**, instead of incorrectly paragraph-normalizing an
arbitrary function address. Both contribution gates still pass. The C inventory's
old UNKNOWN three-byte prefix is corrected to SOUND's verified tail; no C code
is added there. Shared `omf.py` now correctly reads LIDATA leaf lengths and nested
blocks. A source-constant/pinned-TLINK probe verifies 18 bytes, including nesting;
the existing ASM gate's conservative LIDATA rejection remains unchanged.

## Relocation order: unresolved

Original order is not reproduced. Every entry has the right site and resolved
word; only these zero-based table positions differ:

| Owner | Different positions | Positions |
|---|---:|---|
| DGDATA | 7 | 5..11 |
| GAME | 2 | 22..23 |
| SOUND | 26 | 66..69, 77..80, 82..90, 97..105 |
| C, TIMER, startup/library | 0 | none |

GAME's resource declarations follow CODE to preserve the observed forward-SEG
fixup behavior; frame 3629 is declared before CODE. TIMER's DGROUP declaration
follows CODE. These ordinary source arrangements improve 66 initially differing
positions to 35 without changing a single image byte. They are reproducing
choices, not recovered historical source spelling. Fixup order inside the
remaining DGDATA/GAME/SOUND records remains a blocker.

`python build/workers/link/relocprobe.py` reverses all 525 relocation tuples in
a scratch **oracle experiment**, packs with `PKLITE REVERSE.EXE`, then expands
with `PKLITE -x REVERSE.EXE`. The packed file differs and expansion preserves
the complete reversed tuple order. No packer sorting or loss of order was
observed. This experiment edits a scratch input to test PKLITE, never a build
output for acceptance. Packed equality therefore still requires solving the
actual relocation sequence; image equality cannot stand in for it.

## Byte accounting

Disjoint accounting, using contribution extents rather than the old rounded
paragraph census:

| Class | Bytes |
|---|---:|
| Exact ASM instruction code | 25,885 |
| Exact C instruction code | 7,030 |
| Runtime library code | 5,048 |
| Runtime library initialized data | 834 |
| Compiler switch tables | 44 |
| Initialized C globals | 4 |
| RAW data, assembly-owned | 4,584 |
| RAW far banks + game DGROUP | 365,818 |
| Assembler/linker padding | 31 |
| UNKNOWN file bytes | 0 |
| **Load image** | **409,278** |

RAW data debt is **370,402 file bytes**, plus 128 virtual bytes with unknown
owner/use. Known source ownership does not establish the meaning of copied
opaque data. The image contribution certificates include data/padding within
their extents; those bytes are not counted again as instruction code above.

## Failed and inconclusive hypotheses

All assembly probes use pinned `TASM /kh8192 P.ASM,P.OBJ[,P.LST]` unless stated.
Full source transformations are retained in `build/workers/link/*.py`; many
variants have named `.ASM` snapshots. None of the unpromoted probe aliases or
combined objects participates in `build.py`.

| Exact tool/options and experiment | Result |
|---|---|
| TASM /kh8192 BANKS.ASM,BANKS.OBJ,BANKS.LST, all banks in one file | Fatal out of memory after assembly; split into 21 normal source/object modules. |
| TASM /kh8192 DGDATA.ASM,DGDATA.OBJ,DGDATA.LST, self EXTRN and PUBLIC ext_5C09 | Duplicate/different-kind errors; own frame is a real label, not EXTRN. |
| TLINK /m /s @response with startup + DGDATA + GAME + SOUND + ZERO + MODULE + TIMER + banks | Exact initialized image on first natural link; min_alloc 9 versus 17, 66 relocation positions different. |
| PKLITE CYCLE.EXE then PKLITE -x CYCLE.EXE on the first natural link | min_alloc remains 9: packing/extraction does not explain the extra allocation. |
| TASM, orderprobe.py: move all/segment/code EXTRNs after CODE | TIMER order exact; GAME resource declarations nearly exact; generic moves do not fix SOUND. |
| TASM, orderprobe.py: `call seg symbol:far ptr symbol` | Expecting scalar type errors; not valid direct-far-call syntax. |
| TASM, syntaxprobe.py: `call far ptr OTHER:0123h`; `call far ptr (seg x):offset x`; `call far ptr seg x:offset x` | Near-call-to-different-CS or undefined OFFSET errors. Ordinary `call far ptr x` works. |
| TASM /kh8192 with each of /zi /zd /z /l /la /m1 /t /q, optionsprobe.py | Same observed LEDATA record extents; no order solution. |
| TASM /kh8192 /ut200 and /ut300, emulateprobe.py | Same extents/order as baseline; no solution. |
| TASM /kh8192 /ut100 and /um510 | GAME/SOUND grow to 21155/8580 bytes; rejected. /u200 is an illegal version spelling. |
| TASM, aliasprobe.py / frameprobe.py / refine.py | Forward symbolic EQU references alter order but do not solve the stream. Bare forward frame aliases in MOV/PUSH can become memory operands and grow GAME; rejected. |
| TASM, soundprobe.py: DUP prefix as all/per16/tail, optional close/reopen segment; forward final SEG | Some alias variants reduce SOUND order differences, none matches all; no variant promoted. |
| TASM, ddprobe.py / declarationprobe.py / internalprobe*.py / layoutprobe.py / dgorder.py | DD pointers, internal segments, forward group/label/alias declarations and declaration placement do not reproduce DGDATA's eight-site order. |
| TASM + TLINK /m /s, combineprobe*.py | Embedding DGDATA before GAME in one object keeps the image exact but gives 44 or 45 differing relocation positions, worse than separate objects. |
| TASM, groupknown.py / dgpointerprobe.py | Known/forward DGROUP expressions and actual forward data-pointer labels still fail the initial eight-site order. |

Next work should discriminate TASM fixup/backpatch emission with small examples
of the three remaining records, then promote an ordinary source arrangement
only after the complete fresh packed comparison passes. No further instruction
reconstruction or runtime copying is needed for the current initialized image.
