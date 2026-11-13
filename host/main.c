/* Native engine: literal adapters, no instruction decoder or CPU emulation.
 * IRQ placement is wholegame.Clock's deterministic policy. Wall time only
 * paces those placements; it cannot add, drop or reorder game interrupts. */
#include "host.h"
#include <SDL3/SDL_main.h>
#include <stdlib.h>
#include <string.h>
#include <stddef.h>
#include <direct.h>
#include <errno.h>
#include <windows.h>
#include <stdatomic.h>
unsigned host_frame,host_limit;
int host_headless,host_scripted,host_digests,host_quit;
const char *host_shot;
static int paced=1,smoke,stopped,terminal_seen;
static uint64_t start_ns,wall_start_ns,deadline_ns,irq_time_ns,retrace_time_ns,audio_time_ns,timer_irqs,retraces;
extern void ugh_devices_reset(void);
extern const char *host_native_units[];
extern const unsigned host_native_unit_count;
extern const char *host_variant;
static double timeout_seconds;
static const char *save_dir;
static DosFile persisted;
static atomic_int watchdog_stop;
static int SDLCALL watchdog(void *unused) {
    (void)unused;
    while(!atomic_load(&watchdog_stop)) {
        SDL_Delay(100);
        if(SDL_GetTicksNS()-wall_start_ns>(uint64_t)(timeout_seconds*1e9)) {
            fprintf(stderr,"host: wall-time bound exceeded\n"); fflush(stderr); ExitProcess(4);
        }
    }
    return 0;
}
void host_fail(const char *why) { fprintf(stderr,"host: %s (%s)\n",why,SDL_GetError()); exit(1); }
static unsigned word(const uint8_t *p) { return p[0]+256u*p[1]; }
extern const char host_data_hash[];
static void load_data(const char *path) {
    FILE *f=fopen(path,"rb"); if(!f) host_fail("missing ugh-data.exe; run python tools/build.py then tools/hostbuild.py");
    if(fseek(f,0,SEEK_END)) host_fail("data seek failed");
    long size=ftell(f); rewind(f);
    if(size<28 || size>2*1024*1024) host_fail("invalid data size");
    uint8_t *bytes=malloc((size_t)size); if(!bytes) host_fail("data allocation failed");
    if(fread(bytes,1,(size_t)size,f)!=(size_t)size) host_fail("data read failed");
    fclose(f);
    char hash[65]; host_sha256(bytes,(unsigned)size,hash);
    if(strcmp(hash,host_data_hash)) host_fail("data differs from the rebuilt executable used to compile this host");
    unsigned header=word(bytes+8)*16,relocs=word(bytes+6),table=word(bytes+24);
    if(word(bytes)!=0x5a4d || header>(unsigned)size || table+4*relocs>header || UGH_LOAD*16+(unsigned)size-header>0xa0000) host_fail("invalid MZ data");
    memset(ugh_mem,0,UGH_MEM_SIZE); memcpy(ugh_mem+UGH_LOAD*16,bytes+header,(size_t)size-header);
    for(unsigned i=0;i<relocs;i++) {
        unsigned site=word(bytes+table+4*i)+16*word(bytes+table+4*i+2);
        if(site+2>(unsigned)size-header) host_fail("invalid relocation");
        uint32_t address=UGH_LOAD*16+site;
        uint16_t v=(uint16_t)(word(ugh_mem+address)+UGH_LOAD);
        ugh_mem[address]=(uint8_t)v; ugh_mem[address+1]=(uint8_t)(v>>8);
    }
    free(bytes);
}
static void scores_load(void) {
    if(_mkdir(save_dir) && errno!=EEXIST) host_fail("cannot create save directory");
    char path[4096]; if(snprintf(path,sizeof path,"%s/UGH!.HI",save_dir)>=(int)sizeof path) host_fail("save path too long");
    FILE *f=fopen(path,"rb");
    if(f) {
        DosFile *file=&ugh_devices.files[0]; strcpy((char *)file->name,"UGH!.HI"); file->exists=1;
        file->length=(uint32_t)fread(file->data,1,sizeof file->data,f);
        if(ferror(f) || fgetc(f)!=EOF) host_fail("score file exceeds DOS file capacity");
        fclose(f);
    } else if(errno!=ENOENT) host_fail("cannot read score file");
    persisted=ugh_devices.files[0];
}
static void scores_save(void) {
    if(!save_dir) return;
    for(unsigned i=0;i<8;i++) {
        DosFile *f=&ugh_devices.files[i];
        if(!f->exists || strcmp((char *)f->name,"UGH!.HI") ||
           (persisted.exists && persisted.length==f->length && !memcmp(persisted.data,f->data,f->length))) continue;
        char path[4096],temp[4096]; snprintf(path,sizeof path,"%s/UGH!.HI",save_dir); snprintf(temp,sizeof temp,"%s/UGH!.HI.tmp",save_dir);
        FILE *out=fopen(temp,"wb"); if(!out) host_fail("cannot write score file");
        if(fwrite(f->data,1,f->length,out)!=f->length) host_fail("score write failed");
        if(fclose(out)) host_fail("score close failed");
        if(!MoveFileExA(temp,path,MOVEFILE_REPLACE_EXISTING|MOVEFILE_WRITE_THROUGH)) host_fail("score replacement failed");
        persisted=*f;
    }
}
static void pace_and_audio(void) {
    uint64_t elapsed=irq_time_ns>retrace_time_ns?irq_time_ns:retrace_time_ns;
    if(elapsed>audio_time_ns) { host_audio_advance(elapsed-audio_time_ns); audio_time_ns=elapsed; }
    if(host_headless || !paced) return;
    deadline_ns=start_ns+elapsed;
    /* A pause/slow renderer must not build an unlimited audio queue or catch-up
     * burst. Resync wall origin; the integer game clock and events stay intact. */
    uint64_t now=SDL_GetTicksNS();
    if(now>deadline_ns+250000000ull) { start_ns+=now-deadline_ns; deadline_ns=now; }
    while(!host_quit && (now=SDL_GetTicksNS())<deadline_ns) {
        host_input_pump(); uint64_t left=deadline_ns-now; SDL_DelayNS(left>2000000?2000000:left);
    }
}
static int timer_site(uint16_t seg,uint16_t off) {
    return (seg==GAME_SEG && off==G(WaitVerticalRetraceActive)) ||
        (seg==SOUND_SEG && off==S(loc_1EA3)) ||
        (seg==UGH_S_C_StopSoundChannel && off==UGH_O_C_StopSoundChannel+0x53) ||
        (seg==UGH_S_C_StopMusicTrack && off==UGH_O_C_StopMusicTrack+0x95) ||
        (seg==UGH_S_C_LoadIffSample && off==UGH_O_C_LoadIffSample+0x4e7);
}
static int service(uint16_t segment,uint16_t offset,Regs *r) {
    Devices *d=&ugh_devices;
    host_input_pump(); if(host_quit) { stopped=1; return UGH_BUDGET; }
    int retrace=segment==GAME_SEG && offset==G(WaitVerticalRetraceActive);
    if(retrace) { retraces++; retrace_time_ns+=14268000ull; }
    if((r->flags&IF) && d->irq_cursor>=d->irq_count) {
        if(timer_site(segment,offset) && !(d->pic_mask&1)) {
            if(rd16(0,0x22)==TIMER_SEG) {
                uint32_t clocks=d->pit_divisor?d->pit_divisor:65536;
                d->irq_cursor=0; d->irq_count=1; d->irqs[0]=(IrqEvent){segment,offset,0,0,clocks};
                irq_time_ns+=(uint64_t)clocks*1000000000ull/1193182; timer_irqs++;
            }
        } else if(segment==GAME_SEG && offset==G(PollKeyboardScanChange)) {
            if(host_scripted) scenario_load_frame(host_frame,host_enqueue);
            if(d->pic_mask&2) return UGH_OK;
            uint8_t scan;
            int got=host_take_scan(&scan);
            if(!got && host_scripted) got=scenario_cycle_scan(&scan);
            if(got) {
                uint32_t v=scan; host_values(0x60,&v,1,1);
                d->irq_cursor=0; d->irq_count=1; d->irqs[0]=(IrqEvent){segment,offset,0,1,0};
            }
        }
    }
    if(retrace || timer_site(segment,offset)) {
        pace_and_audio();
        if(retrace && !host_headless) host_present();
    }
    return UGH_OK;
}
static int boundary(Regs *r) {
    if(ugh_devices.error) return UGH_UNSUPPORTED;
    if(host_digests) host_digest(r,NULL);
    if(host_digests) fflush(stdout);
    ugh_devices.count=0; host_frame++;
    if(!host_headless) host_present();
    scores_save();
    if(host_limit && host_frame>=host_limit) { stopped=1; return UGH_BUDGET; }
    return UGH_OK;
}
static unsigned number(const char *text) {
    char *end; unsigned long v=strtoul(text,&end,10);
    if(!*text || *end || !v || v>MAX_FRAMES) host_fail("frame/scale bound invalid");
    return (unsigned)v;
}
static void usage(void) {
    puts("ugh [--headless N] [--script FILE] [--frames N] [--digests] [--smoke N]\n"
         "    [--data FILE] [--save-dir DIR] [--shot FILE.bmp] [--wav FILE.wav]\n"
         "    [--timeout SECONDS] [--scale 1..8] [--no-audio] [--unpaced]\n"
         "Headless emits wholegame-compatible JSON records to stdout. Diagnostics use stderr.\n"
         "--smoke starts the cold attract fixture; --script accepts tests/scenarios/*.txt.");
}
static void print_version(void) {
    printf("Ugh host (%s); native units:",host_variant);
    if(!host_native_unit_count) printf(" none (literal L1)");
    for(unsigned i=0;i<host_native_unit_count;i++) printf(" %s",host_native_units[i]);
    putchar('\n');
}
int main(int argc,char **argv) {
    const char *script=NULL,*data=NULL,*wav=NULL; int scale=3,audio=1,frame_option=0;
    scenario_defaults();
    for(int i=1;i<argc;i++) if(!strcmp(argv[i],"--version")) { print_version(); return 0; }
    for(int i=1;i<argc;i++) {
        const char *arg=argv[i];
        if(!strcmp(arg,"--help")) { usage(); return 0; }
        if(!strcmp(arg,"--no-audio")) { audio=0; continue; }
        if(!strcmp(arg,"--unpaced")) { paced=0; continue; }
        if(!strcmp(arg,"--digests")) { host_digests=1; continue; }
        if(i+1==argc) host_fail("option needs a value");
        const char *v=argv[++i];
        if(!strcmp(arg,"--headless")) { host_headless=1; host_digests=1; host_limit=number(v); frame_option=1; }
        else if(!strcmp(arg,"--frames")) { host_limit=number(v); frame_option=1; }
        else if(!strcmp(arg,"--smoke")) { smoke=1; host_limit=number(v); frame_option=1; }
        else if(!strcmp(arg,"--script")) { script=v; host_scripted=1; }
        else if(!strcmp(arg,"--data")) data=v;
        else if(!strcmp(arg,"--save-dir")) save_dir=v;
        else if(!strcmp(arg,"--shot")) host_shot=v;
        else if(!strcmp(arg,"--wav")) wav=v;
        else if(!strcmp(arg,"--scale")) { scale=(int)number(v); if(scale>8) host_fail("scale must be 1..8"); }
        else if(!strcmp(arg,"--timeout")) { char *end; timeout_seconds=strtod(v,&end); if(*end || timeout_seconds<1 || timeout_seconds>3600) host_fail("timeout must be 1..3600 seconds"); }
        else host_fail("unknown option (use --help)");
    }
    if(script) { scenario_read(script); if(!frame_option) host_limit=scenario.frames; }
    if(smoke) { if(script) host_fail("--smoke and --script are separate modes"); strcpy(scenario.entry,"GAME:PlayAttractDemo"); scenario.adlib=0; host_scripted=1; }
    if(!timeout_seconds && (host_headless || host_limit)) timeout_seconds=120;
    if(host_headless) audio=0;
    if(!SDL_Init(host_headless?0:SDL_INIT_VIDEO|SDL_INIT_GAMEPAD|(audio?SDL_INIT_AUDIO:0))) host_fail("SDL init failed");
    wall_start_ns=start_ns=SDL_GetTicksNS();
    SDL_Thread *guard=timeout_seconds?SDL_CreateThread(watchdog,"ugh-bound",NULL):NULL;
    if(timeout_seconds && !guard) host_fail("watchdog failed");
    host_digest_init();
    char data_path[4096],save_path[4096]; const char *base=SDL_GetBasePath();
    if(!base) host_fail("executable directory unavailable");
    if(!data) { snprintf(data_path,sizeof data_path,"%sugh-data.exe",base); data=data_path; }
    load_data(data); ugh_devices_reset(); scenario_fixture();
    if(!host_headless && (!host_scripted || save_dir)) {
        if(!save_dir) { snprintf(save_path,sizeof save_path,"%ssaves",base); save_dir=save_path; }
        scores_load();
    } else save_dir=NULL;
    if(!host_scripted && !host_headless) ugh_set_interrupt_service(host_live_interrupt);
    if(!host_headless) { if(!host_video_init(scale)) host_fail("SDL window failed"); host_gamepad_init(); }
    if(!host_audio_init(audio,wav)) host_fail("SDL audio failed; use --no-audio on machines without an audio device");
    ugh_set_output_observer(host_audio_out);
    ugh_set_frame_observer(boundary); ugh_set_service_observer(service);
    HostSymbol entry=host_symbol(scenario.entry);
    Regs r={0}; r.cs=entry.segment; r.ip=entry.offset; r.ds=r.es=DATA_SEG;
    r.ss=0x8000; r.sp=0xfefe; r.flags=0x202; wr16(r.ss,r.sp,0xfff0);
    int status=ugh_dispatch(entry.segment,entry.offset,&r);
    if(*scenario.end && !stopped && ((!strcmp(scenario.end,"exit") && status==UGH_DOS_EXIT) || (!strcmp(scenario.end,"return") && status==UGH_OK))) {
        if(status==UGH_OK) { r.sp=(uint16_t)(r.sp+2); r.ip=0xfff0; }
        if(host_digests) host_digest(&r,scenario.end);
        terminal_seen=1;
    }
    scores_save(); if(host_shot) host_save_shot(host_shot);
    ugh_set_output_observer(NULL); ugh_set_service_observer(NULL); ugh_set_frame_observer(NULL); ugh_set_interrupt_service(NULL);
    host_audio_close(); host_digest_close(); host_input_close(); host_video_close();
    atomic_store(&watchdog_stop,1); if(guard) SDL_WaitThread(guard,NULL);
    fprintf(stderr,"host: status=%d error=%u flips=%u retraces=%llu timer_irqs=%llu terminal=%d wall=%.3fs\n",
        status,ugh_devices.error,host_frame,(unsigned long long)retraces,(unsigned long long)timer_irqs,terminal_seen,(SDL_GetTicksNS()-wall_start_ns)/1e9);
    SDL_Quit();
    if(ugh_devices.error) return 2;
    if(host_quit) return 0;
    if(*scenario.end && !terminal_seen) return 2;
    return (stopped && status==UGH_BUDGET) || terminal_seen || status==UGH_DOS_EXIT?0:2;
}
