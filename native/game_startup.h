#ifndef NATIVE_GAME_STARTUP_H
#define NATIVE_GAME_STARTUP_H
#include "game_boot.h"
GSStatus game_picture_mode(GameWorld *,GameServices *);
GSStatus game_gameplay_mode(GameWorld *,GameServices *);
GSStatus game_clear_video(GameWorld *,GameServices *);
GSStatus game_startup_pictures(GameWorld *,GameServices *);
GSStatus game_install_input(GameWorld *,GameServices *);
GSStatus game_calibrate_input(GameWorld *,GameServices *);
GSStatus game_poll_input(GameWorld *,GameServices *);
GSStatus game_sample_input(GameWorld *,GameServices *);
GSStatus game_initialize_audio(GameWorld *,GameServices *);
GSStatus game_startup_timer(GameWorld *,GameServices *);
#endif
