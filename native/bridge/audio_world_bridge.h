#ifndef AUDIO_WORLD_BRIDGE_H
#define AUDIO_WORLD_BRIDGE_H
#include "timing_world_bridge.h"
void audio_world_bindings(void);
void audio_world_snapshot(AudioState *view);
/* Peer requests carry enum identities, never original callee offsets. The
 * binding word only admits the existing canonical ABI code view; it cannot
 * select a peer. Delivery uses direct native calls, without a resolver. */
int audio_peer_deliver(AudioPeerRole role,uint16_t binding,Regs *registers);
int audio_peer_active(void);
uint16_t audio_external_read(unsigned index);
void audio_external_write(unsigned index,uint16_t value);
void audio_workspace_read(uint8_t *destination,uint32_t address,unsigned count);
void audio_borrowed_store(uint8_t *window,uint32_t index,uint8_t value);
void audio_workspace_publish(uint32_t address,const uint8_t *source,unsigned count,unsigned extent,size_t written);
#endif
