# Ugh! reconstruction

Reconstruction of the DOS game Ugh! (Ego Software / Play Byte, 1992) from `UGH.EXE`.

Status: bootstrap. The oracle is locked and every byte of the program is classified; no source
has been reconstructed yet.

| | Bytes | Share |
|---|---:|---:|
| Hand assembly (game, sound, timer) | 30,496 | 7.5 % |
| Compiled C (Borland C++ 3.0, huge model) | 7,072 | 1.7 % |
| Borland runtime | 5,040 | 1.2 % |
| Data | 366,670 | 89.6 % |

```
python tools/oracle.py     # needs assets/dos/UGH.EXE and the tools in C:\tools
python tools/census.py
```

- `docs/evidence.md` — what is known about the DOS and Amiga versions
- `docs/executable.md` — oracle chain, layout, link order, toolchain evidence
- `metadata/` — oracle lock, toolchain lock, region classification
- `AGENTS.md` — working rules

The original game files and the historical tools are private local inputs and are not part of
this repository.
