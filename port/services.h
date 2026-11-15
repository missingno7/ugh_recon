#ifndef UGH_PORT_SERVICES_H
#define UGH_PORT_SERVICES_H
#include <stddef.h>
#include <stdint.h>

/* Synchronous game-thread capabilities. A failure stops at the consumed prefix;
 * services never invoke game logic from a window or audio callback. */
typedef enum GSStatus { GS_OK, GS_EMPTY, GS_UNSUPPORTED, GS_INVALID,
    GS_IO_ERROR, GS_QUIT, GS_OVERFLOW } GSStatus;
typedef uint64_t GSResourceId;
typedef struct GSBinding { uint64_t token; } GSBinding;
typedef enum GSResourceClass { GS_IMMUTABLE=1, GS_MUTABLE, GS_OPAQUE_MUTABLE,
    GS_SCRATCH } GSResourceClass;
typedef struct GSBytes { const uint8_t *data; size_t size; } GSBytes;
typedef struct GSMutableBytes { uint8_t *data; size_t size; } GSMutableBytes;

typedef enum GSVideoRoute {
    GS_SEQ_INDEX, GS_SEQ_DATA, GS_GC_INDEX, GS_GC_DATA,
    GS_CRTC_INDEX, GS_CRTC_DATA, GS_ATTRIBUTE_WRITE, GS_ATTRIBUTE_READ
} GSVideoRoute;
typedef enum GSReadRole { GS_SOURCE_READ, GS_COLLISION_READ } GSReadRole;
typedef enum GSDacKind { GS_DAC_SELECT, GS_DAC_COMPONENT } GSDacKind;
typedef struct GSDacWrite { GSDacKind kind; uint8_t value; } GSDacWrite;
/* Cells address the provider's complete four-lane indexed store. Producers make
 * their specified word reductions; the provider does not clip to the viewport. */
typedef struct GSVideoOps {
    GSStatus (*control_write)(void *,GSVideoRoute,uint8_t);
    GSStatus (*control_read)(void *,GSVideoRoute,uint8_t *);
    GSStatus (*read)(void *,uint16_t,GSReadRole,uint8_t *);
    GSStatus (*store)(void *,uint16_t,uint8_t);
    GSStatus (*store_word)(void *,uint16_t,uint16_t);
    GSStatus (*copy)(void *,uint16_t,uint16_t,uint8_t *);
    GSStatus (*water_mark)(void *,uint16_t,uint8_t *);
    GSStatus (*dac)(void *,GSDacWrite);
    GSStatus (*retrace_level)(void *,uint8_t *);
    GSStatus (*present)(void *);
    /* step 7: pending: noncanonical pixel continuation and external control. */
    GSStatus (*compatibility)(void *);
} GSVideoOps;

typedef enum GSQueueOp { GS_QUEUE_PEEK, GS_QUEUE_TAKE } GSQueueOp;
typedef enum GSInputPollCut { GS_INPUT_SCAN,GS_INPUT_WAIT } GSInputPollCut;
typedef enum GSVectorOp { GS_VECTOR_CAPTURE, GS_VECTOR_INSTALL, GS_VECTOR_RESTORE } GSVectorOp;
typedef struct GSJoystickCounts {
    uint16_t counts[4],latched[4],remaining;
} GSJoystickCounts;
typedef struct GSInputOps {
    GSStatus (*scan)(void *,uint8_t *);
    GSStatus (*acknowledge)(void *);
    GSStatus (*queue)(void *,GSQueueOp,uint16_t *);
    GSStatus (*flush)(void *,uint16_t *);
    GSStatus (*vector)(void *,GSVectorOp,GSBinding,GSBinding *);
    GSStatus (*joystick_start)(void *,uint8_t);
    GSStatus (*presence)(void *,uint8_t *);
    GSStatus (*buttons)(void *,unsigned,uint16_t *);
    GSStatus (*counts)(void *,uint16_t,uint8_t,GSJoystickCounts *);
    GSStatus (*pump)(void *,GSInputPollCut);
} GSInputOps;

typedef struct GSRegisterWrite { uint8_t reg,value; } GSRegisterWrite;
typedef enum GSClockDelivery { GS_CLOCK_TIMER, GS_CLOCK_BIOS_CHAIN } GSClockDelivery;
typedef enum GSCalibrationPhase { GS_CALIBRATION_BEGIN,GS_CALIBRATION_WAIT,GS_CALIBRATION_FINISH } GSCalibrationPhase;
typedef struct GSCalibrationReply {uint16_t remainder,progress;uint8_t marker;} GSCalibrationReply;
typedef enum GSTimerLifetimeKind { GS_TIMER_READ_BINDING,GS_TIMER_BIND_HANDLER,
    GS_TIMER_BIND_SAVED,GS_TIMER_RESET_COUNTER,GS_TIMER_DELIVER_SAVED } GSTimerLifetimeKind;
typedef struct GSTimerLifetimeRequest {
    GSTimerLifetimeKind kind;GSBinding binding;uint8_t command,low,high,enable_interrupts;
} GSTimerLifetimeRequest;
typedef struct GSAudioOps {
    GSStatus (*opl)(void *,GSRegisterWrite);
    GSStatus (*status)(void *,uint8_t *); /* step 7: pending probe prefix */
    GSStatus (*advance)(void *,uint64_t);
    /* Delivered on the game thread to a later engine adapter, never synthesized
     * as an additional guard-clock increment. step 7: pending. */
    GSStatus (*clock)(void *,GSClockDelivery);
    /* step 7: pending: calibration and timer lifetime adapter, including saved
     * external role and low/high counter programming, at their matching cuts. */
    GSStatus (*calibration)(void *,GSCalibrationPhase,GSCalibrationReply *);
    GSStatus (*timer_lifetime)(void *,GSTimerLifetimeRequest,GSBinding *);
} GSAudioOps;
/* step 7: pending: lifetime calibration/vector prefix must supply these witnesses
 * at its accepted cuts; they are not synthesized from audio sample count. */
typedef enum GSEventKind { GS_RETRACE_INACTIVE, GS_RETRACE_ACTIVE, GS_TIMER_OPPORTUNITY,
    GS_INPUT_OPPORTUNITY } GSEventKind;
typedef struct GSEvent { GSEventKind kind; uint64_t tick,nanoseconds; } GSEvent;
typedef struct GSTimeOps {
    /* The engine requests the cut; this source does not invent a cross-family
     * callback order. Retrace/timer opportunities advance independent70Hz
     * timelines; pacing uses their maximum. Timer accounting stays engine-side. */
    GSStatus (*deliver)(void *,GSEventKind,GSEvent *);
    GSStatus (*suspend)(void *,int);
    GSStatus (*pace)(void *);
} GSTimeOps;

/* Encoded score bytes are owned/complemented by the engine. A short read never
 * pads the caller's retained tail. Open handles stay logical even after an
 * atomic disk persistence; the engine's omitted close must not be invented. */
typedef struct GSFileReply { uint16_t value; uint8_t failed; } GSFileReply;
typedef struct GSFilesOps {
    GSStatus (*open_scores)(void *,int,GSFileReply *);
    GSStatus (*read)(void *,uint16_t,uint8_t *,uint16_t,GSFileReply *);
    GSStatus (*write)(void *,uint16_t,const uint8_t *,uint16_t,GSFileReply *);
    GSStatus (*close)(void *,uint16_t,GSFileReply *);
    GSStatus (*persist)(void *);
} GSFilesOps;
typedef struct GSResourceOps {
    GSStatus (*view)(void *,GSResourceId,GSBytes *,GSResourceClass *);
    GSStatus (*mutable_view)(void *,GSResourceId,GSMutableBytes *);
} GSResourceOps;
typedef struct GSSeedReply { uint8_t hours,minutes,seconds,hundredths; } GSSeedReply;
typedef struct GSSeedOps { GSStatus (*read)(void *,GSSeedReply *); } GSSeedOps;
/* Provider lifetime only: native lifecycle retains its peer orchestration. */
typedef enum GSLifecycleAction { GS_LIFECYCLE_START, GS_LIFECYCLE_STOP,
    GS_LIFECYCLE_VIDEO_QUERY, GS_LIFECYCLE_VIDEO_SET,GS_LIFECYCLE_VIDEO_RESTORE,
    GS_LIFECYCLE_CPU_QUERY,GS_LIFECYCLE_TERMINAL } GSLifecycleAction;
typedef enum GSLifecycleBindingRole { GS_BIND_CRITICAL_ERROR_FAIL } GSLifecycleBindingRole;
typedef struct GSLifecycleRequest { GSLifecycleAction action; uint8_t value; } GSLifecycleRequest;
typedef struct GSLifecycleOps {
    /* step 7: pending: lifecycle prefix/critical-error/external binding adapter. */
    GSStatus (*request)(void *,GSLifecycleRequest,uint8_t *);
    GSStatus (*binding)(void *,GSLifecycleBindingRole,GSVectorOp,GSBinding,GSBinding *); /* step 7: pending */
} GSLifecycleOps;
typedef struct GameServices {
    void *video_context,*input_context,*audio_context,*time_context;
    void *files_context,*resources_context,*seed_context,*lifecycle_context;
    GSVideoOps video; GSInputOps input; GSAudioOps audio; GSTimeOps time;
    GSFilesOps files; GSResourceOps resources; GSSeedOps seed; GSLifecycleOps lifecycle;
} GameServices;
#endif
