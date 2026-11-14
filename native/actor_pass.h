#ifndef NATIVE_ACTOR_PASS_H
#define NATIVE_ACTOR_PASS_H
#include <stdint.h>
/* Borrow the live actor store. A callback is reloaded for every visit; this
 * continuation owns neither actors nor their phase-dependent cursor words. */
typedef enum ActorCallback {
    ACTOR_CALLBACK_UNSUPPORTED=0,
    ACTOR_CALLBACK_ReadPassengerJourneyLeg,
    ACTOR_CALLBACK_WaitForPassengerPlatform,
    ACTOR_CALLBACK_PlacePassengerOnPlatform,
    ACTOR_CALLBACK_AnimatePassengerArrival,
    ACTOR_CALLBACK_BeginPassengerPlatformWait,
    ACTOR_CALLBACK_UpdatePassengerPlatformWait,
    ACTOR_CALLBACK_BeginPassengerDestinationDisplay,
    ACTOR_CALLBACK_UpdatePassengerDestinationDisplay,
    ACTOR_CALLBACK_BeginPassengerQuestionDisplay,
    ACTOR_CALLBACK_UpdatePassengerQuestionDisplay,
    ACTOR_CALLBACK_BeginPassengerApproach,
    ACTOR_CALLBACK_UpdatePassengerApproach,
    ACTOR_CALLBACK_BoardWaterbornePassenger,
    ACTOR_CALLBACK_BoardPassenger,
    ACTOR_CALLBACK_UpdateCarriedPassenger,
    ACTOR_CALLBACK_DeliverPassenger,
    ACTOR_CALLBACK_WalkPassengerToExit,
    ACTOR_CALLBACK_BeginPassengerDeparture,
    ACTOR_CALLBACK_AnimatePassengerDeparture,
    ACTOR_CALLBACK_IgnoreActorState,
    ACTOR_CALLBACK_BeginStonePickupWait,
    ACTOR_CALLBACK_UpdateStonePickupWait,
    ACTOR_CALLBACK_AttachStoneToPlayer,
    ACTOR_CALLBACK_WaitForStoneRelease,
    ACTOR_CALLBACK_ThrowCarriedStone,
    ACTOR_CALLBACK_UpdateThrownStone,
    ACTOR_CALLBACK_BeginPassengerResurfacing,
    ACTOR_CALLBACK_UpdatePassengerResurfacing,
    ACTOR_CALLBACK_BeginPassengerSinking,
    ACTOR_CALLBACK_UpdatePassengerSinking,
    ACTOR_CALLBACK_BeginPassengerFloating,
    ACTOR_CALLBACK_UpdatePassengerFloating,
    ACTOR_CALLBACK_UpdateFloatingDestinationDisplay,
    ACTOR_CALLBACK_UpdateFloatingQuestionDisplay,
    ACTOR_CALLBACK_UpdateFloatingPassengerApproach,
    ACTOR_CALLBACK_IgnoreWaterbornePassengerState,
    ACTOR_CALLBACK_COUNT
} ActorCallback;
typedef enum ActorPassAction { ACTOR_PASS_DONE, ACTOR_PASS_CALL,
    ACTOR_PASS_UNSUPPORTED, ACTOR_PASS_LIMIT } ActorPassAction;
typedef struct ActorPass { uint16_t cursor; uint32_t remaining; } ActorPass;
void actor_pass_begin(ActorPass *pass);
ActorPassAction actor_pass_select(const ActorPass *pass,uint16_t descriptor,ActorCallback callback);
void actor_pass_resume(ActorPass *pass,uint16_t live_cursor);
/* The unexplained standalone return has no demonstrated gameplay role. */
void actor_reserved_return(void);
#endif
