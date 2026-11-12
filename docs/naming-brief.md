# Region naming workers

You analyse one region of the byte-exact DOS Ugh! reconstruction. Write a proposal and a
report; the supervisor applies it. Read AGENTS.md, docs/workers.md, docs/executable.md,
docs/evidence.md, docs/link.md, docs/asm.md and docs/c-module.md first. Never execute the game.
Do not edit maintained source, metadata, tools or another worker's files. Your work order
assigns a region and scratch/report directory; proposals go in build/proposals/REGION.txt.

## Binding naming rule

A thing gets a name only when the code shows what it is. Otherwise retain its mechanical
name and explain what prevents a sound interpretation. A hunch goes in a `note`, never in a
name. Names are modern reconstructions, not claims about original source spelling.

Use CamelCase verb phrases for routines (`WaitVerticalRetrace`, `RestoreTimerInterrupt`)
and CamelCase nouns for data (`PreviousTimerVector`). Prefer purpose to instruction
sequences, but do not hide observable hardware effects. Name important loops/exits only
where they improve understanding. Avoid broad names such as `UpdateGame` unless the code
actually establishes that scope. Do not change instructions to make a proposed name fit.

For every routine in the assigned region, propose a justified name and a contract, or keep
the mechanical name and say why in the report. Cover table/vector/callback entries and the
unreferenced seeds too. Check both callers and callees before claiming an ABI. Shared tails,
fallthrough and indirect calls can make the physical source interval larger or smaller than
the reachable body. Do not infer reachability from a pattern seed alone.

## Coordinates, source and identities

All command-line numbers are hexadecimal unless stated otherwise. Coordinates are relative
to the unrelocated original load image, not a live DOS segment. Source object offsets begin
at zero; frame-relative addresses include the contribution displacement:

| Module | Frame | Frame-relative extent, end exclusive | Maintained source |
|---|---|---|---|
| GAME | 013B | 0008..529C | src/asm/GAME.ASM |
| SOUND | 0664 | 000C..2143 | src/asm/SOUND.ASM |
| C | 0878 | 0003..1BA5 | src/c/module.c |
| TIMER | 0A32 | 0006..0341 | src/asm/TIMER.ASM |
| DGROUP | 5C09 | data labels/EQU offsets | src/data/DGDATA.ASM and ASM EQU declarations |
| C initialized globals | 1A37 | 0000..0004 | src/c/module.c |

GAME/SOUND/TIMER are assembly-origin. The C module is matched as C, huge model, BCC 3.0
`-mh -2`. Most C far globals bind to SOUND frame 0664, not DGROUP. DS/ES can change within
a routine; a displacement alone does not establish the accessed segment. Far-data banks
are separate src/data modules. Their labels do not by themselves establish their contents.

metadata/names.json is the single symbol ledger. Its immutable dictionary keys combine
original frame:offset, scope and mechanical spelling; values contain the current name,
kind, one line of evidence and all associated source spellings. Local labels and public C
interface aliases at the same address share an identity where that relationship is known.
Distinct storage-boundary labels can remain separate identities at the same address.
DGROUP EQUs repeated in several assembly files share one identity. Keys survive renaming;
use a full key when an already-renamed mechanical spelling is needed unambiguously.
Stack argument names, C local variables, field/type names and assembler segment names are
outside this address-based ledger. `_main`, contribution anchors and `*_BASE` names have
fixed linker/generator roles and are refused as semantic naming targets.

`loc_00E4` and other offsets occur in more than one module. Use `GAME:loc_00E4` or
`TIMER:loc_00E4`, even when a shorter spelling currently happens to be unique. C definitions
can be qualified `C:fn_0003`; C-facing assembly declarations can be supplied in their C
spelling (`fn_0664_205C`) or their ASM spelling (`_fn_0664_205C`). The tool renames the local
entry, C identifier, decorated public and EXTRNs together. Do not manually add underscores.

The tool accepts ASCII letters followed by letters/digits/underscores, rejects collisions
case-insensitively across maintained source, and rejects the union of TASM/C keywords,
registers and instructions. It also rejects leading underscores as implementation-reserved
new names. Limits were measured with the pinned tools (scratch evidence in
build/workers/naming-infra/length-probes.json): BCC distinguishes 32 source characters;
TASM distinguishes internal identifiers through 255 but exports only 63; TLINK correctly
reads PUBLIC names through 63. Longer TLINK names can corrupt a map even with exit 0.
The common tool limit is therefore 63 characters for assembly-only names and 32 for anything
with a C spelling. The compiler-generated underscore is accounted for separately.

## Exploration commands

```text
python tools/where.py 013B:0020 --disasm 16
python tools/where.py cs:112B --module SOUND --disasm 12
python tools/where.py SOUND:ClearSoundState
python tools/where.py C:fn_0003 --disasm 12
python tools/where.py ds:7B72
python tools/where.py 08783
python tools/graph.py SOUND:ClearSoundState --tree 2
python tools/graph.py C:fn_0003
python tools/graph.py ds:7B72
```

where.py prints module, source file/line, nearest current label and any displacement, then
optionally disassembles N instructions from the **locked original**. A bare number is image
linear, `frame:offset` is explicit, `ds:` is DGROUP, and `cs:` requires `--module`. The original
16-bit CBW/CWD opcodes print correctly despite Capstone's CWDE/CDQ naming bug. Disassembling
data is a diagnostic and does not classify it as code. Data EQUs can point to a declaration
of the offset rather than the storage itself.
Inside an ASM routine, instruction annotations refine the source line; C addresses resolve
to the current function definition. Exact entry queries show the label's definition line.

graph.py reports direct callers/callees, cross-module edges, constant ports, interrupts/AH,
memory offsets read/written and source data symbols. With a data argument it reports the
referencing routines. `--tree N` bounds the direct callee tree and marks cycles. It reads
original code only inside classified code spans, excluding compiler tables. It conservatively
tracks straight-line register constants, resetting at branch targets, calls and interrupts.
`DS?:`/`ES?:` means the segment is unknown; an indexed displacement is a base, not an exact
cell. Known index constants give an initial effective offset, not the full REP/loop extent.
Source `ds_XXXX` references are listed as symbolic DGROUP offsets, not proof of the
current DS. Indirect edges, register-based accesses and side effects through callees are
incomplete. An absent edge or access is never evidence of absence.

metadata/naming-regions.json partitions the 286 current call/seed routine entries exactly
once: GAME 201, SOUND 52, TIMER 10, C 23. Branch-only targets are local labels, not separate
routines. Regions keep nearby source intervals, favouring cuts with fewer direct call edges.
Data labels are assigned to their heaviest referencing region (ties are deterministic).
GAME regions have roughly 800..2000 routine source lines. SOUND is one region; TIMER and C
are whole smaller modules. Declarations and shared resident data can lie outside the counted
routine intervals. Read every listed data label needed by the routines too.

The supervisor can run `python tools/symtab.py --check` to check identities and the exact
routine partition. `--regions` regenerates the partition from current sources and static
calls; do this only between worker batches because assignment boundaries can change.
`--init` creates a missing name ledger and refuses to overwrite one. Never regenerate an
existing ledger: that would discard the permanent mechanical identities.

## Contracts

Write only what helps a C translator preserve behavior. Use at most 100 columns per line:

```text
; Purpose in one or two lines, with the evidence-bearing scope.
; In: registers, stack arguments, flags and shared state consumed; units/ranges if known.
; Out: results, flags and state changes, including failure paths.
; Clobbers/preserves: only unusual effects or preservation relied upon by callers.
; Effects/quirks: DOS, BIOS, hardware, interrupt context, shared tails, nonlocal exits,
; 16-bit wraps, signedness, equality-only limits, stale fields or wrong-segment accesses.
```

Omit empty headings and per-instruction narration. Do not promise a register survives merely
because it is not written along the one path inspected. For C, retain the recovered types,
evaluation order, explicit unsigned arithmetic and far/huge-pointer semantics. Behavioral C
translations of assembly never count as exact ASM or exact C source matches.

## Proposal format

Directives are case-sensitive. Blank lines and `#` lines outside blocks are ignored.

* `rename OLD NEW`: whole-token rename with the interface and metadata semantics above.
  Multiple renames are simultaneous. Collision swaps/chains into existing tokens are refused.
* `comment LABEL`: one or more lines starting with `;`, ending at a **blank line** or EOF.
  No `end` directive. Managed contract blocks above the label are replaced. C blocks are
  converted to C comments before the `@frame:offset` marker, preserving judge adjacency.
* `data LABEL byte|word|dword|string [count]`: retype an entire consecutive literal DB run
  immediately at/after a physical ASM data label. Count is the number of output elements
  (string bytes for `string`) and must equal the run's extent. The run must equal the original,
  contain no relocation, and be independently classified data if inside ASM. No code,
  symbolic SEG/OFFSET, uninitialized bytes, partial runs or EQU views are accepted. Strings
  must be printable ASCII without apostrophes; zero terminators need a separate labelled run.
  This is a declaration change, not an ownership/classification assertion. A worker may
  propose such a change, but does not edit src/data; respect concurrent data-worker ownership.
* `note text...`: one report-only line. It never changes source. Put uncertainties here.

Comments/data can refer to old or newly proposed names. Stable ledger keys also work. All
entries are validated before any write; errors carry proposal line numbers and reject the
whole file. Gate failure restores every maintained file in the transaction. Outputs from a
failed build remain diagnostic scratch; a fresh successful gate refreshes them.

Complete small example (an additional proposal, **not already applied**):

```text
# The word flag is tested and written by both observed timer lifecycle routines.
rename TIMER:byte_0006 TimerInterruptInstalled

comment TIMER:byte_0006
; CS word flag gating installation and restoration of the INT 08h dispatcher.
; In/Out: zero means inactive; installation writes one and restoration writes zero.

data TIMER:byte_data_0006 word 1
note TIMER:00D2 dispatches callbacks indirectly; do not infer all callback contracts here.
```

Supervisor commands:

```text
python tools/apply.py build/proposals/REGION.txt --dry
python tools/apply.py build/proposals/REGION.txt
python tools/symtab.py --check
```

apply.py runs asmverify.py, cjudge.py and verify.py after the transaction. Logs, notes and
touched-file lists go to build/workers/naming-infra/apply/REGION/. For a direct rename use
`python tools/rename.py OLD NEW --check`, or `--file pairs.txt` containing `OLD NEW` per line
(`#` comments allowed). Direct writes also run the three gates by default; `--dry` only
validates. Both tools report every touched file. Run only one applying supervisor at a time.
Workers can explore concurrently; do not run builds/mutations against shared outputs in
parallel. Never edit build/link fragments or LAYOUT.ASM: fragment.py regenerates them.

The locked packed file is the proof: verify.py must report FULL_PACKED_FILE. The plain
build still differs in exactly 35 relocation-table positions by design; its image/relocation
set is diagnostic. Do not relock the oracle or change the curated region census. No code DB
blobs, INCBIN, output patching, library rewrites or expected bytes from a candidate.

The original Amiga game under assets/amiga/ can supply semantic leads about game behavior,
formats or terminology. It proves nothing about DOS instructions, addresses, ABI, toolchain,
or matching bytes. Verify any proposed DOS name against DOS code; leave an Amiga-only hunch
as a note. Assets are immutable oracle evidence. Work on copies under build/ only.

## Worker report

Follow docs/workers.md: build/workers/WORKER/REPORT.md, final answer at most 15 lines starting
`STATUS: done | partial | blocked | failed`. List routines covered and those deliberately
left mechanical, evidence for names, hardware/DOS effects, original quirks and translation
uncertainties. Give commands and results for verified claims, exact options for rejected
hypotheses, and findings outside your region. Proposals are review material until the
supervisor applies them and the complete proof passes.
