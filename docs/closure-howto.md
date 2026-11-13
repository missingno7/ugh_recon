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
python verif/ice_tool_probe.py
python verif/ice_smt.py
python verif/ice_evidence.py
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
outer iteration, with complete inner loops. This is useful coverage, not a useful
whole-contract proof. Under the document's conservative rule these compiled-C
checks are level C. `ice_smt.py` proves explicit bitvector/array models via a local
Z3 DLL; manual model-to-C correspondence remains a review obligation. Do not call
these models an automatically verified implementation. CBMC/KLEE acquisition was
blocked in this environment; exact probes are retained in `tool-probe.json`.

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

Receipts/results live under `build/native/` and `build/workers/pilot-ice/`; sources
and certificate stay in Git. Keep exact commands, bounds, times, tool hashes,
negative results and pending D scenarios in the certificate/report. A successful
lint does not promote evidence. The pilot proposes `migrated`; the supervisor owns
the final status and any decision to invest in a whole-C proof frontend.
