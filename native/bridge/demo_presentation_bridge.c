/* Checked literal ABI shells consume a native sequence at every service cut. */
#include "platform.h"
#include "../demo_presentation.h"
#include <stdlib.h>

typedef struct DemoScenePlan {
    DemoPresentationCursor cursor;
    DemoPresentationInput observed;
    DemoPresentationAction pending_action;
    int active,pending,completed;
} DemoScenePlan;
static void dp_require(int condition) {if(!condition) abort();}
static int dp_environment(const Regs *r) {return r->ds==DATA_SEG && r->cs==GAME_SEG;}
static void dp_open(Regs *r,DemoScenePlan *plan,DemoPresentationKind kind) {
    *plan=(DemoScenePlan){0};plan->active=dp_environment(r);plan->cursor=demo_presentation_begin(kind);
}
static DemoPresentationInput dp_input(Regs *r,const DemoScenePlan *plan) {
    DemoPresentationInput input=plan->observed;
    input.fade_level=rd16(r->ds,D(ScreenFadeLevel));input.fade_step=rd16(r->ds,D(ScreenFadeStep));
    input.exit_code=rd16(r->ds,D(DemoExitCode));input.water_y=rd16(r->ds,D(WaterYPixels));return input;
}
static DemoPresentationAction dp_event(Regs *r,DemoScenePlan *plan,DemoPresentationActionKind kind) {
    dp_require(!plan->pending && !plan->completed && dp_environment(r));
    DemoPresentationInput input=dp_input(r,plan);
    DemoPresentationAction action=demo_presentation_next(&plan->cursor,&input);dp_require(action.kind==kind);return action;
}
static DemoPresentationService dp_service_id(uint16_t target) {
    switch(target) {
    case G(InitializeDemoScripts):return DP_SERVICE_INITIALIZE;
    case G(PollKeyboardScanChange):return DP_SERVICE_POLL_KEYBOARD;
    case G(ScaleAndUploadFadedPalette):return DP_SERVICE_PALETTE;
    case G(WaitNextVerticalRetrace):return DP_SERVICE_RETRACE;
    case G(EraseDemoSprites):return DP_SERVICE_ERASE;
    case G(DrawWaterSurface):return DP_SERVICE_WATER;
    case G(AdvanceDemoScripts):return DP_SERVICE_ADVANCE;
    case G(DrawDemoSprites):return DP_SERVICE_DRAW;
    case G(SwapAndDisplayVgaPage):return DP_SERVICE_SWAP;
    case G(TestAllDemoScriptsFinished):return DP_SERVICE_TEST;
    case G(SampleJoystickAxesAndButtons):return DP_SERVICE_JOYSTICK;
    case G(PrepareAttractMap0):return DP_SERVICE_PREPARE_ZERO;
    case G(PrepareAttractMap90):return DP_SERVICE_PREPARE_NINETY;
    case G(RunScriptedDemo):return DP_SERVICE_RUN;
    case G(SetDemoRevealSpriteWidth):return DP_SERVICE_REVEAL_WIDTH;
    }
    dp_require(0);return DP_SERVICE_INITIALIZE;
}
static void dp_before_id(Regs *r,DemoScenePlan *plan,DemoPresentationService service) {
    if(!plan->active) return;
    DemoPresentationAction action=dp_event(r,plan,DP_ACTION_SERVICE);dp_require(action.service==service);
    if(service!=DP_SERVICE_MUSIC_STOP && service!=DP_SERVICE_MUSIC_START) dp_require(action.value==0);
    plan->pending_action=action;plan->pending=1;
}
static void dp_before(Regs *r,DemoScenePlan *plan,uint16_t target) {
    if(plan->active) dp_before_id(r,plan,dp_service_id(target));
}
static void dp_resume(Regs *r,DemoScenePlan *plan) {
    if(!plan->active) return;
    dp_require(plan->pending && !plan->completed);
    switch(plan->pending_action.service) {
    case DP_SERVICE_PALETTE:plan->observed.palette_work=r->cx;break;
    case DP_SERVICE_POLL_KEYBOARD:plan->observed.key_word=r->ax;break;
    case DP_SERVICE_TEST:plan->observed.finished=(r->flags&CF)!=0;break;
    case DP_SERVICE_JOYSTICK:plan->observed.joystick_idle=(r->flags&ZF)!=0;break;
    default:break;
    }
    plan->pending=0;
}
static void dp_write(Regs *r,DemoScenePlan *plan,uint16_t address,uint16_t expected) {
    if(!plan->active) {wr16(r->ds,address,expected);return;}
    DemoPresentationActionKind kind=address==D(DemoExitCode)?DP_ACTION_EXIT:address==D(ScreenFadeLevel)?DP_ACTION_LEVEL:address==D(ScreenFadeStep)?DP_ACTION_STEP:DP_ACTION_REVEAL_X;
    dp_require(address==D(DemoExitCode) || address==D(ScreenFadeLevel) || address==D(ScreenFadeStep) || address==D(ActorX32));
    DemoPresentationAction action=dp_event(r,plan,kind);dp_require(action.value==expected);wr16(r->ds,address,action.value);
}
static uint16_t dp_vector_pointer(uint16_t vector) {
    switch(vector) {
    case DEMO_PRESENT_REVEAL:return D(DemoTable_24DE);
    case DEMO_PRESENT_PREGAME:return D(DemoTable_1792);
    case DEMO_PRESENT_ATTRACT:return D(DemoTable_1E40);
    case DEMO_PRESENT_COMPLETION:return D(DemoTable_1020);
    }
    dp_require(0);return 0;
}
static uint16_t dp_vector(Regs *r,DemoScenePlan *plan,uint16_t expected) {
    if(!plan->active) return expected;
    DemoPresentationAction action=dp_event(r,plan,DP_ACTION_VECTOR);uint16_t value=dp_vector_pointer(action.value);dp_require(value==expected);return value;
}
static uint16_t dp_music_value(Regs *r,DemoScenePlan *plan,DemoPresentationService service,uint16_t expected) {
    if(!plan->active) return expected;
    dp_before_id(r,plan,service);dp_require(plan->pending_action.value==expected);return plan->pending_action.value;
}
static void dp_finish(Regs *r,DemoScenePlan *plan) {
    if(!plan->active) return;
    DemoPresentationAction action=dp_event(r,plan,DP_ACTION_DONE);
    dp_require(action.value==(plan->cursor.kind==DEMO_PRESENT_RUN?rd16(r->ds,D(DemoExitCode)):0));
    dp_require(plan->cursor.phase==DP_TERMINAL);plan->completed=1;
}
static void dp_repeat(Regs *r,DemoScenePlan *plan) {
    if(!plan->active) return;
    DemoPresentationAction action=dp_event(r,plan,DP_ACTION_REPEAT);
    dp_require(action.value==0 && plan->cursor.phase==DP_LOOP);
}
static int dp_tail(Regs *r,DemoScenePlan *plan,int direct) {
    dp_before(r,plan,G(RunScriptedDemo));
    int status=direct?c_RunScriptedDemo(r):ugh_dispatch(r->cs,G(RunScriptedDemo),r);
    dp_resume(r,plan);if(!status) dp_finish(r,plan);return status;
}
typedef struct DemoEffectPlan {DemoFadeEffect fade;DemoRevealWidth width;int active;} DemoEffectPlan;
static DemoEffectPlan dp_effect(Regs *r,int width) {
    DemoEffectPlan plan={0};plan.active=dp_environment(r) && !(r->bx&1u) && r->bx<32;
    if(!plan.active) return plan;
    if(width) plan.width=demo_presentation_width(rd16(r->ds,(uint16_t)(D(ActorX32)+r->bx)));
    else plan.fade=demo_presentation_fade(rd16(r->ds,(uint16_t)(D(ActorSpriteIds)+r->bx)),rd16(r->ds,D(ScreenFadeLevel)));
    return plan;
}
static void dp_effect_write(Regs *r,DemoEffectPlan *plan,uint16_t address,uint16_t expected) {
    if(!plan->active) {wr16(r->ds,address,expected);return;}
    dp_require(plan->fade.triggered);uint16_t value=address==D(ScreenFadeStep)?plan->fade.fade_step:plan->fade.level;
    dp_require((address==D(ScreenFadeStep) || address==D(ScreenFadeLevel)) && value==expected);wr16(r->ds,address,value);
}
static uint8_t dp_width_byte(Regs *r,DemoEffectPlan *plan) {
    if(!plan->active) return (uint8_t)r->ax;
    dp_require(plan->width.pixel_x==r->cx && plan->width.width_word==r->ax && plan->width.width==(uint8_t)r->ax);return plan->width.width;
}

#define R(n) rd16(r->ds,D(n))
#define W(n,v) dp_write(r,&plan,D(n),(uint16_t)(v))
#define CALL(n,ret) do {dp_before(r,&plan,G(n));int status=ugh_call_near(G(n),ret,r);dp_resume(r,&plan);if(status) return status;} while(0)

/* BEGIN CHECKED DEMO SHELLS */
static void push(Regs *r,uint16_t v) { r->sp=(uint16_t)(r->sp-2); wr16(r->ss,r->sp,v); }

static uint16_t pop(Regs *r) { uint16_t v=rd16(r->ss,r->sp); r->sp=(uint16_t)(r->sp+2); return v; }

static int scene_far_call(Regs *r,DemoScenePlan *plan,uint16_t seg,uint16_t off,uint16_t ret) {
    if(plan->active) dp_require(plan->pending && (plan->pending_action.service==DP_SERVICE_MUSIC_STOP || plan->pending_action.service==DP_SERVICE_MUSIC_START));
    push(r,r->cs); push(r,ret); int st=ugh_dispatch(seg,off,r);
    r->sp=(uint16_t)(r->sp+4); dp_resume(r,plan);return st;
}

EXPORT int c_RunScriptedDemo(Regs *r) { DemoScenePlan plan;dp_open(r,&plan,DEMO_PRESENT_RUN);
    CALL(InitializeDemoScripts,G(RunScriptedDemo)+3);
    r->ax=logic(r,0,16); W(DemoExitCode,r->ax); W(ScreenFadeLevel,r->ax); W(ScreenFadeStep,4);
    CALL(PollKeyboardScanChange,G(RunScriptedDemo)+0x14);
    for(unsigned budget=0;budget<100000;budget++) {
        r->cx=R(ScreenFadeLevel); sub16(r,r->cx,0,0);
        if((int16_t)r->cx<0) { logic(r,R(DemoExitCode),16); dp_finish(r,&plan);return UGH_OK; }
        sub16(r,r->cx,256,0);
        if((int16_t)r->cx<=256) {
            CALL(ScaleAndUploadFadedPalette,G(RunScriptedDemo)+0x2f);
            r->cx=add16(r,r->cx,R(ScreenFadeStep),0); W(ScreenFadeLevel,r->cx);
        } else { CALL(WaitNextVerticalRetrace,G(RunScriptedDemo)+0x3c); }
        CALL(EraseDemoSprites,G(RunScriptedDemo)+0x3f);
        sub16(r,R(WaterYPixels),192,0);
        if((int16_t)R(WaterYPixels)<192) { CALL(DrawWaterSurface,G(RunScriptedDemo)+0x4d); }
        CALL(AdvanceDemoScripts,G(RunScriptedDemo)+0x50);
        CALL(DrawDemoSprites,G(RunScriptedDemo)+0x53);
        CALL(SwapAndDisplayVgaPage,G(RunScriptedDemo)+0x56);
        CALL(TestAllDemoScriptsFinished,G(RunScriptedDemo)+0x59);
        if(!(r->flags&CF)) {
            CALL(SampleJoystickAxesAndButtons,G(RunScriptedDemo)+0x61);
            if(r->flags&ZF) {
                CALL(PollKeyboardScanChange,G(RunScriptedDemo)+0x69);
                logic(r,r->ax>>8,8); if(!(r->ax>>8)) {dp_repeat(r,&plan);continue;}
                set_al(r,(uint8_t)logic(r,r->ax&0x7f,8));
                sub16(r,(uint8_t)r->ax,0x10,0);
                if((uint8_t)r->ax==0x10) W(DemoExitCode,0xffff);
                else {
                    sub16(r,(uint8_t)r->ax,1,0);
                    W(DemoExitCode,(uint8_t)r->ax==1?1:0);
                }
            } else W(DemoExitCode,0);
        }
        sub16(r,R(ScreenFadeStep),0,0);
        if((int16_t)R(ScreenFadeStep)<0) {dp_repeat(r,&plan);continue;}
        r->ax=0xfffc; W(ScreenFadeStep,r->ax); W(ScreenFadeLevel,add16(r,R(ScreenFadeLevel),r->ax,0)); dp_repeat(r,&plan);
    }
    return UGH_BUDGET;
}

EXPORT int c_PlaySpriteRevealDemo(Regs *r) { DemoScenePlan plan;dp_open(r,&plan,DEMO_PRESENT_REVEAL);
    CALL(PrepareAttractMap0,G(PlaySpriteRevealDemo)+3); r->si=dp_vector(r,&plan,D(DemoTable_24DE));
    CALL(RunScriptedDemo,G(PlaySpriteRevealDemo)+9); push(r,r->flags);
    r->bx=logic(r,0,16); W(ActorX32,r->bx);
    CALL(SetDemoRevealSpriteWidth,G(PlaySpriteRevealDemo)+0x13); r->flags=pop(r); dp_finish(r,&plan);return UGH_OK;
}

EXPORT int c_PlayPreGameDemo(Regs *r) { DemoScenePlan plan;dp_open(r,&plan,DEMO_PRESENT_PREGAME);
    CALL(PrepareAttractMap0,G(PlayPreGameDemo)+3); r->si=dp_vector(r,&plan,D(DemoTable_1792));
    return dp_tail(r,&plan,0);
}

EXPORT int c_PlayAttractDemo(Regs *r) { DemoScenePlan plan;dp_open(r,&plan,DEMO_PRESENT_ATTRACT);
    CALL(PrepareAttractMap90,G(PlayAttractDemo)+3); r->si=dp_vector(r,&plan,D(DemoTable_1E40));
    return dp_tail(r,&plan,1);
}

EXPORT int c_PlayGameCompletionDemo(Regs *r) { DemoScenePlan plan;dp_open(r,&plan,DEMO_PRESENT_COMPLETION);
    CALL(PrepareAttractMap0,G(PlayGameCompletionDemo)+3); push(r,dp_music_value(r,&plan,DP_SERVICE_MUSIC_STOP,0x11));
    int st=scene_far_call(r,&plan,UGH_S_C_StopMusicTrack,UGH_O_C_StopMusicTrack,G(PlayGameCompletionDemo)+10);
    if(st) return st;
    r->sp=add16(r,r->sp,2,0); push(r,dp_music_value(r,&plan,DP_SERVICE_MUSIC_START,0xa5)); push(r,0); push(r,UGH_S_B3279_ext_3279); push(r,0);
    st=scene_far_call(r,&plan,UGH_S_C_StartMusicTrack,UGH_O_C_StartMusicTrack,G(PlayGameCompletionDemo)+0x1d);
    if(st) return st;
    r->sp=add16(r,r->sp,8,0); r->si=dp_vector(r,&plan,D(DemoTable_1020)); return dp_tail(r,&plan,0);
}

EXPORT int c_StartDemoFadeWhenSpriteHidden(Regs *r) { DemoEffectPlan plan=dp_effect(r,0);
    uint16_t sprite=rd16(r->ds,(uint16_t)(D(ActorSpriteIds)+r->bx));
    sub16(r,sprite,0x7fff,0);
    if(plan.active) dp_require(plan.fade.triggered==(sprite==0x7fff));
    if(sprite==0x7fff) {
        r->ax=0xfffc;
        dp_effect_write(r,&plan,D(ScreenFadeStep),r->ax);
        dp_effect_write(r,&plan,D(ScreenFadeLevel),
             add16(r,rd16(r->ds,D(ScreenFadeLevel)),r->ax,0));
    }
    return UGH_OK;
}

EXPORT int c_SetDemoRevealSpriteWidth(Regs *r) { DemoEffectPlan plan=dp_effect(r,1);
    uint16_t x=rd16(r->ds,(uint16_t)(D(ActorX32)+r->bx));
    r->cx=(uint16_t)((x>>5) | ((x&0x8000) ? 0xf800u : 0));
    r->ax=sub16(r,320,r->cx,0);
    sub16(r,r->ax,127,0);
    if((int16_t)r->ax>127) set_al(r,127);
    r->di=rd16(r->cs,G(DemoRevealWidthPointer));
    r->es=rd16(r->cs,(uint16_t)(G(DemoRevealWidthPointer)+2));
    wr8(r->es,r->di,dp_width_byte(r,&plan));
    r->di=(uint16_t)(r->di+step(r));
    return UGH_OK;
}

