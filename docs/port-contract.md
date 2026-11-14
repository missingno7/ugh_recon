# Platform contract

The port supplies the services below; native units retain the game's decisions and arithmetic.
This contract consolidates the committed certificates at `a5e9a1e783d245b3e9d5cfb5e94df36c61564192` (2026-11-14), including
the accepted lifecycle and session units. Service role names describe capabilities, not a new
shared binary ABI. The inherited VGA-state row reports a scenario census, not a proof.

## Service list

| Area | Services | Native callers / detail |
|---|---|---|
| Video | Stateful register transactions; plane/aperture reads and writes; pixel and copy transactions; page presentation; DAC; retrace levels | video_dos, render_primitives, player_physics, water_weather, hud; presentation and session through those peers. [Video](#video), V1-V6. |
| Input | Ordered set-1 scan bytes; a separate BIOS-style editor queue; two joystick count/button deliveries | input; menus/high_scores and session through input. [Input](#input), I1-I3. |
| Audio | Ordered OPL writes/status; calibration measurements; PIT programming, timer/IRQ delivery and wait progress | audio units and timer. Logical music-clock arithmetic stays native. [Audio](#audio), A1-A4. |
| Time and pacing | Serialized event opportunities at explicit cuts; presentation/audio pacing; diagnostic noncompletion | Wait, input, timer, demo and session clients. [Time](#time-pacing-and-delivery). |
| Files and resources | DOS-style score-file operations; stable borrowed resources and live reads | high_scores, pictures, session, resource views and rendering/audio consumers. ICE remains an engine peer. [Resources](#files-and-resources), F1-F5. |
| DOS lifecycle | Virtual vector/interrupt-frame services; critical-error fail; video query/set and terminal exit | input, timer, adlx_lifetime, video_dos, lifecycle. [DOS services](#dos-lifecycle-services); [sequencing](#lifecycle-and-session-sequencing). |
| Random seed | DOS-time-shaped reply at the seed point | random, called by lifecycle; recurrence remains native. [Seed](#random-seed). |

The detailed sections cite each obligation. The Sound Blaster digital path is unreachable in
the shipped program; its optional API-compatible services are separated in A4. The four
external hooks remain unexplained literal near RETs, not new port callbacks.

## Conventions and common call rules

Names such as `video.read` below are **service roles**, not newly implemented functions.
Current units emit their own typed requests; bridges still bind them to the literal machine.
Here "DOS bridge" means that retained register/memory/interrupt calling shell. The SDL host
emulates those DOS services; it does not install real DOS interrupt vectors in the host OS.
An engine peer (collision, drawing, ICE, RNG, timer accounting, music interpretation) is not an
OS service merely because a bridge calls it. Preserve those accepted algorithms; replace only
their hardware/resource/delivery capabilities.

`u8/u16/u32` mean exact unsigned bit patterns; `s16` means the signed interpretation of a raw
word, not a wider host integer. Arithmetic wraps where the producer specifies. Cursor wrap
occurs after an operand; a two-byte operand may have a contiguous high byte beyond FFFF.
Opaque resource/buffer identities replace segment values in an ordinary native API. Their
bindings must retain alias identity and lifetime; they must not become independent copies.
Sources: `video_dos.interface.effects`, `render_primitives.interface.inputs`, `ice.interface`,
`far_copy.interface`, `actor_types.assumptions`, `level_view.interface.projection`.

**Common call rule:** consume each request synchronously, publish its preceding writes before
calling, and import permitted service mutations before producing the next request. Do not
snapshot a whole frame, callback list or future operation sequence across mutable service
cuts. Game callbacks run serially on the game thread; no certificate authorizes arbitrary
mid-operation game-state mutation from an SDL/audio thread. A normal API result word, including
FFFF or a signed negative word, is distinct from the C bridge's `int` transport status:0 means
ordinary completion, nonzero stops at the current prefix. Do not invent rollback/cleanup on
failure. Sources: `adlx_music.interface.preconditions`, `adlx_sections.interface`,
`demo_presentation.interface.effects`, `hud.interface.effects`, `input.interface.preconditions`,
`high_scores.interface.preconditions`. Shapes below are refined by the cited public headers
where certificate prose does not enumerate C member types; the certificates do not define one
shared binary ABI.

Aliases used in tables: VD=video_dos, RP=render_primitives, PP=player_physics,
WW=water_weather, HUD=hud, DP=demo_presentation.

Certificate citations use `name.field[index]`, referring to `metadata/closure/name.json` at the
commit above; indexes are zero-based. Host citations name the actual function read. Host code
observations are distinguished from certificate obligations throughout. No evidence counts or
status promotions are implied.

## Video

### V1. Stateful register transactions

**Callers:** video_dos, render_primitives, water_weather, hud and player_physics, directly or
through their retained pixel shells. **Shape:** current bridge `platform_out(u16 port, unsigned
width, u32 value)` consumes width 1 or 2, low byte first at consecutive ports; `platform_in`
returns a zero-extended byte in `u32` for supported reads. A semantic backend may instead expose
typed register-selection/read/write transactions, but must retain index and data ordering.
Source: `video_dos.callees.services`, `render_primitives.callees.services`,
`water_weather.interface.effects`, `hud.interface.effects[1]`, `player_physics.interface.outputs`;
signature/transport refinement: `c/platform.h`, `c/platform.c:platform_in/platform_out`.

**State:** four 64KiB planes; four latch bytes; sequencer index and low 4 map mask; GC index,
read plane, read mode, compare/care, write mode, rotate/logical function, set/reset enable/value,
bit mask; CRTC index/registers/start/line compare; attribute index/data phase. A 3DAh read also
resets attribute phase in today's machine backend. Read-modify-write requests require the live
old register byte, not a reset default. Source: `video_dos.interface.inputs[1]`,
`render_primitives.interface.effects`, `player_physics.retained[6]`,
`water_weather.retained[6]`; concrete state refinement: `c/platform.c:in/out_byte`, `c/memory.c`.

**Today / modern:** shared `c/platform.c` and `c/memory.c` implement this state for the SDL host;
SDL itself does not implement VGA. A modern software/GPU backend may implement equivalent
transactions, but must not reset inherited controls at every draw, map mask 0 to all planes,
or treat register writes as independent final values. Host implementation: those two files;
obligation: `render_primitives.retained[2..3]`, `hud.interface.effects[1]`.

### V2. Aperture reads and writes, collision samples

**Shape:** ordered `read(buffer,u16 offset)->u8` and `write(buffer,u16 offset,u8)->void`; word
operations are two ordered contiguous byte operations. Collision request is a selected read
plane plus `PlayerCollisionProbe {u16 pixel_x,pixel_y,columns,rows}`; rows/columns are wrapping
relative cell offsets, with fixed 96-cell rows. The service returns the ten full sample bytes
or their defined full-byte OR; physics consumes bit 7, while the exported sampler retains its
whole-byte result. Sample offsets are 0,3,5,720h,723h,725h,240h,245h,480h,485h. Read all ten in
order, including a hit on the first byte. Sources: `player_physics.interface.inputs[2]`,
`interface.outputs`, `interface.effects`, `retained[5..7]`; shape: `native/player_physics.h`.

**State/order:** each physical VGA read loads all four latches, then returns selected-plane or
compare/care-mode data. Writes consume existing latches and controls; writes do not implicitly
read the destination. Collision uses the **background**, never the visible page; plane selection
is not restored. Publish player/world writes before the next probe. Transparent sprite zero
causes neither destination read nor write. Sources: `player_physics.interface.effects`,
`retained[6..7]`, `render_primitives.retained[1]`.

**Today / modern:** `c/memory.c:ugh_read/ugh_write` supplies these semantics and the SDL host
reads its planes for display. An indexed image may be a presentation cache, not the sole
collision/storage authority. Preserve index bits 7/6 independently of RGB colors. Do not replace
the asymmetric left/up repeated probes with a geometric sweep, or early-out the ten reads.
Sources: `player_physics.retained[5..7]`, `water_weather.interface.effects[0..1]`;
host: `host/video.c:host_render`, `c/memory.c`.

### V3. Drawing and copy transactions

| Service / callers | Exact producer request | Required transaction |
|---|---|---|
|Sprite resource/pixel draw — render_primitives; actor_render, hud, menus, demo_presentation use that peer|Sprite ID u16; raw X/Y u16 interpreted signed for placement; directory `{u16 offset,u8 width,u8 height}`; source/destination cursors u16; mask/value u8|Column-major source, transparent-zero skip, native shade/mask decisions; do not clip. Zero dimension byte means 256. Source: RP.interface.inputs/outputs, RP.retained[0..1]; shape: native/render_primitives.h.|
|Restore rectangle — render_primitives; actor_render, menus, water_weather, player wrappers|`{u16 x,y,width,height}` plus background/draw bindings; each row `{u16 source,destination,count,source_end,destination_end;u8 backward}`|Whole cells, no edge masks; ordered source-read then destination-write; force forward direction per row; mode 1 during copy, clear only write-mode bits afterward. Zero row height means 65536 rows. Source: RP.interface.effects, RP.retained[2].|
|Save draw background — render_primitives|Same copy request, raw u16 count and direction byte|Honor full page bindings, incoming direction, zero-count REP semantics, overlap and per-word ordering. No snapshot memcpy. Source: RP.retained[3], RP.interface.effects.|
|Water mark / rain restore / frame tail — water_weather|`WeatherAction {kind,field;u16 value,position}`; raw u8 plane masks; five u8 frame colors; frame recipe 0..2|Mark:80 descending live background read/writes under bitmask 40h/ROP10h, then prescribed resets. Rain: latch-copy with bitmask 0, inherited map/read/write controls, then maskFF. Frame recipes issue 320 cells in order and final maskF. Source: WW.interface.inputs/outputs/effects, WW.retained[6]; native/water_weather.h.|
|Timer-bar pixel writes — hud|Live mask-table u8, wrapping cell u16, color u8; rows 0/96/192; preceding-cell count u16|No screen read. Partial cell precedes full-mask descending fill; restore maskF; do not force a GC mode or refresh latches. Source: HUD.interface.inputs[2], effects[1], retained final item.|
|Chunky upload — video_dos; pictures calls that peer|Borrowed indexed source, source/destination u16, count u16, direction|Masks 1,2,4,8 for successive source bytes; advance destination once per four; count 0=65536 groups; final mask 15. Source: VD.retained[4]; native/video_dos.h.|

Here and below RP=render_primitives, WW=water_weather, HUD=hud, VD=video_dos certificate names.
The shorthand is a field citation, not a different source. Sprite/rectangle/rain operations
deliberately address physical A000 with page offsets; save/water tails honor full buffer
bindings. Do not generalize either convention to every primitive. Sources: RP.interface.inputs[2],
RP.retained[2..3], WW.interface.effects[1]. Today's bridges execute these transactions through
V1/V2; modern batching is permitted only if replies, live overlap, final latch/control state and
the order of observable writes remain the same. No pixel service may mutate unrelated player,
actor or HUD arrays while a request is outstanding. Sources: RP.interface.preconditions[0],
HUD.interface.preconditions[0], WW.interface.preconditions[0].

### V4. Pages, display start and presentation

**Callers:** video_dos; render, water, physics and presentation clients borrow these same cells.
`VideoPages` contains raw u16 draw/display/background/fixed offsets, playfield height and copy
count. These are **byte offsets per plane**, not pixel pointers or interchangeable SDL textures.
Configure changes offset words, not buffer bindings. Gameplay initial fixed/display/draw/background
are 0/0A88h/5A08h/A988h, height 192, copy count 4800h; picture values 0/0/3E80h/7D00h,
height 200/count 3E80h. Configuration tail-swaps draw/display. Source: VD.memory.pages/meaning,
VD.retained[3]; `native/video_dos.h:VideoPages`.

Swap publishes exchanged offsets, waits for **inactive level only**, then writes CRTC start high
before low, restores its machine shell, and signals a frame boundary. The displayed offset is
the new CRTC start. Background is saved scenery/collision/restore storage, not "the other display
page"; fixed 0 supports the HUD after line compare. Sources: VD.retained[5], VD.memory.meaning.
`host/video.c:host_render` already expands four planes with CRTC start, pitch=2*CRTC[13h] and
line compare into320x200 RGB; `host/main.c:boundary` presents/persists scores. A new backend may
present on its own window system, but must not couple a game page swap to an extra game tick,
rewrite borrowed page fields, or discard offscreen/background storage. Sources: VD.interface.effects,
RP.memory.borrowed, PP.retained[7]; current host functions above.

### V5. Palette/DAC

**Callers:** video_dos; pictures, menus, high_scores and demo_presentation call palette peers.
Requests are raw u8 index/component or a contiguous sequence of RGB bytes; fade factor is raw u16,
not float. Native scales `AH(low16(component*factor))`, no saturation; backend DAC masks output
to 6 bits. Source: VD.retained[0]; shape: `native/video_dos.h:VideoScaled/VideoPaletteRange`.

Keep DAC index u8 and component phase 0..2 between calls.3C8 sets index and resets phase;3C9
stores R/G/B and auto-increments index after B. Base upload covers 256 entries; fades cover 0..216.
Blacken sets index once, then eight batches of 32 triples separated by waits; do not reset the
index between batches. Fade steps are inclusive 0..256 and 256..0 by 4, with the original service
cut and live-factor behavior. Source: VD.retained[0..1]. Pictures copy their own 768 already-RGB6
bytes without shifting; ordinary game palette duplication reads only its first 384 bytes and
writes two halves. Sources: pictures.retained[1], VD.retained[2], VD.memory.palette.

Today `c/platform.c:out_byte` keeps phase and masks; `host/video.c` expands 6-bit channels for
SDL output. A modern renderer may replace that final RGB conversion; it must retain palette
indices for collision/water, raw fade arithmetic, ranges and component order. No sRGB fade,
whole-palette fade, channel clamp before the native multiplication, or index deduplication is
authorized by those contracts.

### V6. Retrace and input waits

**Callers:** video_dos, input, pictures, menus, high_scores, demo_presentation and drawing peers.
`wait_level(active:bool)->status` tests current bit 3 of a delivered status u8; active/inactive
are levels, not invariably edges. Next=inactive then active; Through=active then inactive.
Counted wait takes raw u16 N; zero means 65536 Next waits. Active-entry delivery runs even when
already active; inactive has no corresponding active-entry service. Stuck hardware has no DOS
timeout; literal adapters have diagnostic poll bounds. Event backend must wait or report a
delivery failure, not fabricate success. Sources: VD.interface.inputs[2], preconditions[2],
retained[6], uncertainty[2].

Two blocking-input peers deliberately differ. `WaitForInputOrRetraceTimeout(u16 remaining)`
discards an initial change, then scan, buttons, Next and decrement; button/expiry yields 39h,
otherwise packed change/scan, with live remaining count. `WaitForScanChangeOrJoystickButton`
discards its initial change, then Next, buttons, service/scan, with no caller count. Thus their
button/key precedence and first wait are not interchangeable. Sources: VD.retained[7],
input.retained[7]. Current SDL host feeds a virtual 0/8 status waveform and services named poll
sites; it does not measure monitor retrace. A modern event loop may replace polling while
retaining the level/sequence/count and input-order distinctions. Host: scenario_fixture,
host/main.c:service; no certificate fixes a refresh frequency.

## Input

### I1. Scan-byte delivery and I2. BIOS editing keys

**Callers:** input owns scan matching; menus/high_scores use its waits and separate BIOS editing
services. IRQ request is one raw u8 scan; prefixes and break bytes are separate deliveries, not
preclassified actions. Native input owns previous/current/change, sequence candidate/index and
word commands. Current IRQ reads 60h then sends 20h EOI; it neither chains the old keyboard handler
nor queues a BIOS character. No 61h acknowledge toggle should be invented. Source:
input.interface.inputs/outputs, input.retained[0..2], input.callees.services.

Delivery must respect installed handler, interrupt enable/mask and explicit service cuts. Install
and restore flush BIOS head to tail; a new backend must prevent held/released events from being
reinterpreted across a mode switch accidentally. For compatibility the vector operation and
queue flush remain observable, not merely a new function pointer. Sources: input.interface.effects,
retained[7], callees.services. Host: main.service and input.host_live_interrupt.

Editor service is `peek()->{available:bool,key:u16}`, then `read()->{status,key:u16}`; DOS BIOS
convention is AH scan/AL character. Peek does not consume. ASCII classification, uppercasing,
backspace/capacity and default-name/password decisions belong to native high_scores/menus;
do not replace them with a Unicode text widget. Sources: high_scores.interface.inputs[2],
retained[4..5], menus.retained[2]; concrete request/reply: their bridges' INT16 AH1/AH0 calls.
Keep this queue distinct from the raw scan stream. `host/input.c` has both queues, set1 mappings,
E0 prefixes, repeat/make/break input and release-on-focus-loss; BIOS mode uses an ASCII-oriented
queue. It does not supply arbitrary Unicode editing, which is not part of this contract.

### I3. Joystick measurement/buttons

**Callers:** input calibration/sampling/mapping; menus/control selection and waits consume the
same owner. Preferred request/reply is raw u16 x/y counts for each of two sticks, presence word
and two independent active-high button-mask groups (30h/C0h), retained as raw u16 button words.
Do **not** supply only up/down/left/right classifications: native computes thresholds and
inclusive signed classification. Sources: input.interface.inputs[1], outputs[1], retained[3..6];
shape: `native/input.h:InputJoystick/InputState`.

A low-level alternative supplies one status u8 per 201h loop delivery and accepts 201h trigger OUT.
Axes are tested 1,2,4,else 8; a detected axis does not decrement the count. Limit 0 means 65536 empty
decrements. Disabled/unlatched axes use the live limit. Button groups come from independent
reads. Counts must use consistent calibration/sample units. Native computes ceil(n/2),
low16(n+floor(n/2)), low16(2*n), unsigned maximum after wrap, then signed direction comparisons
with low-direction precedence; absent/stale fields and second-sample overwrite rules remain.
Sources: input.retained[3..6], interface.outputs[1].

Today's SDL gamepad supplies **keyboard** E0/arrows/RCTRL/F1 using a host threshold; it does not
populate live joystick counts/presence or implement two live sticks. Scripted 201h waveforms do
exercise the DOS timing adapter. A future live joystick backend may synthesize deterministic
virtual counts around calibration, but must specify their units and preserve the game's
arithmetic instead of silently using the gamepad deadzone as the game's decision. Host:
input.host_input_pump/host_gamepad_init, scenario.host_wave/scenario_load_frame.

## Audio

### A1. Ordered OPL writes

**Callers:** adlx_main/effects, allocation, sections, music, voice and lifetime. Request is
`AudioRegisterWrite {u8 reg,value}` in an ordered list (u16 write_count for the voice/interpreter results); reply is
synchronous completion/transport status. Packed facade input is a raw u16 word:
high byte is the register, low byte is the value (`audio_voice_register`). It is not an
endian-dependent host struct. Sources: adlx_main.interface.outputs[1], adlx_voice.interface,
adlx_allocation.purpose, adlx_sections.interface.outputs; shape: native/adlx_main.h,
native/adlx_voice.h.

Keep OPL address latch u8 and register file, plus synthesis phase/sample time. Current bridge
writes 388h index then 389h value for each event. Preserve duplicates, bank/order and intervening
timer/service cuts; a final register map is insufficient. Examples include frequency A0 then B0,
carrier-before-optional-modulator levels, and the instrument's intervening 01h write. Sources:
adlx_main.retained, adlx_voice.retained[4..5], adlx_main.memory.writes.

`host/audio.c` already forwards data writes to pinned Nuked-OPL3, generates 48kHz stereo signed 16
samples on the game thread and queues SDL consumption; the consumer never mutates game state.
A modern backend may change audio-device buffering/rate conversion while retaining the logical
OPL event order and deterministic relation to game time. It must not run game timer/fade/Tick
callbacks on the audio callback thread. Source obligation: adlx_music.interface.effects,
adlx_main.interface.preconditions[0]; host source: host_audio_out/advance.

### A2. Probe, I/O delay and calibration delivery

**Callers:** adlx_lifetime, adlx_voice; optional digital peers. OPL status replies are raw u8.
Probe first requires status&E0h=0; second requires nonzero, not equality C0h. The platform may
provide deterministic emulated capability responses instead of probing real hardware. Source:
adlx_lifetime.retained[0..1].

Calibration service delivers interrupted **u16 CX remainder and u16 DX progress**, marker and
vector-service results. Begin acknowledges PIC before installing Finish; Finish acknowledges
before restoring the saved vector, stores raw CX/DX, then forces CX1/AL1 while retaining DOS AH.
Native does no Hz conversion or division. Progress includes its original bias/wrap. A modern
backend must explicitly provide a virtual measurement contract; measuring the SDL thread's
speed is not an equivalent substitute. Sources: adlx_lifetime.interface.inputs[2..3],
outputs[2..3], effects[1], preconditions[2], memory.calibration.

Delay accepts factor u8 and calibration u8, returns `AudioIoDelay {u32 iterations,u8 overflow}`;
zero product means 65536 iterations and the product's overflow/flags remain in compatibility.
CPU-spin elapsed time is not a portable music clock. Hardware backends may enforce actual OPL
spacing rather than burn DOS loops; virtual backends need not invent timing events in these
state-only loops. Sources: adlx_voice.retained[5], assumptions[2], adlx_main.assumptions[3];
native/adlx_voice.h. Host scenario_fixture currently installs virtual measurement IRQs and
scripted OPL probe bytes; it has no native hardware-speed measurement.

### A3. Timer delivery, fade waits and the music clock

**Callers:** timer accounting is native; adlx_lifetime installs playback, adlx_music schedules
fades, main/effects change periods. Register takes typed callback identity and u32 interval in
**PIT clocks**; admitted native registration yields an integer handle, retained publicly as raw
u16 even byte-offset identity. Remove/set take that identity; set takes u32 interval. Hardware
programming takes low u16 divisor (zero encodes 65536), separately from full scheduler quantum u32.
Sources: timer.interface.inputs/outputs/machine_shell, timer.retained[4]; native/timer.h.

Preserve installed state, saved external vector binding, countdowns/intervals/due/handle maps,
PIT low/high-byte phase and programmed divisor. Account all slots using the old quantum;
reload due once; publish the next quantum before callbacks; consume due in descending slot
order one at a time, re-reading after callback mutation. Never snapshot/sort a due list or
"catch up" with repeated reloads. Preserve stale due bits, wrong-stride compaction and broken
handle mapping on the admitted boundary. Unknown/mixed callback fragments are not permission
to call an arbitrary host pointer: retain compatibility or surface unsupported behavior.
Sources: timer.interface, timer.retained[0..5].

Today TIMER install/restore/chain and machine interrupt frames remain platform/L1 services.
The native callback identities include BIOS-chain, fade and ADLX playback; saved BIOS IRQ is
an external callback. Initialization creates its baseline BIOS-chain slot, not a generic empty
scheduler. Source: timer.native.bridge, interface.projection, callees.boundary; detail refinement:
c/timer_system.c:InstallTimerInterrupt. A modern backend may use a monotonic event queue to
deliver ticks serially, but must preserve this policy and must not reinterpret public handles
as a clean container index or repair the removal bug silently.

`SERVICE_TIMER_WAIT` is an explicit opportunity for timer progress during blocking stop/wait
operations, not "sleep until elapsed wall duration." Reproject after each delivered callback;
ordinary failure stops the caller. Source: adlx_music.interface.preconditions/effects,
adlx_music.retained[1..3]. Host main.service schedules one IRQ quantum at named sites only when
IF/mask/vector permit, using current PIT divisor. It is a deterministic polling policy, not a
free-running OS interrupt source. Its suitability beyond that policy is a backend gap.

The ADLX counter/origin are u32, ticks-per-unit u16; elapsed is
`((ticks-origin) mod 2^32)/rate`, with an explicit divide fault at rate 0. Main/effect deadlines,
Q8 wait math and Tick/guard increments remain native algorithms. This clock is distinct from
PIT period, audio sample time and wall time; rate/period events change real duration without
allowing their states to collapse. Sources: music_clock.interface/retained[0,4],
adlx_sections.interface, adlx_music.retained[6]. `AdvanceGuardedSoundClock` is API-only by
adlx_music.uncertainty[1]; do not schedule it as an invented extra game tick.

Binding caveat: the audio facade preserves shutdown's live-DS latch-store typo and rebinds
child state after every return. A legacy-compatible backend must not silently retarget that
store to a cleaner logical audio field or freeze a pre-call owner snapshot. A fully typed
binding that removes this machine alias needs a separate justification. Sources:
`adlx_facade.retained[1]`, `adlx_facade.interface.effects[1]`, `adlx_allocation.memory`.

### A4. Sound Blaster/digital compatibility — not a shipped-game service requirement

**Unreachable in the shipped program:** startup requests AdLib 1; no sample resource ships and
bank hooks are stubs; DSP probe crosses a far-call/lone-near-RET broken boundary. Do not repair
these barriers to make a sample path run. Sources: adlx_digital.assumptions[0..2],
adlx_samples.assumptions final item.

If an API-compatible digital backend is later required, it needs ordered byte DSP status/data,
u16 sample rate, DMA1 page u8/address u16/count u16, mask/mode/flip-flop state, PIC mask/EOI and
explicit block IRQ delivery. Zero count programs count-1 and means 65536; page crossing is not
corrected. Preserve polling limits/fallthrough writes, mixer byte-versus-pair bug, stale DMA
tail, inherited headers and signed averaging/faults. Sources: adlx_digital.interface,
memory.DMA, retained; adlx_samples.interface. This is not SDL host functionality: host/scenario.c
accepts only none/adlib and host/audio.c outputs OPL only. The separate Python SB fixture is not
an SDL implementation. Do not describe the native host as supporting DSP/DMA because the model
exists in tools/emu.py.

## Time, pacing and delivery

**T1 — game-thread delivery:** native units expose service cuts, not arbitrary concurrent
interrupt safety. IRQ enable/mask/vector state and exact call ordering are compatibility inputs.
A backend supplies retrace, timer or input events at the appropriate cut; normal methods may
block for an event but cannot mutate unrelated state or complete a pending request twice.
Sources: input.interface.preconditions, timer.interface.preconditions,
player_physics.interface.preconditions[3], demo_presentation.interface.preconditions,
adlx_lifetime.interface.preconditions.

**T2 — pacing is outside simulation:** certificates count retraces/PIT clocks and preserve word
arithmetic, never prescribe a monitor refresh or a CPU-speed-derived delta-time update. SDL's
main.service currently assigns 14,268,000ns per active-wait entry, converts PIT clocks using
1193182Hz, and pace_and_audio advances to the maximum of those two virtual timelines. Wall time
only delays/resynchronizes presentation; it does not add/drop/reorder simulated IRQs. This is
the host's chosen policy, **not a certificate-mandated universal frame rate**. Sources:
VD.interface.effects[2], adlx_main.assumptions[3], music_clock.retained[4]; host/main.c:service,
pace_and_audio. A modern backend must choose and document an equivalent event policy; running
all logic once per SDL vsync or deriving ADLX ticks from the audio consumer is not justified.

**T3 — errors/noncompletion:** preserve the distinction between normal reply/error bits,
transport failure, arithmetic fault, literal nontermination and a harness diagnostic budget.
No blanket "return zero," auto-retry, rollback or auto-shutdown policy follows. Examples:
high-score DOS carry errors complete normally; ADLX loader's -1 is true to its wrapper; divide 0
maps to unsupported/fault rather than a fabricated result; stuck retrace may never complete.
Sources: high_scores.interface.preconditions[2], adlx_loader.purpose,
music_clock.interface.outputs[2], decimal.interface, VD.uncertainty[2]. Host has explicit
status/budget/error exits and a wall watchdog; these are diagnostic/application choices,
not recovered DOS timeouts. Source: host/main.c:watchdog/boundary/main.

## Files and resources

### F1. High-score byte file

**Caller:** high_scores. Current DOS requests: open read-only filename bytes `UGH!.HI\0`;
create/truncate with attributes u16=0; read/write `{handle:u16,count:u16=107,borrowed byte buffer}`;
close handle u16. Normal replies have `{failed:bool,value:u16}` (handle/count or DOS code); C
transport failure is separate. Maintain handle mode, position, existence and length across
requests. Sources: high_scores.interface/callees, retained[2..3]; exact DOS register shape:
native/bridge/high_scores_bridge.c.

Format is 107 complemented bytes: five 21-byte rows (14 name/padding,6 ASCII score characters,CR)
then 00 FF in memory; file bytes are XORFF throughout. No header/checksum/validation. Missing/open
failure leaves state unchanged; read failure leaks handle; close failure skips complement;
successful short/zero read complements the whole stale-filled block. Save complements before
create, accepts short writes, **never closes**, and complements again on normal DOS carry
errors; transport failure can stop before undo. Preserve these decisions in native high_scores;
the backend must not pad short reads or manufacture closes. Sources: high_scores.interface.outputs[1],
retained[2..3], memory.name/stride.

Today c/platform.c simulates files/handles; host/main.c loads/saves the simulated bytes to a
save directory, using a temporary file and atomic replacement on persistence. Host rejects a
physical file exceeding its simulated capacity and treats non-missing OS failures as fatal;
that is an extra host policy, not an original format rule. A modern backend may atomically
persist bytes, but must not alter in-call DOS count/carry behavior or trigger persistence only
on Close, since Save does not issue one. Sources: high_scores.retained[2..3]; host scores_load/scores_save,
c/platform.c:platform_interrupt.

### F2. Resource views, F3. ICE, F4. level/sprite/text data

**Callers:** pictures, menus/attract, level_view, actor_types, render_primitives, demo_core,
adlx_loader/interpreters and the gameplay resource consumers. Resource service returns a stable
borrowed byte view/identity and length; no implicit allocation or second persistent owner.
Identity resolution belongs at the binding, not as a dereference of DOS words inside ordinary
native code. Mutations explicitly allowed by a unit must remain live. Sources:
level_view.interface.inputs/preconditions/projection, actor_types.assumptions,
RP.interface.inputs/preconditions, adlx_loader.interface/assumptions.

ICE is an **existing native engine service**, not a second OS codec. Its actual signature takes
source/output byte buffers and `size_t` lengths, returns IceStatus plus `IceResult` cursors,
writes and token count. Full 65536-byte initialized disjoint windows retain the fixed-ring
compatibility; shorter buffers may return TRUNCATED/RANGE with partial writes. BAD_MAGIC is
normal at the bridge; it still causes a picture palette copy. No full-ring alias guarantee is
provided. Sources: ice.interface, pictures.retained[0..2]; native/ice.h. Pictures are four embedded
ICE streams; decoded layout is 64000 indices plus 768 RGB6 bytes at FA00, no inner header. No
picture filename/missing-file branch exists. Source: pictures.interface.inputs[0], retained[1..2].

Level views take raw 26-byte descriptions,320 tile bytes and borrowed platform/actor/enemy arrays
with `size_t` counts. Platform records retain 16 bytes; descriptor geometry is four raw u16 words;
encoded references/reserved fields remain evidence, not host addresses. The immutable closure
domain is the shipped record/order graph, not every malformed list. Stateful loading is owned by session; its live read protocol is S4 below. Sources:
level_view.interface/retained, session.interface, session.memory.owned[0]; native/level.h, native/session.h.

Sprite provider exposes the original directory `{LE u16 bank_offset,u8 width,u8 height}` and four
column-major indexed banks selected by unsigned IDs at 217/298/547. Native text and HUD decide
glyph IDs, widths/advance and raw byte terminators; a platform text renderer must not substitute
host font metrics. Descriptor/animation/demo identities are resolved from the registered resource
set with valid borrowed lifetimes. Do not normalize reserved words, typed geometry into sprite
bounds, CP437 control bytes or palette-index transparency. Sources: RP.retained[0..1],
level_view.retained[1..2], actor_types.interface.preconditions, menus.retained[4..7],
hud.interface.outputs. The demo reveal width byte is explicitly mutable between draws; "resource
immutable" cannot freeze that byte globally. Source: demo_presentation.memory.owned[1].

Today host/main.c:load_data requires a hash-matching rebuilt MZ data image, relocates it into
ugh_mem and uses bridge bindings; no original code bytes are executed. A modern backend may
package decoded resources/typed IDs, provided content, identity, lifetime, permitted mutability
and read ordering stay equivalent. Missing data errors for that new package need a new policy:
they are not DOS "truncated memory." Sources: ice.interface.malformed,
level_view.interface.preconditions, pictures.retained[2]; host load_data.

### F5. Broken external resource hooks

Digital-bank/probe hooks remain literal near-RET control prefixes, not recovered resource
loader specifications. Do not assign them a successful asynchronous loading role. Source:
adlx_digital.callees.services, retained final items, uncertainty[2]. Modern packaged resource
loading for the shipped game should use F2 and explicit admission, not "repair" these hooks.

## DOS lifecycle services

**D1 — vectors/IRQ frames.** Input, timer and adlx_lifetime need get-vector(u8 number)->opaque
callback binding, set-vector(u8,binding)->status and serialized interrupt delivery. DOS binding
is two raw u16 words; native timer targets are symbolic identities/fragments, not host pointers.
Delivery preserves the interrupted context/flags on IRET, acknowledges PIC in the caller's
specified order and respects masks/enable. Source: input.callees.services, timer.interface.projection/
machine_shell, adlx_lifetime.interface.effects[1]. Modern code may use a local callback registry
and virtual enable state rather than install OS vectors, but cannot silently chain IRQ1 or erase
the timer's saved BIOS-chain obligation. Today c/platform.c plus c/dispatch.c virtualize vectors,
PIC and supported interrupt frames; host/main.c schedules their delivery.

**D2 — critical-error fail.** video_dos installs INT24 without saving/restoring its previous
vector; handler returns AL u8=3, temporarily STI before the service-owned IRET frame. No user
retry prompt or invented chain. Modern filesystem errors may feed its fail outcome rather than
install a process-wide DOS handler. Source: VD.interface.outputs[1], retained[8]. Current bridge
and shared platform model implement this; SDL adds no separate error-handler API.

**D3 — BIOS video and termination.** Current retained lifecycle tail queries/saves BIOS mode,
sets mode 13h for setup, restores saved mode on shutdown, then keyboard restoration and DOS4C
exit. BIOS query reply is mode u8, columns u8, page u8; set consumes mode u8; exit code u8. These are
machine-shell shapes, not mandatory SDL display-mode changes. Source: pictures.retained final
item, input.retained[7], adlx_facade.interface; concrete refinement: c/video.c shutdown/startup
shell, c/platform.c INT10/INT21. Modern backend may create/destroy a window and return a typed
termination outcome, but must preserve ordered sound/input cleanup and terminal/nonreturning
semantics. Accepted top-level orchestration is specified in S1 below. Host main recognizes
DOS_EXIT/status, persists scores and closes SDL/audio/input; user window-close instead stops
through a host budget path, an application-specific exit policy, not the DOS Q path.

## Lifecycle and session sequencing

### S1. Startup, shutdown and external-hook reachability

**Caller/shape:** lifecycle emits `LifecycleRequest {LifecycleAction action; u16 argument}`.
Query-video replies are raw words; only the low mode byte masked by 7Fh is saved. Other service
replies complete synchronously or stop at the consumed prefix. The saved mode is one lifecycle
cell, not a second video owner. Current bridge consumes each request before calling its peer;
no failure invents rollback or a shutdown sequence. Sources: lifecycle.interface,
memory.owned[0], retained[0]; shape/order refinement: native/lifecycle.h/.c and its bridge.

Program order is bind the existing world, initialize platform, show startup pictures, configure
gameplay pages, enter the main-menu/attract dispatcher, then the terminal shutdown service if
that dispatcher returns normally. Platform initialization orders:

1. Query BIOS video mode, save its low seven bits, execute the retained FLAGS CPU probe.
2. Install critical-error fail, load high scores, seed from DOS-time seconds.
3. Set mode 13h, configure picture pages, install keyboard handler, calibrate joysticks.
4. Initialize sound with **mask 1 (AdLib only)**, then clear VGA planes.

Sources: lifecycle.interface.outputs[0], callees.services[0], eliminated[0]; precise requests:
native/lifecycle.c:program_actions/initialize_actions and native/bridge/lifecycle_bridge.c.
The CPU probe is retained machine compatibility, not a requirement to execute x86 FLAGS on a
modern CPU. Startup pictures are Play Byte, Bones Park, presenter and title, with 280/280/140/420
retraces. Escape skips the remaining pictures; Q enters shutdown; normal timeout/advance leaves
the installed keyboard handler in place. Source: pictures.retained[4..6].

The terminal DOS service orders `FadeAndShutdownSound`, restore saved video mode,
`RestoreKeyboardInterrupt`, then DOS 4Ch termination. Sound shutdown itself orders
`StopMusicTrack(0x11)` then `ShutdownSoundSystem`. The port may use a typed terminal outcome and
window teardown instead of BIOS/DOS calls, but must retain service order and failure prefixes;
it must not return to the menu after terminal success. Sources: lifecycle.callees.services[0],
retained[0], pictures.retained[6]; native/lifecycle.c:sound_shutdown_actions,
c/video.c:c_DosShutdownTail.

**External hooks are still boundaries.** Fresh startup bypasses them. If the initialized flag
and device word are nonzero, sound initialization first shuts down retained state: device
mask 02h set can reach
`ShutdownSoundSystem -> ShutdownDspPlayback -> GAME:001F`. Terminal shutdown can take that path
too. Do not equate AdLib-only request 1 with proof that all retained-state entries bypass the
hook. The digital probe and bank path retain their other broken far-call/near-RET transfers;
the four 001C..001F entries have no invented loader, callback or probe role. The three shipped
Sound Blaster barriers in A4 remain unchanged. Sources: lifecycle.indirect.retained,
uncertainty[0], adlx_facade.callees.services/retained[0..1], adlx_digital.purpose/callees.services;
docs/roadmap.md lifecycle row; native/bridge/adlx_digital_bridge.c:c_ShutdownDspPlayback.

### S2. Frame request order and publication

**Caller/shape:** session emits `SessionRequest {SessionAction action; u16 index,value,other;
u8 decision}`. Replies reborrow `SessionWorld`: raw u16 fade level/rate, palette reply, player
byte count/count, level/limit/password reply; u8 lives/completion/rain/scan. Requests and replies
are serialized; public world values and retained render histories stay with their existing
owners. Do not replace `PlayerCount` with `PlayerArrayBytes`, or reset stale histories during
binding. Sources: session.interface, memory.owned[0]/borrowed[0]; native/session.h.

At each frame start, signed fade level < 0 exits toward music stop and outcome handling; 0..256
uploads the faded palette then advances fade using the **live returned palette word** and fade
step; a larger nonnegative level waits Next retrace instead. Then the frame orders:

1. Refresh HUD/timer bar; erase players, actors, enemies and items; restore rain if enabled.
2. Advance water; offer the explicit `SERVICE_IO` cut; poll controls; perform the pause poll
   if requested; process Escape and decide whether player movement is enabled.
3. Move players when admitted; update actors, enemies, then items.
4. Draw actors, enemy back layer, players, enemy front layer, items, then actor overlays.
5. If rain is enabled, advance and draw it; draw water; swap/display the page.

Writes preceding a service must be visible before it runs; callback/clobber results are read
before the next request. Keep movement's equality-only continuation against `PlayerCount`;
erase/draw use the byte-count boundary instead. No backend frame batching may substitute a
single whole-world snapshot for these cuts. Sources: session.interface.outputs[0],
preconditions[1], callees.services[0], memory.frame[0]; native/session.c:session_next/acknowledge,
native/bridge/session_bridge.c:c_RunGameFromPassword; docs/roadmap.md session row.

### S3. Pause polling and diagnostic limits

After control polling, scan 19h (P make) enters the pause protocol. Repeated
`PollKeyboardScanChange` replies must first yield 99h (P break), then any byte with its high bit
clear (`(scan & 80h) == 0`), then any byte with it set (`(scan & 80h) != 0`). Those later
make/break tests do **not** require the same key and
do not test the change byte. There is no joystick-unpause test, frame advance or retrace wait
inside these loops. Each keyboard poll still provides its `SERVICE_IO` opportunity, so a port
must deliver scans while paused rather than only when it presents a frame. If the required
input never arrives, the game keeps polling; do not add a gameplay pause timeout. Sources:
session.interface/callees.services[0], input.interface.effects, input.callees.services;
native/session.c:SP_PAUSE_RELEASE/MAKE/BREAK and session_acknowledge,
native/bridge/input_bridge.c:c_PollKeyboardScanChange.

The current bridge counts completed page-swapped frames in a u32 private cursor and returns
`UGH_BUDGET` on 100000. It resets that cursor after **each** level initialization, including a
death restart; it is not a whole-session limit. This is the retained translation's verification
guard, not a game timeout, timer expiry or level outcome. A production event policy must not
turn it into automatic game-over; a diagnostic compatibility runner may retain it explicitly.
Sources: session.retained[1], memory.owned[0], lifecycle.retained[1];
native/session.c:session_acknowledge(SESSION_INITIALIZE_LEVEL/SWAP_PAGE),
native/bridge/session_bridge.c:c_RunGameFromPassword; docs/roadmap.md session row.

### S4. Live level-resource reads and initialization

**Caller/shape:** session's loader emits `SessionLoadRequest {action,field,arithmetic;
u16 slot,index,value}`. It receives raw u16 read replies and a symbolic `SessionLoadClass`;
identities are bindings, never dereferenceable host function addresses. Reads, skips, native
arithmetic, stores and callback-role publication are interleaved, not a speculative bulk parse.
The platform supplies the requested bytes/words and resource identities; level construction
remains native. Sources: session.interface, indirect.classification, memory.owned[0];
native/session.h:SessionLoadRequest/SessionLoadRecord and native/session.c:session_load_*.

The current binding selects the mode-specific level-order table with low16((PlayerCount-1)*2),
then the level entry with low16(level*2). It copies the 26-byte descriptor **backward**, thirteen
word reads/stores at offsets 24 down to 0. It decodes the borrowed compressed tile-map resource
through the existing ICE peer and copies 160 words from the selected scratch offset, honoring
incoming direction/cursor wrapping. Both players' seeds are initialized even in one-player
mode. Sources: session.interface.preconditions[0], memory.owned[0], level_view.interface;
native/bridge/session_bridge.c:c_LoadCurrentLevelState; docs/roadmap.md session row.

Platform, actor and enemy lists then supply sequential live LE u16 words; platform termination
tests the first word's sign bit, actor/enemy termination tests FFFFh. Descriptor callback reads
use offsets 8 or 16 (stone); spawn/height replies come from the **current** platform arrays.
The Triopterus/default enemy path performs a fresh read of the prior list word, not reuse of
the first speed sample; unknown enemy identities take that default path. Native skip counts,
word wrap, scalar scaling, reserved fields and store order remain exact. Do not repair a bad
record into an empty list or invent a file-error branch: completion requires valid resource
bindings and finite prefixes. A resource pack may validate at admission under a separately
chosen missing/malformed-data policy. Sources: session.interface.preconditions[0],
indirect.classification, level_view.interface.preconditions;
native/bridge/session_bridge.c:sq_load_lists/c_LoadCurrentLevelState.

Display initialization then calls load state, level introduction, plane clear, blacken,
palette duplication, tile map, save background, page swap, restore playfield, HUD borders,
enemy updates, actor updates and erase-history reset, in that order. Do not transfer page,
water, input or render-history ownership to the resource provider. Sources:
session.callees.services[0], memory.borrowed[0], interface.preconditions[1];
native/session.c:session_display_* and native/bridge/session_bridge.c:c_InitializeLevelDisplay.

## Random seed

**Caller:** random seed entry, invoked by startup; gameplay consumers call the accepted RNG,
not the OS. Time request returns `RandomDosTime {u8 hours,minutes,seconds,hundredths}`. DOS
AH2Ch returns CH/CL/DH/DL. Native overwrites **only the high byte of word 0 with seconds**,
preserving the remaining 56 state bits; no recurrence step occurs on seed. Source:
random.interface.inputs/outputs/seeding; native/random.h.

Later random requests take raw u16 bound and return multiply-high u16 while updating all four u16
words; bound enters the recurrence and even 0/1 advances it. This is an engine peer, not a
replaceable system random service. Sources: random.interface.recurrence/range_reduction,
retained[0..2]. Host scenario_fixture currently supplies a fixed DOS-time script; live mode
does not replace AH2Ch with the OS clock. A modern backend may supply real or replayed seconds
at the existing seed point, but cannot hash a timestamp, fully reseed, use modulo reduction or
substitute a standard PRNG while claiming the same contract.

## Compatible differences in certificate wording

These exact statements apply to different operations or domains. They constrain the service
binding together; none grants a global simplification. The reconciled audio boundary fields now
name their migrated owners and are not contradictions.

| Classification | Exact statement A | Exact statement B | Combined constraint |
|---|---|---|---|
| Different buffer-binding domains | "Full pointer segments remain backend bindings: water/page selection uses existing pointers exactly; sprite and rectangle output deliberately use physical A000 with page offsets only." (`render_primitives.interface.inputs.2`) | "Rain restore copies live physical A000 background cells to draw cells under GC bit mask0, leaving inherited sequencer map mask and write/read modes intact; final maskFF. Rain draw and both restore routines deliberately use physical A000 and page offsets, whereas water surface tails and marking honor full original segment:offset pointers." (`water_weather.interface.effects.1`) | Not a contradiction: bind per operation. A universal full-pointer blitter and a universal fixed-A000 blitter are both wrong. |
| Immutability is per operation | "Ordinary disjoint code/data, stack and borrowed resources. Pixel services are synchronous and do not mutate player simulation/caches or resource descriptors while the primitive executes." (`render_primitives.interface.preconditions.0`) | "Fade callback: level/step conditional writes. Reveal callback: exactly one byte through the original mutable far pointer, with original DI direction/wrap." (`demo_presentation.memory.owned.1`) | No simultaneous-mutation contradiction: the reveal width is mutable between draws. Resource-provider immutability must exclude this byte; do not cache a forever-immutable sprite width. |
| Palette-width domain | "Palette is768 bytes atFA00, copied384 words verbatim with no shift to6bits. Shipped values already0..63." (`pictures.retained.1`) | "Palette scale is AH(low16(byte*factor)), no saturation/mask; raw eight-bit outputs are masked to six bits by DAC service." (`video_dos.retained.0`) | Compatible: RGB6 describes shipped data; the arithmetic/DAC interface still admits raw8-bit values. A global clamp or another shift changes the contract. |
| Different units, not a common clock | "AHDR ticks/unit scales an ADLX counter. PIT period events change real duration; playing, descriptor active/repeat bits, loop enable, origin and deadline cannot be collapsed into one boolean or wall-clock time." (`music_clock.retained.4.reason`) | "Register: typed TimerCallback; interval in PIT clocks" (`timer.interface.inputs.1`) | Keep logical ADLX tick/rate, PIT clocks and host/sample time distinct. No certificate authorizes replacing them with one elapsed-millisecond value. |
| Two bounds on resource access | "for smaller ordinary file buffers every L1 access must be within available storage; RANGE/TRUNCATED are native safety extensions, not DOS errors" (`ice.interface.preconditions.3`) | "No file open/read/length or missing-file branch: four resources are embedded. Raw absent/truncated memory is not rejected by a picture-length check." (`pictures.retained.2`) | Native small-buffer safety is an extension, not the historical picture parser result. The port must choose its compatibility/profile policy explicitly; missing package data does not become a successful stale palette by default. |

## VGA: shipped requirement versus literal-compatible edges

The certificate contracts are broader than shipped reachability. "Only edge evidence" below
means **not established as a shipped dependency**, not proof that it is unreachable. The
"Inherited VGA write state" row reports the close-stones-13 census (C/D observation over the
maintained scenarios, `verif/vga_state_census.py`); it is not a whole-game invariant.

| Obligation | Required for the shipped game | Edge-only / remaining reachability question |
|---|---|---|
|Four planes, page offsets, hidden background and HUD line compare|Yes: RP background restores, PP background collision, WW rain/water and VD swap/configuration use these stores. A sole320x200 visible index array loses data.|Arbitrary alternate segment bindings and physical aliases are admitted compatibility domains; do not require them to display canonical resources. Sources: VD.memory.meaning, RP.interface.inputs[2], PP.retained[7], WW.interface.effects[1].|
|Latch copies|Yes: rectangle restore selects mode 1; rain restore uses bitmask 0. Both require source-read to load four latches before writes to enabled planes.|Odd overlap, mask 0 reads and arbitrary nondefault compare/write controls extend this operation; existing certificates retain them. Sources: RP.retained[2..3], WW.retained[6].|
|Collision index reads and final latches|Yes: physics consumes background bit 7 and all ten reads; RGB/geometric collision cannot replace that contract. Water uses index bit 6.|Full 80-bit reply and arbitrary read-mode compare/care states are broader than physics's bit 7 decision. A shipped later dependency on every such bit/state is not asserted. Source: PP.interface.inputs[2], effects[1], retained[6].|
|Inherited VGA write state|Measured (close-stones-13, HEAD a5e9a1e: all 20 maintained scenarios plus `random-rain`, 601,950 service entries over 17,952 flips). At every reached pixel/copy entry the writer logic is canonical: write mode 0, read mode 0, bit mask FFh, rotate/function 0, set/reset disabled. Not constant: the read-map select persists as 0..3 (for example the collision sampler at departure frame 114 enters with read map 1), and the three water-frame services enter with map mask 1 set by DrawWaterSurface. Copies (save, rectangle, rain restore; 75,919 calls) never overlap and only use latches loaded inside their own call, but SaveDrawPageBackground (67/67 calls) and 8 rectangle restores read cells written earlier in the same frame. Physics consumes collision bit 7 only; toggling bits 0..6 leaves all 21 traces unchanged, clearing bit 7 diverges. Real off-allocation accesses and 16-bit address reductions occur (sprite at departure frame 292 writes A000:59CD, before draw page 5A08); no word or access stream crosses A000:FFFF.|A port may use a typed indexed-pixel backend under this explicit game-path assumption: 64 Ki cells of four index bytes, direct lane stores, live four-lane copies, the OR 40h water mark, and an explicit read plane and write-lane mask. It must keep both page layouts with padding and unclipped word destinations, read current (not frame-start) copy sources, keep index bits 6/7, and keep the DAC batch position across waits. Not covered: 5/81 level records initialized (1P 1, 2, 4, 43, 59; 2P 1); 5 services unreached (DrawHudDigitAndAdvance, RestoreTileBackground, UploadBasePalette, WaitThroughVerticalRetrace, FailDosCriticalError). The broader per-operation contracts (HUD.interface.effects[1], RP.retained[1,3], VD.retained[4]) are unchanged and remain the bit-exact profile.|
|Water logical bit marking|Yes: native mark transaction uses live read/modify/write state and bit 40h, then resets prescribed controls. A visual-only translucent water layer omits collision/background effects.|Arbitrary raw colors, masks, phase bytes and foreign buffer bindings extend the literal-compatible edge. Sources: WW.interface.effects[0], retained[0,6].|
|Planar pitch and signed/offscreen addressing|Yes: gameplay uses 96-cell rows, cached collision origins and unclipped placement; picture pitch differs. Retaining only visible pixels discards required backing storage.|An actual FFFF-crossing word high byte outside the aperture, huge raw counts and all corrupt page values are compatibility edges; no shipped need for each extreme is established. Sources: PP.retained[5..7], RP.retained[0], VD.interface.effects[0].|
|Zero dimensions and mutable metadata|Render do/decrement semantics must remain; demo modifies a width byte between draws.|Do not call every zero width "unreachable": the committed certificates do not discharge reachability of every reveal-width value. Huge malformed heights/counts have edge evidence. Sources: RP.retained[1], DP.memory.owned[1].|
|DAC phase across waits|Yes: blacken deliberately keeps its index/component state over batches; indexed colors are live during fades.|Raw components>63 and pathological factor/count words extend the edge; backend still masks DAC input after native arithmetic. Sources: VD.retained[0..1], pictures.retained[1].|

DP=demo_presentation; PP=player_physics. A modern renderer need not expose VGA ports, but a
semantic transaction backend still needs equivalent persistent plane/control/latch state for
these obligations. A simple framebuffer plus ad hoc memcpy is not the consolidated contract.

## Existing SDL host: coverage and gaps

| Area | Present implementation read | Gap / boundary |
|---|---|---|
|Video and planar transactions|host/video.c presents c/memory.c's four planes; c/platform.c keeps registers/latches/masks/DAC. CRTC pitch/start/split are used.|A direct typed pixel backend still needs to replace machine bindings; SDL rendering alone is not that backend. The VGA census observes only canonical inherited writer modes on the shipped path (C/D); hidden storage is still required.|
|Retrace/pacing|scenario_fixture supplies 0/8; main.service counts active-wait entries; pace_and_audio follows virtual timelines and paces with SDL.|No physical monitor-retrace service. Policy is explicit deterministic polling, not a free-running/refresh-independent scheduler specification.|
|Keyboard/BIOS|Set1 queue/E0/make/break and BIOS queue; vector-mode switches clear queues; held-key releases on focus loss.|ASCII-oriented editor path; no semantic Unicode API. Queue/IRQ placement still depends on virtual vectors and named cuts.|
|Joystick|Scripted 201h waveforms; live first gamepad maps to keyboard scans.|No live two-stick count/presence/buttons backend. Keyboard emulation is usable input, not implementation of I3.|
|OPL|Nuked-OPL3 state, ordered register data, generated stereo samples, SDL stream/WAV.|No exact physical OPL timing/analogue promise; no game callbacks on audio thread.|
|Timers/calibration|Virtual IRQ placement, PIT phase/model and scripted measurement IRQs; real native timer accounting behind bridges.|No OS interrupt installation required. A general modern event scheduler and calibrated-count delivery policy remain design work.|
|Digital audio|None in host/audio.c; scenario parser rejects card sb.|Intentionally unnecessary for shipped program; optional compatibility backend remains separate Python model/API work.|
|Scores|DOS byte-file model, save-dir import and atomic replacement, preserved raw format.|Fixed file/handle capacities and fatal OS I/O policy are host extensions; native save does not close.|
|Resources|Hash-checked rebuilt MZ data, relocation, existing native codecs/views/bridges.|No independent portable resource pack/provider yet; meaning/identity/mutable metadata must survive extraction.|
|Lifecycle/faults|Virtual DOS/BIOS interrupts, supported IRET frames, statuses, watchdog, host cleanup.|Still machine-shaped and Windows-specific in places (_mkdir/MoveFileEx/CNG/watchdog); accepted lifecycle/session requests still bind to that model.|
|Random seed|Fixed scripted DOS time in scenario_fixture; accepted native RNG remains.|No live system-seconds provider currently; introducing one changes runs intentionally at the documented seed point.|
|Build/check identity|hostbuild receipt stores variant and executable SHA-256; check verifies both before scenarios.|Implemented; changing the --variant label alone cannot check the other build. Sources: lifecycle.evidence_refreshed; host/check.py:require_built_variant.|

Host verification now binds checks to the actual executable: `tools/hostbuild.py` records
`variant` and `executable_sha256`; `host/check.py:require_built_variant` rejects a mismatched
variant or executable digest before running comparisons. Native and literal checks still
require their corresponding builds. This is implemented verification infrastructure, not an
open platform-service decision. Sources: `lifecycle.evidence_refreshed` (host-check fix),
`tools/hostbuild.py:build`, `host/check.py:require_built_variant/main`.

## Decisions for the port layer

These choices remain open; the certificates constrain their observable boundaries.

* **Event scheduling:** use deterministic virtual retrace/PIT events, or a real-time scheduler
  with a documented mapping to them. Either must preserve level/edge sequences, timer phase,
  callback order and synchronous cuts, including delivery during pause; neither may derive
  extra simulation steps from SDL vsync/audio callbacks. The per-level guard stays diagnostic.
  Constraints: video_dos.retained[6], timer.interface/retained, session.retained[1]/interface.
* **Live joystick count units:** synthesize a calibrated virtual count range from modern axes,
  or expose measured/emulated 201h counts. Define common calibration/sample units and presence
  and button replies; leave wrapping thresholds and signed inclusive direction decisions to
  native input. Constraints: input.interface.inputs[1], outputs[1], retained[3..6].
* **Resource pack and missing-data policy:** retain the relocated data-image provider, or
  extract a portable pack with stable identities and explicit mutable metadata. Choose startup
  rejection, a surfaced resource error, or an optional complete-window compatibility profile
  for missing/malformed data; the historical picture path supplies no missing-file result.
  Preserve live loader reads and partial effects; ICE safety errors are extensions, not DOS
  errors. Constraints: pictures.retained[2], ice.interface.preconditions[3],
  level_view.interface, session.interface.preconditions[0], demo_presentation.memory.owned[1].
* **Live random seed:** retain a replay/fixed DOS-time reply, or supply live system seconds at
  the existing seed point. Only the seed word's high byte is replaced; choose neither a new
  recurrence nor a full-timestamp hash implicitly. Constraints: random.interface.seeding,
  lifecycle.callees.services[0]; native/random.h.
* **Optional bit-exact compatibility profile:** keep a full machine-shaped backend alongside
  semantic services, or document a narrower admitted resource/state domain for the port.
  Neither option silently fixes retained bugs. The compatibility profile covers admitted
  aliases, wrap, flags/frames, malformed full windows and optional unreachable digital API
  behavior; the shipped path still needs hidden planes/latches/collision indices. The VGA
  census supports a narrower typed pixel backend for the shipped path as a C/D assumption
  (see "Inherited VGA write state"); adopting it is this decision, and broader level traces
  would strengthen it. Constraints:
  render_primitives.retained/interface, video_dos.interface.effects,
  player_physics.retained[6..7], ice.interface, adlx_digital.assumptions[0..3].
