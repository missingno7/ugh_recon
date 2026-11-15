#include "platform.h"
#ifndef ENEMIES_BORROWER
#define ENEMIES_BORROWER ENEMIES_BORROW_ACTORS
#endif
#include "enemies_borrow.h"
#include "platform.h"
#ifndef ACTORS_BORROWER
#define ACTORS_BORROWER ACTORS_BORROW_ACTORS
#endif
#include "actors_borrow.h"
#include "platform.h"
#ifndef PLATFORMS_BORROWER
#define PLATFORMS_BORROWER PLATFORMS_BORROW_ACTORS
#endif
#include "platforms_borrow.h"
#include "platform.h"
#ifndef PLAYER_BORROWER
#define PLAYER_BORROWER PLAYER_BORROW_ACTORS
#endif
#include "player_borrow.h"
#include "platform.h"
#ifndef RUN_BORROWER
#define RUN_BORROWER RUN_BORROW_ACTORS
#endif
#include "run_borrow.h"
#include "ugh.h"
#include "../actor_pass.h"
static ActorCallback callback_identity(uint16_t word) {
    if (word==G(ReadPassengerJourneyLeg)) return ACTOR_CALLBACK_ReadPassengerJourneyLeg;
    if (word==G(WaitForPassengerPlatform)) return ACTOR_CALLBACK_WaitForPassengerPlatform;
    if (word==G(PlacePassengerOnPlatform)) return ACTOR_CALLBACK_PlacePassengerOnPlatform;
    if (word==G(AnimatePassengerArrival)) return ACTOR_CALLBACK_AnimatePassengerArrival;
    if (word==G(BeginPassengerPlatformWait)) return ACTOR_CALLBACK_BeginPassengerPlatformWait;
    if (word==G(UpdatePassengerPlatformWait)) return ACTOR_CALLBACK_UpdatePassengerPlatformWait;
    if (word==G(BeginPassengerDestinationDisplay)) return ACTOR_CALLBACK_BeginPassengerDestinationDisplay;
    if (word==G(UpdatePassengerDestinationDisplay)) return ACTOR_CALLBACK_UpdatePassengerDestinationDisplay;
    if (word==G(BeginPassengerQuestionDisplay)) return ACTOR_CALLBACK_BeginPassengerQuestionDisplay;
    if (word==G(UpdatePassengerQuestionDisplay)) return ACTOR_CALLBACK_UpdatePassengerQuestionDisplay;
    if (word==G(BeginPassengerApproach)) return ACTOR_CALLBACK_BeginPassengerApproach;
    if (word==G(UpdatePassengerApproach)) return ACTOR_CALLBACK_UpdatePassengerApproach;
    if (word==G(BoardWaterbornePassenger)) return ACTOR_CALLBACK_BoardWaterbornePassenger;
    if (word==G(BoardPassenger)) return ACTOR_CALLBACK_BoardPassenger;
    if (word==G(UpdateCarriedPassenger)) return ACTOR_CALLBACK_UpdateCarriedPassenger;
    if (word==G(DeliverPassenger)) return ACTOR_CALLBACK_DeliverPassenger;
    if (word==G(WalkPassengerToExit)) return ACTOR_CALLBACK_WalkPassengerToExit;
    if (word==G(BeginPassengerDeparture)) return ACTOR_CALLBACK_BeginPassengerDeparture;
    if (word==G(AnimatePassengerDeparture)) return ACTOR_CALLBACK_AnimatePassengerDeparture;
    if (word==G(IgnoreActorState)) return ACTOR_CALLBACK_IgnoreActorState;
    if (word==G(BeginStonePickupWait)) return ACTOR_CALLBACK_BeginStonePickupWait;
    if (word==G(UpdateStonePickupWait)) return ACTOR_CALLBACK_UpdateStonePickupWait;
    if (word==G(AttachStoneToPlayer)) return ACTOR_CALLBACK_AttachStoneToPlayer;
    if (word==G(WaitForStoneRelease)) return ACTOR_CALLBACK_WaitForStoneRelease;
    if (word==G(ThrowCarriedStone)) return ACTOR_CALLBACK_ThrowCarriedStone;
    if (word==G(UpdateThrownStone)) return ACTOR_CALLBACK_UpdateThrownStone;
    if (word==G(BeginPassengerResurfacing)) return ACTOR_CALLBACK_BeginPassengerResurfacing;
    if (word==G(UpdatePassengerResurfacing)) return ACTOR_CALLBACK_UpdatePassengerResurfacing;
    if (word==G(BeginPassengerSinking)) return ACTOR_CALLBACK_BeginPassengerSinking;
    if (word==G(UpdatePassengerSinking)) return ACTOR_CALLBACK_UpdatePassengerSinking;
    if (word==G(BeginPassengerFloating)) return ACTOR_CALLBACK_BeginPassengerFloating;
    if (word==G(UpdatePassengerFloating)) return ACTOR_CALLBACK_UpdatePassengerFloating;
    if (word==G(UpdateFloatingDestinationDisplay)) return ACTOR_CALLBACK_UpdateFloatingDestinationDisplay;
    if (word==G(UpdateFloatingQuestionDisplay)) return ACTOR_CALLBACK_UpdateFloatingQuestionDisplay;
    if (word==G(UpdateFloatingPassengerApproach)) return ACTOR_CALLBACK_UpdateFloatingPassengerApproach;
    if (word==G(IgnoreWaterbornePassengerState)) return ACTOR_CALLBACK_IgnoreWaterbornePassengerState;
    return ACTOR_CALLBACK_UNSUPPORTED;
}
/* Direct calls to accepted native entry adapters. Preserve the historical
 * near frame and CS publication without any resolver or dispatcher round trip. */
static int invoke_actor(ActorCallback callback,Regs *r) {
    uint16_t saved_cs=r->cs;
    r->sp=(uint16_t)(r->sp-2);
    enemies_write16(r->ss,r->sp,(uint16_t)(G(DispatchActorUpdates)+0x10));
    if (r->cs!=GAME_SEG) return UGH_BAD_CALLBACK;
    int status;
    switch (callback) {
    case ACTOR_CALLBACK_ReadPassengerJourneyLeg: status=c_ReadPassengerJourneyLeg(r); break;
    case ACTOR_CALLBACK_WaitForPassengerPlatform: status=c_WaitForPassengerPlatform(r); break;
    case ACTOR_CALLBACK_PlacePassengerOnPlatform: status=c_PlacePassengerOnPlatform(r); break;
    case ACTOR_CALLBACK_AnimatePassengerArrival: status=c_AnimatePassengerArrival(r); break;
    case ACTOR_CALLBACK_BeginPassengerPlatformWait: status=c_BeginPassengerPlatformWait(r); break;
    case ACTOR_CALLBACK_UpdatePassengerPlatformWait: status=c_UpdatePassengerPlatformWait(r); break;
    case ACTOR_CALLBACK_BeginPassengerDestinationDisplay: status=c_BeginPassengerDestinationDisplay(r); break;
    case ACTOR_CALLBACK_UpdatePassengerDestinationDisplay: status=c_UpdatePassengerDestinationDisplay(r); break;
    case ACTOR_CALLBACK_BeginPassengerQuestionDisplay: status=c_BeginPassengerQuestionDisplay(r); break;
    case ACTOR_CALLBACK_UpdatePassengerQuestionDisplay: status=c_UpdatePassengerQuestionDisplay(r); break;
    case ACTOR_CALLBACK_BeginPassengerApproach: status=c_BeginPassengerApproach(r); break;
    case ACTOR_CALLBACK_UpdatePassengerApproach: status=c_UpdatePassengerApproach(r); break;
    case ACTOR_CALLBACK_BoardWaterbornePassenger: status=c_BoardWaterbornePassenger(r); break;
    case ACTOR_CALLBACK_BoardPassenger: status=c_BoardPassenger(r); break;
    case ACTOR_CALLBACK_UpdateCarriedPassenger: status=c_UpdateCarriedPassenger(r); break;
    case ACTOR_CALLBACK_DeliverPassenger: status=c_DeliverPassenger(r); break;
    case ACTOR_CALLBACK_WalkPassengerToExit: status=c_WalkPassengerToExit(r); break;
    case ACTOR_CALLBACK_BeginPassengerDeparture: status=c_BeginPassengerDeparture(r); break;
    case ACTOR_CALLBACK_AnimatePassengerDeparture: status=c_AnimatePassengerDeparture(r); break;
    case ACTOR_CALLBACK_IgnoreActorState: status=c_IgnoreActorState(r); break;
    case ACTOR_CALLBACK_BeginStonePickupWait: status=c_BeginStonePickupWait(r); break;
    case ACTOR_CALLBACK_UpdateStonePickupWait: status=c_UpdateStonePickupWait(r); break;
    case ACTOR_CALLBACK_AttachStoneToPlayer: status=c_AttachStoneToPlayer(r); break;
    case ACTOR_CALLBACK_WaitForStoneRelease: status=c_WaitForStoneRelease(r); break;
    case ACTOR_CALLBACK_ThrowCarriedStone: status=c_ThrowCarriedStone(r); break;
    case ACTOR_CALLBACK_UpdateThrownStone: status=c_UpdateThrownStone(r); break;
    case ACTOR_CALLBACK_BeginPassengerResurfacing: status=c_BeginPassengerResurfacing(r); break;
    case ACTOR_CALLBACK_UpdatePassengerResurfacing: status=c_UpdatePassengerResurfacing(r); break;
    case ACTOR_CALLBACK_BeginPassengerSinking: status=c_BeginPassengerSinking(r); break;
    case ACTOR_CALLBACK_UpdatePassengerSinking: status=c_UpdatePassengerSinking(r); break;
    case ACTOR_CALLBACK_BeginPassengerFloating: status=c_BeginPassengerFloating(r); break;
    case ACTOR_CALLBACK_UpdatePassengerFloating: status=c_UpdatePassengerFloating(r); break;
    case ACTOR_CALLBACK_UpdateFloatingDestinationDisplay: status=c_UpdateFloatingDestinationDisplay(r); break;
    case ACTOR_CALLBACK_UpdateFloatingQuestionDisplay: status=c_UpdateFloatingQuestionDisplay(r); break;
    case ACTOR_CALLBACK_UpdateFloatingPassengerApproach: status=c_UpdateFloatingPassengerApproach(r); break;
    case ACTOR_CALLBACK_IgnoreWaterbornePassengerState: status=c_IgnoreWaterbornePassengerState(r); break;
    default: status=UGH_BAD_CALLBACK; break;
    }
    if (status!=UGH_CONTROL_TRANSFER && status!=UGH_DOS_EXIT) r->cs=saved_cs;
    if (!status) r->sp=(uint16_t)(r->sp+2);
    return status;
}
EXPORT int c_DispatchActorUpdates(Regs *r) {
    ActorPass pass; actor_pass_begin(&pass); r->bx=logic(r,pass.cursor,16);
    while (pass.remaining) {
        uint16_t descriptor=enemies_read16(r->ds,(uint16_t)(D(ActorDescriptors)+pass.cursor));
        sub16(r,descriptor,0xffff,0);
        ActorCallback callback=ACTOR_CALLBACK_UNSUPPORTED;
        if (descriptor!=0xffff)
            callback=callback_identity(enemies_read16(r->ds,(uint16_t)(D(ActorUpdateOrScriptCursor)+pass.cursor)));
        ActorPassAction action=actor_pass_select(&pass,descriptor,callback);
        if (action==ACTOR_PASS_DONE) return UGH_OK;
        int status=invoke_actor(callback,r); if(status) return status;
        actor_pass_resume(&pass,r->bx);
        r->bx=add16(r,r->bx,2,0);
    }
    return UGH_BUDGET;
}
EXPORT int c_loc_0B4E(Regs *r) { (void)r; actor_reserved_return(); return UGH_OK; }
