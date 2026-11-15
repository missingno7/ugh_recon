#include "s7_shadow.h"
#include "input.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
extern void ugh_devices_reset(void);
/* Only oracle platform references these entrypoints; no engine is called. */
int ugh_dispatch_interrupt(uint16_t s,uint16_t o,Regs *r){(void)s;(void)o;(void)r;abort();}
#define CHECK(x) do{if(!(x)){fprintf(stderr,"EDGE FAIL line %d: %s\n",__LINE__,#x);exit(86);}}while(0)
static uint32_t random_word=0x91723041;
static uint32_t rng(void){random_word^=random_word<<13;random_word^=random_word>>17;random_word^=random_word<<5;return random_word;}
static void gc(unsigned index,unsigned value){platform_out(0x3ce,2,index+(value<<8));}
static void script(uint16_t port,const GSTestRun *runs,unsigned n,uint32_t cycles){
    InputScript *s=NULL;for(unsigned i=0;i<ugh_devices.script_count;i++)if(ugh_devices.scripts[i].port==port)s=&ugh_devices.scripts[i];
    if(!s)s=&ugh_devices.scripts[ugh_devices.script_count++];memset(s,0,sizeof *s);s->port=port;s->count=n;s->cycles=s->cycles_left=cycles;
    for(unsigned i=0;i<n;i++)s->runs[i]=(ScriptRun){runs[i].value,runs[i].repeat};
}
static void copy_cell(uint16_t src,uint16_t dst){
    uint8_t v=0;CHECK(s7_services.video.copy(&s7_backend,src,dst,&v)==GS_OK);
    uint8_t expected=s7_model_read(0xa0000u+src);s7_model_write(0xa0000u+dst,expected);CHECK(v==expected);s7_check();
}
static void video_edges(void){
    ugh_devices_reset();for(unsigned p=0;p<4;p++)for(unsigned i=0;i<65536;i++)ugh_devices.plane[p][i]=(uint8_t)rng();
    GSTestRun retraces[]={{0,1},{8,1}};script(0x3da,retraces,2,1);s7_begin();
    /* All write modes, operations, rotations, set/reset, masks and compare/care. */
    for(unsigned i=0;i<30000;i++){
        unsigned reg=rng()%9;gc(reg,rng()&255);platform_out(0x3c4,2,2+((rng()&255)<<8));
        uint16_t src=(uint16_t)rng(),dst=(uint16_t)rng();ugh_read(0xa0000u+src);ugh_write(0xa0000u+dst,(uint8_t)rng());
        /* Reuse the existing latches at a second destination. */
        ugh_write(0xa0000u+(uint16_t)(dst+1),(uint8_t)rng());
        if(i%300==0)s7_check();if(i%73==0)copy_cell(dst,(uint16_t)(dst+2));
    }
    gc(5,0);gc(1,0);gc(3,0);gc(8,255);platform_out(0x3c4,2,0xf02);
    ugh_write(0xa0010,0x95);gc(5,1);copy_cell(16,17);copy_cell(17,18);
    gc(5,0);gc(3,0x10);gc(8,0x40);
    uint8_t old=0;CHECK(s7_services.video.water_mark(&s7_backend,18,&old)==GS_OK);uint8_t expected=s7_model_read(0xa0012);s7_model_write(0xa0012,0x40);CHECK(old==expected);s7_check();
    gc(5,0);CHECK(s7_services.video.store_word(&s7_backend,65535,0x1122)==GS_UNSUPPORTED);s7_model_write(0xaffff,0x22);s7_check();
    for(unsigned i=0;i<5000;i++){
        if(i%17==0)platform_out(0x3c8,1,rng()&255);platform_out(0x3c9,1,rng()&255);
        if(i%101==0)s7_check();
    }
    platform_out(0x3c0,1,3);platform_in(0x3c1,1); /* inherited attribute phase */
    CHECK(platform_in(0x3da,1)==0);CHECK(platform_in(0x3da,1)==8);
    s7_finish();puts("PASS video modes/latches/live copies/water/partial DAC/prefix");
}
static void count_case(uint16_t limit,uint8_t enabled,const GSTestRun *runs,unsigned n){
    ugh_devices_reset();script(0x201,runs,n,1);s7_begin();
    CHECK(gs_test_stream(&s7_backend.joystick,runs,n,1)==GS_OK);
    GSJoystickCounts got;unsigned start=ugh_devices.count;CHECK(s7_services.input.counts(&s7_backend,limit,enabled,&got)==GS_OK);
    InputAxisTimer work=input_axis_begin(limit,enabled);
    if(enabled)for(;;){int more=input_axis_delivery(&work,(uint8_t)s7_model_in(0x201,1));CHECK(more>=0);if(!more)break;}
    CHECK(got.remaining==work.remaining);for(unsigned a=0;a<4;a++){CHECK(got.latched[a]==work.latched[a]);CHECK(got.counts[a]==input_axis_count(limit,work.latched[a]));}
    s7_effects(start);InputScript *s=&ugh_devices.scripts[0];CHECK(s7_backend.joystick.cursor==s->cursor&&s7_backend.joystick.used==s->used);s7_finish();
}
static void input_edges(void){
    ugh_devices_reset();GSTestRun scans[]={{0xe0,1},{0x4b,1},{0xe0,1},{0xcb,1},{0x1d,1},{0x9d,1}};script(0x60,scans,6,1);
    GSTestRun keys[]={{0x1e61,1},{0x4800,1},{0x1c0d,1}};script(0xffff,keys,3,1);s7_begin();
    for(unsigned i=0;i<6;i++){CHECK(platform_in(0x60,1)==scans[i].value);platform_out(0x20,1,0x20);}
    Regs r={0};for(unsigned i=0;i<3;i++){r.ax=0x100;platform_interrupt(0x16,&r);CHECK(r.ax==keys[i].value);r.ax=0x100;platform_interrupt(0x16,&r);r.ax=0;platform_interrupt(0x16,&r);CHECK(r.ax==keys[i].value);}
    r.ax=0x100;platform_interrupt(0x16,&r);CHECK(r.flags&ZF);
    r.ax=0x3509;platform_interrupt(0x21,&r);r.ax=0x2509;r.ds=GAME_SEG;r.dx=G(HandleKeyboardScanInterrupt);platform_interrupt(0x21,&r);r.ax=0x3509;platform_interrupt(0x21,&r);r.ax=0x2509;r.ds=r.dx=0;platform_interrupt(0x21,&r);s7_finish();
    GSTestRun absent[]={{255,65536}},simultaneous[]={{0xf0,4}},phased[]={{255,2},{254,1},{252,1},{248,1},{240,1}};
    count_case(0,15,absent,1);count_case(0,15,simultaneous,1);count_case(0,15,phased,5);count_case(9,0,absent,1);
    count_case(7,15,phased,5);
    ugh_devices_reset();s7_begin();GSBinding untouched={91};
    CHECK(s7_services.input.vector(&s7_backend,GS_VECTOR_INSTALL,(GSBinding){99},&untouched)==GS_UNSUPPORTED&&untouched.token==91);
    s7_finish();
    /* D2 synthetic counts use the same units for calibration and later samples. */
    uint16_t prior=250;for(int a=INT16_MIN;a<=INT16_MAX;a++){
        uint16_t value=gs_test_axis_count((int16_t)a);CHECK(value>=prior&&value-prior<=1);prior=value;
    }CHECK(prior==1750&&gs_test_axis_count(0)==1000);
    GSTestBackend *b=&s7_backend;gs_test_init(b);GameServices s=gs_test_services(b);GSJoystickCounts c;
    CHECK(gs_test_gamepad(b,0,1,INT16_MIN,INT16_MAX,3)==GS_OK);CHECK(gs_test_gamepad(b,1,1,0,-1,1)==GS_OK);
    CHECK(s.input.counts(b,0,15,&c)==GS_OK&&c.counts[0]==250&&c.counts[1]==1750&&c.counts[2]==1000&&c.remaining==(uint16_t)(0-1750));
    puts("PASS scan/E0/break/queue/tokens/count units/zero-limit wrap");
}
static void file_edges(void){
    ugh_devices_reset();s7_begin();Regs r={0};r.ds=0x7000;r.dx=100;const char *name="UGH!.HI";
    for(unsigned i=0;i<8;i++)wr8(r.ds,(uint16_t)(r.dx+i),(uint8_t)name[i]);
    r.ax=0x3d00;platform_interrupt(0x21,&r);CHECK(r.ax==2&&(r.flags&CF));r.ax=0x3c00;platform_interrupt(0x21,&r);CHECK(r.ax==5);r.bx=r.ax;
    for(unsigned i=0;i<107;i++)wr8(r.ds,(uint16_t)(200+i),(uint8_t)(i^0xa5));r.dx=200;r.cx=107;r.ax=0x4000;platform_interrupt(0x21,&r);CHECK(r.ax==107);
    CHECK(s7_services.files.persist(&s7_backend)==GS_OK&&s7_backend.handles[5].active);
    r.ax=0x3e00;platform_interrupt(0x21,&r);r.dx=100;r.ax=0x3d00;platform_interrupt(0x21,&r);CHECK(r.ax==5);r.bx=r.ax;
    for(unsigned i=0;i<128;i++)wr8(r.ds,(uint16_t)(200+i),0xcc);r.dx=200;r.cx=128;r.ax=0x3f00;platform_interrupt(0x21,&r);CHECK(r.ax==107&&rd8(r.ds,307)==0xcc);
    r.ax=0x3f00;platform_interrupt(0x21,&r);CHECK(r.ax==0);r.ax=0x4000;platform_interrupt(0x21,&r);CHECK(r.ax==5&&(r.flags&CF));
    r.bx=4;r.ax=0x3e00;platform_interrupt(0x21,&r);CHECK(r.ax==6&&(r.flags&CF));s7_finish();
    /* Error injection and short-write limits are fixtures in both providers. */
    ugh_devices_reset();ugh_devices.dos_error=19;ugh_devices.dos_error_skip=1;ugh_devices.io_limit=7;s7_begin();
    r=(Regs){0};r.ds=0x7000;r.dx=100;r.ax=0x3c00;platform_interrupt(0x21,&r);r.bx=r.ax;r.ax=0x4000;r.cx=20;r.dx=200;platform_interrupt(0x21,&r);CHECK(r.ax==19&&(r.flags&CF));
    r.ax=0x4000;platform_interrupt(0x21,&r);CHECK(r.ax==7);r.ax=0x4000;r.cx=0;platform_interrupt(0x21,&r);CHECK(r.ax==0);s7_finish();puts("PASS scores/short reads/retained tail/errors/limits/persist");
}
static void clock_edges(void){
    ugh_devices_reset();GSTestRun times[]={{0x10203040,1}};script(0xfffe,times,1,1);s7_begin();
    Regs seed_request={0};seed_request.ax=0x2c00;platform_interrupt(0x21,&seed_request);
    CHECK(seed_request.cx==0x1020&&seed_request.dx==0x3040);
    platform_out(0x43,1,0x36);platform_out(0x40,1,0x35);platform_out(0x40,1,0x12);platform_out(0x40,1,0xab);platform_out(0x43,1,0x36);platform_out(0x40,1,0);platform_out(0x40,1,0);
    platform_out(0x21,1,3);CHECK(platform_in(0x21,1)==3);
    CHECK(s7_services.time.interrupt(&s7_backend,0,65536,1)==GS_EMPTY);platform_out(0x21,1,0);
    CHECK(s7_services.time.interrupt(&s7_backend,0,65536,0)==GS_EMPTY);
    unsigned start=ugh_devices.count;ugh_devices.clocks+=65536;ugh_devices.log[ugh_devices.count++]=(IoEvent){LOG_IRQ,0,0,65536};s7_irq(0,65536,1);CHECK(ugh_devices.count==start+1);
    for(unsigned i=0;i<1000;i++){platform_out(0x388,1,rng()&255);platform_out(0x389,1,rng()&255);}
    GameServices *s=&s7_services;GSEvent e;
    for(unsigned i=1;i<=7000;i++){
        CHECK(s->time.deliver(&s7_backend,GS_RETRACE_INACTIVE,&e)==GS_OK);CHECK(s->time.deliver(&s7_backend,GS_RETRACE_ACTIVE,&e)==GS_OK);CHECK(e.tick==i&&e.nanoseconds==i/70u*1000000000ull+i%70u*1000000000ull/70);
        CHECK(s->time.deliver(&s7_backend,GS_TIMER_OPPORTUNITY,&e)==GS_OK&&e.tick==i);
    }
    CHECK(e.nanoseconds==100000000000ull);CHECK(s->time.suspend(&s7_backend,1)==GS_OK);CHECK(s->time.deliver(&s7_backend,GS_TIMER_OPPORTUNITY,&e)==GS_EMPTY);CHECK(s->time.suspend(&s7_backend,0)==GS_OK);CHECK(s->time.deliver(&s7_backend,GS_INPUT_OPPORTUNITY,&e)==GS_OK&&e.tick==7000);
    uint8_t v=77;GSBinding binding={55};GSCalibrationReply c={1,2,3};
    CHECK(s->video.compatibility(&s7_backend)==GS_UNSUPPORTED);CHECK(s->audio.status(&s7_backend,&v)==GS_UNSUPPORTED&&v==77);CHECK(s->audio.clock(&s7_backend,GS_CLOCK_TIMER)==GS_UNSUPPORTED);CHECK(s->audio.calibration(&s7_backend,GS_CALIBRATION_BEGIN,&c)==GS_UNSUPPORTED&&c.marker==3);
    CHECK(s->audio.timer_lifetime(&s7_backend,(GSTimerLifetimeRequest){0},&binding)==GS_UNSUPPORTED&&binding.token==55);
    CHECK(s->lifecycle.request(&s7_backend,(GSLifecycleRequest){GS_LIFECYCLE_START,0},&v)==GS_UNSUPPORTED&&v==77);CHECK(s->lifecycle.binding(&s7_backend,GS_BIND_CRITICAL_ERROR_FAIL,GS_VECTOR_INSTALL,binding,&binding)==GS_UNSUPPORTED&&binding.token==55);
    Regs r={0};r.ax=0x13;platform_interrupt(0x10,&r);r.ax=0xf00;platform_interrupt(0x10,&r);CHECK((r.ax&255)==0x13);r.ax=0x4c2a;platform_interrupt(0x21,&r);CHECK(s7_backend.exited&&s7_backend.exit_code==42);s7_finish();puts("PASS PIT/masks/IRQ/OPL/D1 scheduling/pending Unsupported/terminal");
}
int main(int argc,char **argv){
    if(argc!=2)return 2;
    if(!strcmp(argv[1],"video"))video_edges();else if(!strcmp(argv[1],"input"))input_edges();else if(!strcmp(argv[1],"files"))file_edges();else if(!strcmp(argv[1],"clock"))clock_edges();else return 2;return 0;
}
