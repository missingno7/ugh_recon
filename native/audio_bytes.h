#ifndef NATIVE_AUDIO_BYTES_H
#define NATIVE_AUDIO_BYTES_H
/* Borrowed byte-window reads. The verification composition can provide a
 * typed shared view for state aliases; ordinary resource arrays stay direct.
 * This is a read service, not an owner or a copied resource window. */
#ifdef NATIVE_AUDIO_BYTE_SERVICE
#include <stdint.h>
uint8_t audio_borrowed_byte(const uint8_t *window,uint32_t index);
#define AUDIO_BYTE(window,index) audio_borrowed_byte(window,index)
#else
#define AUDIO_BYTE(window,index) window[index]
#endif
#endif
