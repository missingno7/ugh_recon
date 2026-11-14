#ifndef NATIVE_ADLX_DIGITAL_H
#define NATIVE_ADLX_DIGITAL_H
#include "audio.h"

/* Temporary borrows of the one audio owner. No new resident state. */
typedef struct AudioDigitalView {
    AudioChannel *channels;
    uint16_t devices,busy,count,mask;
    uint8_t interrupt_busy,selection,interrupt_mask;
} AudioDigitalView;
typedef struct AudioDmaHeader {uint16_t address,offset,count;uint8_t page;} AudioDmaHeader;
typedef struct AudioDmaLocation {
    AudioDmaHeader header;
    uint16_t final_address;
    uint8_t initial_page,carry,fallback;
} AudioDmaLocation;
AudioDmaLocation audio_dma_locate(uint16_t storage_page,uint16_t storage_offset,uint16_t buffer,uint16_t skip,uint16_t fallback);

typedef struct AudioDigitalWrite {uint16_t port;uint8_t value;} AudioDigitalWrite;
typedef struct AudioDmaBlock {
    AudioDigitalWrite writes[9];
    uint8_t commands[3];uint16_t encoded_count;
} AudioDmaBlock;
AudioDmaBlock audio_dma_block(uint16_t count,uint16_t address,uint8_t page);
/* Only called after rate_enabled admits the unsigned rate>=1000. */
uint16_t audio_dsp_constant(uint16_t rate);
int audio_dsp_rate_enabled(uint16_t devices,uint16_t rate);
typedef struct AudioDspPoll {uint16_t remaining;uint8_t busy;} AudioDspPoll;
/* remaining=0 means 65536 reads, including the timeout write. */
int audio_dsp_poll(AudioDspPoll *work,uint8_t status,int wait_busy);

typedef enum AudioDigitalAction {
    AUDIO_DIGITAL_DONE,AUDIO_DIGITAL_REJECT,AUDIO_DIGITAL_WAIT,
    AUDIO_DIGITAL_STOP_ADLIB,AUDIO_DIGITAL_MIX,AUDIO_DIGITAL_START_BLOCK,
    AUDIO_DIGITAL_ACK,AUDIO_DIGITAL_MASK,AUDIO_DIGITAL_BUSY_RETURN,
    AUDIO_DIGITAL_DSP_COMMAND,AUDIO_DIGITAL_UNMASK,AUDIO_DIGITAL_INTERRUPT
} AudioDigitalAction;
AudioDigitalAction audio_digital_stop_begin(AudioDigitalView *view,uint16_t slot);
/* Finish is admitted only for an active sample slot0..7 after its wait. */
void audio_digital_stop_finish(AudioDigitalView *view,uint16_t slot);
int audio_digital_prime_enabled(const AudioDigitalView *view);
int audio_digital_prime_active(const AudioDigitalView *view);
AudioDigitalAction audio_digital_interrupt_begin(AudioDigitalView *view);
AudioDigitalAction audio_digital_interrupt_queue(AudioDigitalView *view,uint16_t queued);
uint16_t audio_digital_queue_index(uint8_t selection);
uint8_t audio_digital_pic(uint8_t incoming,uint8_t mask,int enable);

typedef struct AudioDmaView {AudioDigitalView shared;AudioDmaHeader headers[2];} AudioDmaView;
typedef struct AudioDmaInterruptWork {uint8_t stage,selected;} AudioDmaInterruptWork;
typedef struct AudioDmaRequest {AudioDigitalAction action;AudioDmaHeader header;uint8_t selected;} AudioDmaRequest;
/* EOI is delivered before beginning; ACK precedes all queue reads. Rebind
 * headers after each synchronous block/mix service, including their aliases. */
AudioDmaRequest audio_dma_interrupt_next(AudioDmaView *view,AudioDmaInterruptWork *work,uint16_t reply);
typedef struct AudioDmaPrimeWork {uint8_t stage;} AudioDmaPrimeWork;
typedef struct AudioDmaPrimeRequest {AudioDigitalAction action;uint16_t destination;uint8_t command,count_checked;} AudioDmaPrimeRequest;
AudioDmaPrimeRequest audio_dma_prime_next(AudioDmaView *view,AudioDmaPrimeWork *work,uint16_t reply);

/* Bank positions index a borrowed cyclic 1MiB resource, not segmented RAM. */
uint32_t audio_bank_add(uint32_t position,uint32_t amount);
uint32_t audio_bank_entry(uint32_t base,uint32_t directory,uint16_t index);
int audio_bank_admit(uint16_t slot,uint32_t entry,uint32_t base,uint32_t length);
uint8_t audio_bank_tag_position(uint8_t character);
uint8_t audio_bank_tag_byte(int sample,uint8_t character);
typedef enum AudioBankAction {AUDIO_BANK_READ,AUDIO_BANK_SAMPLE,AUDIO_BANK_ADLX,AUDIO_BANK_REJECT} AudioBankAction;
typedef struct AudioBankScan {uint32_t source;uint8_t character,sample,first;} AudioBankScan;
typedef struct AudioBankRequest {AudioBankAction action;uint32_t position;} AudioBankRequest;
AudioBankRequest audio_bank_scan_next(AudioBankScan *work,uint8_t reply);
#endif
