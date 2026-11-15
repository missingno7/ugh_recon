"""Write the step8-groundwork worker report from completed service receipts."""
from pathlib import Path
import collections,json,subprocess
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'build/workers/close-stones-26'
def read(name):return json.loads((OUT/(name+'.json')).read_text())
def main():
 receipt=read('receipt');assert receipt['result']=='PASS'
 build=read('build');unit=read('unit');pack=read('pack');video=read('video');manifest=read('ugh.manifest')
 classes=collections.Counter(r['classification'] for r in manifest['resources'])
 resolved=sum(r['resource'] is not None for r in manifest['model_bindings'])
 text='''# close-stones-26: standalone service groundwork

**STATUS: done for the requested groundwork.** No game code is linked. No game
world, bridge, certificate, document, host/composition file or maintained verifier
was edited. Other workers' pre-existing dirty files are not credited to this work.
Nothing was committed or staged. The four unexplained external hooks are untouched.

## Deliverables and reproduction

```
python verif/port_services.py --all
python verif/port_report.py
```

The first command builds only port providers/tests and independent hardware/
presentation oracles. Children run serially with 600-second and 8-GiB caps. SDL
dummy audio/video drivers exercise real window/texture and stream creation without
live devices. No download or background helper is used. No default scenario/gate
changes are made. This task needs no certificate promotion or dependent relock.

`port/services.h` is an SDL-independent GameServices vtable. It contains no register
model, memory image or historical address. Provider state is in
`port/sdl/backend.h`. Runtime resource loading uses only the new pack; the rebuilt
executable is read only by the build-time extractor and independent test oracle.
`port/README.md` documents the format, build and pending boundaries.

## Operation correspondence

Operations are synchronous on the game thread. No service rewrites unrelated
world state, rolls back a consumed prefix, or invokes simulation from an audio/
window callback. Renderer/physics/music/codec decisions remain engine peers.

| GameServices operation | Existing typed request / evidence | Backend behavior |
|---|---|---|
| video.control_write/read | video_pages VideoControlRoute and pixel_world PixelControlRoute; video_service_control_* / pixel_service_control_* | Separate index/data transactions, sequencer/GC/CRTC/attribute state, inherited read/modify/write bytes, attribute phase |
| video.read | pixel_service_read(VideoCellAddress, PixelReadRole), video_service_source_byte for indexed storage | Loads all four live latches and returns the full selected/compare-mode byte; source/collision roles distinct |
| video.store/store_word | pixel_service_store / video_service_store_byte/word | Write-lane mask plus GC write mode, rotate/ROP, enable/set-reset and bit mask; no destination read or viewport clipping. Word high byte is contiguous; an unbound crossing retains the low-store prefix then Unsupported |
| video.copy | pixel_service_copy | Source read now, latch write now; next copy sees preceding writes, not a frame snapshot |
| video.water_mark | pixel_service_water_mark | Live read, then CPU value40h under inherited controls; not a software flat-image OR |
| video.control CRTC + present | video_pages page/start requests, video_service_frame_end | Backend presents after the caller's high/low CRTC order. It does not own/swap native page fields or add a game tick |
| video.dac | palette_world PaletteDacWrite SELECT/COMPONENT | Streaming select/component, six-bit output mask, persistent index/phase and wrap after blue. Caller samples source immediately before delivery |
| video.retrace_level | video_service_retrace_level | Returns delivered level, resets attribute phase; no implicit event/time advance |
| video.compatibility | pixel_service_continuation and pixel_service_compatibility_write | Unsupported; step7 pending. No external control-word decoder |
| input.scan / acknowledge | input_service_scan / input_service_acknowledge_scan | Ordered set1 bytes; E0 and make/break remain separate bytes. Queue overflow fails atomically before an E0 pair |
| input.queue / flush | input_service_queue TAKE/PEEK and input_service_queue_flush | Separate editor queue; uppercase ASCII/scan words, no scan-handler duplication; empty is GS_EMPTY. Flush carries its u16 reply, including a nonzero terminal witness |
| input.vector | input_service_vector CAPTURE/INSTALL_HANDLER/RESTORE_SAVED | Opaque provider-issued tokens; install/restore flush both recipients and retire physical holds so stale releases cannot leak |
| input.joystick_start/presence/buttons/counts | input_service_joystick_start/presence/buttons/counts and InputCountsReply | Trigger acknowledgement, two presence/button groups and common calibrated units; counts, latched and remaining words preserve16-bit arithmetic |
| input.pump(SCAN/WAIT) | input_service_poll(InputPollCut) | SDL events delivered only at requested cuts; two gamepads, separate focus state, no direct game command writes |
| audio.opl | AudioRegisterWrite and audio_voice_register's decoded pair | Ordered OPL3_WriteRegBuffered(reg,value) at48000Hz; no batch reordering |
| audio.advance | host/audio.c virtual-time sample accumulation | Exact integer sample remainder; SDL consumes queued PCM, never engine state |
| audio.clock | timing_world logical timer/BIOS external delivery | Calls an explicit synchronous receiver; no extra guard-clock increment. Unsupported without the later engine receiver |
| audio.status/calibration/timer_lifetime | adlx_lifetime capability/calibration witnesses; TimerLifetimeRequest binding/reset/delivery | Typed reply/request shapes retained, including CX/DX-style progress, opaque saved binding and command/low/high bytes; Unsupported, step7 pending |
| time.deliver/suspend/pace | explicit retrace/timer/input cuts; adopted D1; host/main.c two-timeline pattern | Requested order only, independent70Hz retrace/timer timelines, maximum for pacing; no wall-derived game steps or vsync/audio callbacks |
| files.open_scores/read/write/close/persist | high_scores F1 logical handle/count/failure replies,107 raw encoded bytes | Short-read tail untouched; no complement/header added; logical handles retained across Windows atomic replacement, including omitted-close behavior |
| resources.view/mutable_view | resource_catalog tokens, actor/level resource views, D3 | Stable IDs and live canonical byte views; immutable writes denied; same-byte aliases share storage |
| seed.read | RandomDosTime reply at random_seed's existing lifecycle point | Local system seconds or explicit fixed replay reply. No RNG recurrence, full reseed or additional seed point in backend |
| lifecycle.request/binding | lifecycle/terminal provider/video/CPU/error-handler/exit prefixes | Explicit value/result and opaque binding boundaries; Unsupported, step7 pending. No invented external-hook role |

## D1, D2 and D4 details

The event source uses integer rational ticks:70 complete ticks equal exactly one
second. Retrace and timer opportunities have independent counters, as the existing
host has independent timelines; event timestamps/pacing use their maximum. The
engine adapter must pass explicit elapsed deltas to audio.advance. Input/status
requests do not manufacture time. A timer opportunity is not an extra native
music-clock increment: the engine retains scheduler quantum, callback selection,
phase, reborrow and delivery decisions. No global cross-family callback order is
invented here; the caller selects each explicit cut.

Host suspension freezes delivery and shifts the pacing epoch by the suspended wall
duration on resume. No catch-up tick is inserted. Game pause must not call host
suspend: keyboard polling and timer opportunities can continue without a page swap.
This distinction is tested with timer-only progress and a fixed retrace counter.

D2 synthetic discharge counts use neutral1000 and endpoints250/1750, with integer
interpolation over the full signed SDL axis domain. These are common calibration
and sample units, not backend direction/deadzone decisions. Native input still
computes thresholds/ceil/wrap and inclusive signed directions. Counts are bounded
by the requested sample limit; limit0 retains its65536-cycle meaning. Disabled/
absent axes retain unlatched witnesses and the raw limit-based count. Player0/1
presence and30h/C0h button groups remain independent.

D4 supplies the current local system time's seconds byte (or the fixed replay
reply10/20/30/40h). The native engine remains solely responsible for replacing only
the high byte of word0 at the original single seed point.

## Resource pack

`tools/respack.py` first uses cgen's read-only fresh-plain check: rebuilt load-image
and relocation identity, source receipts, TLINK map and TASM symbols. It reads no
assets and never modifies the oracle. Selection is limited to curated DATA objects
and actual assembly db/dw/dd declarations. A declaration overlapping a known ASM
instruction start is rejected. Unlocated declarations or layout gaps fail closed.

The pack has a128-byte version1 header, sorted64-byte entries, SHA256 for the table,
payload and every view, and a deduplicated data payload. IDs1/2/3 encode the exact
resource_catalog kind/index namespaces. Family4 uses checked CRC32 keys over
curated symbolic object/model names. Hash collisions abort extraction; changing a
registered name/partition is a schema review, not silent ID reuse. No image
coordinate is present in the runtime format or generated C admission header.

The extractor generates symbolic ID macros and a required-object C manifest with
class, size, content digest and canonical file-relative alias position. Compile
that header into the eventual executable. The reader checks that exact set before
publishing a usable pack, rejects hidden payload and detached aliases even when
the attacker recomputes the file's own checksums, and denies a writable alias of
an immutable view. Mutable values can then change live; startup hashes are not
misused as invariants over later gameplay.

'''
 text+=f"The pack has **{len(manifest['resources']):,} IDs**, **{manifest['payload_bytes']:,} unique payload bytes** and **{sum(r['size'] for r in manifest['resources']):,} compared view bytes** including aliases.\n\n"
 text+='| Class | Views | Policy |\n|---|---:|---|\n'
 for c,description in [('immutable','Only the explicit60-byte codec data block/subviews and three empty semantic effect tokens'),('mutable','Whole662 sprite records and their aliases; known C startup-flag initializer data'),('opaque_mutable','Other declarations/initializers/resources, including unclassified/padding bytes; no constness from absent model writers')]:text+=f'| {c} | {classes[c]} | {description} |\n'
 text+=f'''
The program model is a may-analysis, not a complete allocation map.
**{resolved} of {len(manifest['model_bindings'])} model names** have unique exact declared-object
starts and receive named alias IDs. The other{len(manifest['model_bindings'])-resolved} receive no guessed extent;
the manifest records the limitation. Base declarations still preserve their known
data, and scratch/library exclusions are explicit. In particular a biased codec
anchor is not treated as a new allocation. This is the same finding the accepted
provider review established.

All initialized game-data records are individually identified initializer/resource
templates, never an address-space snapshot to restore. Raw descriptor/script/
callback transport words remain **opaque data**, not function pointers or a
runtime code-address resolver. Step7 still needs semantic resource facades and
registered callback roles before those records can drive engine control flow.
The generic pack validates identity/content/aliasing, not arbitrary callback
execution or every future native view's semantic admission.

| Excluded object | Bytes | Reason |
|---|---:|---|
'''
 for r in manifest['excluded']:text+=f"| {r['name']} | {r['size']} | {r['reason']} |\n"
 text+='''
The64768-byte zero workspace is an allocation reservation, not a serialized RAM
window. No new codec or scratch owner is introduced. The accepted65536-byte
workspace/audio-flag/752-byte packed-map alias binding remains a step7 owner-adapter
obligation; this pack neither clips nor snapshots an active workspace. Source
initializers for resources and flags are data, not a second live game owner.

Classification verification compares the accepted catalog's semantic policy, not
its changing dependent-lock notes. Concurrent certificate relocks therefore do not
invalidate an otherwise identical pack, while a class/assumption change does.

## Tests and evidence

| Command / check | Result |
|---|---|
| `python verif/port_services.py --all` | PASS; build, unit, pack and video children serial and bounded |
| `tools/respack.py --verify` / Python source roundtrip | Every selected view byte equals the rebuilt plain image; no code/header/RAM reconstruction payload |
| C startup reader | PASS: all IDs/classes/digests/lengths/aliases; readonly denial and live mutable named/catalog aliases |
| Pack controls |13 explicit corrupt/missing controls rejected; all errors identify resource pack failure |
| Input goldens | Recorded A repeat/make/break, E0 arrows/right-control/keypad Enter, editor words/backspace, focus loss, stale release suppression, atomic overflow |
| Joystick | Recorded two-pad sequences, endpoint/center values; all65536 signed axis inputs monotone/in range; limit0, disabled/absent axes and button groups |
| Time |7000 paired ticks=100 seconds; timer-only pause progress; suspend/resume without catch-up; real dummy-test wall pacing |
| Video transactions | Lane mask, full-byte plane/latches, chained live copies, hidden destinationFFFF, water40h mark, DAC wrap/phase and retrace attribute reset |
| Picture golden | Original startup frame12, all12 records equal maintained ASM reference; all64000 RGB pixels equal unchanged host_render on identical device fields |
| Presentation boundaries |64 additional page/pitch/split/wrapping cases equal host_render; real SDL dummy window/texture/present exercised |
| OPL golden |4800 stereo frames byte-equal independent direct pinned Nuked-OPL3 output;14 ordered writes and nonzero synthesis; logical sink order and real SDL dummy stream |
| Score file | Raw107-byte roundtrip, retained short-read tail, truncation under another handle, original handles5..31/exhaustion/mode errors, atomic replace without logical close |
| Seed | Fixed replay bytes exact; live hours/minutes/seconds range; backend contains no RNG state |

Picture/PCM goldens are not produced by port code: one comes from the reconstructed
ASM and unchanged host presentation body, the other from direct calls to the pinned
synthesizer. Committed golden metadata fixes their hashes; missing or changed
goldens fail rather than silently regenerate. Bulk source snapshots/PCM remain
uncommitted under the worker cache. No game units are linked into the provider or
oracle tests. The small NativeVga accelerator used during ASM capture is hardware
model code only.

'''
 text+='- Picture RGB SHA256: `'+video['golden']['rgb_sha256']+'`.\n'
 text+='- OPL PCM SHA256: `'+unit['audio']['pcm_sha256']+'`.\n'
 text+='- Pack SHA256: `'+manifest['pack_sha256']+'`.\n\n'
 text+='| Rejected pack control | Diagnostic |\n|---|---|\n'
 for r in pack['controls']:text+='| '+r['control']+' | '+r['diagnostic']+' |\n'
 text+='''
## Toolchain and negative results

The existing host's pinned MinGW GCC is at C:/msys64/mingw64/bin/gcc.exe; SDL3 and
Nuked-OPL3 are the requested C:/tools installations. tests/port/toolchain.json pins
their actual executable/source hashes; drift is rejected before building. No new
compiler/library is downloaded. The exact commands, compiler/DLL/source hashes,
SDL provenance and linked source list are in build.json. Nuked-OPL3 remains the
external LGPL-2.1-or-later provider, not vendored game code.

- Initial strict builds rejected misleading one-line indentation and a promoted
  byte-complement comparison. The code was corrected; -Wall/-Wextra/-Werror stayed
  enabled. Failed commands/output remain under negative/.
- The first picture capture attempted a full DeviceState copy from whole game's
  deliberately shorter device prefix, then used the singular field spelling.
  It was corrected to populate a zero-initialized oracle state with the recorded
  prefix and use planes; all12 frame hashes were rechecked on the complete rerun.
- No solver timeout/cap or failing test is counted as positive. This groundwork
  does not make A/B equivalence claims or promote any closure certificate.
- A final rerun found the shared plain UGH.EXE absent during another worker's
  rebuild. It failed before extraction and is retained in negative/. No shared
  build was modified; the complete run was repeated after cgen validated the
  newly completed plain build.
- Golden text provenance uses LF-normalized source hashes and canonical JSON
  frame hashes, so a CRLF checkout or cache formatting change cannot invalidate
  unchanged pixels/PCM. The binary picture/PCM goldens themselves were unchanged.
- The final static request audit retained handles5..31 (27 live slots), the
  nonzero-capable flush reply and button levels in the presence byte. The final
  tests cover those fields; earlier drafts are not credited as equivalent.

## Gaps for step7 / proposed contract follow-up

1. Bind native world requests to GameServices at their accepted cuts, including
   frame-end/retrace/time coordination and synchronous failure prefixes. Keep
   native page exchange, simulation/frame order and timer accounting engine-owned.
   The event source supplies opportunities, not an unproved replacement scheduler.
2. Connect the logical clock receiver to the native timing/audio peer graph and
   close capability/probe/calibration/timer-lifetime prefixes. The current raw
   calibration context cannot be filled honestly from sample time. Those typed
   operations return Unsupported until that adapter exists.
3. Replace bank-shaped source bindings with explicit native resource/scratch
   borrows. Indexed read/store operations here denote only the hardware store;
   scratch/resource sources go through their owners, not a fabricated second video
   address space. Noncanonical pixel continuation/control requests stay Unsupported.
   Already moved mutable metadata stays authoritative in resource_catalog when
   wired: bind/hand off once, never keep both pack views and a native copy as live
   authorities. Initializer records must never resynchronize active world owners.
4. Generate semantic descriptor/journey/script/callback admission from the shipped
   resource graph. Preserve raw compatibility data in the verification target;
   do not make a production original-code-word resolver from opaque pack bytes.
  184 model names lack a sound independent allocation extent and are recorded.
5. Connect lifecycle/terminal/window/input/audio teardown in the accepted order,
   with saved-role handling and the live terminal value. No successful lifecycle
   or unexplained-hook role is fabricated by the pending provider.
   The keyboard flush reply remains an explicit opaque u16 witness; its default0
   matches the current deterministic provider. Step7 must bind that reply and pass
   its live low byte through terminal exit, never substitute a clean exit code.
6. Exercise actual monitor/audio/gamepad combinations during integration. Dummy
   drivers prove the service API and pixels/PCM, not every physical driver. The
   score persistence backend currently follows the existing Windows atomic-replace
   implementation; another OS needs its atomic provider.

Proposed follow-up text (no docs edited): "Step8 groundwork provides the typed
GameServices table, data-only versioned resource pack/admission reader and
headless-tested SDL video/input/time/audio/files/seed providers. It links no game
code. Step7 must still bind world cuts, timer/calibration/lifecycle continuations,
resource/scratch identities and shipped callback admission before a standalone
game executable exists."
'''
 (OUT/'REPORT.md').write_text(text,encoding='utf-8')
 print('REPORT.md written; no certificate or document modified')
if __name__=='__main__':main()
