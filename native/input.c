#include "input.h"
InputScanChange input_scan_change(uint8_t previous,uint8_t delivered)
{InputScanChange result={previous,delivered,(uint8_t)(previous^delivered)};return result;}
InputThresholds input_thresholds(uint16_t measured)
{
    uint16_t half=(uint16_t)(measured>>1);
    InputThresholds result={(uint16_t)(measured-half),(uint16_t)(measured+half),(uint16_t)(measured*2u)};return result;
}
int input_axis_direction(uint16_t measured,uint16_t low,uint16_t high)
{return (int16_t)measured<=(int16_t)low ? -1 : (int16_t)measured>=(int16_t)high ? 1 : 0;}
uint16_t input_calibration_limit(const uint16_t doubled[4])
{uint16_t maximum=doubled[0];for(unsigned i=1;i<4;i++) if(maximum<doubled[i]) maximum=doubled[i];return maximum;}
int input_joystick_present(uint8_t discharged,uint8_t joystick)
{return !(discharged&(joystick ? 12u : 3u));}
int input_controls_need_sample(uint16_t first,uint16_t second,uint16_t count)
{return (int16_t)first>=0 || ((int16_t)second>=0 && count==2);}
void input_state_scan(InputState *state,uint8_t delivered)
{
    InputScanChange result=input_scan_change(state->current_scan,delivered);
    state->previous_scan=result.previous;state->current_scan=result.current;state->change=result.change;
}
void input_calibration_start(InputState *state)
{
    state->enabled_axes=0;state->loop_limit=65535;
    for(unsigned i=0;i<2;i++) {state->joysticks[i].present=0;state->joysticks[i].double_x=0;state->joysticks[i].double_y=0;}
    for(unsigned i=0;i<4;i++) state->calibration_reset_words[i]=0;
}
void input_calibration_detect(InputState *state,unsigned joystick)
{
    state->joysticks[joystick].present=65535;state->control_mode[joystick]=(uint16_t)joystick;
    state->enabled_axes|=(uint8_t)(3u<<(2u*joystick));
}
void input_calibration_apply(InputState *state,unsigned joystick)
{
    InputJoystick *stick=&state->joysticks[joystick];
    InputThresholds horizontal=input_thresholds(stick->x),vertical=input_thresholds(stick->y);
    stick->double_x=horizontal.doubled;stick->left=horizontal.low;stick->right=horizontal.high;
    stick->double_y=vertical.doubled;stick->up=vertical.low;stick->down=vertical.high;
}
InputAxisTimer input_axis_begin(uint16_t limit,uint8_t enabled)
{InputAxisTimer work={limit,{0,0,0,0},1000000,(uint8_t)~enabled};return work;}
int input_axis_delivery(InputAxisTimer *work,uint8_t delivered)
{
    if(!work->budget) return -1;
    work->budget--;
    uint8_t ended=(uint8_t)~(delivered|work->completed);
    if(ended) {
        unsigned axis=ended&1u ? 0 : ended&2u ? 1 : ended&4u ? 2 : 3;
        work->latched[axis]=work->remaining;work->completed|=(uint8_t)(1u<<axis);
        if(work->completed==255) return 0;
    } else {
        work->remaining=(uint16_t)(work->remaining-1u);
        if(!work->remaining) return 0;
    }
    return work->budget ? 1 : -1;
}
uint16_t input_axis_count(uint16_t live_limit,uint16_t latched) {return (uint16_t)(live_limit-latched);}
uint16_t input_button_bits(uint8_t delivered,unsigned joystick)
{return (uint16_t)((uint8_t)~delivered&(joystick ? 192u : 48u));}

InputKeyWork input_key_begin(uint8_t scan,uint8_t index,int reset_only)
{InputKeyWork work={32768,32768,0,index,scan,0,0,(uint8_t)(reset_only ? 8 : 0)};return work;}
InputKeyRequest input_key_next(InputKeyWork *work,uint16_t reply)
{
    InputKeyRequest request={INPUT_KEY_DONE,0,0};
    for(;;) switch(work->stage) {
    case 0:
        if(!work->budget--) {request.action=INPUT_KEY_BOUND;return request;}
        request.action=INPUT_KEY_READ_TABLE;request.position=(uint16_t)(work->position+5u);work->stage=1;return request;
    case 1:
        if(reply==255) {work->stage=7;break;}
        request.action=INPUT_KEY_READ_TABLE;request.position=(uint16_t)(work->position+work->index);work->stage=2;return request;
    case 2:
        if(reply!=work->scan) {request.action=INPUT_KEY_WRITE_TABLE;request.position=(uint16_t)(work->position+5u);request.value=255;work->stage=7;return request;}
        request.action=INPUT_KEY_READ_TABLE;request.position=(uint16_t)(work->position+work->index+1u);work->stage=3;return request;
    case 3:
        if(reply!=255) {work->matches++;work->stage=7;break;}
        request.action=INPUT_KEY_READ_TABLE;request.position=(uint16_t)(work->position+3u);work->stage=4;return request;
    case 4:
        work->destination=(uint8_t)reply;request.action=INPUT_KEY_READ_MODE;request.position=reply&2u;work->stage=5;return request;
    case 5:
        if(!(reply&32768u)) {work->stage=8;break;}
        request.action=INPUT_KEY_READ_TABLE;request.position=(uint16_t)(work->position+3u);work->stage=6;return request;
    case 6:
        work->destination=(uint8_t)reply;request.action=INPUT_KEY_READ_TABLE;request.position=(uint16_t)(work->position+4u);work->stage=11;return request;
    case 11:
        request.action=INPUT_KEY_WRITE_ACTION;request.position=work->destination;request.value=(uint8_t)reply;work->stage=8;return request;
    case 7:
        work->position=(uint16_t)(work->position+6u);request.action=INPUT_KEY_READ_TABLE;request.position=work->position;work->stage=12;return request;
    case 12:
        if(reply!=255) {work->stage=0;break;}
        if(!work->matches) {work->stage=8;break;}
        request.action=INPUT_KEY_READ_INDEX;work->stage=13;return request;
    case 13:request.action=INPUT_KEY_WRITE_INDEX;request.value=(uint8_t)(reply+1u);work->stage=14;return request;
    case 8:
        request.action=INPUT_KEY_WRITE_INDEX;work->position=0;work->stage=9;return request;
    case 9:
        if(!work->reset_budget) {request.action=INPUT_KEY_BOUND;return request;}
        request.action=INPUT_KEY_READ_TABLE;request.position=work->position;work->stage=10;return request;
    case 10:
        if(reply==255) return request;
        request.action=INPUT_KEY_WRITE_TABLE;request.position=(uint16_t)(work->position+5u);work->stage=15;return request;
    case 15:work->position=(uint16_t)(work->position+6u);work->reset_budget--;work->stage=9;break;
    default:return request;
    }
}
InputControlSource input_control_source(uint16_t mode)
{InputControlSource result={(uint16_t)(mode*2u),0};result.joystick=(uint8_t)((int16_t)result.position>=0);return result;}
uint16_t input_player_visits(uint16_t configured_count) {return configured_count==2 ? 2 : 1;}
InputCommands input_control_map(const InputJoystick *joystick)
{
    InputCommands commands={0,0,0,0,0};
    int horizontal=input_axis_direction(joystick->x,joystick->left,joystick->right);
    int vertical=input_axis_direction(joystick->y,joystick->up,joystick->down);
    if(horizontal<0) commands.left=65535;else if(horizontal>0) commands.right=65535;
    if(vertical<0) commands.up=65535;else if(vertical>0) commands.down=65535;
    if(joystick->buttons) commands.action=65535;
    return commands;
}
InputWaitAction input_wait_next(InputWaitWork *work,int changed)
{
    for(;;) switch(work->stage++) {
    case 0:return INPUT_WAIT_SCAN;
    case 1:if(!work->budget--) return INPUT_WAIT_BOUND;return INPUT_WAIT_RETRACE;
    case 2:return INPUT_WAIT_SAMPLE;
    case 3:if(changed) return INPUT_WAIT_DONE;return INPUT_WAIT_SERVICE;
    case 4:return INPUT_WAIT_SCAN;
    default:if(changed) return INPUT_WAIT_DONE;work->stage=1;break;
    }
}
