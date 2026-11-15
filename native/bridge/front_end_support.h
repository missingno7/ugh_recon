#ifndef NATIVE_FRONT_END_SUPPORT_H
#define NATIVE_FRONT_END_SUPPORT_H
#include "platform.h"
#include "../front_end.h"
#include "../front_end_world.h"
/* The native continuation is projected only for an existing service request.
 * Replies are accepted at that cut, including deliberately changed registers. */
static inline void front_editor_request(Regs *r,const NativeFrontEditor *editor) {
 r->si=editor->position;r->bx=editor->blink_word;
}
static inline void front_editor_reply(NativeFrontEditor *editor,const Regs *r) {
 editor->position=r->si;editor->blink_word=r->bx;
}
#define ECALL(n,ret) do { front_editor_request(r,&editor);int result=ugh_call_near(G(n),ret,r);front_editor_reply(&editor,r);if(result)return result; } while(0)
static inline uint8_t compare_byte(Regs *r,uint8_t a,uint8_t b) {
    uint8_t v=(uint8_t)(a-b);
    flag(r,CF,a<b); flag(r,OF,((a^b)&(a^v)&128u)!=0);
    flag(r,AF,((a^b^v)&16u)!=0); szp(r,v,8); return v;
}

static inline uint16_t increment_word(Regs *r,uint16_t v) {
    uint16_t carry=r->flags&CF;
    v=add16(r,v,1,0); flag(r,CF,carry); return v;
}

static inline void front_text_request(Regs *r,const NativeFrontTextCursor *cursor) {
 r->si=cursor->position;r->bx=cursor->x;r->cx=cursor->y;
}
static inline void front_text_reply(NativeFrontTextCursor *cursor,const Regs *r) {
 cursor->position=r->si;cursor->x=r->bx;cursor->y=r->cx;
}
static inline uint8_t front_text_character(Regs *r,NativeFrontTextCursor *cursor) {
    uint8_t value=frontend_read8(r->ds,cursor->position);
    cursor->position=(uint16_t)(cursor->position+step(r));r->si=cursor->position;
    set_al(r,value);return value;
}
static inline uint8_t load_character(Regs *r) {
    NativeFrontTextCursor cursor={r->si,r->bx,r->cx};return front_text_character(r,&cursor);
}

static inline void push(Regs *r,uint16_t v) { r->sp=(uint16_t)(r->sp-2); wr16(r->ss,r->sp,v); }

static inline uint16_t pop(Regs *r) { uint16_t v=rd16(r->ss,r->sp); r->sp=(uint16_t)(r->sp+2); return v; }

static inline uint8_t add_byte(Regs *r,uint8_t a,uint8_t b) {
    uint8_t v=(uint8_t)(a+b); flag(r,CF,(unsigned)a+b>255);
    flag(r,OF,((~(a^b))&(a^v)&128)!=0); flag(r,AF,((a^b^v)&16)!=0); szp(r,v,8); return v;
}

static inline uint8_t inc_byte(Regs *r,uint8_t a) {
    uint16_t cf=r->flags&CF; uint8_t v=add_byte(r,a,1); flag(r,CF,cf); return v;
}

static inline int menu_far(Regs *r,uint16_t seg,uint16_t off,uint16_t ret,unsigned bytes) {
    push(r,r->cs); push(r,ret); int st=ugh_dispatch(seg,off,r); if(st) return st;
    r->sp=(uint16_t)(r->sp+4); r->sp=add16(r,r->sp,(uint16_t)bytes,0); return UGH_OK;
}

/* Replays only the original comparison/AL flags. Native FrontEditCommand
 * decides acceptance, capacity and writes; no input state is owned here. */
static inline void editor_compare_trace(Regs *r,uint8_t ch,int spaces) {
    int accepted=0;compare_byte(r,ch,'A');
    if(ch>='A') {compare_byte(r,ch,'Z');if(ch<='Z') accepted=1;}
    if(!accepted) {compare_byte(r,ch,'a');if(ch>='a') {compare_byte(r,ch,'z');if(ch<='z') {ch=compare_byte(r,ch,32);set_al(r,ch);accepted=1;}}}
    if(!accepted) {compare_byte(r,ch,'0');if(ch>='0') {compare_byte(r,ch,'9');if(ch<='9') accepted=1;}}
    if(!accepted && spaces) compare_byte(r,ch,32);
}
#endif
