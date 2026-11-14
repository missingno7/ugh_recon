#ifndef NATIVE_TERMINAL_TAIL_H
#define NATIVE_TERMINAL_TAIL_H
#include <stdint.h>
typedef enum TerminalAction { TERMINAL_STOP_SOUND, TERMINAL_RESTORE_VIDEO,
    TERMINAL_RESTORE_INPUT, TERMINAL_EXIT, TERMINAL_COMPLETE } TerminalAction;
typedef struct TerminalTail { uint8_t cursor; } TerminalTail;
void terminal_tail_begin(TerminalTail *tail);
TerminalAction terminal_tail_next(TerminalTail *tail);
/* The saved-mode byte is supplied after sound returns, from the live owner. */
uint8_t terminal_tail_video_mode(uint8_t saved_mode);
#endif
