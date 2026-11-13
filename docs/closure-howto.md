# Closing a native component

Read `modernization.md` and `workers.md` first. Keep L0 and L1 independent. Start
with the caller return sites and memory ownership, not a prettier translation.
Record what is observed, what can be removed, and which malformed/alias/wrap
states the boundary admits. The ICE certificate is a worked example, not a claim
that every component needs byte-window cursors.

Put the ordinary API in `native/<component>.h` and its code in `native/`. Put the
machine adapter only in `native/bridge/`. The ICE API is an in/out byte-buffer
function; the bridge preserves registers and flags outside that API. Small-buffer
errors are explicitly extensions, while complete windows retain the DOS wrap.

The reusable harness library is now `verif/closure_support.py` (about 100 lines).
It owns function extraction, checked C compilation, the pinned CBMC preprocessing
and process-tree timeout recipe, and receipts with source/tool/preprocessed hashes.
It contains no component algorithm. `ice_evidence.py` uses its compiler runner
and `ice_cbmc.py` uses its preprocessor runner and solver process owner;
the original ICE certificate and historical proof claims remain unchanged. Run a
fresh pilot reproduction in an isolated destination:

```
python verif/ice_evidence.py --out build/workers/close-small/pilot-ice
python verif/ice_cbmc.py --mode reader --stream 16 --output 8 --unwind 17 --timeout 30 --out build/workers/close-small/pilot-cbmc
```

For a small new unit, use `small_units.pair()` as the worked recipe: copy actual
L1 functions with `closure_support.function()` and rename their exported names,
include the maintained native C and optionally its bridge, then compile them
together. The extraction masks comments/strings when finding braces and fails
if a named function disappears. It does not translate instructions or substitute
a hand-written arithmetic model. The small-unit harnesses include the real
`c/ugh.h`; the ICE-specific `ugh.h` shim is not suitable for their other helpers.
Minimal system headers still come from `verif/cbmc_shim`. `-U_WIN32` suppresses
only the DLL export decoration during CBMC preprocessing. A RAM accessor shim
must state its exact footprint and alias assumptions.

```
python verif/small_units.py enumerate --mutants
python verif/small_units.py coordinate_scale --timeout 30
python verif/small_units.py far_copy --bound 1 --exact --timeout 30
python verif/small_units.py far_copy --bound 12 --exact --canonical --timeout 30
python verif/small_units.py far_copy --bound 20 --exact --canonical --timeout 30
python verif/small_units.py decimal --kind 0 --timeout 30
python verif/small_units.py decimal --kind 2 --canonical --timeout 60
python verif/small_units.py far_copy --bound 20 --exact --canonical --unwind 1 --negative --timeout 30
python verif/small_units.py decimal --kind 2 --canonical --unwind 1 --negative --timeout 30
python verif/small_integration.py --whole
python tools/closure.py
python verif/closure_kat.py
```

Here `--canonical` means disjoint fixed spans for the copy proof, and canonical
divisors/disjoint output for decimal. Those restrictions are B, even though the
bytes, direction and input values remain symbolic. The unrestricted overlap and
large-array CBMC profiles timed out; they have no proof claim. Enumeration covers
every 16-bit scaler input, all two/four-digit value inputs with canonical divisors,
all 65536 byte-value/ten-divisor pairs for the two-digit entry,
and every six-digit value 0..999999. These finite domains are A; the 168 copy
cases and the three defect controls are C. Do not describe the million-value
six-digit enumeration as covering arbitrary 32-bit inputs or mutable divisors.
The native API deliberately retains those broader quirks, whose general evidence
is C. The certificates record the distinctions and proposed statuses.

`nbuild.build(..., components=[...])` builds one combined bridged DLL. Shared L1
translation units are copied under `build/native/` and the selected reference
functions become `l1_*`; the original exported names belong to the bridges.
The maintained L1 files are never edited. Default selection remains ICE.
`small_integration.py` reuses the existing six routine suites and calls the actual
`wholegame.main()` with its `load_dll` binding supplied by the runner. It copies
cached references into its worker output directory and redirects `wholegame.OUT`.
Thus the full whole-game gate runs against the variant without changing its
source or tests. This is a Python API hook; the tool has no variant-DLL CLI option.
Failure tracing would need a separate instrumented-variant build hook.

New certificates can carry `verification_inputs`: SHA-256 hashes of maintained
L1/native/harness/tool inputs. `closure.py` rejects a changed input until evidence
is rerun and the certificate reviewed. This lock detects stale evidence, but does
not prove the assertions are sound. `verification_input_hashing: sha256-lf-text`
normalizes only CRLF to LF so Git's Windows checkout setting does not invalidate
text-source locks; generated build/proof receipts still hash the actual bytes.
Generated receipts are reproducible under
`build/workers/close-small/`; they need not be present for boundary lint on a clean
checkout. Certificate `status` remains the initial administrative `unanalyzed`;
`proposed_status` and its reason are for the supervisor's decision.

Run the pilot from the repository root (Python 3, pycparser, Unicorn/Capstone and
the existing MinGW installation are prerequisites):

```
python tools/nbuild.py native
python tools/nbuild.py bridge
python verif/ice_smt.py
python verif/ice_evidence.py
python verif/ice_cbmc.py --stream 16 --output 6 --unwind 17 --timeout 120 --tag final
python verif/ice_cbmc.py --stream 32 --output 4 --unwind 17 --timeout 120 --tag final
python verif/ice_cbmc.py --mode init --stream 16 --output 8 --unwind 17 --timeout 30 --tag final
python verif/ice_cbmc.py --mode step --stream 16 --output 8 --unwind 17 --timeout 120 --tag final
python verif/ice_cbmc.py --stream 16 --output 4 --unwind 17 --timeout 90 --tag reach --coverage
python verif/ice_cbmc_defects.py
python verif/ice_fuzz.py --count 3000 --mutants
python verif/ice_regressions.py
python verif/ice_integration.py
python tools/closure.py
python verif/closure_kat.py
```

`nbuild.build()` builds native, reference or bridge variants in `build/native/`
without calling `cgen` or touching `c/`. It substitutes just the migrated module,
records compiler/input hashes, and uses a process-specific DLL name. Extend its
small source selection when introducing the next component. The integration
runner loads that DLL and reuses the maintained test modules; its whole-program
report write is redirected to the worker directory. It never patches tests.

Use three independent views where available: L1 execution, native execution, and
an independent data generator/reference. `ice_fuzz.py` uses the exact Python
packer, deterministic random/structured inputs, real rebuilt resources, edge sizes
and single-bit mutations. It compares all output-window bytes and the L1 register
projection. The strict Python reference rejects some DOS-defined corrupt states;
record those rejections separately. Avoid running arbitrary malformed streams
unbounded: compare a stated prefix using generated guard-limited copies.

`ice_evidence.py` extracts the maintained L1 token statements verbatim and includes
both C implementations in one harness. Exhaustively cover small encoding spaces,
then use symbolic algebra or an inductive argument for dimensions that cannot be
enumerated. Its finite whole-decoder family covers 1,280 initial states and one
outer iteration, with complete inner loops. Exhaustive execution of every element
of an explicitly stated finite domain is A for that domain. Sampling remains C;
a proof of a guard-limited copy does not prove the production decoder. The token
encoding enumerations are A for the encodings and initial reader alignment they
actually cover. `ice_smt.py` uses the installed Python z3 from
`metadata/verif-tools.json`, with no scratch-DLL dependency. Its explicit models
remain proofs about models; they do not raise the C implementation's level.

`ice_cbmc.py` checks actual C with the supervisor's pinned CBMC 6.11.0. It needs
neither Unicorn nor the reconstructed executable. Its generated L1 copy changes
only the include spelling and adds a ghost iteration count. Both production loop
guards remain 2000000. Tables/macros come from L0 data and the generated L1 symbol
header, not from native constants. The memory shim supplies disjoint ordinary
buffers and immutable tables. Only L1's data accesses carry in-range assumptions;
native range errors on an admitted L1 execution fail the proof. Header bytes,
sentinel bits, literal bytes and output seeds are nondeterministic. Malformed
seeded references and header-as-payload encodings are admitted if their accesses
fit. A checked token-count assertion follows output progress rather than assuming
a token limit. Output storage is below 65536, so writes cannot wrap and continue
indefinitely within the admitted storage. This excludes general malformed
full-window behavior from the bounded whole proof.

On Windows CBMC defaults to an absent `cl.exe`, and MinGW system headers are not
parseable by this CBMC release. The reusable recipe is:

```
gcc -E -P -nostdinc -Iverif/cbmc_shim -Inative [bounds/defines] harness.c -o harness.i
cbmc harness.i --unwind N --unwindset [per-loop bounds] --unwinding-assertions \
  --bounds-check --pointer-check --signed-overflow-check --slice-formula --trace
```

The Python runner prints the result and records both exact command arrays, the
generated `.i` hash, input hashes, tool manifest and solver/decision times. Its
minimal `stdint.h`/`stddef.h` use Windows x64 widths. `ugh.h` models only the
decoder's register shell/accessors. Adjust these shims deliberately for the next
component; never use assumptions to paper over a difference in native code.
Per-loop unwinds avoid multiplying the outer bound by unnecessarily large literal
and bit-reading bounds. They remain assertions: `--unwind 1 --tag negative` must
fail, not silently truncate. Larger tested profiles timed out; see the report.

`--mode init` extracts the actual pre-loop prefixes and proves establishment of
the reader relation. `--mode step` extracts one actual outer iteration from each
implementation, tagging its terminal branch, and proves preservation of the
reader, buffers, environment and progress relation. Initial pending bits and
cursors are arbitrary, not just reachable from a particular compressed file.
Equal input/output bytes, equal cursor/sentinel state, no native error and immutable
tables are the relational invariant. In-range L1 accesses remain a contract
assumption for every step. Induction therefore covers arbitrary many such steps
in the stated buffer domain; it does not prove a file is well formed or extend
those buffers to 64 KiB. The header proof establishes the initial relation, and
the step's progress assertion supplies the finite bound. No handwritten decoder
model replaces either C body.

Modes `reader`, `bits`, `literal`, `length`, `offset` prove real helper code and
extracted L1 token statements from arbitrary reader state. Literal comparison
uses the DEC/JNS count lemma already proved by exhaustive compiled-C enumeration;
that dependency is explicit in the harness. `--coverage` is intentionally a set
of negated witness assertions: all four must fail with counterexamples proving
recognized magic, multiple iterations, seeded reads and malformed endpoints are
reachable. It keeps unwinding assertions enabled. CBMC's dedicated `--cover`
mode crashed on this case, so no proof relies on it. `windows_job.py` owns each
CBMC/solver process tree and kills it on timeout, avoiding orphaned solvers.

Seed defects in scratch copies and record which layer actually detects each one.
The ICE ordinary stream corpus misses a signed literal-count boundary caught by
the exhaustive token probes. `ice_regressions.py` then gives that finding a direct
three-way case. Keep the before/after distinction when evaluating the method.

Create `metadata/closure/<component>.json` with all fields in `modernization.md`.
The checker additionally requires a `dependencies` map keyed by every owned native
`.c`/`.h` file. Each entry declares sorted `includes` and `calls`, including static
helper calls and bridge calls. `python tools/closure.py --inventory` prints the
actual inventory for review. The checker validates required fields/statuses,
compares AST call inventories, bans L1 identifiers/headers outside bridges and
numeric code offsets declared in certificates, and rejects unowned native files.
It accepts a deliberately small C dialect with ordinary includes and types;
macro-generated control flow/complex new typedef requirements need a reviewed
checker extension. It is a boundary lint, not an alias analysis or proof engine.

Receipts/results live under `build/native/`, `build/workers/pilot-ice/` and the
second round's `build/workers/pilot-ice-2/`; sources
and certificate stay in Git. Keep exact commands, bounds, times, tool hashes,
negative results and pending D scenarios in the certificate/report. A successful
lint does not promote evidence. The second round proposes
`verified-under-assumptions` only for the explicit bounded/step domains; the
general full-window contract retains C evidence. The supervisor owns final status.

## Timer state and callback boundary

The timer worker adds `native/timer.h`, `native/timer.c` and its bridge. Slots
are records, while public handles retain their original even identities. The
handle map is deliberately not required to be a bijection: removal corrupts it.
`timer_remove_wrong_stride` retains the sequential, overlapping callback-word
copy through symbolic fragment provenance. Only the bridge binds fragments to
machine words. Mixed or externally supplied targets remain explicit OPEN cases.
Normal callers register a `TimerCallback` enum. The two fixture callbacks are
separately named and are not claims about game registration sites.

The bridge admits aligned active slots within capacity, with a selected handle
mapping to an active slot. Removing the last remaining slot, invalid/stale/odd
handles, overflow registration and unknown registration targets use the retained
L1 implementation. Passing those cases therefore verifies compatibility, not a
native proof for unchecked segment writes. Installation, restoration, saved BIOS
chaining, PIT/PIC I/O and stack adapters remain at the machine/platform boundary.
Native tick accounting and descending due consumption are separate phases;
the bridge reprojects after each callback, preserving callback mutations and its
original cursor. It does not precompute a callback list.

```
python verif/timer_evidence.py enumerate
python verif/timer_projection.py
python verif/timer_mutants.py
python verif/timer_evidence.py register --count 16 --symbolic --timeout 120
python verif/timer_evidence.py remove --count 16 --symbolic --timeout 120
python verif/timer_evidence.py set --count 16 --symbolic --timeout 90
python verif/timer_evidence.py tick --count 1 --timeout 90
python verif/timer_evidence.py tick --count 3 --timeout 90
python verif/timer_evidence.py tick --count 16 --timeout 150
python verif/timer_evidence.py tick --count 3 --negative --timeout 30
python verif/timer_integration.py --whole
python tools/closure.py
```

Symbolic API profiles admit any active count up to 16, any even in-range handle
with an active aligned mapping, arbitrary words (including corrupt other maps),
and arbitrary intervals/countdowns/due/target fragments. Registration additionally
requires capacity and a free handle at or below the new slot; its symbolic proof
uses the playback callback, with typed target projection checked separately.
Tick proofs admit arbitrary words at the stated fixed counts. These are actual-C
relational operation checks on an aligned, normalized timer-RAM shim, with safety
and unwind assertions enabled. They do not prove instruction-level asynchronous
interleavings. The variable-count tick profile timed out at 120 seconds and earns
no proof. The finite enumerations state their domains in the timer certificate.

`timer_build.py` uses `closure_support.compile_c` for an isolated combined DLL.
It copies and renames only the four selected L1 endpoints; original stack wrappers
dispatch to the bridged endpoints. Generated audit counters distinguish native
steps from L1 fallback. No existing builder/certificate is changed. The integration
runner gives `wholegame.main` a separate Windows loader reference because that
entry point unloads the DLL it receives; the runner retains its reference to read
the counters afterwards. All reports live under `build/workers/close-timer/`.

## Immutable level views and contact predicates

`native/level.h` and `native/geometry.h` are shared resource/geometry vocabulary,
authorized by the close-contacts work order. They describe borrowed immutable
inputs, not a new simulation state. Platform `destination_icon` is its established
HUD type word, not an invented terrain/material type. A surface consists of its
signed pixel bounds and aspect-converted Y. Input +E, complete packed level bytes,
actor placement tails and complete variable enemy placement bytes stay raw.
Unprojected descriptor callbacks and +3A/+3C remain in the original immutable
tables; the geometry projection reads only the four established words (two for
items, with literal three-pixel extents). No callback or actor state API is implied.

`level_bridge_project` resolves the record's encoded references, copies the chosen
320-byte tile map and builds a const view in caller-owned storage. It does not
replace `LoadCurrentLevelState`, decompress resources, initialize simulation state,
or change the loader's reverse-copy/alias behavior. Native helpers decode ordinary
resource bytes; segment arithmetic and descriptor identities stay in the bridge.
The projection contract requires ordinary stable RAM and accessible nonwrapping
level/list records; descriptor geometry alone retains operand-offset wrap and a
contiguous word spanning FFFF. Capacity/unknown-enemy failures leave the output view
unpublished, with partially filled storage permitted.

```
python verif/level_view_evidence.py --loader
python verif/level_view_evidence.py --prove
python verif/contacts_evidence.py enumerate
python verif/contacts_evidence.py enumerate --mutant
python verif/contacts_evidence.py enumerate --pairs --kind 0
python verif/contacts_evidence.py enumerate --pairs --kind 2
python verif/contacts_evidence.py enumerate --pairs --kind 2 --case 1
python verif/contacts_evidence.py enumerate --pairs --kind 3
python verif/contacts_evidence.py prove --kind 0 --bridge --timeout 45
python verif/contacts_evidence.py prove --kind 1 --bridge --timeout 45
python verif/contacts_evidence.py prove --kind 2 --bridge --timeout 45
python verif/contacts_evidence.py prove --kind 3 --count 2 --bridge --timeout 45
python verif/contacts_evidence.py prove --kind 2 --negative --timeout 30
python verif/contacts_integration.py --whole
python tools/amiga.py --out build/workers/close-contacts/amiga
python tools/closure.py
```

All generated files belong to `build/workers/close-contacts/`. The isolated builder
renames only L1 **definitions**, so calls in the same translation unit also enter
the bridges. It uses the shared compiler/receipt helpers without changing the
historically locked `nbuild.py` or `closure_support.py`. Audit counters separately
report native entry and the explicit corrupt/unterminated stone-list fallback.
The integration runner checks the actual whole-game entry point and retains its
own DLL loader reference while that entry point unloads its separate reference.
`contacts_reference.py` reads a checked fresh canonical plain build/expansion if
present. From a clean checkout it instead prepares both under this worker using
the pinned original tools, checks the plain image/relocation set/symbols against
the existing lock, and checks expansion/repack against the unchanged oracle lock.
It never calls `cgen.generate`. To exercise that path even with canonical caches:

```
python verif/contacts_reference.py --fresh
python verif/level_view_evidence.py --loader --local-reference
python verif/contacts_integration.py --whole --local-reference
```

On a missing whole-game reference cache, the maintained whole-game tool generates
the reference from the rebuilt plain L0 inside the isolated output directory.

Enumeration executes actual extracted L1 C and the maintained native C. The short
profile covers 2,752,544 cases: full word-coordinate slices in six geometry classes,
all player-count words, all stone vertical-step words and ordered stone slots.
Each `--pairs` profile additionally executes all 2^32 Cartesian coordinate pairs
with the remaining inputs fixed. Kind 0 is item, kind 2 is actor/enemy geometry,
kind 3 is one eligible stone; case 1 is the signed-wrap/reversed-bound class.
These are A only for the explicitly enumerated finite domains. The mutant changes
an inclusive horizontal edge to exclusive and must be detected with a changed hit.

CBMC uses the real `ugh.h` arithmetic, actual extracted L1 functions and actual
native/bridge code. Player profiles admit arbitrary geometry words, positions,
platforms, count and incoming flags, on a normalized read-only footprint. They
compare selection, scratch/platform results and the complete register/flag shell.
Stone count-two admits arbitrary eligible/ineligible descriptor/handler words,
coordinates and vertical steps. It is B for that list bound; it is not a full-pool
proof. Both count-16 profiles timed out (byte RAM 45 seconds; equivalent word RAM
with `--word-memory` and arrays-UF 120 seconds). They earn no proof. The negative
profile must fail the actual L1 `shl` unwinding assertion. Geometry arithmetic has
no assumed on-screen range, ordered-rectangle invariant, or canonical descriptors.

The bridge publishes DI byte identities and final TEST-DI flags. Actor platform
loading follows TEST and must not change SF even for platform FFFF. All four
geometric comparisons are signed and inclusive **after** word wrapping; reversed
signed intervals are empty. Only count exactly two retries player one. Contacts
read current X32/Y32, not pixel/render caches. Amiga h0:06D92 instead uses cached
sprite dimensions/origins and shifts position differences before comparing; its
inclusive BGT/SLE edges do not establish DOS geometric equivalence. Keep these
implementations distinct.
