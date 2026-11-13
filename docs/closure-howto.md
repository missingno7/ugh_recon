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
