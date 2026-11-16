# The executable and the oracle boundary

Numbers are hexadecimal unless a unit is given. "Frame" is a segment value relative to the DOS
load segment, as stored at relocation sites. Everything here is measured by `tools/oracle.py`
and `tools/census.py`; re-run them before repeating a number.

## Oracle chain

```
assets/dos/UGH.EXE  --PKLITE -x-->  build/oracle/UGH_X.EXE  --PKLITE-->  UGH.EXE (byte exact)
     packed, 139685 bytes               expanded, 411838 bytes
```

- The shipped file is packed with PKLITE 1.15, standard mode. `metadata/oracle.json` locks both
  files; `tools/oracle.py` re-derives the expansion and the repack on every run.
- **The proof target is the packed file.** A rebuilt executable is accepted when PKLITE 1.15
  packs it to the original 139685 bytes. The expanded file is the working target for
  diagnostics: image, header fields and relocations are compared against it.
- What `PKLITE -x` does not restore is unknown. The expansion may differ from the executable
  TLINK originally wrote in fields PKLITE does not keep. Observed so far: the relocation table
  is *not* sorted, and its order looks like TLINK's module order (below), so order appears to
  survive packing. Not yet tested by packing a file with a known unusual order.

## Expanded MZ

| Field | Value |
|---|---|
| header | A00 bytes; relocation table at 3E, 525 entries, zero padded |
| header bytes 1C..21 | `01 00 FB 50 6A 72` — the TLINK 5.0 signature (a fresh TLINK 5.0 link writes the same six bytes) |
| load image | 409278 bytes (decimal), no tail after it |
| entry | 0000:0000 |
| stack | 63EC:0080 — a 128-byte `_STACK`, the Borland default TLINK lays out |
| min/max alloc | 11 / FFFF paragraphs |

## Layout

`python tools/census.py` prints the full table from `metadata/regions.json`.

| Frame | Bytes (dec) | Class | Content |
|---|---:|---|---|
| 0000 | 5040 | RUNTIME | `_TEXT`: C0H startup, then library members |
| 013B | 21136 | ASM | game; entered at 013B:0008 |
| 0664 | 8512 | ASM | sound (AdLib, DMA) |
| 0878 | 7072 | C | one or more C modules, DS = 1A37 |
| 0A32 | 848 | ASM | timer |
| 0A67 | 64768 | DATA | all zero bytes in the file |
| 1A37..5B63 | 269600 | DATA | 23 far data frames: graphics, levels, sound (owners not established) |
| 5C09 | 32302 | DATA | DGROUP |

Totals: data 89.6 %, assembly 7.5 % (30496 bytes), C 1.7 %, runtime 1.2 %.

Frames come from relocation values, so they are lower bounds on segmentation: a frame can hold
several link segments, and a far data frame with no relocation pointing at it is invisible.

## Link order evidence

The relocation table, in file order, visits source frames in this sequence:

```
0000 (4 sites)  5C09 (8)  013B  0664  0878 (337 sites)  0A32  0000  5C09  0000 ...
```

TLINK emits fixups object by object. Read that way: the startup object first (its code in
`_TEXT`, its data in DGROUP), then game, sound, C, timer, then library members, whose code is
appended to `_TEXT` at frame 0000. A probe link of `C0H.OBJ + module + CH.LIB` with TLINK 5.0
gives the same segment pattern: `_TEXT`, module code, far data, DGROUP, `_STACK`.

Inside frame 0878 the sites run mostly *descending* (331 runs for 337 sites). Descending fixups
within a record are what Borland's compiler emits and what TASM does not, which agrees with
0878 being compiled C.

## Toolchain

| Tool | Evidence | Status |
|---|---|---|
| Borland C++ 3.0, huge model | banner "Borland C++ - Copyright 1991 Borland Intl."; entry code equals `C0H.OBJ` 3.0 on 476 of 512 bytes (2.0 and 3.1 at most 168) | supported; the differing bytes not yet shown to be fixups only |
| TLINK 5.0 | header signature; stack and segment pattern | supported |
| BCC options | `enter` in functions with locals implies `-2` or higher | hypothesis; other options unknown |
| TASM | `jcc` + three `nop` — TASM 3.0 with `JUMPS` emits exactly this for a forward short jump (probe) | release not discriminated; 3.0 is the reproducing candidate |

`metadata/toolchain-lock.json` pins the binaries used, by hash. They are a reproducing
configuration, not a claim about the original development machine.

## Runner notes

- All tools run under `C:\tools\nmlgcdos\msdos.exe` (BCC 3.0 included).
- TLINK treats `+` in a path as a separator, so nothing under `borland-c++-3.0` can be named on
  its command line. Stage `C0H.OBJ` and `CH.LIB` into the build directory first.

## Native session diagnostics (2026-11-16)

These are behavioral composition diagnostics, not new binary-match evidence.
`python tools/nativebuild.py --out build/workers/s7-session/production` rejected the
initial assumption that every actor placement's third word names an itinerary:
stone placements retain zero there. The extractor now represents that ignored
payload as an empty typed identity. The same command rejected insufficient braces
in generated empty enemy initializers under the pinned GCC `-Wall -Wextra -Werror`.

`python verif/s7_session_prefix.py` initially differed in RAM observation at frames
2..5 while devices, ordered I/O and scalars were equal. Independent literal
diagnostics (`python verif/s7_session_prefix.py --diagnose`, inside the bounded
worker runner) identified omitted demo terminator, HUD and reserved record-tail
publications in the test recorder. Correcting the observer yielded six complete
equal records for each of 81 physical openings; no native kernel was changed.

## Native object composition diagnostics (2026-11-16)

These are behavioral composition diagnostics, not binary-match evidence.
`python tools/nativebuild.py --out build/workers/s7-gameplay/production`
initially rejected an incorrect resource-enum spelling (`RESOURCE_SPRITE`);
the admitted type is `RESOURCE_SPRITE_RECORD`. The following link rejected
omitted `native/items.c` from the positive manifest; its unchanged accepted
kernel is now explicitly linked. Missing plain-build scratch was recreated
with `python tools/build.py` before extracting the DATA views.

`python verif/s7_gameplay_objects.py --no-build`, after adding terminal-leg
cases, stopped Unsupported on actor case zero. The hypothesis that the earlier
object graph contained all nineteen actor callback members was false: its
descriptor links stop at +2A, omitting the retirement member +2C. The additive
production extractor reads that DATA member at build time and admits its
already registered typed callback role. No runtime callback-word decoder or
change to the accepted identity registry was introduced. Repeated loader/pass
comparisons and direct terminal/departure/stone/water cases verify the result.


## Native enemy composition diagnostics (2026-11-16)

These are behavioral composition diagnostics, not new binary-match evidence.
`python verif/s7_enemies.py --no-build` rejected the first patrol projection:
it sampled only the incoming direction, while Triopterus can turn before its
frame lookup. Borrowing both direction vectors fixed the composition; the
accepted hazard kernel was unchanged. The same command rejected a renderer
scratch mismatch caused by unequal test page heights (native zero, literal
192). The independent render constructors now explicitly set the same page
geometry, without changing a production rendering algorithm.

`python verif/s7_enemies.py --no-build`, extended with active AdLib owner
projections, rejected repeat=0 for warning, dino and reward effects: the
independent compiled L1 retained repeat=1 and control=5. Only bird flight uses
repeat=0. The enemy caller now supplies those distinct arguments. An additive
`game_audio_effect_stop` entry borrows the unchanged allocation kernel so an
inactive FFFF flight handle retains its ordinary no-op stop result; the older
bounded-channel entry and all accepted audio algorithms are unchanged.

The enemy projection preserves SHL-1 index aliases (bird targets 8000/8001 and
Triopterus platform indices with bit 15 set), while the physical comparison
words keep their raw high bits. Independent odd animation-cursor samples retain
raw high sprite bytes. These are typed composition observations, not additional
executable-byte ownership or reconstruction claims.

## Native frame composition diagnostics (2026-11-16)

Behavioral evidence only; no new binary-match bytes or changed matching sources.

- `python verif/s7_frame.py tests/scenarios/gameplay.txt --build --out
  build/workers/s7-frame/gameplay` reached 15 exact records, then the requested
  enemy stub stopped at the initial fruit-tree update. The hypothesis that the
  ordinary first level is enemy-free is false: CAVITY has an active tree slot.
  The same boundary applies to the full gameplay-AdLib trace; a prefix is not
  its 979-record certificate.
- `python verif/s7_frame.py tests/levels/one-08.txt --out
  build/workers/s7-frame/openings/one-08` initially differed only in the first
  two device records. The component recorder retained the boot IRQ count;
  setting the explicit component fixture's IRQ count to zero fixed observation.
- `python verif/s7_frame.py tests/levels-audio/adlib-43.txt --out
  build/workers/s7-frame/audio/adlib-43` initially had 360 equal RAM/device/scalar
  records but a differing cumulative log. The recorder had reused gameplay's
  score-file-dependent seed DOS operand. Restoring this scenario's operand
  yielded all 360 complete records. Initial joystick/BIOS scripts also require
  the oracle fixture's run compression; later Clock waveform replacements do not.
- `python verif/s7_frame.py tests/scenarios/departure.txt --out
  build/workers/s7-frame/scenarios/departure --dump 1` exposed two differing
  gameport OUT operands in the calibration prefix. A separately bounded
  `verif/s7_frame_diagnose.py` run against the literal DLL equaled original ASM
  and identified both original values as the live presence byte (F0), versus
  native zero. The composition now forwards that byte to the unchanged input
  algorithm. Controls and timeout waits likewise forward the preceding scan
  operand through the existing typed trigger entry. No accepted input kernel
  changed.
- `python verif/s7_frame.py tests/native-frame/pause-escape.txt --out
  build/workers/s7-frame/deep/pause-escape` initially differed only in the final
  return-observation word: a returned near component observes zero, rather
  than its consumed FFF0 sentinel. Correcting the observer yielded 331 equal
  records, including the raw pause release/make/break handshake and lives FF.
- `python verif/s7_frame.py tests/native-frame/menu-session-return.txt --out
  build/workers/s7-frame/deep/menu-session-return --dump 344` initially differed
  only in terminal RAM. Independent literal diagnostics matched all original
  ASM records and found the absent C shutdown-latch publication. The inherited
  audio recorder published that latch only when a timer table existed. The new
  frame observer publishes it unconditionally; production already held one.
  All 345 records now agree through resumed-menu Q and terminal exit.

The frame recorder links audited production objects, replacing main and wrapping
three typed presentation/frame cuts plus the temporary enemy boundary for output
metadata. Wrappers do not import expected state or change native continuation
operands. It uses incremental cumulative I/O hashing and retains raw dumps only
for an explicitly requested diagnostic frame. Its per-level 100000-frame bound
is diagnostic; production has no such exit rule.

The first common-gate attempt (`python tools/gate.py --jobs 3 --out
build/workers/s7-frame/gate`) rejected native composition's collision-cell
literal `0x720`: it coincided with an original code offset under the unchanged
closure audit. The composer now spells its ten geometric deltas in 96-cell row
units (19/6/12 rows), as in the accepted pixel primitive. This is not an address
resolver or an audit exemption. After a fresh production build, all native COFF
loadable sections (.text/.data/.bss/.rdata/.xdata/.pdata) are byte-identical to the
preceding audited object; `geometry-spelling.json` records the check. A fresh
one-43 recording also passes all 160 complete records. This native artifact
comparison is not new original-game binary-match evidence.
