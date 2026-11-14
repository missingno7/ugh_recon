# Standalone native executable: census and plan

Goal: the native game runs on its own, with no L1 fallbacks, no L1 routines, and no emulated DOS
machine (`ugh_mem`, `Regs`, the dispatcher, `c/platform.c`) in the production executable. The
platform services it needs are specified in [port-contract.md](port-contract.md).

## Census at 485f006 (close-adlx-19)

`python verif/standalone_census.py --all` builds an instrumented copy of the native-bridged
host and runs the 20 scenarios and the smoke run. Its receipts and detail tables (per-bridge
machine use, 392 named state cells with candidate owners, every machine edge with
scenario/frame) are written under `build/workers/close-adlx-19/`.

- All 20 scenarios match their references with the instrumentation in place.
- **Fallbacks:** none of the 104 bridge fallback sites was taken. This is scenario evidence, not
  a proof that the admission failures are unreachable.
- **ICE decoder:** one L1 path runs unconditionally. `c_UnpackIceToScratch` (`c/dos_input.c`)
  calls the original ICE decoder 49 times: 32 times from the attract-map preparation and 17
  times from the level loader. The host build renames direct calls inside L1 bodies to their
  `l1_` copies, so replacing the decoder's dispatcher entry did not retire this call.
- **Remaining entries:** six of the 14 non-replaced L1 entries execute: timer install, restore
  and chain, `DispatchActorUpdates`, `DosShutdownTail` and `UnpackIceToScratch`.
- **L1 code at run time:** eight `c/` files still execute: `dispatch.c`, `memory.c`,
  `platform.c`, `timer_system.c`, `video.c`, `demo_scripts.c`, `dos_input.c` and `ice.c`.
  `ugh.h` adds inline machine helpers. All 27 `c/` files are still linked.

## Plan

This is a composition plan, not a migration or a change to accepted contracts. The census is
scenario evidence; an unobserved branch is not a universal unreachability proof. Keep the
current deterministic event/input/time policy for verification until the user chooses a live
policy. The five choices at the end of docs/port-contract.md are not implicitly decided here.

## Candidate world and ownership

Use one `GameWorld` containing the actual owners, with borrowed views passed to accepted APIs.
Do not persist every bridge's projection struct as an independent copy. `OWNERS.md` lists the
program-model writers/readers for every named cell; `BRIDGES.md` lists each bridge's use and
`static.json` retains raw numeric, indexed and far-pointer access expressions. Unknown aliases
remain unknown; ordinary typed ownership is an admitted-domain choice, not an alias theorem.

| Candidate storage | Authoritative native owner / borrowed users |
|---|---|
| Level/session/configuration | Session owns level, lives/score reset and initialization order. Menus write the same player count/control-mode configuration that input/session consume. Keep `PlayerCount` and `PlayerArrayBytes` as distinct raw words; no new normalization. Score is shared with gameplay awarders and high-score insertion. |
| Player slots and control commands | One player store for position, velocity, caches, carried state, five command words and rendering history; physics, actor interactions, input and session borrow it. Do not rebuild cached pixels/history from fixed coordinates at entry. |
| Actors, hazards, items and histories | Existing actor/stone/passenger/hazard/item policies own their field updates. Session invokes ordered passes; actor_render retains its policies and pass adapters, not a second session implementation. Descriptor/callback roles become typed resource identities. |
| Level resources and working arrays | Resource registry owns stable borrowed descriptors, lists, animations, scripts, tile resources and codec workspaces. Session alone constructs current level/platform/actor/enemy fields. Retain reserved bytes, ordering and mutable reveal-width metadata; do not assume every resource byte is forever immutable. |
| Weather and shared surface | One surface/particle state. Water/weather updates it; level initialization and menus also write the shared water Y. All readers must refer to that same value rather than separate menu/weather copies. |
| Video | One `VideoPages`/palette owner, 64-Ki-cell storage of four index lanes, hidden background and fixed HUD storage, persistent read plane/write-lane selection. Full GC/latch state may remain a native compatibility backend; removing broader inherited state needs the fifth port decision and the census's explicit C/D assumption, not a claim of a universal invariant. |
| Input | One scan/sequence/calibration owner, borrowing shared player modes/commands. BIOS editing characters and raw scan bytes are separate queues. Calibration/sample counts stay in common units. |
| Audio and timers | Accepted AudioState remains the single C/SOUND owner, including record-12 and channel-9 aliases; timer slots/handles/phase and the logical music counter are separate state with explicit cuts. Sample descriptors borrow resources. Do not merge ADLX ticks, PIT clocks and wall time. |
| Front end | One raw high-score table and edit state, text cursor and password buffer; the session owns password-to-level lookup. Files are services, not another copy of the score table. |
| RNG and lifetime | One four-word RNG state; only seconds partially reseed it at the accepted seed point. Lifecycle owns its continuation/saved mode and calls peers; it does not own their state. |

These are composition boundaries drawn from the accepted headers and certificates. They are
not new globally allocated structures written by this work order. `variables[*].complete=false`
in the program model is retained; all raw binding expressions must be audited as a unit moves.

## Verification after state leaves ugh_mem

Create a **test-only** serializer/projector with two directions: import the existing cold
scenario fixture into a typed world; serialize the native world and explicit service state at
every original frame/terminal boundary into the historical observation layout. Production
must neither allocate a DOS RAM image nor call that projector.

The projector needs more than the scalar list. Existing references hash RAM (with the stated
stack exclusion), device state and cumulative ordered I/O. Initialize its immutable/unwritten
bytes from the independently rebuilt baseline; overlay declared owner fields, stale/reserved
bytes and any scratch bytes that references observe. Map typed resource/callback identities
back to original words **only in the test projector**. Map boundary roles to original return
identities for the scalar observation; do not bring emulated call frames into the production
world. Keep a write/effect journal where final typed state alone cannot reproduce overwritten
or stale bytes. Never fill projected state from expected reference records.

First validate the projector against the current bridges: at every boundary compare its
serialization to actual `ugh_mem`, devices and logs. Use per-owner output/frame/dependence
checks and deliberately corrupt one projected field, stale byte, lane selection, event order
and identity mapping to show the comparator detects them. Check overlapping views and all
shared writers. Then retain exactly the existing references while substituting direct
composition one unit at a time. API-only and malformed/alias evidence stays separate from the
scenario gate; do not claim the scenarios exercise every admitted state.

A test service backend can serialize DOS-shaped port/vector/file effects without any game
routine from c/. That backend is verification infrastructure, not the live SDL port layer.
It must be independently checked against the current platform model before c/platform.c is
removed from the verification run. A production backend may use semantic transactions under
the port contract; it does not need to expose DOS addresses or a `Devices` byte layout.

## Ordered steps and acceptance gates

| Step | Concrete change to propose next | What proves it | User port decision required? |
|---|---|---|---|
| 1. Freeze the seam | Preserve this census, fixture/resource identities and observation schema; build the test-only projector and owner layout. | Project every boundary against the current host, including terminal records; output/frame/dependence and corruption controls for the serializer. | No. Use existing deterministic fixtures, resources and scheduling. |
| 2. First subsystem: resource/ICE leaves | Replace the scratch wrapper's direct L1 decoder call with composition of the accepted native ICE API and an explicit workspace view. Bind numeric, geometry, copy and RNG leaves directly. | Existing codec corpus and API certificates; byte-window/workspace effects and whole-game references. A linker/symbol check must show no L1 ICE body; census verifies the call disappears. | No for the current verified resource provider. A new pack and its admission/error policy need decision 3 later. Preserve fixed seed replies until decision 4. |
| 3. First stateful composition: audio + timer | Retain one AudioState; direct typed peer calls and ordered OPL service lists. Replace timer install/restore/chain and stack adapters with lifetime requests, typed callback roles/intervals and baseline slot initialization. Preserve ordering, handles, phase and partial-error semantics. | Replay affected audio/timer API/corpus evidence, callback-mutation cases and frame references; show no timer/audio L1 body or machine edge. Keep the current virtual PIT policy initially. | No for deterministic verification. Live event policy is decision 1. Optional digital/malformed compatibility is decision 5; do not repair the four external hooks. |
| 4. Input and video services | Bind raw scan delivery/count replies, retrace level requests, indexed plane/copy/DAC transactions to explicit native services. Retain shared pages, read plane, lane mask and hidden storage. | All input/video/render/weather API evidence plus scenarios; ordered service streams, lane contents, collision replies and exact palette/retrace behavior. Reproduce census edge examples; distinguish the narrower measured video assumption from full compatibility. | Live joystick units: decision 2. Live pacing/retrace: decision 1. Restricting the broader VGA contract: decision 5. A full compatibility-state backend can defer that restriction. |
| 5. World and actor passes | Move canonical player/actor/hazard/item/level/weather fields to the one world; bind descriptor/callback identities through typed registries. Replace DispatchActorUpdates with a direct ordered native pass and loc_0B4E with its explicit no-op role. | Per-owner write/frame tests and callback mutation/alias admission cases; all scenarios via the validated projector. Compare old/new dispatch order and histories; require no fallback and no machine edge for moved passes. | No with current resources/fixtures. A broader/narrower resource-admission profile depends on decisions 3/5. |
| 6. Front end, session and lifecycle | Direct calls for drawing/input/audio/demo/session peers; native level streaming and startup/frame/pause orchestration. Replace DOS shutdown tail with ordered typed terminal services; no Regs or far stack frames in production. | Front-end/session/lifecycle API evidence, pause make/break order, per-level guard tests, failed-service prefixes, terminal scenarios and every frame reference. Recheck shared control/water/score writes. | No for current scripted services. New persistent file errors/pack policy: decision 3; live seed: decision 4. |
| 7. Fail closed and unlink the machine | For every unobserved fallback, replace admission failure with an explicit unsupported/invariant result at the same prefix; eliminate its L1 link. Remove c/ from the production link and all original-address resolution. Keep broken hooks unsupported or in test-only compatibility; never invent their successful meaning. | Repeat all scenarios/API contracts for the admitted domain; injected admission failures must stop rather than execute L1. Link map/undefined-symbol and source checks ban l1_*, c_ game entries, Regs, ugh_mem, dispatch/near-call and c/platform.c in production. Re-run this census before removing it from that target. | Choosing a narrower admitted compatibility domain is decision 5. Observed-zero alone does not justify a universal branch-deletion theorem. |
| 8. Live standalone SDL backend | Implement the port services without DOS vectors, RAM projection or device emulation. The verification executable retains its separate test backend/projector; the shipped executable does not link them. | Deterministic replays still match references; live service conformance tests exercise scans, calibration, retrace, ordered OPL, file partial/error cases and callback serialization. Verify startup/shutdown/focus-loss/device-loss independently of game algorithms. | Resolve all five choices: event scheduling, joystick units, resource/missing-data policy, live seed and optional bit-exact profile. |

Steps 2-6 can be staged behind the existing host only as verification scaffolding; completion
means the resulting production target has **no** c/ runtime dependency, not that a fallback
counter happens to be zero. The first measurable retirement is the ICE scratch path. The
first stateful subsystem should be audio/timer because it already has a typed owner, explicit
ordered output and a small set of remaining lifetime/ABI shims.

The final port may still read a chosen resource package derived from the rebuilt image; that
does not authorize loading a mutable 1-MiB DOS machine or executing original code. Resource
identity translation, compatibility serialization and historical symbol offsets belong in
tools/tests, not the standalone game's ordinary API.
