# Ugh! reconstruction

Reconstruction of the DOS game Ugh! (Ego Software / Play Byte, 1992) from `UGH.EXE`.

Status: **full-file proof reached.** `python tools/verify.py` builds the whole program from
source with Borland C++ 3.0, TASM 3.0 and TLINK 5.0 plus the original `C0H.OBJ` and `CH.LIB`,
and PKLITE 1.15 packs the result into the original `UGH.EXE`, byte for byte.

| Class | Bytes | State |
|---|---:|---|
| Hand assembly code (game, sound, timer) | 25,885 | exact; all 286 routines have contract comments, 257 named |
| Compiled C (sound and music front end) | 7,074 | exact; 23 functions named |
| Borland runtime | 5,048 code + 834 data | linked from the original library |
| Data, typed and labelled | 100,103 | strings, tables, level records, headers |
| Data, payload with a known format | 223,409 | sprite pixels, maps, music events, samples |
| Data, Pack-Ice streams | 42,138 | packed `db`; an exact Python packer exists, not used by the build |
| Data, UNKNOWN | 4,593 | 4,584 in tables owned by the sound module, 9 elsewhere |

Known debt:

- Relocation order is reproduced by a derived proof variant, not by recovered structure. The
  maintained assembly is plain (one segment per module) and builds to the exact image, header
  and relocation set, with 35 table positions in a different order. `tools/fragment.py` derives
  a fragmented variant from it (cut points and piece order in `metadata/reloc-layout.json`,
  taken from the original's relocation table) that reproduces the packed file. `verify.py`
  requires both builds and identical load images. See `docs/link.md`.
- Names are modern reconstructions from static reading, corrected where translation and
  testing contradicted them. Local jump labels are still mechanical.

## Portable C translation (`c/`, `tests/`)

A literal C translation of the program on the original memory layout, compared routine by
routine with the rebuilt program under an emulator (`tools/difftest.py`). It is behavioural
evidence, not a byte match, and it is deliberately not idiomatic C: it is the verified
reference for a later native port.

| | |
|---|---|
| Routines translated and directly tested | 277 of 284 (3 more exist only inlined in the Pack-Ice decoder) |
| Differential cases, normal and poison modes | 3,677 of 3,677 equal |
| Call edges verified by composed cases | 598; 76 not yet verified |
| Whole-program run against the original | equal for the first two startup frames; not pursued further yet |

Open in the translation:

- Four entries are translated only up to a point where the original itself goes wrong: the C
  sound module calls four game hooks with far calls, the hooks return near, and execution
  continues with a stale segment word on the stack. This affects the Sound Blaster (DSP)
  branch of sound initialisation and the sound-bank loader. The game requests AdLib only at
  startup, so the path is not taken in normal play.
- The tree-reward pool's full-pool path returns through a saved register value; what follows
  depends on stack contents and is documented, not reproduced.
- No SDL3 host and no native (idiomatic) port yet.

```
python tools/oracle.py      # original file, expansion and repack against the lock
python tools/verify.py      # fresh build, compared with the expanded and the packed original
python tools/asmverify.py   # assembly contributions in isolation
python tools/cjudge.py      # C functions in isolation
python tools/libmatch.py    # runtime attribution
python tools/census.py      # coarse region table (boundaries predate the exact extents)
python tools/difftest.py    # C translation against the rebuilt program (add --poison)
python tools/coverage.py    # which routines are translated and tested
```

- `docs/evidence.md` — what is known about the DOS and Amiga versions
- `docs/executable.md` — oracle chain, layout, link order, toolchain evidence
- `metadata/` — oracle lock, toolchain lock, region classification
- `AGENTS.md` — working rules

The original game files and the historical tools are private local inputs and are not part of
this repository.
