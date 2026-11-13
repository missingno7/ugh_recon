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
endian, unaligned access. Effective offset calculations wrap before each operand;
bytes within a single word/dword operand stay physically contiguous across FFFFh.
This also applies above 1 MiB (A20 enabled); no native pointer represents an original far pointer.
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
`tools/cgen.py` generates `c/ugh_adapters.h`, package include headers and
`c/dispatch_table.inc` from actual TRANSLATES/export pairs. The common header
also declares pending plan entries. `ugh_resolve` is the single original-address
resolver: it returns an implemented adapter or NULL. `ugh_dispatch` returns
UGH_BAD_CALLBACK for untranslated/unknown targets, never default success. It
flows DS/ES and working registers, supplies the target CS during execution, and
restores the calling CS. It does not construct a CALL frame or implement RET.
Near CALL sites use `ugh_call_near` with the measured original return IP;
tail transfers retain the existing frame. Water's saved-DS tail ABI is retained.
TIMER's far callback site supplies its ISR save area and original far return.
`ugh_dispatch_interrupt` accepts only the explicit known IRET entries, executes
their body, consumes the six-byte frame and restores CS/IP/FLAGS. PUSHF/CALL FAR
keeps live IF/TF; hardware delivery clears them before entering the handler.
External saved BIOS handlers remain unsupported unless explicitly modeled.

GAME:001C..001F really execute near RET. `ugh_call_near_ret_hook` constructs
CALL FAR's two words, executes the actual translated leaf and pops only IP.
CS remains GAME and the saved caller CS remains at SS:SP. `UGH_CONTROL_TRANSFER`
(4) propagates that exact landing without unwinding native caller-owned frames.
It is an unresolved transfer, never successful resource/device completion.
`CONTROL_PREFIX` adapters resolve for composed diagnostics but coverage does not
count them as completed translations. `python tests/_abi_kat.py` compares the
actual original landing, registers, nonstack RAM, retained CS word and devices:

| Entry | First hook call | Actual continuation | Retained word |
|---|---|---|---|
| SOUND:ProbeSoundBlasterDmaIrq | 1F14 -> GAME:001F | GAME:1F19 | SOUND CS |
| SOUND:InitializeDspPlayback | Probe after calibration | GAME:1F19 | SOUND CS |
| SOUND:ShutdownDspPlayback | 20C0 -> GAME:001F | GAME:20C5 | SOUND CS |
| C:LoadSoundBankResource | 0111 -> GAME:001D | GAME:0116 | C CS |
| C:InitializeSoundSystem, bits=2 | Initialise DSP -> Probe | GAME:1F19 | SOUND CS |

GAME:1F19 decodes as IN AX,DX then SUB DI,DI; at 1F1C the next opcode is
invalid (FF /7). A returning word-input service would therefore lead to a CPU
fault, not the intended SOUND probe scan. Word IN and CPU fault delivery are not
modelled services. GAME:20C5 enters UpdateFloatingPassengerApproach after its SI
load, using live DS/SI/BX. GAME:0116 enters the middle of the menu player-count
instruction stream: XOR AL,26h; XOR AX,3; store player count; shift/store array
size; jump to menu redraw. Subsequent RETs consume the retained segment word as
an IP in GAME. Those corrupted continuations are not repaired or executed in C.
The second resource-length hook at C:014D and the later intended DSP hooks have
no accepted returning path from these entries. The four control prefixes remain
explicit translation debt. C:InitializeSoundSystem's ordinary disabled/AdLib
paths are implemented and tested; its DSP path has a verified transfer landing.

The tree-reward full-pool defect is separate: SpawnFallingItem pushes caller BX,
scans indices 22,20,...,0, then reaches RET with saved BX still at SS:SP. RET
pops that saved value as IP, leaving the actual near return word pending and
CS unchanged. Thus the continuation depends on the caller's BX and subsequent
stack contents. No allocation failure result or normal reward return is invented.

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
record stride and pointer storage. c/music_clock.c proves three translated
functions: SwapDwordByteOrder, DisableMusicSectionLoop and GetElapsedMusicTime.
The latter two leave ES=SOUND, as the compiled code does. Time subtraction is
uint32_t modulo arithmetic; rate zero is an unsupported INT-0 path, not zero time.
No runtime function is rewritten in src/. Later portable arithmetic may replace
compiler helpers only with differential evidence for the corresponding callers.

## Platform and deterministic time

Platform services are port transactions, physical VGA accesses, software
interrupts and named polling service points. `tools/emu.py:Devices` independently
implements the emulator boundary; `c/platform.c` and `c/memory.c` implement the C
boundary. The ctypes layout is checked against `sizeof(Devices)` before every
suite. RAM, complete device state (including script cursors, files and handles),
and ordered I/O/DOS/IRQ logs compare. Unsupported requests and exhausted scripts
fail. `python tests/_platform_kat.py` supplies independent known answers for each
service, including the contiguous-operand regression.

| Service | Implemented narrow fixture contract |
|---|---|
| VGA | Four 64-KiB unchained planes; reads fill all latches, read modes 0/1; write modes 0..3, rotate/logic/set-reset/bit-mask and sequencer map mask. Mode 1 copies latches, mode 0/mask zero retains latches. GC 0..8, SEQ 0..4, CRTC 0..24, attribute index/data phase and DAC RGB6/index cycling are stored device state. Scripts provide raw 3DAh status; reads reset attribute phase. |
| IRQ/PIT/PIC | IVT in original RAM; PIC mask and ordered EOI, PIT command 36h and low/high divisor bytes (zero means 65536). Finite explicit site/visit IRQ events carry integer PIT clocks. Enabled, unmasked delivery reads IVT[8+IRQ], creates the real saved FLAGS/CS/IP frame, clears IF/TF and executes an accepted handler to IRET. |
| Keyboard | Raw 60h script bytes including prefixes and breaks. INT16 AH01 peeks and sets ZF; AH00 consumes one BIOS key word. An empty AH01 queue sets ZF; an empty blocking AH00 request fails. The BIOS word queue is a separate fixture, without implicit conversion from raw scans. |
| Joystick | OUT 201h logs actual AL and rewinds that port's finite raw sample script. Every IN consumes exactly one raw byte. Two button reads and axis priority/counting remain in translated code. |
| AdLib | 388h address, 389h register data; 388h probe/timer status is scripted. OPL event interpretation, delays, channels and track state remain original SOUND RAM. |
| DSP/DMA | DSP probed bases 200h..260h: explicit status/data scripts at +Ch/+Ah/+Eh authorize reset/command writes at +6h/+Ch. No implicit ready/AA response or invented DMA completion. DMA1 address/count/page/mode/mask and shared low/high flip-flop, PIC mask/EOI are stored. IRQ delivery requires an event fixture. |
| DOS files | Eight case-sensitive named in-memory files of at most 8192 bytes, handles 5..31 allocated lowest first. AH3C creates/truncates, 3D opens, 3E closes, 3F reads, 40 writes/truncates at CX=0. AX/CF report results; invalid handles, missing files and access errors are explicit. io_limit supplies short transfers; dos_error injects one consumed error after dos_error_skip file requests. Contents, length, cursors and handles compare; no real host file is opened. |
| Other DOS/BIOS | INT21 AH25 stores DS:DX to IVT[AL]; AH35 returns ES:BX, otherwise preserving registers/FLAGS. AH2C consumes configured CH/CL/DH/DL. AH4C records fixture exit code; it never exits the host. INT10 AH00 records mode/page; AH0F returns configured mode/columns/page. These are boundary fixtures, not a DOS/BIOS boot or VGA BIOS initialization emulation. |

`m.device.script(port, values, cycles=1)` run-length encodes at most 128 runs
in one of 16 independent script slots, with 1..FFFFFFFFh finite cycles. Peeking
does not consume a run or cycle. Exhaustion still fails; after the last cycle the
cursor equals count and cycles_left remains one. OUT 201h restarts the entire
configured waveform and its cycle countdown. Empty waveforms and zero cycles
are rejected before fixture state changes. Port FFFFh configures BIOS key words;
FFFEh encodes DOS time as hour/minute/second/hundredth bytes.

`dos_error_skip` counts only INT21 AH3C..40 requests while dos_error is nonzero.
Every request logs first. A skipped request runs its ordinary service, including
natural failures. The selected request sets AX/CF, consumes dos_error, and leaves
file/handle/buffer state untouched. Non-file services do not decrement the count.
`m.device.file(name, bytes)` configures a file fixture. Ordered C logs have
1,080,000 entries (the whole menu exceeds the prior 270,000-entry bound).
These are explicit fixture capacities, not clipping in game algorithms.

A Case with kind='exit' stops at the modelled INT21 AH4C on the emulator side;
C propagates UGH_DOS_EXIT (5) with the live stack. No RET or host process exit is
fabricated. Ordinary routine cases continue to require a checked return sentinel.
The reference CPU's POPF-zero probe has 286 semantics; an 8086 rejection fixture
has not been supplied.

`m.device.schedule(segment, offset, irq=0, skip=0, clocks=1)` appends one of at
most 64 events. Only the next event is eligible; matching site visits decrement
skip first. IF-clear/PIC-masked events remain pending. Delivery logs
`(LOG_IRQ,irq,0,clocks)` and advances the integer clock by that many PIT clocks.
No wall clock, host sleep or arbitrary instruction-count timer is used. The
emulator stops/restarts at that original instruction; C calls
`platform_service_point_at` at the identical point. Calibration uses SOUND
loc_1163 and loc_116B (including inner LOOP visits), executes both real temporary
IRQ handlers, and retains DX's original Begin-handler-offset bias. Tests verify
both captured words and restoration of the prior vector. Retrace/input scripts
advance at IN operations. The additional GAME:00E9 and 0D7B polling sites permit finite keyboard IRQ traces
through main-menu/game composition. Main/ISR races elsewhere remain unverified.

## Translation inventory and composition

The maintained files now have content names. `menu.c`, `scene.c`, `actors.c` /
`actors_states.c`, `items_water.c`, `render.c` / `render_primitives.c`, `video.c`,
`dos_input.c`, `adlib.c`, `dsp.c`, `sound_api.c`, `sound_engine.c`, `timer.c`,
`timer_system.c` and `timer_stack.c` retain original-address adapters. Smaller
files contain menu helpers, demo scripts, game services, music clocks/analysis,
sound-state clearing, ICE, memory, ABI transfers and platform services.

`metadata/translation-plan.json` is a schema-2 routine/file/suite/status table,
with each of the 284 curated identities exactly once. There are 277 translated
entries, three established inline ICE entries and four control prefixes still
counted as remaining. `coverage.py` checks actual source markers, file paths and
suite declarations; it does not infer completion from a prefix or rename an
unsupported entry to inline. `cgen.py` publishes shared entries and explicit
control prefixes for dispatch without granting them translation credit.

C compiler scratch values can become visible through ASM callers. In particular,
StopAdlibTrackChannel's disabled exit leaves AX=SOUND; after active release it
pops the channel argument into CX, reloads AX=SOUND and DX=the saved guard.
StartAdlibTrackChannel also leaves the deadline low word in CX (tick+3),
which the assembly effect callers expose. RestoreAdlibVoiceAllocation retains
the compiler's BX stride scratch and POP CX
where SOUND's effect-expiry handler exposes them. ShutdownSoundSystem writes
through live DS; foreground fade cancellation or AdLib teardown -> TIMER removal can leave DGROUP,
so the final latch write goes to DGROUP:0002. ScanMusicEvents clears DF on its
runtime-memset path. These are literal behaviours, not API improvements.

`difftest.py --coverage` records executed call/tail edges per case as well as
instruction visits. A missing callee or unsupported request still fails. Known
external BIOS interrupt contexts and corrupt return targets remain outside the
finite certificate. Frame snapshots use a read-only observer at the real page
flip RET (GAME:4EE5); diagnostic stops propagate a budget result. The observer
does not change game RAM, clocks or platform logs. `tests/_whole_program.py`
starts GAME:0008 (_main), stops after two flips and compares the original-address
RAM, VGA/device state and ordered logs at each boundary. This is bounded
composition evidence, not a DOS boot or a complete playthrough.

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

Borland runtime is a separate library class, outside the 284 translation entries. Its
rebuilt runtime interrupt census is retained in build/workers/c-infra/runtime-io.txt:
C0H startup uses INT21 AH30/4A/58/67/48/49, BIOS INT1A AH00, vector get/set
AH35/AH25 for vectors 00/04/05/06, stderr AH40 and exit AH4C; linked library
isatty uses AX4400, lseek uses AH42, setblock uses AH4A and write uses AH40.
These startup/termination/file operations need platform contracts if a future composed
test crosses them. No runtime startup or DOS boot runs in the pilot. The existing
runtime library remains the byte-match authority; it is never rewritten as matching C.
