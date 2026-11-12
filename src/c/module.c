/* JUDGE: -mh -2
 * BIND: AdlxPlaybackGuard 0664:0236
 * BIND: MainAdlxPlaying 0664:0256
 * BIND: MainAdlxSectionLoopEnabled 0664:025C
 * BIND: SoundDeviceBits 0664:026A
 * BIND: CancelMusicFade 0664:1331
 * BIND: ShutdownDspPlayback 0664:20B9
 * BIND: ShutdownAdlibPlayback 0664:1A65
 * BIND: AudioChannelStates 0664:0014
 * BIND: MusicTicksPerUnit 0664:0238
 * BIND: AdlxTickCount 0664:023A
 * BIND: MainAdlxTimeOrigin 0664:023E
 * OMF: F_LUDIV@ 0000:039D
 * BIND: SampleMixerBusy 0664:000E
 * BIND: SoundBankBase 0664:024E
 * BIND: SoundBankLength 0664:0252
 * BIND: ActiveSampleVoiceCount 0664:026E
 * BIND: ActiveSampleVoiceMask 0664:0270
 * BIND: ClearSoundState 0664:112B
 * BIND: InitializeDspPlayback 0664:205C
 * BIND: SetDspSampleRate 0664:1C39
 * BIND: InitializeAdlibPlayback 0664:1A89
 * BIND: PrimeSampleDmaPlayback 0664:1E97
 * BIND: fn_013B_001E 013B:001E
 * BIND: fn_013B_001F 013B:001F
 * BIND: fn_013B_001D 013B:001D
 * BIND: fn_013B_001C 013B:001C
 * OMF: F_PCMP@ 0000:0372
 * BIND: MainAdlxStartPointer 0664:0212
 * BIND: MusicEventStreamLength 0664:0216
 * BIND: MusicVoiceCount 0664:022E
 * BIND: ScannedMusicClockTicks 0664:0242
 * BIND: MusicFadeStep 0664:0246
 * BIND: MusicFadeDuration 0664:0248
 * BIND: MusicFadeStartVolume 0664:024A
 * BIND: MusicFadeTargetVolume 0664:024C
 * BIND: MusicFadeScheduled 0664:0258
 * BIND: MusicTrackVolume 0664:025A
 * BIND: AdlibInstrumentMap 0664:0266
 * BIND: ReservedAdlibChannelCount 0664:026C
 * BIND: CurrentAdlxSlot 0664:0274
 * BIND: AdlibVoiceStates 0664:0278
 * BIND: SavedAdlibVoiceStates 0664:032C
 * BIND: ScannedAdlibVoiceStates 0664:03E0
 * BIND: ScheduleMusicFade 0664:134E
 * BIND: SilenceAdlibOperators 0664:1A37
 * BIND: SetAdlibChannelVolume 0664:1211
 * BIND: KeyOffAdlibChannel 0664:14B1
 * BIND: CopyFarBytes 013B:0020
 * BIND: LoadAdlibInstrument 0664:1377
 * BIND: SetAdlibFrequency 0664:1503
 * BIND: MainAdlxCursor 0664:021C
 * BIND: FirstScannedEvent 0664:025E
 * OMF: F_PADD@ 0000:04ED
 * OMF: F_PINA@ 0000:054D
 * OMF: F_PADA@ 0000:0465
 * OMF: F_LXLSH@ 0000:0444
 * BIND: memset 0000:106B
 * BIND: MainAdlxSectionEnd 0664:0262
 * OMF: F_LXMUL@ 0000:035B
 * DATA: 1A37
 * All 23 C functions in one translation unit. See inventory.json for stubs and tables.
 */
int SoundSystemInitialized = 0;
int SoundSystemShutdown = 0;
extern int far AdlxPlaybackGuard, MainAdlxPlaying, MainAdlxSectionLoopEnabled, SoundDeviceBits;
extern void far CancelMusicFade(void);
extern void far ShutdownDspPlayback(void);
extern void far ShutdownAdlibPlayback(void);

struct s_0014 {
    unsigned long f00;
    unsigned f04;
    unsigned char far *f06;
    unsigned f0A, f0C;
    unsigned f0E;
    unsigned char far *f10;
    unsigned f14, f16, f18, f1A;
    unsigned f1C;
    unsigned long f1E;
    unsigned f22, f24, f26, f28;
};
extern struct s_0014 far AudioChannelStates[];
extern unsigned far MusicTicksPerUnit;
extern unsigned long far AdlxTickCount, MainAdlxTimeOrigin;
/* Borland long-division helper is compiler emitted, not called in C. */

extern int far SampleMixerBusy, ActiveSampleVoiceCount, ActiveSampleVoiceMask;
extern unsigned char huge * far SoundBankBase;
extern unsigned long far SoundBankLength;
extern void far ClearSoundState(void);
extern int far InitializeDspPlayback(void);
extern void far SetDspSampleRate(unsigned);
extern int far InitializeAdlibPlayback(void);
extern void far PrimeSampleDmaPlayback(void);
extern void far fn_013B_001E(void), far fn_013B_001F(void);
extern unsigned char huge *far fn_013B_001D(unsigned long,unsigned long,unsigned long);
extern unsigned long far fn_013B_001C(unsigned long);
void ShutdownSoundSystem(void);
void StopAdlibTrackChannel(int);
void RestoreAdlibVoiceAllocation(int);
int LoadAdlibTrackData(int, unsigned char far *, int);
int StartAdlibTrackChannel(int,int);
int SetMusicTrackVolume(int);

extern unsigned far MusicEventStreamLength, MusicVoiceCount, MusicFadeScheduled, MusicTrackVolume, ReservedAdlibChannelCount, CurrentAdlxSlot;
extern unsigned far MusicFadeStep, MusicFadeDuration, MusicFadeStartVolume, MusicFadeTargetVolume;
extern unsigned long far ScannedMusicClockTicks;
extern unsigned char far * far MainAdlxStartPointer, * far AdlibInstrumentMap;
extern void far ScheduleMusicFade(void), far SilenceAdlibOperators(void);
extern void far SetAdlibChannelVolume(int,unsigned), far KeyOffAdlibChannel(int);
extern void far CopyFarBytes(unsigned long, void far *, void far *);
struct s_0278 {
    unsigned char f00[12];
    unsigned f0C, f0E, f10, f12;
};
extern struct s_0278 far AdlibVoiceStates[], far SavedAdlibVoiceStates[], far ScannedAdlibVoiceStates[];
struct s_chunk {
    unsigned char tag[4];
    unsigned long size;
    unsigned f08;
    unsigned char f0A, f0B;
    unsigned f0C, f0E;
};

extern void far LoadAdlibInstrument(int,void far *), far SetAdlibFrequency(int,unsigned);
extern unsigned char far * far MainAdlxCursor, * far FirstScannedEvent;

int StopSoundChannel(unsigned);
int LoadIffSample(unsigned, unsigned char huge *, unsigned, unsigned, unsigned);

extern void far *far memset(void far *,int,unsigned);
extern unsigned char far * far MainAdlxSectionEnd;

/* CONTRACT (tools/apply.py)
 * Initializes requested devices after shutting down prior devices and clearing sound state.
 * In: device bits, bit 0 AdLib and bit 1 DSP; Out: returns/stores successful-device subset.
 * Quirk: SetDspSampleRate(8000) runs before SoundDeviceBits is assigned, so its gate is clear.
 * DSP success also calls near-RET game hooks through far declarations; do not repair that ABI.
 * END CONTRACT */
/* @0878:0003 */
int InitializeSoundSystem(unsigned bits)
{
    int result = 0;
    int i;
    if (SoundSystemInitialized && SoundDeviceBits)
        ShutdownSoundSystem();
    ClearSoundState();
    if ((bits & 2) && InitializeDspPlayback()) {
        result |= 2;
        for (i = 0; i < 9; i++) {
            fn_013B_001F();
            fn_013B_001E();
        }
        SetDspSampleRate(8000);
    }
    if ((bits & 1) && InitializeAdlibPlayback())
        result |= 1;
    SoundDeviceBits = result;
    SoundSystemInitialized = 1;
    return result;
}

/* CONTRACT (tools/apply.py)
 * Sets AdlxPlaybackGuard, cancels any fade, and tears down devices selected by SoundDeviceBits.
 * Out: clears device bits and sets SoundSystemShutdown; leaves the ADLX guard set.
 * Returns early only when shutdown was already recorded and no device bit remains set.
 * END CONTRACT */
/* @0878:008A */
void ShutdownSoundSystem(void)
{
    if (SoundSystemShutdown && !SoundDeviceBits)
        return;
    AdlxPlaybackGuard = 1;
    CancelMusicFade();
    if (SoundDeviceBits & 2)
        ShutdownDspPlayback();
    if (SoundDeviceBits & 1)
        ShutdownAdlibPlayback();
    SoundDeviceBits = 0;
    SoundSystemShutdown = 1;
}

/* CONTRACT (tools/apply.py)
 * Calls GAME:001Dh for a huge bank pointer and GAME:001Ch for its length.
 * In: three dword arguments; Out: -1 for a null pointer, otherwise stores base/length.
 * Quirk: both game hooks are near RET stubs called through far declarations, with no result
 * assignment. The executable supplies no implemented resource-loader contract for these hooks.
 * END CONTRACT */
/* @0878:00F5 */
unsigned long LoadSoundBankResource(unsigned long a, unsigned long b, unsigned long c)
{
    unsigned char huge *p;
    if ((p = fn_013B_001D(a,b,c)) == 0)
        return -1L;
    SoundBankBase = p;
    SoundBankLength = fn_013B_001C(b);
    return SoundBankLength;
}

/* CONTRACT (tools/apply.py)
 * Finds VHDR and BODY tags bytewise in FORM data and initializes sample descriptor 0..7.
 * In: huge data pointer, volume, repeat count and Q8 step; requires SoundDeviceBits&2.
 * Out: 1 on setup or -1 on rejection; clamps volume to 255 and rounds BODY length down even.
 * Effects: calls StopSoundChannel, then waits for SampleMixerBusy before setting mask/count.
 * Descriptor writes precede that wait; there is no claimed atomic descriptor replacement.
 * END CONTRACT */
/* @0878:0176 */
int LoadIffSample(unsigned x, unsigned char huge *p, unsigned volume, unsigned count, unsigned step)
{
    unsigned long length;
    unsigned rate;
    unsigned mode;
    unsigned char huge *start = p;
    if (!(SoundDeviceBits & 2))
        return -1;
    if (x >= 8)
        return -1;
    if (*p++ != 'F' || *p++ != 'O' || *p++ != 'R' || *p++ != 'M')
        return -1;
    length = *p;
    p++;
    length = (length << 8) + *p;
    p++;
    length = (length << 8) + *p;
    p++;
    length = (length << 8) + *p;
    p++;
    while (*p++ != 'V' || *p++ != 'H' || *p++ != 'D' || *p++ != 'R')
        if (p > start + length)
            return -1;
    rate = (p[16] << 8) + p[17];
    if (p[19])
        mode = 3;
    else
        mode = 2;
    while (*p++ != 'B' || *p++ != 'O' || *p++ != 'D' || *p++ != 'Y')
        if (p > start + length)
            return -1;
    length = *p;
    p++;
    length = (length << 8) + *p;
    p++;
    length = (length << 8) + *p;
    p++;
    length = (length << 8) + *p;
    p++;
    if (length > 64000UL)
        return -1;
    StopSoundChannel(x);
    if (volume > 255)
        volume = 255;
    length &= 0xfffe;
    AudioChannelStates[x].f28 = 0;
    if (!count)
        AudioChannelStates[x].f28 |= 2;
    else
        AudioChannelStates[x].f04 = count;
    AudioChannelStates[x].f1C = volume;
    AudioChannelStates[x].f06 = (unsigned char far *)p;
    AudioChannelStates[x].f10 = (unsigned char far *)((unsigned long)p & 0xffff0000UL);
    AudioChannelStates[x].f0A = length;
    AudioChannelStates[x].f0C = mode;
    AudioChannelStates[x].f18 = mode & 1;
    AudioChannelStates[x].f26 = step;
    AudioChannelStates[x].f14 = length >> 1;
    if (mode & 2)
        AudioChannelStates[x].f1A = 127;
    else
        AudioChannelStates[x].f1A = 0;
    AudioChannelStates[x].f0E = rate;
    while (SampleMixerBusy)
        ;
    ActiveSampleVoiceCount++;
    ActiveSampleVoiceMask |= 1 << x;
    return 1;
}

/* CONTRACT (tools/apply.py)
 * Attempts to load an ADLX descriptor and stores its requested volume.
 * In: unsigned channel >=8, far data pointer, volume and playback count.
 * Quirk: LoadAdlibTrackData returns 1 or -1, both true here; parse/device rejection therefore
 * still stores the volume and returns 1. Only channel<8 returns -1 through this wrapper.
 * END CONTRACT */
/* @0878:0691 */
int LoadAdlibChannel(unsigned x, unsigned char far *p, unsigned a, unsigned b)
{
    if (x < 8)
        return -1;
    StopAdlibTrackChannel(x);
    if (LoadAdlibTrackData(x,p,b)) {
        AudioChannelStates[x].f1C = a;
        return 1;
    } else
        return -1;
}

/* CONTRACT (tools/apply.py)
 * Resolves a bank entry and dispatches 8SVX or ADLX data to its format loader.
 * In: channel index, bank-entry index, volume, count and step.
 * Out: returns the selected loader result, or -1 for invalid index, bounds or tag.
 * Effects: follows huge bank pointers and preserves the original format-specific loader behavior.
 * END CONTRACT */
/* @0878:06E4 */
int LoadBankSoundByIndex(unsigned x, unsigned index, unsigned a, unsigned b, unsigned c)
{
    unsigned char huge *p;
    if (x >= 12)
        return -1;
    p = SoundBankBase + *(unsigned long huge *)SoundBankBase + index * 12 + 8;
    if (p > SoundBankBase + SoundBankLength)
        return -1;
    p = SoundBankBase + *(unsigned long huge *)p;
    if (p[0] == 'F' && p[1] == 'O' && p[2] == 'R' && p[3] == 'M' &&
        p[8] == '8' && p[9] == 'S' && p[10] == 'V' && p[11] == 'X')
        return LoadIffSample(x,p,a,b,c);
    else if (p[0] == 'A' && p[1] == 'D' && p[2] == 'L' && p[3] == 'X' &&
        p[8] == 'A' && p[9] == 'H' && p[10] == 'D' && p[11] == 'R')
        return LoadAdlibChannel(x,(unsigned char far *)p,a,b);
    else
        return -1;
}

/* CONTRACT (tools/apply.py)
 * Starts queued sample DMA and attempts to start loaded ADLX effect descriptors 8..11.
 * In: SoundDeviceBits, ActiveSampleVoiceCount, and each effect descriptor's stored volume.
 * Effects: PrimeSampleDmaPlayback refills/starts DMA; StartAdlibTrackChannel allocates voices.
 * Already-active/unloaded ADLX descriptors are rejected by the callee; results are ignored.
 * No direct caller was identified; this routine does not stop the active outputs.
 * END CONTRACT */
/* @0878:096B */
void StartSoundOutputs(void)
{
    int i;
    if ((SoundDeviceBits & 2) && ActiveSampleVoiceCount)
        PrimeSampleDmaPlayback();
    if (SoundDeviceBits & 1)
        for (i = 8; i < 12; i++)
            StartAdlibTrackChannel(i,AudioChannelStates[i].f1C);
}

/* CONTRACT (tools/apply.py)
 * Stops a selected sample voice, or delegates an ADLX effect slot to StopAdlibTrackChannel.
 * In: unsigned slot; Out: -1 for slot>12 or an inactive sample when device bit 1 is enabled.
 * Otherwise returns 1, including no-op requests with device bit 1 clear or slot twelve.
 * Quirk: the SoundDeviceBits&2 gate also encloses ADLX delegation, even with AdLib enabled.
 * Sample path clears repeat count, waits on SampleMixerBusy, then rechecks/clears mask and count.
 * END CONTRACT */
/* @0878:09CA */
int StopSoundChannel(unsigned x)
{
    if (x > 12)
        return -1;
    if (SoundDeviceBits & 2) {
        if (x < 8) {
            if (!(ActiveSampleVoiceMask & (1 << x)))
                return -1;
            AudioChannelStates[x].f04 = 0;
            while (SampleMixerBusy)
                ;
            if (ActiveSampleVoiceMask & (1 << x)) {
                ActiveSampleVoiceMask &= ~(1 << x);
                --ActiveSampleVoiceCount;
            }
        } else
            StopAdlibTrackChannel(x);
    }
    return 1;
}

/* CONTRACT (tools/apply.py)
 * Reverses the four bytes of a 32-bit value.
 * In: one unsigned long.
 * Out: returns the byte-reversed value; no shared state changes.
 * END CONTRACT */
/* @0878:0A70 */
unsigned long SwapDwordByteOrder(unsigned long x)
{
    unsigned long y = x;
    ((unsigned char *)&y)[0] = ((unsigned char *)&x)[3];
    ((unsigned char *)&y)[1] = ((unsigned char *)&x)[2];
    ((unsigned char *)&y)[2] = ((unsigned char *)&x)[1];
    ((unsigned char *)&y)[3] = ((unsigned char *)&x)[0];
    return y;
}

/* CONTRACT (tools/apply.py)
 * Parses ADLX/AHDR/IMAP/TRCK into descriptor 8..12; requires SoundDeviceBits&1.
 * In: far data pointer and repeat count (zero sets infinite-repeat bit); Out: 1 or -1.
 * Stores start/cursor at TRCK payload and length=root_size-34; sizes use original mixed endian.
 * For slot 12, f06/f10 are MainAdlxStartPointer/MainAdlxCursor; also sets IMAP and ticks/unit.
 * Effect voice count must fit 9-ReservedAdlibChannelCount; tags/sizes lack full bounds checks.
 * END CONTRACT */
/* @0878:0AA9 */
int LoadAdlibTrackData(int x, unsigned char far *p, int n)
{
    struct s_chunk far *a, far *b, far *c, far *d;
    if (!(SoundDeviceBits & 1))
        return -1;
    if (x > 12 || x < 8)
        return -1;
    a = (struct s_chunk far *)p;
    p += 8;
    if (a->tag[0] != 'A' || a->tag[1] != 'D' || a->tag[2] != 'L' || a->tag[3] != 'X')
        return -1;
    b = (struct s_chunk far *)p;
    p += 8;
    if (b->tag[0] != 'A' || b->tag[1] != 'H' || b->tag[2] != 'D' || b->tag[3] != 'R')
        return -1;
    p += (unsigned)SwapDwordByteOrder(b->size);
    c = (struct s_chunk far *)p;
    p += 8;
    if (c->tag[0] != 'I' || c->tag[1] != 'M' || c->tag[2] != 'A' || c->tag[3] != 'P')
        return -1;
    p += (unsigned)SwapDwordByteOrder(c->size);
    d = (struct s_chunk far *)p;
    p += 8;
    if (d->tag[0] != 'T' || d->tag[1] != 'R' || d->tag[2] != 'C' || d->tag[3] != 'K')
        return -1;
    if (x != 12 && b->f0A > 9 - ReservedAdlibChannelCount)
        return -1;
    if (x == 12) {
        AdlibInstrumentMap = (unsigned char far *)c + 8;
        MusicTicksPerUnit = b->f0E;
    }
    AudioChannelStates[x].f26 = 0x100;
    AudioChannelStates[x].f0A = SwapDwordByteOrder(a->size) + (-34);
    AudioChannelStates[x].f22 = b->f0A;
    AudioChannelStates[x].f10 = p;
    AudioChannelStates[x].f06 = p;
    AudioChannelStates[x].f28 = 4;
    if (!n)
        AudioChannelStates[x].f28 |= 2;
    else
        AudioChannelStates[x].f04 = n;
    return 1;
}

/* CONTRACT (tools/apply.py)
 * Starts loaded ADLX descriptor 8..12 and reserves physical OPL channels for effects 8..11.
 * In: slot and volume (any high byte clamps to 255); requires device bit 0 and loaded bit 2.
 * Out: 1 with descriptor active bit and deadline=AdlxTickCount+3; restores saved guard on success.
 * Effects: CurrentAdlxSlot is assigned before range/descriptor rejection and is not restored.
 * Capacity failure rolls back ReservedAdlibChannelCount but leaves AdlxPlaybackGuard set to 1.
 * END CONTRACT */
/* @0878:0CFC */
int StartAdlibTrackChannel(int x, int n)
{
    int i;
    unsigned old = AdlxPlaybackGuard;
    if (!(SoundDeviceBits & 1))
        return -1;
    CurrentAdlxSlot = x;
    if (n & 0xff00)
        n = 255;
    if (x > 12 || x < 8 || !(AudioChannelStates[x].f28 & 4) || (AudioChannelStates[x].f28 & 1))
        return -1;
    AdlxPlaybackGuard = 1;
    AudioChannelStates[x].f1C = n;
    if (x < 12) {
        StopAdlibTrackChannel(x);
        ReservedAdlibChannelCount += AudioChannelStates[x].f22;
        if (ReservedAdlibChannelCount > 9) {
            ReservedAdlibChannelCount -= AudioChannelStates[x].f22;
            return -1;
        }
        AudioChannelStates[x].f24 = 9 - ReservedAdlibChannelCount;
    }
    for (i = AudioChannelStates[x].f24; i < AudioChannelStates[x].f24 + AudioChannelStates[x].f22; i++) {
        if (i < MusicVoiceCount) {
            SavedAdlibVoiceStates[i].f12 = AdlibVoiceStates[i].f12;
            CopyFarBytes(12, &AdlibVoiceStates[i], &SavedAdlibVoiceStates[i]);
            SavedAdlibVoiceStates[i].f0C = MusicTrackVolume;
            SavedAdlibVoiceStates[i].f0E = AdlibVoiceStates[i].f0E;
        }
        SetAdlibChannelVolume(i,0);
        KeyOffAdlibChannel(i);
        AdlibVoiceStates[i].f0C = n;
    }
    AudioChannelStates[x].f28 |= 1;
    AudioChannelStates[x].f1E = AdlxTickCount + 3;
    AdlxPlaybackGuard = old;
    return 1;
}

/* CONTRACT (tools/apply.py)
 * Copies a loaded descriptor's f06 start pointer to f10 cursor; leaves its deadline untouched.
 * In: signed slot; Out: -1 for slot>12 or missing loaded bit, otherwise 1.
 * Quirk: no lower-bound check; for valid slot 12 this writes MainAdlxCursor.
 * END CONTRACT */
/* @0878:0F2D */
int ResetAdlibTrackChannelCursor(int x)
{
    if (x > 12 || !(AudioChannelStates[x].f28 & 4))
        return -1;
    AudioChannelStates[x].f10 = AudioChannelStates[x].f06;
    return 1;
}

/* CONTRACT (tools/apply.py)
 * Loads the main ADLX descriptor and enables main playback, immediately or with fade-in.
 * In: far track pointer, fade-callback count (zero immediate), requested target volume.
 * Out: -1 for missing AdLib/parser failure, otherwise 1; lower-level start result is ignored.
 * Stores MainAdlxTimeOrigin=AdlxTickCount. Playback timer was registered by AdLib initialization.
 * Fade-in resets MusicFadeStep and registers a separate fixed-period callback; stored track
 * volume is assigned the target immediately, even while hardware volume is still fading.
 * END CONTRACT */
/* @0878:0F88 */
int StartMusicTrack(unsigned char far *p, int n, int a)
{
    if (!(SoundDeviceBits & 1))
        return -1;
    CancelMusicFade();
    if (LoadAdlibTrackData(12,p,0) < 0)
        return -1;
    MainAdlxPlaying = 1;
    if (!n) {
        StartAdlibTrackChannel(12,a);
        SetMusicTrackVolume(a);
    } else {
        StartAdlibTrackChannel(12,0);
        MusicFadeStartVolume = 0;
        MusicFadeTargetVolume = a;
        MusicFadeStep = 0;
        MusicFadeDuration = n;
        ScheduleMusicFade();
    }
    MusicTrackVolume = a;
    MainAdlxTimeOrigin = AdlxTickCount;
    return 1;
}

/* CONTRACT (tools/apply.py)
 * Stops effects 8..11, then disables main playback immediately or after a blocking fade-out.
 * In: zero for immediate stop, otherwise number of independent fade callbacks through the target.
 * Out: -1 without AdLib or an active main track, otherwise 1; main descriptor flags remain.
 * Fade mode waits for MusicFadeScheduled to clear, sets CurrentAdlxSlot=0 and silences operators.
 * Immediate mode only clears MainAdlxPlaying after canceling a fade; it does not key off music.
 * END CONTRACT */
/* @0878:1059 */
int StopMusicTrack(int n)
{
    int i;
    if (!(SoundDeviceBits & 1))
        return -1;
    for (i = 8; i < 12; i++)
        StopAdlibTrackChannel(i);
    if (!MainAdlxPlaying)
        return -1;
    CancelMusicFade();
    if (!n)
        MainAdlxPlaying = 0;
    else {
        MusicFadeTargetVolume = 0;
        MusicFadeStartVolume = MusicTrackVolume;
        MusicFadeStep = 0;
        MusicFadeDuration = n;
        ScheduleMusicFade();
        while (MusicFadeScheduled)
            ;
        MainAdlxPlaying = 0;
        CancelMusicFade();
        CurrentAdlxSlot = 0;
        SilenceAdlibOperators();
    }
    return 1;
}

/* CONTRACT (tools/apply.py)
 * Stores requested music volume and routes it over OPL channels 0..MusicVoiceCount-1.
 * In: volume, device bit 0 and MainAdlxPlaying; Out: 1 applied, -1 if device/track unavailable.
 * Preserves CurrentAdlxSlot around a temporary value of 12; reserved channels update saved state.
 * CurrentAdlxSlot selects the track context, not the OPL channel in the loop.
 * END CONTRACT */
/* @0878:1128 */
int SetMusicTrackVolume(int n)
{
    int i;
    unsigned old = CurrentAdlxSlot;
    if (!(SoundDeviceBits & 1))
        return -1;
    if (!MainAdlxPlaying)
        return -1;
    MusicTrackVolume = n;
    CurrentAdlxSlot = 12;
    for (i = 0; i < MusicVoiceCount; i++)
        SetAdlibChannelVolume(i,n);
    CurrentAdlxSlot = old;
    return 1;
}

/* CONTRACT (tools/apply.py)
 * Scans from MainAdlxStartPointer to two timing thresholds and enables a recurring section loop.
 * In: start/end units multiplied by MusicTicksPerUnit; requires AdLib and MainAdlxPlaying.
 * Out: FirstScannedEvent, MainAdlxSectionEnd, start-state snapshot, and second-pass tick delta;
 * returns 1 and sets MainAdlxSectionLoopEnabled, or -1 without rolling back prior scan writes.
 * Only the first pass updates ScannedAdlibVoiceStates; waits can overshoot either threshold.
 * Quirks: no ordering/zero-span validation or playback guard. Scanner uses nominal payload sizes;
 * unlike SOUND it skips invalid-channel instrument/frequency payloads and length-skips 77h.
 * END CONTRACT */
/* @0878:11AD */
int ScanMusicEvents(unsigned a, unsigned b)
{
    unsigned char far *p = MainAdlxStartPointer;
    unsigned long total = 0;
    unsigned long threshold;
    unsigned char code, op;
    unsigned char far * far *out = &FirstScannedEvent;
    unsigned long delta;
    int i, j;
    if (!(SoundDeviceBits & 1))
        return -1;
    if (!MainAdlxPlaying)
        return -1;
    memset(ScannedAdlibVoiceStates,0,180);
    for (j = 0; j < MusicVoiceCount; j++)
        ScannedAdlibVoiceStates[j].f0C = MusicTrackVolume;
    threshold = (unsigned long)a * MusicTicksPerUnit;
    for (i = 0; i < 2; i++) {
        ScannedMusicClockTicks = total;
        while (total < threshold) {
            code = *p++;
            op = code & 0xf0;
            if (p >= MainAdlxStartPointer + MusicEventStreamLength)
                return -1;
            switch (op) {
            case 0:
                delta = (((unsigned long)code << 8) + *p) << 7;
                p++;
                total += delta;
                break;
            case 0x10:
                if (!i)
                    ScannedAdlibVoiceStates[code & 15].f12 = *(unsigned far *)p;
                p += 2;
                break;
            case 0x20:
                if (!i)
                    ScannedAdlibVoiceStates[code & 15].f12 &= 0xdfff;
                break;
            case 0x30:
                if (!i)
                    ScannedAdlibVoiceStates[code & 15].f0E = *p;
                p++;
                break;
            case 0x40:
                if (!i) {
                    CopyFarBytes(12,p,&ScannedAdlibVoiceStates[code & 15]);
                    ScannedAdlibVoiceStates[code & 15].f10 = 12;
                }
                p += 11;
                break;
            case 0x60:
                p += 2;
                break;
            case 0x70:
                p += *p;
                p++;
                break;
            default:
                delta = code & 0x7f;
                total += delta;
            }
        }
        *out = p;
        out = &MainAdlxSectionEnd;
        ScannedMusicClockTicks = total - ScannedMusicClockTicks;
        threshold = (unsigned long)b * MusicTicksPerUnit;
    }
    MainAdlxSectionLoopEnabled = 1;
    return 1;
}

/* CONTRACT (tools/apply.py)
 * Disables the recurring scanned section loop by clearing MainAdlxSectionLoopEnabled.
 * In: MainAdlxPlaying; only clears the flag while that word is nonzero. Always returns 1.
 * Leaves scan pointers, snapshots and clocks untouched; no pending event is acknowledged.
 * END CONTRACT */
/* @0878:1491 */
int DisableMusicSectionLoop(void)
{
    if (MainAdlxPlaying)
        MainAdlxSectionLoopEnabled = 0;
    return 1;
}

/* CONTRACT (tools/apply.py)
 * Releases an effect descriptor's reserved OPL channels and compacts the remaining allocations.
 * In: effect slot and descriptor voice count/base; Out: decreases ReservedAdlibChannelCount.
 * Moves live effect records and restores displaced main-track state where music voices exist.
 * Effects: writes CurrentAdlxSlot for instrument ownership/routing and does not restore it.
 * The hardware helpers write OPL registers; SetAdlibFrequency unconditionally reenables IF.
 * END CONTRACT */
/* @0878:14BB */
void RestoreAdlibVoiceAllocation(int x)
{
    int i, n, begin, end, k, tmp;
    n = AudioChannelStates[x].f22;
    begin = 9 - ReservedAdlibChannelCount;
    end = begin + n;
    AudioChannelStates[x].f28 = 0;
    ReservedAdlibChannelCount -= n;
    for (k = 8; k < 12; k++)
        if (k != x && (AudioChannelStates[k].f28 & 4) && AudioChannelStates[k].f24 < AudioChannelStates[x].f24)
            AudioChannelStates[k].f24 += n;
    if (AudioChannelStates[x].f24 > begin)
        for (i = AudioChannelStates[x].f24 + n - 1; i >= end; i--) {
            CopyFarBytes(12,&AdlibVoiceStates[i-n],&AdlibVoiceStates[i]);
            AdlibVoiceStates[i].f0C = AdlibVoiceStates[i-n].f0C;
            AdlibVoiceStates[i].f0E = AdlibVoiceStates[i-n].f0E;
            AdlibVoiceStates[i].f12 = AdlibVoiceStates[i-n].f12;
            AdlibVoiceStates[i].f10 = AdlibVoiceStates[i-n].f10;
            CurrentAdlxSlot = AdlibVoiceStates[i].f10;
            tmp = AdlibVoiceStates[i].f12;
            KeyOffAdlibChannel(i);
            LoadAdlibInstrument(i,&AdlibVoiceStates[i]);
            SetAdlibFrequency(i,tmp);
        }
    for (i = begin; i < end; i++) {
        if (i < MusicVoiceCount) {
            AdlibVoiceStates[i].f0C = MusicTrackVolume;
            AdlibVoiceStates[i].f0E = SavedAdlibVoiceStates[i].f0E;
            CurrentAdlxSlot = 12;
            AdlibVoiceStates[i].f10 = 12;
            tmp = SavedAdlibVoiceStates[i].f12;
            KeyOffAdlibChannel(i);
            LoadAdlibInstrument(i,&SavedAdlibVoiceStates[i]);
            SetAdlibFrequency(i,SavedAdlibVoiceStates[i].f12);
        } else {
            KeyOffAdlibChannel(i);
            SetAdlibChannelVolume(i,0);
        }
    }
}

/* CONTRACT (tools/apply.py)
 * Stops an active loaded ADLX effect slot 8..11; slot 12 main music is explicitly excluded.
 * In: device bit 0, descriptor flags and AdlxPlaybackGuard; invalid/inactive requests do nothing.
 * Out: clears descriptor flags, restores its start cursor, keys off allocated OPL channels,
 * and calls RestoreAdlibVoiceAllocation. Saves/restores the ADLX guard on the accepted path.
 * Cursor is an ADLX event cursor; CurrentAdlxSlot may change during allocation restoration.
 * END CONTRACT */
/* @0878:1768 */
void StopAdlibTrackChannel(int x)
{
    int i;
    unsigned old = AdlxPlaybackGuard;
    if (!(SoundDeviceBits & 1))
        return;
    if (x < 8 || x >= 12 || !(AudioChannelStates[x].f28 & 4) || !(AudioChannelStates[x].f28 & 1))
        return;
    {
        AdlxPlaybackGuard = 1;
        AudioChannelStates[x].f28 = 0;
        AudioChannelStates[x].f10 = AudioChannelStates[x].f06;
        for (i = 0; i < AudioChannelStates[x].f22; i++)
            KeyOffAdlibChannel(AudioChannelStates[x].f24 + i);
        RestoreAdlibVoiceAllocation(x);
        AdlxPlaybackGuard = old;
    }
}

/* CONTRACT (tools/apply.py)
 * Selects free effect slot 8..11, or replaces the slot with the least unsigned f00 field.
 * In: far ADLX data, volume and repeat count; requires device bit 0.
 * Out: chosen slot or -1; free-slot path returns the slot even if loading/starting fails.
 * Quirks: LoadAdlibChannel treats parser -1 as true; free-slot path ignores start result.
 * No timestamp writer for f00 was found; replacement ties favor slot 8, not proven oldest age.
 * END CONTRACT */
/* @0878:1852 */
int PlayAdlibEffect(unsigned char far *p, int n, int a)
{
    int x = 8;
    int oldest = 8;
    if (!(SoundDeviceBits & 1))
        return -1;
    for (; x < 12; x++)
        if (!(AudioChannelStates[x].f28 & 1)) {
            if (LoadAdlibChannel(x,p,n,a) >= 0)
                StartAdlibTrackChannel(x,n);
            return x;
        }
    for (x = 8; x < 12; x++)
        if (AudioChannelStates[x].f00 < AudioChannelStates[oldest].f00)
            oldest = x;
    x = oldest;
    StopAdlibTrackChannel(x);
    if (!(AudioChannelStates[x].f28 & 1))
        if (LoadAdlibChannel(x,p,n,a) >= 0)
            if (StartAdlibTrackChannel(x,n) >= 0)
                return x;
    return -1;
}

/* CONTRACT (tools/apply.py)
 * Restores the scanned section-start cursor and voice snapshot when the loop threshold is met.
 * In: device bit 0, FirstScannedEvent, ScannedMusicClockTicks and scanned voice records.
 * Out: MainAdlxCursor=FirstScannedEvent; adds loop ticks to MainAdlxTimeOrigin with 32-bit wrap.
 * Leaves AdlxTickCount, the main deadline and MainAdlxSectionLoopEnabled unchanged.
 * Restores live OPL channels below 9-ReservedAdlibChannelCount, saved records above that boundary;
 * final volume call reads the live record even on the saved-record path. Relies on caller context.
 * END CONTRACT */
/* @0878:1943 */
void ApplyScannedMusicEvents(void)
{
    int i;
    if (!(SoundDeviceBits & 1))
        return;
    MainAdlxCursor = FirstScannedEvent;
    MainAdlxTimeOrigin += ScannedMusicClockTicks;
    for (i = 0; i < MusicVoiceCount; i++) {
        if (i < 9 - ReservedAdlibChannelCount) {
            CopyFarBytes(20,&ScannedAdlibVoiceStates[i],&AdlibVoiceStates[i]);
            LoadAdlibInstrument(i,&AdlibVoiceStates[i]);
            SetAdlibFrequency(i,AdlibVoiceStates[i].f12);
        } else
            CopyFarBytes(20,&ScannedAdlibVoiceStates[i],&SavedAdlibVoiceStates[i]);
        SetAdlibChannelVolume(i,AdlibVoiceStates[i].f0C);
    }
}

/* CONTRACT (tools/apply.py)
 * Returns (AdlxTickCount-MainAdlxTimeOrigin)/MusicTicksPerUnit as unsigned 32-bit arithmetic.
 * In: nonzero ticks/unit; no device/active-state check or guard against a torn clock read.
 * Origin is set at start/whole-track repeat and advanced by section-loop duration on restore.
 * Units are AHDR timing units, not seconds when ADLX events change the playback timer period.
 * END CONTRACT */
/* @0878:1A50 */
unsigned long GetElapsedMusicTime(void)
{
    return (AdlxTickCount - MainAdlxTimeOrigin) / MusicTicksPerUnit;
}


/* CONTRACT (tools/apply.py)
 * Scans nominal ADLX opcode payload sizes and divides accumulated waits by MusicTicksPerUnit.
 * In: device bit 0, MainAdlxPlaying, start pointer/length and nonzero ticks/unit; else returns 0.
 * Out: unsigned 16-bit timing-unit count; not a wall-clock duration when timer periods vary.
 * Quirks: long-wait delta wraps at 16 bits here; scanner skips invalid-channel payloads and
 * treats 77h as length-prefixed, unlike SOUND. Payload advances have no per-event bounds check.
 * END CONTRACT */
/* @0878:1A8E */
unsigned GetMusicTrackDuration(void)
{
    unsigned long total = 0;
    unsigned char code;
    unsigned char far *p, far *end;
    unsigned amount;
    if (!(SoundDeviceBits & 1))
        return 0;
    if (!MainAdlxPlaying || !MusicTicksPerUnit)
        return 0;
    p = MainAdlxStartPointer;
    end = p + MusicEventStreamLength;
    while (p < end) {
        code = *p++;
        switch (code >> 4) {
        case 0:
            amount = ((code << 8) + *p) << 7;
            p++;
            total += amount;
            break;
        case 1:
            p += 2;
            break;
        case 2:
            break;
        case 3:
            p++;
            break;
        case 4:
            p += 11;
            break;
        case 6:
            p += 2;
            break;
        case 7:
            p += *p;
            p++;
            break;
        default:
            amount = code & 0x7f;
            total += amount;
        }
    }
    return total / MusicTicksPerUnit;
}


