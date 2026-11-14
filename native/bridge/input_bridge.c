#include "platform.h"
#include "../input.h"
/* The only binding of native input decisions to DOS fields, ports, vectors,
 * timing deliveries and near/interrupt frames. No endpoint fallback. */
static void push(Regs *r,uint16_t x) {
    r->sp=(uint16_t)(r->sp-2); wr16(r->ss,r->sp,x);
}
static uint16_t pop(Regs *r) {
    uint16_t x=rd16(r->ss,r->sp); r->sp=(uint16_t)(r->sp+2); return x;
}
static int call(Regs *r,uint16_t target,uint16_t ret) {
    return ugh_call_near(target,ret,r);
}
static InputState input_project(uint16_t bank) {
    InputState state={0};state.latest_scan=rd8(GAME_SEG,G(LatestInterruptScanCode));
    state.current_scan=rd8(bank,D(CurrentKeyboardScanCode));state.previous_scan=rd8(bank,D(PreviousPolledScanCode));state.change=rd8(bank,D(KeyboardScanCodeChangeBits));state.sequence_index=rd8(bank,D(KeyboardSequenceIndex));
    state.enabled_axes=rd8(bank,D(JoystickEnabledAxisMask));state.loop_limit=rd16(bank,D(JoystickSampleLoopLimit));state.player_count=rd16(bank,D(PlayerCount));
    for(unsigned i=0;i<2;i++) {uint16_t d=(uint16_t)(2u*i);InputJoystick *j=&state.joysticks[i];state.control_mode[i]=rd16(bank,(uint16_t)(D(PlayerOneControlMode)+d));
        j->present=rd16(bank,(uint16_t)(D(JoystickPresentFlags)+d));j->x=rd16(bank,(uint16_t)(D(FirstJoystickXCount)+d));j->y=rd16(bank,(uint16_t)(D(FirstJoystickYCount)+d));j->buttons=rd16(bank,(uint16_t)(D(JoystickButtonBits)+d));
        j->double_x=rd16(bank,(uint16_t)(D(FirstJoystickXDoubleCenter)+d));j->double_y=rd16(bank,(uint16_t)(D(FirstJoystickYDoubleCenter)+d));j->left=rd16(bank,(uint16_t)(D(JoystickLeftThresholds)+d));j->right=rd16(bank,(uint16_t)(D(JoystickRightThresholds)+d));j->up=rd16(bank,(uint16_t)(D(JoystickUpThresholds)+d));j->down=rd16(bank,(uint16_t)(D(JoystickDownThresholds)+d));
        InputCommands *c=&state.commands[i];c->up=rd16(bank,(uint16_t)(D(PlayerUpInput)+d));c->down=rd16(bank,(uint16_t)(D(PlayerDownInput)+d));c->left=rd16(bank,(uint16_t)(D(PlayerLeftInput)+d));c->right=rd16(bank,(uint16_t)(D(PlayerRightInput)+d));c->action=rd16(bank,(uint16_t)(D(PlayerActionInput)+d));
    }
    for(unsigned i=0;i<4;i++) state.calibration_reset_words[i]=rd16(bank,(uint16_t)(D(ds_3321)+2u*i));
    return state;
}
static int input_key_run(Regs *r,uint16_t bank,InputKeyWork *work,int installation) {
    uint16_t reply=0;
    for(;;) {
        InputKeyRequest request=input_key_next(work,reply);
        switch(request.action) {
        case INPUT_KEY_DONE:return UGH_OK;
        case INPUT_KEY_BOUND:return UGH_BUDGET;
        case INPUT_KEY_READ_TABLE:reply=rd8(bank,(uint16_t)(D(KeyboardSequenceRecords)+request.position));break;
        case INPUT_KEY_WRITE_TABLE:
            wr8(bank,(uint16_t)(D(KeyboardSequenceRecords)+request.position),request.value);
            if(installation) r->si=add16(r,r->si,6,0);
            break;
        case INPUT_KEY_READ_MODE:reply=rd16(bank,(uint16_t)(D(PlayerOneControlMode)+request.position));break;
        case INPUT_KEY_READ_INDEX:reply=rd8(bank,D(KeyboardSequenceIndex));break;
        case INPUT_KEY_WRITE_INDEX:wr8(bank,D(KeyboardSequenceIndex),request.value);break;
        case INPUT_KEY_WRITE_ACTION:wr8(bank,(uint16_t)(D(PlayerUpInput)+request.position),request.value);break;
        default:return UGH_UNSUPPORTED;
        }
    }
}
EXPORT int c_HandleKeyboardScanInterrupt(Regs *r) {
    uint8_t scan=(uint8_t)platform_in(0x60,1);if(ugh_devices.error) return UGH_UNSUPPORTED;
    wr8(r->cs,G(LatestInterruptScanCode),scan);InputKeyWork work=input_key_begin(scan,rd8(DATA_SEG,D(KeyboardSequenceIndex)),0);
    int status=input_key_run(r,DATA_SEG,&work,0);if(status) return status;platform_out(0x20,1,0x20);return UGH_OK;
}
EXPORT int c_PollKeyboardScanChange(Regs *r) {
    int status=platform_service_point_at(SERVICE_IO,r->cs,G(PollKeyboardScanChange),r);if(status) return status;
    InputState state=input_project(r->ds);input_state_scan(&state,rd8(GAME_SEG,G(LatestInterruptScanCode)));
    wr8(r->ds,D(PreviousPolledScanCode),state.previous_scan);wr8(r->ds,D(CurrentKeyboardScanCode),state.current_scan);
    set_al(r,state.current_scan);set_ah(r,(uint8_t)logic(r,state.change,8));wr8(r->ds,D(KeyboardScanCodeChangeBits),state.change);return UGH_OK;
}
EXPORT int c_InstallKeyboardSequenceInterrupt(Regs *r) {
    set_al(r,0);logic(r,0,8);r->si=logic(r,0,16);InputKeyWork work=input_key_begin(0,0,1);
    int reset_status=input_key_run(r,r->ds,&work,1);if(reset_status) return reset_status;
    /* CMP byte,FF defines SF/ZF/PF/CF/OF; equal is all zero except ZF/PF. */
    sub16(r,255,255,0); flag(r,IF,0); r->di=0x40; r->es=r->di;
    r->ax=rd16(r->es,0x1c); wr16(r->es,0x1a,r->ax);
    r->ax=0x3509; int status=platform_interrupt(0x21,r); if(status) return status;
    wr16(r->ds,D(PreviousKeyboardVector),r->bx); wr16(r->ds,D(PreviousKeyboardVectorSegment),r->es);
    uint16_t ds=r->ds; r->ax=0x2509; r->dx=rd16(r->ds,D(KeyboardHandlerVector));
    r->ds=rd16(r->ds,(uint16_t)(D(KeyboardHandlerVector)+2));
    status=platform_interrupt(0x21,r); r->ds=ds; flag(r,IF,1); return status;
}
EXPORT int c_RestoreKeyboardInterrupt(Regs *r) {
    uint16_t ds=r->ds; r->ax=0x2509; r->dx=rd16(r->ds,D(PreviousKeyboardVector));
    r->ds=rd16(r->ds,D(PreviousKeyboardVectorSegment)); int status=platform_interrupt(0x21,r); r->ds=ds;
    flag(r,IF,0); r->di=0x40; r->es=r->di; r->ax=rd16(r->es,0x1c); wr16(r->es,0x1a,r->ax);
    flag(r,IF,1); return status;
}
EXPORT int c_SampleJoystickAxesAndButtons(Regs *r) {
    uint16_t saved_flags=r->flags; flag(r,IF,0); r->dx=0x201;
    platform_out(r->dx,1,(uint8_t)r->ax); r->bx=r->bp=r->si=r->di=0;
    r->cx=rd16(r->ds,D(JoystickSampleLoopLimit));
    set_al(r,(uint8_t)platform_in(r->dx,1)); r->ax=(uint16_t)~r->ax; r->ax=input_button_bits((uint8_t)~r->ax,0);
    wr16(r->ds,D(JoystickButtonBits),r->ax);
    set_al(r,(uint8_t)platform_in(r->dx,1)); r->ax=(uint16_t)~r->ax; r->ax=input_button_bits((uint8_t)~r->ax,1);
    wr16(r->ds,D(SecondJoystickButtonBits),r->ax);
    uint8_t mask=rd8(r->ds,D(JoystickEnabledAxisMask));InputAxisTimer work=input_axis_begin(r->cx,mask);
    if(mask) for(;;) {
        uint8_t delivery=(uint8_t)platform_in(r->dx,1);if(ugh_devices.error) return UGH_UNSUPPORTED;
        int again=input_axis_delivery(&work,delivery);r->cx=work.remaining;r->bx=work.latched[0];r->bp=work.latched[1];r->si=work.latched[2];r->di=work.latched[3];
        if(again<0) return UGH_BUDGET;
        if(!again) break;
    }
    if(ugh_devices.error) return UGH_UNSUPPORTED;
    r->flags=saved_flags; r->ax=rd16(r->ds,D(JoystickSampleLoopLimit));
    sub16(r,r->ax,r->di,0);r->dx=input_axis_count(r->ax,r->di); wr16(r->ds,D(SecondJoystickYCount),r->dx);
    sub16(r,r->ax,r->si,0);r->cx=input_axis_count(r->ax,r->si); wr16(r->ds,D(SecondJoystickXCount),r->cx);
    sub16(r,r->ax,r->bx,0);r->dx=input_axis_count(r->ax,r->bx); wr16(r->ds,D(FirstJoystickXCount),r->dx);
    sub16(r,r->ax,r->bp,0);r->ax=input_axis_count(r->ax,r->bp); wr16(r->ds,D(FirstJoystickYCount),r->ax);
    r->ax=logic(r,rd16(r->ds,D(JoystickButtonBits))|rd16(r->ds,D(SecondJoystickButtonBits)),16);
    return UGH_OK;
}
static void input_threshold_binding(Regs *r,uint16_t count,uint16_t low,uint16_t high) {
    r->ax=rd16(r->ds,count);r->bx=r->ax;InputThresholds result=input_thresholds(r->ax);r->ax=(uint16_t)(r->ax>>1);
    r->bx=sub16(r,r->bx,r->ax,0);wr16(r->ds,low,result.low);r->bx=add16(r,r->bx,r->ax,0);r->bx=add16(r,r->bx,r->ax,0);wr16(r->ds,high,result.high);
}
EXPORT int c_DetectAndCalibrateJoysticks(Regs *r) {
    flag(r,IF,0); r->ax=sub16(r,r->ax,r->ax,0);
    InputState state=input_project(r->ds);input_calibration_start(&state);
    wr16(r->ds,D(JoystickPresentFlags),state.joysticks[0].present); wr16(r->ds,D(SecondJoystickPresent),state.joysticks[1].present);
    wr8(r->ds,D(JoystickEnabledAxisMask),state.enabled_axes);wr16(r->ds,D(JoystickSampleLoopLimit),state.loop_limit);
    const uint16_t clear[]={D(ds_3321),D(ds_3325),D(ds_3323),D(ds_3327),
        D(FirstJoystickXDoubleCenter),D(FirstJoystickYDoubleCenter),
        D(SecondJoystickXDoubleCenter),D(SecondJoystickYDoubleCenter)};
    for(unsigned i=0;i<8;i++) wr16(r->ds,clear[i],r->ax);
    r->dx=0x201; platform_out(r->dx,1,(uint8_t)r->ax);
    r->cx=0x1600; do { r->cx=dec16(r,r->cx); } while(r->cx);
    set_al(r,(uint8_t)platform_in(r->dx,1)); if(ugh_devices.error) return UGH_UNSUPPORTED;
    push(r,r->ax); logic(r,(uint8_t)r->ax&3,8);
    if(input_joystick_present((uint8_t)r->ax,0)) {
        state=input_project(r->ds);input_calibration_detect(&state,0);
        wr16(r->ds,D(JoystickPresentFlags),state.joysticks[0].present);wr16(r->ds,D(PlayerOneControlMode),state.control_mode[0]);
        wr8(r->ds,D(JoystickEnabledAxisMask),(uint8_t)logic(r,state.enabled_axes,8));
        int status=call(r,G(SampleJoystickAxesAndButtons),G(DetectAndCalibrateJoysticks)+89); if(status) return status;
        state=input_project(r->ds);input_calibration_apply(&state,0);
        r->ax=rd16(r->ds,D(FirstJoystickXCount)); r->bx=rd16(r->ds,D(FirstJoystickYCount));
        r->ax=(uint16_t)(r->ax*2); r->bx=(uint16_t)(r->bx*2);
        wr16(r->ds,D(FirstJoystickXDoubleCenter),state.joysticks[0].double_x); wr16(r->ds,D(FirstJoystickYDoubleCenter),state.joysticks[0].double_y);
        input_threshold_binding(r,D(FirstJoystickXCount),D(JoystickLeftThresholds),D(JoystickRightThresholds));
        input_threshold_binding(r,D(FirstJoystickYCount),D(JoystickUpThresholds),D(JoystickDownThresholds));
    }
    r->ax=pop(r); logic(r,(uint8_t)r->ax&12,8);
    if(input_joystick_present((uint8_t)r->ax,1)) {
        state=input_project(r->ds);input_calibration_detect(&state,1);
        wr16(r->ds,D(SecondJoystickPresent),state.joysticks[1].present);wr16(r->ds,D(PlayerTwoControlMode),state.control_mode[1]);
        wr8(r->ds,D(JoystickEnabledAxisMask),(uint8_t)logic(r,state.enabled_axes,8));
        r->cx=0x1600; do { r->cx=dec16(r,r->cx); } while(r->cx);
        int status=call(r,G(SampleJoystickAxesAndButtons),G(DetectAndCalibrateJoysticks)+188); if(status) return status;
        state=input_project(r->ds);input_calibration_apply(&state,1);
        r->cx=rd16(r->ds,D(SecondJoystickXCount)); r->dx=rd16(r->ds,D(SecondJoystickYCount));
        r->cx=(uint16_t)(r->cx*2); r->dx=(uint16_t)(r->dx*2);
        wr16(r->ds,D(SecondJoystickXDoubleCenter),state.joysticks[1].double_x); wr16(r->ds,D(SecondJoystickYDoubleCenter),state.joysticks[1].double_y);
        input_threshold_binding(r,D(SecondJoystickXCount),D(SecondJoystickXLowThreshold),D(SecondJoystickXHighThreshold));
        input_threshold_binding(r,D(SecondJoystickYCount),D(SecondJoystickYLowThreshold),D(SecondJoystickYHighThreshold));
    }
    state=input_project(r->ds);uint16_t doubled[]={state.joysticks[0].double_x,state.joysticks[0].double_y,state.joysticks[1].double_x,state.joysticks[1].double_y};
    uint16_t prefix[]={doubled[0],doubled[1],doubled[2],0};
    /* Only the last CMP flags survive. Its left operand is the native
     * unsigned maximum of the preceding three wrapped measurements. */
    r->ax=input_calibration_limit(prefix);sub16(r,r->ax,doubled[3],0);
    r->ax=input_calibration_limit(doubled);wr16(r->ds,D(JoystickSampleLoopLimit),r->ax); flag(r,IF,1); return UGH_OK;
}
#define INPUT_READ(n) rd16(r->ds,D(n))
#define INPUT_READ_AT(n,i) rd16(r->ds,(uint16_t)(D(n)+(i)))
#define INPUT_CALL(n,ret) do {int status=ugh_call_near(G(n),ret,r);if(status) return status;} while(0)
EXPORT int c_PollPlayerControls(Regs *r) {
    INPUT_CALL(PollKeyboardScanChange,(uint16_t)(G(PollPlayerControls)+3));
    logic(r,INPUT_READ(PlayerOneControlMode),16);
    if((int16_t)INPUT_READ(PlayerOneControlMode)<0) {
        logic(r,INPUT_READ(PlayerTwoControlMode),16);
        if((int16_t)INPUT_READ(PlayerTwoControlMode)>=0) sub16(r,INPUT_READ(PlayerCount),2,0);
    }
    if(input_controls_need_sample(INPUT_READ(PlayerOneControlMode),INPUT_READ(PlayerTwoControlMode),INPUT_READ(PlayerCount))) {INPUT_CALL(SampleJoystickAxesAndButtons,(uint16_t)(G(PollPlayerControls)+0x26));}
    r->bx=logic(r,0,16);uint16_t visits=input_player_visits(INPUT_READ(PlayerCount));
    for(unsigned player=0;player<visits;player++) {
        InputControlSource source=input_control_source(INPUT_READ_AT(PlayerOneControlMode,r->bx));r->si=source.position;logic(r,r->si,16);
        if(source.joystick) {
            r->ax=logic(r,0,16);wr16(r->ds,(uint16_t)(D(PlayerUpInput)+r->bx),0);wr16(r->ds,(uint16_t)(D(PlayerDownInput)+r->bx),0);wr16(r->ds,(uint16_t)(D(PlayerLeftInput)+r->bx),0);wr16(r->ds,(uint16_t)(D(PlayerRightInput)+r->bx),0);wr16(r->ds,(uint16_t)(D(PlayerActionInput)+r->bx),0);
            /* position<=7FFE: these ordinary source words start at3315 and
             * cannot alias command bytes278C..279F. Reading them together
             * preserves their values; selected stores retain original order. */
            InputJoystick stick={0};stick.x=INPUT_READ_AT(FirstJoystickXCount,r->si);stick.y=INPUT_READ_AT(FirstJoystickYCount,r->si);stick.left=INPUT_READ_AT(JoystickLeftThresholds,r->si);stick.right=INPUT_READ_AT(JoystickRightThresholds,r->si);stick.up=INPUT_READ_AT(JoystickUpThresholds,r->si);stick.down=INPUT_READ_AT(JoystickDownThresholds,r->si);stick.buttons=INPUT_READ_AT(JoystickButtonBits,r->si);
            InputCommands commands=input_control_map(&stick);r->ax=stick.x;
            if(commands.left) wr16(r->ds,(uint16_t)(D(PlayerLeftInput)+r->bx),commands.left);else if(commands.right) wr16(r->ds,(uint16_t)(D(PlayerRightInput)+r->bx),commands.right);
            r->ax=stick.y;if(commands.up) wr16(r->ds,(uint16_t)(D(PlayerUpInput)+r->bx),commands.up);else if(commands.down) wr16(r->ds,(uint16_t)(D(PlayerDownInput)+r->bx),commands.down);
            if(commands.action) wr16(r->ds,(uint16_t)(D(PlayerActionInput)+r->bx),commands.action);
        }
        r->bx=add16(r,r->bx,2,0);sub16(r,r->bx,INPUT_READ(PlayerCount),0);
    }
    set_al(r,rd8(r->ds,D(CurrentKeyboardScanCode)));set_ah(r,rd8(r->ds,D(KeyboardScanCodeChangeBits)));return UGH_OK;
}
EXPORT int c_WaitForScanChangeOrJoystickButton(Regs *r) {
    InputWaitWork work={1000000,0};int changed=0;
    for(;;) {
        InputWaitAction action=input_wait_next(&work,changed);int status=0;
        switch(action) {
        case INPUT_WAIT_SCAN:
            status=call(r,G(PollKeyboardScanChange),work.stage==1 ? G(loc_44DE) : G(loc_44DE)+14);if(status) return status;
            if(work.stage!=1) {logic(r,r->ax>>8,8);changed=!!(r->ax>>8);}break;
        case INPUT_WAIT_RETRACE:status=call(r,G(WaitNextVerticalRetrace),G(loc_44DE)+3);break;
        case INPUT_WAIT_SAMPLE:status=call(r,G(SampleJoystickAxesAndButtons),G(loc_44DE)+6);changed=!(r->flags&ZF);break;
        case INPUT_WAIT_SERVICE:status=platform_service_point_at(SERVICE_IO,r->cs,G(loc_44DE)+11,r);break;
        case INPUT_WAIT_DONE:return UGH_OK;
        default:return UGH_BUDGET;
        }
        if(status) return status;
    }
}
