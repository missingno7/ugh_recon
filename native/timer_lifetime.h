#ifndef NATIVE_TIMER_LIFETIME_H
#define NATIVE_TIMER_LIFETIME_H
#include "timer.h"

/* Provider-issued identity, not a machine pointer. The provider retains the
 * external binding even when its role is not one the current backend accepts. */
typedef enum TimerExternalRole { TIMER_EXTERNAL_OTHER, TIMER_EXTERNAL_BIOS } TimerExternalRole;
typedef struct TimerExternalBinding { TimerExternalRole role; uint32_t identity; } TimerExternalBinding;
typedef struct TimerLifetime { TimerExternalBinding saved; } TimerLifetime;

typedef enum TimerLifetimeKind {
    TIMER_LIFETIME_NONE, TIMER_LIFETIME_READ_BINDING, TIMER_LIFETIME_BIND_TIMER,
    TIMER_LIFETIME_BIND_SAVED, TIMER_LIFETIME_RESET_PIT, TIMER_LIFETIME_DELIVER
} TimerLifetimeKind;
typedef struct TimerLifetimeRequest {
    TimerLifetimeKind kind;
    TimerExternalBinding binding;
    unsigned enable_interrupts;
    uint8_t pit_command, pit_low, pit_high;
} TimerLifetimeRequest;

void timer_lifetime_install(TimerState *state, TimerLifetimeRequest *request);
void timer_lifetime_restore(TimerState *state, const TimerLifetime *life, TimerLifetimeRequest *request);
void timer_lifetime_chain(const TimerLifetime *life, TimerLifetimeRequest *request);
/* Consume only a successful, matching service. Failed services leave their
 * request outstanding and retain the already-published prefix. */
int timer_lifetime_consume(TimerState *state, TimerLifetime *life,
    TimerLifetimeRequest *request, TimerLifetimeKind completed, TimerExternalBinding reply);

typedef enum TimerApiKind { TIMER_API_REGISTER, TIMER_API_REMOVE } TimerApiKind;
typedef struct TimerApiRequest {
    TimerApiKind kind;
    TimerCallback callback;
    uint32_t interval;
    uint16_t handle;
} TimerApiRequest;
typedef struct TimerApiResult { uint16_t handle; uint32_t minimum; } TimerApiResult;
/* Admitted scheduler API only; rejected requests make no state changes. */
int timer_lifetime_apply(TimerState *state, const TimerApiRequest *request, TimerApiResult *result);
#endif
