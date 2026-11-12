# Readable source and derived relocation proof

Status: **done**. `python tools/verify.py` returns **0**, `FULL_PACKED_FILE`,
with both builds reported. The plain executable has the exact header fields,
409,278 load-image bytes and relocation set/multiset; **35** relocation table
positions differ in order. The proof executable equals all 411,838 expanded
file bytes, including all **525 relocation tuples in order**. Pinned PKLITE 1.15
produces the original 139,685 packed bytes. Both load images are identical.

Packed SHA-256: `1058cad6771a540f75b109dbe77adda1f6590e7c0309349482c601542e459e7a`.
Proof expanded SHA-256: `ef93d2cd5eb558f6a7d0007e0109f2e9ee952dc125389d7a6256646087636d7c`.

## Maintained source and generated files

GAME, SOUND and TIMER are plain, single-segment sources in image order, restored
from commit 6776f37. Real cross-module symbols, corrected labels and natural data
OFFSET/string labels remain. Added ordinary labels provide named cut points;
they emit no bytes. There are no GCODE/SCODE segments, branch addends, shuffled
pieces, artificial branch reservations or proof LAYOUT source under src/.

`tools/fragment.py` reads these clean assembly/data sources and
`metadata/reloc-layout.json` only. It never reads the oracle, asm-map, object
files, listings, maps or previous build output. Its outputs are restricted to
build/link/. `build.py` invokes it afresh in build/link/proof/; nobody edits its
outputs. The plain build copies the maintained sources directly to
build/link/plain/. Both variants independently assemble all sources, compile C,
stage hash-checked C0H.OBJ/CH.LIB and link with pinned tools, using fresh objects.
`datagen.py` remains an explicit data bootstrap, never a build dependency.

The layout header states that its ordering was derived from the original
relocation table. It is a modern **reproducing device, not recovered source
structure**. It contains physical cut labels, proof piece names/declaration
orders, fourteen branch/alignment form decisions, three deferred DGDATA externs,
and empty layout tail declarations. It contains no instructions or expected
byte strings. Stable IDs refer into the flat `labels` dictionary; all actual
label names are values in that dictionary. A rename tool changes source
label definitions/references and the corresponding dictionary values, leaving
IDs and their uses intact. No line numbers or comment addresses are consumed.
The numeric-looking portions of label names are opaque names to the generator.

Missing or repeated labels, changed cut ordering, invalid piece permutations,
and mechanical adjustments that no longer match their instruction fail loudly.
For example a source-only rename gives:
`GAME: cut label loc_0072 (game_001) not found in clean source`.
Renaming that label in source and layout, with extra comments/blank lines,
passes the complete verifier and the independent clean ASM gate.

## Build and verification

```
python tools/oracle.py
python tools/asmverify.py
python tools/cjudge.py
python tools/census.py
python tools/verify.py
```

`asmverify.py` certifies clean contribution bytes and relocation site sets and
targets; emitted order remains a diagnostic. Listing auditing rejects data
instructions outside independent classified data extents. `cjudge.py` is
unchanged. The canonical asm-map describes whole clean segments, without
fragment placement metadata. During the proof build, generated listing data
extents are audited against that same independent map; generated LAYOUT must
have no bytes, fixups or publics. Other data-only sources cannot contain CODE.

`verify.py` exits zero only if all three gates hold:

- Plain header fields/gap/padding/tail, every image byte and relocation
  tuple/site sets and multisets match, with exactly 35 order differences.
- Proof expanded file and complete PKLITE output match the locked originals.
- Plain and proof load images are identical.

The plain result is explicitly `IMAGE_AND_RELOCATION_SET_DIAGNOSTIC`; it is not
called a packed proof. An overall `FULL_PACKED_FILE` also certifies the tie to
the readable source. Field differences, every changed relocation index, image
ranges and first differences per region, packed differences, class totals and
RAW debt are retained in build/link/verify.json. No binary output is patched,
trimmed or reordered. All linker ordering is ordinary source/object order.

## Mechanical proof transformation

TASM emits each segment's data/fixups in declaration order. TLINK places PUBLIC
segments where their first ordinary declaration established them. A generated
empty LAYOUT object establishes physical piece order; generated GAME/SOUND
objects declare pieces in the separate order recorded by the layout. GROUP
supplies a common code frame, not physical storage ordering. Pinned TASM writes
GRPDEF members in reverse source-list order. GAME has 32 pieces in GAME_GROUP;
SOUND has a resident prefix plus 14 code pieces in SOUND_GROUP.

The generator moves trailing code EXTRNs before the generated declarations,
qualifies native local OFFSET references with their group and rewrites only
cross-piece transfers. Existing SHORT/NEAR forms, near calls and LOOP/JCXZ forms
come from the source. The few unqualified branches require label-keyed layout
form decisions: short, reserved short (three NOPs), or inverse-short/near-jump.
Cross-piece local far calls become PUSH CS / near CALL, with the original
forward-call NOP reservation when the target is defined later. One EVEN becomes
a NOP because piece-local parity differs from group parity. Pinned TLINK's
LOC0 relative fixup subtracts two rather than one, so derived cross-piece short
branches use target+1; LOC1 near branches need no addend. These mechanics exist
only in generated sources and use instructions, never code DB directives.

Piece emission orders (the layout file is authoritative):

```
GAMESEG GCODE02 GCODE04 GCODE01 GCODE03 GCODE05 GCODE07 GCODE06 GCODE09 GCODE08 GCODE10
GCODE12 GCODE11 GCODE14 GCODE16 GCODE13 GCODE15 GCODE17 GCODE19 GCODE18 GCODE21 GCODE20
GCODE23 GCODE25 GCODE22 GCODE24 GCODE26 GCODE28 GCODE27 GCODE30 GCODE29 GCODE31

SOUNDSEG SCODE00 SCODE02 SCODE01 SCODE03 SCODE05 SCODE07 SCODE04 SCODE06 SCODE08 SCODE10
SCODE09 SCODE11 SCODE13 SCODE12
```

## Object/library order and commands

Both variants use these pinned commands in their own directory:

```
TASM /kh8192 NAME.ASM,NAME.OBJ,NAME.LST
BCC -c -mh -2 -n. MODULE.C
TLINK @LINK.RSP
```

Plain LINK.RSP:

```
/m /s C0H.OBJ+DGDATA.OBJ+GAME.OBJ+SOUND.OBJ+ZERO.OBJ+MODULE.OBJ+TIMER.OBJ+B1A38.OBJ+B1E1F.OBJ+B2BC6.OBJ+B2BF6.OBJ+B2D9A.OBJ+B2F9E.OBJ+B2FB7.OBJ+B325B.OBJ+B3260.OBJ+B3265.OBJ+B326B.OBJ+B3274.OBJ+B3279.OBJ+B3444.OBJ+B3629.OBJ+B3632.OBJ+B3637.OBJ+B37A7.OBJ+B438A.OBJ+B4E83.OBJ+B5B63.OBJ+RESERVE.OBJ,UGH.EXE,UGH.MAP,CH.LIB
```

Proof LINK.RSP differs only by adding LAYOUT.OBJ immediately after C0H.OBJ:

```
/m /s C0H.OBJ+LAYOUT.OBJ+DGDATA.OBJ+GAME.OBJ+SOUND.OBJ+ZERO.OBJ+MODULE.OBJ+TIMER.OBJ+B1A38.OBJ+B1E1F.OBJ+B2BC6.OBJ+B2BF6.OBJ+B2D9A.OBJ+B2F9E.OBJ+B2FB7.OBJ+B325B.OBJ+B3260.OBJ+B3265.OBJ+B326B.OBJ+B3274.OBJ+B3279.OBJ+B3444.OBJ+B3629.OBJ+B3632.OBJ+B3637.OBJ+B37A7.OBJ+B438A.OBJ+B4E83.OBJ+B5B63.OBJ+RESERVE.OBJ,UGH.EXE,UGH.MAP,CH.LIB
```

The naturally pulled CH.LIB members, without an extraction list, are:

```
ATEXIT EXIT FILES FILES2 F_LXMUL F_PCMP H_LDIV H_LLSH H_PADA H_PADD
H_PINA IOERROR ISATTY LSEEK N_PCMP SETUPIO STKLEN TELL FARHEAP FBRK
SETBLOCK FFLUSH FLUSHALL FSEEK MEMSET SETVBUF WRITE WRITEA XFFLUSH
```

Runtime `_TEXT` totals 13B8h (5,048 bytes); ordinary TLINK same-segment far-call
relaxations remain unchanged. Runtime code comes from the original library.

## Physical extents and data ownership

| Contribution | Placement / declaration |
|---|---|
| Runtime `_TEXT` | 00000..013B8, original BYTE PUBLIC CODE |
| GAMESEG (plain) / GAME_GROUP (proof) | 013B8..0664C, plain WORD PUBLIC CODE; proof first piece WORD, others BYTE PUBLIC CODE |
| SOUNDSEG (plain) / SOUND_GROUP (proof) | 0664C..08783, plain WORD PUBLIC CODE; proof WORD resident prefix, BYTE code pieces, all PUBLIC CODE |
| MODULE_TEXT | 08783..0A325, BCC BYTE PUBLIC CODE |
| TIMERSEG | 0A326..0A661, WORD PUBLIC CODE |
| ZERODATA | 0A670..1A370, PARA PUBLIC FAR_DATA |
| MODULE_DATA | 1A370..1A374, BCC WORD PUBLIC FAR_DATA; 12 following alignment bytes |
| BANK_xxxx | 1A380..5C090, 21 PARA PUBLIC FAR_DATA resource-bank sources |
| DGROUP | 5C090..63EBE, original runtime DATA/INITDATA around game `_DATA` |
| `_STACK` | 63EC:0000..0080, original C0H PARA STACK STACK |
| TAIL_RESERVE | 63F4:0000..0080, PARA PUBLIC RESERVE, uninitialized |

DGROUP has startup data 0000..0091, alignment at 0091, game data 0092..7B7C,
then library data/INITDATA through 7E2E. The library subranges are ATEXIT
7B7C..7BFE, EXIT 7BFE..7C0A, FILES 7C0A..7D9A, FILES2 7D9A..7DC4,
IOERROR 7DC4..7E1F, alignment 7E1F..7E20, STKLEN 7E20..7E22,
FBRK 7E22..7E24, SETVBUF 7E24..7E28 and SETUPIO 7E28..7E2E.

The ten string offsets at DGROUP 00DA..00EC are now `DW OFFSET` references to
actual string labels. GAME:0652 indexes the option entries and copies DS strings;
the values point to EASY/MEDIUM/HARD, player/control text and the two name lists.
The clean data source declares its external selectors normally at the top.
The proof generator defers three far-bank EXTRNs to the end, reproducing selector
order 0099,00A1,00AD,00B1,00B9,009D,00A5,00B5. Those declarations are selected by
label IDs in the layout file. The plain build retains seven DGROUP order
positions in its total of 35. A separate DGDATA object suffices for exact proof;
this stream does not uniquely establish a historical combined GAME+data object.

All exported code hooks, C-visible sound globals and far-bank selectors are real
PUBLIC/EXTRN labels/relocatable aliases. The module.c BIND/OMF comments are only
independent object-judge expectations; the natural linker never consumes them.
Numeric DS equates remain where full symbol conversion is unnecessary.

The eight additional allocation paragraphs are still represented by the
128-byte trailing uninitialized reservation. Its historical owner/use and exact
byte granularity inside that allocation remain unknown. Its debt is reported
separately; packed equality does not turn that reproducing reservation into
historical source attribution.

## Byte classes and debt

| Class | Bytes |
|---|---:|
| ASM_code | 25,885 |
| C_code | 7,030 |
| runtime_library_code | 5,048 |
| runtime_library_data | 834 |
| compiler_switch_tables | 44 |
| C_initialized_data | 4 |
| RAW_assembly_owned_data | 4,584 |
| RAW_far_banks_and_game_DGROUP | 365,818 |
| assembler_and_linker_padding | 31 |
| UNKNOWN_file_bytes | 0 |
| **Load image total** | **409,278** |

RAW debt is **370,402 file bytes**, plus **128 virtual bytes** of unknown
owner/use. A known assembly owner does not establish the meaning of opaque
copied data. ASM contributions include 30,470 bytes total: 25,885 instruction
bytes, 4,584 owned data bytes and one padding byte. The C contribution is 7,074
bytes, including 44 switch-table bytes; its four initialized globals are separate.

## Link-3 refactor controls

`build/workers/link/clean_refactor/test_renames.py` temporarily renames GAME's
loc_0072 and its layout value, inserts a comment and blank line, runs
`python tools/verify.py` and `python tools/asmverify.py`, then restores inputs in
a finally block. Both exit 0. Restoring only the layout while retaining the
source rename makes `python tools/fragment.py --output build/link/rename-negative`
and `python tools/verify.py` both exit 2 with the missing cut label named explicitly. Full logs and the successful
renamed verification JSON are retained alongside the script.

An initial plain measurement retained the old late DGDATA EXTRNs and therefore
had 28 differences. Moving those proof-only declarations back to the clean
source's normal header and deriving their late placement restores the required
35 (GAME 2, SOUND 26, DGDATA 7). OFFSET/string labels remain unchanged.
The bootstrap datagen now emits the same natural header. This required no
source instruction change or additional byte transformation.

The restored canonical inputs were rebuilt and reverified after the controls.
Historical experiments below describe the reviewed link-2 context; static
fragment source and independent piece-map requirements in that context have
been superseded by the generator and two-build gates above.

## Release axis: no discriminator

The reviewed 35-position baseline is frozen in `build/workers/link/releases/baseline/`.
All unique TASM/TASMX/TASM32 binaries found under C:/tools were hashed; duplicate
paths are retained in releases/inventory.json. The private runner verifies the
binary and locked MS-DOS Player hashes before invocation. No lock file was changed.
The 14 runnable 2.x..5.0 binaries preserve exact contribution bytes and the same
2/26/0/7 GAME/SOUND/TIMER/DGDATA order differences. No toolchain-lock change is
proposed. The pinned 3.0 tools reproduce the generated proof variant.

| Version | Candidate path | SHA-256 | Unchanged baseline result |
|---|---|---|---|
| 2.51 | `C:\tools\borland-c++-2.0\files\BIN\TASM.EXE` | `712e4127e470e056c8b7ddda802039f1fe64b509941ba8d820ff8bc7a955c57a` | exact bytes; order differences 2 / 26 / 0 / 7 |
| 32-bit runtime | `C:\tools\borland-c++-2.0\files\BIN\TASMX.EXE` | `d1cf3399545b567c58e30b18fa5cfa53c513f8c0bc7159e3def7e819b8e8d2cc` | exact bytes; order differences 2 / 26 / 0 / 7 |
| 3.0 | `C:\tools\borland-c++-3.0\files\BIN\TASM.EXE` | `c338721a4280f0302a4ba5505a94da2057fa155a83fa512379eecc83738013df` | exact bytes; order differences 2 / 26 / 0 / 7 |
| 3.0 | `C:\tools\borland-c++-3.0\files\BIN\TASMX.EXE` | `ac710334231e1a777e77037e58b26c6c976de01402639c8318359a4499371962` | exact bytes; order differences 2 / 26 / 0 / 7 |
| 3.1 | `C:\tools\borland-c++-3.1\files\BIN\TASM.EXE` | `80534cd6a1e2c2b4376ae3f21954c6dbfa77a6998d5e0bf8b8bee6153f3174ea` | exact bytes; order differences 2 / 26 / 0 / 7 |
| 3.1 | `C:\tools\borland-c++-3.1\files\BIN\TASMX.EXE` | `421decd9cde792c49cc35c096c93e092df98188e96fc43a58e00ee48a21b2724` | exact bytes; order differences 2 / 26 / 0 / 7 |
| 1.0 | `C:\tools\borland-turbo-c-2.00-empires\TASM.EXE` | `754b70821e4bac4997f398e3bdcee0f046a42cc3dad89cfbe0138f67d5b6142b` | GAME rejected; SOUND 8576, TIMER 830 bytes |
| 3.2 | `C:\tools\bp70\TASM\TASM.EXE` | `c2fbb4bb57a34815f337046a2ec476b6b5c8a4e29a7e65aab407b0d77b440869` | exact bytes; order differences 2 / 26 / 0 / 7 |
| 3.2 | `C:\tools\bp70\TASM\TASMX.EXE` | `e742d1cb691e425b84b24af0567729dd4848a0804455bb759d7b09d495242185` | exact bytes; order differences 2 / 26 / 0 / 7 |
| 1.01 | `C:\tools\tasm-1.01\files\disk01\TASM.EXE` | `c58db9e628469769f8ddd69a9288d333d5875558c51925d7e8218a66c205a549` | GAME rejected; SOUND 8576, TIMER 830 bytes |
| 2.0 | `C:\tools\tasm-2.00\files\disk01\expanded\TASM\TASM.EXE` | `672cc3814fb66fcb73550aa5ad98049bb52ebcd66c66dcdedbe81d83335e62ff` | exact bytes; order differences 2 / 26 / 0 / 7 |
| 2.01 | `C:\tools\tasm-2.01\files\disk01\expanded\TASM\TASM.EXE` | `48dd9b48dd83a0041ea4b820379146b10de5f44b3e2633778a35d062f2e1814c` | exact bytes; order differences 2 / 26 / 0 / 7 |
| 4.0 | `C:\tools\tasm-4.0\expanded\TASM.EXE` | `30b5dd70bb8d9770905b78ed943b19e351fc1ca685498863acb85a754156b3b5` | exact bytes; order differences 2 / 26 / 0 / 7 |
| 32-bit runtime | `C:\tools\tasm-4.0\expanded\TASM32.EXE` | `0307e863a7769d944fd8621c6d9d8b859f72d6c2acea20bd970934d1c406203d` | DPMI32VM initialization fails, exit 83 |
| 4.0 | `C:\tools\tasm-4.0\expanded\TASMX.EXE` | `0cac03ef7365ac1309ae9999a356f5a6b91c87b6fab5435b859e081f10c4292b` | exact bytes; order differences 2 / 26 / 0 / 7 |
| 4.1 | `C:\tools\tasm-5.0\expanded\TASM.EXE` | `cafc42bbd1df39ab36e775be74ccb82c0a80da7d2a6dff4dcc2f16ba0e220f95` | exact bytes; order differences 2 / 26 / 0 / 7 |
| 32-bit runtime | `C:\tools\tasm-5.0\expanded\TASM32.EXE` | `ba50fe547863b96242d98cff54cdf95ab268a8682395afad172eedbfc46c5b26` | DPMI32VM initialization fails, exit 83 |
| 4.1 | `C:\tools\tasm-5.0\expanded\TASMX.EXE` | `0c2f542d66294ac76d079da52a75b6197b7c04da8530b94c063f88f137d3b9f8` | exact bytes; order differences 2 / 26 / 0 / 7 |

TASM 1.x rejects GAME's PROC syntax and emits nonmatching SOUND/TIMER extents.
TASM32 4.0/5.0 fail DPMI initialization under the required runner, including after
their hashed runtime/OVL dependencies are staged; they did not assemble a source.

## Probe record and controls

The acceptance build relies on the measured segment-order rule above. Expression
pool experiments also show that forward-reference order depends on other fixups,
including non-DOS offset fixups, and on internal batching. The 22-entry control
is an observation for its stated source, not a universal buffer-size claim.
Every probe below retains input sources, logs and results under the worker tree;
the frozen per-variant inputs identify the exact pre-promotion context.

| Driver under build/workers/link/ | Exact tools/options and result |
|---|---|
| releases.py | Private hash-checking MS-DOS Player wrapper; each candidate `/kh8192 NAME.ASM,NAME.OBJ,NAME.LST`, compatible no-/kh fallback when rejected. Frozen reviewed baseline and all inputs/logs/objects retained under releases/. No candidate release fixes the baseline stream. |
| tasm32deps.py | TASM32 /kh8192 TIMER.ASM,TIMER.OBJ, with hashed local TASM32/32RTM/RTM/DPMI16BI/DPMI32VM files staged. Both versions still exit 83 before assembly. |
| emission.py | Pinned `TASM P.ASM,P.OBJ,P.LST`: earlier/later/external targets; segment/group/label/SEG label; MOV/DW/DD/CALL; record boundaries; JUMPS, PROC and LOCAL. Every small source, listing and decoded record stream retained in emission/. |
| emission_mix.py | Same command; known/forward external and other-segment calls, EQU aliases, zero/nonzero addends, conditional branches. Missing ASSUME for a later CODE segment rejects some controls; these are recorded errors. |
| emission_prefix.py / emission_header.py / emission_regs.py | Same command: prior NOP/data/far-call/offset/branch/public declarations, full resident header, and all eight immediate destination registers. Register/header choice does not explain the old ordering. |
| countprobe.py / windowprobe.py | Same command: 1..320 known fixups, forward references, DW versus MOV, extra NOPs. A 32-known-fixup control emits 22 known entries, then the forward entry, then the rest. This batching is not simply the LEDATA byte limit. |
| hashprobe.py | Default, /kh4096, /kh8192, /kh16384: no observed order change in the controlled cases. |
| flagmatrix.py | /kh8192 plus /zi /zd /q /z /l /la /m1 /s /a /mu /jMASM /jNOJUMPS: old baseline order unchanged. /ml and /mx preserve spelling and are rejected by the uppercase-only baseline binding adapter; not an encoding discriminator. |
| predict.py / delayprobe.py | /kh8192: forward frame aliases/labels, defined 0..128 instructions after their uses. No complete solution. EXTRN inside CODE selects the wrong frame; closing/reopening avoids that frame error but does not solve order. |
| splitsound.py | /kh8192 and TLINK /m /s: resident prefix in an earlier combined-segment object, code in another; top/tail base EXTRN. Exact image, unchanged remaining order; not retained. |
| groupsound.py / groupsound_native.py | Same tools: DATA before CODE physically, source CODE before/after DATA, native variables and pointer immediates. Initial variants have 12/4 offset differences; explicit group-relative offsets restore the image. Forward DATA frame anchors can reduce remaining positions to 20, but do not complete the stream; not retained. |
| realdatarefs.py | Same tools: DS equates converted to actual exported DGROUP label aliases. Image exact; GAME/both give 32 differences and TIMER gives 28. Not retained. |
| semantic_sound.py | Same tools: nine code-supported immediate buffer/table pointers converted to OFFSET, compact/explicit resident data and forward frame anchors. Initial WORD PTR OFFSET forms grow code and are rejected; corrected forms retain size but do not solve order. Not retained. |
| assumeprobe.py | Same tools: CS group, CS:nothing, omitted CS assumption; explicit local far-call instructions. One-member group retains the image but does not solve order; absent CS is rejected for near transfers. |
| dgnormal.py | Same tools: real menu/string offset fixups plus late asset EXTRNs reproduce all eight DGROUP relocations. Pointer-offset-only variant does not. Real OFFSET/string labels are maintained; late EXTRN placement is now derived only. |
| groupbranch.py | TASM then TLINK: LOC0 cross-segment short branches land one byte early without +1; LOC1 near call lands correctly. This establishes the source addend used in grouped fragments. |
| segmentorder.py | TASM /s versus /a then TLINK: SEGDEF and LEDATA/FIXUPP order both follow the selected segment ordering. GROUP member order does not determine physical layout. |
| fragments.py / pack_candidate.py | /kh8192, then original TLINK /m /s and PKLITE: grouped code fragments plus an empty physical-order object reproduce complete expanded and packed files. Earlier GAME trial loses EVEN padding after a fragment-origin change; an explicit padding NOP restores it. The reviewed static files were replaced by the mechanical derivation described above. |
| gate_controls.py | /kh8192: wrong real callee is rejected despite equal sites/order; the former grouped-object gate rejected reordered declarations despite equal bytes/sites; the current clean gate treats order as diagnostic and the whole-program proof enforces it. Synthetic instruction-data and empty listing controls are also rejected. |


The controlled PKLITE reversal experiment from the first phase still applies:
reversing all 525 tuples changes packed bytes, and expansion retains the reversed
order. It was a scratch packer-input experiment, never an acceptance build patch.

Earlier failed hypotheses and their exact commands are preserved in
`build/workers/link/phase1-link.md`; the original partial report is
`build/workers/link/REPORT-phase1.md`. Shared runtime/data-worker documentation
and the oracle/region locks were not edited by this work.
