#ifndef SESSION_ACTOR_RENDER_H
#define SESSION_ACTOR_RENDER_H
#include "ugh.h"
/* Original inline passes: no additional emulated near-return word. The slot
 * policy and history are owned by actor_render, not the session adapter. */
int actor_render_session_GAME_ERASE(Regs *r);
int actor_render_session_GAME_DRAW(Regs *r);
int actor_render_session_GAME_OVERLAY(Regs *r);
#endif
