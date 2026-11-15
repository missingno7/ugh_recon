#include "game_startup.h"
#define TRY(call) do{GSStatus status=(call);if(status!=GS_OK)return status;}while(0)
static InputState borrow(GameWorld *w) {
    InputState view={0};view.loop_limit=w->input.loop_limit;
    view.enabled_axes=(uint8_t)w->input.enabled_axis_storage;
    for(unsigned i=0;i<2;i++){view.joysticks[i]=w->input.joysticks[i];view.control_mode[i]=w->run.configuration.control_mode[i];}
    return view;
}
static void retain(GameWorld *w,const InputState *view) {
    w->input.loop_limit=view->loop_limit;
    w->input.enabled_axis_storage=(uint16_t)((w->input.enabled_axis_storage&65280)|view->enabled_axes);
    for(unsigned i=0;i<2;i++){w->input.joysticks[i]=view->joysticks[i];w->run.configuration.control_mode[i]=view->control_mode[i];}
    for(unsigned i=0;i<4;i++)w->input.calibration_reset_words[i]=view->calibration_reset_words[i];
}
GSStatus game_install_input(GameWorld *w,GameServices *s) {
    InputKeyWork work=input_key_begin(0,0,1);uint16_t reply=0;
    for(;;) {
        InputKeyRequest request=input_key_next(&work,reply);
        switch(request.action) {
        case INPUT_KEY_DONE:goto installed;
        case INPUT_KEY_READ_TABLE:
            if(request.position>=sizeof w->input.sequence)return GS_UNSUPPORTED;
            reply=w->input.sequence[request.position];break;
        case INPUT_KEY_WRITE_TABLE:
            if(request.position>=sizeof w->input.sequence)return GS_UNSUPPORTED;
            w->input.sequence[request.position]=request.value;break;
        case INPUT_KEY_WRITE_INDEX:w->input.index=request.value;break;
        case INPUT_KEY_BOUND:return GS_OVERFLOW;
        default:return GS_UNSUPPORTED;
        }
    }
installed:;
    uint16_t flush;GSBinding reply_binding;
    TRY(s->input.flush(s->input_context,&flush));
    TRY(s->input.vector(s->input_context,GS_VECTOR_CAPTURE,(GSBinding){0},&w->keyboard_saved));
    return s->input.vector(s->input_context,GS_VECTOR_INSTALL,(GSBinding){2},&reply_binding);
}
GSStatus game_sample_input_trigger(GameWorld *w,GameServices *s,uint8_t trigger) {
    TRY(s->input.joystick_start(s->input_context,trigger));
    for(unsigned i=0;i<2;i++)TRY(s->input.buttons(s->input_context,i,&w->input.joysticks[i].buttons));
    GSJoystickCounts reply;TRY(s->input.counts(s->input_context,w->input.loop_limit,(uint8_t)w->input.enabled_axis_storage,&reply));
    for(unsigned i=0;i<2;i++){w->input.joysticks[i].x=reply.counts[2*i];w->input.joysticks[i].y=reply.counts[2*i+1];}
    return GS_OK;
}
GSStatus game_sample_input(GameWorld *w,GameServices *s){return game_sample_input_trigger(w,s,0);}
GSStatus game_calibrate_input(GameWorld *w,GameServices *s) {
    InputState view=borrow(w);input_calibration_start(&view);retain(w,&view);
    TRY(s->input.joystick_start(s->input_context,0));uint8_t presence;
    TRY(s->input.presence(s->input_context,&presence));
    for(unsigned i=0;i<2;i++)if(input_joystick_present(presence,(uint8_t)i)) {
        view=borrow(w);input_calibration_detect(&view,i);retain(w,&view);
        TRY(game_sample_input(w,s));view=borrow(w);input_calibration_apply(&view,i);retain(w,&view);
    }
    uint16_t doubled[]={w->input.joysticks[0].double_x,w->input.joysticks[0].double_y,w->input.joysticks[1].double_x,w->input.joysticks[1].double_y};
    w->input.loop_limit=input_calibration_limit(doubled);return GS_OK;
}
GSStatus game_poll_input(GameWorld *w,GameServices *s) {
    TRY(s->input.pump(s->input_context,GS_INPUT_SCAN));uint8_t scan;
    GSStatus status=s->input.scan(s->input_context,&scan);
    if(status!=GS_OK&&status!=GS_EMPTY)return status;
    if(status==GS_OK){
        w->input.latest=scan;InputKeyWork work=input_key_begin(scan,w->input.index,0);uint16_t reply=0;
        for(;;){InputKeyRequest r=input_key_next(&work,reply);
            if(r.action==INPUT_KEY_DONE)break;
            if(r.action==INPUT_KEY_READ_TABLE||r.action==INPUT_KEY_WRITE_TABLE){
                if(r.position>=sizeof w->input.sequence)return GS_UNSUPPORTED;
                if(r.action==INPUT_KEY_READ_TABLE)reply=w->input.sequence[r.position];else w->input.sequence[r.position]=r.value;
            }else if(r.action==INPUT_KEY_READ_INDEX)reply=w->input.index;
            else if(r.action==INPUT_KEY_WRITE_INDEX)w->input.index=r.value;
            else if(r.action==INPUT_KEY_READ_MODE){if(r.position>2||(r.position&1))return GS_UNSUPPORTED;reply=w->run.configuration.control_mode[r.position/2];}
            else if(r.action==INPUT_KEY_BOUND)return GS_OVERFLOW;
            else return GS_UNSUPPORTED; /* command recipient belongs to session */
        }TRY(s->input.acknowledge(s->input_context));
    }
    InputScanChange change=input_scan_change((uint8_t)w->input.current_scan_storage,w->input.latest);
    w->input.previous=change.previous;w->input.change=change.change;
    w->input.current_scan_storage=(uint16_t)((w->input.current_scan_storage&65280)|change.current);
    return GS_OK;
}
