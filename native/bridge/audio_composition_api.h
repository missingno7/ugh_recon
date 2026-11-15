#ifndef AUDIO_COMPOSITION_API_H
#define AUDIO_COMPOSITION_API_H
#ifdef UGH_NATIVE_AUDIO
#include "audio_world_bridge.h"
typedef AudioPeerRole AudioPeerBinding;
#define AUDIO_SOUND_PEER(name) AUDIO_PEER_##name
#define AUDIO_C_PEER(name) AUDIO_PEER_##name
#define AUDIO_C_SHORT_PEER(name) AUDIO_PEER_##name
#define AUDIO_TIMER_PEER(name) AUDIO_PEER_##name
#define AUDIO_PEER_TRANSFER(bank,target,registers) audio_peer_deliver(target,bank,registers)
#define AUDIO_LITERAL(name,registers) ((void)(registers),UGH_UNSUPPORTED)
#else
typedef uint16_t AudioPeerBinding;
#define AUDIO_SOUND_PEER(name) S(name)
#define AUDIO_C_PEER(name) UGH_O_C_##name
#define AUDIO_TIMER_PEER(name) T(name)
#define AUDIO_C_SHORT_PEER(name) C(name)
#define AUDIO_PEER_TRANSFER(bank,target,registers) ugh_dispatch(bank,target,registers)
#define AUDIO_LITERAL(name,registers) name(registers)
#endif
#endif
