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
