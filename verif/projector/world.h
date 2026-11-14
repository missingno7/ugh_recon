/* Test-only composition vocabulary. No historical addresses or Regs here.
 * Binding/identity registries and unclassified-byte journals live in the verifier,
 * not in this world. These structures preserve storage, not an independent game.
 * Declared capacities are not ownership proofs: schema.json lists the bound
 * members. Conflicting legacy views stay unbound and use the raw write journal.
 */
#ifndef VERIF_PROJECTOR_WORLD_H
#define VERIF_PROJECTOR_WORLD_H
#include <stdint.h>

/* A registered resource/callback WORD identity, or an explicitly unresolved word.
 * Split timer targets remain split: the removal bug can splice target halves.
 */
typedef struct ProjectIdentity {uint32_t token;uint16_t unresolved;} ProjectIdentity;
typedef struct ProjectCursor {uint16_t index;ProjectIdentity bank;} ProjectCursor;
typedef struct ProjectChannel {
    uint32_t age,deadline;
    uint16_t repeats,length,sample_mode,sample_rate,sample_half_length;
    uint16_t reserved_word,sample_selector,sample_accumulator,volume;
    uint16_t voice_count,first_voice,step_q8,control;
    ProjectCursor start,cursor;
} ProjectChannel;
typedef struct ProjectVoice {
    uint8_t instrument[12];uint16_t volume,gain,owner,frequency;
} ProjectVoice;
typedef struct ProjectAudio {
    ProjectChannel channels[13];
    ProjectVoice live[9],displaced[9],scanned[9];uint8_t operator_index[9];
    uint16_t guard,rate,playing,section_loop,timer_period,timer_handle;
    uint16_t reserved_voices,current_channel,track_volume;
    uint32_t ticks,origin,scanned_ticks;
    ProjectCursor section_start,section_end;
    uint16_t fade_step,fade_duration,fade_start,fade_target,fade_scheduled,fade_handle;
    uint16_t devices,initialized,shutdown_latch,active_sample_voices;
    uint16_t delay_multiplier,calibration_remainder,record_offset,init_attempted_padding;
    uint16_t mixer_busy,dsp_port,dsp_vector,sample_mask;
    uint32_t bank_length;ProjectCursor instrument_map,bank;
    ProjectIdentity previous_calibration_offset,previous_calibration_bank;
    uint8_t init_attempted;
} ProjectAudio;
typedef struct ProjectTimerSlot {
    uint32_t interval,remaining;uint16_t due,handle;
    ProjectIdentity target_offset,target_bank;
} ProjectTimerSlot;
typedef struct ProjectTimers {
    ProjectTimerSlot slots[16];uint16_t by_handle[16],last_offset,installed,divisor;
    uint32_t quantum,earliest;
    ProjectIdentity previous_offset,previous_bank;
} ProjectTimers;
typedef struct ProjectActors {
    ProjectIdentity descriptor[16],callback_or_cursor[16],journey[16],overlay[16];
    uint16_t platform_or_done[16],source_platform[16],destination_platform[16];
    uint16_t source_index[16],destination_index[16];
    uint16_t x32[16],y32[16],pixel_x[16],pixel_y[16],previous_x[16],previous_y[16];
    uint16_t sprite[16],erase_sprite[16],erase_overlay[16],animation_offset[16],animation_countdown[16];
    /* Accepted combined storage views; do not split them into per-phase owners. */
    uint16_t phase_or_demo_cursor[16],motion_wait_or_demo_repeats[16];
    uint16_t vertical_or_demo_period[16],quick_delivery_ticks[16];
} ProjectActors;
typedef struct ProjectPlayers {
    uint16_t x32[2],y32[2],pixel_x[2],pixel_y[2],cached_x[2],cached_y[2],cached_sprite[2];
    uint16_t vx[2],vy[2],platform[2],sprite[2],impact[2],impact_limit[2],thrust[2];
    uint16_t carried[2],destination[2],fare[2],minimum_fare[2];
    uint16_t up[2],down[2],left[2],right[2],action[2];
    uint16_t animation_countdown[2],cycle_start[2],cycle_end[2];
} ProjectPlayers;
typedef struct ProjectEnemies {
    ProjectIdentity descriptor[6],callback[6],animation_or_drop[6];
    uint16_t platform[6],x32[6],y32[6],draw_x[6],draw_y[6],previous_x[6],previous_y[6];
    uint16_t sprite[6],erase_sprite[6],animation_offset[6],animation_countdown[6];
    uint16_t direction[6],speed[6],delay[6],counter[6],sound_handle[6];
} ProjectEnemies;
typedef struct ProjectItems {
    ProjectIdentity descriptor[12],callback[12];
    uint16_t x32[12],y32[12],draw_x[12],draw_y[12],previous_x[12],previous_y[12];
    uint16_t sprite[12],erase_sprite[12],motion_or_lifetime[12],vertical_step[12];
} ProjectItems;
typedef struct ProjectWeather {
    uint16_t fixed_y,surface_y,previous_y,byte_offset,frame;
    uint8_t phase,countdown,pending,rain_direction;
    uint16_t particle[193],previous_particle[193],modulo_four[193];
} ProjectWeather;
typedef struct ProjectConfiguration {uint16_t players,player_bytes,control_mode[2];} ProjectConfiguration;
typedef struct ProjectSession {
    uint16_t level,timer,fade_level,fade_step;uint32_t score;
    uint8_t lives,multiplier,completion;
    uint16_t level_record[13];uint8_t tile_map[320];
} ProjectSession;
typedef struct ProjectPlatforms {
    /* The admitted native passenger view has ten slots. Further raw indexed
     * storage is not assigned here; it remains in the unclassified journal. */
    uint16_t left[10],right[10],height[10],arrival[10],waiting[10],spawn[10],icon[10],occupant[10];
} ProjectPlatforms;
typedef struct ProjectInput {
    uint8_t latest,current,previous,change,sequence_index,enabled_axes;
    uint16_t sample_limit,present[2],buttons[2],left[2],right[2],up[2],down[2];
} ProjectInput;
typedef struct ProjectVideo {
    ProjectCursor draw,displayed,background,fixed;
    uint16_t height,copy_bytes;uint8_t base_palette[768],faded_palette[768];
} ProjectVideo;
typedef struct ProjectFrontEnd {
    uint8_t scores[107],password[20],name[13],stride;uint16_t file_handle;
} ProjectFrontEnd;
typedef struct GameWorld {
    ProjectAudio audio;ProjectTimers timers;ProjectActors actors;ProjectPlayers players;
    ProjectEnemies enemies;ProjectItems items;ProjectWeather weather;
    ProjectConfiguration configuration;ProjectSession session;ProjectInput input;
    ProjectVideo video;ProjectFrontEnd front_end;uint16_t random[4];ProjectPlatforms platforms;
} GameWorld;

/* Explicit test service state. These are delivered device effects, not a second
 * implementation of the platform algorithms. Serialization maps members, not
 * the native struct's padding, to the historical device layout. */
typedef struct ProjectRun {uint32_t value,repeat;} ProjectRun;
typedef struct ProjectScript {
    uint32_t port,count,cursor,used;ProjectRun runs[128];uint32_t cycles,cycles_left;
} ProjectScript;
typedef struct ProjectIrq {uint32_t segment,offset,skip,irq,clocks;} ProjectIrq;
typedef struct ProjectFile {uint8_t name[64],data[8192];uint32_t exists,length;} ProjectFile;
typedef struct ProjectHandle {uint32_t active,file,position,mode;} ProjectHandle;
typedef struct ProjectVgaService {
    uint8_t plane[4][65536],latch[4];
    uint8_t seq_index,map_mask,gc_index,read_map,gc[9],seq[5],crtc[25],attr[21],dac[768];
    uint8_t crtc_index,attr_index,attr_phase,dac_index,dac_component;
} ProjectVgaService;
typedef struct ProjectAudioService {uint8_t address,registers[256];} ProjectAudioService;
typedef struct ProjectBusService {
    uint8_t pic_mask,dma_flip,dma_mode,dma_mask,dma_page,pit_phase,pit_command;
    uint16_t dma_address,dma_count,pit_divisor;uint32_t clocks,irq_count,irq_cursor;
    ProjectIrq irqs[64];
} ProjectBusService;
typedef struct ProjectInputService {uint32_t count;ProjectScript scripts[16];} ProjectInputService;
typedef struct ProjectFileService {
    ProjectFile files[8];ProjectHandle handles[32];uint32_t io_limit,error,error_skip;
} ProjectFileService;
typedef struct ProjectLifetimeService {uint8_t mode,page,columns,exit_code,exited;} ProjectLifetimeService;
typedef struct ServiceState {
    ProjectVgaService video;ProjectAudioService audio;ProjectBusService bus;
    ProjectInputService input;ProjectFileService files;ProjectLifetimeService lifetime;
    uint32_t error;
} ServiceState;
typedef struct ProjectEvent {uint32_t kind,port,width,value;} ProjectEvent;
#endif
