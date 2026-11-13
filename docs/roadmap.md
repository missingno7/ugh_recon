# Modernization roadmap and inventory

Living document. Method and rules: `docs/modernization.md`. Status values are the closure
statuses defined there; only the supervisor changes them.

## Starting point (2026-11-13)

- L0: byte-exact; all gates pass.
- L1 (`c/`, 6,596 lines): 277 of 284 routines translated and tested against L0 (3,677 cases);
  composition checked for two startup frames; whole-game scenarios being built.
- Machine-level machinery in L1, measured with grep (`c/*.c`): 405 functions take `Regs *`,
  1,014 direct memory accessor calls, 207 flag references, 1,070 segment-register references,
  47 dispatches through original addresses.
- L2 (`native/`): does not exist yet.

## Main obstacles

1. **Register and flag ABIs.** Many routines return results in CF/ZF/SF, pass values in
   registers, share tails, or leave ES for the next routine. Removing them needs liveness
   evidence at every call site.
2. **Segments.** Variables live in DGROUP, in the code segments of GAME, SOUND and TIMER, and
   in 23 far data frames; DS and ES change inside routines.
3. **Indirect control flow.** Timer callback slots hold `seg:off` pairs; demo scripts, actor
   state handlers and a 36-entry dispatcher call through tables; four C-to-GAME hooks are far
   calls to near returns (an original defect).
4. **Memory layout.** Parallel arrays, overlapping records (a sound channel record overlapping
   shared globals; an item's speed field reused as its lifetime), 16-bit wrap.
5. **Time.** Game logic runs partly in timer callbacks in interrupt context; the frame loop
   paces itself by retrace polling.
6. **Hardware.** Planar VGA with latches, AdLib, a DMA sample mixer, joystick timing.
7. **Thin composition evidence.** 76 call edges without a composed case.

## Decomposition

The program model (`docs/program-model.md`, `metadata/program-model.json`) partitions all 284
routines into 20 components by ownership and dependency: audio (75 routines, owning the storage
the C module and the SOUND driver share), passenger/stone (37), hazards (31), front end (23),
video/DOS (20), render/HUD (19), demo (13), timer (10), water/weather (9), input (8), numeric (7),
sequencing (6), falling items (5), ice (5), contacts (4), external hooks (4), pictures (3),
level loader (2), player physics (2), far copy (1). Measured facts that shape the order:

- 67 indirect transfer sites: 4 fully resolved, 61 resolved under stated invariants, 1 partial,
  1 external. Most dispatch is closable with recorded invariants, not open-ended.
- The call graph is shallow: two 8-routine cycles, everything else acyclic.
- No routine has an unrestricted complete register interface yet, because some callers are
  reached only through conditionally resolved sites. Interfaces are complete under the stated
  invariants.
- Passenger/stone state and demo state share one DGROUP range by mode; timer and audio call each
  other through callbacks; the level loader initialises several components' state.

## Evidence from the Amiga original

`docs/amiga.md`, `metadata/amiga-map.json` (65 correspondences: 5 confirmed equivalent, 8
equivalent under assumptions, 37 same purpose with different implementation, 14 confirmed
behavioural differences, 1 unresolved). Findings so far:

- The patrolling animal is the Triopterus, not a dinosaur; the stationary hazard is Dino.
  Renamed in L0, L1 and tests (16 symbols).
- Hazard phases, scores and the Triopterus impact-routing quirk's context correspond closely,
  with different timer constants (for example 150 versus 100 updates of warning delay).
- Craft physics was reimplemented for DOS with a different fixed-point scale (velocity words
  shifted by 6, clamps of 6144), not translated from the Amiga code.

## Architecture model

The native architecture is not designed up front. It is recovered (docs/modernization.md,
"Architectural recovery") and recorded in `docs/architecture-model.md`, which is created once
the program model and the Amiga correspondence are in. Planned uses:

- candidate ranking weighs whether a unit is a recovered subsystem with owned state and a
  clear role, not only coupling and removable machinery;
- record layouts confirmed by several readers and by the Amiga version become `STRUC`
  declarations in L0 (byte-neutral) and types in L2;
- state machines (passengers, animals, game flow) are recovered as states and transitions
  before their code is migrated.

## Candidates for early closure

| Candidate | Why | Concern |
|---|---|---|
| Pack-Ice decoder (`GAME:UnpackIceStream`) | pure function bytes to bytes; independent Python reference and exact packer; much removable machinery (register bit buffer, carry, backward segment pointers) | moderate architectural value; loops need bounded proofs |
| Timer slot table (TIMER register/remove/interval) | small owned state; parallel arrays to a struct; callbacks to typed pointers | callback targets must be resolved first; interacts with the timing model |
| Music clock and ADLX event scan (C module) | originally C, close to readable already; documented format | shares variables with the SOUND driver |
| Decimal and HUD number formatting | small, pure-ish | shared tails between several entry points |

## Pilot

Pack-Ice decoder. Selected because it exercises the whole pipeline (contract, liveness of
registers at call sites, segment-wrap preconditions, bridge, proofs, differential testing,
certificate) on a component with almost no coupling, and because an independent reference
(the Python decoder and the exact packer) allows generated test inputs. The timer slot table
is the second unit, chosen to exercise state ownership and indirect control flow.

## Inventory

| Component | Status | Certificate |
|---|---|---|
| Pack-Ice decoder | migrated. Primitives: level A (exhaustive enumeration and CBMC on the actual C). Whole decoder: level B only for windows of 16/6 and 32/4 bytes and an inductive step proof for 16/8; level C at real sizes (3,807 streams). Integration: level C. The worker proposed `verified-under-assumptions`; not granted, because the proved domain is far smaller than the contract's (real streams are 32,000 and 64,768 bytes). | `metadata/closure/ice.json` |
| Coordinate scaling | integration-validated: whole 16-bit domain enumerated on compiled code (A), bridge register shell proved (A), 14 scenarios with the bridge (D) | `metadata/closure/coordinate_scale.json` |
| Decimal digits | migrated: complete domains for the divisors the game uses (A), arbitrary divisors bounded (B) | `metadata/closure/decimal.json` |
| Far copy | migrated: observed call lengths proved (B), general overlap and wrap tested (C) | `metadata/closure/far_copy.json` |
| Timer service | migrated: each API operation proved from any admitted state (B), handle domains enumerated (A), tick accounting at 1/3/16 slots (B), interrupt interleavings open; both removal defects retained | `metadata/closure/timer.json` |
| everything else | unanalyzed | |

## Tooling gaps

- No C model checker on the machine (CBMC). It is the missing piece for level B on whole
  algorithms: a bounded two-implementation harness over the actual C at multi-token sizes.
- z3 is only available as a DLL extracted from a Ghidra extension into worker scratch; it
  needs a proper, pinned install outside `build/`.
- Worker sandboxes cannot reach the network or write `C:\tools`; tool installs are done by the
  supervisor.

## Running natively

`python tools/hostbuild.py` builds `build/host/ugh.exe`: the literal C with SDL3 platform services
(window, keyboard, AdLib through Nuked-OPL3). Its headless mode reproduces the whole-game digests
of all 14 scenarios. Closed native units are not linked into the host yet.

## Work in progress

None.
