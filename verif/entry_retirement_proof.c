#include "../native/actor_pass.c"
#include "../native/terminal_tail.c"
void __CPROVER_assert(int,const char *);
void __CPROVER_assume(int);
uint16_t nondet_word(void);
uint32_t nondet_count(void);
int nondet_int(void);
#define assert(x) __CPROVER_assert((x),#x)
int main(void) {
    uint16_t descriptor=nondet_word(),cursor=nondet_word();
    ActorCallback callback=(ActorCallback)nondet_int();
    ActorPass pass={nondet_word(),nondet_count()},saved=pass;
    __CPROVER_assume(pass.remaining<=32768u);
    ActorPassAction action=actor_pass_select(&pass,descriptor,callback);
    assert(pass.cursor==saved.cursor && pass.remaining==saved.remaining);
    if (!saved.remaining) assert(action==ACTOR_PASS_LIMIT);
    else if (descriptor==UINT16_MAX) assert(action==ACTOR_PASS_DONE);
    else if (callback<=ACTOR_CALLBACK_UNSUPPORTED || callback>=ACTOR_CALLBACK_COUNT)
        assert(action==ACTOR_PASS_UNSUPPORTED);
    else assert(action==ACTOR_PASS_CALL);
    if (pass.remaining) {
        actor_pass_resume(&pass,cursor);
        assert(pass.cursor==(uint16_t)(cursor+2u));
        assert(pass.remaining==saved.remaining-1u);
    }
    actor_pass_begin(&pass);assert(pass.cursor==0 && pass.remaining==32768u);
    TerminalTail tail;terminal_tail_begin(&tail);
    assert(terminal_tail_next(&tail)==TERMINAL_STOP_SOUND);
    assert(terminal_tail_next(&tail)==TERMINAL_RESTORE_VIDEO);
    assert(terminal_tail_next(&tail)==TERMINAL_RESTORE_INPUT);
    assert(terminal_tail_next(&tail)==TERMINAL_EXIT);
    assert(terminal_tail_next(&tail)==TERMINAL_COMPLETE);
    assert(terminal_tail_next(&tail)==TERMINAL_COMPLETE && tail.cursor==4);
    assert(terminal_tail_video_mode((uint8_t)cursor)==(uint8_t)cursor);
    actor_reserved_return();
}
