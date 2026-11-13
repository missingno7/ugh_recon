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

## Falling items: slot transitions and capacity

`native/items.h` keeps twelve records, a flight/landed handler enum, and the
original sprite activity marker. The motion/lifetime cell remains one field:
landing replaces it, and retirement leaves it stale. Rendering continues to own
its erase and pixel caches. Only the bridge publishes sprite/position words.
The full-pool native result is explicit. Its bridge exposes saved-BX as the
pending CS:IP continuation with `UGH_CONTROL_TRANSFER`; the real return frame
remains pending. The known RET-only saved target can continue normally. This
refines L1's `BAD_CALLBACK` diagnosis of an unresolved target without repairing
the original stack defect.

Run from a clean checkout:

```
python verif/items_evidence.py enumerate
python verif/items_evidence.py spawn --timeout 60
python verif/items_evidence.py flight --platforms 10 --timeout 90
python verif/items_evidence.py land --timeout 30
python verif/items_evidence.py collect --timeout 60
python verif/items_evidence.py dispatch-selection --timeout 90
python verif/items_evidence.py flight --negative --timeout 30
python verif/items_mutants.py
python verif/items_capacity.py
python verif/items_integration.py --whole --local-reference
python verif/items_scenario.py author
python verif/items_scenario.py verify
python verif/items_scenario.py author --kind timer
python verif/items_scenario.py verify --kind timer
python tools/closure.py
python verif/items_host.py
```

The relational harness compiles the maintained L1 routines, native module,
contact implementation and actual bridge together. Every slot word and shared
benefit is compared, plus complete registers/flags and abnormal continuation.
Its normalized RAM retains the adjacent platform-array alias at the eleventh
left word / first right word. Descriptors, data, stack and device apertures are
otherwise separate and stable. Callback words have their complete established
target set. Direct-operation proofs normalize the selected slot to zero; the
same disjoint array indexing applies to all twelve identities. Dispatch-selection
proves the actual dispatchers with observing no-op callbacks, recording every
visited index. Each real handler's state effects are separately proved. Full
mixed-handler dispatcher CBMC timed out; finite composition enumeration and
whole-game evidence are reported separately.

`items_capacity.py` derives a B envelope over all 150 shipped order entries.
The stone energy identity is an integer model linked by static writer review,
not a proof on the stone C. Actual native free flight is enumerated for 829,722
initial Y/velocity pairs; its maximum 125 updates plus 560 landed updates is
below the deliberately conservative 700-update window. Itinerary animation/
countdown lower bounds and tree cooldowns give at most twelve items including
the impending spawn, hence at most eleven occupied slots before allocation.
These assumptions are explicit in the receipt and certificate. Arbitrary
injected item states can fill the pool and retain the abnormal continuation.

The existing fourteen scenarios reach only inactive item dispatch. The worker's
two additional input-only scenarios exercise a quick-delivery multiplier and a
tree timer pickup, each compared at every boundary with L0. Their exact text
stays under `build/workers/close-items/` for supervisor addition to tests. Lives
descriptor ordinal nine has no shipped spawn source; a truthful shipped-game
scenario cannot collect it. Its numeric transition has actual-C proof and
exhaustive byte-add enumeration instead.

The isolated builder avoids changing historically source-locked shared tooling.
`items_host.py` invokes the real host builder with a read-only selection overlay
for the proposed migrated unit and suppresses regeneration of protected L1
files. It then runs the unchanged `host/check.py --variant native`. Certificate
promotion remains the supervisor's decision.

## Hazard transitions and the native host review

`hazards.h` defines the five-slot record once. Its animation inputs are immutable
first/next windows sampled at the incoming cursor; the native step owns cursor
advancement, reset, state transitions and shared-state effects. The flight-side
selector and reward-list ordinal preserve future resource selection. An ordered
semantic store journal supports the temporary full-register bridge. The bridge
consumes those native values, checks the write owner/index/order, and retains
instruction expressions solely for register/flag reconstruction. It does not
run a shadow L1 state machine and overwrite its result afterwards. The returned
audio handle remains an explicit external service result.

Reproduce from maintained files (generated sources/receipts stay under the worker):

```
python verif/hazards_inventory.py
python verif/hazards_evidence.py generated
python verif/hazards_evidence.py UpdateBirdFlight --timeout 120
python verif/hazards_evidence.py UpdateTriopterusCharge --semantic --timeout 120
python verif/hazards_evidence.py dispatcher --timeout 30
python verif/hazards_evidence.py dispatcher --negative --timeout 30
python verif/hazards_mutants.py
python verif/hazards_integration.py --whole --local-reference
python verif/hazards_scenario.py
python verif/hazards_host.py
```

`python verif/hazards_reproduce.py` runs that chain and every standard entry
profile, then the real repository-wide closure gate. `--skip-proofs` reruns the
finite/C/D evidence. A pre-existing unrelated stale certificate still makes
the final gate fail; the runner never bypasses or relocks it.

Each exported entry except the dispatcher has its own proof profile, selected
by its original routine name. Default `--stones 1` includes actual independent
L1 contacts and actual native contacts. `--stones 16` attempts full composition;
timeouts earn no proof. `--contracts --stones 16` instead gives the caller a
relational contact contract: any shared selected index/miss, with equality of
the full query arguments asserted. This is conditional B evidence for the actual
caller C, not a proof of sixteen-entry contact selection. The contacts unit's
separate evidence still determines that link's strength. `--semantic` checks
the entire resulting slot/shared state and requests, plus store count, while
omitting ordered journal-value comparison; the ordinary profile checks both.
Safety and unwinding assertions remain enabled in every profile.

`hazards_host.py` copies maintained source and the checked plain reference into
an isolated scratch tree, sets only its hazard certificate to `migrated`, then
runs the real `python tools/hostbuild.py` and
`python host/check.py --variant native` there. It changes neither host selection
nor generation functions. It includes all sixteen maintained scenarios and the
additional input-only Dino witness in `verif/hazards_dino.txt`, plus the checker’s
256-frame smoke. A scratch host pass does not promote the maintained certificate.

## ADLX interpreters and borrowed channel records

Effects ADLX uses the accepted main voice API and a borrowed effect record.
Run `adlx_effects_proofs.py` for the logical caller contract, the three
`adlx_effects_timer_scalar.py` modes for timer output/frame/dependence, and the
compiled corpus/integration/host runners for real driver/C-stop composition.
Physical channel 9 instrument stamps saved voice 0 owner before loader rejection.
Never publish a cached audio snapshot after C stop/restoration returns.

Where a whole-handler proof times out, split it as the effects closure did:
separate output, frame (everything else unchanged) and dependence (no other
input matters) properties over the actual code, each its own CBMC profile. A
timeout earns nothing; a set of split properties that together cover the
handler's whole observable state is B.

## Passenger branch stages and matching cuts

`delivery_reproduce.py --fresh` reproduces the passenger waiting/delivery unit.
`delivery_proofs.py` runs output, byte-frame and input-dependence profiles for
literal L1 spans and the actual native branch helpers. It also proves the real
projection predicate and journal/dispatch/completion helpers. `--resume` reuses
only PASS receipts whose recorded inputs still match. The clean-checkout path
does not require saved worker receipts. `--record-stop` records open pieces
without proposing migration.

The composition inventory is `delivery_coverage.py`: it removes each literal
proved span from all six updating bodies, checks the small remaining SI/DI
setup, both display selectors, the full shell adaptation and the exact native
branch order. Tick, animation, contact and multiplication seams assert all
input arguments equal and allow arbitrary shared outputs; independent actual-C
helper theorems discharge these assumptions. The animation theorem admits any
registered nonempty vector and any live/sentinel cursor, rather than only the
small vectors used by the compiled corpus. Journal append is proved at an
arbitrary prefix length, so the zero-prefix stage proofs can be concatenated.
Dependence profiles observe an arbitrary appended position through that proved
append lemma; they retain every append argument/count without duplicating two
symbolically updated full journal arrays. Output profiles use the actual append
implementation. Native frame profiles hide its owned journal-cell writes using
the actual append frame theorem, retaining the exact count and bound. The
inventory also checks that native callers never read the hidden journal payload.

Output alone is insufficient: compare the typed working slot/world at the
matching cut, after that operation's journal and before its immediate tail or
service. A parent's working snapshot is not the callee's poststate. Frame
checks cover every other native/resource/history byte and an arbitrary RAM
byte, including other physical slots and the HUD high byte. Dependence varies
inactive aliases and retained renderer histories independently. Active alias
reads must still obey the existing phase table; do not widen it to fit a proof.
`delivery_frame_full.py` additionally varies every slot field outside the
declared read/retained-output inputs. This proves frame preservation for a
phase-agnostic shared helper at every phase value, rather than only at one seed
phase. Native and RAM byte-frame obligations are separate solver profiles.
Selected craft, next requests, pending finish, item/audio requests and abnormal
completion are observable outputs, even if the retained machine shell could
otherwise hide a private native defect.

`delivery_limits.py` enforces two solver permits across this worker's CLIs,
a hard 8 GiB private-memory job cap (CBMC plus child solver) and at most600 s.
Every non-PASS result is archived with the generated C, preprocessed input and
log. Timeouts, caps and source changes are negative results, never proof. A
successful caller theorem with abstract child effects remains conditional on
the contacts/items/audio owners' contracts; the compiled differential and
scratch native-host runs exercise the actual children.
