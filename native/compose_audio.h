#ifndef NATIVE_COMPOSE_AUDIO_H
#define NATIVE_COMPOSE_AUDIO_H
#include "game_boot.h"
#include "music_clock.h"
/* IDs refer to admitted pack objects. No executable coordinates or callback
 * words are accepted by this interface. API negatives remain ordinary replies. */
typedef struct GameAudioResult {GSStatus status;uint16_t value;} GameAudioResult;
GSStatus game_audio_construct(GameWorld *,GameServices *);
GSResourceId game_audio_resource_id(unsigned);
GSResourceId game_audio_score_resource(void);
GSResourceId game_audio_menu_resource(void);
GSResourceId game_audio_game_over_resource(void);
GSResourceId game_audio_intro_resource(void);
GSStatus game_audio_init(GameWorld *,GameServices *,uint16_t mask);
GameAudioResult game_audio_music_start(GameWorld *,GameServices *,GSResourceId,uint16_t duration,uint16_t volume);
GameAudioResult game_audio_music_stop(GameWorld *,GameServices *,uint16_t duration);
GameAudioResult game_audio_effect(GameWorld *,GameServices *,GSResourceId,uint16_t volume,uint16_t repeats);
GameAudioResult game_audio_channel(GameWorld *,GameServices *,unsigned,int start,uint16_t volume);
GSStatus game_audio_effect_stop(GameWorld *,GameServices *,uint16_t);
GSStatus game_audio_volume(GameWorld *,GameServices *,uint16_t);
GSStatus game_audio_cancel_fade(GameWorld *,GameServices *);
GSStatus game_audio_schedule_fade(GameWorld *,GameServices *);
GSStatus game_audio_events(GameWorld *,GameServices *,unsigned record);
GSStatus game_audio_tick(GameWorld *,GameServices *);
GSStatus game_audio_guarded_tick(GameWorld *,GameServices *);
GSStatus game_audio_timer(GameWorld *,GameServices *);
GSStatus game_audio_callback(GameWorld *,GameServices *,TimerCallback);
GSStatus game_audio_shutdown(GameWorld *,GameServices *);
GSStatus game_audio_terminal(GameWorld *,GameServices *);
MusicClockResult game_audio_elapsed(const GameWorld *);
#endif
