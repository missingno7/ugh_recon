; Maintained reconstruction; asmgen.py is the bootstrap, asmverify.py is the gate.
; Image contribution 0664C..08783 (end exclusive).
.286
JUMPS
extrn _fn_013B_001F:far
extrn _InstallTimerInterrupt:far
extrn _RestoreTimerInterrupt:far
extrn _RegisterTimerCallback:far
extrn _RemoveTimerCallback:far
extrn _SetTimerCallbackInterval:far
extrn _InitializeSoundSystem:far
extrn _SetMusicTrackVolume:far
extrn _StopAdlibTrackChannel:far
extrn _ApplyScannedMusicEvents:far
SOUNDSEG segment word public 'CODE'
assume cs:SOUNDSEG
public ext_0664
ext_0664 label far
SOUND_BASE label byte
public _AdlxPlaybackGuard
_AdlxPlaybackGuard equ SOUND_BASE+022Ah
public _MainAdlxPlaying
_MainAdlxPlaying equ SOUND_BASE+024Ah
public _MainAdlxSectionLoopEnabled
_MainAdlxSectionLoopEnabled equ SOUND_BASE+0250h
public _SoundDeviceBits
_SoundDeviceBits equ SOUND_BASE+025Eh
public _CancelMusicFade
_CancelMusicFade equ SOUND_BASE+01325h
public _ShutdownDspPlayback
_ShutdownDspPlayback equ SOUND_BASE+020ADh
public _ShutdownAdlibPlayback
_ShutdownAdlibPlayback equ SOUND_BASE+01A59h
public _AudioChannelStates
_AudioChannelStates equ SOUND_BASE+08h
public _MusicTicksPerUnit
_MusicTicksPerUnit equ SOUND_BASE+022Ch
public _AdlxTickCount
_AdlxTickCount equ SOUND_BASE+022Eh
public _MainAdlxTimeOrigin
_MainAdlxTimeOrigin equ SOUND_BASE+0232h
public _SampleMixerBusy
_SampleMixerBusy equ SOUND_BASE+02h
public _SoundBankBase
_SoundBankBase equ SOUND_BASE+0242h
public _SoundBankLength
_SoundBankLength equ SOUND_BASE+0246h
public _ActiveSampleVoiceCount
_ActiveSampleVoiceCount equ SOUND_BASE+0262h
public _ActiveSampleVoiceMask
_ActiveSampleVoiceMask equ SOUND_BASE+0264h
public _ClearSoundState
_ClearSoundState equ SOUND_BASE+0111Fh
public _InitializeDspPlayback
_InitializeDspPlayback equ SOUND_BASE+02050h
public _SetDspSampleRate
_SetDspSampleRate equ SOUND_BASE+01C2Dh
public _InitializeAdlibPlayback
_InitializeAdlibPlayback equ SOUND_BASE+01A7Dh
public _PrimeSampleDmaPlayback
_PrimeSampleDmaPlayback equ SOUND_BASE+01E8Bh
public _MainAdlxStartPointer
_MainAdlxStartPointer equ SOUND_BASE+0206h
public _MusicEventStreamLength
_MusicEventStreamLength equ SOUND_BASE+020Ah
public _MusicVoiceCount
_MusicVoiceCount equ SOUND_BASE+0222h
public _ScannedMusicClockTicks
_ScannedMusicClockTicks equ SOUND_BASE+0236h
public _MusicFadeStep
_MusicFadeStep equ SOUND_BASE+023Ah
public _MusicFadeDuration
_MusicFadeDuration equ SOUND_BASE+023Ch
public _MusicFadeStartVolume
_MusicFadeStartVolume equ SOUND_BASE+023Eh
public _MusicFadeTargetVolume
_MusicFadeTargetVolume equ SOUND_BASE+0240h
public _MusicFadeScheduled
_MusicFadeScheduled equ SOUND_BASE+024Ch
public _MusicTrackVolume
_MusicTrackVolume equ SOUND_BASE+024Eh
public _AdlibInstrumentMap
_AdlibInstrumentMap equ SOUND_BASE+025Ah
public _ReservedAdlibChannelCount
_ReservedAdlibChannelCount equ SOUND_BASE+0260h
public _CurrentAdlxSlot
_CurrentAdlxSlot equ SOUND_BASE+0268h
public _AdlibVoiceStates
_AdlibVoiceStates equ SOUND_BASE+026Ch
public _SavedAdlibVoiceStates
_SavedAdlibVoiceStates equ SOUND_BASE+0320h
public _ScannedAdlibVoiceStates
_ScannedAdlibVoiceStates equ SOUND_BASE+03D4h
public _ScheduleMusicFade
_ScheduleMusicFade equ SOUND_BASE+01342h
public _SilenceAdlibOperators
_SilenceAdlibOperators equ SOUND_BASE+01A2Bh
public _SetAdlibChannelVolume
_SetAdlibChannelVolume equ SOUND_BASE+01205h
public _KeyOffAdlibChannel
_KeyOffAdlibChannel equ SOUND_BASE+014A5h
public _LoadAdlibInstrument
_LoadAdlibInstrument equ SOUND_BASE+0136Bh
public _SetAdlibFrequency
_SetAdlibFrequency equ SOUND_BASE+014F7h
public _MainAdlxCursor
_MainAdlxCursor equ SOUND_BASE+0210h
public _FirstScannedEvent
_FirstScannedEvent equ SOUND_BASE+0252h
public _MainAdlxSectionEnd
_MainAdlxSectionEnd equ SOUND_BASE+0256h
; CONTRACT (tools/apply.py)
; Word period set from BE16 ADLX 6n events and used for effect timing ratios.
; END CONTRACT
AdlxTimerPeriod equ SOUND_BASE+00h
; CONTRACT (tools/apply.py)
; Word set during sample mixing; polled before foreground voice changes and DMA priming.
; END CONTRACT
SampleMixerBusy equ SOUND_BASE+02h
; CONTRACT (tools/apply.py)
; Word base for DSP reset/status/command ports; probe tests 210h through 260h.
; END CONTRACT
DspBasePort equ SOUND_BASE+04h
; CONTRACT (tools/apply.py)
; Word containing selected IRQ+8 vector number in low byte; used by DOS AH=25h/35h.
; END CONTRACT
DspInterruptVector equ SOUND_BASE+06h
; CONTRACT (tools/apply.py)
; Word field +04h of voice 0; indexed by 2Ah; decremented at sample end unless flags&2.
; END CONTRACT
SampleVoiceRepeatCount equ SOUND_BASE+0Ch
; CONTRACT (tools/apply.py)
; Far pointer field +06h of voice 0; indexed by 2Ah and loaded with LDS by mixer.
; END CONTRACT
SampleVoiceDataPointer equ SOUND_BASE+0Eh
; CONTRACT (tools/apply.py)
; Word field +0Ah of voice 0; indexed by 2Ah; compared to scaled sample byte offset.
; END CONTRACT
SampleVoiceByteLength equ SOUND_BASE+012h
; CONTRACT (tools/apply.py)
; Word at field +10h of voice 0, indexed by 2Ah; mixer increments once per byte pair.
; END CONTRACT
SampleVoicePairCursor equ SOUND_BASE+018h
; CONTRACT (tools/apply.py)
; Word field +1Ch of voice 0; mixer uses low byte>>1 as signed IMUL factor.
; END CONTRACT
SampleVoiceVolume equ SOUND_BASE+024h
; CONTRACT (tools/apply.py)
; Word field +26h of voice 0; mixer uses low16((cursor*step)>>8) for sample offset.
; END CONTRACT
SampleVoiceStepQ8 equ SOUND_BASE+02Eh
; CONTRACT (tools/apply.py)
; Word field +28h of voice 0, indexed by 2Ah; bit 1 suppresses repeat decrement.
; END CONTRACT
SampleVoiceFlags equ SOUND_BASE+030h
; CONTRACT (tools/apply.py)
; Word field +04h of main record at 020Ch; 77h decrements unless flags&2.
; END CONTRACT
MainAdlxRepeatCount equ SOUND_BASE+0204h
; CONTRACT (tools/apply.py)
; Far origin pointer of main stream; 77h restores cursor from words 0212h/0214h.
; END CONTRACT
MainAdlxStartPointer equ SOUND_BASE+0206h
; CONTRACT (tools/apply.py)
; High word of main stream origin pointer, copied into cursor segment by 77h.
; END CONTRACT
MainAdlxStartSegment equ SOUND_BASE+0208h
; CONTRACT (tools/apply.py)
; Far main stream cursor; LES loads it and wait handlers update low word DI.
; END CONTRACT
MainAdlxCursor equ SOUND_BASE+0210h
; CONTRACT (tools/apply.py)
; High word of main stream cursor, restored from origin segment on repeat.
; END CONTRACT
MainAdlxCursorSegment equ SOUND_BASE+0212h
; CONTRACT (tools/apply.py)
; Low word of main-event deadline; wait handlers add deltas and propagate carry.
; END CONTRACT
MainAdlxDeadlineLow equ SOUND_BASE+021Eh
; CONTRACT (tools/apply.py)
; High word of main-event deadline, compared unsigned before low word in dispatcher.
; END CONTRACT
MainAdlxDeadlineHigh equ SOUND_BASE+0220h
; CONTRACT (tools/apply.py)
; Word main record +28h: 77h tests repeat bit 1 and clears active bit 0 on expiration.
; END CONTRACT
MainAdlxFlags equ SOUND_BASE+0228h
; CONTRACT (tools/apply.py)
; Word guard: dispatcher increments time then skips playback while bit 0 is set.
; END CONTRACT
AdlxPlaybackGuard equ SOUND_BASE+022Ah
; CONTRACT (tools/apply.py)
; 32-bit clock view; ASM increments low word here and carries to CS:023Ch.
; END CONTRACT
AdlxTickCount equ SOUND_BASE+022Eh
; CONTRACT (tools/apply.py)
; High word of clock incremented on CS:023Ah wrap, used in unsigned deadline checks.
; END CONTRACT
AdlxTickHighWord equ SOUND_BASE+0230h
; CONTRACT (tools/apply.py)
; 32-bit origin subtracted from AdlxTickCount by C:GetElapsedMusicTime.
; Start and whole-track repeat copy the current clock; section restore adds scanned loop ticks.
; Section restore changes this origin, not AdlxTickCount or the main event deadline.
; END CONTRACT
MainAdlxTimeOrigin equ SOUND_BASE+0232h
; CONTRACT (tools/apply.py)
; High word of elapsed origin copied from sound clock by main-track 77h repeat.
; END CONTRACT
MainAdlxTimeOriginHigh equ SOUND_BASE+0234h
; CONTRACT (tools/apply.py)
; Word incremented once per AdvanceMusicFade callback, independently of AdlxTickCount.
; C resets it to zero; interpolation runs through MusicFadeDuration, then the next call cancels.
; END CONTRACT
MusicFadeStep equ SOUND_BASE+023Ah
; CONTRACT (tools/apply.py)
; Word fade-callback count: unsigned completion limit and signed IDIV interpolation divisor.
; The fade callback has its own 0001:D1EBh PIT-clock interval; these are not ADLX ticks.
; With duration zero, an entry step of FFFFh wraps to zero and divides by zero; step zero cancels.
; Values with bit 15 set are signed divisors despite the unsigned completion comparison.
; END CONTRACT
MusicFadeDuration equ SOUND_BASE+023Ch
; CONTRACT (tools/apply.py)
; Word interpolation starting volume in signed IMUL/IDIV expression at 12E5h.
; END CONTRACT
MusicFadeStartVolume equ SOUND_BASE+023Eh
; CONTRACT (tools/apply.py)
; Word target in start + signed((target-start)*step)/duration, with 16-bit arithmetic.
; For ordinary positive durations/volume ranges, step==duration applies the target value.
; The callback remains scheduled until a later incremented step is unsigned-above duration.
; END CONTRACT
MusicFadeTargetVolume equ SOUND_BASE+0240h
; CONTRACT (tools/apply.py)
; Main-track dispatch/routing flag: C start sets one, C stop clears it.
; Separate from main record flags at 0234h; a finite 77h expiration clears those flags only.
; ASM tests bit 0; C tests the full word. ClearSoundState zeroes both states.
; END CONTRACT
MainAdlxPlaying equ SOUND_BASE+024Ah
; CONTRACT (tools/apply.py)
; Word set to one when ScheduleMusicFade registers the independent fade callback.
; CancelMusicFade or the callback's step>duration path clears it; C fade-out polls the word.
; It stays set between callbacks and is not a callback reentry guard.
; END CONTRACT
MusicFadeScheduled equ SOUND_BASE+024Ch
; CONTRACT (tools/apply.py)
; Word whose bit 0 enables repeated cursor-offset checks against MainAdlxSectionEnd.
; Successful C:ScanMusicEvents sets one; C:DisableMusicSectionLoop clears it if music is active.
; C:ApplyScannedMusicEvents restores the first scan cursor/state without clearing this flag.
; END CONTRACT
MainAdlxSectionLoopEnabled equ SOUND_BASE+0250h
; CONTRACT (tools/apply.py)
; Far cursor saved by the second C:ScanMusicEvents pass, after the end-time threshold.
; Driver compares only its offset to the main cursor; reaching it restores FirstScannedEvent.
; Thresholds can overshoot by a wait event; pointer segment is stored but not compared here.
; END CONTRACT
MainAdlxSectionEnd equ SOUND_BASE+0256h
; CONTRACT (tools/apply.py)
; Word bits: 0 AdLib, 1 DSP/sample output; consumed by hardware lifecycle calls.
; END CONTRACT
SoundDeviceBits equ SOUND_BASE+025Eh
; CONTRACT (tools/apply.py)
; Word count of physical channels taken by effects; main routing uses 9 minus low byte.
; END CONTRACT
ReservedAdlibChannelCount equ SOUND_BASE+0260h
; CONTRACT (tools/apply.py)
; Word number of active sample voices; mixer divides signed sums by its current value.
; END CONTRACT
ActiveSampleVoiceCount equ SOUND_BASE+0262h
; CONTRACT (tools/apply.py)
; Low-byte voice bitset; mixer shifts CL over 8 voices, clears finished bits with XOR.
; END CONTRACT
ActiveSampleVoiceMask equ SOUND_BASE+0264h
; CONTRACT (tools/apply.py)
; Word ADLX descriptor/owner context: 12 for main music, 8..11 for effects during dispatch.
; C start and allocation restoration also assign it; volume routing uses this slot context.
; It is not an OPL channel index. C fade-out writes zero; the effect loop can leave twelve.
; END CONTRACT
CurrentAdlxSlot equ SOUND_BASE+0268h
; CONTRACT (tools/apply.py)
; Byte +01h in first 20-byte live instrument record; total-level low 6 bits and high KSL bits.
; END CONTRACT
AdlibModulatorLevel equ SOUND_BASE+026Dh
; CONTRACT (tools/apply.py)
; Byte +06h in first live instrument record; scaled into OPL carrier total-level register.
; END CONTRACT
AdlibCarrierLevel equ SOUND_BASE+0272h
; CONTRACT (tools/apply.py)
; Byte +0Ah of first live instrument record; bit 0 selects whether modulator level is scaled.
; END CONTRACT
AdlibConnectionFlags equ SOUND_BASE+0276h
; CONTRACT (tools/apply.py)
; Byte +0Ch in live 20-byte record, indexed by 14h; saved requested volume for gain reapply.
; END CONTRACT
AdlibChannelVolume equ SOUND_BASE+0278h
; CONTRACT (tools/apply.py)
; Byte +0Eh in live 20-byte record, indexed by 14h; multiplied into requested channel volume.
; END CONTRACT
AdlibChannelGain equ SOUND_BASE+027Ah
; CONTRACT (tools/apply.py)
; Word +10h in live 20-byte record, indexed by 14h; instrument load stamps current slot.
; END CONTRACT
AdlibChannelOwnerSlot equ SOUND_BASE+027Ch
; CONTRACT (tools/apply.py)
; Word +12h in live 20-byte record; low A0 frequency byte, high B0 block/key control.
; END CONTRACT
AdlibPackedFrequency equ SOUND_BASE+027Eh
; CONTRACT (tools/apply.py)
; High byte of packed frequency; key-off clears bit 5 here before writing B0 register.
; END CONTRACT
AdlibKeyControlByte equ SOUND_BASE+027Fh
; CONTRACT (tools/apply.py)
; Byte +0Ch in displaced 20-byte record bank at 032Ch; updated for channels reserved by effects.
; END CONTRACT
DisplacedAdlibVolume equ SOUND_BASE+032Ch
; CONTRACT (tools/apply.py)
; Byte +0Eh in displaced record bank; updated instead of live gain for reserved main channels.
; END CONTRACT
DisplacedAdlibGain equ SOUND_BASE+032Eh
; CONTRACT (tools/apply.py)
; Word +12h in displaced record bank; main events save frequency/key-off for reserved channels.
; END CONTRACT
DisplacedAdlibFrequency equ SOUND_BASE+0332h
; CONTRACT (tools/apply.py)
; Byte 1<<IRQ selected during probe; used to mask/unmask master PIC port 21h.
; END CONTRACT
DspPicIrqMask equ SOUND_BASE+0488h
; CONTRACT (tools/apply.py)
; Offset word of saved DOS IRQ vector; LDS at shutdown uses it with following segment word.
; END CONTRACT
PreviousDspVectorOffset equ SOUND_BASE+0489h
; CONTRACT (tools/apply.py)
; Segment word of saved DOS IRQ vector returned by INT 21h AH=35h.
; END CONTRACT
PreviousDspVectorSegment equ SOUND_BASE+048Bh
; CONTRACT (tools/apply.py)
; Byte set to 1 by temporary IRQ probe handler; polled with LOOP(E) during DMA probe.
; END CONTRACT
DspProbeIrqSeen equ SOUND_BASE+0495h
; CONTRACT (tools/apply.py)
; Byte bit 0 prevents reentry into the DMA interrupt mixer; set and cleared around handler work.
; END CONTRACT
DspIrqBusy equ SOUND_BASE+0496h
; CONTRACT (tools/apply.py)
; Byte toggled with XOR 1 when a queued block is started; selects alternate 040Ah-stride header.
; END CONTRACT
DmaMixBufferSelect equ SOUND_BASE+0499h
; CONTRACT (tools/apply.py)
; Word queued count for first buffer header; values below 28h mask IRQ instead of playing.
; END CONTRACT
DmaMixBufferOneCount equ SOUND_BASE+049Bh
; CONTRACT (tools/apply.py)
; Physical address page byte for first DMA buffer, derived from loaded CS and selected offset.
; END CONTRACT
DmaMixBufferOnePage equ SOUND_BASE+049Dh
; CONTRACT (tools/apply.py)
; Word physical offset within DMA page for first mix buffer.
; END CONTRACT
DmaMixBufferOneAddress equ SOUND_BASE+049Fh
; CONTRACT (tools/apply.py)
; Word CS-relative offset for first mix buffer; normally 04AFh, fallback 0CC3h.
; END CONTRACT
DmaMixBufferOneOffset equ SOUND_BASE+04A1h
; CONTRACT (tools/apply.py)
; Word queued count for second buffer header, 040Ah after first header.
; END CONTRACT
DmaMixBufferTwoCount equ SOUND_BASE+08A5h
; CONTRACT (tools/apply.py)
; Physical address page byte for second DMA buffer, computed by 1C74h.
; END CONTRACT
DmaMixBufferTwoPage equ SOUND_BASE+08A7h
; CONTRACT (tools/apply.py)
; Word physical offset within DMA page for second mix buffer.
; END CONTRACT
DmaMixBufferTwoAddress equ SOUND_BASE+08A9h
; CONTRACT (tools/apply.py)
; Word CS-relative offset for second mix buffer; normally 08B9h, fallback 0CC3h.
; END CONTRACT
DmaMixBufferTwoOffset equ SOUND_BASE+08ABh
; CONTRACT (tools/apply.py)
; Word remaining pair count initialized to BX>>1; signed JLE tests after decrement.
; END CONTRACT
SampleMixPairsRemaining equ SOUND_BASE+010BBh
; CONTRACT (tools/apply.py)
; Far old INT 08h vector saved before temporary calibration handlers are installed.
; END CONTRACT
PreviousCalibrationTimerVector equ SOUND_BASE+010BFh
; CONTRACT (tools/apply.py)
; High word of old INT 08h vector restored by calibration completion handler.
; END CONTRACT
PreviousCalibrationTimerSegment equ SOUND_BASE+010C1h
; CONTRACT (tools/apply.py)
; Word signed scaled sum for first output byte of each pair; divided by active voice count.
; END CONTRACT
SampleMixFirstSum equ SOUND_BASE+010C3h
; CONTRACT (tools/apply.py)
; Word signed scaled sum for second output byte of each pair; divided by active voice count.
; END CONTRACT
SampleMixSecondSum equ SOUND_BASE+010C5h
; CONTRACT (tools/apply.py)
; Word CS offset of current 42-byte record: 020Ch main or 0164h..01E2h effects.
; END CONTRACT
CurrentAdlxRecordOffset equ SOUND_BASE+010E3h
; CONTRACT (tools/apply.py)
; Nine byte operator-index offsets: 0,1,2,8,9,0Ah,10h,11h,12h for OPL melodic channels.
; END CONTRACT
AdlibOperatorOffsets equ SOUND_BASE+010E9h
; CONTRACT (tools/apply.py)
; Word slot handle returned by TIMER:01AAh; used by 6n period events and shutdown.
; END CONTRACT
AdlxPlaybackTimerHandle equ SOUND_BASE+01116h
; CONTRACT (tools/apply.py)
; Word timer slot handle for 12E5h fade callback; read when canceling scheduled fade.
; END CONTRACT
MusicFadeTimerHandle equ SOUND_BASE+01118h
; CONTRACT (tools/apply.py)
; Byte set before OPL probe; not cleared on failure, so subsequent init returns success.
; END CONTRACT
AdlibInitAttempted equ SOUND_BASE+0111Ah
; CONTRACT (tools/apply.py)
; Word interrupted CX saved by second calibration IRQ0 handler; no resolved consumer.
; END CONTRACT
CalibrationLoopRemainder equ SOUND_BASE+0111Bh
; CONTRACT (tools/apply.py)
; Word interrupted DX from calibration; delay helper multiplies only its low byte by AL.
; END CONTRACT
SoundIoDelayMultiplier equ SOUND_BASE+0111Dh
; CONTRACT (tools/apply.py)
; EQU address view of 16 near handler offsets indexed by opcode high nibble.
; END CONTRACT
MainAdlxDispatchTable equ SOUND_BASE+0173Fh
; CONTRACT (tools/apply.py)
; EQU address view of 16 near handler offsets for effect ADLX bytecode.
; END CONTRACT
EffectAdlxDispatchTable equ SOUND_BASE+0190Dh
; CONTRACT (tools/apply.py)
; EQU view of four candidate IRQ bytes 7,5,3,2, indexed by DSP base/IRQ probe.
; END CONTRACT
DspProbeIrqOrder equ SOUND_BASE+0204Ch
byte_data_000C:
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 000C..001C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 001C..002C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 002C..003C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 003C..004C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 004C..005C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 005C..006C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 006C..007C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 007C..008C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 008C..009C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 009C..00AC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 00AC..00BC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 00BC..00CC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 00CC..00DC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 00DC..00EC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 00EC..00FC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 00FC..010C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 010C..011C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 011C..012C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 012C..013C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 013C..014C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 014C..015C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 015C..016C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 016C..017C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 017C..018C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 018C..019C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 019C..01AC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 01AC..01BC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 01BC..01CC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 01CC..01DC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 01DC..01EC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 01EC..01FC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 01FC..020C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 020C..021C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 021C..022C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 022C..023C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 023C..024C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 024C..025C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 025C..026C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 026C..027C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 027C..028C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 028C..029C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 029C..02AC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 02AC..02BC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 02BC..02CC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 02CC..02DC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 02DC..02EC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 02EC..02FC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 02FC..030C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 030C..031C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 031C..032C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 032C..033C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 033C..034C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 034C..035C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 035C..036C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 036C..037C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 037C..038C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 038C..039C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 039C..03AC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 03AC..03BC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 03BC..03CC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 03CC..03DC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 03DC..03EC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 03EC..03FC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 03FC..040C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 040C..041C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 041C..042C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 042C..043C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 043C..044C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 044C..045C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 045C..046C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 046C..047C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 047C..048C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 0A6h, 014h, 00h ; data 048C..049C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 049C..04AC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 04AC..04BC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 04BC..04CC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 04CC..04DC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 04DC..04EC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 04EC..04FC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 04FC..050C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 050C..051C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 051C..052C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 052C..053C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 053C..054C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 054C..055C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 055C..056C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 056C..057C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 057C..058C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 058C..059C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 059C..05AC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 05AC..05BC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 05BC..05CC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 05CC..05DC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 05DC..05EC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 05EC..05FC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 05FC..060C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 060C..061C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 061C..062C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 062C..063C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 063C..064C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 064C..065C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 065C..066C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 066C..067C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 067C..068C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 068C..069C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 069C..06AC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 06AC..06BC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 06BC..06CC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 06CC..06DC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 06DC..06EC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 06EC..06FC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 06FC..070C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 070C..071C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 071C..072C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 072C..073C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 073C..074C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 074C..075C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 075C..076C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 076C..077C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 077C..078C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 078C..079C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 079C..07AC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 07AC..07BC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 07BC..07CC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 07CC..07DC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 07DC..07EC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 07EC..07FC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 07FC..080C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 080C..081C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 081C..082C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 082C..083C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 083C..084C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 084C..085C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 085C..086C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 086C..087C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 087C..088C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 088C..089C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 089C..08AC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 08AC..08BC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 08BC..08CC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 08CC..08DC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 08DC..08EC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 08EC..08FC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 08FC..090C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 090C..091C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 091C..092C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 092C..093C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 093C..094C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 094C..095C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 095C..096C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 096C..097C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 097C..098C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 098C..099C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 099C..09AC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 09AC..09BC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 09BC..09CC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 09CC..09DC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 09DC..09EC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 09EC..09FC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 09FC..0A0C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0A0C..0A1C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0A1C..0A2C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0A2C..0A3C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0A3C..0A4C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0A4C..0A5C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0A5C..0A6C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0A6C..0A7C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0A7C..0A8C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0A8C..0A9C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0A9C..0AAC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0AAC..0ABC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0ABC..0ACC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0ACC..0ADC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0ADC..0AEC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0AEC..0AFC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0AFC..0B0C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0B0C..0B1C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0B1C..0B2C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0B2C..0B3C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0B3C..0B4C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0B4C..0B5C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0B5C..0B6C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0B6C..0B7C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0B7C..0B8C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0B8C..0B9C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0B9C..0BAC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0BAC..0BBC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0BBC..0BCC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0BCC..0BDC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0BDC..0BEC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0BEC..0BFC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0BFC..0C0C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0C0C..0C1C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0C1C..0C2C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0C2C..0C3C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0C3C..0C4C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0C4C..0C5C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0C5C..0C6C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0C6C..0C7C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0C7C..0C8C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0C8C..0C9C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0C9C..0CAC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0CAC..0CBC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0CBC..0CCC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0CCC..0CDC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0CDC..0CEC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0CEC..0CFC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0CFC..0D0C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0D0C..0D1C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0D1C..0D2C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0D2C..0D3C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0D3C..0D4C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0D4C..0D5C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0D5C..0D6C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0D6C..0D7C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0D7C..0D8C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0D8C..0D9C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0D9C..0DAC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0DAC..0DBC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0DBC..0DCC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0DCC..0DDC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0DDC..0DEC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0DEC..0DFC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0DFC..0E0C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0E0C..0E1C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0E1C..0E2C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0E2C..0E3C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0E3C..0E4C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0E4C..0E5C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0E5C..0E6C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0E6C..0E7C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0E7C..0E8C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0E8C..0E9C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0E9C..0EAC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0EAC..0EBC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0EBC..0ECC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0ECC..0EDC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0EDC..0EEC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0EEC..0EFC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0EFC..0F0C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0F0C..0F1C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0F1C..0F2C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0F2C..0F3C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0F3C..0F4C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0F4C..0F5C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0F5C..0F6C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0F6C..0F7C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0F7C..0F8C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0F8C..0F9C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0F9C..0FAC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0FAC..0FBC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0FBC..0FCC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0FCC..0FDC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0FDC..0FEC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0FEC..0FFC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 0FFC..100C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 100C..101C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 101C..102C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 102C..103C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 103C..104C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 104C..105C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 105C..106C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 106C..107C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 107C..108C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 108C..109C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 109C..10AC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 10AC..10BC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 10BC..10CC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 10CC..10DC
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 10DC..10EC
    db 00h, 00h, 09h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 01h, 02h, 08h, 09h, 0Ah, 010h ; data 10EC..10FC
    db 011h, 012h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 10FC..110C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 110C..111C
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 111C..112B
; CONTRACT (tools/apply.py)
; Zero the 0488h-byte sound-state interval CS:000Ch..0493h inclusive.
; Out: AX=CX=0, DF=0; ES and DI preserved; resident buffers after 0493h survive.
; END CONTRACT
ClearSoundState:
    push es ; @112B
    push di ; @112C
    mov ax, cs ; @112D
    mov es, ax ; @112F
    mov di, 0Ch ; @1131
    mov cx, 0488h ; @1134
    cld ; @1137
    xor ax, ax ; @1138
    rep stosb ; @113A
    pop di ; @113C
    pop es ; @113D
    retf ; @113E
; CONTRACT (tools/apply.py)
; Measure busy-loop progress between two IRQ0 ticks using temporary INT 08h handlers.
; Out: saves CX and DX measurements at CS:1127h/1129h; restores the old vector.
; Preserves AX/BX/CX/DX/DS/ES on normal return; requires timer interrupts to arrive.
; Quirk: both handlers call DOS AH=25h in interrupt context and change live AX/CX.
; END CONTRACT
CalibrateSoundDelay:
    push ax ; @113F
    push bx ; @1140
    push cx ; @1141
    push dx ; @1142
    push ds ; @1143
    push es ; @1144
    mov ax, 03508h ; @1145
    int 021h ; @1148
    mov word ptr cs:[PreviousCalibrationTimerVector], bx ; @114A
    mov word ptr cs:[PreviousCalibrationTimerSegment], es ; @114F
    mov ax, seg SOUNDSEG ; @1154
    mov ds, ax ; @1157
    mov dx, offset BeginSoundDelayMeasurement ; @1159
    mov ax, 02508h ; @115C
    int 021h ; @115F
    xor ax, ax ; @1161
loc_1163:
    cmp ah, 1 ; @1163
    jne short loc_1163 ; @1166
loc_1168:
    mov cx, 0 ; @1168
loc_116B:
    loop loc_116B ; @116B
    inc dx ; @116D
    cmp al, 1 ; @116E
    jne short loc_1168 ; @1170
    pop es ; @1172
    pop ds ; @1173
    pop dx ; @1174
    pop cx ; @1175
    pop bx ; @1176
    pop ax ; @1177
    retf ; @1178
; CONTRACT (tools/apply.py)
; First temporary IRQ0 handler: acknowledge PIC and install the second handler.
; Out: live AH=1, AL=0 starts the waiting calibration loop; returns with IRET.
; Preserves DS/DX; does not chain the old handler; invokes DOS AH=25h inside IRQ0.
; END CONTRACT
BeginSoundDelayMeasurement:
    push dx ; @1179
    push ds ; @117A
    mov al, 020h ; @117B
    out 020h, al ; @117D
    mov ax, seg SOUNDSEG ; @117F
    mov ds, ax ; @1182
    mov dx, offset FinishSoundDelayMeasurement ; @1184
    mov ax, 02508h ; @1187
    int 021h ; @118A
    pop ds ; @118C
    pop dx ; @118D
    mov ah, 1 ; @118E
    xor al, al ; @1190
    iret ; @1192
; CONTRACT (tools/apply.py)
; Second temporary IRQ0 handler: acknowledge PIC, restore the saved INT 08h vector.
; Out: CS:1127h=CX, CS:1129h=interrupted DX; live CX=1, AL=1; IRET.
; Preserves DS/DX; DOS AH=25h runs in interrupt context; the calibration loop resumes.
; END CONTRACT
FinishSoundDelayMeasurement:
    push ds ; @1193
    push dx ; @1194
    mov al, 020h ; @1195
    out 020h, al ; @1197
    lds dx, dword ptr cs:[PreviousCalibrationTimerVector] ; @1199
    mov ax, 02508h ; @119E
    int 021h ; @11A1
    mov word ptr cs:[CalibrationLoopRemainder], cx ; @11A3
    pop dx ; @11A8
    mov word ptr cs:[SoundIoDelayMultiplier], dx ; @11A9
    mov cx, 1 ; @11AE
    mov al, 1 ; @11B1
    pop ds ; @11B3
    iret ; @11B4
; CONTRACT (tools/apply.py)
; Busy-wait using AL times the low byte of the measured calibration word at CS:1129h.
; Preserves AX/CX. LOOP executes at least once; a zero product means 65536 iterations.
; END CONTRACT
DelaySoundIo:
    push ax ; @11B5
    push cx ; @11B6
    mul byte ptr cs:[SoundIoDelayMultiplier] ; @11B7
    mov cx, ax ; @11BC
loc_11BE:
    loop loc_11BE ; @11BE
    pop cx ; @11C0
    pop ax ; @11C1
    retf ; @11C2
; CONTRACT (tools/apply.py)
; Advance the 32-bit sound clock, then attempt dispatch under the already-set guard.
; Quirk: if initially unguarded, 1939h increments the clock a second time but skips
; playback because this routine sets CS:0236h first. No identified caller (pattern seed).
; END CONTRACT
AdvanceGuardedSoundClock:
    inc word ptr cs:[AdlxTickCount] ; @11C3
    jne loc_11D2 ; @11C8
    inc word ptr cs:[AdlxTickHighWord] ; @11CD
loc_11D2:
    test word ptr cs:[AdlxPlaybackGuard], 1 ; @11D2
    jne loc_11F1 ; @11D9
    mov word ptr cs:[AdlxPlaybackGuard], 1 ; @11DE
    call far ptr TickAdlxPlayback ; @11E5 same-segment far call
    mov word ptr cs:[AdlxPlaybackGuard], 0 ; @11EA
loc_11F1:
    retf ; @11F1
; CONTRACT (tools/apply.py)
; Write OPL register BH with BL through ports 0388h/0389h, with calibrated delays.
; Preserves AX/DX and delay helper CX; reads the calibration byte at CS:1129h.
; END CONTRACT
WriteAdlibRegister:
    push dx ; @11F2
    push ax ; @11F3
    mov dx, 0388h ; @11F4
    mov al, bh ; @11F7
    out dx, al ; @11F9
    mov ax, 1 ; @11FA
    call far ptr DelaySoundIo ; @11FD same-segment far call
    mov dx, 0389h ; @1201
    mov al, bl ; @1204
    out dx, al ; @1206
    mov ax, 4 ; @1207
    call far ptr DelaySoundIo ; @120A same-segment far call
    pop ax ; @120E
    pop dx ; @120F
    retf ; @1210
; CONTRACT (tools/apply.py)
; Scale saved OPL total levels by channel/requested volume and write operator levels.
; In: far cdecl words OPL channel [BP+6] low byte<9, volume [BP+8] low byte.
; Out: updates live/displaced channel record; preserves AX/BX/CX/DX/SI.
; Displaced routing needs MainAdlxPlaying bit 0, CurrentAdlxSlot>=12, and a reserved channel
; at/above 9-ReservedAdlibChannelCount. CurrentAdlxSlot is a descriptor slot, not this channel.
; Live arithmetic keeps high bytes of unsigned 8-bit products without clipping.
; END CONTRACT
SetAdlibChannelVolume:
    enter 0, 0 ; @1211
    push si ; @1215
    push ax ; @1216
    push bx ; @1217
    push cx ; @1218
    push dx ; @1219
    mov bl, byte ptr [bp + 6] ; @121A
    mov dl, byte ptr [bp + 8] ; @121D
    cmp bl, 9 ; @1220
    jae loc_12DE ; @1223 JUMPS expansion
loc_1228:
    mov ax, 014h ; @1228
    mul bl ; @122B
    mov si, ax ; @122D
    test word ptr cs:[MainAdlxPlaying], 1 ; @122F
    je loc_126D ; @1236
    cmp word ptr cs:[CurrentAdlxSlot], 0Ch ; @123B
    jb loc_126D ; @1241
    test word ptr cs:[ReservedAdlibChannelCount], 0Fh ; @1246
    je loc_126D ; @124D
    mov ax, 9 ; @1252
    sub al, byte ptr cs:[ReservedAdlibChannelCount] ; @1255
    cmp bl, al ; @125A
    jb loc_126D ; @125C
    mov byte ptr cs:[si + DisplacedAdlibVolume], dl ; @1261
    pop dx ; @1266
    pop cx ; @1267
    pop bx ; @1268
    pop ax ; @1269
    pop si ; @126A
    leave ; @126B
    retf ; @126C
loc_126D:
    mov byte ptr cs:[si + AdlibChannelVolume], dl ; @126D
    mov cl, byte ptr cs:[si + AdlibChannelGain] ; @1272
    xor bh, bh ; @1277
    mov ch, byte ptr cs:[bx + AdlibOperatorOffsets] ; @1279
    mov al, byte ptr cs:[si + AdlibCarrierLevel] ; @127E
    mov dh, al ; @1283
    and dh, 0C0h ; @1285
    and al, 03Fh ; @1288
    neg al ; @128A
    add al, 03Fh ; @128C
    mul cl ; @128E
    mov al, ah ; @1290
    mul dl ; @1292
    neg ah ; @1294
    add ah, 03Fh ; @1296
    mov al, ah ; @1299
    or al, dh ; @129B
    mov bh, ch ; @129D
    add bh, 043h ; @129F
    mov bl, al ; @12A2
    call far ptr WriteAdlibRegister ; @12A4 same-segment far call
    test word ptr cs:[si + AdlibConnectionFlags], 1 ; @12A8
    je loc_12DE ; @12AF
    mov al, byte ptr cs:[si + AdlibModulatorLevel] ; @12B4
    mov dh, al ; @12B9
    and dh, 0C0h ; @12BB
    and al, 03Fh ; @12BE
    neg al ; @12C0
    add al, 03Fh ; @12C2
    mul cl ; @12C4
    mov al, ah ; @12C6
    mul dl ; @12C8
    neg ah ; @12CA
    add ah, 03Fh ; @12CC
    mov al, ah ; @12CF
    or al, dh ; @12D1
    mov bh, ch ; @12D3
    add bh, 040h ; @12D5
    mov bl, al ; @12D8
    call far ptr WriteAdlibRegister ; @12DA same-segment far call
loc_12DE:
    pop dx ; @12DE
    pop cx ; @12DF
    pop bx ; @12E0
    pop ax ; @12E1
    pop si ; @12E2
    leave ; @12E3
    retf ; @12E4
; CONTRACT (tools/apply.py)
; Independent fade-timer callback: increment 16-bit MusicFadeStep, then interpolate volume.
; In: MusicFadeDuration, start/target volumes; timer period is fixed at 0001:D1EBh PIT clocks.
; Applies start + signed((target-start)*step)/duration via C:SetMusicTrackVolume while unsigned
; step<=duration; the first unsigned-above step removes the callback and clears scheduled state.
; Normal positive duration reaches target at equality and clears MusicFadeScheduled one call later.
; Preserves AX/BX/CX/DX; cancellation changes DS. IDIV signedness/overflow and step wrap survive.
; END CONTRACT
AdvanceMusicFade:
    push ax ; @12E5
    push bx ; @12E6
    push cx ; @12E7
    push dx ; @12E8
    mov dx, word ptr cs:[MusicFadeStep] ; @12E9
    inc dx ; @12EE
    mov word ptr cs:[MusicFadeStep], dx ; @12EF
    mov bx, word ptr cs:[MusicFadeDuration] ; @12F4
    cmp dx, bx ; @12F9
loc_12FB:
    ja loc_131F ; @12FB
    mov cx, word ptr cs:[MusicFadeStartVolume] ; @1300
    mov ax, word ptr cs:[MusicFadeTargetVolume] ; @1305
    sub ax, cx ; @1309
    imul dx ; @130B
    idiv bx ; @130D
    add ax, cx ; @130F
    push ax ; @1311
loc_1312:
    call far ptr _SetMusicTrackVolume ; @1312
    add sp, 2 ; @1317
loc_131A:
    pop dx ; @131A
    pop cx ; @131B
    pop bx ; @131C
    pop ax ; @131D
    retf ; @131E
loc_131F:
    mov ax, word ptr cs:[MusicFadeTimerHandle] ; @131F
    call far ptr _RemoveTimerCallback ; @1323
    mov word ptr cs:[MusicFadeScheduled], 0 ; @1328
    jmp short loc_131A ; @132F
; CONTRACT (tools/apply.py)
; Cancel the fade timer slot if CS:0258h bit 0 is set, then clear that word.
; In: callback handle CS:1124h; TIMER:021Bh changes DS and other registers.
; END CONTRACT
CancelMusicFade:
    test word ptr cs:[MusicFadeScheduled], 1 ; @1331
    je loc_134D ; @1338
    mov ax, word ptr cs:[MusicFadeTimerHandle] ; @133D
    call far ptr _RemoveTimerCallback ; @1341
    mov word ptr cs:[MusicFadeScheduled], 0 ; @1346
loc_134D:
    retf ; @134D
; CONTRACT (tools/apply.py)
; Register 12E5h at timer period CX:BX=0001:D1EBh unless fade bit 0 is already set.
; Out: saves returned timer handle in CS:1124h and sets CS:0258h=1.
; END CONTRACT
ScheduleMusicFade:
    test word ptr cs:[MusicFadeScheduled], 1 ; @134E
loc_1355:
    jne loc_1376 ; @1355
    mov bx, 0D1EBh ; @135A
    mov cx, 1 ; @135D
    mov ax, offset AdvanceMusicFade ; @1360
loc_1363:
    mov dx, seg SOUNDSEG ; @1363
loc_1366:
    call far ptr _RegisterTimerCallback ; @1366
    mov word ptr cs:[MusicFadeTimerHandle], ax ; @136B
    mov word ptr cs:[MusicFadeScheduled], 1 ; @136F
loc_1376:
    retf ; @1376
; CONTRACT (tools/apply.py)
; Copy instrument state and write modulator/carrier and feedback OPL registers.
; In: far cdecl OPL channel [BP+6] low byte<9, far instrument pointer [BP+8].
; Out: copies 12 bytes into a 20-byte record, leaves DF clear; live path stamps CurrentAdlxSlot
; as channel owner and reapplies saved volume. Event payload advancement is only 11 bytes.
; Displaced copy requires CurrentAdlxSlot==12 and channel>=9-ReservedAdlibChannelCount.
; Slot twelve means main-track context, not physical OPL channel twelve.
; END CONTRACT
LoadAdlibInstrument:
    enter 0, 0 ; @1377
    push es ; @137B
    push ds ; @137C
    push si ; @137D
    push di ; @137E
    push cx ; @137F
    push dx ; @1380
    mov cx, word ptr [bp + 6] ; @1381
    xor ch, ch ; @1384
    cmp cx, 9 ; @1386
    jae loc_14A9 ; @1389 JUMPS expansion
loc_138E:
    lds si, dword ptr [bp + 8] ; @138E
    mov ax, cs ; @1391
    mov es, ax ; @1393
    mov ax, 014h ; @1395
    mul cl ; @1398
    mov di, ax ; @139A
    cmp word ptr cs:[CurrentAdlxSlot], 0Ch ; @139C
    jne loc_13D3 ; @13A2
    test word ptr cs:[ReservedAdlibChannelCount], 0Fh ; @13A7
    je loc_13D3 ; @13AE
    mov al, 9 ; @13B3
    sub al, byte ptr cs:[ReservedAdlibChannelCount] ; @13B5
    cmp cl, al ; @13BA
    jb loc_13D3 ; @13BC
    add di, word ptr 032Ch ; @13C1
    cld ; @13C5
    mov cx, 0Ch ; @13C6
    rep movsb ; @13C9
    pop dx ; @13CB
    pop cx ; @13CC
    pop di ; @13CD
    pop si ; @13CE
    pop ds ; @13CF
    pop es ; @13D0
    leave ; @13D1
    retf ; @13D2
loc_13D3:
    add di, word ptr 0278h ; @13D3
    mov al, cl ; @13D7
    cld ; @13D9
    mov cx, 0Ch ; @13DA
    rep movsb ; @13DD
    sub si, 0Ch ; @13DF
    mov cl, al ; @13E2
    xor ah, ah ; @13E4
    mov bx, ax ; @13E6
    mov ch, byte ptr cs:[bx + AdlibOperatorOffsets] ; @13E8
    mov bl, byte ptr [si] ; @13ED
    inc si ; @13EF
    mov bh, ch ; @13F0
    add bh, 020h ; @13F2
    call far ptr WriteAdlibRegister ; @13F5 same-segment far call
    mov bl, byte ptr [si] ; @13F9
    inc si ; @13FB
    mov bh, ch ; @13FC
    add bh, 040h ; @13FE
    test byte ptr [si + 8], 1 ; @1401
    je loc_140D ; @1405
    or bl, 03Fh ; @140A
loc_140D:
    call far ptr WriteAdlibRegister ; @140D same-segment far call
    mov bl, byte ptr [si] ; @1411
    inc si ; @1413
    mov bh, ch ; @1414
    add bh, 060h ; @1416
    call far ptr WriteAdlibRegister ; @1419 same-segment far call
    mov bl, byte ptr [si] ; @141D
    inc si ; @141F
    mov bh, ch ; @1420
    add bh, 080h ; @1422
    call far ptr WriteAdlibRegister ; @1425 same-segment far call
    mov bl, byte ptr [si] ; @1429
    inc si ; @142B
    mov bh, ch ; @142C
    add bh, 0E0h ; @142E
    call far ptr WriteAdlibRegister ; @1431 same-segment far call
    add ch, 3 ; @1435
    mov bl, byte ptr [si] ; @1438
    inc si ; @143A
    mov bh, ch ; @143B
    add bh, 020h ; @143D
    call far ptr WriteAdlibRegister ; @1440 same-segment far call
    mov bl, byte ptr [si] ; @1444
    inc si ; @1446
    mov bh, ch ; @1447
    add bh, 040h ; @1449
    or bl, 03Fh ; @144C
    call far ptr WriteAdlibRegister ; @144F same-segment far call
    mov bl, byte ptr [si] ; @1453
    inc si ; @1455
    mov bh, ch ; @1456
    add bh, 060h ; @1458
    call far ptr WriteAdlibRegister ; @145B same-segment far call
    mov bl, byte ptr [si] ; @145F
    inc si ; @1461
    mov bh, ch ; @1462
    add bh, 080h ; @1464
    call far ptr WriteAdlibRegister ; @1467 same-segment far call
    mov bx, 0120h ; @146B
    call far ptr WriteAdlibRegister ; @146E same-segment far call
    mov bl, byte ptr [si] ; @1472
    inc si ; @1474
    mov bh, ch ; @1475
    add bh, 0E0h ; @1477
    call far ptr WriteAdlibRegister ; @147A same-segment far call
    mov bl, byte ptr [si] ; @147E
    inc si ; @1480
    mov bh, cl ; @1481
    add bh, 0C0h ; @1483
    call far ptr WriteAdlibRegister ; @1486 same-segment far call
    mov ax, 014h ; @148A
    mul cl ; @148D
    mov bx, ax ; @148F
    mov ax, word ptr cs:[CurrentAdlxSlot] ; @1491
    mov word ptr cs:[bx + AdlibChannelOwnerSlot], ax ; @1495
    push word ptr cs:[bx + AdlibChannelVolume] ; @149A
    push word ptr [bp + 6] ; @149F
    call far ptr SetAdlibChannelVolume ; @14A2 same-segment far call
    add sp, 4 ; @14A6
loc_14A9:
    pop dx ; @14A9
    pop cx ; @14AA
    pop di ; @14AB
    pop si ; @14AC
    pop ds ; @14AD
    pop es ; @14AE
    leave ; @14AF
    retf ; @14B0
; CONTRACT (tools/apply.py)
; Clear bit 5 of saved OPL B0 control byte and write it through ports 0388h/0389h.
; In: far cdecl word channel [BP+6], low byte<9; preserves AX/BX/DX.
; END CONTRACT
KeyOffAdlibChannel:
    enter 0, 0 ; @14B1
    push ax ; @14B5
    push bx ; @14B6
    push dx ; @14B7
    mov bx, word ptr [bp + 6] ; @14B8
    cmp bl, 9 ; @14BB
    jae loc_14FE ; @14BE
    mov ah, bl ; @14C3
    push ax ; @14C5
    mov ax, 014h ; @14C6
    mul bl ; @14C9
    mov bx, ax ; @14CB
    mov dl, byte ptr cs:[bx + AdlibKeyControlByte] ; @14CD
    and dl, 0DFh ; @14D2
    mov byte ptr cs:[bx + AdlibKeyControlByte], dl ; @14D5
    pop ax ; @14DA
    mov bh, ah ; @14DB
    add bh, 0B0h ; @14DD
    mov ah, dl ; @14E0
    mov dx, 0388h ; @14E2
    mov al, bh ; @14E5
    out dx, al ; @14E7
    mov bh, ah ; @14E8
    mov ax, 1 ; @14EA
    call far ptr DelaySoundIo ; @14ED same-segment far call
    mov dx, 0389h ; @14F1
    mov al, bh ; @14F4
    out dx, al ; @14F6
    mov ax, 2 ; @14F7
    call far ptr DelaySoundIo ; @14FA same-segment far call
loc_14FE:
    pop dx ; @14FE
    pop bx ; @14FF
    pop ax ; @1500
    leave ; @1501
    retf ; @1502
; CONTRACT (tools/apply.py)
; Save and write packed OPL A0/B0 frequency, block and key-on bits for a channel.
; In: far cdecl words channel [BP+6] low byte<9, packed value [BP+8].
; Preserves AX/BX/CX/DX; valid-channel path executes CLI then unconditional STI,
; so callers entering with IF=0 leave with interrupts enabled.
; END CONTRACT
SetAdlibFrequency:
    enter 0, 0 ; @1503
    push ax ; @1507
    push bx ; @1508
    push cx ; @1509
    push dx ; @150A
    mov cl, byte ptr [bp + 6] ; @150B
    cmp cl, 9 ; @150E
    jae loc_156B ; @1511
    mov ax, 014h ; @1516
    mul cl ; @1519
    mov bx, ax ; @151B
    mov ax, word ptr [bp + 8] ; @151D
    mov word ptr cs:[bx + AdlibPackedFrequency], ax ; @1520
    cli ; @1525
    mov bh, cl ; @1526
    add bh, 0A0h ; @1528
    mov bl, al ; @152B
    push ax ; @152D
    mov dx, 0388h ; @152E
    mov al, bh ; @1531
    out dx, al ; @1533
    mov ax, 1 ; @1534
    call far ptr DelaySoundIo ; @1537 same-segment far call
    mov dx, 0389h ; @153B
    mov al, bl ; @153E
    out dx, al ; @1540
    mov ax, 3 ; @1541
    call far ptr DelaySoundIo ; @1544 same-segment far call
    pop ax ; @1548
    mov bl, ah ; @1549
    mov bh, cl ; @154B
    add bh, 0B0h ; @154D
    mov dx, 0388h ; @1550
    mov al, bh ; @1553
    out dx, al ; @1555
    mov ax, 1 ; @1556
    call far ptr DelaySoundIo ; @1559 same-segment far call
    mov dx, 0389h ; @155D
    mov al, bl ; @1560
    out dx, al ; @1562
    sti ; @1563
    mov ax, 2 ; @1564
    call far ptr DelaySoundIo ; @1567 same-segment far call
loc_156B:
    pop dx ; @156B
    pop cx ; @156C
    pop bx ; @156D
    pop ax ; @156E
    leave ; @156F
    retf ; @1570
; CONTRACT (tools/apply.py)
; Set per-OPL-channel gain and reapply saved volume, or update the displaced gain byte.
; In: far cdecl channel [BP+6] low byte<9, gain [BP+8] low byte; event handlers call this.
; Displaced path needs CurrentAdlxSlot>=12, reservations, and channel>=9-reserved count;
; it does not additionally test MainAdlxPlaying. Preserves CX/DX/SI; AX/BX may change.
; END CONTRACT
SetAdlibChannelGain:
    enter 0, 0 ; @1571
    push cx ; @1575
    push dx ; @1576
    push si ; @1577
    mov cl, byte ptr [bp + 6] ; @1578
    cmp cl, 9 ; @157B
    jae loc_15B7 ; @157E
    mov dl, byte ptr [bp + 8] ; @1583
    mov ax, 014h ; @1586
    mul cl ; @1589
    mov si, ax ; @158B
    cmp word ptr cs:[CurrentAdlxSlot], 0Ch ; @158D
    jb loc_15BC ; @1593
    test word ptr cs:[ReservedAdlibChannelCount], 0Fh ; @1598
    je loc_15BC ; @159F
    mov bl, 9 ; @15A4
    sub bl, byte ptr cs:[ReservedAdlibChannelCount] ; @15A6
    cmp cl, bl ; @15AB
    jb loc_15BC ; @15AD
    mov byte ptr cs:[si + DisplacedAdlibGain], dl ; @15B2
loc_15B7:
    pop si ; @15B7
    pop dx ; @15B8
    pop cx ; @15B9
    leave ; @15BA
    retf ; @15BB
loc_15BC:
    mov byte ptr cs:[si + AdlibChannelGain], dl ; @15BC
    push word ptr cs:[si + AdlibChannelVolume] ; @15C1
    push cx ; @15C6
    call far ptr SetAdlibChannelVolume ; @15C7 same-segment far call
    add sp, 4 ; @15CB
    pop si ; @15CE
    pop dx ; @15CF
    pop cx ; @15D0
    leave ; @15D1
    retf ; @15D2
; CONTRACT (tools/apply.py)
; Fetch ADLX bytes at ES:DI and tail-dispatch on the high nibble through CS:174Bh.
; In: main-track state and reserved AdLib channels; no bounds checks.
; Out: wait/end handlers RETF to this interpreter caller; other handlers tail-loop.
; END CONTRACT
RunMainAdlxEvents:
    mov al, byte ptr es:[di] ; @15D3
    inc di ; @15D6
    xor ah, ah ; @15D7
    mov bx, ax ; @15D9
    shr bx, 3 ; @15DB
    and bx, 0FFFEh ; @15DE
    add bx, offset MainAdlxDispatchTable ; @15E1
    jmp word ptr cs:[bx] ; @15E5
; CONTRACT (tools/apply.py)
; Main ADLX 0n: consume one byte, add (((n<<8)|byte)<<7) modulo 65536 to deadline.
; Out: carry extends the wrapped delta into CS:022Ch; saves DI at CS:021Ch; RETF.
; Preserves DX; uses the dispatch caller far return frame, not a new handler frame.
; END CONTRACT
HandleMainAdlxLongWait:
    push dx ; @15E8
    mov dl, byte ptr es:[di] ; @15E9
    inc di ; @15EC
    mov dh, al ; @15ED
    and dh, 0Fh ; @15EF
    shl dx, 7 ; @15F2
    add word ptr cs:[MainAdlxDeadlineLow], dx ; @15F5
    adc word ptr cs:[MainAdlxDeadlineHigh], 0 ; @15FA
    mov word ptr cs:[MainAdlxCursor], di ; @1600
    pop dx ; @1605
    retf ; @1606
; CONTRACT (tools/apply.py)
; Main ADLX 1n: consume LE16 frequency only for n<9; apply or save displaced value.
; Out: tail-dispatch next event; invalid n consumes no payload (original behavior).
; END CONTRACT
HandleMainAdlxFrequency:
    and al, 0Fh ; @1607
    cmp al, 9 ; @1609
    jae loc_1639 ; @160B
    push dx ; @1610
    push cx ; @1611
    push si ; @1612
    mov cl, al ; @1613
    mov ax, word ptr es:[di] ; @1615
    add di, 2 ; @1618
    mov bl, 9 ; @161B
    sub bl, byte ptr cs:[ReservedAdlibChannelCount] ; @161D
    cmp cl, bl ; @1622
    jb loc_163B ; @1624
    push ax ; @1629
    mov ax, 014h ; @162A
    mul cl ; @162D
    mov bx, ax ; @162F
    pop word ptr cs:[bx + DisplacedAdlibFrequency] ; @1631
    pop si ; @1636
    pop cx ; @1637
    pop dx ; @1638
loc_1639:
    jmp short RunMainAdlxEvents ; @1639
loc_163B:
    push ax ; @163B
    push cx ; @163C
    call far ptr SetAdlibFrequency ; @163D same-segment far call
    add sp, 4 ; @1641
    pop si ; @1644
    pop cx ; @1645
    pop dx ; @1646
    jmp short RunMainAdlxEvents ; @1647
; CONTRACT (tools/apply.py)
; Main ADLX 2n: key off n<9, or clear bit 5 in its displaced saved frequency.
; Out: tail-dispatch next event; invalid n has no channel effect.
; END CONTRACT
HandleMainAdlxKeyOff:
    and al, 0Fh ; @1649
    cmp al, 9 ; @164B
    jae loc_166F ; @164D
    mov bl, 9 ; @1652
    sub bl, byte ptr cs:[ReservedAdlibChannelCount] ; @1654
    cmp al, bl ; @1659
    jb loc_1672 ; @165B
    mov bl, al ; @1660
    mov ax, 014h ; @1662
    mul bl ; @1665
    mov bx, ax ; @1667
    and word ptr cs:[bx + DisplacedAdlibFrequency], 0FFDFh ; @1669
loc_166F:
    jmp near ptr RunMainAdlxEvents ; @166F
loc_1672:
    push ax ; @1672
    call far ptr KeyOffAdlibChannel ; @1673 same-segment far call
    add sp, 2 ; @1677
    jmp near ptr RunMainAdlxEvents ; @167A
; CONTRACT (tools/apply.py)
; Main ADLX 3n: apply one-byte channel gain through 1571h when n<9.
; Out: always advances DI by one payload byte, then tail-dispatches.
; END CONTRACT
HandleMainAdlxGain:
    and al, 0Fh ; @167D
    cmp al, 9 ; @167F
    jae loc_1692 ; @1681
    mov bl, byte ptr es:[di] ; @1686
    push bx ; @1689
    push ax ; @168A
    call far ptr SetAdlibChannelGain ; @168B same-segment far call
    add sp, 4 ; @168F
loc_1692:
    inc di ; @1692
    jmp near ptr RunMainAdlxEvents ; @1693
; CONTRACT (tools/apply.py)
; Main ADLX 4n: load instrument at ES:DI for n<9, then advance DI by 11 bytes.
; Quirk: invalid n consumes no payload; 1377h copies 12 bytes; tail-dispatches.
; END CONTRACT
HandleMainAdlxInstrument:
    and al, 0Fh ; @1696
    cmp al, 9 ; @1698
    jae loc_16AC ; @169A
    push es ; @169F
    push di ; @16A0
    push ax ; @16A1
    call far ptr LoadAdlibInstrument ; @16A2 same-segment far call
    add sp, 6 ; @16A6
    add di, 0Bh ; @16A9
loc_16AC:
    jmp near ptr RunMainAdlxEvents ; @16AC
; CONTRACT (tools/apply.py)
; Main ADLX 5n: ignore the opcode and tail-dispatch without consuming payload.
; END CONTRACT
HandleMainAdlxNoOp:
    jmp near ptr RunMainAdlxEvents ; @16AF
; CONTRACT (tools/apply.py)
; Main ADLX 6n: consume BE16 period into CS:000Ch; change timer slot CS:1122h.
; Out: requests CX:BX=0:period through TIMER:02C1h, then tail-dispatches; preserves CX.
; END CONTRACT
HandleMainAdlxTimerPeriod:
    push cx ; @16B2
    mov bx, word ptr es:[di] ; @16B3
    xchg bl, bh ; @16B6
    mov word ptr cs:[AdlxTimerPeriod], bx ; @16B8
    mov ax, word ptr cs:[AdlxPlaybackTimerHandle] ; @16BD
    xor cx, cx ; @16C1
    call far ptr _SetTimerCallbackInterval ; @16C3
    inc di ; @16C8
    inc di ; @16C9
    pop cx ; @16CA
    jmp near ptr RunMainAdlxEvents ; @16CB
; CONTRACT (tools/apply.py)
; Main ADLX 7n: 77h ends/repeats; 70h consumes 3 bytes; others skip length+payload.
; Out: 77h decrements repeats unless flag bit 1; expiration clears active bit only.
; Repeat restores track pointer and rebases deadline/elapsed origin to sound clock;
; 77h RETF returns to interpreter caller; extension skips tail-dispatch.
; END CONTRACT
HandleMainAdlxControl:
    cmp al, 077h ; @16CE
    je loc_16F1 ; @16D0
    mov ah, byte ptr es:[di] ; @16D5
    inc di ; @16D8
    and al, 0Fh ; @16D9
    cmp al, 0 ; @16DB
    je loc_16EB ; @16DD
    mov al, ah ; @16E2
    xor ah, ah ; @16E4
    add di, ax ; @16E6
    jmp near ptr RunMainAdlxEvents ; @16E8
loc_16EB:
    add di, 2 ; @16EB
    jmp near ptr RunMainAdlxEvents ; @16EE
loc_16F1:
    test word ptr cs:[MainAdlxFlags], 2 ; @16F1
    jne loc_170E ; @16F8
    dec word ptr cs:[MainAdlxRepeatCount] ; @16FD
    jg loc_170E ; @1702
    and word ptr cs:[MainAdlxFlags], 0FFFEh ; @1707
    retf ; @170D
loc_170E:
    mov ax, word ptr cs:[MainAdlxStartSegment] ; @170E
    mov word ptr cs:[MainAdlxCursorSegment], ax ; @1712
    mov ax, word ptr cs:[MainAdlxStartPointer] ; @1716
    mov word ptr cs:[MainAdlxCursor], ax ; @171A
    mov ax, word ptr cs:[AdlxTickCount] ; @171E
    mov word ptr cs:[MainAdlxDeadlineLow], ax ; @1722
    mov word ptr cs:[MainAdlxTimeOrigin], ax ; @1726
    mov ax, word ptr cs:[AdlxTickHighWord] ; @172A
    mov word ptr cs:[MainAdlxDeadlineHigh], ax ; @172E
    mov word ptr cs:[MainAdlxTimeOriginHigh], ax ; @1732
    retf ; @1736
; CONTRACT (tools/apply.py)
; Main ADLX 80h..FFh: add opcode&7Fh to the 32-bit deadline and save cursor DI.
; Out: RETF to interpreter caller; uses the existing far return frame.
; END CONTRACT
HandleMainAdlxShortWait:
    and ax, word ptr 07Fh ; @1737
    add word ptr cs:[MainAdlxDeadlineLow], ax ; @173A
    adc word ptr cs:[MainAdlxDeadlineHigh], 0 ; @173F
    mov word ptr cs:[MainAdlxCursor], di ; @1745
    retf ; @174A
; CONTRACT (tools/apply.py)
; Physical 16-word relocated handler table; MainAdlxDispatchTable is the indexed address view.
; END CONTRACT
MainAdlxDispatchStorage:
    dw offset HandleMainAdlxLongWait
    dw offset HandleMainAdlxFrequency
    dw offset HandleMainAdlxKeyOff
    dw offset HandleMainAdlxGain
    dw offset HandleMainAdlxInstrument
    dw offset HandleMainAdlxNoOp
    dw offset HandleMainAdlxTimerPeriod
    dw offset HandleMainAdlxControl
    dw offset HandleMainAdlxShortWait
    dw offset HandleMainAdlxShortWait
    dw offset HandleMainAdlxShortWait
    dw offset HandleMainAdlxShortWait
    dw offset HandleMainAdlxShortWait
    dw offset HandleMainAdlxShortWait
    dw offset HandleMainAdlxShortWait
    dw offset HandleMainAdlxShortWait
; CONTRACT (tools/apply.py)
; Fetch effect ADLX bytes at ES:DI and tail-dispatch through CS:1919h.
; In: CS:10EFh points to the selected 42-byte effect record; no bounds checks.
; Out: wait/end handlers RETF to interpreter caller; other handlers tail-loop.
; END CONTRACT
RunEffectAdlxEvents:
    mov al, byte ptr es:[di] ; @176B
    inc di ; @176E
    xor ah, ah ; @176F
    mov bx, ax ; @1771
    shr bx, 3 ; @1773
    and bx, 0FFFEh ; @1776
    add bx, offset EffectAdlxDispatchTable ; @1779
    jmp word ptr cs:[bx] ; @177D
; CONTRACT (tools/apply.py)
; Effect ADLX 0n: consume byte, wrap long-wait delta to 16 bits, multiply by Q8 scale.
; Out: add product>>8 (24 bits) to record deadline, save DI cursor, RETF; preserves DX.
; END CONTRACT
HandleEffectAdlxLongWait:
    push dx ; @1780
    mov dl, byte ptr es:[di] ; @1781
    inc di ; @1784
    mov dh, al ; @1785
    and dh, 0Fh ; @1787
    shl dx, 7 ; @178A
    mov bx, word ptr cs:[CurrentAdlxRecordOffset] ; @178D
    mov ax, dx ; @1792
    xor dx, dx ; @1794
    mul word ptr cs:[bx + 026h] ; @1796
    mov al, ah ; @179A
    mov ah, dl ; @179C
    mov dl, dh ; @179E
    xor dh, dh ; @17A0
    add word ptr cs:[bx + 01Eh], ax ; @17A2
    adc word ptr cs:[bx + 020h], dx ; @17A6
    mov word ptr cs:[bx + 010h], di ; @17AA
    pop dx ; @17AE
    retf ; @17AF
; CONTRACT (tools/apply.py)
; Effect ADLX 1n: add record channel base to n with 8-bit wrap; apply LE16 if result<9.
; Out: advances DI by 2 only on valid channel; tail-dispatches.
; END CONTRACT
HandleEffectAdlxFrequency:
    and al, 0Fh ; @17B0
    mov bx, word ptr cs:[CurrentAdlxRecordOffset] ; @17B2
    add al, byte ptr cs:[bx + 024h] ; @17B7
    cmp al, 9 ; @17BB
    jae loc_17D0 ; @17BD
    push word ptr es:[di] ; @17C2
    push ax ; @17C5
    call far ptr SetAdlibFrequency ; @17C6 same-segment far call
    add sp, 4 ; @17CA
    add di, 2 ; @17CD
loc_17D0:
    jmp short RunEffectAdlxEvents ; @17D0
; CONTRACT (tools/apply.py)
; Effect ADLX 2n: add record channel base to n with 8-bit wrap; key off if result<9.
; Out: tail-dispatch next event.
; END CONTRACT
HandleEffectAdlxKeyOff:
    and al, 0Fh ; @17D2
    mov bx, word ptr cs:[CurrentAdlxRecordOffset] ; @17D4
    add al, byte ptr cs:[bx + 024h] ; @17D9
    cmp al, 9 ; @17DD
    jae loc_17EC ; @17DF
    push ax ; @17E4
    call far ptr KeyOffAdlibChannel ; @17E5 same-segment far call
    add sp, 2 ; @17E9
loc_17EC:
    jmp near ptr RunEffectAdlxEvents ; @17EC
; CONTRACT (tools/apply.py)
; Effect ADLX 3n: apply gain byte for wrapped base+n<9, then always advance DI by one.
; Quirk: pushes a word from ES:DI although gain helper uses its low byte; tail-dispatches.
; END CONTRACT
HandleEffectAdlxGain:
    and al, 0Fh ; @17EF
    mov bx, word ptr cs:[CurrentAdlxRecordOffset] ; @17F1
    add al, byte ptr cs:[bx + 024h] ; @17F6
    cmp al, 9 ; @17FA
    jae loc_180C ; @17FC
    push word ptr es:[di] ; @1801
    push ax ; @1804
    call far ptr SetAdlibChannelGain ; @1805 same-segment far call
    add sp, 4 ; @1809
loc_180C:
    inc di ; @180C
    jmp near ptr RunEffectAdlxEvents ; @180D
; CONTRACT (tools/apply.py)
; Effect ADLX 4n: accept wrapped base+n<=9, stamp owner and call instrument loader.
; Quirk: channel 9 writes CS:033Ch although loader rejects it; DI still advances 11.
; Values above 9 skip no payload. Loader copies 12 bytes; tail-dispatches.
; END CONTRACT
HandleEffectAdlxInstrument:
    and al, 0Fh ; @1810
    mov bx, word ptr cs:[CurrentAdlxRecordOffset] ; @1812
    add al, byte ptr cs:[bx + 024h] ; @1817
    cmp al, 9 ; @181B
    ja loc_1844 ; @181D
    push ax ; @1822
    push word ptr cs:[CurrentAdlxSlot] ; @1823
    mov bl, al ; @1828
    mov ax, 014h ; @182A
    mul bl ; @182D
    mov bx, ax ; @182F
    pop word ptr cs:[bx + AdlibChannelOwnerSlot] ; @1831
    pop ax ; @1836
    push es ; @1837
    push di ; @1838
    push ax ; @1839
    call far ptr LoadAdlibInstrument ; @183A same-segment far call
    add sp, 6 ; @183E
    add di, 0Bh ; @1841
loc_1844:
    jmp near ptr RunEffectAdlxEvents ; @1844
; CONTRACT (tools/apply.py)
; Effect ADLX 5n: ignore opcode and tail-dispatch without consuming payload.
; END CONTRACT
HandleEffectAdlxNoOp:
    jmp near ptr RunEffectAdlxEvents ; @1847
; CONTRACT (tools/apply.py)
; Effect ADLX 6n: consume BE16 period. If music inactive and global period zero,
; set global period and timer slot; otherwise set effect Q8 scale=request/global.
; Quirk: music active with global period zero divides by zero; preserves CX/DX.
; END CONTRACT
HandleEffectAdlxTimerPeriod:
    push cx ; @184A
    push dx ; @184B
    test word ptr cs:[MainAdlxPlaying], 1 ; @184C
    jne loc_187C ; @1853
    test word ptr cs:[AdlxTimerPeriod], 0FFFFh ; @1858
    jne loc_187C ; @185F
    mov bx, word ptr es:[di] ; @1864
    xchg bl, bh ; @1867
    mov word ptr cs:[AdlxTimerPeriod], bx ; @1869
    mov ax, word ptr cs:[AdlxPlaybackTimerHandle] ; @186E
    xor cx, cx ; @1872
    call far ptr _SetTimerCallbackInterval ; @1874
    jmp loc_1895 ; @1879
loc_187C:
    xor dx, dx ; @187C
    mov bx, word ptr cs:[AdlxTimerPeriod] ; @187E
    mov ax, word ptr es:[di] ; @1883
    mov dl, al ; @1886
    xor al, al ; @1888
    div bx ; @188A
    mov bx, word ptr cs:[CurrentAdlxRecordOffset] ; @188C
    mov word ptr cs:[bx + 026h], ax ; @1891
loc_1895:
    inc di ; @1895
    inc di ; @1896
    pop dx ; @1897
    pop cx ; @1898
    jmp near ptr RunEffectAdlxEvents ; @1899
; CONTRACT (tools/apply.py)
; Effect ADLX 7n: skip extension payloads or handle 77h end/repeat using record flags.
; Out: expiration calls C:1768h with CS:0274h; repeat resets record far cursor only.
; 77h RETF returns to interpreter caller; extension skips tail-dispatch.
; END CONTRACT
HandleEffectAdlxControl:
    cmp al, 077h ; @189C
    je loc_18BF ; @189E
    mov ah, byte ptr es:[di] ; @18A3
    inc di ; @18A6
    and al, 0Fh ; @18A7
    cmp al, 0 ; @18A9
    je loc_18B9 ; @18AB
    mov al, ah ; @18B0
    xor ah, ah ; @18B2
    add di, ax ; @18B4
    jmp near ptr RunEffectAdlxEvents ; @18B6
loc_18B9:
    add di, 2 ; @18B9
    jmp near ptr RunEffectAdlxEvents ; @18BC
loc_18BF:
    mov bx, word ptr cs:[CurrentAdlxRecordOffset] ; @18BF
    test word ptr cs:[bx + 028h], 2 ; @18C4
    jne loc_18E6 ; @18CA
    dec word ptr cs:[bx + 4] ; @18CF
    jg loc_18E6 ; @18D3
    push word ptr cs:[CurrentAdlxSlot] ; @18D8
    call far ptr _StopAdlibTrackChannel ; @18DD
    add sp, 2 ; @18E2
    retf ; @18E5
loc_18E6:
    mov ax, word ptr cs:[bx + 8] ; @18E6
    mov word ptr cs:[bx + 012h], ax ; @18EA
    mov ax, word ptr cs:[bx + 6] ; @18EE
    mov word ptr cs:[bx + 010h], ax ; @18F2
    retf ; @18F6
; CONTRACT (tools/apply.py)
; Effect ADLX 80h..FFh: add low 16 bits of ((opcode&7Fh)*Q8scale)>>8 to deadline.
; Out: saves DI cursor, RETF to interpreter caller; preserves DX; no stream bounds check.
; END CONTRACT
HandleEffectAdlxShortWait:
    push dx ; @18F7
    and ax, word ptr 07Fh ; @18F8
    xor dx, dx ; @18FB
    mov bx, word ptr cs:[CurrentAdlxRecordOffset] ; @18FD
    mul word ptr cs:[bx + 026h] ; @1902
    mov al, ah ; @1906
    mov ah, dl ; @1908
    add word ptr cs:[bx + 01Eh], ax ; @190A
    adc word ptr cs:[bx + 020h], 0 ; @190E
    mov word ptr cs:[bx + 010h], di ; @1913
    pop dx ; @1917
    retf ; @1918
; CONTRACT (tools/apply.py)
; Physical 16-word relocated handler table; EffectAdlxDispatchTable is the indexed address view.
; END CONTRACT
EffectAdlxDispatchStorage:
    dw offset HandleEffectAdlxLongWait
    dw offset HandleEffectAdlxFrequency
    dw offset HandleEffectAdlxKeyOff
    dw offset HandleEffectAdlxGain
    dw offset HandleEffectAdlxInstrument
    dw offset HandleEffectAdlxNoOp
    dw offset HandleEffectAdlxTimerPeriod
    dw offset HandleEffectAdlxControl
    dw offset HandleEffectAdlxShortWait
    dw offset HandleEffectAdlxShortWait
    dw offset HandleEffectAdlxShortWait
    dw offset HandleEffectAdlxShortWait
    dw offset HandleEffectAdlxShortWait
    dw offset HandleEffectAdlxShortWait
    dw offset HandleEffectAdlxShortWait
    dw offset HandleEffectAdlxShortWait
; CONTRACT (tools/apply.py)
; Timer callback: increment AdlxTickCount even while AdlxPlaybackGuard bit 0 prevents dispatch.
; Unguarded path sets the guard, runs due main events if MainAdlxPlaying bit 0, then effects 8..11.
; Main loop: if MainAdlxSectionLoopEnabled bit 0 and cursor offset>=MainAdlxSectionEnd offset,
; call C:ApplyScannedMusicEvents to restore section-start state, then reload the far cursor.
; This is recurring: restore leaves the enable flag set, ignores threshold segment, and rebases
; MainAdlxTimeOrigin without changing AdlxTickCount/deadline. Effect records require flags&5==5.
; Preserves AX/BX/DX and ES/DI around interpreters; clears guard without restoring its prior word.
; END CONTRACT
TickAdlxPlayback:
    inc word ptr cs:[AdlxTickCount] ; @1939
    jne loc_1948 ; @193E
    inc word ptr cs:[AdlxTickHighWord] ; @1943
loc_1948:
    test word ptr cs:[AdlxPlaybackGuard], 1 ; @1948
    jne loc_1A36 ; @194F JUMPS expansion
loc_1954:
    mov word ptr cs:[AdlxPlaybackGuard], 1 ; @1954
    push ax ; @195B
    push bx ; @195C
    push dx ; @195D
    test word ptr cs:[MainAdlxPlaying], 1 ; @195E
    je loc_19C9 ; @1965
    mov dx, word ptr cs:[AdlxTickHighWord] ; @196A
    cmp dx, word ptr cs:[MainAdlxDeadlineHigh] ; @196F
    jb loc_19C9 ; @1974
    ja loc_198C ; @1979
    mov ax, word ptr cs:[AdlxTickCount] ; @197E
    cmp ax, word ptr cs:[MainAdlxDeadlineLow] ; @1982
    jb loc_19C9 ; @1987
loc_198C:
    mov word ptr cs:[CurrentAdlxRecordOffset], 020Ch ; @198C
    mov word ptr cs:[CurrentAdlxSlot], 0Ch ; @1993
    push es ; @199A
    push di ; @199B
    push bx ; @199C
    les di, dword ptr cs:[MainAdlxCursor] ; @199D
    test word ptr cs:[MainAdlxSectionLoopEnabled], 1 ; @19A2
    je loc_19C2 ; @19A9
    cmp di, word ptr cs:[MainAdlxSectionEnd] ; @19AE
    jb loc_19C2 ; @19B3
    call far ptr _ApplyScannedMusicEvents ; @19B8
    les di, dword ptr cs:[MainAdlxCursor] ; @19BD
loc_19C2:
    call far ptr RunMainAdlxEvents ; @19C2 same-segment far call
    pop bx ; @19C6
    pop di ; @19C7
    pop es ; @19C8
loc_19C9:
    test word ptr cs:[ReservedAdlibChannelCount], 0Fh ; @19C9
    je loc_1A2C ; @19D0
    mov bx, 0164h ; @19D5
    mov word ptr cs:[CurrentAdlxSlot], 8 ; @19D8
loc_19DF:
    mov al, byte ptr cs:[bx + 028h] ; @19DF
    and al, 5 ; @19E3
    cmp al, 5 ; @19E5
    jne loc_1A1E ; @19E7
    mov ax, word ptr cs:[AdlxTickHighWord] ; @19EC
    cmp ax, word ptr cs:[bx + 020h] ; @19F0
    jb loc_1A1E ; @19F4
    ja loc_1A0B ; @19F9
    mov ax, word ptr cs:[AdlxTickCount] ; @19FE
    cmp ax, word ptr cs:[bx + 01Eh] ; @1A02
    jb loc_1A1E ; @1A06
loc_1A0B:
    mov word ptr cs:[CurrentAdlxRecordOffset], bx ; @1A0B
    push es ; @1A10
    push di ; @1A11
    push bx ; @1A12
    les di, dword ptr cs:[bx + 010h] ; @1A13
    call far ptr RunEffectAdlxEvents ; @1A17 same-segment far call
    pop bx ; @1A1B
    pop di ; @1A1C
    pop es ; @1A1D
loc_1A1E:
    inc word ptr cs:[CurrentAdlxSlot] ; @1A1E
    add bx, 02Ah ; @1A23
    cmp bx, word ptr 020Ch ; @1A26
    jb short loc_19DF ; @1A2A
loc_1A2C:
    mov word ptr cs:[AdlxPlaybackGuard], 0 ; @1A2C
    pop dx ; @1A33
    pop bx ; @1A34
    pop ax ; @1A35
loc_1A36:
    retf ; @1A36
; CONTRACT (tools/apply.py)
; Write OPL register 01h=0 then 01h=20h; set both operators of all 9 channels to 3Fh.
; Preserves SI; clobbers BX/CX; does not clear channel key-on state in saved records.
; END CONTRACT
SilenceAdlibOperators:
    push si ; @1A37
    mov bx, 0100h ; @1A38
    call far ptr WriteAdlibRegister ; @1A3B same-segment far call
    mov bx, 0120h ; @1A3F
    call far ptr WriteAdlibRegister ; @1A42 same-segment far call
    mov cx, 9 ; @1A46
    xor si, si ; @1A49
loc_1A4B:
    mov bh, byte ptr cs:[si + AdlibOperatorOffsets] ; @1A4B
    add bh, 040h ; @1A50
    mov bl, 03Fh ; @1A53
    call far ptr WriteAdlibRegister ; @1A55 same-segment far call
    add bh, 3 ; @1A59
    call far ptr WriteAdlibRegister ; @1A5C same-segment far call
    inc si ; @1A60
    loop loc_1A4B ; @1A61
    pop si ; @1A63
    retf ; @1A64
; CONTRACT (tools/apply.py)
; Cancel playback timer slot if attempted-init byte CS:1126h is nonzero.
; Restore timer interrupt, clear attempted-init byte, and silence AdLib operators.
; Quirk: init failures also leave that byte set, so the stored handle may be stale.
; END CONTRACT
ShutdownAdlibPlayback:
    cmp byte ptr cs:[AdlibInitAttempted], 0 ; @1A65
    je loc_1A79 ; @1A6B
    mov ax, word ptr cs:[AdlxPlaybackTimerHandle] ; @1A70
    call far ptr _RemoveTimerCallback ; @1A74
loc_1A79:
    call far ptr _RestoreTimerInterrupt ; @1A79
    mov byte ptr cs:[AdlibInitAttempted], 0 ; @1A7E
    call far ptr SilenceAdlibOperators ; @1A84 same-segment far call
    retf ; @1A88
; CONTRACT (tools/apply.py)
; Calibrate delays, probe OPL timer status at 0388h, silence operators, install timer.
; Out: AX=1 success/already attempted, AX=0 failed probe; period initially 0000:1843h.
; Preserves ES/DI/SI. Sets CS:1126h before probing and leaves it set on failure;
; a second call therefore reports success without retrying or registering a slot.
; END CONTRACT
InitializeAdlibPlayback:
    push es ; @1A89
    push di ; @1A8A
    push si ; @1A8B
    cmp byte ptr cs:[AdlibInitAttempted], 0 ; @1A8C
loc_1A92:
    jne loc_1B2D ; @1A92 JUMPS expansion
loc_1A97:
    mov byte ptr cs:[AdlibInitAttempted], 1 ; @1A97
    call far ptr CalibrateSoundDelay ; @1A9D same-segment far call
    mov bx, 0100h ; @1AA1
    call far ptr WriteAdlibRegister ; @1AA4 same-segment far call
    mov bx, 0460h ; @1AA8
    call far ptr WriteAdlibRegister ; @1AAB same-segment far call
    mov al, 014h ; @1AAF
    call far ptr DelaySoundIo ; @1AB1 same-segment far call
    mov bx, 0480h ; @1AB5
    call far ptr WriteAdlibRegister ; @1AB8 same-segment far call
    mov al, 014h ; @1ABC
    call far ptr DelaySoundIo ; @1ABE same-segment far call
    mov dx, 0388h ; @1AC2
    in al, dx ; @1AC5
    test al, 0E0h ; @1AC6
loc_1AC8:
    jne loc_1B34 ; @1AC8
    mov bx, 02FFh ; @1ACD
loc_1AD0:
    call far ptr WriteAdlibRegister ; @1AD0 same-segment far call
    mov al, 014h ; @1AD4
    call far ptr DelaySoundIo ; @1AD6 same-segment far call
    mov bx, 0421h ; @1ADA
    call far ptr WriteAdlibRegister ; @1ADD same-segment far call
    mov al, 0FFh ; @1AE1
    call far ptr DelaySoundIo ; @1AE3 same-segment far call
    in al, dx ; @1AE7
    test al, 0E0h ; @1AE8
loc_1AEA:
    je loc_1B34 ; @1AEA
    mov bx, 0460h ; @1AEF
    call far ptr WriteAdlibRegister ; @1AF2 same-segment far call
    mov al, 014h ; @1AF6
    call far ptr DelaySoundIo ; @1AF8 same-segment far call
    mov bx, 0480h ; @1AFC
    call far ptr WriteAdlibRegister ; @1AFF same-segment far call
    mov al, 014h ; @1B03
    call far ptr DelaySoundIo ; @1B05 same-segment far call
    call far ptr SilenceAdlibOperators ; @1B09 same-segment far call
    mov bx, 0120h ; @1B0D
    call far ptr WriteAdlibRegister ; @1B10 same-segment far call
loc_1B14:
    call far ptr _InstallTimerInterrupt ; @1B14
    mov bx, 01843h ; @1B19
    xor cx, cx ; @1B1C
    mov ax, offset TickAdlxPlayback ; @1B1E
loc_1B21:
    mov dx, seg SOUNDSEG ; @1B21
loc_1B24:
    call far ptr _RegisterTimerCallback ; @1B24
    mov word ptr cs:[AdlxPlaybackTimerHandle], ax ; @1B29
loc_1B2D:
    mov ax, 1 ; @1B2D
    pop si ; @1B30
    pop di ; @1B31
    pop es ; @1B32
    retf ; @1B33
loc_1B34:
    xor ax, ax ; @1B34
    pop si ; @1B36
    pop di ; @1B37
    pop es ; @1B38
    retf ; @1B39
; CONTRACT (tools/apply.py)
; Reset the word cursor at CS:0024h+AX*2Ah with 16-bit wrapping and no range check.
; Preserves BX/DX; AX becomes low product. Unreferenced pattern seed, reachability unproved.
; END CONTRACT
ResetSampleVoiceCursor:
    push dx ; @1B3A
    push bx ; @1B3B
    mov bx, 02Ah ; @1B3C
    mul bx ; @1B3F
    mov bx, ax ; @1B41
    mov word ptr cs:[bx + SampleVoicePairCursor], 0 ; @1B43
    pop bx ; @1B4A
    pop dx ; @1B4B
    retf ; @1B4C
; CONTRACT (tools/apply.py)
; Poll DSP write-status bit 7 at base+0Ch, then write command byte AL.
; Preserves AX/CX/DX; zero-initialized CX permits 65536 polls and still writes on timeout.
; Delay jumps are intentional instruction-time waits, not removable empty control flow.
; END CONTRACT
WriteSoundBlasterDsp:
    push dx ; @1B4D
    push ax ; @1B4E
    push cx ; @1B4F
    mov ah, al ; @1B50
    mov dx, word ptr cs:[DspBasePort] ; @1B52
    add dx, 0Ch ; @1B57
    xor cx, cx ; @1B5A
loc_1B5C:
    jmp loc_1B61 ; @1B5C
    nop ; @1B5F
    nop ; @1B60
loc_1B61:
    jmp loc_1B66 ; @1B61
    nop ; @1B64
    nop ; @1B65
loc_1B66:
    jmp loc_1B6B ; @1B66
    nop ; @1B69
    nop ; @1B6A
loc_1B6B:
    in al, dx ; @1B6B
    test al, 080h ; @1B6C
    loopne loc_1B5C ; @1B6E
    mov al, ah ; @1B70
    out dx, al ; @1B72
    pop cx ; @1B73
    pop ax ; @1B74
    pop dx ; @1B75
    retf ; @1B76
; CONTRACT (tools/apply.py)
; Program DMA channel 1 and DSP single-cycle 8-bit output command 14h.
; In: CH=physical page, DX=physical offset, BX=byte count (decremented for hardware).
; Out: unmasks DMA1; writes count-1 to DMA and DSP; restores BX/CX, clobbers AL.
; No zero-count or boundary validation; hardware I/O delay jumps must be retained.
; END CONTRACT
StartDmaSampleBlock:
    push cx ; @1B77
    dec bx ; @1B78
    mov al, 5 ; @1B79
    out 0Ah, al ; @1B7B
    jmp loc_1B82 ; @1B7D
    nop ; @1B80
    nop ; @1B81
loc_1B82:
    jmp loc_1B87 ; @1B82
    nop ; @1B85
    nop ; @1B86
loc_1B87:
    jmp loc_1B8C ; @1B87
    nop ; @1B8A
    nop ; @1B8B
loc_1B8C:
    mov al, 0 ; @1B8C
    out 0Ch, al ; @1B8E
    jmp loc_1B95 ; @1B90
    nop ; @1B93
    nop ; @1B94
loc_1B95:
    jmp loc_1B9A ; @1B95
    nop ; @1B98
    nop ; @1B99
loc_1B9A:
    jmp loc_1B9F ; @1B9A
    nop ; @1B9D
    nop ; @1B9E
loc_1B9F:
    mov al, 049h ; @1B9F
    out 0Bh, al ; @1BA1
    jmp loc_1BA8 ; @1BA3
    nop ; @1BA6
    nop ; @1BA7
loc_1BA8:
    jmp loc_1BAD ; @1BA8
    nop ; @1BAB
    nop ; @1BAC
loc_1BAD:
    jmp loc_1BB2 ; @1BAD
    nop ; @1BB0
    nop ; @1BB1
loc_1BB2:
    mov al, dl ; @1BB2
    out 2, al ; @1BB4
    jmp loc_1BBB ; @1BB6
    nop ; @1BB9
    nop ; @1BBA
loc_1BBB:
    jmp loc_1BC0 ; @1BBB
    nop ; @1BBE
    nop ; @1BBF
loc_1BC0:
    jmp loc_1BC5 ; @1BC0
    nop ; @1BC3
    nop ; @1BC4
loc_1BC5:
    mov al, dh ; @1BC5
    out 2, al ; @1BC7
    jmp loc_1BCE ; @1BC9
    nop ; @1BCC
    nop ; @1BCD
loc_1BCE:
    jmp loc_1BD3 ; @1BCE
    nop ; @1BD1
    nop ; @1BD2
loc_1BD3:
    jmp loc_1BD8 ; @1BD3
    nop ; @1BD6
    nop ; @1BD7
loc_1BD8:
    mov al, ch ; @1BD8
    out 083h, al ; @1BDA
    jmp loc_1BE1 ; @1BDC
    nop ; @1BDF
    nop ; @1BE0
loc_1BE1:
    jmp loc_1BE6 ; @1BE1
    nop ; @1BE4
    nop ; @1BE5
loc_1BE6:
    jmp loc_1BEB ; @1BE6
    nop ; @1BE9
    nop ; @1BEA
loc_1BEB:
    mov al, bl ; @1BEB
    out 3, al ; @1BED
    jmp loc_1BF4 ; @1BEF
    nop ; @1BF2
    nop ; @1BF3
loc_1BF4:
    jmp loc_1BF9 ; @1BF4
    nop ; @1BF7
    nop ; @1BF8
loc_1BF9:
    jmp loc_1BFE ; @1BF9
    nop ; @1BFC
    nop ; @1BFD
loc_1BFE:
    mov al, bh ; @1BFE
    out 3, al ; @1C00
    jmp loc_1C07 ; @1C02
    nop ; @1C05
    nop ; @1C06
loc_1C07:
    jmp loc_1C0C ; @1C07
    nop ; @1C0A
    nop ; @1C0B
loc_1C0C:
    jmp loc_1C11 ; @1C0C
    nop ; @1C0F
    nop ; @1C10
loc_1C11:
    mov al, 1 ; @1C11
    out 0Ah, al ; @1C13
    jmp loc_1C1A ; @1C15
    nop ; @1C18
    nop ; @1C19
loc_1C1A:
    jmp loc_1C1F ; @1C1A
    nop ; @1C1D
    nop ; @1C1E
loc_1C1F:
    jmp loc_1C24 ; @1C1F
    nop ; @1C22
    nop ; @1C23
loc_1C24:
    mov al, 014h ; @1C24
    call far ptr WriteSoundBlasterDsp ; @1C26 same-segment far call
    mov al, bl ; @1C2A
    call far ptr WriteSoundBlasterDsp ; @1C2C same-segment far call
    mov al, bh ; @1C30
    call far ptr WriteSoundBlasterDsp ; @1C32 same-segment far call
    inc bx ; @1C36
    pop cx ; @1C37
    retf ; @1C38
; CONTRACT (tools/apply.py)
; Set DSP time constant to low byte of -(1000000/rate) using command 40h.
; In: far cdecl unsigned rate [BP+6]; only acts for device bit 1 and rate>=1000.
; Preserves AX/BX/DX; integer division and low-byte truncation are observable.
; END CONTRACT
SetDspSampleRate:
    enter 0, 0 ; @1C39
    push ax ; @1C3D
    push bx ; @1C3E
    push dx ; @1C3F
    test word ptr cs:[SoundDeviceBits], 2 ; @1C40
    je loc_1C6F ; @1C47
    cmp word ptr [bp + 6], word ptr 03E8h ; @1C4C
    jb loc_1C6F ; @1C51
    mov dx, 0Fh ; @1C56
    mov ax, 04240h ; @1C59
    div word ptr [bp + 6] ; @1C5C
    neg ax ; @1C5F
    mov bx, ax ; @1C61
    mov al, 040h ; @1C63
    call far ptr WriteSoundBlasterDsp ; @1C65 same-segment far call
    mov al, bl ; @1C69
    call far ptr WriteSoundBlasterDsp ; @1C6B same-segment far call
loc_1C6F:
    pop dx ; @1C6F
    pop bx ; @1C70
    pop ax ; @1C71
    leave ; @1C72
    retf ; @1C73
; CONTRACT (tools/apply.py)
; Compute physical page/offset and CS offsets for two 0400h-byte mix buffers.
; Out: use CS:04AFh and 08B9h normally, substitute CS:0CC3h on 64K crossing.
; Quirk: the end comparison treats an exactly-64K end as crossing; AX/CX clobbered.
; END CONTRACT
LocateDmaMixBuffers:
    mov ax, seg SOUNDSEG ; @1C74
loc_1C77:
    mov cx, ax ; @1C77
    shr ch, 4 ; @1C79
    shl ax, 4 ; @1C7C
    add ax, word ptr 04AFh ; @1C7F
    adc ch, 0 ; @1C82
    mov word ptr cs:[DmaMixBufferOneAddress], ax ; @1C85
    mov word ptr cs:[DmaMixBufferOneOffset], 04AFh ; @1C89
    mov byte ptr cs:[DmaMixBufferOnePage], ch ; @1C90
    add ax, word ptr 0400h ; @1C95
    jae loc_1CB6 ; @1C98
    sub ax, word ptr 0400h ; @1C9D
    add ax, word ptr 0814h ; @1CA0
    adc ch, 0 ; @1CA3
    mov byte ptr cs:[DmaMixBufferOnePage], ch ; @1CA6
    mov word ptr cs:[DmaMixBufferOneAddress], ax ; @1CAB
    mov word ptr cs:[DmaMixBufferOneOffset], 0CC3h ; @1CAF
loc_1CB6:
    mov ax, seg SOUNDSEG ; @1CB6
    mov cx, ax ; @1CB9
    shr ch, 4 ; @1CBB
    shl ax, 4 ; @1CBE
    add ax, word ptr 08B9h ; @1CC1
    adc ch, 0 ; @1CC4
    mov word ptr cs:[DmaMixBufferTwoAddress], ax ; @1CC7
    mov word ptr cs:[DmaMixBufferTwoOffset], 08B9h ; @1CCB
    mov byte ptr cs:[DmaMixBufferTwoPage], ch ; @1CD2
    add ax, word ptr 0400h ; @1CD7
    jae loc_1CF8 ; @1CDA
    sub ax, word ptr 0400h ; @1CDF
    add ax, word ptr 040Ah ; @1CE2
    adc ch, 0 ; @1CE5
    mov byte ptr cs:[DmaMixBufferTwoPage], ch ; @1CE8
    mov word ptr cs:[DmaMixBufferTwoAddress], ax ; @1CED
    mov word ptr cs:[DmaMixBufferTwoOffset], 0CC3h ; @1CF1
loc_1CF8:
    retf ; @1CF8
; CONTRACT (tools/apply.py)
; Mix up to 8 signed-byte voices into unsigned byte pairs at CS:DX; BX=request bytes.
; Each voice reads DS:base+low16((cursor*step)>>8), scales by signed (volume>>1),
; and increments cursor once per pair; divide sums by current active count, add 7Fh.
; Preserves registers/DS via PUSHA except returned AX; CS:000Eh marks mixing busy.
; Quirks: effective offsets wrap at 16 bits; repeat resets cursor but skips this pair;
; early exit returns original BX minus remaining PAIRS, not produced byte count;
; odd/zero requests still enter the pair loop when any voice is active.
; END CONTRACT
MixSampleVoicePairs:
    xor ax, ax ; @1CF9
    cmp word ptr cs:[ActiveSampleVoiceCount], 0 ; @1CFB
    je loc_1DD5 ; @1D01 JUMPS expansion
loc_1D06:
    mov word ptr cs:[SampleMixerBusy], 1 ; @1D06
    pusha ; @1D0D
    push ds ; @1D0E
    shr bx, 1 ; @1D0F
    mov word ptr cs:[SampleMixPairsRemaining], bx ; @1D11
    mov di, dx ; @1D16
    xor bp, bp ; @1D18
    mov word ptr cs:[SampleMixFirstSum], 0 ; @1D1A
    mov word ptr cs:[SampleMixSecondSum], 0 ; @1D21
    mov cl, 1 ; @1D28
loc_1D2A:
    test byte ptr cs:[ActiveSampleVoiceMask], cl ; @1D2A
    je loc_1D7D ; @1D2F
    lds bx, dword ptr cs:[bp + SampleVoiceDataPointer] ; @1D34
    mov ax, word ptr cs:[bp + SampleVoicePairCursor] ; @1D39
    mul word ptr cs:[bp + SampleVoiceStepQ8] ; @1D3E
    mov al, ah ; @1D43
    mov ah, dl ; @1D45
    cmp ax, word ptr cs:[bp + SampleVoiceByteLength] ; @1D47
    jae loc_1DD6 ; @1D4C JUMPS expansion
loc_1D51:
    add ax, bx ; @1D51
    mov si, ax ; @1D53
    mov ch, byte ptr cs:[bp + SampleVoiceVolume] ; @1D55
    shr ch, 1 ; @1D5A
    mov dx, word ptr [si] ; @1D5C
    mov al, dl ; @1D5E
    imul ch ; @1D60
    mov al, ah ; @1D62
    cbw ; @1D64
    add word ptr cs:[SampleMixFirstSum], ax ; @1D65
    mov al, dh ; @1D6A
    imul ch ; @1D6C
    mov al, ah ; @1D6E
    cbw ; @1D70
    add word ptr cs:[SampleMixSecondSum], ax ; @1D71
    inc word ptr cs:[bp + SampleVoicePairCursor] ; @1D76
    sub si, bx ; @1D7B
loc_1D7D:
    add bp, 02Ah ; @1D7D
    shl cl, 1 ; @1D80
    jae short loc_1D2A ; @1D82
    mov ax, word ptr cs:[SampleMixFirstSum] ; @1D84
    cwd ; @1D88
    idiv word ptr cs:[ActiveSampleVoiceCount] ; @1D89
    add ax, word ptr 07Fh ; @1D8E
    mov byte ptr cs:[di], al ; @1D91
    inc di ; @1D94
    mov ax, word ptr cs:[SampleMixSecondSum] ; @1D95
    cwd ; @1D99
    idiv word ptr cs:[ActiveSampleVoiceCount] ; @1D9A
    add ax, word ptr 07Fh ; @1D9F
    mov byte ptr cs:[di], al ; @1DA2
    inc di ; @1DA5
    dec word ptr cs:[SampleMixPairsRemaining] ; @1DA6
    jle loc_1DC5 ; @1DAB
    mov word ptr cs:[SampleMixFirstSum], 0 ; @1DB0
    mov word ptr cs:[SampleMixSecondSum], 0 ; @1DB7
    mov cl, 1 ; @1DBE
    xor bp, bp ; @1DC0
    jmp near ptr loc_1D2A ; @1DC2
loc_1DC5:
    mov word ptr cs:[SampleMixerBusy], 0 ; @1DC5
    pop ds ; @1DCC
    popa ; @1DCD
    mov ax, bx ; @1DCE
    sub ax, word ptr cs:[SampleMixPairsRemaining] ; @1DD0
loc_1DD5:
    retf ; @1DD5
loc_1DD6:
    test word ptr cs:[bp + SampleVoiceFlags], 2 ; @1DD6
    jne loc_1DEC ; @1DDD
    dec word ptr cs:[bp + SampleVoiceRepeatCount] ; @1DE2
    jle loc_1DF5 ; @1DE7
loc_1DEC:
    mov word ptr cs:[bp + SampleVoicePairCursor], 0 ; @1DEC
    jmp short loc_1D7D ; @1DF3
loc_1DF5:
    xor byte ptr cs:[ActiveSampleVoiceMask], cl ; @1DF5
    dec word ptr cs:[ActiveSampleVoiceCount] ; @1DFA
    jle short loc_1DC5 ; @1DFF
    jmp near ptr loc_1D7D ; @1E01
; CONTRACT (tools/apply.py)
; Acknowledge PIC, guard reentry, acknowledge DSP at base+0Eh and ping-pong mix buffers.
; Start queued block if count>=28h; refill the other buffer through 1CF9h.
; Out: IRET; normal path preserves general/segment registers, but flags follow IRET.
; Quirk: reentry returns after PIC EOI without DSP acknowledgement; short queued count
; masks the selected IRQ. No old-handler chaining; mixing occurs in interrupt context.
; END CONTRACT
HandleSampleDmaInterrupt:
    push ax ; @1E04
    mov al, 020h ; @1E05
    out 020h, al ; @1E07
    pop ax ; @1E09
    test byte ptr cs:[DspIrqBusy], 1 ; @1E0A
    je loc_1E16 ; @1E10
    iret ; @1E15
loc_1E16:
    mov byte ptr cs:[DspIrqBusy], 1 ; @1E16
    pusha ; @1E1C
    push es ; @1E1D
    push ds ; @1E1E
    mov dx, word ptr cs:[DspBasePort] ; @1E1F
    add dx, 0Eh ; @1E24
    in al, dx ; @1E27
    xor si, si ; @1E28
    test byte ptr cs:[DmaMixBufferSelect], 1 ; @1E2A
    jne loc_1E38 ; @1E30
    mov si, 040Ah ; @1E35
loc_1E38:
    mov bx, word ptr cs:[si + DmaMixBufferOneCount] ; @1E38
    cmp bx, 028h ; @1E3D
    jb loc_1E7D ; @1E40
    xor byte ptr cs:[DmaMixBufferSelect], 1 ; @1E45
    mov dx, word ptr cs:[si + DmaMixBufferOneAddress] ; @1E4B
    mov ch, byte ptr cs:[si + DmaMixBufferOnePage] ; @1E50
    call far ptr StartDmaSampleBlock ; @1E55 same-segment far call
    mov word ptr cs:[si + DmaMixBufferOneCount], 0 ; @1E59
    neg si ; @1E60
    mov dx, word ptr cs:[si + DmaMixBufferTwoOffset] ; @1E62
    mov bx, 0400h ; @1E67
    call far ptr MixSampleVoicePairs ; @1E6A same-segment far call
    mov word ptr cs:[si + DmaMixBufferTwoCount], ax ; @1E6E
loc_1E73:
    pop ds ; @1E73
    pop es ; @1E74
    popa ; @1E75
    mov byte ptr cs:[DspIrqBusy], 0 ; @1E76
    iret ; @1E7C
loc_1E7D:
    in al, 021h ; @1E7D
    or al, byte ptr cs:[DspPicIrqMask] ; @1E7F
    jmp loc_1E89 ; @1E84
    nop ; @1E87
    nop ; @1E88
loc_1E89:
    jmp loc_1E8E ; @1E89
    nop ; @1E8C
    nop ; @1E8D
loc_1E8E:
    jmp loc_1E93 ; @1E8E
    nop ; @1E91
    nop ; @1E92
loc_1E93:
    out 021h, al ; @1E93
    jmp short loc_1E73 ; @1E95
; CONTRACT (tools/apply.py)
; If device bit 1 and active voice count>0, wait for mixer idle, halt DSP DMA (D0h),
; fill first buffer, unmask IRQ and enter 1E04h via PUSHF/far CALL (IRET-compatible).
; Out: sets first-buffer selection; same mixer and IRQ side effects as hardware entry.
; END CONTRACT
PrimeSampleDmaPlayback:
    test word ptr cs:[SoundDeviceBits], 2 ; @1E97
    je loc_1EF4 ; @1E9E
loc_1EA3:
    test word ptr cs:[SampleMixerBusy], 1 ; @1EA3
    jne short loc_1EA3 ; @1EAA
    cmp word ptr cs:[ActiveSampleVoiceCount], 0 ; @1EAC
    jle loc_1EF4 ; @1EB2
    mov al, 0D0h ; @1EB7
    call far ptr WriteSoundBlasterDsp ; @1EB9 same-segment far call
    mov dx, word ptr cs:[DmaMixBufferOneOffset] ; @1EBD
    mov bx, 0400h ; @1EC2
    call far ptr MixSampleVoicePairs ; @1EC5 same-segment far call
    mov word ptr cs:[DmaMixBufferOneCount], ax ; @1EC9
    mov byte ptr cs:[DmaMixBufferSelect], 1 ; @1ECD
    in al, 021h ; @1ED3
    mov ah, byte ptr cs:[DspPicIrqMask] ; @1ED5
    not ah ; @1EDA
    and al, ah ; @1EDC
    jmp loc_1EE3 ; @1EDE
    nop ; @1EE1
    nop ; @1EE2
loc_1EE3:
    jmp loc_1EE8 ; @1EE3
    nop ; @1EE6
    nop ; @1EE7
loc_1EE8:
    jmp loc_1EED ; @1EE8
    nop ; @1EEB
    nop ; @1EEC
loc_1EED:
    out 021h, al ; @1EED
    pushf ; @1EEF
    call far ptr HandleSampleDmaInterrupt ; @1EF0 same-segment far call
loc_1EF4:
    retf ; @1EF4
; CONTRACT (tools/apply.py)
; Temporary IRQ probe handler: send master PIC EOI, set CS:04A1h byte=1, IRET.
; Quirk: AL is clobbered and DSP status is not read.
; END CONTRACT
HandleDspProbeInterrupt:
    mov al, 020h ; @1EF5
    out 020h, al ; @1EF7
    mov byte ptr cs:[DspProbeIrqSeen], 1 ; @1EF9
    iret ; @1EFF
; CONTRACT (tools/apply.py)
; Locate mix buffers; scan bases 210h..260h and IRQ candidates 7,5,3,2.
; For each candidate replace its DOS vector, trigger 3-byte DMA, poll 1000h iterations,
; mask the candidate IRQ and restore its vector; success AX=1 leaves base/vector/mask.
; Out: failure AX=0, base=0 (vector=0 after candidate exhaustion); preserves DS/ES.
; Quirks: CX!=0 defines success, not probe flag; original PIC mask is not restored.
; END CONTRACT
ProbeSoundBlasterDmaIrq:
    push es ; @1F00
    push ds ; @1F01
    call far ptr LocateDmaMixBuffers ; @1F02 same-segment far call
    mov word ptr cs:[DspInterruptVector], 1 ; @1F06
    mov word ptr cs:[DspBasePort], 0200h ; @1F0D
loc_1F14:
    call far ptr _fn_013B_001F ; @1F14
    call far ptr _fn_013B_001F ; @1F19
    cmp word ptr cs:[DspBasePort], word ptr 0260h ; @1F1E
loc_1F25:
    jae loc_2044 ; @1F25 JUMPS expansion
loc_1F2A:
    add word ptr cs:[DspBasePort], 010h ; @1F2A
    call far ptr ResetSoundBlasterDsp ; @1F30 same-segment far call
    jb short loc_1F14 ; @1F35
    mov byte ptr cs:[DspProbeIrqSeen], 0 ; @1F37
    mov al, 0D3h ; @1F3D
    call far ptr WriteSoundBlasterDsp ; @1F3F same-segment far call
    call far ptr _fn_013B_001F ; @1F43
    call far ptr _fn_013B_001F ; @1F48
    xor bx, bx ; @1F4D
loc_1F4F:
    mov cl, byte ptr cs:[bx + DspProbeIrqOrder] ; @1F4F
    push bx ; @1F54
    mov al, cl ; @1F55
    add al, 8 ; @1F57
    mov byte ptr cs:[DspInterruptVector], al ; @1F59
    mov al, 1 ; @1F5D
    shl al, cl ; @1F5F
    mov byte ptr cs:[DspPicIrqMask], al ; @1F61
    mov ah, 035h ; @1F65
    mov al, byte ptr cs:[DspInterruptVector] ; @1F67
    int 021h ; @1F6B
    mov ax, es ; @1F6D
    mov word ptr cs:[PreviousDspVectorSegment], ax ; @1F6F
    mov word ptr cs:[PreviousDspVectorOffset], bx ; @1F73
    call far ptr _fn_013B_001F ; @1F78
    call far ptr _fn_013B_001F ; @1F7D
    in al, 021h ; @1F82
    or al, byte ptr cs:[DspPicIrqMask] ; @1F84
    jmp loc_1F8E ; @1F89
    nop ; @1F8C
    nop ; @1F8D
loc_1F8E:
    jmp loc_1F93 ; @1F8E
    nop ; @1F91
    nop ; @1F92
loc_1F93:
    jmp loc_1F98 ; @1F93
    nop ; @1F96
    nop ; @1F97
loc_1F98:
    out 021h, al ; @1F98
    call far ptr _fn_013B_001F ; @1F9A
    call far ptr _fn_013B_001F ; @1F9F
loc_1FA4:
    mov bx, seg SOUNDSEG ; @1FA4
loc_1FA7:
    mov dx, offset HandleDspProbeInterrupt ; @1FA7
    mov ah, 025h ; @1FAA
    mov al, byte ptr cs:[DspInterruptVector] ; @1FAC
    mov ds, bx ; @1FB0
    int 021h ; @1FB2
    call far ptr _fn_013B_001F ; @1FB4
    call far ptr _fn_013B_001F ; @1FB9
    in al, 021h ; @1FBE
    xor al, byte ptr cs:[DspPicIrqMask] ; @1FC0
    jmp loc_1FCA ; @1FC5
    nop ; @1FC8
    nop ; @1FC9
loc_1FCA:
    jmp loc_1FCF ; @1FCA
    nop ; @1FCD
    nop ; @1FCE
loc_1FCF:
    jmp loc_1FD4 ; @1FCF
    nop ; @1FD2
    nop ; @1FD3
loc_1FD4:
    out 021h, al ; @1FD4
    mov ch, byte ptr cs:[DmaMixBufferOnePage] ; @1FD6
    mov dx, word ptr cs:[DmaMixBufferOneAddress] ; @1FDB
    mov bx, 3 ; @1FE0
    call far ptr StartDmaSampleBlock ; @1FE3 same-segment far call
    mov cx, 01000h ; @1FE7
loc_1FEA:
    test byte ptr cs:[DspProbeIrqSeen], 1 ; @1FEA
    loope loc_1FEA ; @1FF0
    in al, 021h ; @1FF2
    or al, byte ptr cs:[DspPicIrqMask] ; @1FF4
    jmp loc_1FFE ; @1FF9
    nop ; @1FFC
    nop ; @1FFD
loc_1FFE:
    jmp loc_2003 ; @1FFE
    nop ; @2001
    nop ; @2002
loc_2003:
    jmp loc_2008 ; @2003
    nop ; @2006
    nop ; @2007
loc_2008:
    out 021h, al ; @2008
    call far ptr _fn_013B_001F ; @200A
    call far ptr _fn_013B_001F ; @200F
    mov ah, 025h ; @2014
    mov al, byte ptr cs:[DspInterruptVector] ; @2016
    lds dx, dword ptr cs:[PreviousDspVectorOffset] ; @201A
    int 021h ; @201F
    call far ptr _fn_013B_001F ; @2021
    call far ptr _fn_013B_001F ; @2026
    cmp cx, 0 ; @202B
    jne loc_2051 ; @202E
    pop bx ; @2033
    inc bx ; @2034
    cmp bx, 3 ; @2035
loc_2038:
    jbe loc_1F4F ; @2038 JUMPS expansion
loc_203D:
    mov word ptr cs:[DspInterruptVector], 0 ; @203D
loc_2044:
    mov word ptr cs:[DspBasePort], 0 ; @2044
    mov ax, 0 ; @204B
    pop ds ; @204E
    pop es ; @204F
    retf ; @2050
loc_2051:
    pop bx ; @2051
    mov ax, 1 ; @2052
    pop ds ; @2055
    pop es ; @2056
    retf ; @2057
; CONTRACT (tools/apply.py)
; Physical 4-byte candidate IRQ table: 7,5,3,2.
; END CONTRACT
DspProbeIrqOrderStorage:
    db 07h, 05h, 03h, 02h ; data 2058..205C
; CONTRACT (tools/apply.py)
; Calibrate delays and probe DSP/DMA IRQ; if found, save vector and install 1E04h.
; Out: AX=1 success or AX=0 failure; success unmasks IRQ and enables speaker (D1h).
; Preserves DS/ES; no repeat-install guard; DOS vectors and PIC mask are modified.
; END CONTRACT
InitializeDspPlayback:
    push ds ; @205C
    push es ; @205D
    call far ptr CalibrateSoundDelay ; @205E same-segment far call
    call far ptr ProbeSoundBlasterDmaIrq ; @2062 same-segment far call
    test ax, 1 ; @2066
loc_2069:
    je loc_20B6 ; @2069
    mov ah, 035h ; @206E
    mov al, byte ptr cs:[DspInterruptVector] ; @2070
    int 021h ; @2074
    mov ax, es ; @2076
    mov word ptr cs:[PreviousDspVectorSegment], ax ; @2078
    mov word ptr cs:[PreviousDspVectorOffset], bx ; @207C
loc_2081:
    mov ax, seg SOUNDSEG ; @2081
loc_2084:
    mov ds, ax ; @2084
    mov dx, offset HandleSampleDmaInterrupt ; @2086
    mov ah, 025h ; @2089
    mov al, byte ptr cs:[DspInterruptVector] ; @208B
    int 021h ; @208F
    in al, 021h ; @2091
    mov ah, byte ptr cs:[DspPicIrqMask] ; @2093
    not ah ; @2098
    and al, ah ; @209A
    jmp loc_20A1 ; @209C
    nop ; @209F
    nop ; @20A0
loc_20A1:
    jmp loc_20A6 ; @20A1
    nop ; @20A4
    nop ; @20A5
loc_20A6:
    jmp loc_20AB ; @20A6
    nop ; @20A9
    nop ; @20AA
loc_20AB:
    out 021h, al ; @20AB
    mov al, 0D1h ; @20AD
    call far ptr WriteSoundBlasterDsp ; @20AF same-segment far call
    mov ax, 1 ; @20B3
loc_20B6:
    pop es ; @20B6
    pop ds ; @20B7
    retf ; @20B8
; CONTRACT (tools/apply.py)
; Disable DSP speaker (D3h), mask selected IRQ, restore its saved DOS vector, reset DSP.
; Preserves DS; reset helper returns CF status. No installed-state check or PIC-mask restore.
; END CONTRACT
ShutdownDspPlayback:
    push ds ; @20B9
    mov al, 0D3h ; @20BA
    call far ptr WriteSoundBlasterDsp ; @20BC same-segment far call
    call far ptr _fn_013B_001F ; @20C0
    call far ptr _fn_013B_001F ; @20C5
    in al, 021h ; @20CA
    or al, byte ptr cs:[DspPicIrqMask] ; @20CC
    jmp loc_20D6 ; @20D1
    nop ; @20D4
    nop ; @20D5
loc_20D6:
    jmp loc_20DB ; @20D6
    nop ; @20D9
    nop ; @20DA
loc_20DB:
    jmp loc_20E0 ; @20DB
    nop ; @20DE
    nop ; @20DF
loc_20E0:
    out 021h, al ; @20E0
    call far ptr _fn_013B_001F ; @20E2
    call far ptr _fn_013B_001F ; @20E7
    mov ah, 025h ; @20EC
    mov al, byte ptr cs:[DspInterruptVector] ; @20EE
    lds dx, dword ptr cs:[PreviousDspVectorOffset] ; @20F2
    int 021h ; @20F7
    call far ptr _fn_013B_001F ; @20F9
    call far ptr _fn_013B_001F ; @20FE
    call far ptr ResetSoundBlasterDsp ; @2103 same-segment far call
    call far ptr _fn_013B_001F ; @2108
    call far ptr _fn_013B_001F ; @210D
    pop ds ; @2112
    retf ; @2113
; CONTRACT (tools/apply.py)
; Pulse DSP reset at base+6; delay with AL=3; poll bit 7 at base+0Eh up to 100 times.
; Out: CF clear iff the byte read at base+0Ah equals AAh, otherwise CF set.
; Quirk: reads and compares response even after timeout; AX/CX/DX and flags change.
; END CONTRACT
ResetSoundBlasterDsp:
    mov dx, word ptr cs:[DspBasePort] ; @2114
    add dx, 6 ; @2119
    mov al, 1 ; @211C
    out dx, al ; @211E
    mov ax, 3 ; @211F
    call far ptr DelaySoundIo ; @2122 same-segment far call
    xor al, al ; @2126
    out dx, al ; @2128
    add dx, 8 ; @2129
    mov cx, 064h ; @212C
loc_212F:
    in al, dx ; @212F
    test al, 080h ; @2130
    loope loc_212F ; @2132
    sub dx, 4 ; @2134
    in al, dx ; @2137
    cmp al, 0AAh ; @2138
    jne loc_2141 ; @213A
    clc ; @213F
    retf ; @2140
loc_2141:
    stc ; @2141
    retf ; @2142
sound_code_end:
SOUNDSEG ends
end
