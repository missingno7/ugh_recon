# Modernization by semantic closure

How the literal C translation becomes readable, native C without losing the game's behaviour.
This document is the method and the acceptance rules; `docs/roadmap.md` is the living plan and
inventory. Guiding sequence: understand, bound, prove what matters, replace, verify, close.

## Layers

```
L0  src/        byte-exact TASM + Borland C reconstruction   (proof: tools/verify.py)
L1  c/          literal C on the original machine model       (evidence vs L0: tools/difftest.py)
L2  native/     modern C: typed state, normal functions       (evidence vs L1: per component, below)
```

- L0 is historical evidence. Its rules (AGENTS.md) are unchanged; modernization never edits it
  except through the naming tools for comment and name corrections.
- L1 stays as the independent behavioural reference. It is not modernized in place. It changes
  only to fix a proven divergence from L0, and every such fix gets a direct case.
- L2 is where readable code lives. It is built separately from L1.

Evidence is a chain and is reported per link. ASM-to-L1 evidence is differential (routine
cases, whole-game scenarios). L1-to-L2 evidence is whatever the component's certificate
states (levels A to D below). A proof between L1 and L2 says nothing about L0 by itself; the
composite claim is only as strong as its weaker link, and certificates state both links.

## Rules for native/

Ordinary L2 code (everything outside `native/bridge/`) must not use:

- the register model (`Regs`, register fields, flag helpers), segment registers or `seg:off`
  addresses, `ugh_mem` and the `rd*/wr*` accessors, `ugh_sym.h`, original code addresses, the
  dispatch table, return-address or stack-layout tricks.

It uses normal parameters and return values, named types for game state, enums for states,
typed function pointers or direct calls for control flow. Original integer behaviour that
matters (16-bit wrap, signedness, stale fields, ordering, original bugs) is kept explicitly,
with a comment that names it as retained.

`native/bridge/` holds the adapters that let a migrated component run inside the L1 program
during migration: they read the component's inputs from the L1 machine state, call the L2
function, and write its effects back. Bridges are the only place that knows both models. A
bridge disappears when all callers of the component are native.

`tools/closure.py` checks these rules mechanically (forbidden identifiers outside bridges,
declared dependencies against actual includes and calls). A component cannot be closed while
the check fails.

## What a component must establish before it is replaced

For each routine or routine group, from static evidence first:

1. responsibilities;
2. inputs (registers, flags, memory, devices) and outputs, with value ranges where known;
3. complete read/write effects on memory and devices;
4. direct callees and the full target set of every indirect transfer it makes or receives;
5. what callers can observe afterwards: register and flag liveness at every return site,
   memory that is read later, ordering of device effects;
6. dependence on stack layout, segment arithmetic, aliasing and timing;
7. the semantic contract: inputs, outputs, effects, preconditions, retained quirks.

A machine-level detail is eliminated only when the evidence shows nothing observes it (for
example: a register that is dead at every call site, a flag no caller tests, a segment value
that is constant on every path). Otherwise it is retained and named in the contract.

## Evidence levels

| Level | Meaning | Typical tools |
|---|---|---|
| A | equivalence proved for all inputs satisfying the contract, bit-precise | SMT (z3), CBMC equivalence harness with unbounded or fully covering bounds |
| B | equivalence proved under stated assumptions: loop bounds, input sizes, invariants, reachable-state restrictions | bounded model checking, SMT with assumptions |
| C | differential testing: representative, generated and edge cases, traces | the L1 harness, generated inputs, fuzzing against L1 |
| D | whole-game scenarios agree on the observation model | tools/wholegame.py |

A certificate names the level reached for each property, with the exact command and its
result. Tests passing never yield more than C. A bounded proof is never described as
unrestricted.

## Observation model

L2 is compared with L1 on semantic observations at deterministic simulation boundaries, not on
every byte of the original memory. Per component the contract defines:

1. externally observable behaviour (returned values, events, device effects, frames);
2. persistent logical state that determines future behaviour (it must be preserved even when
   nothing shows it now);
3. machine state that may be abstracted away, with the evidence that nothing observes it.

The canonical projection of (2) is a function from the L1 memory image to typed L2 state; the
bridge implements it. Equivalence over time means: projection commutes with one step of the
component (L1 step then project equals project then L2 step) for every state the contract
admits. Lower-level comparison (raw memory, registers) stays available for diagnosis.

## Closure certificate

One file per component: `metadata/closure/<component>.json`, checked by `tools/closure.py`.

| Field | Content |
|---|---|
| `component` | short name |
| `status` | one of the statuses below |
| `original` | L0 identities (module:label, address) and L1 functions |
| `native` | L2 functions and files, public header |
| `purpose` | responsibilities in a few lines |
| `interface` | inputs, outputs, effects, preconditions |
| `callers`, `callees`, `indirect` | with the target set of every indirect site and its classification |
| `memory` | regions read and written, owners, aliases, layouts that matter |
| `assumptions` | invariants and environment assumptions relied on |
| `eliminated` | machine-level dependencies removed, each with its evidence |
| `retained` | machine-level semantics kept on purpose, each with its reason |
| `evidence` | per property: level, method, exact command, result, date |
| `amiga` | correspondence findings, if any, with their classification |
| `uncertainty` | what remains unknown |

Statuses, in order: `unanalyzed`, `analyzed`, `boundary-established`, `migrated`,
`verified-under-assumptions`, `verified-within-contract`, `integration-validated`, and
`blocked` (with reason). Only the supervisor sets a status. `verified-within-contract` needs
level A for the contract's properties; `verified-under-assumptions` needs level B;
`integration-validated` additionally needs level D for the scenarios that reach the component.

## Workflow

1. **Analysis** (read-only, may be delegated): fill the certificate fields from static
   evidence; status `analyzed`, then `boundary-established` when the interface and effects are
   complete and reviewed.
2. **Implementation**: L2 code and its bridge, nothing else; status `migrated`.
3. **Verification**: the strongest feasible level per property, recorded in the certificate.
4. **Review** by the supervisor against this document; status set.
5. **Close**: callers that are already native call the L2 interface directly; the bridge stays
   until no L1 caller remains. `tools/closure.py` keeps the boundary from eroding.

Small, independently reviewable changes. One writer per shared file. Agents do not invent
state representations: shared L2 types are introduced by the supervisor or by a work order
that names them.

## Choosing units

By dependency structure, not by file: strongly connected call-graph components, shared
memory effects, callback relations. Prefer low coupling, high confidence, tractable
verification, much removable machinery, architectural value and reusable technique. Start
small; gameplay state machines come after the techniques are proven on leaves.

## The Amiga version

`assets/amiga/` holds the original game for another CPU. DOS is authoritative for the DOS
behaviour; Amiga is independent evidence of design and intent. Agreement strengthens a
reading; disagreement is investigated and classified (confirmed equivalent, equivalent under
assumptions, similar purpose with different implementation, confirmed difference, unresolved)
and never silently normalized. DOS behaviour is never changed to match Amiga without an
explicit decision. Amiga analysis is static and used where it resolves a real ambiguity.
