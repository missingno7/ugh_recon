# Registry and world-gate usage

A new world adds its own native/bridge files and certificate, a metadata/worlds/<component>.json
entry, and a small case module. Use an existing entry for the callback signatures. The entry
filename must match component. Membership must stay fixed after cold import; aliases share
lanes. A storage_owner can delegate an allocation (audio delegates to timing).

Declare every new source/helper in native.files, verification_inputs, or the registry's optional
files list. gate.cases names a Python file with a docstring followed by literal SPEC. Its legacy
key names the case-operator module (new modules need not be historical). Declare API groups,
case selectors/admitted rejections and defect IDs there. Operators provide their unique
router/proof/borrower cases; the framework supplies scheduling, fixtures, bounds and receipts.
Optional result_files maps historical result names. scenario-flag defects declare id, flag,
scenario, frames and either an expected diagnostic exit or a difference from its reference.

```
python verif/world_gate.py <component> --jobs 3 --out build/workers/<worker>/gate
python verif/world_gate.py <component> --finalize --locks --out build/workers/<worker>/gate
python tools/gate.py --jobs 3 --out build/gate
python tools/hostbuild.py --out build/custom-host
python host/check.py --variant native --out build/custom-host --receipt-dir build/custom-check
```

The world gate freezes committed HEAD plus admitted/declared overlays. Only its target gets
scratch promotion; the maintained certificate status stays unchanged. An unrelated unadmitted
world's in-progress files are excluded. Other modified dependencies remain checked inputs.
Generated source trees are reset, and prior success receipts are removed when a run starts.
Use separate output directories for simultaneous commands. The default pool is three; jobs=1
has identical semantic results. Each child owns an 8-GiB/600-second Job. Timing/commands/hashes
remain in diagnostics. The primary receipt omits scheduling metadata and keeps test outcomes.
Finalization refuses partial stage sets or changed source inputs.

Existing *_composition.py names forward to this driver. Unique historical case generators live
in world_cases/legacy_*.py; new workers do not copy their scheduling/build/finalization boilerplate.
A whole-gate wall may exceed 600 seconds; each individual child remains below that bound.
