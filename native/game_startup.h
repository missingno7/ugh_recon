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
GSStatus game_sample_input_trigger(GameWorld *,GameServices *,uint8_t);
GSStatus game_initialize_audio(GameWorld *,GameServices *);
GSStatus game_startup_timer(GameWorld *,GameServices *);
GSStatus game_video_retrace(GameWorld *,GameServices *,int);
GSStatus game_video_next(GameWorld *,GameServices *);
GSStatus game_video_swap(GameWorld *,GameServices *);
GSStatus game_video_fade(GameWorld *,GameServices *,int);
GSStatus game_video_wait(GameWorld *,GameServices *,uint16_t,uint8_t *);
GSStatus game_show_picture(GameWorld *,GameServices *,unsigned,uint16_t,int16_t *);
#endif
