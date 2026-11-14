#ifndef NATIVE_INPUT_H
#define NATIVE_INPUT_H
#include <stdint.h>

/* One logical input owner. Front-end/session changes to modes, player count
 * and commands are writes to this same storage, never a second input owner.
 * Projections borrowed by actors/player physics do not own these words. */
typedef struct InputCommands {uint16_t up,down,left,right,action;} InputCommands;
typedef struct InputJoystick {
    uint16_t present,x,y,buttons,double_x,double_y;
    uint16_t left,right,up,down;
} InputJoystick;
typedef struct InputState {
    uint8_t latest_scan,current_scan,previous_scan,change,sequence_index,enabled_axes;
    uint16_t loop_limit,control_mode[2],player_count;
    InputJoystick joysticks[2];InputCommands commands[2];
    uint16_t calibration_reset_words[4]; /* only observed use: clear at detection */
} InputState;
typedef struct InputKeyRecord {uint8_t scans[3],destination,value,candidate;} InputKeyRecord;

typedef struct InputScanChange {uint8_t previous,current,change;} InputScanChange;
InputScanChange input_scan_change(uint8_t previous,uint8_t delivered);
typedef struct InputThresholds {uint16_t low,high,doubled;} InputThresholds;
InputThresholds input_thresholds(uint16_t measured);
int input_axis_direction(uint16_t measured,uint16_t low,uint16_t high);
uint16_t input_calibration_limit(const uint16_t doubled[4]);
int input_joystick_present(uint8_t discharged,uint8_t joystick);
int input_controls_need_sample(uint16_t first,uint16_t second,uint16_t count);
void input_calibration_start(InputState *state);
void input_calibration_detect(InputState *state,unsigned joystick);
void input_calibration_apply(InputState *state,unsigned joystick);
void input_state_scan(InputState *state,uint8_t delivered);

/* DOS timing service adapter: one raw delivery per iteration. A port may
 * instead supply final x/y counts and the two active-high button groups.
 * Counts, not preclassified directions, remain the game's calibration input. */
typedef struct InputAxisTimer {
    uint16_t remaining,latched[4];uint32_t budget;uint8_t completed;
} InputAxisTimer;
InputAxisTimer input_axis_begin(uint16_t limit,uint8_t enabled);
int input_axis_delivery(InputAxisTimer *work,uint8_t delivered);
uint16_t input_axis_count(uint16_t live_limit,uint16_t latched);
uint16_t input_button_bits(uint8_t delivered,unsigned joystick);

/* Byte requests bind a borrowed cyclic sequence table. Valid records have
 * three scans plus destination/value/candidate. Unchecked index lookahead,
 * mutable sentinels and action/table aliases are delivered synchronously. */
typedef enum InputKeyAction {
    INPUT_KEY_DONE,INPUT_KEY_BOUND,INPUT_KEY_READ_TABLE,INPUT_KEY_WRITE_TABLE,
    INPUT_KEY_READ_MODE,INPUT_KEY_READ_INDEX,INPUT_KEY_WRITE_INDEX,INPUT_KEY_WRITE_ACTION
} InputKeyAction;
typedef struct InputKeyRequest {InputKeyAction action;uint16_t position;uint8_t value;} InputKeyRequest;
typedef struct InputKeyWork {
    uint32_t budget,reset_budget;uint16_t position,index;
    uint8_t scan,matches,destination,stage;
} InputKeyWork;
InputKeyWork input_key_begin(uint8_t scan,uint8_t index,int reset_only);
InputKeyRequest input_key_next(InputKeyWork *work,uint16_t reply);

/* Source position is the wrapping word-index encoding in a control mode.
 * Normal UI values select one of two typed joystick records. The bridge
 * retains unchecked source positions; all admitted mapped reads lie above
 * the command words and cannot alias them. */
typedef struct InputControlSource {uint16_t position;uint8_t joystick;} InputControlSource;
InputControlSource input_control_source(uint16_t mode);
InputCommands input_control_map(const InputJoystick *joystick);
uint16_t input_player_visits(uint16_t configured_count);

/* Initial scan change is deliberately discarded by the blocking wait. */
typedef enum InputWaitAction {INPUT_WAIT_SCAN,INPUT_WAIT_RETRACE,INPUT_WAIT_SAMPLE,INPUT_WAIT_SERVICE,INPUT_WAIT_DONE,INPUT_WAIT_BOUND} InputWaitAction;
typedef struct InputWaitWork {uint32_t budget;uint8_t stage;} InputWaitWork;
InputWaitAction input_wait_next(InputWaitWork *work,int changed);
#endif
