# Compiled C contribution (worker cmod)

## Verified result

`python tools/cjudge.py` exits 0: all 23 identified compiled functions match, using pinned Borland C++ 3.0 with `-c -mh -2 -n. UNIT.C`. The contribution is 7074 bytes: 7030 instruction bytes and 44 compiler-generated switch-table bytes. Every function extent and all resolved fixup targets agree. The 337 MZ relocation sites also agree in original record order.

This is a bound-object/function certificate. It is not a rebuilt executable or a packed-file certificate. `python tools/oracle.py` separately passes the existing expansion/repack oracle. No runtime library code has been rewritten. No inline assembly or original code-byte blobs are present in the C source.

Source: `src/c/module.c`. Machine-readable census, callees, globals, all relocation offsets, and external callers: `src/c/inventory.json`. Build outputs: `build/c/module/`. The source uses mechanical function/global names; descriptive roles below are interpretations of the reproduced code.

## Extents and classification

The original frame-based boundary was five bytes too early. The C code and its tables occupy **image 08783..0A324 inclusive**, or `0878:0003..1BA5` exclusive. The final switch table is `0878:1B95..1BA5` and therefore includes image `0A320..0A324`, formerly assigned to frame 0A32.

`0878:0000..0003` contains `retf; stc; retf`. No call root to those bytes was found. They are an **UNKNOWN prefix**, not attributed to compiled C and not counted as matched ASM. They may belong to the preceding contribution; their owner is unproved. No source filler was added to reproduce them.

| Entry | End (exclusive) | Bytes incl. table | Local bytes | MZ sites | Status / supported role |
|---|---|---:|---:|---:|---|
| 0003 | 008A | 135 | 0 | 9 | exact; device-bit initialization |
| 008A | 00F5 | 107 | 0 | 9 | exact; shutdown |
| 00F5 | 0176 | 129 | 4 | 7 | exact; callback-backed data load |
| 0176 | 0691 | 1307 | 10 | 52 | exact; FORM/8SVX sample load |
| 0691 | 06E4 | 83 | 0 | 2 | exact; ADLX channel load wrapper |
| 06E4 | 096B | 647 | 4 | 26 | exact; bank item format dispatch |
| 096B | 09CA | 95 | 0 | 6 | exact; restart/reapply active channels |
| 09CA | 0A70 | 166 | 0 | 8 | exact; stop channel |
| 0A70 | 0AA9 | 57 | 4 | 1 | exact; reverse four bytes |
| 0AA9 | 0CFC | 595 | 16 | 13 | exact; ADLX/AHDR/IMAP/TRCK parsing |
| 0CFC | 0F2D | 561 | 2 | 35 | exact; start channel |
| 0F2D | 0F88 | 91 | 0 | 4 | exact; reset channel cursor |
| 0F88 | 1059 | 209 | 0 | 12 | exact; start main track |
| 1059 | 1128 | 207 | 0 | 16 | exact; stop/fade main track |
| 1128 | 11AD | 133 | 2 | 9 | exact; apply track volume |
| 11AD | 1491 | 740 | 24 | 29 | exact; scan two track positions |
| 1491 | 14BB | 42 | 0 | 3 | exact; clear track flag |
| 14BB | 1768 | 685 | 8 | 44 | exact; restore displaced channel state |
| 1768 | 1852 | 234 | 2 | 13 | exact; stop/release ADLX channel |
| 1852 | 1943 | 241 | 2 | 6 | exact; select free/oldest channel |
| 1943 | 1A50 | 269 | 0 | 20 | exact; restore main-track state |
| 1A50 | 1A8E | 62 | 0 | 5 | exact; elapsed ticks divided by rate |
| 1A8E | 1BA5 | 279 | 14 | 8 | exact; scan total track duration |

The two tables are `1475..1491` (seven case values and seven target offsets, 28 bytes) and `1B95..1BA5` (eight dense target offsets, 16 bytes). The latter has index 5 mapped to the default arm. They are compiler-owned data, not additional functions. All other bytes in the contribution disassemble through the identified function returns.

## Compiler profile and one-axis probes

The first probe wave used the real functions 008A, 0A70, and 1491 before reconstructing the large bodies. It reproduced all three with `-mh -2`; changing only model to `-ml` or `-mc`, or adding `-O`, `-O1`, `-O2`, `-G`, or `-N`, broke controls. The final wave repeats the axes on the complete TU: `python build/workers/cmod/options.py`. Exact commands, per-function results, compiler messages and object SHA-256 values are in `build/c/probes.json`; objects are in `build/c/probes/<axis-number>/`.

Each table row is invoked as pinned `BCC -c <options> -n. UNIT.C`; no options file or project configuration is supplied. Counts below include uniform TU target placement, so a changed predecessor can also invalidate a caller.

| Options | Exact functions | Interpretation |
|---|---:|---|
| -mh -2 | 23 | reproducing baseline |
| -mh -0 | 0 | rejected option; BCC 3.0 has no -0 spelling |
| -mh -1 | 23 | indistinguishable from -2 on all functions |
| -mh -3 | 0 | rejected option; BCC 3.0 has no -3 spelling |
| -mh | 2 | default instruction set fails enter/imul/shift code |
| -mh -1- | 2 | disabling 186 selection fails |
| -mh -2- | 23 | observed same output; not a discriminator |
| -ml -2 | 0 | large model fails DS/huge-module assumptions |
| -mc -2 | 0 | compact model fails far code/DS assumptions |
| -mh -2 -O | 2 | optimization must remain disabled for this source |
| -mh -2 -O1 | 0 | optimization changes code |
| -mh -2 -O2 | 0 | optimization changes code |
| -mh -2 -G | 0 | speed/global optimization changes code |
| -mh -2 -Z | 9 | alias optimization changes code |
| -mh -2 -r- | 5 | register variables needed |
| -mh -2 -k- | 8 | standard stack frames needed |
| -mh -2 -N | 0 | stack overflow checks absent |
| -mh -2 -d | 23 | same code; this axis is not independently discriminated |
| -mh -2 -a | 12 | word alignment changes local layout/code |
| -mh -2 -P | 23 | C++ front end has identical code after unambiguous name demangling |
| -mh -2 -K | 23 | same code; this axis is not independently discriminated |
| -mh -2 -v | 23 | debug information changes object records, not function bytes |
| -mh -2 -y | 23 | line information changes records, not function bytes |
| -mh -2 -O- | 23 | same code; this axis is not independently discriminated |
| -mh -2 -G- | 23 | same code; this axis is not independently discriminated |
| -mh -2 -Z- | 23 | same code; this axis is not independently discriminated |
| -mh -2 -r | 23 | same code; this axis is not independently discriminated |
| -mh -2 -k | 23 | same code; this axis is not independently discriminated |
| -mh -2 -N- | 23 | same code; this axis is not independently discriminated |
| -mh -2 -d- | 23 | same code; this axis is not independently discriminated |
| -mh -2 -a- | 23 | same code; this axis is not independently discriminated |
| -mh -2 -K- | 23 | same code; this axis is not independently discriminated |

The defensible configuration is huge model, 186/286-class instruction generation, ordinary stack frames and register variables, no stack checking, no tested optimization switches, and default alignment. `-1` and `-2` are both reproducing configurations: ENTER alone never established 286 specifically. C versus C++ mode, `-K`, `-d`, and debug/line output cannot be settled from these bytes. All character data in the recovered source has explicit unsigned types. Exact historic command-line spelling is unobservable on those axes.

## Translation-unit structure

One source file reproduces **one byte-aligned CODE segment of 7074 bytes** and **one word-aligned FAR_DATA segment of 4 bytes**. Every public code offset plus 3 equals its oracle offset, with no per-function placement adjustment. Both generated tables and every no-fixup relative call agree in that placement. There are no inter-function padding bytes. This and the exact 337-site relocation order strongly support one compiled TU in the recovered function order. This is a reproducing TU boundary; an indistinguishable original division cannot be excluded solely from linked bytes.

Earlier definitions use the compiler-generated four-byte `push cs; call near` sequence. Forward definitions retain a five-byte far-call fixup in the object, which TLINK 5.0 relaxes to `nop; push cs; call near` without changing extent. A pinned control (`python build/workers/cmod/linkprobe.py`) verifies that transformation. `python build/workers/cmod/structcheck.py` independently prints segment sizes, uniform +3 placement, and exact ordered relocation agreement.

The judge reads shared `tools/omf.py`. A private reader was used before that worker delivered the shared reader; it survives only as scratch evidence and is not a dependency. The shared reader currently calls the OMF LOCAT M bit `self_relative`; the adapter explicitly inverts it because M=1 denotes segment-relative addressing. The judge validates record checksums, rejects unsupported records, resolves target bindings, requires uniform code placement, checks relocation sites and their order, rejects unmarked code publics, and rebuilds fresh. It does not rewrite the object or patch a build output.

## DS=1A37 data and far storage

The only direct DS globals touched by compiled C are:

| Offset | Width | Reproducing declaration | Observed use |
|---|---:|---|---|
| 0000 | 2 | `int g_0000 = 0` | initialization has run |
| 0002 | 2 | `int g_0002 = 0` | shutdown has run |

The candidate contributes four initialized zero bytes, equal to image `1A37:0000..0004`. The next twelve file bytes are zero and the separately referenced frame 1A38 begins with `ICE!`; this is a 16-byte file interval, not evidence for a 64-KiB C BSS. The reproduced object has no additional uninitialized C segment. The code establishes four accessed bytes. The remaining twelve zero bytes are compatible with alignment before the next asset, but unused storage versus padding is not independently settled. No code evidence supports extending this module's DS storage beyond offset 000F.

An uninitialized-definition control (`int g_0000; int g_0002;`, otherwise the same TU) produces no FAR_DATA LEDATA, keeps segment size 4, and reverses these mechanical names' offsets (g_0002=0, g_0000=2). Thus original initialization syntax and original variable names are not recovered by the zero bytes. Explicit initialization in the canonical source is a natural reproducing declaration, not proof of original spelling.

All other global accesses bind to **frame 0664**, including writable data located in the assembly sound segment. There are no direct references to DGROUP 5C09 and no references to other far-asset frames in these C functions; asset pointers arrive as arguments or through the sound globals. Far-global lists are recorded per function in the inventory. The principal layouts are:

| Sound offset | Source view / extent | Evidence |
|---|---|---|
| 000E | word | polled completion/lock flag |
| 0014 | array of 42-byte `s_0014` | all indexed references multiply by 2Ah |
| 0212, 0216, 021C, 022E | pointer, word, pointer, word | overlap element 12 of the 42-byte array |
| 0236 | word | saved guard/state word |
| 0238 | word | divisor / track tick rate |
| 023A, 023E, 0242 | dwords | time / accumulated tick arithmetic |
| 0246..024C | four words | fade parameters |
| 024E | huge pointer | bank base |
| 0252 | dword | bank extent |
| 0256..025C | four words | track state / volume / flags |
| 025E, 0262, 0266 | three far pointers | scanner output positions / instrument map |
| 026A..0274 | six words | device bits / channel allocation / state |
| 0278, 032C, 03E0 | arrays of 20-byte `s_0278` | all indexed references multiply by 14h; copy lengths 12 or 20 |

The aliased declarations deliberately preserve the observed overlay: `0014 + 12*42 = 020C`, so element 12 fields at +06, +0A, +10, +22 equal globals 0212, 0216, 021C, 022E. Entries 8..11 are selected as transient channels; entry 12 represents the main-track view. These are views of assembly-owned storage, not separate allocations introduced by C.

## Assembly interface

All exported functions are far cdecl: arguments appear from BP+6, words occupy 2 bytes, pointers/dwords 4 bytes; callers remove arguments. The C callee preserves DS, BP and used SI/DI. Return words are AX, returned dwords/pointers DX:AX. Locals use SS. Types of opaque forwarded argument groups in 00F5 are a reproducing choice; the original source types cannot be distinguished where only words are forwarded.

| C entry | Argument order | External assembly callers |
|---|---|---|
| 0003 | unsigned device bit mask | 013B:4F45, passing 1 |
| 008A | none | 013B:4F58 |
| 0F88 | far data pointer, fade/control word, volume word | 013B:0078, 0297, 08BA, 0C75 |
| 1059 | control/fade word | 013B:0065, 017F, 0284, 06CF, 08A7, 0C59, 0FA9, 4F50; all pass 11h |
| 1128 | volume word | 0664:1312 |
| 1768 | channel word | 013B:25A6; 0664:18DD |
| 1852 | far data pointer, volume word, control/count word | 013B:0192, 06E2, 1AFA, 1CE4, 23CE, 2484, 29A2, 2B4E |
| 1943 | none | 0664:19B8 |

No direct far-call site from timer frame 0A32 into the C contribution was found. The call inventory contains all 26 relocated far-call sites found across the image. It records the preceding 18 bytes as argument evidence; internal near calls and every other callee are listed per function. Indirect callers cannot be excluded by that census.

C calls assembly hooks `013B:001C..0020` and sound entries `0664:112B,1211,1331,134E,1377,14B1,1503,1A37,1A65,1A89,1C39,1E97,205C,20B9`. Their source declarations are intentionally mechanical. Runtime calls bind `F_LXMUL@=0000:035B`, `F_PCMP@=0372`, `F_LUDIV@=039D`, `F_LXLSH@=0444`, `F_PADA@=0465`, `F_PADD@=04ED`, `F_PINA@=054D`, and `_memset=106B`. The compiler emits arithmetic and huge-pointer helper calls; source does not implement them. `_memset` and the colliding far-memset library entry cannot be distinguished from the target bytes alone; the reproducing source requests `_memset`.

## Failed hypotheses and verifier controls

Exact one-axis commands and failures are retained in the probe table and JSON. Source-shape negatives under `BCC -c -mh -2 -n. UNIT.C` were:

- 00F5 as six separate word arguments: promotes the repeated middle arguments to SI/DI and changes its prologue. Grouping into three dwords reproduces the forwarding ABI.
- 00F5 using a separately assigned pointer followed by `if (p == 0)`: adds two reloads. Combining assignment and comparison reproduces the original. `if (!p)` instead avoids the huge-pointer comparison helper and is also wrong.
- 0AA9 spelling the final length expression as subtraction emits `sub ax,22h`; `+ (-34)` reproduces `add ax,FFDEh`. No dummy declarations or extra operations are used.
- 1768 using a positive compound guard gives long branch expansions. Separate early rejection of invalid conditions reproduces its short-branch fan-in.
- 11AD multiplying `(unsigned long)g_0238 * a` / `* b` reverses operand preparation and adds one byte at each site. `(unsigned long)a * g_0238` / `b` reproduces both.
- Declaring 1A8E as returning unsigned long adds DX clearing on zero-return paths. Returning unsigned reproduces the original while its internal accumulator stays 32-bit.
- Initial TLINK probe syntax `TLINK /m PROBE.OBJ PROBE.EXE PROBE.MAP` fails with inability to open probe.exe. Correct syntax is `TLINK /m PROBE.OBJ,PROBE.EXE,PROBE.MAP`.

`python build/workers/cmod/negative_checks.py` rejects all three controls with exit 1: changed C body, changed far-global binding, and removed function marker. Logs and `negative_checks.json` are retained under the worker directory. Re-run `python tools/cjudge.py` afterward to refresh the canonical build result.

## Remaining project integration

The C work is complete at the stated proof level. The initial three bytes remain UNKNOWN. The five-byte C/timer boundary correction needs a curated census update by its owner. Full natural linking, ownership of the remaining twelve DS-frame zero bytes, and packed-file equality remain project-level obligations. No shared metadata, executable evidence document, or other worker's files were changed.
