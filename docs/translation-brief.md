# Translation worker work order

Translate one assigned final-wave package from metadata/translation-plan.json into its
exclusive C/test files. Read AGENTS.md, docs/workers.md, docs/architecture.md,
the source contracts, relevant naming-worker REPORT.md and applied `note` lines
first. Read both callers and callees; source-line intervals do not bound shared
tails. Use c/ice.c and tests/ice.py as a working example. Do not edit src/, assets/,
the oracle lock, another package's files, existing tools or the common interfaces.
Propose exact shared-interface changes in your report for the supervisor.

The supervisor creates a separate Git worktree for each worker. Never share a
worktree/build directory or run simultaneous build/test commands in one worktree.
Workers write only their assigned C file and suite, plus build/workers/WORKER/.
They do not stage, commit, create worktrees or change Git state themselves.
Start from a clean checkout with `python tools/build.py`, then
`python tools/difftest.py`: no assets/ directory or original game file is needed.
The pinned historical toolchain and Python/Unicorn/native GCC still must exist.
Never run verify.py or oracle.py in a translation worker worktree. Those gates
belong to the supervisor with the original evidence. cbuild.py/difftest.py keep
their fixed build/ paths; worktree isolation is the parallel-build mechanism.

Use these code-proven details where older comments disagree: motion-script
header X/Y are pixels; InitializeDemoScripts shifts left five for X32/Y32.
TIMER installation initializes slot zero and handle maps, leaving other slot
storage stale. Removal copies callback pointers with undoubled slot offsets in
the interleaved table. The generated DGDATA annotations and two TIMER comments
await their canonical source/tool correction; preserve the observed behaviour.

## Starting and writing a routine

1. All eight remaining packages run concurrently in final wave 1. Order local
   dependencies internally, including indirect dispatcher/handler mutual families.
   Read callers, callees and tables even if the static direct graph has no edge.
   For another package's routine, use `ugh_dispatch(live_segment, offset, r)`
   through `ugh_adapters.h`; form the actual near/far frame at a CALL site, retain
   the incoming frame for a tail. Do not directly link an absent c_Label symbol.
   Unknown/untranslated targets return UGH_BAD_CALLBACK. Tests reaching such a
   boundary must record the exact edge as unverified; a pre-transfer comparison
   is a diagnostic, never composed acceptance. No emulator bridge is implemented.
   Do not replace a dependency with an Ignore/RET handler. Integration runs the
   actual callees and closes every recorded edge after all packages arrive.
2. Run `python tools/build.py` first, then `python tools/cgen.py --check`.
   Rebuilt map/listings supply symbols; never edit generated offsets. If the
   source receipt is stale, rerun build.py and report persistent drift. cbuild.py
   automatically refreshes the generated adapter interface and package headers
   from your implementations. Generated files are not maintained worker edits.
3. Write a contract: entry/return kind, register/flag inputs/outputs, segment flows,
   cdecl stack words if any, state/output ranges, call targets and device effects.
   Cite each unusual width, signed comparison, stale value and bug in a short
   comment. A mechanical name remains mechanical until code proves its meaning.
4. Add `/* TRANSLATES MODULE:Label */` immediately above
   `EXPORT int c_Label(Regs *r) { ... }`. If label spellings collide, export
   c_MODULE_Label and set Case.cfunc explicitly. The generator publishes
   prototypes in `c/ugh_adapters.h` and a package
   include header; do not maintain local declaration workarounds. Common files
   are supervisor-owned. Include `ugh.h` or `ugh_adapters.h` for peer calls.
   The marker is for
   coverage, not acceptance by itself. Record inline helpers separately in the
   report; do not mark them independently translated without their own adapter.
5. Keep all game lvalues in ugh_mem through rd8/rd16/rd32/wr8/wr16/wr32. Use G/S/D/T
   generated offset macros and generated segment macros. For other banks use
   UGH_O_MODULE_Name and UGH_S_MODULE_Name. A struct field displacement or length
   can be a literal if established by code; a labelled address cannot. Dynamic
   DS/ES comes from r, not from the data symbol's usual owner. No native pointer
   or C static/global may hold original game state or converted records.

Effective offsets and register operations wrap explicitly at the original byte/word
boundary. Bytes within one word/dword operand are contiguous across FFFFh;
rd16/rd16_linear/wr16/rd32/wr32 implement that distinction. Use
int16_t/int8_t only where signed x86 branches demand it. Preserve original carry
chains, logical-versus-arithmetic shifts, flags that survive INC/DEC/LOOP, zero
counts that execute a full loop, and equality-only sentinel tests. Widening a
temporary, clearing an old field, clipping an index, changing evaluation order,
or normalizing a malformed resource can change the game. Preserve original bugs.
Never restructure a routine into cleaner intended logic as part of translation.

Adapters receive the incoming CALL stack; far-cdecl argument zero is arg16(r,0).
They leave frame cleanup to the harness, and preserve SS/SP unless the original
contract intentionally changes them. DS/ES always flow back and are always
compared. Model SAVE/RESTORE exactly for registers callers consume. For a direct
translated call pass the same register model or explicitly map the documented
contract. A fallthrough/shared tail is one helper, not a copied approximation.
An indirect call/jump reads the original pointer/table and resolves its original
address; unknown targets return an error. Near RET under a far declaration is
an actual stack quirk, not permission to repair the oracle. Self-references use
generated original addresses. Callback arguments, return kind and stack support
belong at each actual call
site. `ugh_dispatch` resolves all implemented addresses; `ugh_call_near` supplies
the measured near return IP. IRET dispatch is separate from ordinary callbacks.

## Hardware boundary

Use platform.h for port transactions, physical VGA access and software interrupt
requests. The implemented fixture services and their capacities are listed in architecture.md.
An unsupported request fails. Do not return zero/default success, bypass a wait,
replace a drawing call with a no-op or mutate game state in a test-only device
hook to make equality appear. Specify the narrow missing service with inputs,
outputs, timing, state and ordered-log semantics, implement its independent
Python and C models with known-answer checks through the supervisor, then add
the routine cases. Tests must not perform real DOS file writes or exit processes.

Timer/retrace/input waits need the same finite deterministic service-point script
on both sides. No host wall time, background interrupt threads or sleeps. The
original timer/DMA/OPL algorithms belong in translated routines; platform services
model only the hardware interactions. A C version of assembly is behavioural
evidence and never adds to exact ASM/C reconstruction totals.

## Tests and commands

tests/PACKAGE.py defines CASES, a list of difftest.Case objects. setup(m) writes
static state or data obtained from our rebuilt image. `m.address('MODULE:Name')`
returns live segment/offset; m.off/m.seg extract one component; m.rb/rw/wb/ww
address a named cell with an optional byte delta. m.read/write address fixture
buffers. Setup must not run the oracle to manufacture expected state.

Case.regs is a dict or a function of m; Case.args is a tuple of far-cdecl words
or a function of m. Specify `kind='far'` or `kind='iret'` when appropriate (default
near). Set required DS/ES explicitly; unspecified registers are poisoned in the
poison run. `out_regs` lists every output/preserved register/defined flag promised
by the contract. CS/DS/ES/SS/SP are mandatory automatically. `flags` provides initial
IF/DF; name required arithmetic input flags in `flag_inputs` to preserve their
values from `flags`; poison mode fills the remaining arithmetic flags. `ranges` lists additional
output buffers as (live segment, offset, length), checked even if in stack
scratch. All non-stack RAM and VGA/device logs are compared regardless of ranges.
`check(m,result)` may assert an independent expected value against the original
result, e.g. ICE's independent decoder. Budget exhaustion is a failure to resolve,
not a reason to remove a case. Do not mask unexplained differences.

Cases should cover every identified branch, real built data, zero/max/sign/wrap
edges, stale storage, aliases and overlap, errors and flag paths. Use fixed seeds
for any randomized cases. Avoid huge collections of redundant examples. Full
instruction coverage is a diagnostic, not proof that values/contracts are complete.
The pilot demonstrates full RAM comparison plus 32-bit clock and DF poison cases.

Run serially (shared build outputs must not be mutated concurrently):

```
python tools/build.py                # once first, and after exact-source changes
python tools/cbuild.py
python tools/difftest.py PACKAGE
python tools/difftest.py PACKAGE --poison
python tests/_platform_kat.py          # if device semantics are touched
python tools/difftest.py --coverage    # integration owner, all accepted suites
python tools/coverage.py
```

A routine is done when its readable memory-model implementation, complete
documented contract and edge/real-data tests pass normal and poison comparisons;
all differences are explained without masks; at least three different deliberate
C mutations in its package are caught by assertions/comparisons; and any remaining
unexecuted/unsupported paths are named. Restore mutations in finally blocks and
rerun the restored suite. Inline-only, translated-untested and platform-boundary
entries are separate statuses. Never mark a whole package complete from a few
passing paths. The supervisor runs verify.py, asmverify.py and cjudge.py at integration.
Changing src/ or running verify.py/oracle.py is outside a translation worker's
ownership. A passing bounded body does not close an unavailable native call edge.

## Report

Write build/workers/WORKER/REPORT.md, with STATUS, exact files written, routine
addresses and status (directly tested / inline / unresolved), contracts, branch
and value coverage, oracle instruction counts/missing paths, hardware/DOS effects,
quirks retained, mutations and their first differences, exact commands and exits,
and unresolved assumptions or dependencies. Include exact proposed text for any
shared-file changes. Do not commit, stage or alter Git state. Final response is
at most 15 lines, starts `STATUS: done | partial | blocked | failed`, and gives the
result, verification evidence, blockers and suggested next step.
