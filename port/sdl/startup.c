#include "backend.h"
#include <string.h>
static GSStatus request(void *ctx,GSLifecycleRequest q,uint8_t *reply){
    (void)ctx;if(!reply)return GS_INVALID;if(q.action!=GS_LIFECYCLE_CPU_QUERY)return GS_UNSUPPORTED;*reply=1;return GS_OK;
}
static GSStatus binding(void *ctx,GSLifecycleBindingRole role,GSVectorOp op,GSBinding value,GSBinding *reply){
    GSSdlStartup *p=ctx;if(!reply||role!=GS_BIND_CRITICAL_ERROR_FAIL)return GS_INVALID;
    if(op!=GS_VECTOR_INSTALL||value.token!=2)return GS_UNSUPPORTED;
    *reply=p->critical;p->critical=value;return GS_OK;
}
static GSStatus query(void *ctx,GSVideoModeReply *reply){GSSdlStartup *p=ctx;if(!reply)return GS_INVALID;*reply=p->mode;return GS_OK;}
static GSStatus mode(void *ctx,uint8_t value){GSSdlStartup *p=ctx;p->mode.mode=value;p->mode.page=0;return GS_OK;}
static GSStatus terminate(void *ctx,uint8_t value){GSSdlStartup *p=ctx;p->exited=1;p->exit_code=value;return GS_OK;}
static GSStatus status(void *ctx,uint8_t *reply){GSSdlStartup *p=ctx;if(!reply)return GS_INVALID;*reply=p->adlib?(p->probe_reads++?192:0):224;return GS_OK;}
static GSStatus calibration(void *ctx,GSCalibrationPhase phase,GSCalibrationReply *reply){
    (void)ctx;if(!reply||(unsigned)phase>GS_CALIBRATION_FINISH)return GS_INVALID;
    /* Deterministic virtual measurement in discharge-loop units. The engine
     * still executes the accepted measurement arithmetic. */
    *reply=(GSCalibrationReply){phase==GS_CALIBRATION_WAIT?1:0,1,phase==GS_CALIBRATION_BEGIN?256:1};return GS_OK;
}
static GSStatus lifetime(void *ctx,GSTimerLifetimeRequest q,GSBinding *reply){
    GSSdlStartup *p=ctx;if(!reply)return GS_INVALID;
    if(q.kind==GS_TIMER_READ_BINDING)*reply=p->timer;
    else if(q.kind==GS_TIMER_BIND_HANDLER){*reply=p->timer;p->timer=(GSBinding){2};}
    else return GS_UNSUPPORTED;
    return GS_OK;
}
static GSStatus opl(void *ctx,GSRegisterWrite w){GSSdlStartup *p=ctx;return p->audio_ops.opl(p->audio,w);}
static GSStatus advance(void *ctx,uint64_t ns){GSSdlStartup *p=ctx;return p->audio_ops.advance(p->audio,ns);}
static GSStatus clock_delivery(void *ctx,GSClockDelivery kind){(void)ctx;return kind==GS_CLOCK_BIOS_CHAIN?GS_OK:GS_UNSUPPORTED;}
static GSStatus pit_command(void *ctx,uint8_t value){GSSdlStartup *p=ctx;if(value!=0x36)return GS_UNSUPPORTED;p->pit_phase=0;return GS_OK;}
static GSStatus pit_counter(void *ctx,uint8_t value){GSSdlStartup *p=ctx;p->divisor=p->pit_phase?(uint16_t)((p->divisor&255)|value<<8):(uint16_t)((p->divisor&65280)|value);p->pit_phase^=1;return GS_OK;}
static GSStatus mask(void *ctx,uint8_t value){GSSdlStartup *p=ctx;p->mask=value;return GS_OK;}
static GSStatus read_mask(void *ctx,uint8_t *value){GSSdlStartup *p=ctx;if(!value)return GS_INVALID;*value=p->mask;return GS_OK;}
static GSStatus ack(void *ctx){(void)ctx;return GS_OK;}
static GSStatus interrupt(void *ctx,unsigned irq,uint32_t clocks,int enabled){GSSdlStartup *p=ctx;(void)clocks;if(irq>=8)return GS_INVALID;return enabled&&!(p->mask&(1u<<irq))?GS_OK:GS_EMPTY;}
static GSStatus deliver(void *ctx,GSEventKind kind,GSEvent *event){
    GSSdlStartup *p=ctx;GSStatus result=p->time_ops.deliver(p->time,kind,event);if(result!=GS_OK)return result;
    if(kind==GS_RETRACE_ACTIVE)p->video->retrace=1;
    if(kind==GS_RETRACE_INACTIVE)p->video->retrace=0;
    if(event->nanoseconds>p->audio_ns){result=p->audio_ops.advance(p->audio,event->nanoseconds-p->audio_ns);p->audio_ns=event->nanoseconds;}
    if(result!=GS_OK)return result;
    /* DAC fades do not swap pages. Refresh the current indexed page at its
     * existing retrace cut so each palette step is visible. This is provider
     * presentation/pacing, never another game frame or callback. */
    if(kind==GS_RETRACE_ACTIVE){
        result=p->time_ops.pace(p->time);if(result!=GS_OK)return result;
        if(p->video->renderer){GSVideoOps video=gs_video_operations();result=video.present(p->video);if(result==GS_OK)p->presentations++;}
    }
    return result;
}
static GSStatus pace(void *ctx){GSSdlStartup *p=ctx;return p->time_ops.pace(p->time);}
static GSStatus suspend_time(void *ctx,int v){GSSdlStartup *p=ctx;return p->time_ops.suspend(p->time,v);}
void gs_sdl_startup(GSSdlStartup *p,GameServices *s,GSSdlVideo *v,GSSdlInput *i,GSSdlTime *t,GSSdlAudio *a,GSSdlFiles *f,GSSdlSeed *seed,int adlib){
    memset(p,0,sizeof *p);memset(s,0,sizeof *s);p->video=v;p->time=t;p->audio=a;p->adlib=!!adlib;
    p->audio_ops=gs_audio_operations();p->time_ops=gs_time_operations();p->timer=(GSBinding){1};p->mode=(GSVideoModeReply){3,80,0};
    s->video_context=v;s->video=gs_video_operations();s->input_context=i;s->input=gs_input_operations();
    s->audio_context=s->time_context=s->lifecycle_context=p;
    s->audio=(GSAudioOps){opl,status,advance,clock_delivery,calibration,lifetime,NULL};
    s->time=(GSTimeOps){deliver,suspend_time,pace,pit_command,pit_counter,mask,read_mask,ack,interrupt};
    s->lifecycle=(GSLifecycleOps){request,binding,query,mode,terminate};
    s->files_context=f;s->files=gs_files_operations();s->seed_context=seed;s->seed=gs_seed_operations();
}
