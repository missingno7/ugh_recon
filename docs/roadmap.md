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

## Decomposition (provisional)

To be replaced by the dependency analysis (program model work order). Layers from the bottom:

1. Pure leaves: Pack-Ice decoder, byte and number conversions, decimal formatting.
2. Platform services: VGA, keyboard, joystick, DOS files, AdLib, DSP/DMA, PIT/IRQ.
3. Timer service (16 callback slots).
4. Sound engine: the C module (ADLX music, IFF samples) and the SOUND driver.
5. Resources and levels: level records, maps, sprite banks, palettes.
6. Rendering: tiles, sprites, background restore, HUD, page flipping.
7. Simulation: player craft, passengers, animals, items, water, collisions.
8. Sequencing: menus, demos, scenes, high scores, game flow.

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
| Pack-Ice decoder | analyzed (in progress) | `metadata/closure/ice.json` (pending) |
| everything else | unanalyzed | |

## Work in progress

| Work order | Writes | Purpose |
|---|---|---|
| `whole` | `c/`, `tests/`, emulator and test tools | whole-game scenarios L0 vs L1 (level D base) |
| `model` | program model tool and data | call graph, indirect targets, effects, SCCs, candidate ranking |
| `amiga` | Amiga analysis tool and docs | static disassembly of the Amiga original and a correspondence map |
| `pilot-ice` | `native/`, closure tooling, verification tooling | the pilot through the full pipeline |
