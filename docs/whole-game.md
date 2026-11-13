# Whole-game regression

Run from the repository root:

```
python tools/wholegame.py
```

The command runs every `tests/scenarios/*.txt` file in name order and returns
zero only when every compared boundary agrees and every required scenario
milestone was reached. A passing scenario prints one line containing its bound
actually reached, wall time, page flips per second, and `reference` or `cached`.
Terminal records are labelled separately and do not inflate the frame rate.
`--refresh` regenerates references. Positional scenario names select a subset;
`--progress` prints diagnostic original-frame scalars. `--python-vga --refresh`
selects the slower independent Python VGA callbacks for a cross-check.

This is a finite regression certificate. It starts at GAME:RunDosGame, the
assembly game entry after Borland startup, or at an explicitly named component
entry with a documented cold fixture. It does not boot DOS, execute the packed
EXE directly, cover all 69 levels, prove arbitrary input histories or establish
all interrupt interleavings. The exact packed-file certificate remains
`verify.py`; portable C and these tests add no byte-match credit.

## Scenarios

All input and bounds are checked in. Input authoring may use C to plan a flight;
expected state is always generated independently by the rebuilt original.
No scenario imports a C-produced state snapshot or patches gameplay state
during execution.

| Scenario | Entry and purpose |
|---|---|
| startup | Real game entry, unskipped startup pictures and initial attract frames; no sound card. |
| adlib | Real entry, actual AdLib probe, calibration, TIMER callbacks, menu and Q through DOS termination. |
| attract | Original recorded attract scripts, with no input; cold renderer fixture. |
| reveal | Original sprite reveal scripts, with no input; cold renderer fixture. |
| pregame | Original pregame scripts, with no input; cold renderer fixture. |
| completion | Original completion scripts, with no input; cold renderer fixture. |
| menu | Real entry; F3 difficulty, F4 player count, F5 options, control selection and Escape. |
| two-player | Real entry and two-player game, extended player-one and ordinary player-two keyboard scans. |
| passenger | Real entry, actual joystick calibration, takeoff, landing, boarding, another flight and delivery; fare 477. |
| gameplay | Real entry, keyboard control, repeated impact deaths, level retries, game over, BIOS name entry and DOS score saving. The persistent score file begins with blank scores so zero qualifies. |
| enemy | Real entry, F2/BIOS entry of FIRSTCOMMUNION, F1 to level 2, controlled hover, bird hit and life loss. |
| water | Real entry, joystick flight to the water, controlled water contact, then energy exhaustion on its surface and life loss. No impact damage. |
| high-score | Cold score-editor integration with score 999999, letters/digit/backspace, score display and in-memory file creation. |
| password | Cold password-editor integration with letters, digit and backspace, through normal return. |

The demo bounds cover recorded-script prefixes, not their entire natural
duration. Cold fixtures declare page geometry, player/control defaults and the
keyboard vector statically, matching the documented routine-test fixture; they
never capture initialization by running either implementation. The full-entry
scenarios cover initialization and its composed callers separately.

The water scenario includes hovering to use energy, then holds the player at
the surface before exhaustion. Its assertion requires a negative LevelTimer,
zero impact and `PlayerYPixels + 18 == WaterYPixels` when the game starts the
death fade. It is not a claim that touching water kills instantly. The bird
assertion requires a positive timer and zero impact; that trace also exercises
UpdateBirdFlight/FindPlayerTouchingEnemy, has no gameplay Escape, and makes no
passenger delivery. The crash trace requires impact at least 2300. End-state
assertions require the relevant life decrement, player count, level or fare.

## Input and timing

The fixed timing policy is explained in `architecture.md`. Every maintained
scenario names it explicitly. A small file looks like:

```
timing pit-quantum-at-polls
frames 200
card none
1: esc -esc
4: esc -esc
9: f1 -f1
12: enter -enter
14: cycle=enter,-enter
60: right
120: -right
requires GAME:RunGameFromPassword GAME:MovePlayerWithVgaCollisions
```

`N:` means after page flip N; zero is before the first flip. Events become
eligible at the next keyboard polling entry. Several scans on a line queue in
order and deliver one per polling visit, not all in one interrupt. Named arrow
keys include E0; `-key` adds the break bit. Other tokens are hexadecimal raw
scan bytes. `cycle=enter,-enter` repeats that sequence when the explicit queue
is empty, allowing a non-flipping input wait to see press and release.
`cycle=off` stops the repetition. Be careful
at a static menu: repeatedly changing unrecognized keys can continually restart
its timeout, so the bound must stop at its last visible page or provide a menu
command.

`joystick` declares the initial raw 201h waveform. `stick=-1,0` selects left and
neutral Y; axis commands are -1/0/+1. They expand to two F0h button samples and
fixed axis discharge counts: X 2/9/28, Y 2/10/28. The game computes its own
calibration and thresholds. `sticks=0,-1;0,-1;0,1` cycles those waveforms once
per eligible frame; a later `sticks=0,1` replaces the cycle. `joy=f0,f0,ff,...`
supplies a raw waveform instead. OUT 201h rearms the waveform as in the device
contract. These are hardware inputs, not writes to player input arrays.

`bios` lists finite hexadecimal INT16 key words for editors. `scores blank`
provides a valid complemented 107-byte UGH!.HI fixture with blank score columns;
file content, handles, positions and writes stay inside the modelled DOS file
system. `entry` selects a cold component entry, `players` configures that cold
fixture, `password` supplies a cold initial edit buffer, and `score` supplies a
cold score-editor value. `end return` or `end exit` requires normal return or
modelled DOS exit within the frame bound and compares a final terminal record.
Other scenarios must reach exactly their fixed page-flip bound.

`requires` names routines that must actually execute in the original trace.
`expect Name value` asserts an end scalar. `death crash|bird|water` asserts the
corresponding original-state witness above. A matching but incorrectly routed
scenario fails these checks instead of receiving a misleading PASS.

## Compared state and reference reuse

At GAME:4EE5, before the page-flip RET, compare SHA-256 digests of:

* The complete original address space: DGROUP, all GAME/SOUND/TIMER code and
  variables, far banks/workspaces, IVT and BIOS state, unexpected writes and
  memory above 1 MiB. As in difftest, only dedicated stack scratch below the
  original incoming return frame is excluded. There are no gameplay/data masks.
* The complete device-state prefix, including four 64-KiB VGA planes, latches,
  controller/palette registers, OPL/PIT/PIC state, fixture script cursors, finite
  IRQ events and the modelled DOS files/handles. Unsupported requests fail.
* A running SHA-256 of ordered platform events, encoded as four little-endian
  uint32 fields per event. Each frame drains its events after hashing, so neither
  side accumulates an ever-growing log.

Each record also contains plain-text level, lives, score words, player position,
platform/carried state, first passenger/demo state, water, timer, impact, fade
and caller-return scalars. These help inspect a report; they do not replace the
full-state digests. Terminal records additionally cover shutdown or editor/file
effects after the last flip.

A reference key covers the rebuilt load image, the complete scenario text,
tool version/source, independent emulator source, Unicorn version and the
compiler binary used for its optional VGA hardware helper. The existing
checked rebuilt-image certificate is verified before loading. Changing portable
gameplay C does **not** refresh expected state: the new C must agree with the
old original reference. A cache hit constructs the fixture and runs only C;
the Unicorn CPU never starts. Refresh is atomic, and temporary source/DLL/build
receipts are removed even on failure.

Only compact references, `last-run.json`, the edge receipt and a short report
for a failing scenario persist in `build/whole/`. There are no frame images,
per-frame files or RAM dumps. See the worker report for measured times and size.

## First divergence

The first mismatching frame stops native execution. Its
`NAME.divergence.json` contains expected/actual digests and scalars, named RAM
differences resolved through the same independently built symbol coordinates as
`ugh_sym.h`, device field differences, the checkpoint used, and the first
different routine entry with incoming registers and caller identity. The first
register difference is reported separately from the first state/log or entry
order difference so unused ABI scratch does not displace the first effect.

Original checkpoints hold RAM, full CPU context, device state, scheduler and
rolling hash every 32 frames in RAM only. On a cached failure one diagnostic
replay creates checkpoints. Replay from the nearest checkpoint reaches the
previous frame and records entries only within the failing frame. Native C
replays its cheap prefix from entry: retaining a native C call stack would need
fibers or a continuation rewrite and would complicate the code being checked.
This deliberate adaptation leaves the expensive emulator replay checkpointed.

The trace build instruments generated scratch copies of adapters; maintained
C is untouched. It records entry order, memory/device/log digests and register
arguments, not per-instruction execution. Inline ICE bit readers are excluded
from the sequence because they have no corresponding standalone C adapter.
The entry difference narrows the investigation; the separate register report
can require checking the caller contract before blaming a routine. Reproduce an
actual translation error as a new direct suite case before fixing its body,
then rerun normal/poison comparisons and the unchanged whole-game reference.

`python tests/_whole_kat.py` checks CPU/device checkpoint replay at frame 32,
512 seeded native-versus-Python VGA vectors, complete real map/demo digests,
IRQ input policy and a deliberate translation fault in scratch. Doubling the
demo fade step is caught at frame 3 and the trace names RunScriptedDemo as the
caller that introduced it. No intentional fault remains in maintained C.

## Coverage and maintenance

Original routine-entry hooks collect a set of routines. Hooks at the 76
previously unverified sites collect actual `(site, target)` transfers, not
inferred edges from callee presence. Hooks retire after their evidence is
complete; there is no global Python instruction hook. Native VGA callbacks
contain only hardware operations and never dispatch original game code to C.

`build/whole/call-edges.json` preserves the c-close baseline and adds scenario
witnesses to covered obligations. `coverage.py` reads it only when the complete
input receipt is current and its run passed. It reports these additions
separately from routine/instruction coverage; the c-close worker's files remain
untouched. A bounded edge witness is not a certificate of all callee paths.
Sound Blaster corruption continuations and arbitrary external handlers remain
explicit debt even if ordinary gameplay agrees.

To add a scenario, copy a small existing file, choose a finite bound and fixed
hardware inputs, and add outcome assertions. Run it by stem while authoring.
Inspect the original scalars to ensure it reached the intended event, then run
the complete gate twice. Keep the full cold set around ten minutes or less;
measure a long scenario before extending it. Reuse existing references while
changing C, and run `difftest.py`, `difftest.py --poison`, `verify.py`,
`asmverify.py` and `cjudge.py` before accepting translation changes.
