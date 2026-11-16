#ifndef UGH_SDL_BACKEND_H
#define UGH_SDL_BACKEND_H
#include "../services.h"
#include <SDL3/SDL.h>
#include "opl3.h"

typedef struct GSSdlTime {
    uint64_t tick,retrace_tick,timer_tick,epoch_ns,suspended_at;
    /* Virtual time: retraces at 70 Hz; timer opportunities at their PIT interval. */
    uint64_t timer_clocks,now_ns;uint32_t pending_clocks;
    int suspended,paced;
} GSSdlTime;
void gs_time_init(GSSdlTime *,int);
uint64_t gs_time_tick_ns(uint64_t);
GSTimeOps gs_time_operations(void);

typedef struct GSSdlInput {
    uint8_t scans[4096],held[SDL_SCANCODE_COUNT];
    uint32_t scan_head,scan_tail,bios_head,bios_tail;
    uint16_t bios[256]; uint8_t editor,quit,focused;
    /* step7 binds the live queue-position/terminal witness. Zero is the existing
     * deterministic provider value, not an instruction to force exit zero. */
    uint16_t flush_reply;
    uint8_t present[2],buttons[2]; int16_t axes[4];
    GSBinding installed; SDL_Gamepad *pads[2];
} GSSdlInput;
void gs_input_init(GSSdlInput *);
void gs_input_close(GSSdlInput *);
GSStatus gs_input_key(GSSdlInput *,SDL_Scancode,int,int,uint32_t);
GSStatus gs_input_editor(GSSdlInput *,int);
GSStatus gs_input_focus_lost(GSSdlInput *);
GSStatus gs_input_gamepad(GSSdlInput *,unsigned,int,int16_t,int16_t,uint8_t);
uint16_t gs_input_axis_count(int16_t);
GSInputOps gs_input_operations(void);

typedef struct GSSdlVideo {
    uint8_t planes[4][65536],latches[4],seq[5],gc[9],crtc[25],attribute[21];
    uint8_t seq_index,gc_index,crtc_index,attribute_index,attribute_phase;
    uint8_t map_mask,read_plane,dac[768],dac_index,dac_component,retrace;
    SDL_Window *window; SDL_Renderer *renderer; SDL_Texture *texture;
} GSSdlVideo;
void gs_video_init(GSSdlVideo *);
GSStatus gs_video_window(GSSdlVideo *,int);
void gs_video_close(GSSdlVideo *);
void gs_video_rgb(const GSSdlVideo *,uint32_t [320*200]);
GSVideoOps gs_video_operations(void);

typedef struct GSSdlAudio {
    opl3_chip chip; SDL_AudioStream *stream;
    uint64_t remainder,frames,registers;
    uint8_t values[256];
    GSStatus (*clock_sink)(void *,GSClockDelivery);void *clock_context;
} GSSdlAudio;
GSStatus gs_audio_init(GSSdlAudio *,int);
void gs_audio_close(GSSdlAudio *);
GSStatus gs_audio_generate(GSSdlAudio *,int16_t *,unsigned);
GSAudioOps gs_audio_operations(void);

typedef struct GSSdlFiles {
    char path[4096]; uint8_t data[107]; uint16_t length;
    uint8_t exists,dirty; struct { uint16_t position; uint8_t open,write; } handles[32];
} GSSdlFiles;
GSStatus gs_files_init(GSSdlFiles *,const char *);
GSFilesOps gs_files_operations(void);
typedef struct GSSdlSeed { int fixed; GSSeedReply replay; } GSSdlSeed;
GSSeedOps gs_seed_operations(void);
GSLifecycleOps gs_lifecycle_operations(void);
typedef struct GSSdlStartup {
    GSSdlVideo *video;GSSdlTime *time;GSSdlAudio *audio;
    GSAudioOps audio_ops;GSTimeOps time_ops;GSVideoModeReply mode;
    GSBinding critical,timer;uint64_t audio_ns,presentations;
    uint16_t divisor;uint8_t mask,pit_phase,adlib,probe_reads,exited,exit_code;
} GSSdlStartup;
void gs_sdl_startup(GSSdlStartup *,GameServices *,GSSdlVideo *,GSSdlInput *,
    GSSdlTime *,GSSdlAudio *,GSSdlFiles *,GSSdlSeed *,int);
#endif
