#ifndef NATIVE_COMPOSE_FRAME_H
#define NATIVE_COMPOSE_FRAME_H
#include "compose_session.h"
/* Execute one accepted sequencing request. Palette reply belongs to the
 * continuation, not a second fade owner. No frame limit is a game rule. */
GSStatus game_frame_execute(GameWorld *,GameServices *,SessionRequest,uint16_t *);
#endif
