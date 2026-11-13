/* Independent native reader for tests/scenarios text files. Fixtures are cold setup,
 * never a snapshot obtained from executing either implementation. */
#include "host.h"
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
Scenario scenario;
static uint8_t cycle[128];
static unsigned cycle_count,cycle_cursor,joy_count,joy_start;
static Wave *joy_cycles;
static int loaded=-1;

HostSymbol host_symbol(const char *name) {
    for(unsigned i=0;i<host_symbol_count;i++)
        if(!strcmp(name,host_symbols[i].name)) return host_symbols[i];
    host_fail(name); return (HostSymbol){0,0,0};
}
InputScript *host_script(uint16_t port) {
    Devices *d=&ugh_devices;
    for(unsigned i=0;i<d->script_count;i++) if(d->scripts[i].port==port) return &d->scripts[i];
    if(d->script_count==16) host_fail("input script capacity");
    InputScript *s=&d->scripts[d->script_count++]; memset(s,0,sizeof *s); s->port=port; return s;
}
void host_values(uint16_t port,const uint32_t *values,unsigned count,uint32_t cycles) {
    if(!count || count>128 || !cycles) host_fail("invalid input waveform");
    InputScript *s=host_script(port); memset(s,0,sizeof *s); s->port=port;
    s->cycles=s->cycles_left=cycles;
    for(unsigned i=0;i<count;i++) {
        if(s->count && s->runs[s->count-1].value==values[i]) s->runs[s->count-1].repeat++;
        else s->runs[s->count++]=(ScriptRun){values[i],1};
    }
}
void host_wave(const Wave *wave) {
    uint32_t values[128];
    for(unsigned i=0;i<wave->count;i++) values[i]=wave->bytes[i];
    host_values(0x201,values,wave->count,0xffffffff);
}
static void update_wave(const Wave *wave) {
    InputScript *s=host_script(0x201);
    s->count=wave->count; s->cursor=s->used=0; s->cycles=s->cycles_left=0xffffffff;
    for(unsigned i=0;i<wave->count;i++) s->runs[i]=(ScriptRun){wave->bytes[i],1};
}
static unsigned key(const char *word) {
    static const char *names[]={"esc","enter","space","q","c","f1","f2","f3","f4","f5","up","down","left","right"};
    static const unsigned codes[]={1,0x1c,0x39,0x10,0x2e,0x3b,0x3c,0x3d,0x3e,0x3f,0x48,0x50,0x4b,0x4d};
    for(unsigned i=0;i<sizeof codes/sizeof codes[0];i++) if(!strcmp(word,names[i])) return codes[i];
    char *end; unsigned long v=strtoul(word,&end,16);
    if(!*word || *end || v>255) host_fail("invalid scan code");
    return (unsigned)v;
}
static void append(uint8_t *dest,unsigned *count,unsigned scan) {
    if(*count==128) host_fail("scan queue capacity");
    dest[(*count)++]=(uint8_t)scan;
}
static void scan_word(char *word,uint8_t *dest,unsigned *count) {
    int release=*word=='-'; if(*word=='+' || *word=='-') word++;
    if(!strcmp(word,"up") || !strcmp(word,"down") || !strcmp(word,"left") || !strcmp(word,"right")) append(dest,count,0xe0);
    append(dest,count,key(word)|(release?128:0));
}
static Wave wave(int x,int y) {
    if(x < -1 || x>1 || y < -1 || y>1) host_fail("stick axis must be -1/0/1");
    int a=x<0?2:x>0?28:9,b=y<0?2:y>0?28:10;
    Wave w={0,{0}}; w.bytes[w.count++]=0xf0; w.bytes[w.count++]=0xf0;
    for(int t=0;t<(a>b?a:b)+4;t++) w.bytes[w.count++]=(uint8_t)(0xf0|(t<a?1:0)|(t<b?2:0));
    return w;
}
static void parse_wave(char *text,Wave *w,const char *separators) {
    char *context=NULL; w->count=0;
    for(char *v=strtok_r(text,separators,&context);v;v=strtok_r(NULL,separators,&context)) append(w->bytes,&w->count,key(v));
    if(!w->count) host_fail("empty joystick waveform");
}
void scenario_defaults(void) {
    memset(&scenario,0,sizeof scenario); strcpy(scenario.entry,"GAME:RunDosGame");
    scenario.frames=32; scenario.players=1; scenario.adlib=1;
    scenario.input=calloc(MAX_FRAMES+1,sizeof *scenario.input);
    if(!scenario.input) host_fail("input allocation");
}
void scenario_read(const char *path) {
    FILE *f=fopen(path,"rb"); if(!f) host_fail("cannot open scenario");
    scenario.adlib=0; char line[8192]; unsigned number=0;
    while(fgets(line,sizeof line,f)) {
        number++;
        if(!strchr(line,'\n') && !feof(f)) host_fail("scenario line too long");
        char *comment=strchr(line,'#'); if(comment) *comment=0;
        char *text=line; while(isspace((unsigned char)*text)) text++;
        if(!*text) continue;
        if(isdigit((unsigned char)*text) && strchr(text,':')) {
            char *end; unsigned long frame=strtoul(text,&end,10);
            if(*end!=':' || frame>MAX_FRAMES) host_fail("invalid event frame");
            FrameInput *e=&scenario.input[frame]; char *context=NULL;
            for(char *word=strtok_r(end+1," \t\r\n",&context);word;word=strtok_r(NULL," \t\r\n",&context)) {
                if(!strncmp(word,"stick=",6)) {
                    int x,y; if(sscanf(word+6,"%d,%d",&x,&y)!=2) host_fail("invalid stick");
                    e->joy=wave(x,y); e->joy_set=1;
                } else if(!strncmp(word,"sticks=",7)) {
                    char *ctx=NULL; free(e->joy_cycles); e->joy_cycles=calloc(128,sizeof(Wave)); e->joy_count=0;
                    if(!e->joy_cycles) host_fail("stick allocation");
                    for(char *pair=strtok_r(word+7,";",&ctx);pair;pair=strtok_r(NULL,";",&ctx)) {
                        int x,y; if(e->joy_count==128 || sscanf(pair,"%d,%d",&x,&y)!=2) host_fail("invalid sticks");
                        e->joy_cycles[e->joy_count++]=wave(x,y);
                    }
                } else if(!strncmp(word,"joy=",4)) { parse_wave(word+4,&e->joy,","); e->joy_set=1; }
                else if(!strncmp(word,"cycle=",6)) {
                    e->cycle_set=1; e->cycle_count=0;
                    if(strcmp(word+6,"off")) {
                        char *ctx=NULL;
                        for(char *v=strtok_r(word+6,",",&ctx);v;v=strtok_r(NULL,",",&ctx)) scan_word(v,e->cycle,&e->cycle_count);
                    }
                } else scan_word(word,e->scans,&e->count);
            }
            continue;
        }
        char *context=NULL,*name=strtok_r(text," \t\r\n",&context),*v=strtok_r(NULL,"\r\n",&context);
        if(!v) host_fail("missing scenario value");
        while(isspace((unsigned char)*v)) v++;
        size_t len=strlen(v); while(len && isspace((unsigned char)v[len-1])) v[--len]=0;
        if(!strcmp(name,"entry")) { if(len>=sizeof scenario.entry) host_fail("entry too long"); strcpy(scenario.entry,v); }
        else if(!strcmp(name,"frames")) scenario.frames=(unsigned)strtoul(v,NULL,10);
        else if(!strcmp(name,"players")) scenario.players=(unsigned)strtoul(v,NULL,10);
        else if(!strcmp(name,"card")) { if(strcmp(v,"none") && strcmp(v,"adlib")) host_fail("invalid card"); scenario.adlib=!strcmp(v,"adlib"); }
        else if(!strcmp(name,"end")) { if(strcmp(v,"return") && strcmp(v,"exit")) host_fail("invalid end"); strcpy(scenario.end,v); }
        else if(!strcmp(name,"timing")) { if(strcmp(v,"pit-quantum-at-polls")) host_fail("invalid timing policy"); }
        else if(!strcmp(name,"joystick")) parse_wave(v,&scenario.joystick," \t");
        else if(!strcmp(name,"password")) { if(len>20) host_fail("password capacity"); strcpy(scenario.password,v); }
        else if(!strcmp(name,"score")) { scenario.score=(uint32_t)strtoul(v,NULL,10); scenario.score_set=1; }
        else if(!strcmp(name,"scores")) { if(strcmp(v,"blank")) host_fail("invalid scores"); scenario.blank_scores=1; }
        else if(!strcmp(name,"bios")) {
            char *ctx=NULL;
            for(char *b=strtok_r(v," \t",&ctx);b;b=strtok_r(NULL," \t",&ctx)) {
                if(scenario.bios_count==128) host_fail("BIOS capacity");
                scenario.bios[scenario.bios_count++]=(uint32_t)strtoul(b,NULL,16);
            }
        } else if(strcmp(name,"requires") && strcmp(name,"expect") && strcmp(name,"death")) {
            fprintf(stderr,"line %u: %s\n",number,name); host_fail("unknown scenario directive");
        }
    }
    fclose(f);
    if(!scenario.frames || scenario.frames>MAX_FRAMES || scenario.players<1 || scenario.players>2) host_fail("invalid scenario bounds");
}
void scenario_fixture(void) {
    uint32_t retrace[]={0,8},time[]={0x10203040},adlib[66]={0,0xc0};
    host_values(0x3da,retrace,2,0xffffffff);
    if(scenario.joystick.count) host_wave(&scenario.joystick);
    else { uint32_t absent=255; host_values(0x201,&absent,1,0xffffffff); host_script(0x201)->runs[0].repeat=10000; }
    host_values(0xfffe,time,1,0xffffffff);
    if(scenario.adlib) host_values(0x388,adlib,66,0xffffffff);
    else { uint32_t absent=0xe0; host_values(0x388,&absent,1,0xffffffff); }
    wr16(0,0x20,0x100); wr16(0,0x22,0xf000);
    Devices *d=&ugh_devices; d->irq_count=2;
    d->irqs[0]=(IrqEvent){SOUND_SEG,S(loc_1163),0,0,65536};
    d->irqs[1]=(IrqEvent){SOUND_SEG,S(loc_116B),0,0,65536};
    if(strcmp(scenario.entry,"GAME:RunDosGame")) {
        wr16(GAME_SEG,G(PlayfieldHeight),192); wr16(GAME_SEG,G(VgaPlaneCopyByteCount),0x4800);
        wr16(GAME_SEG,G(DrawPagePointer),0x5a08); wr16(GAME_SEG,G(DisplayedVgaPagePointer),0xa88);
        wr16(GAME_SEG,G(BackgroundPagePointer),0xa988);
        wr16(GAME_SEG,G(DrawPagePointer)+2,0xa000); wr16(GAME_SEG,G(DisplayedVgaPagePointer)+2,0xa000);
        wr16(GAME_SEG,G(BackgroundPagePointer)+2,0xa000);
        wr16(DATA_SEG,D(PlayerCount),(uint16_t)scenario.players); wr16(DATA_SEG,D(PlayerArrayBytes),(uint16_t)(2*scenario.players));
        wr16(DATA_SEG,D(PlayerOneControlMode),0xffff); wr16(DATA_SEG,D(PlayerTwoControlMode),0xffff);
        wr16(DATA_SEG,D(JoystickSampleLoopLimit),3); wr16(DATA_SEG,D(WaterYPixels),200);
        wr8(DATA_SEG,D(JoystickEnabledAxisMask),0);
        wr16(0,0x24,G(HandleKeyboardScanInterrupt)); wr16(0,0x26,GAME_SEG); d->irq_count=0;
    }
    if(scenario.bios_count) host_values(0xffff,scenario.bios,scenario.bios_count,1);
    if(scenario.blank_scores) {
        DosFile *f=&d->files[0]; strcpy((char *)f->name,"UGH!.HI"); f->exists=1; f->length=107;
        for(unsigned i=0;i<107;i++) f->data[i]=rd8(DATA_SEG,(uint16_t)(D(HighScoreRows)+i));
        for(unsigned row=0;row<5;row++) memset(f->data+14+21*row,' ',6);
        for(unsigned i=0;i<107;i++) f->data[i]^=255;
    }
    if(scenario.score_set) { wr16(DATA_SEG,D(ScoreLowWord),(uint16_t)scenario.score); wr16(DATA_SEG,D(ScoreHighWord),(uint16_t)(scenario.score>>16)); }
    if(*scenario.password) {
        memset(ugh_mem+lin(DATA_SEG,D(PasswordEditBuffer)),' ',20);
        memcpy(ugh_mem+lin(DATA_SEG,D(PasswordEditBuffer)),scenario.password,strlen(scenario.password));
    }
}
void scenario_load_frame(unsigned frame,void (*enqueue)(uint8_t)) {
    if(frame>MAX_FRAMES) return;
    for(int f=loaded+1;f<=(int)frame;f++) {
        FrameInput *e=&scenario.input[f];
        for(unsigned i=0;i<e->count;i++) enqueue(e->scans[i]);
        if(e->cycle_set) { cycle_count=e->cycle_count; cycle_cursor=0; memcpy(cycle,e->cycle,cycle_count); }
        if(e->joy_count) { joy_cycles=e->joy_cycles; joy_count=e->joy_count; joy_start=(unsigned)f; }
        if(e->joy_set) update_wave(&e->joy);
        else if(joy_count) update_wave(&joy_cycles[((unsigned)f-joy_start)%joy_count]);
    }
    loaded=(int)frame;
}
int scenario_cycle_scan(uint8_t *scan) {
    if(!cycle_count) return 0;
    *scan=cycle[cycle_cursor++%cycle_count]; return 1;
}
