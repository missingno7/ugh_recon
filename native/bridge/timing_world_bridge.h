#ifndef TIMING_WORLD_BRIDGE_H
#define TIMING_WORLD_BRIDGE_H
#include "ugh.h"
#include "../timing_world.h"
int timing_shared_read(uint32_t address,uint8_t *value);
int timing_shared_write(uint32_t address,uint8_t value);
int timing_is_owned(uint32_t address);
void timing_cold_import(uint8_t *memory);
void timing_serialize(uint8_t *observation);
void timing_require_seal(const uint8_t *memory);
int timing_snapshot(TimerState *state,uint16_t *open);
void timing_commit(const TimerState *state,const uint16_t *open);
int timing_deliver(TimerCallback callback,Regs *r);
void timing_saved_words(uint16_t *offset,uint16_t *segment);
void timing_save_binding(uint16_t offset,uint16_t segment);
unsigned timing_owned_bytes(void);
uint32_t timing_check_serialization(const uint8_t *observation);
int timing_audio_callback_active(void);
uint8_t audio_borrowed_byte(const uint8_t *window,uint32_t index);
#endif
