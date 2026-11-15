#ifndef PALETTE_WORLD_BRIDGE_H
#define PALETTE_WORLD_BRIDGE_H
#include "ugh.h"
#include "../palette_world.h"
int palette_is_owned(uint32_t address);
int palette_shared_read(uint32_t address,uint8_t *value);
int palette_shared_write(uint32_t address,uint8_t value);
void palette_cold_import(uint8_t *memory);
void palette_require_seal(const uint8_t *memory);
void palette_serialize(uint8_t *observation);
uint32_t palette_check_serialization(const uint8_t *observation);
unsigned palette_owned_bytes(void);
uint8_t palette_borrowed_byte(const uint8_t *window,uint32_t index);
void palette_borrowed_store(uint8_t *window,uint32_t index,uint8_t value);
/* Original near-frame ABI is confined to this verification adapter. */
typedef enum PalettePeerRole {PALETTE_PEER_WaitNextVerticalRetrace,PALETTE_PEER_ScaleAndUploadFadedPalette} PalettePeerRole;
int palette_peer_deliver(PalettePeerRole role,uint16_t return_identity,Regs *registers);
#endif
