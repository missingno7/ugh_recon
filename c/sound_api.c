/* Behavioural translation of the original huge-model C APIs and TIMER wrappers.
 * C entries are RETF/cdecl. Arguments/results are 16-bit words (DX:AX for long),
 * DS/SI/DI/BP/SS/SP survive. ES is a live compiler result. Arithmetic flags and
 * AX/BX/CX/DX are scratch except declared return values; IF/DF flow through
 * real callees. Records remain in SOUND RAM, stride 42 (voice records 20).
 * The original C source and rebuilt disassembly are the width/ordering oracle.
 */
#include "ugh.h"
#include "platform.h"
#define CSEG UGH_SEG_C
#define CDATA UGH_S_C_SoundSystemInitialized
#define C(n) UGH_O_C_##n
#define SW(n) rd16(SOUND_SEG,S(n))
#define WW(n,v) wr16(SOUND_SEG,S(n),(uint16_t)(v))
static uint16_t rec(uint16_t x) { return (uint16_t)(S(AudioChannelStates)+x*42u); }
static uint16_t voice(uint16_t base,uint16_t x) { return (uint16_t)(base+x*20u); }
static uint16_t field(uint16_t x,unsigned d) { return rd16(SOUND_SEG,(uint16_t)(rec(x)+d)); }
static void put(uint16_t x,unsigned d,uint16_t v) { wr16(SOUND_SEG,(uint16_t)(rec(x)+d),v); }
static void push(Regs *r,uint16_t x) { r->sp=(uint16_t)(r->sp-2); wr16(r->ss,r->sp,x); }
typedef struct { uint16_t sp,bp,si,di,ds; } Frame;
static Frame enter(Regs *r,unsigned locals,unsigned saves) {
    Frame f={r->sp,r->bp,r->si,r->di,r->ds};
    push(r,r->bp); r->bp=r->sp; r->sp=(uint16_t)(r->sp-locals);
    if(saves&1) push(r,r->si);
    if(saves&2) push(r,r->di);
    push(r,r->ds); r->ds=CDATA; return f;
}
static int leave(Regs *r,Frame f,int status) {
    r->sp=f.sp; r->bp=f.bp; r->si=f.si; r->di=f.di; r->ds=f.ds; return status;
}
static uint16_t arg(Regs *r,Frame f,unsigned n) { return rd16(r->ss,(uint16_t)(f.sp+4+n)); }
static void setarg(Regs *r,Frame f,unsigned n,uint16_t v) { wr16(r->ss,(uint16_t)(f.sp+4+n),v); }
/* CALL FAR, including PUSH CS/CALL near sequences: construct the actual four
 * return bytes and arguments, retaining the caller's measured prologue depth.
 * Dispatcher supplies target CS. Callee adapters leave RETF/argument cleanup here. */
static int call(Regs *r,uint16_t seg,uint16_t off,uint16_t ret,const uint16_t *a,unsigned n) {
    uint16_t sp=r->sp;
    for(unsigned i=n;i;i--) push(r,a[i-1]);
    push(r,r->cs); push(r,ret);
    int status=ugh_dispatch(seg,off,r); if(status!=UGH_CONTROL_TRANSFER) r->sp=sp; return status;
}
#define CALL0(seg,n,ret) do { int st=call(r,seg,n,ret,0,0); if(st) return st==UGH_CONTROL_TRANSFER?st:leave(r,f,st); } while(0)
#define CALL(seg,n,ret,...) do { const uint16_t a_[]={__VA_ARGS__}; int st=call(r,seg,n,ret,a_,sizeof(a_)/2); if(st) return st==UGH_CONTROL_TRANSFER?st:leave(r,f,st); } while(0)
/* Original far dword lvalues compile to two separate word operands. */
static uint32_t words32(uint16_t s,uint16_t o) { return rd16(s,o)|((uint32_t)rd16(s,(uint16_t)(o+2))<<16); }

/* Word device mask; returns successful subset. The AdLib and disabled paths
 * return normally. DSP's actual near-RET continuation propagates as status 4
 * with its original stack/CS/IP, never through LEAVE or synthetic RETF. */
/* TRANSLATES C:InitializeSoundSystem */
EXPORT int c_InitializeSoundSystem(Regs *r) {
    Frame f=enter(r,0,3); r->si=logic(r,0,16);
    if(rd16(r->ds,C(SoundSystemInitialized))) {
        r->ax=SOUND_SEG; r->es=r->ax;
        if(SW(SoundDeviceBits)) { CALL0(CSEG,C(ShutdownSoundSystem),C(InitializeSoundSystem)+0x26); }
    }
    CALL0(SOUND_SEG,S(ClearSoundState),C(InitializeSoundSystem)+0x2b);
    logic(r,arg(r,f,0)&2,16);
    if(arg(r,f,0)&2) {
        CALL0(SOUND_SEG,S(InitializeDspPlayback),C(InitializeSoundSystem)+0x37);
        logic(r,r->ax,16);
        if(r->ax) {
            r->si=logic(r,r->si|2,16); r->di=logic(r,0,16);
            while((int16_t)r->di<9) {
                int st=ugh_call_near_ret_hook(r,G(loc_001F),C(InitializeSoundSystem)+0x47);
                if(st) return st;
                st=ugh_call_near_ret_hook(r,G(loc_001E),C(InitializeSoundSystem)+0x4c);
                if(st) return st;
                r->di=(uint16_t)(r->di+1);
            }
            CALL(SOUND_SEG,S(SetDspSampleRate),C(InitializeSoundSystem)+0x5a,8000);
        }
    }
    logic(r,arg(r,f,0)&1,16);
    if(arg(r,f,0)&1) {
        CALL0(SOUND_SEG,S(InitializeAdlibPlayback),C(InitializeSoundSystem)+0x67);
        logic(r,r->ax,16); if(r->ax) r->si=logic(r,r->si|1,16);
    }
    r->ax=SOUND_SEG; r->es=r->ax; WW(SoundDeviceBits,r->si);
    wr16(r->ds,C(SoundSystemInitialized),1); r->ax=r->si; return leave(r,f,0);
}
/* The executable never returns from this hook as a far resource loader.
 * Expose its exact first control transfer; do not assign a pointer or length. */
/* CONTROL_PREFIX C:LoadSoundBankResource */
EXPORT int c_LoadSoundBankResource(Regs *r) {
    Frame f=enter(r,4,0); r->ax=CDATA;
    for(unsigned n=12;n;n-=2) push(r,arg(r,f,n-2));
    return ugh_call_near_ret_hook(r,G(loc_001D),C(LoadSoundBankResource)+0x21);
}

/* Signed slot, far pointer, repeat word. Far arithmetic wraps only the offset;
 * compiler mutates the caller's pointer argument at every += (0AE7..0BBE).
 * AHDR voice count is a BYTE, despite several adjacent word fields. ES on tag
 * rejection is the resource segment; capacity rejection/success leave SOUND. */
/* TRANSLATES C:LoadAdlibTrackData */
EXPORT int c_LoadAdlibTrackData(Regs *r) {
    Frame f=enter(r,16,3); uint16_t x=arg(r,f,0),p=arg(r,f,2),s=arg(r,f,4),n=arg(r,f,6);
    r->es=SOUND_SEG; r->ax=0xffff;
    if(!(SW(SoundDeviceBits)&1)||(int16_t)x>12||(int16_t)x<8) return leave(r,f,0);
    uint16_t a=p,b,c,d;
    p=(uint16_t)(p+8); setarg(r,f,2,p); r->es=s;
    for(unsigned i=0;i<4;i++) if(rd8(s,(uint16_t)(a+i))!=(uint8_t)"ADLX"[i]) return leave(r,f,0);
    b=p; p=(uint16_t)(p+8); setarg(r,f,2,p);
    for(unsigned i=0;i<4;i++) if(rd8(s,(uint16_t)(b+i))!=(uint8_t)"AHDR"[i]) return leave(r,f,0);
    CALL(CSEG,C(SwapDwordByteOrder),C(LoadAdlibTrackData)+0xb4,rd16(s,(uint16_t)(b+4)),rd16(s,(uint16_t)(b+6)));
    p=(uint16_t)(p+r->ax); setarg(r,f,2,p); r->ax=0xffff;
    c=p; p=(uint16_t)(p+8); setarg(r,f,2,p);
    for(unsigned i=0;i<4;i++) if(rd8(s,(uint16_t)(c+i))!=(uint8_t)"IMAP"[i]) return leave(r,f,0);
    CALL(CSEG,C(SwapDwordByteOrder),C(LoadAdlibTrackData)+0x103,rd16(s,(uint16_t)(c+4)),rd16(s,(uint16_t)(c+6)));
    p=(uint16_t)(p+r->ax); setarg(r,f,2,p); r->ax=0xffff;
    d=p; p=(uint16_t)(p+8); setarg(r,f,2,p);
    for(unsigned i=0;i<4;i++) if(rd8(s,(uint16_t)(d+i))!=(uint8_t)"TRCK"[i]) return leave(r,f,0);
    if(x!=12) { r->es=SOUND_SEG; if(rd8(s,(uint16_t)(b+10))>(uint16_t)(9-SW(ReservedAdlibChannelCount))) return leave(r,f,0); }
    if(x==12) { wr16(SOUND_SEG,S(AdlibInstrumentMap)+2,s); WW(AdlibInstrumentMap,(uint16_t)(c+8)); WW(MusicTicksPerUnit,rd16(s,(uint16_t)(b+14))); }
    r->es=SOUND_SEG;
    put(x,0x26,0x100); r->es=s;
    CALL(CSEG,C(SwapDwordByteOrder),C(LoadAdlibTrackData)+0x1b1,rd16(s,(uint16_t)(a+4)),rd16(s,(uint16_t)(a+6)));
    r->es=SOUND_SEG; put(x,0xa,(uint16_t)(r->ax-34));
    put(x,0x22,rd8(s,(uint16_t)(b+10)));
    put(x,0x12,s); put(x,0x10,p); put(x,8,s); put(x,6,p); put(x,0x28,4);
    if(!n) put(x,0x28,(uint16_t)(field(x,0x28)|2)); else put(x,4,n);
    r->ax=1; return leave(r,f,0);
}

/* Device bit 1 gates both sample and ADLX stopping. Unsigned x>12 rejects
 * before ES is loaded. Sample busy wait is a real deterministic service point. */
/* TRANSLATES C:StopSoundChannel */
EXPORT int c_StopSoundChannel(Regs *r) {
    Frame f=enter(r,0,0); uint16_t x=arg(r,f,0); r->ax=0xffff;
    if(x>12) return leave(r,f,0);
    r->es=SOUND_SEG;
    if(SW(SoundDeviceBits)&2) {
        if(x<8) {
            uint16_t mask=(uint16_t)(1u<<x);
            if(!(SW(ActiveSampleVoiceMask)&mask)) return leave(r,f,0);
            put(x,4,0);
            unsigned budget=5000000;
            for(;;) {
                if(!budget--) return leave(r,f,UGH_BUDGET);
                int st=platform_service_point_at(SERVICE_TIMER_WAIT,CSEG,C(StopSoundChannel)+0x53,r);
                if(st) return leave(r,f,st);
                if(!SW(SampleMixerBusy)) break;
            }
            if(SW(ActiveSampleVoiceMask)&mask) { WW(ActiveSampleVoiceMask,SW(ActiveSampleVoiceMask)&~mask); WW(ActiveSampleVoiceCount,SW(ActiveSampleVoiceCount)-1); }
        } else CALL(CSEG,C(StopAdlibTrackChannel),C(StopSoundChannel)+0x9c,x);
    }
    r->ax=1; return leave(r,f,0);
}

/* Signed effect slot 8..11, requires loaded AND active bits. Restores guard;
 * f10 cursor is copied before calls, and flags zeroed before allocation release. */
/* TRANSLATES C:StopAdlibTrackChannel */
EXPORT int c_StopAdlibTrackChannel(Regs *r) {
    Frame f=enter(r,2,3); uint16_t x=arg(r,f,0),old=SW(AdlxPlaybackGuard);
    r->es=SOUND_SEG; r->ax=SOUND_SEG;
    if(!(SW(SoundDeviceBits)&1)||(int16_t)x<8||(int16_t)x>=12||!(field(x,0x28)&4)||!(field(x,0x28)&1)) return leave(r,f,0);
    WW(AdlxPlaybackGuard,1); put(x,0x28,0); put(x,0x12,field(x,8)); put(x,0x10,field(x,6));
    for(uint16_t i=0;i<field(x,0x22);i++) CALL(SOUND_SEG,S(KeyOffAdlibChannel),C(StopAdlibTrackChannel)+0xbf,(uint16_t)(field(x,0x24)+i));
    CALL(CSEG,C(RestoreAdlibVoiceAllocation),C(StopAdlibTrackChannel)+0xd7,x);
    /* POP CX consumes the stack slot argument after this call, then MOV AX
     * reloads SOUND and MOV DX reloads the saved guard (183F..1848). SOUND's
     * effect-expiry handler exposes these compiler scratch outputs. */
    r->cx=x; r->ax=SOUND_SEG; r->dx=old;
    r->es=SOUND_SEG; WW(AdlxPlaybackGuard,old); return leave(r,f,0);
}

/* LoadAdlibTrackData returns -1 or 1: BOTH satisfy this wrapper's truth test.
 * Unsigned slots >=8 have no upper bound here; stride arithmetic wraps. */
/* TRANSLATES C:LoadAdlibChannel */
EXPORT int c_LoadAdlibChannel(Regs *r) {
    Frame f=enter(r,0,1); uint16_t x=arg(r,f,0); r->ax=0xffff;
    if(x<8) return leave(r,f,0);
    CALL(CSEG,C(StopAdlibTrackChannel),C(LoadAdlibChannel)+0x1d,x);
    CALL(CSEG,C(LoadAdlibTrackData),C(LoadAdlibChannel)+0x2d,x,arg(r,f,2),arg(r,f,4),arg(r,f,8));
    if(r->ax) { r->es=SOUND_SEG; put(x,0x1c,arg(r,f,6)); r->ax=1; } else r->ax=0xffff;
    return leave(r,f,0);
}

/* Volume word, result +/-1. CurrentAdlxSlot restored after routing every
 * unsigned voice index. Peer call owns OPL transactions and saved/live routing. */
/* TRANSLATES C:SetMusicTrackVolume */
EXPORT int c_SetMusicTrackVolume(Regs *r) {
    Frame f=enter(r,2,3); uint16_t n=arg(r,f,0),old=SW(CurrentAdlxSlot);
    r->es=SOUND_SEG; r->ax=0xffff;
    if(!(SW(SoundDeviceBits)&1)||!SW(MainAdlxPlaying)) return leave(r,f,0);
    WW(MusicTrackVolume,n); WW(CurrentAdlxSlot,12);
    for(uint16_t i=0;i<SW(MusicVoiceCount);i++) CALL(SOUND_SEG,S(SetAdlibChannelVolume),C(SetMusicTrackVolume)+0x5e,i,n);
    r->es=SOUND_SEG; WW(CurrentAdlxSlot,old); r->ax=1; return leave(r,f,0);
}

/* Starts a loaded descriptor, saving the guard except on capacity failure.
 * Volume clamp modifies the caller argument. CurrentAdlxSlot is set even for
 * invalid slots; word capacity addition/subtraction wrap exactly as ADD/SUB. */
/* TRANSLATES C:StartAdlibTrackChannel */
EXPORT int c_StartAdlibTrackChannel(Regs *r) {
    Frame f=enter(r,2,3); uint16_t x=arg(r,f,0),n=arg(r,f,2),old=SW(AdlxPlaybackGuard);
    r->es=SOUND_SEG; r->ax=0xffff;
    if(!(SW(SoundDeviceBits)&1)) return leave(r,f,0);
    WW(CurrentAdlxSlot,x); if(n&0xff00) { n=255; setarg(r,f,2,n); }
    if((int16_t)x>12||(int16_t)x<8||!(field(x,0x28)&4)||(field(x,0x28)&1)) return leave(r,f,0);
    WW(AdlxPlaybackGuard,1); put(x,0x1c,n);
    if((int16_t)x<12) {
        CALL(CSEG,C(StopAdlibTrackChannel),C(StartAdlibTrackChannel)+0xa0,x);
        WW(ReservedAdlibChannelCount,SW(ReservedAdlibChannelCount)+field(x,0x22));
        if(SW(ReservedAdlibChannelCount)>9) { WW(ReservedAdlibChannelCount,SW(ReservedAdlibChannelCount)-field(x,0x22)); r->ax=0xffff; return leave(r,f,0); }
        put(x,0x24,(uint16_t)(9-SW(ReservedAdlibChannelCount)));
    }
    for(uint16_t i=field(x,0x24);i<(uint16_t)(field(x,0x24)+field(x,0x22));i++) {
        uint16_t v=voice(S(AdlibVoiceStates),i),saved=voice(S(SavedAdlibVoiceStates),i);
        if(i<SW(MusicVoiceCount)) {
            wr16(SOUND_SEG,(uint16_t)(saved+0x12),rd16(SOUND_SEG,(uint16_t)(v+0x12)));
            CALL(GAME_SEG,G(CopyFarBytes),C(StartAdlibTrackChannel)+0x15c,12,0,v,SOUND_SEG,saved,SOUND_SEG);
            wr16(SOUND_SEG,(uint16_t)(saved+0xc),SW(MusicTrackVolume));
            wr16(SOUND_SEG,(uint16_t)(saved+0xe),rd16(SOUND_SEG,(uint16_t)(v+0xe)));
        }
        CALL(SOUND_SEG,S(SetAdlibChannelVolume),C(StartAdlibTrackChannel)+0x19e,i,0);
        CALL(SOUND_SEG,S(KeyOffAdlibChannel),C(StartAdlibTrackChannel)+0x1a7,i);
        wr16(SOUND_SEG,(uint16_t)(v+0xc),n);
    }
    r->es=SOUND_SEG; put(x,0x28,(uint16_t)(field(x,0x28)|1));
    uint32_t deadline=rd32(SOUND_SEG,S(AdlxTickCount))+3u;
    wr32(SOUND_SEG,(uint16_t)(rec(x)+0x1e),deadline);
    /* The compiled deadline calculation leaves its low word in CX. ASM
     * effect callers expose it even though the C API itself promises scratch. */
    r->cx=(uint16_t)deadline; r->bx=(uint16_t)(x*42); r->dx=old;
    WW(AdlxPlaybackGuard,old); r->ax=1; return leave(r,f,0);
}
/* Signed voice compaction indices, unsigned capacity/base comparisons. Copies
 * use the translated GAME helper so incoming DF, overlap and live ES survive.
 * No native record caches: subsequent loads observe all previous writes. */
/* TRANSLATES C:RestoreAdlibVoiceAllocation */
EXPORT int c_RestoreAdlibVoiceAllocation(Regs *r) {
    Frame f=enter(r,8,3); uint16_t x=arg(r,f,0),n=field(x,0x22),begin=(uint16_t)(9-SW(ReservedAdlibChannelCount)),end=(uint16_t)(begin+n);
    r->es=SOUND_SEG; put(x,0x28,0); WW(ReservedAdlibChannelCount,SW(ReservedAdlibChannelCount)-n);
    for(uint16_t k=8;k<12;k++) if(k!=x&&(field(k,0x28)&4)&&field(k,0x24)<field(x,0x24)) put(k,0x24,(uint16_t)(field(k,0x24)+n));
    r->bx=(uint16_t)(x*42); r->ax=field(x,0x24);
    if(field(x,0x24)>begin) {
        uint16_t i=(uint16_t)(field(x,0x24)+n-1); unsigned budget=65536;
        while((int16_t)i>=(int16_t)end) {
            if(!budget--) return leave(r,f,UGH_BUDGET);
            uint16_t dst=voice(S(AdlibVoiceStates),i),src=voice(S(AdlibVoiceStates),(uint16_t)(i-n));
            CALL(GAME_SEG,G(CopyFarBytes),C(RestoreAdlibVoiceAllocation)+0x101,12,0,src,SOUND_SEG,dst,SOUND_SEG);
            for(unsigned d=0xc;d<=0x12;d+=2) {
                /* Original assignment order is volume, gain, frequency, owner. */
                unsigned at=d==0x10?0x12:d==0x12?0x10:d;
                wr16(SOUND_SEG,(uint16_t)(dst+at),rd16(SOUND_SEG,(uint16_t)(src+at)));
            }
            WW(CurrentAdlxSlot,rd16(SOUND_SEG,(uint16_t)(dst+0x10)));
            uint16_t tmp=rd16(SOUND_SEG,(uint16_t)(dst+0x12));
            CALL(SOUND_SEG,S(KeyOffAdlibChannel),C(RestoreAdlibVoiceAllocation)+0x1b4,i);
            CALL(SOUND_SEG,S(LoadAdlibInstrument),C(RestoreAdlibVoiceAllocation)+0x1c7,i,dst,SOUND_SEG);
            CALL(SOUND_SEG,S(SetAdlibFrequency),C(RestoreAdlibVoiceAllocation)+0x1d3,i,tmp);
            i=(uint16_t)(i-1);
        }
    }
    for(uint16_t i=begin;(int16_t)i<(int16_t)end;i++) {
        uint16_t dst=voice(S(AdlibVoiceStates),i),saved=voice(S(SavedAdlibVoiceStates),i);
        if(i<SW(MusicVoiceCount)) {
            wr16(SOUND_SEG,(uint16_t)(dst+0xc),SW(MusicTrackVolume));
            wr16(SOUND_SEG,(uint16_t)(dst+0xe),rd16(SOUND_SEG,(uint16_t)(saved+0xe)));
            WW(CurrentAdlxSlot,12); wr16(SOUND_SEG,(uint16_t)(dst+0x10),12);
            CALL(SOUND_SEG,S(KeyOffAdlibChannel),C(RestoreAdlibVoiceAllocation)+0x260,i);
            CALL(SOUND_SEG,S(LoadAdlibInstrument),C(RestoreAdlibVoiceAllocation)+0x273,i,saved,SOUND_SEG);
            r->bx=(uint16_t)(i*20); r->ax=SOUND_SEG;
            CALL(SOUND_SEG,S(SetAdlibFrequency),C(RestoreAdlibVoiceAllocation)+0x28b,i,rd16(SOUND_SEG,(uint16_t)(saved+0x12)));
        } else {
            CALL(SOUND_SEG,S(KeyOffAdlibChannel),C(RestoreAdlibVoiceAllocation)+0x293,i);
            r->cx=i; /* POP CX at 174E, before the two-word volume call. */
            CALL(SOUND_SEG,S(SetAdlibChannelVolume),C(RestoreAdlibVoiceAllocation)+0x29c,i,0);
        }
    }
    r->es=SOUND_SEG; return leave(r,f,0);
}

/* Two unsigned timing-unit arguments. The scan compares wrapped OFFSET only,
 * checks end after fetching an opcode, and does not bound its payload. Long
 * waits here are 32-bit (unlike GetMusicTrackDuration). Only pass zero snapshots
 * voices; pass one tracks duration. Failure retains partial snapshot/clock. */
static int scan_arm(uint16_t cs,uint8_t op) {
    uint16_t table=(uint16_t)(C(ScanMusicEvents)+0x2c8);
    for(unsigned i=0;i<7;i++) if(rd16(cs,(uint16_t)(table+2*i))==op) {
        uint16_t target=rd16(cs,(uint16_t)(table+14+2*i));
        const uint16_t offsets[]={0x11d,0x155,0x17d,0x19d,0x1c2,0x209,0x20c};
        for(unsigned j=0;j<7;j++) if(target==(uint16_t)(C(ScanMusicEvents)+offsets[j])) return (int)j;
        return -1;
    }
    return 7;
}
/* TRANSLATES C:ScanMusicEvents */
EXPORT int c_ScanMusicEvents(Regs *r) {
    Frame f=enter(r,24,3); uint16_t p=SW(MainAdlxStartPointer),s=rd16(SOUND_SEG,S(MainAdlxStartPointer)+2);
    r->es=SOUND_SEG; r->ax=0xffff;
    if(!(SW(SoundDeviceBits)&1)||!SW(MainAdlxPlaying)) return leave(r,f,0);
    /* Runtime memset executes CLD and leaves it clear (1040:1055). */
    flag(r,DF,0);
    for(unsigned j=0;j<180;j++) wr8(SOUND_SEG,(uint16_t)(S(ScannedAdlibVoiceStates)+j),0);
    for(uint16_t j=0;j<SW(MusicVoiceCount);j++) wr16(SOUND_SEG,(uint16_t)(voice(S(ScannedAdlibVoiceStates),j)+0xc),SW(MusicTrackVolume));
    uint32_t total=0,threshold=(uint32_t)arg(r,f,0)*SW(MusicTicksPerUnit);
    unsigned budget=5000000;
    for(unsigned pass=0;pass<2;pass++) {
        wr32(SOUND_SEG,S(ScannedMusicClockTicks),total);
        while(total<threshold) {
            if(!budget--) return leave(r,f,UGH_BUDGET);
            uint8_t code=rd8(s,p); p=(uint16_t)(p+1); r->es=SOUND_SEG;
            if(p>=(uint16_t)(SW(MainAdlxStartPointer)+SW(MusicEventStreamLength))) { r->ax=0xffff; return leave(r,f,0); }
            uint16_t v=voice(S(ScannedAdlibVoiceStates),code&15);
            switch(scan_arm(r->cs,code&0xf0)) {
            case 0: total+=(((uint32_t)code<<8)+rd8(s,p))<<7; p=(uint16_t)(p+1); break;
            case 1: if(!pass) wr16(SOUND_SEG,(uint16_t)(v+0x12),rd16(s,p)); p=(uint16_t)(p+2); break;
            case 2: if(!pass) wr16(SOUND_SEG,(uint16_t)(v+0x12),(uint16_t)(rd16(SOUND_SEG,(uint16_t)(v+0x12))&0xdfff)); break;
            case 3: if(!pass) wr16(SOUND_SEG,(uint16_t)(v+0xe),rd8(s,p)); p=(uint16_t)(p+1); break;
            case 4:
                if(!pass) {
                    CALL(GAME_SEG,G(CopyFarBytes),C(ScanMusicEvents)+0x1e7,12,0,p,s,v,SOUND_SEG);
                    wr16(SOUND_SEG,(uint16_t)(v+0x10),12);
                }
                p=(uint16_t)(p+11); break;
            case 5: p=(uint16_t)(p+2); break;
            case 6: p=(uint16_t)(p+rd8(s,p)+1); break;
            case 7: total+=code&127; break;
            default: return leave(r,f,UGH_BAD_CALLBACK);
            }
        }
        uint16_t dest=pass?S(MainAdlxSectionEnd):S(FirstScannedEvent);
        wr16(SOUND_SEG,(uint16_t)(dest+2),s); wr16(SOUND_SEG,dest,p);
        wr32(SOUND_SEG,S(ScannedMusicClockTicks),total-rd32(SOUND_SEG,S(ScannedMusicClockTicks)));
        threshold=(uint32_t)arg(r,f,2)*SW(MusicTicksPerUnit);
    }
    r->es=SOUND_SEG; WW(MainAdlxSectionLoopEnabled,1); r->ax=1; return leave(r,f,0);
}

/* No arguments. Cursor and origin update precede all voice restoration calls.
 * Reserved path copies 20 bytes to saved records, then reads volume from LIVE. */
/* TRANSLATES C:ApplyScannedMusicEvents */
EXPORT int c_ApplyScannedMusicEvents(Regs *r) {
    Frame f=enter(r,0,1); r->es=SOUND_SEG;
    if(!(SW(SoundDeviceBits)&1)) return leave(r,f,0);
    wr32(SOUND_SEG,S(MainAdlxCursor),rd32(SOUND_SEG,S(FirstScannedEvent)));
    wr32(SOUND_SEG,S(MainAdlxTimeOrigin),rd32(SOUND_SEG,S(MainAdlxTimeOrigin))+rd32(SOUND_SEG,S(ScannedMusicClockTicks)));
    for(uint16_t i=0;i<SW(MusicVoiceCount);i++) {
        uint16_t src=voice(S(ScannedAdlibVoiceStates),i),v=voice(S(AdlibVoiceStates),i);
        if(i<(uint16_t)(9-SW(ReservedAdlibChannelCount))) {
            CALL(GAME_SEG,G(CopyFarBytes),C(ApplyScannedMusicEvents)+0x8b,20,0,src,SOUND_SEG,v,SOUND_SEG);
            CALL(SOUND_SEG,S(LoadAdlibInstrument),C(ApplyScannedMusicEvents)+0xa0,i,v,SOUND_SEG);
            CALL(SOUND_SEG,S(SetAdlibFrequency),C(ApplyScannedMusicEvents)+0xb8,i,rd16(SOUND_SEG,(uint16_t)(v+0x12)));
        } else CALL(GAME_SEG,G(CopyFarBytes),C(ApplyScannedMusicEvents)+0xde,20,0,src,SOUND_SEG,voice(S(SavedAdlibVoiceStates),i),SOUND_SEG);
        CALL(SOUND_SEG,S(SetAdlibChannelVolume),C(ApplyScannedMusicEvents)+0xf6,i,rd16(SOUND_SEG,(uint16_t)(v+0xc)));
    }
    r->es=SOUND_SEG; return leave(r,f,0);
}

/* Shutdown latch is independent from initialization latch. Leaves guard set.
 * DSP/OPL teardown uses real original-address calls; absent peers fail. */
/* TRANSLATES C:ShutdownSoundSystem */
EXPORT int c_ShutdownSoundSystem(Regs *r) {
    Frame f=enter(r,0,0);
    if(rd16(CDATA,C(SoundSystemShutdown))) { r->es=SOUND_SEG; if(!SW(SoundDeviceBits)) return leave(r,f,0); }
    r->es=SOUND_SEG; WW(AdlxPlaybackGuard,1);
    CALL0(SOUND_SEG,S(CancelMusicFade),C(ShutdownSoundSystem)+0x30);
    if(SW(SoundDeviceBits)&2) CALL0(SOUND_SEG,S(ShutdownDspPlayback),C(ShutdownSoundSystem)+0x43);
    if(SW(SoundDeviceBits)&1) CALL0(SOUND_SEG,S(ShutdownAdlibPlayback),C(ShutdownSoundSystem)+0x56);
    r->es=SOUND_SEG; WW(SoundDeviceBits,0);
    /* 00EC uses live DS: fade cancellation or AdLib teardown -> TIMER removal can leave
     * DGROUP here. Do not redirect that erroneous latch write to CDATA. */
    wr16(r->ds,C(SoundSystemShutdown),1); return leave(r,f,0);
}

/* No arguments. DMA starts only if bit 1 AND sample count; ADLX starts all
 * four effects with stored volumes, ignoring each ordinary return value. */
/* TRANSLATES C:StartSoundOutputs */
EXPORT int c_StartSoundOutputs(Regs *r) {
    Frame f=enter(r,0,1); r->es=SOUND_SEG;
    if((SW(SoundDeviceBits)&2)&&SW(ActiveSampleVoiceCount)) CALL0(SOUND_SEG,S(PrimeSampleDmaPlayback),C(StartSoundOutputs)+0x2a);
    if(SW(SoundDeviceBits)&1) for(uint16_t i=8;i<12;i++) CALL(CSEG,C(StartAdlibTrackChannel),C(StartSoundOutputs)+0x52,i,field(i,0x1c));
    r->es=SOUND_SEG; return leave(r,f,0);
}

/* Far pointer, fade count, volume. Parser/start return handling deliberately
 * differs: parser negatives reject, channel-start negatives are ignored. */
/* TRANSLATES C:StartMusicTrack */
EXPORT int c_StartMusicTrack(Regs *r) {
    Frame f=enter(r,0,3); uint16_t n=arg(r,f,4),a=arg(r,f,6); r->es=SOUND_SEG; r->ax=0xffff;
    if(!(SW(SoundDeviceBits)&1)) return leave(r,f,0);
    CALL0(SOUND_SEG,S(CancelMusicFade),C(StartMusicTrack)+0x2a);
    CALL(CSEG,C(LoadAdlibTrackData),C(StartMusicTrack)+0x38,12,arg(r,f,0),arg(r,f,2),0);
    if((int16_t)r->ax<0) { r->ax=0xffff; return leave(r,f,0); }
    WW(MainAdlxPlaying,1);
    if(!n) {
        CALL(CSEG,C(StartAdlibTrackChannel),C(StartMusicTrack)+0x58,12,a);
        CALL(CSEG,C(SetMusicTrackVolume),C(StartMusicTrack)+0x61,a);
    } else {
        CALL(CSEG,C(StartAdlibTrackChannel),C(StartMusicTrack)+0x6c,12,0);
        WW(MusicFadeStartVolume,0); WW(MusicFadeTargetVolume,a); WW(MusicFadeStep,0); WW(MusicFadeDuration,n);
        CALL0(SOUND_SEG,S(ScheduleMusicFade),C(StartMusicTrack)+0xa0);
    }
    r->es=SOUND_SEG; WW(MusicTrackVolume,a); wr32(SOUND_SEG,S(MainAdlxTimeOrigin),rd32(SOUND_SEG,S(AdlxTickCount)));
    r->ax=1; return leave(r,f,0);
}

/* One fade count. Stops effects before checking playing. Fade path requires
 * deterministic timer delivery; busy state is not cleared by the fixture. */
/* TRANSLATES C:StopMusicTrack */
EXPORT int c_StopMusicTrack(Regs *r) {
    Frame f=enter(r,0,3); uint16_t n=arg(r,f,0); r->es=SOUND_SEG; r->ax=0xffff;
    if(!(SW(SoundDeviceBits)&1)) return leave(r,f,0);
    for(uint16_t i=8;i<12;i++) CALL(CSEG,C(StopAdlibTrackChannel),C(StopMusicTrack)+0x2d,i);
    if(!SW(MainAdlxPlaying)) { r->ax=0xffff; return leave(r,f,0); }
    CALL0(SOUND_SEG,S(CancelMusicFade),C(StopMusicTrack)+0x48);
    if(!n) WW(MainAdlxPlaying,0);
    else {
        WW(MusicFadeTargetVolume,0); WW(MusicFadeStartVolume,SW(MusicTrackVolume)); WW(MusicFadeStep,0); WW(MusicFadeDuration,n);
        CALL0(SOUND_SEG,S(ScheduleMusicFade),C(StopMusicTrack)+0x93);
        unsigned budget=5000000;
        for(;;) {
            if(!budget--) return leave(r,f,UGH_BUDGET);
            int st=platform_service_point_at(SERVICE_TIMER_WAIT,CSEG,C(StopMusicTrack)+0x95,r); if(st) return leave(r,f,st);
            if(!SW(MusicFadeScheduled)) break;
        }
        WW(MainAdlxPlaying,0); CALL0(SOUND_SEG,S(CancelMusicFade),C(StopMusicTrack)+0xb3);
        WW(CurrentAdlxSlot,0); CALL0(SOUND_SEG,S(SilenceAdlibOperators),C(StopMusicTrack)+0xc4);
    }
    r->es=SOUND_SEG; r->ax=1; return leave(r,f,0);
}

/* Far pointer, volume, count. Free path ignores start failure; replacement
 * uses unsigned f00 with strict less-than, preserving first slot on ties. */
/* TRANSLATES C:PlayAdlibEffect */
EXPORT int c_PlayAdlibEffect(Regs *r) {
    Frame f=enter(r,2,3); uint16_t n=arg(r,f,4),a=arg(r,f,6),x=8,oldest=8;
    r->es=SOUND_SEG; r->ax=0xffff; if(!(SW(SoundDeviceBits)&1)) return leave(r,f,0);
    for(;x<12;x++) if(!(field(x,0x28)&1)) {
        CALL(CSEG,C(LoadAdlibChannel),C(PlayAdlibEffect)+0x4f,x,arg(r,f,0),arg(r,f,2),n,a);
        if((int16_t)r->ax>=0) CALL(CSEG,C(StartAdlibTrackChannel),C(PlayAdlibEffect)+0x5c,x,n);
        r->ax=x; return leave(r,f,0);
    }
    for(x=8;x<12;x++) if(rd32(SOUND_SEG,rec(x))<rd32(SOUND_SEG,rec(oldest))) oldest=x;
    x=oldest; CALL(CSEG,C(StopAdlibTrackChannel),C(PlayAdlibEffect)+0xad,x);
    if(!(field(x,0x28)&1)) {
        CALL(CSEG,C(LoadAdlibChannel),C(PlayAdlibEffect)+0xd0,x,arg(r,f,0),arg(r,f,2),n,a);
        if((int16_t)r->ax>=0) {
            CALL(CSEG,C(StartAdlibTrackChannel),C(PlayAdlibEffect)+0xdd,x,n);
            if((int16_t)r->ax>=0) { r->ax=x; return leave(r,f,0); }
        }
    }
    r->ax=0xffff; return leave(r,f,0);
}
/* Borland huge arithmetic normalizes to a 0..15 offset, wrapping segment at
 * sixteen bits. The compiler/runtime helpers remain the byte-match authority;
 * these scalars express their measured semantics, not replacement runtime code. */
typedef struct { uint16_t s,o; } Far;
static Far hadd(Far p,uint32_t n) {
    uint32_t physical=(lin(p.s,p.o)+n)&0xfffffu;
    Far q={(uint16_t)(physical>>4),(uint16_t)(physical&15)}; return q;
}
static int hgreater(Far a,Far b) {
    a=hadd(a,0); b=hadd(b,0); return a.s>b.s||(a.s==b.s&&a.o>b.o);
}
static void savep(Regs *r,Frame f,Far p) { setarg(r,f,2,p.o); setarg(r,f,4,p.s); }
static uint8_t postbyte(Regs *r,Frame f,Far *p) {
    Far old=*p; *p=hadd(*p,1); savep(r,f,*p); r->es=old.s; return rd8(old.s,old.o);
}
static uint32_t be_length(Regs *r,Frame f,Far *p) {
    uint32_t n=0;
    for(unsigned j=0;j<4;j++) {
        r->es=p->s; n=(n<<8)+rd8(p->s,p->o);
        *p=hadd(*p,1); savep(r,f,*p); r->es=r->ss; /* F_PADA@ leaves ES=SS */
    }
    return n;
}
/* Unsigned sample slot, huge pointer, volume/count/Q8 step. Short-circuit tag
 * scans advance for every attempted character, not just one per iteration.
 * Every increment normalizes and overwrites the caller pointer argument.
 * Stale count survives infinite repeat; BODY length is rounded down even. */
/* TRANSLATES C:LoadIffSample */
EXPORT int c_LoadIffSample(Regs *r) {
    Frame f=enter(r,10,3); uint16_t x=arg(r,f,0),vol=arg(r,f,6),count=arg(r,f,8),stepword=arg(r,f,10);
    Far p={arg(r,f,4),arg(r,f,2)},start=p;
    r->es=SOUND_SEG; r->ax=0xffff;
    if(!(SW(SoundDeviceBits)&2)||x>=8) return leave(r,f,0);
    for(unsigned j=0;j<4;j++) if(postbyte(r,f,&p)!=(uint8_t)"FORM"[j]) return leave(r,f,0);
    uint32_t length=be_length(r,f,&p); unsigned budget=5000000;
    for(;;) {
        if(!budget--) return leave(r,f,UGH_BUDGET);
        unsigned j=0; while(j<4&&postbyte(r,f,&p)==(uint8_t)"VHDR"[j]) j++;
        if(j==4) break;
        if(hgreater(p,hadd(start,length))) return leave(r,f,0);
    }
    Far q=hadd(p,16); r->es=q.s; uint16_t rate=(uint16_t)(rd8(q.s,q.o)*256u);
    q=hadd(p,17); r->es=q.s; rate=(uint16_t)(rate+rd8(q.s,q.o));
    q=hadd(p,19); r->es=q.s; uint16_t mode=rd8(q.s,q.o)?3:2;
    for(;;) {
        if(!budget--) return leave(r,f,UGH_BUDGET);
        unsigned j=0; while(j<4&&postbyte(r,f,&p)==(uint8_t)"BODY"[j]) j++;
        if(j==4) break;
        if(hgreater(p,hadd(start,length))) return leave(r,f,0);
    }
    length=be_length(r,f,&p);
    if(length>64000u) return leave(r,f,0);
    CALL(CSEG,C(StopSoundChannel),C(LoadIffSample)+0x3a5,x);
    if(vol>255) vol=255;
    length&=0xfffeu; r->es=SOUND_SEG; put(x,0x28,0);
    if(!count) put(x,0x28,(uint16_t)(field(x,0x28)|2)); else put(x,4,count);
    put(x,0x1c,vol); put(x,8,p.s); put(x,6,p.o); put(x,0x12,p.s); put(x,0x10,0);
    put(x,0xa,(uint16_t)length); put(x,0xc,mode); put(x,0x18,mode&1); put(x,0x26,stepword);
    put(x,0x14,(uint16_t)(length>>1)); put(x,0x1a,(mode&2)?127:0); put(x,0xe,rate);
    budget=5000000;
    for(;;) {
        if(!budget--) return leave(r,f,UGH_BUDGET);
        int st=platform_service_point_at(SERVICE_TIMER_WAIT,CSEG,C(LoadIffSample)+0x4e7,r); if(st) return leave(r,f,st);
        if(!SW(SampleMixerBusy)) break;
    }
    WW(ActiveSampleVoiceCount,SW(ActiveSampleVoiceCount)+1); WW(ActiveSampleVoiceMask,SW(ActiveSampleVoiceMask)|(1u<<x));
    r->ax=1; return leave(r,f,0);
}

/* Five unsigned words. index*12 is a WORD before huge addition, an overflow
 * retained from 0701. Only entry-address upper bound is checked, not data size.
 * Tag probes use normalized huge additions; ADLX is cast back to far. */
/* TRANSLATES C:LoadBankSoundByIndex */
EXPORT int c_LoadBankSoundByIndex(Regs *r) {
    Frame f=enter(r,4,3); uint16_t x=arg(r,f,0),index=arg(r,f,2); r->ax=0xffff;
    if(x>=12) return leave(r,f,0);
    Far base={rd16(SOUND_SEG,S(SoundBankBase)+2),SW(SoundBankBase)};
    Far p=hadd(hadd(hadd(base,words32(base.s,base.o)),(uint16_t)(index*12u)),8);
    r->es=SOUND_SEG;
    if(hgreater(p,hadd(base,rd32(SOUND_SEG,S(SoundBankLength))))) return leave(r,f,0);
    p=hadd(base,words32(p.s,p.o));
    const unsigned positions[]={0,1,2,3,8,9,10,11};
    unsigned j=0;
    for(;j<8;j++) { Far q=j?hadd(p,positions[j]):p; r->es=q.s; if(rd8(q.s,q.o)!=(uint8_t)"FORM8SVX"[j]) break; }
    if(j==8) {
        CALL(CSEG,C(LoadIffSample),C(LoadBankSoundByIndex)+0x192,x,p.o,p.s,arg(r,f,4),arg(r,f,6),arg(r,f,8));
        return leave(r,f,0);
    }
    for(j=0;j<8;j++) { Far q=j?hadd(p,positions[j]):p; r->es=q.s; if(rd8(q.s,q.o)!=(uint8_t)"ADLXAHDR"[j]) break; }
    if(j==8) CALL(CSEG,C(LoadAdlibChannel),C(LoadBankSoundByIndex)+0x277,x,p.o,p.s,arg(r,f,4),arg(r,f,6));
    else r->ax=0xffff;
    return leave(r,f,0);
}

