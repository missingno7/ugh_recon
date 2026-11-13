#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define CHECK(x) do { if (!(x)) { fprintf(stderr,"check failed: %s:%d: %s\n",__FILE__,__LINE__,#x); exit(23); } } while (0)
uint8_t ugh_mem[UGH_MEM_SIZE];
uint8_t ugh_read(uint32_t a) { return ugh_mem[a]; }
void ugh_write(uint32_t a,uint8_t v) { ugh_mem[a]=v; }

static Regs shell(void)
{
    Regs r={0xa5c3,0x5a3c,0x3c5a,0xc3a5,0x6996,0x9669,0x7e81,
            0x1000,0x1234,0x7340,0x7c20,0x7000,0x4321,0xed7};
    return r;
}
static void elapsed(uint32_t ticks,uint32_t origin,uint16_t rate)
{
    wr32(SOUND_SEG,S(AdlxTickCount),ticks);wr32(SOUND_SEG,S(MainAdlxTimeOrigin),origin);
    wr16(SOUND_SEG,S(MusicTicksPerUnit),rate);
    AdlxTickCount=ticks;MainAdlxTimeOrigin=origin;MusicTicksPerUnit=rate;
    Regs a=shell(),b=a;MusicClockResult result=music_clock_elapsed(ticks,origin,rate);
    int old=l1_GetElapsedMusicTime(&a),modern=c_GetElapsedMusicTime(&b);
    CHECK(old==modern && !memcmp(&a,&b,sizeof a));
    CHECK(result.status==(rate ? MUSIC_CLOCK_OK : MUSIC_CLOCK_DIVIDE_BY_ZERO));
    if(rate) {
        uint32_t independent=(uint32_t)(((uint64_t)ticks+0x100000000ULL-origin)&0xffffffffULL)/rate;
        CHECK(result.units==independent && result.units==original_GetElapsedMusicTime());
        CHECK(result.units==((uint32_t)a.dx<<16 | a.ax));
    } else CHECK(old==UGH_UNSUPPORTED && a.ax==shell().ax && a.dx==shell().dx);
}
int main(void)
{
    unsigned disable_count=0,swap_count=0,elapsed_count=0;
    for (unsigned v=0;v<65536;v++) {
        uint16_t playing[4]={0,(uint16_t)v,0x8000,0xffff};
        uint16_t enabled[4]={(uint16_t)v,0x5aa5,(uint16_t)v,(uint16_t)v};
        for(unsigned i=0;i<4;i++) {
            MainAdlxPlaying=playing[i];MainAdlxSectionLoopEnabled=enabled[i];
            wr16(SOUND_SEG,S(MainAdlxPlaying),playing[i]);wr16(SOUND_SEG,S(MainAdlxSectionLoopEnabled),enabled[i]);
            Regs a=shell(),b=a;CHECK(original_DisableMusicSectionLoop()==1);
            CHECK(music_clock_disable_section_loop(playing[i],enabled[i])==MainAdlxSectionLoopEnabled);
            CHECK(l1_DisableMusicSectionLoop(&a)==UGH_OK);
            uint16_t expected=rd16(SOUND_SEG,S(MainAdlxSectionLoopEnabled));
            wr16(SOUND_SEG,S(MainAdlxSectionLoopEnabled),enabled[i]);
            CHECK(c_DisableMusicSectionLoop(&b)==UGH_OK);
            CHECK(!memcmp(&a,&b,sizeof a) && expected==MainAdlxSectionLoopEnabled);
            CHECK(expected==rd16(SOUND_SEG,S(MainAdlxSectionLoopEnabled)));disable_count++;
        }
        uint32_t values[4]={v,(uint32_t)v<<16,(uint32_t)v*65537u,~((uint32_t)v*65537u)};
        for(unsigned i=0;i<4;i++) {
            Regs a=shell(),b=a;wr16(a.ss,a.sp+4,(uint16_t)values[i]);wr16(a.ss,a.sp+6,(uint16_t)(values[i]>>16));
            CHECK(l1_SwapDwordByteOrder(&a)==UGH_OK && c_SwapDwordByteOrder(&b)==UGH_OK);
            CHECK(!memcmp(&a,&b,sizeof a));
            uint32_t independent=0;
            for(unsigned byte=0;byte<4;byte++)independent=independent*256u+((values[i]>>(8*byte))&255);
            CHECK(independent==music_clock_swap_bytes(values[i]));
            CHECK(independent==original_SwapDwordByteOrder(values[i]));swap_count++;
        }
        elapsed(0,1,(uint16_t)v);elapsed(0xffffffffu,0x80000000u,(uint16_t)v);
        elapsed(16,0xfffffff0u,(uint16_t)v);elapsed_count+=3;
    }
    uint32_t seed=0x91a761b5u;
    for(unsigned i=0;i<20000;i++) {
        seed=seed*1664525u+1013904223u;uint32_t ticks=seed;
        seed=seed*1664525u+1013904223u;uint32_t origin=seed;
        seed=seed*1664525u+1013904223u;elapsed(ticks,origin,(uint16_t)seed);elapsed_count++;
    }
    printf("{\"disable\":%u,\"swap\":%u,\"elapsed\":%u}\n",disable_count,swap_count,elapsed_count);
    return 0;
}
