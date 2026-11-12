# Assembly reconstruction

`python tools/asmverify.py` freshly assembles the three maintained sources with the pinned
Borland C++ 3.0 TASM **3.0**, using `/kh8192` and its default single pass. All 30,470 bytes of
the observed assembly contributions and all 102 DOS relocation sites match the locked
expanded image. There are **zero instruction-byte encoding exceptions** and zero UNKNOWN
bytes in these contributions.

This is an **object-contribution certificate**: OMF contents and fixups, resolved at the
observed image placements. It is not an original-object identity, natural-link, or packed-file
certificate. Relocation **order differs in all three objects**; the verifier records this
diagnostic explicitly. Integration must still reproduce link order and pass the packed oracle.

## Observed extents

All ends below are exclusive. A frame is a paragraph used in segment words, not necessarily
the first byte of a contribution.

| Source | Frame-relative range | Image range | Code incl. jump reservations | Owned data | EVEN padding | DOS fixups |
|---|---|---|---:|---:|---:|---:|
| `src/asm/GAME.ASM` | 0008..529C | 013B8..0664C | 21,008 | 131 | 1 | 52 |
| `src/asm/SOUND.ASM` | 000C..2143 | 0664C..08783 | 4,052 | 4,451 | 0 | 42 |
| `src/asm/TIMER.ASM` | 0006..0341 | 0A326..0A661 | 825 | 2 | 0 | 8 |

The old frame ranges cut through other contributions:

* Image 013B0..013B8 is the runtime function at 0000:1377 continuing through its RETF.
* Game's last joystick loop branches across image 06640 and returns at 0664B.
* Sound's final two return paths occupy 08780..08783; the C prologue begins at 08783.
* The C jump table beginning at 0A315 continues through 0A325. Byte 0A325 is zero padding
  compatible with WORD alignment of timer. The timer flag is the word at 0A326.
* Timer's last far wrapper ends at 0A661. The following 15 zero bytes are compatible with
  paragraph alignment of the far data beginning at 0A670.

One WORD PUBLIC CODE segment per source is a reproducing structure. GAME/SOUND BYTE versus
WORD alignment is not distinguished by their even starts. WORD is supported for TIMER by the
odd C end and one zero byte. Original names, classes, combine attributes, and the original
number of source files are not recovered. The frame and relocation grouping supports these
three contributions; it does not uniquely prove three historical translation units.

Sources start at offset zero, with no ORG or copied prefix. For example GAME object offset zero
is image 013B8; the linker frame is 013B. Own-segment offset fixups receive the eight-byte
frame displacement. Sources export their actual contribution bases as `ext_013B`, `ext_0664`,
and `ext_0A32`. Cross-frame code anchors use the observed starts in `external_starts` in the
map, including C at 0878:0003. Thus a call to C 0878:1059 has object addend 1056 against its
contribution base, rather than pretending its contribution begins at paragraph 0878:0000.
External data frames are SEG-only anchors; their contents are outside this work order.

## Directives and source evidence

The maintained configuration is MASM-compatible syntax, `.286`, `JUMPS`, explicit SHORT for
unpadded short branches, and the default single pass. `/kh8192` only provides symbol capacity.
No original release discriminator was found: **only TASM 3.0 was executed**. TASM 2.x, 2.51,
3.1 and 3.2 were not tried. Historical IDEAL versus MASM mode remains unknown; the complete
MASM-compatible reconstruction is verified.

* The recursive instruction map identifies 547 GAME, 71 SOUND and 16 TIMER short conditional
  branches followed by three NOPs. This is a fresh instruction-based count, rather than the
  earlier 527-occurrence estimate. Unqualified forward conditions under `JUMPS` reproduce
  these reservations. There is no evidence requiring a NOJUMPS region: explicit SHORT also
  explains unpadded forward conditions. The maintained source also lets JUMPS emit the
  inverse-short/E9 expansion for 6 GAME, 8 SOUND and 1 TIMER long conditionals.
* `call far ptr` to a forward label in the same segment emits `0E E8 disp16 90`; a backward
  call emits `0E E8 disp16`. `build/workers/asm/farcall.py` verifies both using TASM 3.0.
  The source expresses 76 SOUND and 3 TIMER calls this way. Four-byte forward forms, where
  present, remain explicit PUSH CS and near CALL; the observed bytes alone do not identify
  whether those were manually written or preceded by a declaration in the original source.
* GAME 0020..0039 is written as `PROC C FAR USES ds es si di`, with `ARG` declarations at
  BP+6, BP+8, BP+0A, BP+0E. TASM emits its entire ENTER 0, saves, argument accesses, restores,
  LEAVE and RETF exactly. The unused word at BP+8 has no established meaning; combining
  BP+6/BP+8 into a dword argument also fits. This supports PROC/ARG/USES as an explanation,
  without proving the historical author used it. A separate LOCAL word probe emits
  ENTER 2 and BP-2 access. Other routines retain explicit instructions where their directive
  formulation has not been established.
* EVEN before GAME's CS data at 45FC emits the observed 90 at 45FB. This supports assembler
  alignment there. It is different from the zero gaps outside the contributions.
* Full-width immediates use WORD PTR where TASM could otherwise sign-extend a byte. CS
  symbols force the observed 16-bit displacements, while literal small structure displacements
  preserve 8-bit forms. XCHG AL,AH and XCHG BL,BH produce the original ModR/M orientation;
  Capstone's reversed printed operand order does not.
* `.186` also matches all three complete contributions. `.8086` matches TIMER and fails to
  assemble GAME/SOUND. Therefore the instructions require 80186-class features in GAME/SOUND;
  PUSH immediate and ENTER do **not** establish a 286 CPU directive. `.286` is a reproducing
  choice. It is not a recovered historical directive.

## Recursive map and data

`metadata/asm-map.json` binds the expanded file hash, fixes the full contribution extents,
lists each seed/control-flow entry with evidence, and covers every owned byte exactly once.
Code was reached by recursive descent, not by linear sweep through unclassified bytes.

Seeds include startup's game call, far transfers recognized at DOS relocation sites, DGROUP
far pointers, installed interrupt vectors, and callbacks passed to timer. GAME's CS table at
2DB3 and SOUND's 16-way tables at 174B and 1919 add their explicit destinations. DGROUP
descriptor callback fields at 7638, 7674, 76B0, 76EC, 7728, 7772, 78E4 and 7974 close the
game dispatch families. Only their pointer values were read; no DGROUP or far data was emitted.
Branches, calls, LOOP variants, fallthroughs and TASM jump reservations extend the code map.

Some bounded routines have no identified caller. Their entries are explicitly described as
unreferenced pattern-based seeds, not as proven reachable: GAME 0989, 0B4E, 3EA1, 43D7,
44CF, 4E68; SOUND 11C3, 1571, 1B3A; TIMER 030E, 0323, 032F. Their mnemonic reconstruction
and exact assembly are verified; behavioral reachability is not.

Data spans, all owned by the respective assembly contribution:

| Source | Frame-relative data | Evidence |
|---|---|---|
| GAME | 2DB3..2DB9 | CS jump table indexed at 2DFE |
| GAME | 4509..450A | CS byte variable read at 44F7 |
| GAME | 45FC..4634 | CS variables and relocated far-pointer table used by video helpers |
| GAME | 4DDD..4E19 | CS word tables indexed through BP at 4D03/4D0A/4D19 |
| GAME | 4EF7..4EFF | CS state read/written by 4F09 family |
| SOUND | 000C..112B | resident CS variables, tables and buffers; indexed accesses and buffer setup |
| SOUND | 174B..176B, 1919..1939 | CS dispatch tables |
| SOUND | 2058..205C | byte table read by 1F5F |
| TIMER | 0006..0008 | CS flag read at 0008 and written at 0014 |

Function and location names are mechanical. No gameplay meaning is inferred from the names.
Instruction `db` exception list: **empty (0 bytes, 0 instructions)**. Data initializers alone
use DB/DW. The verifier checks their assembled listing locations against the data map.

## Commands and acceptance boundary

```
python tools/asmverify.py
python tools/census.py
python tools/asmgen.py --emit       # explicitly regenerate; overwrites maintained ASM
python tools/asmgen.py --map        # scratch discovery only; does not replace curated map
```

ASM is the maintained source after bootstrap. The verifier never regenerates it. It deletes
each candidate object before assembly, checks the full locked expansion identity, refuses
missing/additional sources or shortened extents, checks initialized OMF coverage and resolves
every offset/base/far fixup. Every resulting byte is compared without masks. The emitted DOS
relocation set must equal the image set, with no duplicates; target mistakes fail the byte
comparison. All original-image expectations come from the locked oracle, never candidate output.

Current objects have 129 GAME, 298 SOUND and 14 TIMER OMF fixups, including the offset fixups
which disappear during linking. Their 52/42/8 segment sites equal the image sites. The original
OMF offset-fixup stream is unavailable, so original OMF identity is not claimed. The JSON reports
under `build/asm/` retain bindings, all relocation sites, the order diagnostic and mismatches.

`python build/workers/asm/negative.py` verifies three independent gate failures on scratch
copies: instruction DB with identical bytes; wrong segment fixup target with the same sites;
and a literal segment value with identical bytes but a missing relocation. All are rejected.

## Failed and inconclusive probes

All assembly commands below use pinned TASM 3.0 through `tools/dos.py`. Logs and sources are
in `build/workers/asm/`, except the first full-source diagnostics retained in this narrative.

| Tool/options and case | Observed result / correction |
|---|---|
| `TASM GAME.ASM,GAME.OBJ,GAME.LST`, initial bootstrap | Capstone `0x` notation is illegal MASM syntax. Numeric bracket expressions can become immediates even with PTR. Converted numbers to suffix-H syntax and used explicit DS for direct numeric memory. Per-instruction labels exhausted default hash space; retained meaningful targets and used `/kh8192`. |
| `TASM /kh8192 GAME.ASM,GAME.OBJ,GAME.LST`, initial CS expressions | Treating small BP structure displacements as relocatable addresses expanded two instructions by a byte. Preserve literal displacement forms unless the original uses disp16. |
| Same command, canonical Capstone XCHG order | Two GAME and two SOUND ModR/M bytes differed. Swapping the printed byte-register operands fixes all four without DB. |
| `TASM USES1.ASM,USES1.OBJ,USES1.LST` and `USES2` | Both PROC-USES and separate USES forms reproduce the save/restore pattern. Initial ARG word/dword layout placed pointers at BP+8/BP+0C, unlike the target's BP+0A/BP+0E. COPYPROC adds the explicit unknown BP+8 word and matches the complete target routine. |
| `TASM COPYPROC.ASM,COPYPROC.OBJ,COPYPROC.LST`, `PROC FAR C` | Extra characters error. `PROC C FAR` succeeds and matches. |
| `TASM CALLS.ASM,CALLS.OBJ,CALLS.LST`, bare forward `call g` | Forward reference needs override. Explicit `call far ptr g` in FARCALL succeeds and emits the observed optimized form. |
| `TASM /kh8192 /m2 MP2G.ASM,MP2G.OBJ,MP2G.LST` | GAME shrinks to 19,485 bytes, 18,918 positional mismatches; relocation sites differ. |
| Same flags, `MP2S` | SOUND shrinks to 8,233 bytes, 3,614 positional mismatches; sites differ. |
| Same flags, `MP2T` | TIMER shrinks to 770 bytes, 590 positional mismatches; sites differ. |
| `TASM /kh8192 P186G/S/T.ASM,...` | `.186` exact for all three; inconclusive for `.186` versus `.286` historical selection. |
| `TASM /kh8192 P8086G/S/T.ASM,...` | `.8086` fails GAME/SOUND instruction validation; TIMER is exact. |
| `TASM DUPPRB.ASM,DUPPRB.OBJ,DUPPRB.LST` | `DB 2 DUP(0)` emits LIDATA. Shared `tools/omf.py` currently decodes that as `01 01` rather than `00 00`. Source uses explicit data initializers and the gate rejects LIDATA pending a separately verified reader fix. No private OMF reader is used. |
| Pointer-store heuristic at GAME 17FD | Treating every 2C2D store as a function pointer falsely suggests 0112, inside reserved branch padding. That field may have scalar uses. Removed this unproved seed and retained its literal value. |
| Frame-boundary assumption | The nominal paragraph bounds split runtime/game/sound instructions and C table data. Replaced them with the contribution extents above. |

`build/workers/asm/mode-checks.json` records the CPU/multipass results. No original game
program was executed. No assets, oracle locks, region census, runtime source or foreign worker
files were changed.
