# Native Windows host

The host starts at `GAME:RunDosGame` after the historical Borland startup and
uses SDL3 for the window, input and audio. It does not execute DOS, the EXE's
instructions, or a CPU emulator. By default, `hostbuild.py` reads
`metadata/closure/*.json` and links each component whose certificate `status`
is `migrated` or stronger through its maintained bridge. It keeps a renamed L1
entrypoint for each bridge fallback. The pure L1 build is available with
`--literal`. The historical byte certificate and the L1 behavioural
certificates remain separate from native closure evidence.

From the repository root:

```powershell
python tools/build.py
python tools/hostbuild.py
build/host/ugh.exe
```

`python tools/hostbuild.py` builds the default bridged variant at
`build/host/ugh.exe`; the current linked units are coordinate_scale, decimal,
far_copy, ice and timer. `python tools/hostbuild.py --literal` builds the pure
L1 comparison variant at the same path. Each build writes
`build/host/hostbuild.json`; its `variant` and `linked_units` fields identify
the selection. `build/host/ugh.exe --version` prints that selection. A
certificate that qualifies but lacks one native implementation file, one
bridge, or exported `c_` endpoints stops the build with the unit and reason.

The DOS build uses the pinned historical tools through `tools/dos.py`.
`hostbuild.py` requires that build to be current, and checks its source receipts,
symbols, load-image digest and relocation-site digest through `cgen`. It uses
`C:/msys64/mingw64/bin/gcc.exe`, SDL3 3.4.16 from
`C:/tools/sdl3-3.4.16-mingw/SDL3-3.4.16/x86_64-w64-mingw32`, and Nuked-OPL3 from
`C:/tools/nuked-opl3-765ec962e473`. SDL's provenance is in its installation's
`provenance.json`; Nuked's commit and LGPL-2.1-or-later provenance are pinned in
`metadata/verif-tools.json`. No downloads happen during this build.

The result is `build/host/ugh.exe`, with `SDL3.dll` and the applicable MinGW
runtime beside it. `hostbuild.json` records the command, compiler hash, input
hashes and third-party provenance. The build copies the third-party licenses
and the exact Nuked source alongside the result. The application source and
relink command are available in this repository and receipt.

The only program-data input is **`build/link/plain/UGH.EXE` from our build**.
`hostbuild.py` copies it to `build/host/ugh-data.exe`. At runtime the host reads
that copy's MZ header, complete load image and all relocations in their stored
order, relocates at 1010h and initializes the original address space. This
includes mutable code-segment state and the embedded graphics, levels and
music. The bytes are data for translated C, never native instructions. A
compiled-in SHA-256 rejects a data file from a different build. `--data FILE`
can relocate this same checked file. The application needs neither Python nor
`assets/` after building; keep `ugh-data.exe` and the DLLs beside `ugh.exe`.

## Controls and saves

Escape skips the startup pictures. F1 starts a game; Return or another key
advances its pregame waits. F2 edits the level password, F3 selects difficulty,
F4 selects player count, F5 selects controls, and Q quits from the menu. In
gameplay Escape leaves the game. The window's close button also exits.

Player one uses the extended arrow keys and **right Ctrl** for action. Player
two uses **W/Z/A/S** for up/down/left/right and **left Ctrl** for action; the
numeric keypad direction keys and keypad Enter are also original player-two
bindings. Keypad 0 is an original player-one action binding. These follow the
rebuilt keyboard sequence table; ordinary and E0-prefixed scans remain distinct.
Password and score editors receive separate BIOS key words, including Return,
Escape and Backspace. Losing window focus releases held controls.

An SDL gamepad's D-pad or left stick maps to player-one arrow scans, its south
button to right Ctrl, and Start to F1. This is a keyboard mapping: select
keyboard in the game's control options. Physical gameport emulation is used
by scripted joystick scenarios, where the game performs its own calibration.

Interactive saves go to `build/host/saves/UGH!.HI` by default, determined from
the executable's directory rather than the working directory. Choose an
existing parent directory with `--save-dir DIR`; the host creates DIR if needed.
Only `UGH!.HI` is exposed to the game's DOS file calls. The platform retains
the DOS handles, modes, cursors, complemented bytes and error semantics; the
host loads the file into that service and persists changed contents with a
temporary file and atomic replacement. It performs no per-frame disk writes
when the contents are unchanged. An I/O failure exits with an explicit error.

Headless runs always use isolated in-memory score fixtures. Windowed scripted
runs also use those fixtures unless `--save-dir` is explicitly supplied. That
explicit option loads and persists the selected directory's score file.

## Bounded runs and comparison

```powershell
build/host/ugh.exe --headless 12 --script tests/scenarios/startup.txt
build/host/ugh.exe --headless 16 --script tests/scenarios/adlib.txt
build/host/ugh.exe --headless 256 --smoke 256
python tools/wholegame.py
python host/check.py --variant native
python tools/hostbuild.py --literal
python host/check.py --variant literal
python tools/hostbuild.py
```

Run the first checker command after the default build and the second after the
literal build. Each command compares all 14 maintained scenario boundary
digests against `build/whole/*.ref.json` and runs the 256-flip attract smoke;
the checker only reads those references. Results are written to
`build/workers/host-native/host-check-native.json` and
`build/workers/host-native/host-check-literal.json`. The final default build
restores the native-bridged executable at the standard path.

`--headless N` runs at most N page flips without opening video/audio devices.
It prints one JSON record per page flip to stdout and, for a terminal scenario,
one final record. Diagnostics go to stderr. Records use `wholegame.py`'s exact
RAM stack exclusion, complete device prefix, rolling ordered I/O-log SHA-256,
scalars and terminal convention. No game state is rewritten at a boundary.
`host/check.py` captures stdout in memory and compares it with the references
already certified by `wholegame.py`; it never creates expected output.

The native reader accepts the scenario headers and frame-indexed raw scans,
make/break names, E0 arrows, BIOS words, repeat cycles, raw joystick waveforms,
`stick=` and `sticks=` cycles described in `whole-game.md`. It also supports the
documented cold component fixtures. `requires`, `expect` and `death` remain
reference-generation assertions enforced by `wholegame.py`; the host checker
compares every resulting boundary, including their scalar witnesses.

`--smoke N` starts the original attract scripts from the same explicit cold
renderer fixture used by the attract scenario, with no input or sound card.
It must reach N flips to pass. It is a bounded integration smoke, not a complete
playthrough or a replacement for the scenario comparisons.

Other options:

| Option | Effect |
|---|---|
| `--script FILE` | Read a scenario. In a window it replaces live controls; its frame bound is the default. |
| `--frames N` | Stop a windowed run after N flips, maximum 16384. |
| `--digests` | Print digests in a windowed run too. Live input/save state differs from fixed references. |
| `--timeout SECONDS` | Hard process wall bound, 1..3600 seconds; exceeded bounds exit 4. |
| `--shot FILE.bmp` | Save one 320x200 scanout at orderly shutdown, including headless runs. |
| `--wav FILE.wav` | Capture 48-kHz signed 16-bit stereo Nuked output, including headless runs. |
| `--scale 1..8` | Initial window scale, default 3; resizing preserves the logical 320x200 canvas. |
| `--no-audio` | Disable the SDL audio device; synthesis/capture remains available. |
| `--unpaced` | Windowed diagnostic run without sleeps; use a finite frame bound. |
| `--help` | Show usage. |

Headless/scripted/frame-bounded runs default to a 120-second wall bound. A
watchdog enforces it even if an adapter stops reaching service points. An
ordinary interactive run has no wall bound unless requested. Orderly frame
completion, required terminal completion and window closure exit 0; unsupported
services or missed bounds exit nonzero. No child process remains running.

## Platform contracts

| Service | Host implementation and boundary |
|---|---|
| VGA | Reuses `c/memory.c` and `c/platform.c`: four 64-KiB planes, latches, read/write modes, map masks and register/DAC state. `host/video.c` scans the game's unchained 256-colour layout from CRTC start/pitch, line compare and RGB6 DAC, including the fixed eight-line gameplay HUD. SDL scales with nearest sampling and letterboxing. Rendering reads device memory directly and cannot disturb the latches. |
| Keyboard | SDL keys become set-1 make/break/E0 bytes, queued outside game state. One byte per keyboard polling entry enters port 60h through the actual installed IRQ1 handler. INT16 AH01 peeks/sets ZF and AH00 consumes a separate BIOS word; the live editor can wait for input. |
| Timer | At the named retrace and sound wait sites in `architecture.md`, schedule one eligible IRQ0 with the current PIT divisor (zero means 65536), respecting IF/PIC masks and executing the actual translated ISR/callbacks. Retains the two original temporary calibration-handler fixture events and the explicit BIOS INT08 chain. No SDL audio thread can call the engine. |
| Time/presentation | Same `pit-quantum-at-polls` event order as `wholegame.Clock`. Interactive pacing uses the maximum of accumulated PIT-clock time and a 14.268-ms retrace timeline. It sleeps only at service points, never invents extra IRQs to catch up, and resynchronizes the wall origin after a host stall. It presents flips and retrace visits so fades without page flips remain visible. |
| Files | The existing narrow INT21 file service owns all virtual handles/buffers and reports DOS results. Host persistence supplies the high-score file and saves changed output; headless fixtures never access the filesystem. |
| AdLib | The original probe status waveform selects AdLib. A nullable output observer forwards 389h writes, with the current 388h address, into pinned Nuked-OPL3. Integer scheduled time produces PCM queued to SDL. All track, effect and callback logic remains translated SOUND/C/TIMER code. |

Only two optional, default-NULL hooks were added to `c/platform.*`: an output
observer for the external OPL synthesizer, and an interrupt-service override
for interactive BIOS keyboard input. Neither changes the `Devices` layout or
the deterministic backend. No routine translation or `tools/cbuild.py` changed.

## Verified extent and gaps

On 2026-11-13 the standalone executable matched **all 14 maintained scenarios**:
startup 12 flips; AdLib 9 + DOS exit; attract 96; reveal 128; pregame 160;
completion 160; menu 14; two-player 160; passenger 1650; gameplay 979;
enemy 1106; water 5474; password 6 + return; high-score 9 + return.
The 256-flip attract smoke passed. These compare complete digests, including
music/timer state and ordered transactions, rather than images alone.
The full routine gates passed 3681/3681 cases normally and with `--poison`;
`python tools/wholegame.py` also passed all maintained scenarios. A forced
one-second wall bound terminated a long run with exit 4 after 1.03 seconds.

A paced SDL window run received real Windows keyboard messages through SDL,
skipped the pictures, started a game and moved the player through 240 flips.
SDL audio opened successfully; Nuked produced 714203 nonzero channel samples
in 487623 stereo frames. A separate menu run showed the fully faded menu.
The engine wrote a 107-byte score file; native readback of that persisted file
matched an independently executed rebuilt-original boundary. Details, commands
and receipts are in `build/workers/host/REPORT.md`. The screenshots
`menu.bmp` and `live-play.bmp` are scanouts from these windowed runs: desktop
screen capture failed in the sandbox, so the requested renderer fallback was used.

Timing is the documented deterministic polling policy, not cycle-accurate PC
hardware. Scanout implements the modes Ugh uses; there is no general VGA BIOS,
text-mode presenter, arbitrary BIOS handler, Sound Blaster digital output or
DOS runtime startup. The known corrupt near-RET Sound Blaster/resource paths
remain unsupported. This host does not repair those original control transfers.
The gamepad mapping is implemented but no physical controller was available for
an end-to-end check. The literal adapters retain their existing finite internal
loop budgets; this evidence covers bounded scenarios, not every level or an
unlimited session. Music is evidenced by successful SDL audio setup, register
traffic and captured nonzero PCM, without a subjective listening claim.
The DOS time request retains the fixed `0x10203040` scenario fixture, so startup
random seeding is repeatable instead of following the workstation's time of day.
