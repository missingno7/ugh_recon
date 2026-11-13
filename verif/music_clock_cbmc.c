/* Full symbolic scalar domains, ordinary SOUND RAM and disjoint cdecl arguments.
 * This shim is a serialized operation, not an instruction-level IRQ model. */
void __CPROVER_assert(_Bool,const char *);
extern uint8_t nondet_byte(void);
extern uint32_t nondet_dword(void);
extern uint16_t nondet_word(void);
enum { SOUND_BYTES = S(MainAdlxSectionLoopEnabled)-S(MusicTicksPerUnit)+2 };
static uint8_t sound[SOUND_BYTES], saved[SOUND_BYTES], args[4];
uint8_t ugh_read(uint32_t address)
{
    uint32_t first=lin(SOUND_SEG,S(MusicTicksPerUnit));
    if (address>=first && address<first+SOUND_BYTES) return sound[address-first];
    uint32_t stack=lin(0x7000,0x1004);
    __CPROVER_assert(address>=stack && address<stack+4,"only projected SOUND RAM or four argument bytes read");
    return args[address-stack];
}
void ugh_write(uint32_t address,uint8_t value)
{
    uint32_t first=lin(SOUND_SEG,S(MusicTicksPerUnit));
    __CPROVER_assert(address>=lin(SOUND_SEG,S(MainAdlxSectionLoopEnabled)) &&
                      address<lin(SOUND_SEG,S(MainAdlxSectionLoopEnabled))+2,
                      "only the two section-loop bytes written");
    sound[address-first]=value;
}
static void same_shell(Regs a,Regs b)
{
    __CPROVER_assert(a.ax==b.ax && a.bx==b.bx && a.cx==b.cx && a.dx==b.dx &&
        a.si==b.si && a.di==b.di && a.bp==b.bp && a.sp==b.sp && a.cs==b.cs &&
        a.ds==b.ds && a.es==b.es && a.ss==b.ss && a.ip==b.ip && a.flags==b.flags,
        "complete L1 register and flag shell");
}
int main(void)
{
#if MUSIC_MODE == 3
    AdlxTickCount=nondet_dword();MainAdlxTimeOrigin=nondet_dword();MusicTicksPerUnit=nondet_word();
    MusicClockResult result=music_clock_elapsed(AdlxTickCount,MainAdlxTimeOrigin,MusicTicksPerUnit);
    __CPROVER_assert((result.status==MUSIC_CLOCK_DIVIDE_BY_ZERO)==(MusicTicksPerUnit==0),"exact zero-rate fault domain");
    if (MusicTicksPerUnit)
        __CPROVER_assert(result.units==original_GetElapsedMusicTime(),"actual original C/native arithmetic: all 80 input bits");
    return 0;
#else
    Regs old; old.ss=0x7000;old.sp=0x1000; Regs modern=old;
    for (unsigned i=0;i<SOUND_BYTES;i++) sound[i]=nondet_byte();
    for (unsigned i=0;i<4;i++) args[i]=nondet_byte();
    AdlxTickCount=rd32(SOUND_SEG,S(AdlxTickCount));
    MainAdlxTimeOrigin=rd32(SOUND_SEG,S(MainAdlxTimeOrigin));
    MusicTicksPerUnit=rd16(SOUND_SEG,S(MusicTicksPerUnit));
    MainAdlxPlaying=rd16(SOUND_SEG,S(MainAdlxPlaying));
    MainAdlxSectionLoopEnabled=rd16(SOUND_SEG,S(MainAdlxSectionLoopEnabled));
    uint32_t value=(uint32_t)args[0] | (uint32_t)args[1]<<8 | (uint32_t)args[2]<<16 | (uint32_t)args[3]<<24;
    int a,b;
#if MUSIC_MODE == 0
    uint32_t expected=original_SwapDwordByteOrder(value);
    __CPROVER_assert(expected==music_clock_swap_bytes(value),"all 2^32 original C/native byte reversals");
    a=l1_SwapDwordByteOrder(&old);
    __CPROVER_assert(((uint32_t)old.dx<<16 | old.ax)==expected,"L1 original C swap value");
#elif MUSIC_MODE == 1
    uint16_t initial=MainAdlxSectionLoopEnabled;
    __CPROVER_assert(original_DisableMusicSectionLoop()==1,"original disable return");
    __CPROVER_assert(MainAdlxSectionLoopEnabled==music_clock_disable_section_loop(MainAdlxPlaying,initial),
        "all 2^32 playing/enabled pairs");
    a=l1_DisableMusicSectionLoop(&old);
    __CPROVER_assert(rd16(SOUND_SEG,S(MainAdlxSectionLoopEnabled))==MainAdlxSectionLoopEnabled,
        "L1 original C disable state");
#else
    MusicClockResult result=music_clock_elapsed(AdlxTickCount,MainAdlxTimeOrigin,MusicTicksPerUnit);
    __CPROVER_assert((result.status==MUSIC_CLOCK_DIVIDE_BY_ZERO)==(MusicTicksPerUnit==0),"exact zero-rate fault domain");
    /* Do not invoke the undefined original C division for a zero divisor. */
    if (MusicTicksPerUnit)
        __CPROVER_assert(result.units==original_GetElapsedMusicTime(),"original C/native modular arithmetic for every nonzero rate");
    a=l1_GetElapsedMusicTime(&old);
    __CPROVER_assert(a==(MusicTicksPerUnit ? UGH_OK : UGH_UNSUPPORTED),"L1 division fault status");
    if (MusicTicksPerUnit)
        __CPROVER_assert(((uint32_t)old.dx<<16 | old.ax)==result.units,"L1 native elapsed value");
#endif
    for (unsigned i=0;i<SOUND_BYTES;i++) saved[i]=sound[i];
    /* Reset only the original operation's possible output to its initial value. */
#if MUSIC_MODE == 1
    sound[S(MainAdlxSectionLoopEnabled)-S(MusicTicksPerUnit)]=(uint8_t)initial;
    sound[S(MainAdlxSectionLoopEnabled)-S(MusicTicksPerUnit)+1]=(uint8_t)(initial>>8);
#endif
#if MUSIC_MODE == 0
    b=c_SwapDwordByteOrder(&modern);
#elif MUSIC_MODE == 1
    b=c_DisableMusicSectionLoop(&modern);
#else
    b=c_GetElapsedMusicTime(&modern);
#endif
    __CPROVER_assert(a==b,"bridge status");
    same_shell(old,modern);
    for (unsigned i=0;i<SOUND_BYTES;i++)
        __CPROVER_assert(saved[i]==sound[i],"all projected and adjacent SOUND bytes");
    return 0;
#endif
}
