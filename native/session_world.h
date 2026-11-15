#ifndef NATIVE_SESSION_WORLD_H
#define NATIVE_SESSION_WORLD_H
#include "session.h"
#include "demo_presentation.h"
/* The two retained words are physical allocations, not derived results.
 * All run/player/object/HUD/password fields are borrowed live from their owners. */
typedef struct NativeSessionWorld {
 uint16_t coordinate_scale_scratch, demo_exit_code;
} NativeSessionWorld;
NativeSessionWorld *native_session_world(void);
/* Invocation-local native continuation. Nested demo wrappers have independent
 * cursors; they borrow the same live exit/fade/actor/resource fields. */
typedef struct NativeDemoContinuation {
 DemoPresentationCursor cursor;
 DemoPresentationInput observed;
 DemoPresentationAction pending_action;
 int active,pending,completed;
} NativeDemoContinuation;
/* Observations are ephemeral reads. No callback republishes a parent snapshot.
 * Status is supplied by the binding; zero acknowledges, nonzero stops at once.
 * The optional diagnostic hook belongs only to the verification provider. */
typedef SessionWorld (*SessionObserver)(void *context,SessionPhase phase);
typedef int (*SessionExecutor)(void *context,SessionRequest request);
typedef int (*SessionDiagnostic)(void *context,const SessionProcess *process);
typedef struct SessionServices {
 SessionObserver observe;
 SessionExecutor execute;
 SessionDiagnostic diagnostic;
} SessionServices;
int session_world_run(const SessionServices *services,void *context);
#endif
