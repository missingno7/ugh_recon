# Reconstruction constraints

Goal: readable source of the DOS game Ugh! (`UGH.EXE`, Ego Software / Play Byte, 1992) that the
original tools rebuild into the original file, then a portable C translation verified against
it, as the base for a native port.

```
UGH.EXE  <- byte exact ->  TASM + C source  <- differential tests ->  portable C  ->  port layer
```

Read `docs/executable.md` and `docs/evidence.md` before changing anything.

## Rules

- `assets/` is immutable oracle evidence and is not in Git. Work on copies under `build/`.
- Proof is byte equality with the packed `UGH.EXE` after PKLITE 1.15, relocations included.
  Similar, masked or partial results are diagnostics and are reported as such.
- No original code bytes in source: no `db` blobs for code, no `INCBIN`, no post-build patching.
  Unknown bytes stay as labelled UNKNOWN spans and count as debt.
- The three assembly segments are assembly-origin: reconstruct them as TASM source. The C
  module is matched as C under Borland C++ 3.0. Runtime code is taken from the original
  `C0H.OBJ` and `CH.LIB`, never rewritten.
- Report classes separately: exact ASM, exact C, runtime (library), data with known owner,
  UNKNOWN. A C translation of assembly is behavioural and never counts as a match.
- `metadata/oracle.json` is relocked only with `--force` and a stated reason.
- `metadata/regions.json` is curated by hand; `tools/census.py` must pass after every edit.
- Names are modern reconstructions. A thing gets a name only when the code shows what it is.
- Record failed hypotheses with the exact tool and options in `docs/executable.md`.
- The Amiga version (`assets/amiga/`) is the original game and a source of meaning only; it
  proves nothing about DOS bytes.

## Source layout and proof

- `src/asm/GAME.ASM`, `SOUND.ASM`, `TIMER.ASM`: maintained assembly, one code segment per module.
- `src/c/module.c`: the C module (BCC 3.0 `-mh -2`). `src/data/*.ASM`: data modules, raw `db`
  dumps for now (debt).
- Edit only the clean sources under `src/`. The fragmented proof sources and `LAYOUT.ASM` are
  generated under `build/link/` by `tools/fragment.py`; never edit them.
- `metadata/reloc-layout.json` is a relocation-table-derived reproducing layout, not recovered
  source structure. A label rename must update the source and the matching value in its flat
  `labels` dictionary together.
- Finding the natural source arrangement that makes TASM emit the original relocation order
  would retire `fragment.py`; until then the plain build is expected to differ in exactly 35
  table positions and `verify.py` fails if that number changes.

## Commands

```
python tools/verify.py           # the gate: plain build (image + relocation set), proof build
                                 # (packed file equal), identical load images; exit 0 = all three
python tools/asmverify.py        # assembly contributions in isolation
python tools/cjudge.py           # C functions in isolation
python tools/libmatch.py         # runtime attribution against C0H.OBJ and CH.LIB
python tools/oracle.py           # original file, expansion and repack against the lock
python tools/census.py           # coarse region table; --relocs lists link-order evidence
```

Run `verify.py`, `asmverify.py` and `cjudge.py` before proposing any change to `src/`.

Tools run under `C:\tools\nmlgcdos\msdos.exe` through `tools/dos.py`, which checks each binary
against `metadata/toolchain-lock.json`. Worker conventions: `docs/workers.md`.
