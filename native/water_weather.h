#ifndef NATIVE_WATER_WEATHER_H
#define NATIVE_WATER_WEATHER_H
#include <stddef.h>
#include <stdint.h>
/* Working projections of existing level globals and particle arrays, never a
 * second owner. Surface Y is the shared value read by craft/passengers/render. */
typedef struct WaterWeatherState {
 uint16_t fixed_y,surface_y,previous_y,byte_position,frame;
 uint8_t countdown,phase,restore_pending;
} WaterWeatherState;
typedef struct WeatherParticle {uint16_t position,previous,modulo_four;} WeatherParticle;
typedef struct WaterWeatherInputs {uint16_t increment;uint8_t row_stride,direction;} WaterWeatherInputs;
typedef enum WeatherField {WW_FIXED_Y,WW_SURFACE_Y,WW_PREVIOUS_Y,WW_BYTE_POSITION,
 WW_FRAME,WW_COUNTDOWN,WW_PHASE,WW_PENDING,WW_PARTICLE,WW_PREVIOUS,WW_MODULO} WeatherField;
typedef enum WeatherActionKind {WW_STORE,WW_MARK_ROW,WW_RESTORE_ROW,WW_FRAME_TAIL,
 WW_RANDOM,WW_RESPAWN,WW_MASK,WW_PIXEL,WW_COPY,WW_DONE} WeatherActionKind;
typedef struct WeatherAction {WeatherActionKind kind;WeatherField field;uint16_t value,position;} WeatherAction;
typedef struct WeatherResult {WeatherAction actions[10];size_t count;} WeatherResult;
typedef struct WeatherFrameCursor {uint8_t colors[5],mask;unsigned plane,column;int mask_due,finished;} WeatherFrameCursor;
WeatherResult water_weather_advance(WaterWeatherState *state,WaterWeatherInputs inputs);
WeatherResult water_weather_marked(WaterWeatherState *state);
WeatherResult water_weather_prepare(WaterWeatherState *state,WaterWeatherInputs inputs);
WeatherResult weather_particle_advance(WeatherParticle *particle,uint16_t boundary,uint8_t direction,int alternate);
WeatherResult weather_particle_spawn(WeatherParticle *particle,uint16_t random_value,WaterWeatherInputs inputs);
WeatherResult weather_particle_request(uint16_t surface_y);
WeatherResult weather_particle_draw(const WeatherParticle *particle);
WeatherResult weather_particle_restore(const WeatherParticle *particle);
uint16_t weather_random_bound(uint16_t surface_y);
uint16_t weather_first_particle(uint16_t surface_y,int extra);
uint16_t weather_previous_particle(uint16_t byte_index);
int weather_more_particles(uint16_t byte_index);
uint8_t weather_plane_mask(uint16_t modulo_four);
void weather_frame_begin(WeatherFrameCursor *cursor,const uint8_t colors[5],uint8_t mask);
/* frame0..2, complete320-cell color recipe; no sprite or instruction bytes. */
uint8_t weather_frame_color(unsigned frame,unsigned cell,const uint8_t colors[5]);
WeatherAction weather_frame_next(WeatherFrameCursor *cursor,unsigned frame);
#endif
