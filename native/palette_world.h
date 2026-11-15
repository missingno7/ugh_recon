#ifndef NATIVE_PALETTE_WORLD_H
#define NATIVE_PALETTE_WORLD_H
#include <stdint.h>
enum { PALETTE_COMPONENTS=768 };
/* Single persistent owner. Resource-selection views and page geometry are
 * borrowed from their existing owners; no palette values live in those views. */
typedef struct NativePaletteWorld {uint8_t base[PALETTE_COMPONENTS],faded[PALETTE_COMPONENTS];} NativePaletteWorld;
NativePaletteWorld *native_palette_world(void);
/* Streaming DAC batch: select once, then consume each component immediately.
 * Keeping this streaming preserves read/output interleaving and alias effects.
 * The provider owns the full DAC cursor and inherited hardware controls. */
typedef enum PaletteDacKind { PALETTE_DAC_SELECT,PALETTE_DAC_COMPONENT } PaletteDacKind;
typedef struct PaletteDacWrite {PaletteDacKind kind;uint8_t value;} PaletteDacWrite;
void palette_service_dac(PaletteDacWrite request);
#endif
