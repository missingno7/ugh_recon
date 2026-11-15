#ifndef INPUT_WORLD_BRIDGE_H
#define INPUT_WORLD_BRIDGE_H
#include "ugh.h"
#include "../input_world.h"
int input_shared_read(uint32_t address,uint8_t *value);
int input_shared_write(uint32_t address,uint8_t value);
int input_is_owned(uint32_t address);
void input_cold_import(uint8_t *memory);
void input_require_seal(const uint8_t *memory);
void input_serialize(uint8_t *output);
uint32_t input_check_serialization(const uint8_t *output);
unsigned input_owned_bytes(void);
uint8_t input_borrowed_byte(const uint8_t *window,uint32_t index);
void input_borrowed_store(uint8_t *window,uint32_t index,uint8_t value);
typedef enum InputPeerRole {INPUT_PEER_PollKeyboardScanChange,INPUT_PEER_SampleJoystickAxesAndButtons,INPUT_PEER_WaitNextVerticalRetrace} InputPeerRole;
int input_peer_deliver(InputPeerRole role,uint16_t return_identity,Regs *r);
int input_editor_queue(Regs *r);
int input_capture_keyboard(Regs *r);
#endif
