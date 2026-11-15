#ifndef VIDEO_PAGES_BRIDGE_H
#define VIDEO_PAGES_BRIDGE_H
#include "ugh.h"
#include "../video_pages.h"
int video_pages_is_owned(uint32_t address);
int video_pages_shared_read(uint32_t address,uint8_t *value);
int video_pages_shared_write(uint32_t address,uint8_t value);
void video_pages_cold_import(uint8_t *memory);
void video_pages_require_seal(const uint8_t *memory);
void video_pages_serialize(uint8_t *output);
uint32_t video_pages_check_serialization(const uint8_t *output);
unsigned video_pages_owned_bytes(void);
uint8_t video_pages_borrowed_byte(const uint8_t *window,uint32_t index);
void video_pages_borrowed_store(uint8_t *window,uint32_t index,uint8_t value);
typedef enum VideoPeerRole {
 VIDEO_PEER_BlackenVgaPalette,VIDEO_PEER_EnableAllVgaWritePlanes,
 VIDEO_PEER_ClearAllVgaPlanes,VIDEO_PEER_WaitNextVerticalRetrace,
 VIDEO_PEER_WaitVerticalRetraceActive,VIDEO_PEER_WaitVerticalRetraceInactive,
 VIDEO_PEER_PollKeyboardScanChange,VIDEO_PEER_SampleJoystickAxesAndButtons
} VideoPeerRole;
int video_pages_peer(VideoPeerRole role,uint16_t return_identity,Regs *r);
#endif
