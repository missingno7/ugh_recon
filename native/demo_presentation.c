#include "demo_presentation.h"

static int presentation_signed(uint16_t word) {
    return word<32768u?(int)word:(int)word-65536;
}
static DemoPresentationAction presentation_service(DemoPresentationService service) {
    DemoPresentationAction action={DP_ACTION_SERVICE,service,0};return action;
}
static DemoPresentationAction presentation_value(DemoPresentationActionKind kind,uint16_t value) {
    DemoPresentationAction action={kind,DP_SERVICE_INITIALIZE,value};return action;
}
DemoPresentationCursor demo_presentation_begin(DemoPresentationKind kind) {
    DemoPresentationCursor cursor={kind,kind==DEMO_PRESENT_RUN?DP_INITIALIZE:DP_PREPARE};return cursor;
}
DemoPresentationAction demo_presentation_next(DemoPresentationCursor *cursor,const DemoPresentationInput *input) {
    /* At most three non-yielding branch cuts occur before the next observable
     * event. The bound diagnoses an invalid internal cursor, never truncates a
     * demo's potentially wrapping/interruptible outer run. */
    for(unsigned transitions=0;transitions<8;transitions++) {
        switch(cursor->phase) {
        case DP_INITIALIZE:cursor->phase=DP_CLEAR_EXIT;return presentation_service(DP_SERVICE_INITIALIZE);
        case DP_CLEAR_EXIT:cursor->phase=DP_CLEAR_LEVEL;return presentation_value(DP_ACTION_EXIT,0);
        case DP_CLEAR_LEVEL:cursor->phase=DP_CLEAR_STEP;return presentation_value(DP_ACTION_LEVEL,0);
        case DP_CLEAR_STEP:cursor->phase=DP_INITIAL_POLL;return presentation_value(DP_ACTION_STEP,4);
        case DP_INITIAL_POLL:cursor->phase=DP_LOOP;return presentation_service(DP_SERVICE_POLL_KEYBOARD);
        case DP_LOOP:
            if(presentation_signed(input->fade_level)<0) {cursor->phase=DP_TERMINAL;return presentation_value(DP_ACTION_DONE,input->exit_code);}
            if(presentation_signed(input->fade_level)<=256) {cursor->phase=DP_PALETTE_AFTER;return presentation_service(DP_SERVICE_PALETTE);}
            cursor->phase=DP_ERASE;return presentation_service(DP_SERVICE_RETRACE);
        case DP_PALETTE_AFTER:cursor->phase=DP_ERASE;return presentation_value(DP_ACTION_LEVEL,(uint16_t)(input->palette_work+input->fade_step));
        case DP_ERASE:cursor->phase=DP_WATER;return presentation_service(DP_SERVICE_ERASE);
        case DP_WATER:
            cursor->phase=DP_ADVANCE;
            if(presentation_signed(input->water_y)<192) return presentation_service(DP_SERVICE_WATER);
            break;
        case DP_ADVANCE:cursor->phase=DP_DRAW;return presentation_service(DP_SERVICE_ADVANCE);
        case DP_DRAW:cursor->phase=DP_SWAP;return presentation_service(DP_SERVICE_DRAW);
        case DP_SWAP:cursor->phase=DP_TEST;return presentation_service(DP_SERVICE_SWAP);
        case DP_TEST:cursor->phase=DP_TEST_AFTER;return presentation_service(DP_SERVICE_TEST);
        case DP_TEST_AFTER:
            if(input->finished) {cursor->phase=DP_FADE_CHECK;break;}
            cursor->phase=DP_JOYSTICK_AFTER;return presentation_service(DP_SERVICE_JOYSTICK);
        case DP_JOYSTICK_AFTER:
            if(input->joystick_idle) {cursor->phase=DP_KEYBOARD_AFTER;return presentation_service(DP_SERVICE_POLL_KEYBOARD);}
            cursor->phase=DP_FADE_CHECK;return presentation_value(DP_ACTION_EXIT,0);
        case DP_KEYBOARD_AFTER:
            if(!(input->key_word>>8)) {cursor->phase=DP_LOOP;return presentation_value(DP_ACTION_REPEAT,0);}
            cursor->phase=DP_FADE_CHECK;
            {uint16_t key=input->key_word&127u;return presentation_value(DP_ACTION_EXIT,key==16?65535u:key==1?1u:0u);}
        case DP_FADE_CHECK:
            if(presentation_signed(input->fade_step)<0) {cursor->phase=DP_LOOP;return presentation_value(DP_ACTION_REPEAT,0);}
            cursor->phase=DP_FADE_LEVEL;return presentation_value(DP_ACTION_STEP,65532u);
        case DP_FADE_LEVEL:cursor->phase=DP_REPEAT;return presentation_value(DP_ACTION_LEVEL,(uint16_t)(input->fade_level-4u));
        case DP_REPEAT:cursor->phase=DP_LOOP;return presentation_value(DP_ACTION_REPEAT,0);
        case DP_PREPARE:
            cursor->phase=cursor->kind==DEMO_PRESENT_COMPLETION?DP_MUSIC_STOP:DP_VECTOR;
            return presentation_service(cursor->kind==DEMO_PRESENT_ATTRACT?DP_SERVICE_PREPARE_NINETY:DP_SERVICE_PREPARE_ZERO);
        case DP_MUSIC_STOP:cursor->phase=DP_MUSIC_START;
            {DemoPresentationAction action=presentation_service(DP_SERVICE_MUSIC_STOP);action.value=17;return action;}
        case DP_MUSIC_START:cursor->phase=DP_VECTOR;
            {DemoPresentationAction action=presentation_service(DP_SERVICE_MUSIC_START);action.value=165;return action;}
        case DP_VECTOR:cursor->phase=DP_RUN;return presentation_value(DP_ACTION_VECTOR,(uint16_t)cursor->kind);
        case DP_RUN:cursor->phase=cursor->kind==DEMO_PRESENT_REVEAL?DP_REVEAL_X:DP_WRAPPER_DONE;return presentation_service(DP_SERVICE_RUN);
        case DP_REVEAL_X:cursor->phase=DP_REVEAL_WIDTH;return presentation_value(DP_ACTION_REVEAL_X,0);
        case DP_REVEAL_WIDTH:cursor->phase=DP_WRAPPER_DONE;return presentation_service(DP_SERVICE_REVEAL_WIDTH);
        case DP_WRAPPER_DONE:cursor->phase=DP_TERMINAL;return presentation_value(DP_ACTION_DONE,0);
        case DP_TERMINAL:case DEMO_PRESENT_PHASE_COUNT:return presentation_value(DP_ACTION_INVALID,0);
        }
    }
    return presentation_value(DP_ACTION_INVALID,0);
}
DemoFadeEffect demo_presentation_fade(uint16_t sprite,uint16_t level) {
    DemoFadeEffect effect={sprite==32767u,65532u,level};
    if(effect.triggered) effect.level=(uint16_t)(level-4u);
    return effect;
}
DemoRevealWidth demo_presentation_width(uint16_t position_x32) {
    DemoRevealWidth width;
    width.pixel_x=(uint16_t)((position_x32>>5)|((position_x32&32768u)?63488u:0));
    width.width_word=(uint16_t)(320u-width.pixel_x);
    /* Retained AL-only upper clamp: AH survives, negative values have no
     * lower clamp, and the published byte can therefore wrap. */
    if(presentation_signed(width.width_word)>127) width.width_word=(uint16_t)((width.width_word&65280u)|127u);
    width.width=(uint8_t)width.width_word;return width;
}
