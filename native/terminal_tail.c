#include "terminal_tail.h"
void terminal_tail_begin(TerminalTail *tail) { tail->cursor=0; }
TerminalAction terminal_tail_next(TerminalTail *tail) {
    static const TerminalAction order[]={TERMINAL_STOP_SOUND,TERMINAL_RESTORE_VIDEO,
        TERMINAL_RESTORE_INPUT,TERMINAL_EXIT};
    if (tail->cursor>=4) return TERMINAL_COMPLETE;
    return order[tail->cursor++];
}
uint8_t terminal_tail_video_mode(uint8_t saved_mode) { return saved_mode; }
