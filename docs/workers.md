# Worker conventions

Workers are Codex agents started by the supervisor. Each has one work order, one set of files
it may write, and one report. Read `docs/executable.md` first; `docs/evidence.md` for background.

## Shared facts

- Working target: `build/oracle/UGH_X.EXE` (expanded executable; `python tools/oracle.py`
  recreates it). Load image starts at file offset A00h. `tools/common.py` has the `MZ` reader.
- Frames (segment values relative to load): 0000 runtime `_TEXT`, 013B game (ASM),
  0664 sound (ASM), 0878 C module, 0A32 timer (ASM), 0A67..5B63 far data, 5C09 DGROUP.
  A relocation site holds a frame value; the image is unrelocated, so a segment immediate in a
  disassembly is a relocation, not a constant. Check `MZ.sites` before reading one as a value.
- Tools: Borland C++ 3.0 (`BCC`, `TASM` 3.0, `TLINK` 5.0, `TLIB`) and `PKLITE` 1.15, run only
  through `tools/dos.py` (`from dos import dos`), which checks hashes and runs them under
  `C:\tools\nmlgcdos\msdos.exe`. Include files: `C:\tools\borland-c++-3.0\files\INCLUDE`;
  libraries: `...\files\LIB\HLIB` (`C0H.OBJ`, `CH.LIB`); startup source: `...\files\STARTUP`.
- TLINK reads `+` in a path as a separator: copy objects and libraries into your build
  directory and use plain 8.3 names. DOS tools need 8.3 file names and CRLF is safest.
- Python 3 with `capstone` is available. Capstone's 16-bit mode prints `cwde`/`cdq` for
  `cbw`/`cwd` (opcodes 98h/99h without a 66h prefix); correct for it.
- Other versions of TASM, Borland C++ and other DOS tools are under `C:\tools`
  (`C:\tools\CATALOG.md`). Read-only.
- Sibling projects, read-only, for ideas and reusable code (copy what you need, do not import
  across projects): `D:\Prog\pre2_recon` (TASM-origin game: `tools/build.py`, `verify.py`,
  `omf.py`, `explore.py`, `docs/executable.md`), `D:\Prog\duke1_recon`, `D:\Prog\dazzle_recon`
  (PKLITE), `D:\Prog\ai_decomp\skills\matching-decompilation\references` (compiler notes:
  `compilers/borland-c.md`, `compilers/assemblers.md`, `verification.md`, `matching-loop.md`).
- The Amiga original is in `assets/amiga/` (ADF). It can explain what something means; it
  proves nothing about DOS bytes.

## Rules for every worker

- Write only the paths your work order lists. Scratch files go in `build/workers/<name>/`.
  Never write to `assets/`, `metadata/oracle.json`, `AGENTS.md`, or another worker's paths.
- Do not commit, stage, or change Git state. The supervisor reviews and commits.
- Do not run the game or any original program other than the pinned tools. Leave no background
  processes.
- Never relock the oracle. Never derive expected bytes from your own output.
- No original code bytes as source: no `db` for code, no patching of outputs. Data may be `db`.
- A claim is "verified" only with a command that shows it; otherwise call it supported or a
  hypothesis. Record failed hypotheses with the exact tool and options.
- You run non-interactively: never wait for input. A decision that is not yours is a blocker
  to report, with the options.
- Work autonomously and keep going while you have productive directions. Stop at a natural
  decision point: done, a real blocker, or directions exhausted.

## Report

Write `build/workers/<name>/REPORT.md` (details, tables, negative results), and make your final
answer at most 15 lines, first line `STATUS: done | partial | blocked | failed`, then: outcome,
verification evidence (command -> result), blockers, suggested next step. Proposed changes to
files you may not write (for example `metadata/regions.json`) go in the report as exact text.
