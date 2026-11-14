# Test-only state projector

Run from the repository root with the usual rebuilt MZ/symbol inputs and cached whole-game
references available:

```
python verif/projector_evidence.py --all
python verif/projector/inventory.py
```

Every compiler, host and driver child is serial and has a 600-second / 8-GiB Windows Job limit.
The first run archives the accepted `8ecc728` checkpoint under
`build/workers/close-adlx-20/frozen`; later runs keep that pinned baseline. An explicit
`--revision COMMIT` can select another reviewed checkpoint for a fresh output tree; an
existing archive with a different revision is rejected rather than silently reused. Parallel
ICE/timer changes are excluded. The ordinary input sources are
never edited or rebuilt by a maintained tool. Copies of the native and literal hosts, the
relocated observation baseline, mappings, receipts and coverage tables stay in that worker
directory. `--build`, `--one NAME [--controls]` and `--summarize` are available for diagnosis.

`world.h` declares the candidate typed world and explicit service state. It contains no Regs
or historical addresses. `schema.py` binds supported fields to the historical layout only for
verification. Source words that cannot be decoded as registered identities stay explicitly
unresolved. Ambiguous overlapping views are unbound and journalled, not assigned a new owner.
The documented level-record/weather subfields are one canonical physical view, not two copies.
The schema's declared/bound array extents are not a theorem about arbitrary indexed aliases.

The C observer verifies an independently relocated rebuilt baseline **before** fixture setup,
then imports the actual cold fixture. Runtime scalar writes update typed fields; unclassified
writes update a last-write journal, with a write count/order hash. The explicit native decimal,
far-copy and ICE publication hooks cover writes that bypass the RAM accessor. VGA lane/latch
results and platform member changes are delivered through service-effect hooks. Ordered I/O
events are captured from log producers' arguments. Service effect snapshots are the current
producer's delivered values: this does not claim a new independent hardware implementation.

At every digest boundary, serialization uses only the independent baseline, typed fields,
identity registry, byte journal and service/effect state. It does **not** refresh them from
live RAM/device state. The verifier reads live RAM/devices/logs only on the comparison side.
It compares all observed RAM bytes with the original stack exclusion, the exposed return-word
identity, the device-prefix bytes, the error state and the cumulative ordered event list.
Equality of those serialized bytes implies equality of the existing host's digest inputs.
The cached reference records are read only by the Python checker after the child finishes.

The `gameplay` run temporarily corrupts a projected field, an older unclassified ICE-workspace
byte, the VGA write-lane mask, the event order and a registered actor identity mapping. Each
must produce a mismatch; restoring the test state must restore equality before the game
continues. The actual game RAM/devices are never corrupted. Identity codecs also round-trip
every 16-bit word in each of the six registry domains during cold import.

The scope is preservation of current observations, not independent game algorithms or a
production composition. Remaining model cells, codec workspace bytes, raw aliases, transient
ABI state and unsupported views can still be baseline/journal sourced. `COVERAGE.md` and
`schema.json` make the partial typed coverage explicit. The raw expressions/candidate writer
sets are retained by the static inventory command; its incompleteness flags remain false.
SDL queues, OPL synthesis internals and wall-clock state outside the historical observation
layout are not claimed as serialized state. No certificate or status is changed.

All 20 scenarios use their complete cached references. No stored 256-record smoke golden
exists: the smoke prefix uses the cached 96-record attract reference and all 256 records are
also compared with a fresh unmodified literal host built from the same frozen tree. No prior
worker receipt or expected record is used to construct the projected state.
