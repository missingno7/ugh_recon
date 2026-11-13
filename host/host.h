#ifndef UGH_HOST_H
#define UGH_HOST_H
#include "platform.h"
#include <SDL3/SDL.h>
#include <stdio.h>
#define MAX_FRAMES 16384
#define MAX_INPUT 128
typedef struct Wave { unsigned count; uint8_t bytes[128]; } Wave;
typedef struct FrameInput {
    unsigned count; uint8_t scans[MAX_INPUT];
    int cycle_set; unsigned cycle_count; uint8_t cycle[MAX_INPUT];
    int joy_set; Wave joy;
    unsigned joy_count; Wave *joy_cycles;
} FrameInput;
typedef struct Scenario {
    char entry[128], end[16], password[21];
    unsigned frames,players; int adlib,blank_scores,score_set;
    uint32_t score; unsigned bios_count; uint32_t bios[128];
    Wave joystick; FrameInput *input;
} Scenario;
extern Scenario scenario;
extern unsigned host_frame,host_limit;
extern int host_headless,host_scripted,host_digests,host_quit;
extern const char *host_shot;
void host_fail(const char *why);
void scenario_read(const char *path);
void scenario_defaults(void);
void scenario_fixture(void);
void scenario_load_frame(unsigned frame,void (*enqueue)(uint8_t));
int scenario_cycle_scan(uint8_t *scan);
InputScript *host_script(uint16_t port);
void host_values(uint16_t port,const uint32_t *values,unsigned count,uint32_t cycles);
void host_wave(const Wave *wave);
void host_render(uint32_t pixels[320*200]);
int host_video_init(int scale);
void host_present(void);
void host_save_shot(const char *path);
void host_video_close(void);
int host_audio_init(int enabled,const char *wav);
void host_audio_advance(uint64_t nanoseconds);
void host_audio_out(uint16_t port,unsigned size,uint32_t value);
void host_audio_close(void);
void host_digest(Regs *r,const char *terminal);
void host_digest_init(void);
void host_digest_close(void);
void host_sha256(const void *p,unsigned size,char hex[65]);
void host_input_pump(void);
void host_enqueue(uint8_t scan);
int host_take_scan(uint8_t *scan);
int host_live_interrupt(uint8_t n,Regs *r);
void host_input_release(void);
void host_gamepad_init(void);
void host_input_close(void);
/* Generated address/name table, from the rebuilt symbols, for fixture entries. */
typedef struct HostSymbol { const char *name; uint16_t segment,offset; } HostSymbol;
extern const HostSymbol host_symbols[];
extern const unsigned host_symbol_count;
HostSymbol host_symbol(const char *name);
#endif
