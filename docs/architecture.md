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

GAME:001C..001F have near RET despite far C declarations. Preserve actual stack
effects when translating callers: model the incoming return words and entry ABI,
or report a bounded nonreturn. Do not silently replace RET by RETF. General
resource-loader call chains, arbitrary corrupted targets and self-referential
tricks outside ICE remain outside the composed certificate.

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
| DOS files | Eight case-sensitive named in-memory files of at most 8192 bytes, handles 5..31 allocated lowest first. AH3C creates/truncates, 3D opens, 3E closes, 3F reads, 40 writes/truncates at CX=0. AX/CF report results; invalid handles, missing files and access errors are explicit. io_limit supplies short transfers; dos_error injects one consumed error. Contents, length, cursors and handles compare; no real host file is opened. |
| Other DOS/BIOS | INT21 AH25 stores DS:DX to IVT[AL]; AH35 returns ES:BX, otherwise preserving registers/FLAGS. AH2C consumes configured CH/CL/DH/DL. AH4C records fixture exit code; it never exits the host. INT10 AH00 records mode/page; AH0F returns configured mode/columns/page. These are boundary fixtures, not a DOS/BIOS boot or VGA BIOS initialization emulation. |

`m.device.script(port, values)` run-length encodes at most 128 runs in one of
16 independent script slots. Port FFFFh configures BIOS key words; FFFEh encodes
DOS time as hour/minute/second/hundredth bytes. Configure fields directly during
setup; no fixture may execute the oracle to manufacture expected state.
`m.device.file(name, bytes)` configures a file fixture. Bounds are explicit fixture
capacities, not clipping added to game algorithms.

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
advance at IN operations. Main/ISR races elsewhere remain unverified.

## Translation and final-wave ownership

The integrated tree has 132 directly tested adapters, three ICE entries reached
inline, and 149 remaining routines out of 284. GAME:4681 and 4981 are palette
data, excluded from the routine census. This is bounded behavioural evidence;
it changes no original C/runtime byte-match claim. Full gameplay is unverified.

`metadata/translation-plan.json` retains integrated packages in wave 0 and assigns
all remaining routines to eight exclusive C/suite pairs in final wave 1. Workers
order local direct-call and indirect mutual families internally. Cross-package
calls use the common resolver and real caller-owned ABI/frame. An absent callee
fails with UGH_BAD_CALLBACK; workers list that exact edge as unverified and add
composed cases after integration. There is no emulator bridge or success stub.
This permits each worktree to compile independently before peer packages land.
`coverage.py` checks the plan against the curated routine census exactly once,
including inline-only entries, and rejects overlapping final-wave files.

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
