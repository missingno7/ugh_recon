# Static program model and semantic closure plan

The generated [program model](../metadata/program-model.json) covers all 284 curated
application entries: GAME 199, SOUND 52, original C 23, TIMER 10. It is a conservative
static model, not an equivalence certificate or an unrestricted points-to proof.
No game, original application program, emulator, or headless decompiler was run.
The existing build was read without rebuilding or modifying it. The byte-exact sources,
oracle lock, runtime libraries and other workers' files were unchanged.

Keep the Pack-Ice pilot already in progress. Replace the proposed **second closure unit**
with `GAME:CopyFarBytes`, then the decimal multi-entry group. Establish timer ownership
and its callback/stride contract before migrating its slot table. The two coordinate
scalers are worthwhile small exhaustive-proof exercises, with their scratch writes retained.

## Reproduction and queries

```
python tools/progmodel.py
python tools/progmodel.py --check
python tools/progmodel.py routine GAME:UnpackIceStream
python tools/progmodel.py site 013B:4C8C
python tools/progmodel.py site 0603C
python tools/progmodel.py var ActorUpdateOrScriptCursor
python tools/progmodel.py scc
python tools/progmodel.py candidates
python build/workers/model/check_model.py
```

The generator writes only `metadata/program-model.json`; queries only read it.
`--check` rebuilds in memory and compares the complete deterministic serialization.
Keys and set-derived lists are sorted; there are no timestamps or absolute workspace
paths. Receipts cover maintained sources, the relevant metadata and generator helpers,
the plain TLINK map and TASM listings. A stale source receipt/build or image/relocation
digest mismatch fails through `cgen.read_symbols`, rather than silently building.
Capstone 5.0.7 is required by this measured environment. A query does not itself run
the freshness check; run `--check` after source/build changes.

## Evaluation before implementation

* `tools/graph.py`: useful direct-call/port census and careful skipping of classified data.
  Its run found 284 entries and 67 indirect call/jump sites. It uses physical routine
  intervals and straight-line constants reset by calls/branches; its apparent ICE leaf
  write set misses the distant match tail. No CFG, target provenance, caller liveness,
  transitive effects or stack model. Retained the census and decoding approach, not its
  interval summaries as closure facts.
* `tools/where.py`: useful source navigation and original-byte disassembly. Reused its
  CBW/CWD mnemonic correction. Its source comments are navigation, while placement here
  is independently checked against build listings/map. Starting disassembly in the middle
  of an instruction is still the caller's error; discarded the first instructions of the
  exploratory `0878:1AF0` query and used the decoded function stream instead.
* `tools/symtab.py`: reused the curated 284-entry census, source definitions and permanent
  symbol identities. Its physical `end` is not assumed to be a reachable body boundary.
  The older naming brief's 286 count is stale relative to this census; no identities were
  added or removed by this work.
* `c/dispatch_table.inc`: 282 registered L1 entries at evaluation, including shared/control
  entries. It is an implementation resolver, not evidence that other L0 addresses cannot
  occur. Three inline ICE helpers are intentionally not independent exported adapters.
  Used to cross-check address coverage only; it is not an input dependency of the generator,
  so concurrent L1 work does not invalidate an L0 model.
* Capstone 5.0.7, 16-bit detail mode: decoded every byte in the supplied code spans and C
  instruction extents. Reused operand accesses, implicit register accesses and flag masks.
  Corrected its missing CF read for ADC/SBB/RCL/RCR/CMC and its unprefixed 98h/99h names;
  stack, PUSHF/POPF, string DF and zero-count shifts need explicit treatment. Regression
  checks cover these cases. This is not a formal proof of all decoder annotations.
* Ghidra 11.3.1 and 12.1: both local `support/analyzeHeadless.bat` installations were found;
  the 12.1 headless README was read. They can supply p-code and an independent CFG reading,
  but a fresh auto-analysis would still need the known segment contexts, data exclusions,
  shared-entry annotations and broken return conventions imported. Existing exact sources,
  build symbols and Capstone suffice for this census. No headless analysis or claim that
  either Ghidra version fails was made. A targeted p-code cross-check is recommended below.

## Computation and soundness boundary

### Instructions, extents and CFG

`cgen.read_symbols()` validates the plain build receipt, original image digest, relocation
site digest, TLINK public/contribution addresses and TASM symbol tables against names.json.
Instruction bytes then come from `build/link/plain/UGH.EXE`, never from L1 C. ASM decoding
uses `asm-map.json` code spans; C decoding uses each inventory `instruction_length`, excluding
its two switch tables. Source annotations map instructions to lines; generated prologue,
JUMPS expansion and padding locations use their physical owner's label line.

Per routine, traversal follows conditional/unconditional branches and normal continuations;
calls become edges rather than inlining callees. Reaching another curated entry by jump or
fallthrough creates a tail edge. Local tails beyond another routine's physical interval
are followed, which recovers ICE's `4D4B..4DDD` match body. `reachable_spans`, `cfg_sites`,
`shared_sites`, `calls`, `tails` and per-site `edges` make these choices inspectable.
Shared physical sites can belong to multiple entries. `physical_interval` is navigation only.

Code modification, aliasing into instruction bytes and arbitrary malformed transfers are
outside the decoded CFG assumption. Noninstruction targets and unknown transfers are
recorded as open exits, never pruned. Ordinary calls are shown with their syntactic next
instruction even for broken hooks; `abnormal_calls` states why that continuation is not
a valid normal-return edge. No claim is made that all syntactic sites are reachable from
startup. In particular, later DSP hook calls may be unreachable after the first corrupt return.

### Indirect provenance

Every non-immediate CALL/JMP is inventoried. Source-audited transfer shapes describe the
pointer origin and flow; target words are read afresh from the checked build. This is a
small program-specific resolver, not a generic memory SSA engine. Unrecognized new shapes
default to `dynamic` with UNKNOWN, rather than disappearing.

The actor dispatcher at `GAME:1492` has **36 distinct callback targets** under the descriptor
and initialization invariants. This is the useful interpretation of the roadmap's
"36-entry dispatcher": there is no separate 36-word CS jump table in this census. The
36 offsets arise from eight 74-byte passenger/stone descriptors, whose callback fields
feed the mutable `ActorUpdateOrScriptCursor` array. Demo mode uses that same array as data
cursors, so the mode invariant is essential. Enemy callbacks similarly come from four
60-byte descriptors. Item dispatch includes **both +06 and +0A**: spawning installs the
flight handler, landing installs the expiry/collection handler. Descriptor field families
are conservative upper sets; type/path correlations are not assumed proved. Zero target
words remain visible, including `GAME:0000` in enemy-family supersets.

Demo callbacks come from all 28 script headers reached through the four terminated vectors
at DGROUP `1020/1792/1E40/24DE`. Their +6 word flows through `0B21 -> 0B24 -> 0A15`;
the three targets are `0989`, `099F`, `1C0E`. The water table is three words at GAME `2DB3`.
The two SOUND dispatches mask a zero-extended byte into 16 bounded even indices; their
16-word tables each contain nine unique destinations. C `12C6` uses a seven-key bounded
search and C `1B1B` a compare against 7 before doubling BX. These four table sites have
complete target sets within the global no-code/table-corruption assumption.

Timer `0145` is deliberately only partially resolved. Slot zero is `TIMER:0099`; the two
application registrations materialize `SOUND:12E5` and `SOUND:1939`. The public register and
stack APIs also accept a caller-supplied far pointer. Worse, removal at `025C..0268` copies
callback words using undoubled slot offsets into an interleaved far-pointer table, so even
a closed list of registrations does not prove a closed list of pairs after compaction.
The saved INT08 vector at `009B` is external: INT21/3508 -> ES:BX -> DGROUP `7B72/7B74`.
STI/PUSHF/CALL FAR expects an IRET handler and consumes that extra FLAGS word.

`pointer_provenance` retains source OFFSET materializations, candidate pointer stores with
load-site tokens, and all descriptor callback words. Each site has its own flow, invariants,
targets and classification, with load/base provenance and relevant store sites. This
does not prove that every indexed/wide aliasing store has been found. Invariant-resolved
means exactly that: without its listed bounds/initialization/type assumptions, add UNKNOWN.

### Registers, flags and caller observations

Reads and writes use AL/AH etc. as independent atoms; SI/DI/BP/SP and segment registers are
whole words, and each tracked flag is separate. Zeroing XOR/SUB is not an input read.
Variable/zero-count shifts cannot kill incoming values. Undefined flags are possible
writes, not promised deterministic values. Instruction implicit stack/DF effects are added.

A fixed point computes may-input and may-write summaries over calls and tails. Local CFG
intersection supplies definitions guaranteed on every path; a call kills a live input only
when the callee defines it on every returning path. A second backward fixed point propagates
known caller-continuation demand into callee return sites. Every call site stores both
`callee_written_live_after` and `callee_changed_live_after`; the first includes save/restore
writes, while the second subtracts symbolic preservation. Routine outputs union observations
over known callers. Saving an incoming register on the stack is a mechanical input read;
it is not automatically a semantic parameter.

Symbolic register/stack propagation proves some identity preservation and tracks PUSHF/POPF.
These results assume ordinary returning callees and no writes aliasing into saved stack
words. Callee outputs and memory-derived values without a summary remain unknown. Byte
preservation is less precise than input liveness: an unknown write to AH can lose a symbolic
AX identity even when AL actually survives. No path feasibility or minimal semantic output
proof is implied by a may set.

**No routine has an unrestricted complete register/output interface in this model.** Unknown
timer pairs, external entry and saved-BX/mismatched return paths can add callers or observers;
the conservative `complete` and `all_callers_known` flags therefore remain false for all 284.
This is not a claim that every routine is normally called indirectly. It prevents an absence
in the known graph being used to delete a register. The 200 `input_complete` entries have
no transitive unresolved transfer/external service dependency in the analyzed returning
graph; the flag is weaker than unrestricted completeness. Exact semantic elimination still
needs a reviewed component contract restricting these open behaviours.

### Segments, memory and effects

An abstract CFG interpreter carries bounded sets of integer constants, relocation-typed
`frame:XXXX` values, incoming-register identities and opaque load/far-pointer tokens.
Joins union up to 12 alternatives, then widen to UNKNOWN. Relocated immediates are tagged
using the MZ relocation sites: `frame:0000` is the runtime frame; absolute `0000` is not.
Hardware `A000` is an absolute VGA segment, not a load-relative program frame. Calls use
symbolic callee exit summaries; known caller contexts refine segment parameters, while
root/unknown contexts remain unknown. Unknown dominates a join. CS is fixed per decoded
module; SS-relative accesses are explicitly distinguished.

Every explicit memory operand except LEA has its segment expressions/value set, addressing
registers, displacement, operand width, read/write mode and symbols where supported. Missing
operand access annotations are conservatively RW. Implicit stack operations, PUSHA/POPA and
interrupt frames are also recorded. REP/indexed extent is explicitly unbounded by this
domain. Far loads retain their load-site identity. For absolute named pointer cells,
`far_loads` records the initial built offset and relocation-typed/absolute segment under an
explicit unchanged-segment-word invariant. Memory accesses reference this conditional
evidence separately; it never silently turns mutable data into a constant. Thus water's
`far@013B:2DE4` points to initial `DrawPagePointer` segment `absolute:A000`, and ICE's
`far@013B:4C87` to initial `IceScratchPointer` segment `frame:0A67`.

Exact known frame/displacement pairs resolve through names.json; data-layout objects annotate
constant locations. A nearby name is explicitly marked "nearest label"; indexed displacement
names are base hints, not exact cells or bounded arrays. Source variable spellings are
stored separately as `source_offset_hints` when the segment is unproved. Their writer/reader
index is conditional, and does not make a DS displacement a DGROUP access by itself.

Direct effect sets collect memory, stack, ports, interrupt numbers and known DOS/BIOS AH
values. Transitive union closes over every known direct/resolved-indirect/tail edge.
Unknown transfer, library, external interrupt, indexed range and unresolved segment/alias
effects remain explicit. VGA is definite for known A000; an unresolved far pointer may
alias VGA and is marked possible. Port values flow only when the constant domain supports
them; DX unknown is retained. These are unordered may-effect sets; they do not prove device
ordering, atomicity, memory non-aliasing, races, DOS error behaviour or final written values.
The eight called runtime entries have separate linked-byte diagnostic summaries, including
RETF 8 cleanup for division at `0000:039D`; runtime memory/device effects remain external.
No runtime source was replaced or reclassified as application reconstruction.

### Stack and structure

The symbolic interpreter tracks relative SP, saved values, ENTER/LEAVE, caller argument
cleanup and TASM's PUSH CS / CALL NEAR implementation of a same-segment far call. Unknown
or inconsistent SP joins widen. The three water-frame entries consume a saved DS word
(+2 before their near return); their enclosing caller supplies it, so they are tail ABIs,
not three broken ordinary functions. `SpawnFallingItem`'s exhausted-pool RET at `2BE3`
instead pops its saved input BX as IP and leaves the real return word. All four `001C..001F`
hooks execute near RET despite far callers. Each mismatch records the actual callee-CS
landing and retained caller-CS word. `delta_before_return` excludes the return-address pop;
"balanced" assumes compatible returning callees and save-area non-aliasing.

Tarjan SCCs include known calls, tails and resolved indirect destinations. They are a
conditional/lower-bound graph: unknown edges can enlarge SCCs. Both nontrivial SCCs have
eight routines: each SOUND ADLX event-fetch routine and its seven looping opcode handlers.
Wait handlers return out of the interpreter, so they are dependencies outside those SCCs.
Writer hyperedges group routines by shared written symbol, retaining the symbol that causes
coupling. This is preferable to merging every writer-connected routine into one giant unit.
Far/indexed aliases and initialization writes can add writers; ownership is a proposal.

## Measured completeness

| Measure | Result |
|---|---|
| Application routines | 284 |
| Decoded instruction sites | 12694 |
| Indirect CALL/JMP | 67: 4 F, 61 I, 1 P, 1 E; 0 unclassified |
| Return sites | 251 |
| Far-call/near-return syntactic sites | 26 |
| Interfaces present / unrestricted complete | 284 / 0 |
| Input summaries without open transfer/service dependencies | 200 |
| Effect summaries present / without unresolved ranges | 284 / 29 |
| Memory operand/implicit stack records | 5878 |
| Records with unknown/parameter/opaque segment | 3283 |
| Stack summaries | {'balanced': 245, 'unbalanced': 3, 'unresolved': 36} |
| SCCs | 270: sizes 8, 8, then 268 singletons |
| Variable reader/writer candidates | 392 |
| Writer hyperedge clusters | 148 |
| Exhaustive proposed components | 20 |

The 188 decoded sites outside any entry traversal are 185 NOPs and three unreachable direct
jump remnants, not omitted device/memory instructions. All remain in the site map. Fourteen
entries have shared reachable physical sites. An absent named write is not proof that a
state cell is unobserved: e.g. bulk initialization through the workspace pointer can touch
the coordinate scratch without a direct symbol reference.

## Indirect-site inventory

All addresses are module frame:offset. F = fully resolved within the global table/code
integrity assumption; I = complete word-set under listed invariants; P = partial plus
UNKNOWN; E = external. Counts are distinct target words, including null/noninstruction
values. The JSON/site query carries the full target set, provenance and exact invariants.

| Site | Instruction | Class | Targets | Origin |
|---|---|---|---:|---|
| `013B:0A15` | `call word ptr [bx + 0x2c2d]` | I | 3 | 28 motion-script header callback words (+6), four demo vectors |
| `013B:1492` | `call word ptr [bx + 0x2a0d]` | I | 36 | actor descriptor callback words, copied into DGROUP:2A0D parallel array |
| `013B:14DB` | `jmp ax` | I | 1 | actor descriptors +2C near code words |
| `013B:1537` | `jmp word ptr [si + 0xc]` | I | 3 | actor descriptors +0C near code words |
| `013B:15AC` | `jmp word ptr [si + 0x10]` | I | 3 | actor descriptors +10 near code words |
| `013B:1614` | `jmp word ptr [si + 8]` | I | 3 | actor descriptors +08 near code words |
| `013B:16CD` | `jmp word ptr [si + 8]` | I | 3 | actor descriptors +08 near code words |
| `013B:16E9` | `jmp word ptr [si + 0x14]` | I | 2 | actor descriptors +14 near code words |
| `013B:1763` | `jmp word ptr [si + 8]` | I | 3 | actor descriptors +08 near code words |
| `013B:177D` | `jmp word ptr [si + 8]` | I | 3 | actor descriptors +08 near code words |
| `013B:17A4` | `jmp word ptr [si + 0x18]` | I | 2 | actor descriptors +18 near code words |
| `013B:17E2` | `jmp word ptr [si + 0x1c]` | I | 2 | actor descriptors +1C near code words |
| `013B:1843` | `jmp word ptr [si + 8]` | I | 3 | actor descriptors +08 near code words |
| `013B:185D` | `jmp word ptr [si + 8]` | I | 3 | actor descriptors +08 near code words |
| `013B:18B8` | `jmp word ptr [si + 0x14]` | I | 2 | actor descriptors +14 near code words |
| `013B:18C4` | `jmp word ptr [si + 0x10]` | I | 3 | actor descriptors +10 near code words |
| `013B:191F` | `jmp word ptr [si + 8]` | I | 3 | actor descriptors +08 near code words |
| `013B:1939` | `jmp word ptr [si + 8]` | I | 3 | actor descriptors +08 near code words |
| `013B:1954` | `jmp word ptr [si + 0x18]` | I | 2 | actor descriptors +18 near code words |
| `013B:1986` | `jmp word ptr [si + 0x20]` | I | 3 | actor descriptors +20 near code words |
| `013B:1A7A` | `jmp word ptr [si + 0x24]` | I | 3 | actor descriptors +24 near code words |
| `013B:1AEB` | `call word ptr [si + 4]` | I | 1 | item descriptors +04 near code words |
| `013B:1BBA` | `jmp word ptr [si + 0x28]` | I | 2 | actor descriptors +28 near code words |
| `013B:1C0A` | `jmp word ptr [si + 8]` | I | 3 | actor descriptors +08 near code words |
| `013B:1C3E` | `jmp word ptr [si + 0x20]` | I | 3 | actor descriptors +20 near code words |
| `013B:1C7D` | `jmp word ptr [si + 0x24]` | I | 3 | actor descriptors +24 near code words |
| `013B:1D9F` | `jmp word ptr [si + 0x10]` | I | 3 | actor descriptors +10 near code words |
| `013B:1E98` | `jmp word ptr [si + 0x10]` | I | 3 | actor descriptors +10 near code words |
| `013B:1FD2` | `jmp word ptr [si + 0x14]` | I | 2 | actor descriptors +14 near code words |
| `013B:1FDE` | `jmp word ptr [si + 0xc]` | I | 3 | actor descriptors +0C near code words |
| `013B:2026` | `jmp word ptr [si + 0x18]` | I | 2 | actor descriptors +18 near code words |
| `013B:2064` | `jmp word ptr [si + 0x1c]` | I | 2 | actor descriptors +1C near code words |
| `013B:20BD` | `jmp word ptr [si + 0xc]` | I | 3 | actor descriptors +0C near code words |
| `013B:2109` | `jmp word ptr [si + 0x18]` | I | 2 | actor descriptors +18 near code words |
| `013B:213B` | `jmp word ptr [si + 0x20]` | I | 3 | actor descriptors +20 near code words |
| `013B:236F` | `call word ptr [bx + 0x2cf3]` | I | 31 | enemy descriptor callback words, copied into DGROUP:2CF3 parallel array |
| `013B:23AC` | `jmp word ptr [si + 0xc]` | I | 4 | enemy descriptors +0C near code words |
| `013B:23E6` | `jmp word ptr [si + 0x10]` | I | 4 | enemy descriptors +10 near code words |
| `013B:24B2` | `jmp word ptr [si + 8]` | I | 4 | enemy descriptors +08 near code words |
| `013B:2500` | `jmp word ptr [si + 0x1c]` | I | 4 | enemy descriptors +1C near code words |
| `013B:257A` | `jmp word ptr [si + 8]` | I | 4 | enemy descriptors +08 near code words |
| `013B:2645` | `jmp word ptr [si + 0xc]` | I | 4 | enemy descriptors +0C near code words |
| `013B:2663` | `jmp word ptr [si + 0x1c]` | I | 4 | enemy descriptors +1C near code words |
| `013B:268E` | `jmp word ptr [si + 0x10]` | I | 4 | enemy descriptors +10 near code words |
| `013B:26D9` | `jmp word ptr [si + 0x1c]` | I | 4 | enemy descriptors +1C near code words |
| `013B:26F4` | `jmp word ptr [si + 8]` | I | 4 | enemy descriptors +08 near code words |
| `013B:2794` | `jmp word ptr [si + 0x1c]` | I | 4 | enemy descriptors +1C near code words |
| `013B:27AF` | `jmp word ptr [si + 0x14]` | I | 2 | enemy descriptors +14 near code words |
| `013B:282C` | `jmp word ptr [si + 0x18]` | I | 2 | enemy descriptors +18 near code words |
| `013B:2872` | `jmp word ptr [si + 8]` | I | 4 | enemy descriptors +08 near code words |
| `013B:288B` | `jmp word ptr [si + 0x1c]` | I | 4 | enemy descriptors +1C near code words |
| `013B:28D1` | `jmp word ptr [si + 8]` | I | 4 | enemy descriptors +08 near code words |
| `013B:28EA` | `jmp word ptr [si + 0x1c]` | I | 4 | enemy descriptors +1C near code words |
| `013B:2921` | `jmp word ptr [si + 8]` | I | 4 | enemy descriptors +08 near code words |
| `013B:2A4F` | `jmp word ptr [si + 0x1c]` | I | 4 | enemy descriptors +1C near code words |
| `013B:2A83` | `jmp word ptr [si + 0x10]` | I | 4 | enemy descriptors +10 near code words |
| `013B:2B08` | `jmp word ptr [si + 0x1c]` | I | 4 | enemy descriptors +1C near code words |
| `013B:2B3A` | `call word ptr [si + 4]` | I | 1 | item descriptors +04 near code words |
| `013B:2B8C` | `call word ptr [bx + 0x2d83]` | I | 2 | item descriptor callback words, copied into DGROUP:2D83 parallel array |
| `013B:2C8E` | `jmp word ptr [si + 8]` | I | 1 | item descriptors +08 near code words |
| `013B:2DFE` | `jmp word ptr cs:[si + 0x2db3]` | I | 3 | CS:2DB3 three near words |
| `0664:15E5` | `jmp word ptr cs:[bx]` | F | 9 | CS:174B sixteen near words |
| `0664:177D` | `jmp word ptr cs:[bx]` | F | 9 | CS:1919 sixteen near words |
| `0878:12C6` | `jmp word ptr cs:[bx + 0xe]` | F | 7 | compiler switch table CS:1483, 7 words |
| `0878:1B1B` | `jmp word ptr cs:[bx + 0x1b95]` | F | 8 | compiler switch table CS:1B95, 8 words |
| `0A32:009B` | `lcall [0x7b72]` | E | 0 | INT21 AX=3508 returns ES:BX; stored at DGROUP:7B72/7B74 |
| `0A32:0145` | `lcall [si + 0x7b2e]` | P | 3 | timer far-pointer array; public AX:DX callback input; installed slot zero |


Return instructions are additionally inventoried at all 251 sites (168 RET, 75 RETF,
eight IRET). Ordinary returns are `under_invariants` with open stack-derived destinations;
the four hook RETs and `2BE3` are explicitly dynamic. These are separate from the 67
non-immediate CALL/JMP instructions above. No stack transfer is silently counted as a
successful normal callback. The interrupt-return sites are:

| IRET site | Owner |
|---|---|
| `013B:45FA` | GAME:HandleKeyboardScanInterrupt |
| `013B:4E5A` | GAME:FailDosCriticalError |
| `0664:1192` | SOUND:BeginSoundDelayMeasurement |
| `0664:11B4` | SOUND:FinishSoundDelayMeasurement |
| `0664:1E15` | SOUND:HandleSampleDmaInterrupt |
| `0664:1E7C` | SOUND:HandleSampleDmaInterrupt |
| `0664:1EFF` | SOUND:HandleDspProbeInterrupt |
| `0A32:01A9` | TIMER:HandleTimerInterrupt |

The 26 syntactic far-call/near-return mismatches are:

| Far CALL site | Near RET entry | Actual landing |
|---|---|---|
| `0664:1F14` | `013B:001F` | `013B:1F19` |
| `0664:1F19` | `013B:001F` | `013B:1F1E` |
| `0664:1F43` | `013B:001F` | `013B:1F48` |
| `0664:1F48` | `013B:001F` | `013B:1F4D` |
| `0664:1F78` | `013B:001F` | `013B:1F7D` |
| `0664:1F7D` | `013B:001F` | `013B:1F82` |
| `0664:1F9A` | `013B:001F` | `013B:1F9F` |
| `0664:1F9F` | `013B:001F` | `013B:1FA4` |
| `0664:1FB4` | `013B:001F` | `013B:1FB9` |
| `0664:1FB9` | `013B:001F` | `013B:1FBE` |
| `0664:200A` | `013B:001F` | `013B:200F` |
| `0664:200F` | `013B:001F` | `013B:2014` |
| `0664:2021` | `013B:001F` | `013B:2026` |
| `0664:2026` | `013B:001F` | `013B:202B` |
| `0664:20C0` | `013B:001F` | `013B:20C5` |
| `0664:20C5` | `013B:001F` | `013B:20CA` |
| `0664:20E2` | `013B:001F` | `013B:20E7` |
| `0664:20E7` | `013B:001F` | `013B:20EC` |
| `0664:20F9` | `013B:001F` | `013B:20FE` |
| `0664:20FE` | `013B:001F` | `013B:2103` |
| `0664:2108` | `013B:001F` | `013B:210D` |
| `0664:210D` | `013B:001F` | `013B:2112` |
| `0878:0045` | `013B:001F` | `013B:004A` |
| `0878:004A` | `013B:001E` | `013B:004F` |
| `0878:0111` | `013B:001D` | `013B:0116` |
| `0878:014D` | `013B:001C` | `013B:0152` |

## Proposed replacement for the roadmap decomposition

The following exhaustive 20-way partition replaces file/language-based ownership. Its
membership and measured interfaces are also in JSON `components`; entries are assigned
exactly once. Counts are routines, not native API functions. Source-offset writer groups
are evidence for an owner proposal, not proof of exclusive physical-memory ownership.

| Component | Entries | Owns / shared views | Calls in | Calls out / capability interface |
|---|---:|---|---|---|
| `audio` | 75 | C/SOUND shared records, OPL/sample state, clocks/guard/fade | GAME sound facade and TIMER callbacks | timer, far copy, four hooks, runtime and hardware |
| `contacts` | 4 | no persistent owner; borrowed geometry/platform views | passenger, hazards, items | none in known graph |
| `demo` | 13 | mode view of actor arrays, scripts/counters, reveal pointer | front end | render/HUD, video, audio, passenger no-op |
| `external_hooks` | 4 | no service state established | C/SOUND far calls | corrupt-return landing; no invented success API |
| `falling_items` | 5 | 12-slot descriptor/flight/landed state | passenger/tree spawn; sequencing dispatch | contacts; shared timer/lives/multiplier benefits |
| `far_copy` | 1 | no persistent state; borrowed source/destination byte ranges | four original-C routines | none; ordered memory and caller DF |
| `front_end` | 23 | menu/password/score/edit state and record persistence | sequencing | demo, text/render, pictures, audio, level, DOS/input |
| `hazards` | 31 | 5-slot bird/dinosaur/other/tree state | sequencing; level initializes | contacts, falling items, audio; enemy null targets remain open |
| `ice` | 5 | no shared mutable global; borrowed input/output and CS tables | pictures and level/map loading | internal bit helpers only |
| `input` | 8 | scan/keyboard matcher, controls, joystick calibration | front end, sequencing | DOS/BIOS, IRQ/PIC/ports; tests and polling |
| `level_loader` | 2 | producer of level/map/platform and object initial state | front end, sequencing | ICE, numeric and initial behaviour entries |
| `numeric` | 7 | separate digit buffers/divisors, coordinate scratch, CS RNG state | front end, loader, HUD | no known application callees; DOS-time seeding external |
| `passenger_stone` | 37 | gameplay view of 16-slot actors, itineraries and carry state | dispatch and level initialization | contacts, falling items, audio; platform/player views |
| `pictures` | 3 | borrowed decoded image plus palette destination | startup/front end | ICE, video upload, palette/retrace/input |
| `player_physics` | 2 | two-player control/position/velocity/impact state | sequencing | VGA collision reads and shared fade state |
| `render_hud` | 19 | draw/erase caches, page scratch, HUD projection | front end, demos, sequencing | numeric, sprite/palette/page services |
| `sequencing` | 6 | game phase and initialization ordering | startup/runtime | front end, level, simulation, rendering, input, audio/video |
| `timer` | 10 | DGROUP 7A4C..7B7C and CS installation flag | audio scheduling/stack API; INT08 | audio callbacks and external saved vector; PIT/PIC/DOS |
| `video_dos` | 20 | VGA pages/palette and retrace/critical-error services | render/HUD, pictures, front end, sequencing | VGA/BIOS/DOS capability boundary; input polling |
| `water_weather` | 9 | water phase/height and 193-slot rain arrays | sequencing; level initializes | render background restore, VGA state and RNG |


State/interface decisions that matter more than the partition count:

* Audio owns the common C/SOUND storage together, including the 42-byte records, record-12
  aliases, displaced AdLib voices, clocks, guards and sample/DMA state. Treat AdLib and PCM
  drivers as subordinate capabilities. Splitting "original C" from "SOUND driver" would cut
  through the same storage. TIMER invokes audio callbacks; audio registers/removes/changes
  TIMER slots. This callback cycle is an interface boundary even though it is not one of
  the two immediate-call SCCs.
* Passenger/stone state and demo state share DGROUP `29AD..2CAD` by mode/lifetime. Propose
  one supervisor-owned storage projection with mutually exclusive views, rather than two
  independent copies. The loader initializes these arrays; rendering reads and writes their
  erase/draw caches. Descriptor pointer, update handler and bytecode cursor are distinct
  logical roles even where the original reuses one word.
* Hazards own the five-slot behaviour state `2CAD..2D6B`, including the fruit tree/reward
  source. Falling items own `2D6B..2E8B`, where horizontal speed becomes landed lifetime.
  They exchange spawn/collect events and player/level benefits. Keep the full-pool nonlocal
  return as an explicit retained precondition/failure obligation; do not invent an ordinary
  allocation-failure result.
* Level data/resources are immutable inputs; `LoadCurrentLevelState` is a producer of
  multiple components' initial state. It must not become the permanent owner of every
  array it initializes. Its future interface produces the level/map/platform and initial
  object views, with the original ordering and skipped/reserved fields preserved.
* Contact routines take views of player/object/platform geometry, not a dependency on the
  full game machine. Player motion still samples planar VGA pixels, so rendering/collision
  interpretation must be established before replacing it with tile-only collision logic.
* Keep water/weather update and draw adapters under one temporary boundary: water advancement
  restores background through rendering, and rain update uses water/VGA offsets. Separate
  simulation events from pixel operations only after their ordering is verified.
* `numeric` is an analysis grouping, not a proposal for one state struct. Decimal buffers,
  coordinate scratch and RNG state have separate contracts and closure steps. Similarly
  `video_dos` and `front_end` can split further after their outgoing boundaries are closed.

The measured `calls_in`/`calls_out` lists are the precise incoming/outgoing routine interfaces;
`written_only_here` and `shared_written_state` list the current state evidence. Sources of
additional coupling are the explicit unresolved effect lists. A component may be split only
when its shared state/lifetime contract is preserved; a call-graph leaf alone is insufficient.

## Ranking and order of semantic closure

Scores are reviewed judgments, each 1..5 with higher better. C = low coupling, B = behaviour
confidence, V = verification tractability, M = removable machine machinery, A = architectural
value, T = reuse of technique. Totals are a comparison aid, not a dependency schedule.

| Unit | C | B | V | M | A | T | Total / 30 |
|---|---:|---:|---:|---:|---:|---:|---:|
| `far_copy` | 5 | 5 | 4 | 4 | 4 | 5 | 27 |
| `ice` | 5 | 5 | 4 | 5 | 3 | 5 | 27 |
| `decimal` | 4 | 4 | 4 | 4 | 3 | 4 | 23 |
| `timer_slots` | 2 | 4 | 2 | 5 | 5 | 5 | 23 |
| `coordinate_scale` | 4 | 5 | 5 | 2 | 2 | 4 | 22 |
| `demo` | 2 | 4 | 3 | 5 | 4 | 4 | 22 |
| `music_clock` | 3 | 4 | 3 | 3 | 3 | 3 | 19 |


**far_copy** (GAME:CopyFarBytes). C 5: one leaf; four original-C callers; no persistent owned state; B 5: 25 exact bytes; straight REP MOVSB and cdecl adaptation; V 4: finite count but DF, overlap, offset wrap and parameter/save-area aliases need explicit contract; M 4: far cdecl frame, segment registers, register saves and CX loop counter; A 4: used by event scan, voice allocation and state restoration; T 5: ordered buffer-copy/alias/bridge proof reused throughout rendering and audio.

**ice** (GAME:DecodeIceLiteralAndMatchStream, GAME:ReadIceBitToCarry, GAME:ReadIceBitsToDx, GAME:UnpackIceStream, GAME:UnpackIceToScratch). C 5: no shared mutable global outside output/stack; B 5: exact ASM plus independent codec and five asset round trips; V 4: bounded bit grammar and generated streams; arbitrary malformed streams not bounded; M 5: register bit buffer/DF/CS tables/backward segment machinery; A 3: unblocks all maps and pictures, no gameplay architecture ownership; T 5: first bit-precise buffer/alias/bridge technique.

**decimal** (GAME:EncodeFourDecimalDigits, GAME:EncodeSixDecimalDigits, GAME:EncodeTwoDecimalDigits). C 4: digit buffer and divisor state; shared tails must stay grouped; B 4: exact arithmetic visible; formatting quirks retained; V 4: finite ranges and buffer differential cases; M 4: DIV/register digits/segment offsets; A 3: HUD and high scores share formatting; T 4: shared-tail multi-entry contract technique.

**timer_slots** (TIMER:RegisterTimerCallback, TIMER:RemoveTimerCallback, TIMER:SetTimerCallbackInterval). C 2: ISR and sound callbacks share arrays; public callback API; B 4: exact stride defect is visible; behaviour must retain it; V 2: invalid handles/capacity and mixed far words complicate contract; M 5: seven arrays/far pointers/CLI/POPF/stack adapters; A 5: central scheduling and interrupt ownership; T 5: state projection and callback equivalence reusable.

**coordinate_scale** (GAME:ScaleLevelSpeedToThreeHalves, GAME:ScaleLevelYToThreeQuarters). C 4: two arithmetic leaves share CoordinateScaleScratch with level clearing; B 5: few exact instructions; V 5: exhaustive 16-bit domain feasible; scratch write observable unless proved dead; M 2: few registers/flags removed; A 2: narrow geometry utility; T 4: wrap/signed-rounding proof reusable.

**demo** (GAME:AdvanceDemoScripts, GAME:InitializeDemoScripts). C 2: aliases actor arrays and rendering caches; B 4: 28 script headers and finite callback set under initialization invariants; V 3: finite shipped scripts; malformed loops/slots need assumptions; M 5: bytecode pointers and register callbacks; A 4: typed cutscene interpreter; T 4: interpreter/state projection technique.

**music_clock** (C:DisableMusicSectionLoop, C:GetElapsedMusicTime, C:SwapDwordByteOrder). C 3: SOUND globals and C record-12 aliases; arithmetic runtime dependency; B 4: matched original C plus ASM callers; V 3: zero rate faults, 32-bit wrap, runtime division and ES output; M 3: far record loads and helper calls; A 3: sound state ownership valuable after table/API repair analysis; T 3: runtime and originally-C ABI techniques.



Recommended order, respecting current work and dependencies:

1. Finish the in-progress ICE pilot. The model supports its boundary and distant shared tail;
   its three application call boundaries observe DF and preserved ES, but discard returned
   SI/DI before use. The bridge still preserves live saved working registers. Facts were
   published early in [ice-facts.md](../build/workers/model/ice-facts.md). A valid buffer/stream,
   alias and termination contract is necessary; arbitrary malformed input is not a pure
   total decoder. Five original assets and an independent packer are strong finite evidence,
   not an all-input equivalence proof. It remains a good substantial pilot, not the only
   reasonable first unit.
2. Close `CopyFarBytes` next. It is only 25 exact bytes and has four original-C callers
   (start channel, scan events, restore voice allocation, apply scanned events). It obeys
   incoming DF and ordered byte overlap, uses only the low count word, ignores the high
   word, and wraps offsets. A normal `memcpy` substitution is not justified. CX=0 is a
   known caller-observed machine output, so its bridge must reproduce it. This is a stronger
   second unit than timer compaction for proving far-pointer/alias adaptation with little
   behavioural uncertainty. If starting a new pilot from scratch, it is the smallest
   competitive choice; do not interrupt the already useful ICE work to restart there.
3. Close the decimal group's three entries and shared tails together, before the HUD that
   consumes them. Establish digit buffer/divisor ownership and caller-observed flags rather
   than closing the physically adjacent entry intervals independently. Run the coordinate
   scalers as a small exhaustive 16-bit proof exercise, preserving their scratch output
   until read/alias liveness permits removing it.
4. Establish timer API bounds, handle/slot invariants, moved-slot and callback-pair semantics,
   ISR/foreground ordering and saved-vector contracts. Then close slots plus their stack
   adapters with typed callbacks only within the proved contract. Preserve the removal
   stride defect, or make its exclusion an explicit approved reachable-state assumption;
   a conventional correct compaction algorithm is not equivalent merely because it is nicer.
5. Close audio internal arithmetic/clocks after runtime and shared storage boundaries; close
   each ADLX interpreter SCC as a group with its wait exits and driver capabilities. Then
   demo scripts under a mode-specific actor-storage projection, resources/level projection,
   renderer/HUD services, contacts, and object state machines. Sequencing integration comes
   after those boundaries, with whole-scenario evidence, not in place of their contracts.

## Naming findings (proposals only)

* `Actor` is a storage-family term here, not proof of a universal entity class. The eight
  descriptors and routines distinguish passenger and stone behaviours, while demo mode
  overlays the same arrays with motion-script state. Prefer `PassengerStone...` for the
  gameplay view and `DemoMotion...` for the demo view once the shared owner is agreed.
  Do not rename every Actor symbol mechanically.
* `Enemy` includes the fruit tree/reward source as well as bird, dinosaur and the mechanically
  named Triopterus-related entries. `HazardOrRewardSource` is a more faithful component
  scope; retaining concrete per-species names is better than imposing hostility on the tree.
* `ActorUpdateOrScriptCursor` and `ActorOverlayOrScriptCallbacks` correctly expose unions of
  roles. A single generic native callback field would hide the cursor/pointer distinction.
* `FallingItemMotionOrLifetime` is a real phase-dependent union: landing writes 560 into the
  former horizontal step. Separate flight and landed views are supported, subject to stale
  unused fields remaining observable under the contract.
* Retain `TIMER:loc_032F`: it loads three arguments but calls removal, not the interval setter.
  A proposed name like `SetTimerIntervalFromStack` would be false. Retain the four hook names;
  their intended service/delay/resource meaning is not established by a one-byte RET.
* Treat "36-entry dispatcher" as the 36-target actor update interface under the stated
  invariants; do not create a new recovered 36-word table or infer a native class hierarchy.

## Prioritized infrastructure improvements

1. **Close the transfer frontier before deleting machine interfaces.** Add relational
   points-to/memory SSA for callback array stores and descriptor/index/mode correlations;
   preserve unknown joins. Model timer far-word pairs across the actual mis-strided copies,
   invalid handles and overflow. Add compatible-call-frame and saved-BX transfer edges to
   a separate unrestricted graph, rather than pretending the known SCCs are complete.
2. **Check the analyzer independently at narrow boundaries.** Add a version-pinned p-code or
   second decoder cross-check for implicit register/flag accesses, partial-register writes,
   REP count zero, PUSHF/POPF, far/near forms and runtime callee cleanup. The current static
   regressions catch concrete errors but do not prove Capstone annotations correct. Use
   bit-precise SMT/CBMC on the closure contract, not the may-analysis, for elimination claims.
3. **Improve memory/segment precision.** Track offset ranges and far pointers as paired values,
   including relocation origin, word-width overlap and physically contiguous word accesses
   across FFFF. Summarize immutable tables separately from mutable initial values. Introduce
   stack-parameter/alias contracts so preservation claims can become reviewed local proofs.
   The unchanged-pointer invariants in `far_loads` are the immediate frontier, not constants.
4. **Make verification consume the boundary facts.** Generate reviewed call-continuation
   observation cases and state projections from this model; explicitly distinguish preserved
   machine outputs from eliminable semantic ones. Check all ordinary call/tail forms, not
   only isolated routine success. Callback-state/IRQ schedules must cover reentrancy and
   ordering; an instruction/edge count is not race evidence. The existing L0/L1 differential
   harness remains independent and must not derive expected values from this JSON.
5. **Promote owned state without duplicating it.** Supervisor-owned shared projections for
   passenger/stone/demo lifetimes and C/SOUND aliases come before native structs. Extend
   closure dependency checks to the measured call and shared-write hyperedges, with an
   explicit reviewed escape for unresolved effects. Reject automatic "closed" status while
   the component frontier contains unbounded/unknown behaviours.

## Validation and limits of the deliverable

`python tools/progmodel.py --check` verifies reproducibility against the checked source/build
inputs. `python build/workers/model/check_model.py` checks the independent instruction
idioms, routine/site coverage, all indirect classes, the item handler transition, ICE's
noncontiguous extent and live CF/DF, timer flag preservation, library stack cleanup, SCCs,
and exact decomposition partition. Query smoke tests cover all five commands. A second
hash-seeded generation check guards accidental set-order nondeterminism. These commands
verify the model's consistency and concrete static facts, not semantic equivalence of a port.
No src/ edit was proposed, so the historical rebuild gates were not rerun against shared
build output. All remaining incompleteness above is retained in the machine-readable model;
this work grants no closure status and changes no inherited name.
