# Ugh! (Ego Software / Play Byte, 1992) — evidence note

Recorded 2026-11-12. Measurements were made on scratch copies; `assets/` is untouched.
"Not checked" means not looked at, not a negative result.

## Oracle set

| File | Size | SHA-256 |
|---|---:|---|
| `assets/dos/UGH.EXE` (dated 1992-10-07) | 139,685 | `1058cad6771a540f75b109dbe77adda1f6590e7c0309349482c601542e459e7a` |
| DOS image expanded with `PKLITE -x` (1.15) | 411,838 | `ef93d2cd5eb558f6a7d0007e0109f2e9ee952dc125389d7a6256646087636d7c` |
| `assets/amiga/Ugh! (1992)(Play Byte).adf` | 901,120 | `d2418ca9a3ebceab358dd2c46f0d4df8d0992540c2f91b39a2a28cbfde2ec9fc` |

The ADF's provenance (original, crack, re-master) is not established. Only one copy of each
version has been seen.

## DOS version

- Packer: PKLITE 1.15, standard mode. `C:\tools\pklite-1.15\PKLITE.EXE` on the expanded file
  reproduces `UGH.EXE` byte for byte (verified).
- Expanded MZ: header 0xA00, 525 relocations, entry 0000:0000, no overlay tail.
- Linker: TLINK signature `01 00 FB 50` in the header (version byte 0x50).
- Runtime: "Borland C++ - Copyright 1991 Borland Intl."; startup equals BC++ 3.0 `C0H.OBJ`
  (huge model) on 476 of the first 512 bytes. BC++ 2.0 and 3.1 startups score at most 168.
- Code, by relocation-target segment (boundaries approximate):

| Segment | Bytes | Origin | Notes |
|---|---:|---|---|
| 0000 | 5,040 | Borland startup + runtime | |
| 013B | 21,136 | TASM assembly | main game; 527 `jcc`+3×`nop` (JUMPS); VGA ports, joystick 0x201 |
| 0664 | 8,512 | TASM assembly | sound: AdLib 0x388/0x389, DMA and PIC ports |
| 0878 | 7,072 | compiled C, huge model, `-2` | loads DS=1A37; `enter` for locals |
| 0A32 | 848 | assembly | timer (PIT 0x40/0x43) |

- About 370 KB of data follows the code, embedded in the EXE (not inspected in detail).
- Exact TASM release not pinned; BC++ 3.0's bundled TASM is the first candidate.
- Credits in the image: programmed by Mario Knezovic with Carsten Neubauer; "ORIGINAL AMIGA
  VERSION PROGRAMMED THOMAS KLINGER, BJÖRN ROY"; PC graphics Michael Detert; music and FX
  Haiko Ruttmann. Menu has F3 BOPA!, F4 BONES PARK, F5 CONTROL OPTIONS, absent on Amiga.
- Level passwords are stored in clear text.

## Amiga version

AmigaDOS OFS disk "UG1", 56 files. `s/startup-sequence` runs `loader` then `t`.

| File | Bytes | What | Evidence |
|---|---:|---|---|
| `t` | 158,228 | main game, 9 hunks, not packed | hunk 0 CODE 0x8A54 (35 KB): no `link`/`unlk`, 717 `bsr.w`, direct custom-chip access — assembly |
| `loader` | 42,148 | intro/logo player | compiled C (51 `link a5`/`unlk`), German debug strings; compiler not identified |
| `install` | 19,884 | hard-disk installer | assembly with HiSoft debug hunks (`HEAD DBGV01`, `HCLN`), source name `install3.s`, 319 symbols; offers a "68020-version" |
| `TFMX.obj` | 5,780 | TFMX music replayer | with `mdat.`/`smpl.UGH!-All_Sounds` |
| `*.lo5`, `*.lo1`, `*.lo2` | | graphics, magic `JOKE` (packed) | format not decoded |
| `c/*`, `L/*` | | AmigaDOS system files | |

- The assembler that built `t` is not identified; `install` points at HiSoft Devpac, which is
  a lead, not proof. No Devpac release is in `C:\tools`.
- Whether a separate 68020 build of the game exists on the disk is not checked.
- Level passwords are XOR-obfuscated.
- Credits: programmed by Thomas Klinger and Björn Roy; music Rudolf Stember.

## DOS versus Amiga

- 117 strings are common (level names, menu text, high-score defaults): same game content.
- Only 173 bytes of identical binary runs (three short tables): level and graphics data are
  not stored in the same form.
- Whether the DOS assembly follows the Amiga assembly routine by routine is not checked.

## Web search (2026-11-12, two general queries)

No source release, disassembly or decompilation project for Ugh! found. Not proof of absence;
archive.org, GitHub, EAB and Hall of Light were not searched individually. Reported elsewhere:
written first for the Amiga; C64 conversion by Hans Ippisch.
