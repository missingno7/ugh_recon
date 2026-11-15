#include "backend.h"
#include <string.h>

static void effect(GSTestBackend *b,GSTestEffectKind kind,uint32_t a,uint32_t v,uint32_t c){
    if(b->recorder)b->recorder(b->record_context,(GSTestEffect){kind,a,v,c});
}
void gs_test_init(GSTestBackend *b){
    memset(b,0,sizeof *b);b->seq[2]=b->map_mask=15;b->gc[8]=255;
    b->keyboard.token=1;b->video_mode=3;b->video_columns=80;
    b->seed=(GSSeedReply){16,32,48,64};
    for(unsigned i=0;i<4;i++)b->axes[i]=1000;
}
GSStatus gs_test_stream(GSTestStream *s,const GSTestRun *runs,size_t n,uint32_t cycles){
    if(n>128||(!runs&&n))return GS_INVALID;
    for(size_t i=0;i<n;i++)if(!runs[i].repeat)return GS_INVALID;
    memset(s,0,sizeof *s);if(n)memcpy(s->runs,runs,n*sizeof *runs);
    s->count=(uint32_t)n;s->cycles=s->left=cycles;return GS_OK;
}
static GSStatus next(GSTestStream *s,uint32_t *value,int peek){
    if(!s->left||s->cursor>=s->count)return GS_EMPTY;
    *value=s->runs[s->cursor].value;
    if(!peek&&++s->used==s->runs[s->cursor].repeat){
        s->used=0;s->cursor++;
        if(s->cursor==s->count&&s->left>1){s->left--;s->cursor=0;}
    }return GS_OK;
}
static GSStatus control_write(void *ctx,GSVideoRoute route,uint8_t v){
    GSTestBackend *b=ctx;GSStatus status=GS_OK;
    switch(route){
    case GS_SEQ_INDEX:b->seq_index=v;break;
    case GS_SEQ_DATA:if(b->seq_index>=5)status=GS_UNSUPPORTED;else {b->seq[b->seq_index]=v;if(b->seq_index==2)b->map_mask=v&15;}break;
    case GS_GC_INDEX:b->gc_index=v;break;
    case GS_GC_DATA:if(b->gc_index>=9)status=GS_UNSUPPORTED;else {b->gc[b->gc_index]=v;if(b->gc_index==4)b->read_plane=v&3;}break;
    case GS_CRTC_INDEX:b->crtc_index=v;break;
    case GS_CRTC_DATA:if(b->crtc_index>=25)status=GS_UNSUPPORTED;else b->crtc[b->crtc_index]=v;break;
    case GS_ATTRIBUTE_WRITE:
        if(!b->attribute_phase)b->attribute_index=v&31;
        else if(b->attribute_index<21)b->attribute[b->attribute_index]=v;
        else status=GS_UNSUPPORTED;
        b->attribute_phase^=1;break;
    default:return GS_UNSUPPORTED;
    }effect(b,GST_CONTROL_WRITE,route,v,0);return status;
}
static GSStatus control_read(void *ctx,GSVideoRoute route,uint8_t *v){
    GSTestBackend *b=ctx;if(!v)return GS_INVALID;GSStatus status=GS_OK;*v=0;
    switch(route){
    case GS_SEQ_DATA:if(b->seq_index>=5)status=GS_UNSUPPORTED;else *v=b->seq[b->seq_index];break;
    case GS_GC_DATA:if(b->gc_index>=9)status=GS_UNSUPPORTED;else *v=b->gc[b->gc_index];break;
    case GS_CRTC_DATA:if(b->crtc_index>=25)status=GS_UNSUPPORTED;else *v=b->crtc[b->crtc_index];break;
    case GS_ATTRIBUTE_READ:if(b->attribute_index>=21)status=GS_UNSUPPORTED;else *v=b->attribute[b->attribute_index];break;
    default:return GS_UNSUPPORTED;
    }effect(b,GST_CONTROL_READ,route,*v,0);return status;
}
static GSStatus read_cell(void *ctx,uint16_t cell,GSReadRole role,uint8_t *value){
    GSTestBackend *b=ctx;if(!value||(unsigned)role>GS_COLLISION_READ)return GS_INVALID;
    for(unsigned p=0;p<4;p++)b->latches[p]=b->planes[p][cell];
    uint8_t v=b->latches[b->read_plane&3];
    if(b->gc[5]&8){v=255;for(unsigned p=0;p<4;p++)if(b->gc[7]&(1u<<p))v&=b->latches[p]^(b->gc[2]&(1u<<p)?0:255);}
    *value=v;return GS_OK;
}
static GSStatus store(void *ctx,uint16_t cell,uint8_t v){
    GSTestBackend *b=ctx;unsigned mode=b->gc[5]&3,rotate=b->gc[3]&7,op=(b->gc[3]>>3)&3;
    uint8_t rotated=(uint8_t)((v>>rotate)|(v<<(8-rotate)));
    for(unsigned p=0;p<4;p++)if(b->map_mask&(1u<<p)){
        uint8_t latch=b->latches[p],mask=b->gc[8],source,result;
        if(mode==1)result=latch;
        else {
            if(mode==0)source=b->gc[1]&(1u<<p)?(b->gc[0]&(1u<<p)?255:0):rotated;
            else if(mode==2)source=v&(1u<<p)?255:0;
            else {source=b->gc[0]&(1u<<p)?255:0;mask&=rotated;}
            if(op==1)source&=latch;else if(op==2)source|=latch;else if(op==3)source^=latch;
            result=(uint8_t)((source&mask)|(latch&~mask));
        }b->planes[p][cell]=result;
    }return GS_OK;
}
static GSStatus word(void *ctx,uint16_t cell,uint16_t v){
    GSStatus s=store(ctx,cell,(uint8_t)v);if(s!=GS_OK)return s;
    if(cell==UINT16_MAX)return GS_UNSUPPORTED; /* consumed low-byte prefix */
    return store(ctx,(uint16_t)(cell+1),(uint8_t)(v>>8));
}
static GSStatus copy(void *ctx,uint16_t src,uint16_t dst,uint8_t *v){
    GSStatus s=read_cell(ctx,src,GS_SOURCE_READ,v);return s==GS_OK?store(ctx,dst,*v):s;
}
static GSStatus water(void *ctx,uint16_t cell,uint8_t *v){
    GSStatus s=read_cell(ctx,cell,GS_SOURCE_READ,v);return s==GS_OK?store(ctx,cell,0x40):s;
}
static GSStatus dac(void *ctx,GSDacWrite w){
    GSTestBackend *b=ctx;
    if(w.kind==GS_DAC_SELECT){b->dac_index=w.value;b->dac_component=0;}
    else if(w.kind==GS_DAC_COMPONENT){
        b->dac[3*b->dac_index+b->dac_component]=w.value&63;
        if(++b->dac_component==3){b->dac_component=0;b->dac_index++;}
    }else return GS_INVALID;
    effect(b,GST_DAC,w.kind,w.value,0);return GS_OK;
}
static GSStatus retrace(void *ctx,uint8_t *v){
    GSTestBackend *b=ctx;if(!v)return GS_INVALID;b->attribute_phase=0;*v=b->retrace;
    effect(b,GST_CONTROL_READ,8,*v,0);return GS_OK;
}
static GSStatus present(void *ctx){GSTestBackend *b=ctx;b->presents++;effect(b,GST_PRESENT,0,0,0);return GS_OK;}
static GSStatus unsupported(void *ctx){(void)ctx;return GS_UNSUPPORTED;}
static GSStatus scan(void *ctx,uint8_t *v){
    GSTestBackend *b=ctx;if(!v)return GS_INVALID;uint32_t n;GSStatus s=next(&b->scans,&n,0);
    if(s==GS_OK){*v=(uint8_t)n;effect(b,GST_SCAN,0,*v,0);}return s;
}
static GSStatus acknowledge(void *ctx){effect(ctx,GST_ACK,0,0x20,0);return GS_OK;}
static GSStatus queue(void *ctx,GSQueueOp op,uint16_t *v){
    GSTestBackend *b=ctx;if(!v||(unsigned)op>GS_QUEUE_TAKE)return GS_INVALID;
    uint32_t n;GSStatus s=next(&b->bios,&n,op==GS_QUEUE_PEEK);
    if(s==GS_OK)*v=(uint16_t)n;
    effect(b,GST_QUEUE,op,s==GS_OK?*v:0,s);return s;
}
static GSStatus flush(void *ctx,uint16_t *v){
    GSTestBackend *b=ctx;if(!v)return GS_INVALID;
    *v=b->flush_reply;effect(b,GST_FLUSH,0,*v,0);return GS_OK;
}
static GSStatus vector(void *ctx,GSVectorOp op,GSBinding binding,GSBinding *reply){
    GSTestBackend *b=ctx;if(!reply||(unsigned)op>GS_VECTOR_RESTORE)return GS_INVALID;
    if(op!=GS_VECTOR_CAPTURE){
        if(binding.token!=1&&binding.token!=2)return GS_UNSUPPORTED;
        b->keyboard=binding;
    }*reply=b->keyboard;effect(b,GST_VECTOR,op,(uint32_t)reply->token,0);return GS_OK;
}
uint16_t gs_test_axis_count(int16_t axis){return (uint16_t)(1000+(int32_t)axis*750/(axis<0?32768:32767));}
GSStatus gs_test_gamepad(GSTestBackend *b,unsigned stick,int present,int16_t x,int16_t y,uint8_t buttons){
    if(stick>=2)return GS_INVALID;
    b->present[stick]=(uint8_t)!!present;b->buttons[stick]=present?(buttons&3):0;
    b->axes[2*stick]=gs_test_axis_count(x);b->axes[2*stick+1]=gs_test_axis_count(y);return GS_OK;
}
static GSStatus start(void *ctx,uint8_t trigger){
    GSTestBackend *b=ctx;b->joystick.cursor=b->joystick.used=0;b->joystick.left=b->joystick.cycles;
    effect(b,GST_JOYSTICK_START,0,trigger,0);return GS_OK;
}
static GSStatus sample(void *ctx,uint8_t *v){
    GSTestBackend *b=ctx;if(!v)return GS_INVALID;uint32_t n;GSStatus s=next(&b->joystick,&n,0);
    if(s==GS_OK){*v=(uint8_t)n;effect(b,GST_JOYSTICK_SAMPLE,0,*v,0);}return s;
}
static GSStatus presence(void *ctx,uint8_t *v){
    GSTestBackend *b=ctx;if(!v)return GS_INVALID;
    if(b->joystick.count)return sample(ctx,v);
    *v=(uint8_t)((0xf0^(b->buttons[0]<<4)^(b->buttons[1]<<6))|(b->present[0]?0:3)|(b->present[1]?0:12));return GS_OK;
}
static GSStatus buttons(void *ctx,unsigned stick,uint16_t *v){
    GSTestBackend *b=ctx;if(!v||stick>=2)return GS_INVALID;
    if(b->joystick.count){uint8_t n;GSStatus s=sample(ctx,&n);if(s!=GS_OK)return s;*v=(uint16_t)((uint8_t)~n&(stick?192:48));}
    else *v=(uint16_t)(b->buttons[stick]<<(stick?6:4));
    return GS_OK;
}
static GSStatus counts(void *ctx,uint16_t limit,uint8_t enabled,GSJoystickCounts *r){
    GSTestBackend *b=ctx;if(!r)return GS_INVALID;if(enabled&240)return GS_UNSUPPORTED;
    GSStatus status=GS_OK;
    memset(r,0,sizeof *r);r->remaining=limit;
    if(b->joystick.count){
        uint8_t completed=(uint8_t)~enabled;
        if(enabled)for(unsigned budget=1000000;;){
            uint8_t n;GSStatus s=sample(ctx,&n);if(s!=GS_OK){status=GS_UNSUPPORTED;break;}
            uint8_t ended=(uint8_t)~(n|completed);
            if(ended){unsigned a=ended&1?0:ended&2?1:ended&4?2:3;r->latched[a]=r->remaining;completed|=(uint8_t)(1u<<a);if(completed==255)break;}
            else if(!--r->remaining)break;
            if(!--budget){status=GS_OVERFLOW;break;}
        }
    }else {
        unsigned cycles=limit?limit:65536u,latest=0;int incomplete=0;
        for(unsigned a=0;a<4;a++)if(enabled&(1u<<a)){
            unsigned n=b->present[a/2]?b->axes[a]:cycles;
            if(n>=cycles)incomplete=1;
            else {r->latched[a]=(uint16_t)(limit-n);if(n>latest)latest=n;}
        }
        if(enabled)r->remaining=(uint16_t)(incomplete?0:limit-latest);
    }
    for(unsigned a=0;a<4;a++)r->counts[a]=(uint16_t)(limit-r->latched[a]);
    return status;
}
static GSStatus pump(void *ctx,GSInputPollCut cut){(void)ctx;return (unsigned)cut<=GS_INPUT_WAIT?GS_OK:GS_UNSUPPORTED;}
static GSStatus opl_stream(void *ctx,GSOplKind kind,uint8_t v){
    GSTestBackend *b=ctx;if(kind==GS_OPL_SELECT)b->opl_index=v;else if(kind==GS_OPL_DATA)b->opl[b->opl_index]=v;else return GS_INVALID;
    effect(b,GST_OPL,kind,v,0);return GS_OK;
}
static GSStatus opl(void *ctx,GSRegisterWrite w){opl_stream(ctx,GS_OPL_SELECT,w.reg);return opl_stream(ctx,GS_OPL_DATA,w.value);}
static GSStatus audio_status(void *ctx,uint8_t *v){(void)ctx;(void)v;return GS_UNSUPPORTED;}
static GSStatus advance(void *ctx,uint64_t ns){GSTestBackend *b=ctx;if(UINT64_MAX-b->audio_ns<ns)return GS_OVERFLOW;b->audio_ns+=ns;return GS_OK;}
static GSStatus clock_delivery(void *ctx,GSClockDelivery k){(void)ctx;(void)k;return GS_UNSUPPORTED;}
static GSStatus calibration(void *ctx,GSCalibrationPhase p,GSCalibrationReply *r){(void)ctx;(void)p;(void)r;return GS_UNSUPPORTED;}
static GSStatus lifetime(void *ctx,GSTimerLifetimeRequest q,GSBinding *r){(void)ctx;(void)q;(void)r;return GS_UNSUPPORTED;}
uint64_t gs_test_tick_ns(uint64_t tick){return tick/70*1000000000ull+tick%70*1000000000ull/70;}
static GSStatus deliver(void *ctx,GSEventKind kind,GSEvent *e){
    GSTestBackend *b=ctx;if(!e||(unsigned)kind>GS_INPUT_OPPORTUNITY)return GS_INVALID;if(b->suspended)return GS_EMPTY;
    if(kind==GS_RETRACE_ACTIVE){b->retrace_tick++;b->retrace=8;}
    if(kind==GS_RETRACE_INACTIVE)b->retrace=0;
    if(kind==GS_TIMER_OPPORTUNITY)b->timer_tick++;
    uint64_t t=b->timer_tick>b->retrace_tick?b->timer_tick:b->retrace_tick;
    *e=(GSEvent){kind,t,gs_test_tick_ns(t)};effect(b,GST_EVENT,kind,(uint32_t)t,(uint32_t)(t>>32));return GS_OK;
}
static GSStatus suspend_time(void *ctx,int value){GSTestBackend *b=ctx;b->suspended=!!value;return GS_OK;}
static GSStatus pace(void *ctx){(void)ctx;return GS_OK;}
static GSStatus pit_command(void *ctx,uint8_t v){GSTestBackend *b=ctx;effect(b,GST_PIT_COMMAND,0,v,0);if(v!=0x36)return GS_UNSUPPORTED;b->pit_command=v;b->pit_phase=0;return GS_OK;}
static GSStatus pit_counter(void *ctx,uint8_t v){GSTestBackend *b=ctx;
    b->pit_divisor=b->pit_phase?(uint16_t)((b->pit_divisor&255)|((uint16_t)v<<8)):(uint16_t)((b->pit_divisor&0xff00)|v);
    b->pit_phase^=1;effect(b,GST_PIT_COUNTER,0,v,0);return GS_OK;
}
static GSStatus mask_write(void *ctx,uint8_t v){GSTestBackend *b=ctx;b->pic_mask=v;effect(b,GST_MASK_WRITE,0,v,0);return GS_OK;}
static GSStatus mask_read(void *ctx,uint8_t *v){GSTestBackend *b=ctx;if(!v)return GS_INVALID;*v=b->pic_mask;effect(b,GST_MASK_READ,0,*v,0);return GS_OK;}
static GSStatus interrupt(void *ctx,unsigned irq,uint32_t clocks,int enabled){
    GSTestBackend *b=ctx;if(irq>=8)return GS_INVALID;if(!enabled||(b->pic_mask&(1u<<irq)))return GS_EMPTY;
    b->clocks+=clocks;effect(b,GST_IRQ,irq,clocks,0);return GS_OK;
}
static int file_error(GSTestBackend *b,GSFileReply *r){
    if(!b->file_error)return 0;
    if(b->file_error_skip){b->file_error_skip--;return 0;}
    *r=(GSFileReply){(uint16_t)b->file_error,1};b->file_error=0;return 1;
}
static GSStatus open_scores(void *ctx,int create,GSFileReply *r){
    GSTestBackend *b=ctx;if(!r)return GS_INVALID;effect(b,GST_FILE,create?0x3c:0x3d,0,0);if(file_error(b,r))return GS_OK;
    if(!create&&!b->exists){*r=(GSFileReply){2,1};return GS_OK;}
    for(unsigned i=5;i<32;i++)if(!b->handles[i].active){
        b->handles[i].active=1;b->handles[i].position=0;b->handles[i].mode=create?2:0;
        if(create){b->exists=1;b->length=0;b->dirty=1;}*r=(GSFileReply){(uint16_t)i,0};return GS_OK;
    }*r=(GSFileReply){4,1};return GS_OK;
}
static int valid(GSTestBackend *b,uint16_t h){return h<32&&b->handles[h].active;}
static GSStatus read_scores(void *ctx,uint16_t h,uint8_t *data,uint16_t count,GSFileReply *r){
    GSTestBackend *b=ctx;if(!r||(!data&&count))return GS_INVALID;effect(b,GST_FILE,0x3f,h,count);if(file_error(b,r))return GS_OK;
    if(!valid(b,h)){*r=(GSFileReply){6,1};return GS_OK;}
    if(b->handles[h].mode==1){*r=(GSFileReply){5,1};return GS_OK;}
    unsigned pos=b->handles[h].position,n=count;if(b->io_limit&&n>b->io_limit)n=b->io_limit;
    unsigned available=b->length>pos?b->length-pos:0;if(n>available)n=available;
    if(n)memcpy(data,b->scores+pos,n);
    b->handles[h].position+=n;*r=(GSFileReply){(uint16_t)n,0};return GS_OK;
}
static GSStatus write_scores(void *ctx,uint16_t h,const uint8_t *data,uint16_t count,GSFileReply *r){
    GSTestBackend *b=ctx;if(!r||(!data&&count))return GS_INVALID;effect(b,GST_FILE,0x40,h,count);if(file_error(b,r))return GS_OK;
    if(!valid(b,h)){*r=(GSFileReply){6,1};return GS_OK;}
    if(!b->handles[h].mode){*r=(GSFileReply){5,1};return GS_OK;}
    unsigned pos=b->handles[h].position,n=count;if(b->io_limit&&n>b->io_limit)n=b->io_limit;
    if(n>sizeof b->scores-pos)n=(unsigned)sizeof b->scores-pos;
    if(n)memcpy(b->scores+pos,data,n);
    if(!count||pos+n>b->length)b->length=pos+n;
    b->handles[h].position+=n;b->dirty=1;*r=(GSFileReply){(uint16_t)n,0};return GS_OK;
}
static GSStatus close_scores(void *ctx,uint16_t h,GSFileReply *r){
    GSTestBackend *b=ctx;if(!r)return GS_INVALID;effect(b,GST_FILE,0x3e,h,0);if(file_error(b,r))return GS_OK;
    if(!valid(b,h)){*r=(GSFileReply){6,1};return GS_OK;}
    b->handles[h].active=0;*r=(GSFileReply){0,0};return GS_OK;
}
static GSStatus persist(void *ctx){GSTestBackend *b=ctx;b->dirty=0;return GS_OK;}
static GSStatus resource(void *ctx,GSResourceId id,GSBytes *v,GSResourceClass *c){GSTestBackend *b=ctx;return b->resources.view?b->resources.view(b->resource_context,id,v,c):GS_UNSUPPORTED;}
static GSStatus mutable_resource(void *ctx,GSResourceId id,GSMutableBytes *v){GSTestBackend *b=ctx;return b->resources.mutable_view?b->resources.mutable_view(b->resource_context,id,v):GS_UNSUPPORTED;}
static GSStatus seed(void *ctx,GSSeedReply *r){GSTestBackend *b=ctx;if(!r)return GS_INVALID;*r=b->seed;effect(b,GST_SEED,0,0,0);return GS_OK;}
static GSStatus lifecycle(void *ctx,GSLifecycleRequest q,uint8_t *r){(void)ctx;(void)q;(void)r;return GS_UNSUPPORTED;}
static GSStatus binding(void *ctx,GSLifecycleBindingRole role,GSVectorOp op,GSBinding value,GSBinding *r){(void)ctx;(void)role;(void)op;(void)value;(void)r;return GS_UNSUPPORTED;}
static GSStatus query_mode(void *ctx,GSVideoModeReply *r){GSTestBackend *b=ctx;if(!r)return GS_INVALID;*r=(GSVideoModeReply){b->video_mode,b->video_columns,b->video_page};effect(b,GST_VIDEO_MODE,1,0,0);return GS_OK;}
static GSStatus set_mode(void *ctx,uint8_t mode){GSTestBackend *b=ctx;b->video_mode=mode;b->video_page=0;effect(b,GST_VIDEO_MODE,0,mode,0);return GS_OK;}
static GSStatus terminate(void *ctx,uint8_t code){GSTestBackend *b=ctx;b->exited=1;b->exit_code=code;effect(b,GST_TERMINAL,0,code,0);return GS_OK;}
GameServices gs_test_services(GSTestBackend *b){
    GameServices s={0};s.video_context=s.input_context=s.audio_context=s.time_context=b;
    s.files_context=s.resources_context=s.seed_context=s.lifecycle_context=b;
    s.video=(GSVideoOps){control_write,control_read,read_cell,store,word,copy,water,dac,retrace,present,unsupported};
    s.input=(GSInputOps){scan,acknowledge,queue,flush,vector,start,presence,buttons,counts,pump,sample};
    s.audio=(GSAudioOps){opl,audio_status,advance,clock_delivery,calibration,lifetime,opl_stream};
    s.time=(GSTimeOps){deliver,suspend_time,pace,pit_command,pit_counter,mask_write,mask_read,acknowledge,interrupt};
    s.files=(GSFilesOps){open_scores,read_scores,write_scores,close_scores,persist};
    s.resources=(GSResourceOps){resource,mutable_resource};s.seed=(GSSeedOps){seed};
    s.lifecycle=(GSLifecycleOps){lifecycle,binding,query_mode,set_mode,terminate};return s;
}
