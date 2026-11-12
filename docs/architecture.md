# Portable translation boundary

`UGH.EXE <-> src/` is the existing byte-exact reconstruction. `src/ -> c/` is a
separate behavioural certificate. `host/` is not implemented in this phase.
The design adopts pre2's original-address-space model, bounded routine tests,
explicit integer widths and narrow device services. Differences follow below.

## Memory and register contracts

`ugh_mem` is 110000h bytes. Load segment is 1010h; the rebuilt MZ relocation
table is applied without sorting or filtering. All program frames retain their
original relative placement, including runtime, GAME, SOUND, C, TIMER, the zero
workspace, 23 far-data frames and DGROUP. Segment:offset sums above FFFFFh remain
addressable (A20 enabled, as in the reference harness). Offset arithmetic wraps
through explicit uint16_t conversions. Byte/word/dword helpers perform little
endian, unaligned access; no native pointer represents an original far pointer.
VGA aperture detection uses the physical address, including segment aliases.

`Regs` carries AX/BX/CX/DX/SI/DI/BP/SP/CS/DS/ES/SS/IP/FLAGS. **Both DS and ES flow
through every adapter**: a fixed DGROUP DS would break SOUND, C and far copies.
Constants such as DATA_SEG identify storage, not an implicit current DS. Use r->ds
when the instruction uses DS. All three code segments contain mutable state.
Only the RAM image owns game state: no static gameplay globals, record copies,
converted pointer tables or native allocations for original state. Local scalar
temporaries and saved registers are allowed. Device state is separately owned
by the platform, not a shadow copy of game state.

The DLL entry is `int c_<Label>(Regs *r)`; use `c_<MODULE>_<Label>` plus Case.cfunc
when a label is ambiguous. Return zero on normal completion; nonzero is a test
failure, not an invented game result. The adapter receives the incoming SP after
CALL, before its prologue. `arg16(r,0)` reads the first far-cdecl argument at SP+4.
Adapters consume no host return frame; the test runner accounts for RET/RETF/IRET
after return. CS/SS/SP/DS/ES are compared for every case, other registers and defined
flags by the declared contract. Restored flags must be restored, including IF/DF.
Compiler scratch flags and architecturally undefined flags are not outputs unless
there is evidence a caller consumes them. Poison mode seeds every unspecified
general/segment input and arithmetic flag identically on both sides.

Fallthrough is an explicit call to the next translated body. A shared tail is one
helper called by each owning entry, retaining each entry's save/restore and flag
contract. ICE's helpers and its physically separated match tail demonstrate this:
they are inline within c/ice.c and count as reached, not independently translated.
Indirect dispatch reads original offset/segment words and resolves those addresses
to translated functions; never replace a stored callback with a native pointer.
`ugh_dispatch` currently accepts SOUND:ClearSoundState only. This exercises the
TIMER indirect call without faking an interrupt vector or a no-op callback.
The ISR pilot's callback register preparation is sufficient for this no-argument
callee; adding targets that consume working registers/stack requires reproducing
those call-site values and adding cases before expanding the dispatcher.

GAME:001C..001F have near RET despite far C declarations. Preserve actual stack
effects when translating callers: model the incoming return words and entry ABI,
or report a bounded nonreturn. Do not silently replace RET by RETF. These hooks,
self-referential tricks outside ICE and general callback dispatch remain future
work, not claims made by this pilot.

## Addresses and rebuilt execution

`tools/cgen.py` reads build/link/plain/UGH.MAP, its detailed module-contribution
placements and the TASM listing symbol tables. The DGDATA _DATA contribution
starts 92h into DGROUP; GAME/SOUND/TIMER start 8h/Ch/6h into their frames.
Using only a segment's first address would misplace labels. TASM's wrapped long
symbol names and TLINK's `idle` public entries are handled explicitly.
metadata/names.json supplies names and expected coordinates, not placement.
Every identity must have a matching independently built symbol. Missing/moved
symbols, ambiguous generated aliases, changed source receipt hashes, and changed
load-image/relocation-site hashes or source-file sets fail. Header macros have separate `UGH_O_MODULE_Name` offsets and
`UGH_S_MODULE_Name` live segments. `--check` rejects a stale checked-in header.

The harness loads **only the plain rebuilt executable**, never assets/dos/UGH.EXE
or build/oracle/UGH_X.EXE. It verifies the rebuilt image against the existing
image digest in oracle.json; it does not create another oracle lock. After the
plain build exists, differential tests need no original file. The historical
verify.py gate still needs original evidence to certify packing and relocation
order; this infrastructure does not replace it. Tests enter routines directly
and never boot DOS or start the game. A dedicated 8000h stack is outside program
storage. Return kind is explicit (near, far, iret); a sentinel plus checked SP
detects missing/wrong returns. IRQ entry clears live IF/TF, preserves the saved
FLAGS in the frame and restores them on IRET. Instruction budgets and unsupported requests fail.

Both sides start from the same complete RAM/device snapshot. Comparison covers
all RAM except scratch **below the incoming return frame** in the dedicated stack
segment. Return words, arguments, all DGROUP/far data/code bytes, extra declared
output buffers, VGA planes/latches/map-mask state, and ordered port/DOS logs are
compared. Declared buffers are also checked explicitly. There is no data mask or
oracle-derived expected result. ICE also uses the independent dataprobe decoder,
with stream/table bytes from the rebuilt image. Synthetic streams come from the
independent packer; the original routine remains the behavioural oracle.

## Original C decision

Keep src/c/module.c unchanged and translate it into the memory model. This is a
deliberate exception to the preferred one-source option: erasing far/huge does
not preserve 16-bit int, four-byte original pointers, 42-byte records, aliasing of
record 12 with named SOUND globals, or huge-pointer normalization. Ordinary GCC
lvalues cannot address those overlapping cells without rewriting the expressions.
Replacing the entire original module with compatibility macros would obscure both
versions and jeopardize its existing Borland certificate.

The read-only probe build/workers/c-infra/measure_c.py confirms native GCC rejects
the source; even after erasing the qualifiers it fails assertions for DOS int,
record stride and pointer storage. c/module_pilot.c proves three translated
functions: SwapDwordByteOrder, DisableMusicSectionLoop and GetElapsedMusicTime.
The latter two leave ES=SOUND, as the compiled code does. Time subtraction is
uint32_t modulo arithmetic; rate zero is an unsupported INT-0 path, not zero time.
No runtime function is rewritten in src/. Later portable arithmetic may replace
compiler helpers only with differential evidence for the corresponding callers.

## Platform and deterministic time

Platform services are byte/word port transactions, VGA aperture reads/writes,
software interrupts, and explicit service points (platform.h). Python Devices is
the oracle-side implementation; c/platform.c is the C implementation. The pilot
implements unchained full-mask VGA write mode 0/read mode 0, sequencer map mask,
latches, and ordered PIC/PIT writes. No other VGA register mode, retrace, DOS,
OPL, DSP, DMA, keyboard or joystick request is silently serviced. Independent
known-answer checks cover the implemented subset; differential agreement alone
does not prove the device model.

Future services and their observable contracts:

| Service | Contract to implement once per side |
|---|---|
| VGA | 4x64KiB planes; GC read/write modes, latches, rotate/logic/masks; SEQ, CRTC, attribute flip-flop, DAC RGB6/index cycling; BIOS video mode/state; scripted 3DAh retrace |
| IRQ/PIT/PIC | IVT get/set, mask/EOI log; 1193182Hz integer PIT clocks; divisor 0=65536; deliver IRQ0 with IRET register/flag context; keep game timer slots in original DGROUP |
| Keyboard | ordered raw port-60h scan bytes/IRQ1; BIOS INT16 AH00/01 queue and ZF; no implicit scan filtering |
| Joystick | port-201h trigger and deterministic read-index axis decay/buttons; retain software-count calibration semantics |
| AdLib | OPL 388/389 address/data/status transactions with scripted probe/timer status; translate event interpreters and leave their state in SOUND |
| DSP/DMA | DSP base+6/+A/+C/+E reset/data/status protocol, DMA1 address/page/count/flip-flop, PIC mask/IRQ; expose the original eight-voice mixer's output bytes |
| DOS files | in-memory named-file fixture service, create/truncate/open/read/write/close, DOS AX/CF, lowest free handles and short/error results; compare requests, contents, cursors and handles |
| Other DOS/BIOS | vector get/set, critical-error action, time AH2C, video INT10, exit AH4C; fixture/configuration only, never real file writes or process exit in tests |

No wall clock drives tests. The pilot invokes each TIMER ISR synchronously from
a prepared snapshot; no asynchronous IRQ arrives inside a call. The dispatcher
subtracts NextPitQuantum, marks expired slots, invokes due callbacks in descending
slot order, acknowledges IRQ0 and sends only the low earliest-interval word to
the PIT. A single expiration adds the period once, without catch-up. Registration
preserves FLAGS. The music initializer requests 1843h clocks for TickAdlxPlayback;
fade scheduling requests 0001:D1EBh. Event handlers can change these intervals.
Those are not a universal game/frame frequency.

For future wait tests, supply a deterministic event script in integer PIT clocks
at SERVICE_RETRACE, SERVICE_TIMER_WAIT and SERVICE_IO. Advance time at the same
named polling boundary on both sides; deliver enabled IRQs in a fixed order and
model IRET. Polls must exhaust a finite script or make progress; never use host
sleep or arbitrary instruction-count time to escape a wait. Retrace phase, raw
input and DOS delays belong to that script. ISR/main-code interleavings outside
these service points remain unverified until explicit race cases are added.

## Pilot and work ownership

There are 12 exported translations in five files, with suites game_pilot, ice,
render_pilot, timer_pilot and module_pilot. The tests include real built scores,
sprite bytes and all five ICE resources, 16-bit boundaries, reverse/overlapping
copies, a zero-count 65536-iteration VGA loop, timer carry/expiry and 16 slots,
non-boolean music flags and wrapping 32-bit clocks. Mutation controls and gate
receipts live in build/workers/c-infra/. Coverage is generated separately under
build/c/: a directly tested translation, an inline helper, and an executed entry
are different claims. This is a pilot, not gameplay or SDL3 completeness.

metadata/translation-plan.json assigns all 286 curated entries exactly once,
uses the existing naming regions where possible, collapses direct-call/shared-tail
cycles and groups independent leaves by region and depth. Its 56 packages own
disjoint C files in 14 waves; same-wave packages can proceed in parallel. The
integrated pilot and common headers/platform are reserved for the supervisor.
Indirect edges are listed explicitly as unresolved dependencies; static graph
absence is never evidence of no callback. Resolve each from original tables and
call sites before claiming callers/composed execution complete.

## Direct interaction census

The following is the complete application **physical-routine-interval** inventory
from tools/graph.py (52 intervals). Shared/fallthrough tails can be attributed to
the preceding interval; e.g. SwapAndDisplayVgaPage also owns local exit tail 4EE6.
`DX?` means the graph cannot resolve a port across a branch/call. Code establishes
3DAh for retrace, 3C9h for DAC components, and 3C5h for sequencer data. DSP accesses
use DspBasePort+6/+A/+C/+E (probe bases 200h..260h, stride 10h). These unresolved
values must not become guessed constants in a translation. Caller side effects
include all their callees; this table lists direct instructions only.

<!-- hardware census appended from retained graph evidence below -->

| Physical owner interval | Direct ports | Direct software interrupts |
|---|---|---|
| GAME:InsertHighScoreAndClearScore | - | 16/AH=00, 16/AH=01 |
| GAME:SaveHighScores | - | 21/AH=3C, 21/AH=40 |
| GAME:LoadHighScores | - | 21/AH=3D, 21/AH=3E, 21/AH=3F |
| GAME:EditLevelPassword | - | 16/AH=00, 16/AH=01 |
| GAME:MovePlayerWithVgaCollisions | 03CE, 03CF, DX? | - |
| GAME:AdvanceWaterSurface | 03CE, 03CF | - |
| GAME:DrawWaterSurface | 03C4, 03C5 | - |
| GAME:DrawWaterSurfaceFrame0 | DX? | - |
| GAME:DrawWaterSurfaceFrame1 | DX? | - |
| GAME:DrawWaterSurfaceFrame2 | DX? | - |
| GAME:RestoreRainBackground | 03CE, 03CF, DX? | - |
| GAME:DrawRainParticles | 03C4, DX? | - |
| GAME:RefreshHudAndTimerBar | 03C4, 03C5 | - |
| GAME:DrawTransparentSprite | 03C4, DX? | - |
| GAME:RestoreBackgroundRectangle | 03CE, 03CF | - |
| GAME:SaveDrawPageBackground | 03CE, 03CF | - |
| GAME:WaitVerticalRetraceActive | DX? | - |
| GAME:WaitVerticalRetraceInactive | DX? | - |
| GAME:InstallKeyboardSequenceInterrupt | - | 21/AH=25, 21/AH=35 |
| GAME:RestoreKeyboardInterrupt | - | 21/AH=25 |
| GAME:HandleKeyboardScanInterrupt | 0020, 0060 | - |
| GAME:UploadChunkyImageToVgaPlanes | 03C4, DX? | - |
| GAME:InstallDosCriticalErrorFailHandler | - | 21/AH=25 |
| GAME:UploadBasePalette | 03C8, DX? | - |
| GAME:BlackenVgaPalette | 03C8, DX? | - |
| GAME:SwapAndDisplayVgaPage | 03D4, 03D5 | 10/AH=00, 21/AH=4C |
| GAME:SeedRandomFromDosSeconds | - | 21/AH=2C |
| GAME:InitializeDosVideoInputAndSound | - | 10/AH=00, 10/AH=0F |
| GAME:EnableAllVgaWritePlanes | 03C4, 03C5 | - |
| GAME:ConfigureVgaPicturePages | 03C0, 03C1, 03C4, 03C5, 03D4, 03D5 | - |
| GAME:ConfigureVgaGameplayPages | 03C0, 03C1, 03C4, 03C5, 03D4, 03D5 | - |
| GAME:DetectAndCalibrateJoysticks | 0201 | - |
| GAME:SampleJoystickAxesAndButtons | 0201, DX? | - |
| SOUND:CalibrateSoundDelay | - | 21/AH=25, 21/AH=35 |
| SOUND:BeginSoundDelayMeasurement | 0020 | 21/AH=25 |
| SOUND:FinishSoundDelayMeasurement | 0020 | 21/AH=25 |
| SOUND:WriteAdlibRegister | 0388, 0389 | - |
| SOUND:KeyOffAdlibChannel | 0388, 0389 | - |
| SOUND:SetAdlibFrequency | 0388, 0389 | - |
| SOUND:InitializeAdlibPlayback | 0388, DX? | - |
| SOUND:WriteSoundBlasterDsp | DX? | - |
| SOUND:StartDmaSampleBlock | 0002, 0003, 000A, 000B, 000C, 0083 | - |
| SOUND:HandleSampleDmaInterrupt | 0020, 0021, DX? | - |
| SOUND:PrimeSampleDmaPlayback | 0021 | - |
| SOUND:HandleDspProbeInterrupt | 0020 | - |
| SOUND:ProbeSoundBlasterDmaIrq | 0021 | 21/AH=25, 21/AH=35 |
| SOUND:InitializeDspPlayback | 0021 | 21/AH=25, 21/AH=35 |
| SOUND:ShutdownDspPlayback | 0021 | 21/AH=25 |
| SOUND:ResetSoundBlasterDsp | DX? | - |
| TIMER:InstallTimerInterrupt | - | 21/AH=25, 21/AH=35 |
| TIMER:RestoreTimerInterrupt | 0040, 0043 | 21/AH=25 |
| TIMER:HandleTimerInterrupt | 0020, 0040, 0043 | - |

The exact direct graph, including source symbols, callers, unknown accesses and indirect
sites, is retained in build/workers/c-infra/graph.json. Memory-mapped VGA consumers also
include DrawRainParticles, DrawTransparentSprite, DrawMapTile, RestoreSpriteBackground,
RestoreTileBackground, RestorePlayfieldBackground, ClearAllVgaPlanes and their rectangle/
page helpers. Portless wrappers inherit device effects through those calls.

Borland runtime is a separate library class, outside the 286 translation entries. Its
rebuilt runtime interrupt census is retained in build/workers/c-infra/runtime-io.txt:
C0H startup uses INT21 AH30/4A/58/67/48/49, BIOS INT1A AH00, vector get/set
AH35/AH25 for vectors 00/04/05/06, stderr AH40 and exit AH4C; linked library
isatty uses AX4400, lseek uses AH42, setblock uses AH4A and write uses AH40.
These startup/termination/file operations need platform contracts if a future composed
test crosses them. No runtime startup or DOS boot runs in the pilot. The existing
runtime library remains the byte-match authority; it is never rewritten as matching C.
