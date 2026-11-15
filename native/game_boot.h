#ifndef NATIVE_GAME_BOOT_H
#define NATIVE_GAME_BOOT_H
#include "../port/services.h"
#include "lifecycle_world.h"
#include "run_world.h"
#include "input_world.h"
#include "palette_world.h"
#include "front_end_world.h"
#include "video_dos.h"
#include "random.h"
#include "adlx_lifetime.h"
#include "timer_lifetime.h"

/* First production slice. Each member is the sole store for its domain in
 * this target; the verification host continues to use its existing owners. */
typedef struct GameWorld {
    NativeLifecycleWorld lifecycle;
    NativeRunWorld run;
    NativeInputWorld input;
    NativePaletteWorld palette;
    NativeFrontEndWorld front;
    VideoPages pages;
    RandomState random;
    AudioState audio;
    AudioResetCells audio_reset;
    TimerState timer;
    TimerLifetime timer_life;
    GSBinding keyboard_saved,critical_saved;
    uint16_t audio_initialized,delay_multiplier,calibration_remainder;
    uint8_t audio_attempted;
    uint8_t scratch[65536];
    unsigned frames;
} GameWorld;
typedef enum GameBootKind { GAME_BOOT_SLICE_END, GAME_BOOT_SERVICE_ERROR,
    GAME_BOOT_UNSUPPORTED, GAME_BOOT_QUIT } GameBootKind;
typedef struct GameBootResult {
    GameBootKind kind; GSStatus status; LifecycleAction action;
} GameBootResult;
GSStatus game_world_construct(GameWorld *,GameServices *);
/* Stops after pictures and gameplay video setup, immediately before the first
 * menu entry. A caller cannot mistake this for a game exit. */
GameBootResult game_boot(GameWorld *,GameServices *);
#endif
