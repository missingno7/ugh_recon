/* Verification only. The backend is compiled separately with no oracle headers.
 * Each actual host request is also consumed synchronously by GameServices.
 * Fixture changes are stimuli; backend state is never refreshed after begin. */
#include "s7_shadow.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
GSTestBackend s7_backend;
GameServices s7_services;
static int active;
static uint64_t requests[15],boundaries;
static InputScript previous[16];static unsigned previous_valid[16];
static uint16_t saved_keyboard[2];
static IoEvent effects[131072];static unsigned effect_count;
static void fail(const char *what){fprintf(stderr,"S7 MISMATCH %s at request %llu boundary %llu\n",what,(unsigned long long)requests[0],(unsigned long long)boundaries);exit(87);}
#define SAME(a,b) do {if(memcmp(&(a),&(b),sizeof(a)))fail(#a);}while(0)
#define EQUAL(a,b) do {if((a)!=(b))fail(#a);}while(0)
static uint16_t control_port(unsigned route){static const uint16_t ports[]={0x3c4,0x3c5,0x3ce,0x3cf,0x3d4,0x3d5,0x3c0,0x3c1,0x3da};return route<9?ports[route]:0;}
static int route(uint16_t port){for(unsigned i=0;i<9;i++)if(control_port(i)==port)return (int)i;return -1;}
static void record(void *ctx,GSTestEffect e){
    (void)ctx;unsigned kind=LOG_OUT,port=0,value=e.b,size=1;
    switch(e.kind){
    case GST_CONTROL_WRITE:port=control_port(e.a);break;
    case GST_CONTROL_READ:kind=LOG_IN;port=control_port(e.a);break;
    case GST_DAC:port=e.a==GS_DAC_SELECT?0x3c8:0x3c9;break;
    case GST_SCAN:kind=LOG_IN;port=0x60;break;
    case GST_ACK:port=0x20;break;
    case GST_JOYSTICK_START:port=0x201;break;
    case GST_JOYSTICK_SAMPLE:kind=LOG_IN;port=0x201;break;
    case GST_QUEUE:kind=LOG_DOS;port=0x16;size=0;value=e.a==GS_QUEUE_PEEK?0x100:0;break;
    case GST_VECTOR:kind=LOG_DOS;port=0x21;size=0;value=e.a==GS_VECTOR_CAPTURE?0x3500:0x2500;break;
    case GST_OPL:port=e.a==GS_OPL_SELECT?0x388:0x389;break;
    case GST_PIT_COMMAND:port=0x43;break;
    case GST_PIT_COUNTER:port=0x40;break;
    case GST_MASK_WRITE:port=0x21;break;
    case GST_MASK_READ:kind=LOG_IN;port=0x21;break;
    case GST_IRQ:kind=LOG_IRQ;port=e.a;size=0;break;
    case GST_FILE:kind=LOG_DOS;port=0x21;size=0;value=e.a<<8;break;
    case GST_SEED:kind=LOG_DOS;port=0x21;size=0;value=0x2c00;break;
    case GST_VIDEO_MODE:kind=LOG_DOS;port=0x10;size=0;value=e.a?0xf00:0;break;
    case GST_TERMINAL:kind=LOG_DOS;port=0x21;size=0;value=0x4c00;break;
    default:return;
    }
    if(effect_count==131072)fail("effect overflow");effects[effect_count++]=(IoEvent){kind,port,size,value};
}
static void check_effects(unsigned start){
    unsigned n=0;
    for(unsigned i=start;i<ugh_devices.count;i++){
        IoEvent e=ugh_devices.log[i];
        if(e.kind==LOG_DOS)e.value&=0xff00;
        unsigned bytes=e.size==2?2:1;
        for(unsigned j=0;j<bytes;j++){
            IoEvent part=e;
            if(e.size==2){part.size=1;part.port+=j;part.value=(e.value>>(8*j))&255;}
            if(n>=effect_count||memcmp(&part,&effects[n],sizeof part))fail("ordered effect");n++;
        }
    }
    EQUAL(n,effect_count);effect_count=0;
}
void s7_effects(unsigned start){check_effects(start);}
static InputScript *get_script(uint16_t port){for(unsigned i=0;i<ugh_devices.script_count;i++)if(ugh_devices.scripts[i].port==port)return &ugh_devices.scripts[i];return NULL;}
static void sync_stream(uint16_t port,GSTestStream *dest){
    InputScript *s=get_script(port);if(!s)return;
    unsigned i=(unsigned)(s-ugh_devices.scripts);
    if(!previous_valid[i]||memcmp(s,&previous[i],sizeof *s)){
        GSTestRun runs[128];for(unsigned j=0;j<s->count;j++)runs[j]=(GSTestRun){s->runs[j].value,s->runs[j].repeat};
        EQUAL(gs_test_stream(dest,runs,s->count,s->cycles),GS_OK);
        dest->cursor=s->cursor;dest->used=s->used;dest->left=s->cycles_left;
    }
}
static void check_stream(uint16_t port,GSTestStream *dest){
    InputScript *s=get_script(port);if(!s)return;
    EQUAL(s->cursor,dest->cursor);EQUAL(s->used,dest->used);EQUAL(s->cycles_left,dest->left);
    unsigned i=(unsigned)(s-ugh_devices.scripts);previous[i]=*s;previous_valid[i]=1;
}
static uint32_t stimulus(uint16_t port){InputScript *s=get_script(port);if(!s||s->cursor>=s->count)fail("missing external stimulus");return s->runs[s->cursor].value;}
static void controls(void){
    GSTestBackend *b=&s7_backend;Devices *d=&ugh_devices;
    SAME(b->latches,d->latch);SAME(b->seq,d->seq);SAME(b->gc,d->gc);SAME(b->crtc,d->crtc);SAME(b->attribute,d->attr);
    EQUAL(b->seq_index,d->seq_index);EQUAL(b->gc_index,d->gc_index);EQUAL(b->crtc_index,d->crtc_index);
    EQUAL(b->attribute_index,d->attr_index);EQUAL(b->attribute_phase,d->attr_phase);
    EQUAL(b->map_mask,d->map_mask);EQUAL(b->read_plane,d->read_map);
    EQUAL(b->dac_index,d->dac_index);EQUAL(b->dac_component,d->dac_component);
    EQUAL(b->opl_index,d->opl_index);EQUAL(b->pic_mask,d->pic_mask);
    EQUAL(b->pit_command,d->pit_command);EQUAL(b->pit_phase,d->pit_phase);EQUAL(b->pit_divisor,d->pit_divisor);
    EQUAL(b->clocks,d->clocks);
}
void s7_check(void){
    if(!active)return;GSTestBackend *b=&s7_backend;Devices *d=&ugh_devices;
    controls();SAME(b->planes,d->plane);SAME(b->dac,d->dac);SAME(b->opl,d->opl);
    EQUAL(b->video_mode,d->video_mode);EQUAL(b->video_columns,d->video_columns);EQUAL(b->video_page,d->video_page);
    EQUAL(b->exited,d->exited);EQUAL(b->exit_code,d->exit_code);
    EQUAL(b->exists,d->files[0].exists);EQUAL(b->length,d->files[0].length);SAME(b->scores,d->files[0].data);
    EQUAL(b->file_error,d->dos_error);EQUAL(b->file_error_skip,d->dos_error_skip);
    for(unsigned i=0;i<32;i++){EQUAL(b->handles[i].active,d->handles[i].active);EQUAL(b->handles[i].position,d->handles[i].position);EQUAL(b->handles[i].mode,d->handles[i].mode);}
    boundaries++;
}
void s7_begin(void){
    GSTestBackend *b=&s7_backend;Devices *d=&ugh_devices;gs_test_init(b);s7_services=gs_test_services(b);
    memset(requests,0,sizeof requests);memset(previous_valid,0,sizeof previous_valid);boundaries=effect_count=0;
    memcpy(b->planes,d->plane,sizeof b->planes);memcpy(b->latches,d->latch,4);
    memcpy(b->seq,d->seq,5);memcpy(b->gc,d->gc,9);memcpy(b->crtc,d->crtc,25);memcpy(b->attribute,d->attr,21);
    b->seq_index=d->seq_index;b->gc_index=d->gc_index;b->crtc_index=d->crtc_index;b->attribute_index=d->attr_index;b->attribute_phase=d->attr_phase;b->map_mask=d->map_mask;b->read_plane=d->read_map;
    memcpy(b->dac,d->dac,768);b->dac_index=d->dac_index;b->dac_component=d->dac_component;
    memcpy(b->opl,d->opl,256);b->opl_index=d->opl_index;b->pic_mask=d->pic_mask;b->pit_command=d->pit_command;b->pit_divisor=d->pit_divisor;b->pit_phase=d->pit_phase;b->clocks=d->clocks;
    memcpy(b->scores,d->files[0].data,8192);b->exists=(uint8_t)d->files[0].exists;b->length=d->files[0].length;b->io_limit=d->io_limit;b->file_error=d->dos_error;b->file_error_skip=d->dos_error_skip;
    for(unsigned i=0;i<32;i++){b->handles[i].active=d->handles[i].active;b->handles[i].position=d->handles[i].position;b->handles[i].mode=d->handles[i].mode;}
    b->video_mode=d->video_mode;b->video_columns=d->video_columns;b->video_page=d->video_page;b->exited=d->exited;b->exit_code=d->exit_code;
    InputScript *s=get_script(0xfffe);if(s&&s->count){uint32_t v=s->runs[0].value;b->seed=(GSSeedReply){(uint8_t)(v>>24),(uint8_t)(v>>16),(uint8_t)(v>>8),(uint8_t)v};}
    saved_keyboard[0]=rd16(DATA_SEG,D(PreviousKeyboardVector));saved_keyboard[1]=rd16(DATA_SEG,D(PreviousKeyboardVectorSegment));
    b->keyboard.token=rd16(0,36)==G(HandleKeyboardScanInterrupt)&&rd16(0,38)==GAME_SEG?2:1;
    b->recorder=record;active=1;s7_check();
}
void s7_finish(void){
    s7_check();fprintf(stderr,"S7 STREAM requests=%llu reads=%llu stores=%llu outputs=%llu inputs=%llu files=%llu queues=%llu vectors=%llu seed=%llu lifecycle=%llu irq=%llu cuts=%llu pending_status=%llu pending_vectors=%llu flushes=%llu boundaries=%llu\n",(unsigned long long)requests[0],(unsigned long long)requests[1],(unsigned long long)requests[2],(unsigned long long)requests[3],(unsigned long long)requests[4],(unsigned long long)requests[5],(unsigned long long)requests[6],(unsigned long long)requests[7],(unsigned long long)requests[8],(unsigned long long)requests[9],(unsigned long long)requests[10],(unsigned long long)requests[11],(unsigned long long)requests[12],(unsigned long long)requests[13],(unsigned long long)requests[14],(unsigned long long)boundaries);active=0;
}
uint8_t ugh_read(uint32_t address){
    uint8_t got=s7_model_read(address);if(!active||address<0xa0000||address>=0xb0000)return got;
    requests[0]++;requests[1]++;uint8_t value=0;EQUAL(s7_services.video.read(&s7_backend,(uint16_t)address,GS_SOURCE_READ,&value),GS_OK);EQUAL(value,got);SAME(s7_backend.latches,ugh_devices.latch);return got;
}
void ugh_write(uint32_t address,uint8_t value){
    s7_model_write(address,value);if(!active||address<0xa0000||address>=0xb0000)return;
    requests[0]++;requests[2]++;EQUAL(s7_services.video.store(&s7_backend,(uint16_t)address,value),GS_OK);
    for(unsigned p=0;p<4;p++)EQUAL(s7_backend.planes[p][(uint16_t)address],ugh_devices.plane[p][(uint16_t)address]);SAME(s7_backend.latches,ugh_devices.latch);
}
void platform_out(uint16_t port,unsigned size,uint32_t value){
    if(!active){s7_model_out(port,size,value);return;}
    unsigned begin=ugh_devices.count;requests[0]++;requests[3]++;int served=1;
    for(unsigned i=0;i<size;i++){
        uint16_t p=(uint16_t)(port+i);uint8_t v=(uint8_t)(value>>(8*i));int r=route(p);GSStatus s=GS_OK;
        if(r>=0&&r!=7&&r!=8)s=s7_services.video.control_write(&s7_backend,(GSVideoRoute)r,v);
        else switch(p){
        case 0x3c8:case 0x3c9:s=s7_services.video.dac(&s7_backend,(GSDacWrite){p==0x3c8?GS_DAC_SELECT:GS_DAC_COMPONENT,v});break;
        case 0x388:case 0x389:s=s7_services.audio.stream(&s7_backend,p==0x388?GS_OPL_SELECT:GS_OPL_DATA,v);break;
        case 0x20:s=s7_services.time.acknowledge(&s7_backend);break;
        case 0x21:s=s7_services.time.interrupt_mask(&s7_backend,v);break;
        case 0x43:s=s7_services.time.pit_command(&s7_backend,v);break;
        case 0x40:s=s7_services.time.pit_counter(&s7_backend,v);break;
        case 0x201:sync_stream(p,&s7_backend.joystick);s=s7_services.input.joystick_start(&s7_backend,v);break;
        default:served=0;break;
        }if(s!=GS_OK&&s!=GS_UNSUPPORTED)fail("output status");
    }
    s7_model_out(port,size,value);if(served)check_effects(begin);else {effect_count=0;fail("unserved output");}
    if(port==0x201)check_stream(port,&s7_backend.joystick);controls();
}
uint32_t platform_in(uint16_t port,unsigned size){
    if(!active)return s7_model_in(port,size);
    unsigned begin=ugh_devices.count;requests[0]++;requests[4]++;uint8_t v=0;GSStatus s=GS_OK;int r=route(port),served=1;
    if(r>=0&&r!=8)s=s7_services.video.control_read(&s7_backend,(GSVideoRoute)r,&v);
    else switch(port){
    case 0x3da:s7_backend.retrace=(uint8_t)stimulus(port);s=s7_services.video.retrace_level(&s7_backend,&v);break;
    case 0x60:sync_stream(port,&s7_backend.scans);s=s7_services.input.scan(&s7_backend,&v);break;
    case 0x201:sync_stream(port,&s7_backend.joystick);s=s7_services.input.sample(&s7_backend,&v);break;
    case 0x21:s=s7_services.time.read_interrupt_mask(&s7_backend,&v);break;
    case 0x388: /* pending capability prefix: explicitly excluded, never success */
        requests[12]++;EQUAL(s7_services.audio.status(&s7_backend,&v),GS_UNSUPPORTED);served=0;break;
    default:fail("unserved input");
    }
    uint32_t got=s7_model_in(port,size);if(served){EQUAL(s,GS_OK);EQUAL(v,got);check_effects(begin);}else effect_count=0;
    if(port==0x60)check_stream(port,&s7_backend.scans);if(port==0x201)check_stream(port,&s7_backend.joystick);controls();return got;
}
int platform_interrupt(uint8_t number,Regs *r){
    if(!active)return s7_model_interrupt(number,r);
    uint8_t ah=(uint8_t)(r->ax>>8),al=(uint8_t)r->ax;unsigned begin=ugh_devices.count;GSStatus status=GS_OK;
    uint8_t buffer[65536];uint16_t count=r->cx,word=0;GSFileReply file={0};GSBinding token={0};GSVideoModeReply mode={0};GSSeedReply seed={0};int served=1,empty=0;
    if(number==0x21&&ah>=0x3c&&ah<=0x40){
        requests[5]++;
        for(unsigned i=0;i<count;i++)buffer[i]=rd8(r->ds,(uint16_t)(r->dx+i));
        if(ah==0x3c||ah==0x3d)status=s7_services.files.open_scores(&s7_backend,ah==0x3c,&file);
        else if(ah==0x3e)status=s7_services.files.close(&s7_backend,r->bx,&file);
        else if(ah==0x3f)status=s7_services.files.read(&s7_backend,r->bx,buffer,count,&file);
        else status=s7_services.files.write(&s7_backend,r->bx,buffer,count,&file);
    }else if(number==0x16&&(ah==0||ah==1)){
        requests[6]++;sync_stream(0xffff,&s7_backend.bios);status=s7_services.input.queue(&s7_backend,ah?GS_QUEUE_PEEK:GS_QUEUE_TAKE,&word);empty=status==GS_EMPTY;
    }else if(number==0x21&&(ah==0x25||ah==0x35)&&al==9){
        requests[7]++;GSBinding binding={0};
        if(ah==0x25){if(r->dx==saved_keyboard[0]&&r->ds==saved_keyboard[1])binding.token=1;else if(r->dx==G(HandleKeyboardScanInterrupt)&&r->ds==GAME_SEG)binding.token=2;else {fprintf(stderr,"keyboard requested %04x:%04x saved %04x:%04x handler %04x:%04x\n",r->ds,r->dx,saved_keyboard[1],saved_keyboard[0],GAME_SEG,G(HandleKeyboardScanInterrupt));fail("keyboard token");}}
        status=s7_services.input.vector(&s7_backend,ah==0x35?GS_VECTOR_CAPTURE:binding.token==1?GS_VECTOR_RESTORE:GS_VECTOR_INSTALL,binding,&token);
    }else if(number==0x21&&ah==0x2c){requests[8]++;status=s7_services.seed.read(&s7_backend,&seed);}
    else if(number==0x10&&ah==15){requests[9]++;status=s7_services.lifecycle.video_query(&s7_backend,&mode);}
    else if(number==0x10&&ah==0){requests[9]++;status=s7_services.lifecycle.video_set(&s7_backend,al);}
    else if(number==0x21&&ah==0x4c){requests[9]++;status=s7_services.lifecycle.terminate(&s7_backend,al);}
    else if(number==0x21&&(ah==0x25||ah==0x35)){
        requests[13]++;served=0;
        if(al==0x24)EQUAL(s7_services.lifecycle.binding(&s7_backend,GS_BIND_CRITICAL_ERROR_FAIL,GS_VECTOR_CAPTURE,(GSBinding){0},&token),GS_UNSUPPORTED);
        else EQUAL(s7_services.audio.timer_lifetime(&s7_backend,(GSTimerLifetimeRequest){0},&token),GS_UNSUPPORTED);
    }else fail("unmapped interrupt");
    requests[0]++;int result=s7_model_interrupt(number,r);
    if(served){
        if(!empty)EQUAL(status,GS_OK);EQUAL(result,UGH_OK);check_effects(begin);
        if(number==0x21&&ah>=0x3c&&ah<=0x40){EQUAL(r->ax,file.value);EQUAL(!!(r->flags&CF),file.failed);if(ah==0x3f)for(unsigned i=0;i<count;i++)EQUAL(rd8(r->ds,(uint16_t)(r->dx+i)),buffer[i]);}
        else if(number==0x16){if(ah==1)EQUAL(!!(r->flags&ZF),empty);if(!empty)EQUAL(r->ax,word);check_stream(0xffff,&s7_backend.bios);}
        else if(number==0x21&&ah==0x2c){EQUAL(r->cx,(uint16_t)(seed.hours*256u+seed.minutes));EQUAL(r->dx,(uint16_t)(seed.seconds*256u+seed.hundredths));}
        else if(number==0x21&&(ah==0x25||ah==0x35)){
            uint16_t off=token.token==1?saved_keyboard[0]:G(HandleKeyboardScanInterrupt),seg=token.token==1?saved_keyboard[1]:GAME_SEG;
            EQUAL(rd16(0,36),off);EQUAL(rd16(0,38),seg);if(ah==0x35){EQUAL(r->bx,off);EQUAL(r->es,seg);}
        }else if(number==0x10&&ah==15){EQUAL(r->ax,(uint16_t)(mode.mode+256u*mode.columns));EQUAL(r->bx>>8,mode.page);}
    }else effect_count=0;
    controls();return result;
}
void s7_irq(unsigned irq,uint32_t clocks,int enabled){
    if(!active)return;requests[0]++;requests[10]++;unsigned begin=ugh_devices.count-1;
    EQUAL(s7_services.time.interrupt(&s7_backend,irq,clocks,enabled),GS_OK);check_effects(begin);EQUAL(s7_backend.clocks,ugh_devices.clocks);
}
void s7_cut(unsigned kind){if(!active)return;requests[0]++;requests[11]++;GSEvent e;EQUAL(s7_services.time.deliver(&s7_backend,(GSEventKind)kind,&e),GS_OK);}
void s7_flush(uint16_t tail){
    if(!active)return;requests[0]++;requests[14]++;s7_backend.flush_reply=tail;
    uint16_t got=0;EQUAL(s7_services.input.flush(&s7_backend,&got),GS_OK);EQUAL(got,tail);
}
