#ifndef UGH_TEST_BACKEND_H
#define UGH_TEST_BACKEND_H
#include "../services.h"

/* Test fixture storage, never a game-state owner. Effects are synchronous and
 * ordered; a recorder may attach without changing service behaviour. */
typedef enum GSTestEffectKind { GST_CONTROL_WRITE,GST_CONTROL_READ,GST_DAC,
    GST_SCAN,GST_ACK,GST_JOYSTICK_START,GST_JOYSTICK_SAMPLE,GST_QUEUE,
    GST_VECTOR,GST_OPL,GST_PIT_COMMAND,GST_PIT_COUNTER,GST_MASK_WRITE,
    GST_MASK_READ,GST_IRQ,GST_FILE,GST_SEED,GST_VIDEO_MODE,GST_TERMINAL,
    GST_EVENT,GST_PRESENT,GST_FLUSH,GST_AUDIO_STATUS,GST_CALIBRATION,
    GST_LIFECYCLE_BINDING,GST_CPU_QUERY } GSTestEffectKind;
typedef struct GSTestEffect {GSTestEffectKind kind;uint32_t a,b,c;} GSTestEffect;
typedef void (*GSTestRecorder)(void *,GSTestEffect);
typedef struct GSTestRun {uint32_t value,repeat;} GSTestRun;
typedef struct GSTestStream {
    GSTestRun runs[128];uint32_t count,cursor,used,cycles,left;
} GSTestStream;
typedef struct GSTestBackend {
    uint8_t planes[4][65536],latches[4],seq[5],gc[9],crtc[25],attribute[21];
    uint8_t seq_index,gc_index,crtc_index,attribute_index,attribute_phase;
    uint8_t map_mask,read_plane,dac[768],dac_index,dac_component,retrace;
    GSTestStream scans,bios,joystick,retrace_samples;
    GSBinding keyboard;uint16_t flush_reply;
    uint8_t present[2],buttons[2];uint16_t axes[4];
    uint8_t opl[256],opl_index,pic_mask,pit_command,pit_phase;
    uint16_t pit_divisor;uint32_t clocks;
    uint64_t retrace_tick,timer_tick,audio_ns,presents;int suspended;
    uint8_t scores[8192],exists,dirty;
    uint32_t length,io_limit,file_error,file_error_skip;
    struct {uint32_t active,position,mode;} handles[32];
    uint8_t video_mode,video_columns,video_page,exited,exit_code;
    GSSeedReply seed;
    GSTestRecorder recorder;void *record_context;
    GSResourceOps resources;void *resource_context;
    uint8_t startup_enabled,adlib_present,probe_reads,live_seed;
    GSCalibrationReply calibration_reply;
    GSBinding critical,timer_binding;
} GSTestBackend;
void gs_test_init(GSTestBackend *);
GameServices gs_test_services(GSTestBackend *);
/* Explicit production/startup profile. Legacy service tests retain their
 * Unsupported replies unless the embedding application selects this profile. */
void gs_test_startup(GSTestBackend *,int);
/* Fixtures schedule future external deliveries at service reads, not held keys.
 * Flush retires the current BIOS queue witness, not future scripted deliveries.
 * Raw scans preserve E0 and break bytes. Empty streams return Empty. */
GSStatus gs_test_stream(GSTestStream *,const GSTestRun *,size_t,uint32_t);
GSStatus gs_test_gamepad(GSTestBackend *,unsigned,int,int16_t,int16_t,uint8_t);
uint16_t gs_test_axis_count(int16_t);
uint64_t gs_test_tick_ns(uint64_t);
#endif
