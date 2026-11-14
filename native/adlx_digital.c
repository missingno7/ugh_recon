#include "adlx_digital.h"
AudioDmaLocation audio_dma_locate(uint16_t storage_page,uint16_t storage_offset,uint16_t buffer,uint16_t skip,uint16_t fallback)
{
    uint32_t start=(uint32_t)storage_offset+buffer;
    uint8_t page=(uint8_t)(storage_page+(start>65535u));
    uint16_t before=(uint16_t)start;
    AudioDmaLocation result={{before,buffer,0,page},(uint16_t)(before+1024u),page,0,0};
    if((uint32_t)before+1024u>65535u) {
        uint32_t next=(uint32_t)before+skip;
        result.carry=(uint8_t)(next>65535u);result.fallback=1;
        result.final_address=(uint16_t)next;
        result.header.address=result.final_address;result.header.offset=fallback;
        result.header.page=(uint8_t)(page+result.carry);
    }
    return result;
}
AudioDmaBlock audio_dma_block(uint16_t count,uint16_t address,uint8_t page)
{
    uint16_t encoded=(uint16_t)(count-1u);
    AudioDmaBlock result={{{10,5},{12,0},{11,73},{2,(uint8_t)address},{2,(uint8_t)(address>>8)},
        {131,page},{3,(uint8_t)encoded},{3,(uint8_t)(encoded>>8)},{10,1}},
        {20,(uint8_t)encoded,(uint8_t)(encoded>>8)},encoded};
    return result;
}
uint16_t audio_dsp_constant(uint16_t rate)
{return (uint16_t)(0u-(uint16_t)(1000000u/rate));}
int audio_dsp_rate_enabled(uint16_t devices,uint16_t rate)
{return (devices&2u) && rate>=1000u;}
int audio_dsp_poll(AudioDspPoll *work,uint8_t status,int wait_busy)
{
    work->busy=(uint8_t)!!(status&128u);work->remaining=(uint16_t)(work->remaining-1u);
    return work->remaining && (wait_busy ? work->busy : !work->busy);
}
AudioDigitalAction audio_digital_stop_begin(AudioDigitalView *view,uint16_t slot)
{
    if(slot>12u) return AUDIO_DIGITAL_REJECT;
    if(!(view->devices&2u)) return AUDIO_DIGITAL_DONE;
    if(slot>=8u) return AUDIO_DIGITAL_STOP_ADLIB;
    if(!(view->mask&(1u<<slot))) return AUDIO_DIGITAL_REJECT;
    view->channels[slot].repeats=0;return AUDIO_DIGITAL_WAIT;
}
void audio_digital_stop_finish(AudioDigitalView *view,uint16_t slot)
{
    uint16_t bit=(uint16_t)(1u<<slot);
    if(view->mask&bit) {view->mask=(uint16_t)(view->mask&~bit);view->count=(uint16_t)(view->count-1u);}
}
int audio_digital_prime_enabled(const AudioDigitalView *view) {return !!(view->devices&2u);}
int audio_digital_prime_active(const AudioDigitalView *view) {return (int16_t)view->count>0;}
AudioDigitalAction audio_digital_interrupt_begin(AudioDigitalView *view)
{
    if(view->interrupt_busy&1u) return AUDIO_DIGITAL_BUSY_RETURN;
    view->interrupt_busy=1;return AUDIO_DIGITAL_ACK;
}
AudioDigitalAction audio_digital_interrupt_queue(AudioDigitalView *view,uint16_t queued)
{
    if(queued<40u) return AUDIO_DIGITAL_MASK;
    view->selection^=1u;return AUDIO_DIGITAL_START_BLOCK;
}
uint16_t audio_digital_queue_index(uint8_t selection) {return (selection&1u) ? 0 : 1;}
uint8_t audio_digital_pic(uint8_t incoming,uint8_t mask,int enable)
{return enable ? (uint8_t)(incoming&~mask) : (uint8_t)(incoming|mask);}
AudioDmaRequest audio_dma_interrupt_next(AudioDmaView *view,AudioDmaInterruptWork *work,uint16_t reply)
{
    AudioDmaRequest request={AUDIO_DIGITAL_DONE,{0,0,0,0},0};
    switch(work->stage++) {
    case 0:request.action=audio_digital_interrupt_begin(&view->shared);return request;
    case 1:
        work->selected=(uint8_t)audio_digital_queue_index(view->shared.selection);
        request.selected=work->selected;request.header=view->headers[work->selected];
        request.action=audio_digital_interrupt_queue(&view->shared,request.header.count);
        if(request.action==AUDIO_DIGITAL_MASK) work->stage=4;
        return request;
    case 2:
        view->headers[work->selected].count=0;
        request.selected=(uint8_t)(1u-work->selected);request.header=view->headers[request.selected];
        request.action=AUDIO_DIGITAL_MIX;return request;
    case 3:view->headers[1u-work->selected].count=reply;break;
    default:break;
    }
    view->shared.interrupt_busy=0;return request;
}
AudioDmaPrimeRequest audio_dma_prime_next(AudioDmaView *view,AudioDmaPrimeWork *work,uint16_t reply)
{
    AudioDmaPrimeRequest request={AUDIO_DIGITAL_DONE,0,0,0};
    switch(work->stage++) {
    case 0:
        if(!audio_digital_prime_enabled(&view->shared)) return request;
        request.action=AUDIO_DIGITAL_WAIT;return request;
    case 1:
        if(view->shared.busy&1u) {work->stage=1;request.action=AUDIO_DIGITAL_WAIT;return request;}
        request.count_checked=1;
        if(!audio_digital_prime_active(&view->shared)) return request;
        request.action=AUDIO_DIGITAL_DSP_COMMAND;request.command=208;return request;
    case 2:request.action=AUDIO_DIGITAL_MIX;request.destination=view->headers[0].offset;return request;
    case 3:
        view->headers[0].count=reply;view->shared.selection=1;
        request.action=AUDIO_DIGITAL_UNMASK;return request;
    case 4:request.action=AUDIO_DIGITAL_INTERRUPT;return request;
    default:return request;
    }
}
uint32_t audio_bank_add(uint32_t position,uint32_t amount) {return (position+amount)&1048575u;}
uint32_t audio_bank_entry(uint32_t base,uint32_t directory,uint16_t index)
{return audio_bank_add(audio_bank_add(audio_bank_add(base,directory),(uint16_t)(index*12u)),8);}
int audio_bank_admit(uint16_t slot,uint32_t entry,uint32_t base,uint32_t length)
{return slot<12u && entry<=audio_bank_add(base,length);}
uint8_t audio_bank_tag_position(uint8_t character)
{return character<4u ? character : (uint8_t)(character+4u);}
uint8_t audio_bank_tag_byte(int sample,uint8_t character)
{
    const uint8_t sample_tag[8]={'F','O','R','M','8','S','V','X'};
    const uint8_t adlx_tag[8]={'A','D','L','X','A','H','D','R'};
    return sample ? sample_tag[character] : adlx_tag[character];
}
AudioBankRequest audio_bank_scan_next(AudioBankScan *work,uint8_t reply)
{
    AudioBankRequest request={AUDIO_BANK_READ,work->source};
    if(work->first) work->first=0;
    else if(reply!=audio_bank_tag_byte(work->sample,work->character)) {
        if(!work->sample) {request.action=AUDIO_BANK_REJECT;return request;}
        work->sample=0;work->character=0;
    } else if(++work->character==8) {
        request.action=work->sample ? AUDIO_BANK_SAMPLE : AUDIO_BANK_ADLX;return request;
    }
    request.position=audio_bank_add(work->source,audio_bank_tag_position(work->character));return request;
}
