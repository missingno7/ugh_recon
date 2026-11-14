#include "adlx_samples.h"

int16_t audio_sample_scale(uint8_t sample,uint8_t volume)
{
    int16_t signed_sample=sample<128 ? sample : (int16_t)sample-256;
    int16_t product=(int16_t)(signed_sample*(int16_t)(volume>>1));
    uint8_t high=(uint8_t)((uint16_t)product>>8);
    return high<128 ? high : (int16_t)high-256;
}
AudioSampleReset audio_sample_reset(uint16_t index)
{uint32_t product=(uint32_t)index*42u;AudioSampleReset result={(uint16_t)product,(uint8_t)(product>65535u)};return result;}
AudioSampleMixWork audio_sample_mix_begin(AudioSampleView *view,uint16_t requested,uint16_t destination)
{
    AudioSampleMixWork work={requested,destination,0,0,0,0};
    if(!view->count) work.stage=7;
    else {view->busy=1;view->remaining=requested>>1;view->first_sum=0;view->second_sum=0;}
    return work;
}
static AudioSampleRequest sample_finished(AudioSampleView *view,AudioSampleMixWork *work)
{
    view->busy=0;work->result=(uint16_t)(work->requested-view->remaining);work->stage=7;
    AudioSampleRequest request={AUDIO_SAMPLE_DONE,{0},0,0};return request;
}
static uint16_t sample_offset(uint16_t cursor,uint16_t scale)
{return (uint16_t)(((uint32_t)cursor*scale)>>8);}
static unsigned sample_voice(AudioSampleView *view,AudioSampleMixWork *work,AudioSampleRequest *request)
{
    unsigned bit=1u<<work->voice;AudioChannel *voice=&view->voices[work->voice];
    if(!(view->mask&bit)) {work->voice++;return 0;}
    uint16_t offset=sample_offset(voice->cursor.index,voice->step_q8);
    if(offset>=voice->length) {
        if(!(voice->control&2u)) {
            uint16_t old=voice->repeats;voice->repeats=(uint16_t)(old-1u);
            if((int16_t)old<=1) {
                view->mask=(uint16_t)((view->mask&65280u)|((uint8_t)view->mask^bit));old=view->count;view->count=(uint16_t)(old-1u);
                if((int16_t)old<=1) return 2;
                work->voice++;return 0;
            }
        }
        voice->cursor.index=0;work->voice++;return 0;
    }
    request->action=AUDIO_SAMPLE_READ;request->source=voice->start;
    request->source.index=(uint16_t)(request->source.index+offset);work->stage=1;return 1;
}
static void sample_accumulate(AudioSampleView *view,AudioSampleMixWork *work,uint16_t sample)
{
    AudioChannel *voice=&view->voices[work->voice];
    view->first_sum=(uint16_t)(view->first_sum+audio_sample_scale((uint8_t)sample,(uint8_t)voice->volume));
    view->second_sum=(uint16_t)(view->second_sum+audio_sample_scale((uint8_t)(sample>>8),(uint8_t)voice->volume));
    voice->cursor.index=(uint16_t)(voice->cursor.index+1u);work->voice++;work->stage=0;
}
AudioSampleRequest audio_sample_mix_next(AudioSampleView *view,AudioSampleMixWork *work,uint16_t sample)
{
    AudioSampleRequest request={AUDIO_SAMPLE_DONE,{0},0,0};
    for(;;) {
        if(work->stage==7) return request;
        if(work->stage==1) {
            sample_accumulate(view,work,sample);
        }
        if(work->stage==0) {
            while(work->voice<8) {
                unsigned action=sample_voice(view,work,&request);
                if(action==2) return sample_finished(view,work);
                if(action==1) return request;
            }
            work->stage=2;
        }
        if(work->stage==2 || work->stage==3) {
            int32_t divisor=(int16_t)view->count;
            int32_t sum=(int16_t)(work->stage==2 ? view->first_sum : view->second_sum);
            if(!divisor || (sum==-32768 && divisor==-1)) {request.action=AUDIO_SAMPLE_FAULT;return request;}
            int32_t quotient=sum/divisor;
            request.action=AUDIO_SAMPLE_WRITE;request.destination=work->destination;
            request.value=(uint8_t)(quotient+127);work->destination=(uint16_t)(work->destination+1u);work->stage++;return request;
        }
        view->remaining=(uint16_t)(view->remaining-1u);
        if((int16_t)view->remaining<=0) return sample_finished(view,work);
        view->first_sum=0;view->second_sum=0;
        if(++work->iterations==65536u) {request.action=AUDIO_SAMPLE_BOUND;return request;}
        work->voice=0;work->stage=0;
    }
}

static uint32_t sample_ring(uint32_t position) {return position&1048575u;}
AudioSampleImportWork audio_sample_import_begin(uint16_t devices,uint16_t slot,uint32_t position,uint16_t volume,uint16_t repeats,uint16_t scale)
{
    AudioSampleImportWork work={0};work.origin=position;work.position=position;work.slot=slot;work.volume=volume>255 ? 255 : volume;
    work.repeats=repeats;work.scale=scale;work.result=65535;work.first=1;work.budget=5000000;
    if(!(devices&2u) || slot>=8) work.stage=30;
    return work;
}
static AudioSampleImportRequest sample_import_read(AudioSampleImportWork *work,unsigned publication,uint32_t position)
{
    AudioSampleImportRequest request={AUDIO_SAMPLE_IMPORT_READ,position,work->position,(uint8_t)publication,0};
    if(publication) {work->position=sample_ring(work->position+1u);request.next=work->position;request.original_form=work->first;work->first=0;}
    return request;
}
AudioSampleImportRequest audio_sample_import_next(AudioSampleImportWork *work,uint16_t reply)
{
    AudioSampleImportRequest request={AUDIO_SAMPLE_IMPORT_DONE,0,0,0,0};
    for(;;) switch(work->stage) {
    case 0:work->stage=1;return sample_import_read(work,1,work->position);
    case 1:
        if((uint8_t)reply!=(uint8_t)"FORM"[work->character]) {work->stage=30;break;}
        if(++work->character<4) {work->stage=0;break;}
        work->character=0;work->length=0;work->stage=2;break;
    case 2:work->stage=3;return sample_import_read(work,2,work->position);
    case 3:
        work->length=(work->length<<8)+(uint8_t)reply;
        if(++work->character<4) {work->stage=2;break;}
        work->extent=work->length;work->character=0;work->stage=4;break;
    case 4:
        if(!work->budget) {request.action=AUDIO_SAMPLE_IMPORT_BOUND;return request;}
        work->budget--;work->character=0;work->stage=5;break;
    case 5:work->stage=6;return sample_import_read(work,1,work->position);
    case 6:
        if((uint8_t)reply==(uint8_t)(work->tag ? "BODY" : "VHDR")[work->character]) {
            if(++work->character<4) {work->stage=5;break;}
            if(work->tag) {work->character=0;work->length=0;work->stage=12;break;}
            work->stage=7;break;
        }
        if(sample_ring(work->position)>sample_ring(work->origin+work->extent)) {work->stage=30;break;}
        work->stage=4;break;
    case 7:work->stage=8;return sample_import_read(work,0,sample_ring(work->position+16u));
    case 8:work->rate=(uint16_t)((uint8_t)reply*256u);work->stage=9;return sample_import_read(work,0,sample_ring(work->position+17u));
    case 9:work->rate=(uint16_t)(work->rate+(uint8_t)reply);work->stage=10;return sample_import_read(work,0,sample_ring(work->position+19u));
    case 10:work->mode=(uint8_t)reply ? 3 : 2;work->tag=1;work->stage=4;break;
    case 12:work->stage=13;return sample_import_read(work,2,work->position);
    case 13:
        work->length=(work->length<<8)+(uint8_t)reply;
        if(++work->character<4) {work->stage=12;break;}
        if(work->length>64000u) {work->stage=30;break;}
        work->length&=65534u;work->stage=14;request.action=AUDIO_SAMPLE_IMPORT_STOP;return request;
    case 14:work->stage=15;request.action=AUDIO_SAMPLE_IMPORT_APPLY;return request;
    case 15:work->budget=5000000;work->stage=16;break;
    case 16:
        if(!work->budget) {request.action=AUDIO_SAMPLE_IMPORT_BOUND;return request;}
        work->budget--;work->stage=17;request.action=AUDIO_SAMPLE_IMPORT_WAIT;return request;
    case 17:if(reply) {work->stage=16;break;}work->stage=18;request.action=AUDIO_SAMPLE_IMPORT_ACTIVATE;return request;
    case 18:work->result=1;work->stage=30;break;
    default:return request;
    }
}
void audio_sample_import_apply(AudioChannel *voice,const AudioSampleImportWork *work,AudioCursor data)
{
    voice->control=work->repeats ? 0 : 2;if(work->repeats) voice->repeats=work->repeats;
    voice->volume=work->volume;voice->start=data;voice->cursor.window=data.window;voice->cursor.index=0;
    voice->length=(uint16_t)work->length;voice->sample_mode=work->mode;voice->sample_selector=work->mode&1u;
    voice->step_q8=work->scale;voice->sample_half_length=(uint16_t)(work->length>>1);voice->sample_accumulator=work->mode&2u ? 127 : 0;voice->sample_rate=work->rate;
}
void audio_sample_activate(AudioSampleView *view,uint16_t slot)
{view->count=(uint16_t)(view->count+1u);view->mask=(uint16_t)(view->mask|(1u<<slot));}
