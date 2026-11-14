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
| Music clock | verified-within-contract: all properties proved on the actual C for all inputs (A), zero-rate fault retained as a status; two of its three functions are never called in the scenarios | `metadata/closure/music_clock.json` |
| Level view | verified-within-contract: decoding proved (A); projection proved over every shipped level resource and checked against the actual loader (A). Introduces the shared types `native/level.h`, `native/geometry.h` | `metadata/closure/level_view.json` |
| Contact predicates | migrated: complete coordinate domains enumerated (A), arbitrary geometry and two-entry stone lists proved (B), scanning of up to 16 stones only tested (C) | `metadata/closure/contacts.json` |
| Random number generator | integration-validated: one step proved over all 64-bit states, bounds and register shell (A); reduction enumerated over 2^32 pairs; 14 scenarios and a rainy level with 2,795 draws (D) | `metadata/closure/random.json` |
| Falling items | migrated: every transition proved from any admitted slot state (B), finite domains enumerated (A), pickup scenarios for multiplier and timer items (D). Full pool: at most 11 occupied slots under the shipped spawn sources (bounded), abnormal return still reproduced. The lives item has no producer in the shipped game | `metadata/closure/falling_items.json` |
| Actor types | verified-under-assumptions: projection over all shipped actor resources and the per-phase validity table proved (A); renderer history persistence across a mode switch proved by 23 actual-C properties imported from the render-history unit (B). Assumptions: ordinary disjoint RAM, resources and stack; valid physical slots below 16 with an active prefix of at most 15 plus sentinel; normal initializer ownership; synchronous pixel services. Not A for whole-session persistence, corrupt graphs or asynchronous mutation. `native/actors.h` holds the accepted design (docs/actor-storage.md) | `metadata/closure/actor_types.json` |
| Demo interpreter core | migrated: all 28 shipped scripts enumerated over 62,214 ticks (A), one-instruction steps from any admitted slot (B), demo-to-gameplay history handoff checked | `metadata/closure/demo_core.json` |
| Hazards (bird, Triopterus, Dino, reward tree) | migrated: each of 31 handlers proved one step from any admitted slot state (B), finite and generated transitions enumerated (A); composition with all 16 stones only tested. DOS constants and the Triopterus impact routing retained | `metadata/closure/hazards.json` |
| Stone lifecycle | migrated: six handlers proved one step from any admitted slot (B), scalar domains enumerated (A), live borrowing by hazards checked; out-of-contract inputs fall back to L1 in the bridge (zero fallbacks in scenarios) | `metadata/closure/stones.json` |
| Passenger itinerary, appearance, departure | migrated: eight handlers proved one step (B), scalar slices enumerated (A); waiting, request, approach and delivery handlers stay L1 | `metadata/closure/passenger_itinerary.json` |
| Passenger waiting, request, approach, boarding, delivery | migrated: all twelve entries proved one step (B) by 206 split output/frame/dependence properties whose coverage of each handler is checked; seven full 16-bit slices enumerated (A); 3,238 cases and 19 scenarios with zero fallback (C/D). The bridge checks the native selected craft and consumes every request. Retained: 140-tick requests, exact-pixel boarding, unsigned fare floor, rescue fare before the pair switch. Question and rescue are not reached by the scenarios | `metadata/closure/passenger_delivery.json` |
| Water passengers: resurface, sink, float, floating request and approach | migrated: 145 split properties with checked coverage (B); 647,752 differential comparisons, 120 cross-unit tail cases and six 60-dispatch lifecycle chains through rescue, delivery and departure (C); `water-physics` scenario reaches resurface, sink and float (D). Retained: raw velocity integrated by SAR 6 and clamped E800..1800, unsigned sink limit, exact water−18 craft height, lifetime 0 wraps to FFFF. Floating request/approach and the 2195 no-op are not reached by any scenario. The three passenger certificates stay separate for now (decision: consolidate only when a passenger facade replaces the three bridges) | `metadata/closure/passenger_water.json` |
| Actor render history (gameplay erase/draw/overlay, demo erase/draw, reset) | migrated: six slot operations proved against the actual C bodies (B), eight full 16-bit slices (A), 695,552 comparisons and a 26-boundary demo-to-gameplay carryover run (C), 18 of 20 scenarios reach it with zero fallback (D). Native code decides history and the ordered restore/draw requests; the pixel blits stay L1. Debt: the bridge carries a generated copy of the `RunGameFromPassword` session body to intercept its inline actor loops. Lifts actor types' render-persistence obligation to B | `metadata/closure/actor_render.json` |
| Demo presentation (common runner, reveal, pre-game, attract and completion wrappers, fade and reveal-width effects) | migrated: 35 split properties on the actual C (B); three full 16-bit effect slices (A) inside 259,768 compiled comparisons, 24 seeded defects detected, 16 rebuilt-L0 ordering cases for callback-before-clear, Q/Escape interruption and completed returns (C); 18 of 20 scenarios reach it with zero fallback (D). A resumable native cursor yields every palette, page, water, input, music and renderer call as a service request. Retained: Q exits FFFF and Escape 1 from the scan code masked to 7 bits, fade level wraps by −4 with signed boundaries, the reveal width clamps only its low byte (no lower clamp), the pre-game return is ignored by the session. `loc_0B4E` (a lone RET with no caller or vector) stays L1 with a trivial contract. Does not retire the duplicated session body | `metadata/closure/demo_presentation.json` |
| Main ADLX music interpreter | migrated: nine event operations proved one step from any admitted channel state (B); all 11 shipped resources produce identical ordered AdLib writes (96,144). Introduces `native/audio.h` | `metadata/closure/adlx_main.json` |
| AdLib effects ADLX interpreter | migrated: eight event operations and the timer step proved one step from any admitted state (B); all 11 shipped resources replayed as effects (90,280 events, 118,912 ordered writes); `gameplay-adlib` scenario (D). Channel 9 instrument stamps the aliased saved-voice owner (retained); END now reaches native stop/restoration | `metadata/closure/adlx_effects.json` |
| AdLib channel allocation, start, stop, voice restoration | migrated: effect-record selection proved on the actual C (B: first free record, else least unsigned age, ties to the first); start/stop/compaction/restoration by 90,000 actual-C cases, all 11 resources and 19 scenarios (C/D). Retained: current slot stays 12 after music restoration, stale saved owners, capacity failure leaves the guard set. ADLX loading stays L1 | `metadata/closure/adlx_allocation.json` |
| ADLX loading and cursor reset | migrated: all 11 resources loaded in 5,280 contexts and 22 full playback pipelines to END compared on compiled code (C); output, frame and dependence properties proved on a canonical layout (B); 3,526 cases and 19 scenarios (C/D). Retained: no extent validation, chunk skips by low word, length = root size − 34, partial caller-pointer mutation, wrapper treats parser FFFF as success, empty IMAP points at the TRCK tag. Scan and section application remain L1 | `metadata/closure/adlx_loader.json` |
| Music section scan, section application, AdLib tick scheduler | migrated: 30,000 actual-C cases, all 11 resources at every accepted section threshold (2,988 applies, 7,251 ticks), 4,924 cases and 19 scenarios (C/D); 37 split properties proved (B). `ScanMusicEvents` has no caller in the shipped game, so section looping is unused: no scenario can reach it, and the evidence is API and corpus only. Tick still advances the clock when busy; the effect iterator continues from the raw slot left by a callback (12 becomes 13) | `metadata/closure/adlx_sections.json` |
| Music start, stop, volume, fades, guarded clock, silence | migrated: 264 resource pipelines through start, fade and stop with full RAM and ordered writes, 5,342 cases, 19 scenarios (`adlib` and `gameplay-adlib` run 7 starts, 13 stops and 108 fade steps) (C/D); 16 split properties proved (B). TIMER registration and delivery stay a service boundary. Retained: stop silences effects before checking that music plays, volume walks the voice count by low byte (count 256 visits voices 0..8 once), fade completion is unsigned and strict, divide faults keep their partial state. `AdvanceGuardedSoundClock` has no caller | `metadata/closure/adlx_music.json` |
| AdLib voice driver entries (volume, gain, key-off, frequency, instrument, raw register write, I/O delay) | migrated: 70,000 actual-C cases, all 11 resources through the facade, 6,508 cases and 20 scenarios (C/D); 75 split properties (B). Channel acceptance uses the low byte (0100 is voice 0); no device or initialisation checks; device-aperture instrument sources fall back to L1 before any read. Audio now has 48 of 75 routines native; remaining: AdLib init/shutdown/calibration (6), sound facade and banks (7), sample import (1), DSP (7), mixer and DMA (6) | `metadata/closure/adlx_voice.json` |
| AdLib lifetime, shared sound reset, CPU-loop calibration | migrated: 12,000 compiled pairs, all 65,536 probe status bytes, 88 resource pipelines, 6,594 cases and 20 scenarios (`startup`, `adlib`, `gameplay-adlib` reach them) (C/D); 21 split properties (B). DOS vectors, interrupt delivery and TIMER are services. Retained: the attempted flag is set before calibration, so a failed probe makes the next init report success without retrying; calibration has no division and stores two raw counter words (the multiplier keeps a 1179 bias, the delay uses only its low byte); the reset clears exactly 1,160 bytes and keeps DMA buffers and handles. A native port must supply the calibration measurement. Audio: 54 of 75 routines native | `metadata/closure/adlx_lifetime.json` |
| Sample import, voice cursor reset, sample mixer | migrated on API evidence: 67,336 compiled pairs (including all 65,536 reset inputs), 256 import-reset-mix pipelines, 6,684 direct L0 cases (C); 11 split properties (B); the real DMA IRQ handler run against the Sound Blaster model captures 641 identical bytes. Unreachable in the shipped program (see below), so no scenario reaches it. Retained: the importer searches literal `VHDR`/`BODY` tags instead of walking chunks and treats any nonzero compression as mode 3, but nothing decompresses it; the mixer returns requested bytes minus remaining pairs (mixed units, which leaves a stale buffer tail); division by the live count keeps its fault prefix. Audio: 57 of 75 routines native | `metadata/closure/adlx_samples.json` |
| everything else | unanalyzed | |

### The Sound Blaster path is unreachable in the shipped DOS program

Recorded 2026-11-14 from close-adlx-9's run and checked in the source:

- `InitializeAdLibSound` always calls `InitializeSoundSystem(1)`: AdLib only. No setting asks for
  the digital device (bit 2).
- No sample (`FORM`/`8SVX`) resource ships with the DOS game.
- The bank and delay hooks GAME:001C..001F are single near RETs, called as far procedures. The DSP
  probe's far call to 001F returns into unrelated GAME code before any DSP transaction.

Decision: the game is not patched to reach this path. Its routines are still closed, because they
are part of the shipped program, but on API evidence against the deterministic Sound Blaster model
(`card sb` in `tools/wholegame.py`, documented in close-adlx-9's report), with a small proof
budget. The broken transfers stay explicit L1 boundaries. The native host needs no Sound Blaster
output to play the shipped game; digital sound in a port would be a new feature, not a gap.

## Tooling gaps

- CBMC 6.11.0 and z3 are installed and pinned in `metadata/verif-tools.json`. Whole-routine
  byte-RAM bridge proofs still time out; level B is reached per operation on typed state.
- Worker sandboxes cannot reach the network or write `C:\tools`; tool installs are done by the
  supervisor.

## Running natively

`python tools/hostbuild.py` builds `build/host/ugh.exe`: the literal C with SDL3 platform services
(window, keyboard, AdLib through Nuked-OPL3). Its headless mode reproduces the whole-game digests
of all 20 scenarios. The host links every unit at status `migrated` or stronger through its bridge (`--literal` builds the pure translation); both variants reproduce all 20 scenarios.

## Work in progress

None.
