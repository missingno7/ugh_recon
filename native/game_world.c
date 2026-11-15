#include "game_boot.h"
#include "game_defaults.h"
#include <string.h>
static GSStatus word(GameServices *s,GameDefaultField f,uint16_t *out) {
    uint8_t b[2];GSStatus status=game_default_copy(s,f,b,2);
    if(status==GS_OK)*out=(uint16_t)(b[0]|(uint16_t)b[1]<<8);
    return status;
}
#define COPY(f,p,n) do{GSStatus status=game_default_copy(s,f,p,n);if(status!=GS_OK)return status;}while(0)
#define WORD(f,p) do{GSStatus status=word(s,f,p);if(status!=GS_OK)return status;}while(0)
GSStatus game_world_construct(GameWorld *w,GameServices *s) {
    if(!w||!s||!s->resources.view)return GS_INVALID;
    /* Explicit cold defaults for untouched, zero-initialized game allocations.
     * Initialized constructor fields come from independently admitted templates. */
    memset(w,0,sizeof *w);
    uint8_t random[8];COPY(GD_RANDOM,random,sizeof random);
    for(unsigned i=0;i<4;i++)w->random.word[i]=(uint16_t)(random[2*i]|(uint16_t)random[2*i+1]<<8);
    COPY(GD_SCORES,w->front.score_rows,sizeof w->front.score_rows);
    COPY(GD_SEQUENCE,w->input.sequence,sizeof w->input.sequence);
    COPY(GD_BASE_PALETTE,w->palette.base,sizeof w->palette.base);
    COPY(GD_FADED_PALETTE,w->palette.faded,sizeof w->palette.faded);
    WORD(GD_PLAYERS,&w->run.configuration.players);
    WORD(GD_PLAYER_BYTES,&w->run.configuration.player_bytes);
    WORD(GD_CONTROL_ONE,&w->run.configuration.control_mode[0]);
    WORD(GD_CONTROL_TWO,&w->run.configuration.control_mode[1]);
    WORD(GD_DIFFICULTY,&w->run.configuration.difficulty);
    COPY(GD_LATEST,&w->input.latest,1);COPY(GD_PREVIOUS,&w->input.previous,1);
    WORD(GD_SCAN,&w->input.current_scan_storage);COPY(GD_CHANGE,&w->input.change,1);
    COPY(GD_INDEX,&w->input.index,1);WORD(GD_AXES,&w->input.enabled_axis_storage);
    WORD(GD_LIMIT,&w->input.loop_limit);
    COPY(GD_ROW_STRIDE,&w->front.row_stride,1);
    COPY(GD_FILE_HANDLE,w->front.file_handle_bytes,2);
    COPY(GD_OPERATOR_INDEX,w->audio.operator_index,9);
    COPY(GD_SAVED_MODE,&w->lifecycle.saved_bios_video_mode,1);
    /* The unpack destination is a bounded codec allocation, initially zero.
     * Picture IDs must resolve before platform effects begin. */
    for(unsigned i=0;i<4;i++){GSBytes bytes;GSStatus status=game_picture_resource(s,i,&bytes);if(status!=GS_OK)return status;if(bytes.size<12)return GS_INVALID;}
    return GS_OK;
}
