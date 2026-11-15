#include "compose_session.h"
#include <string.h>
#include "session_data_generated.h"
GSStatus session_data_view(GameServices *s,SessionDataView v,GSBytes *out){
    GSBytes b;GSResourceClass kind;
    GSStatus status=s->resources.view(s->resources_context,v.resource,&b,&kind);
    if(status!=GS_OK)return status;
    if(v.offset>b.size||v.size>b.size-v.offset)return GS_INVALID;
    *out=(GSBytes){b.data+v.offset,v.size};return GS_OK;
}
uint16_t session_data_count(uint16_t bytes){return bytes==2?69:bytes==4?81:0;}
GSStatus session_data_level(uint16_t players,uint16_t level,const SessionLevelSpec **out){
    if(!out||players<1||players>2)return GS_UNSUPPORTED;
    uint16_t key=session_loader_level_key(level);
    unsigned index=key/2u;
    if(index>=session_data_count((uint16_t)(players*2u)))return GS_UNSUPPORTED;
    *out=session_levels+session_orders[players-1][index];return GS_OK;
}
GSStatus session_data_passwords(GameServices *s,uint16_t bytes,GSBytes *out){
    if(bytes!=2&&bytes!=4)return GS_UNSUPPORTED;
    return session_data_view(s,session_password_lists[(bytes-2u)/2u],out);
}
GSStatus session_data_password(GameServices *s,uint16_t bytes,uint16_t level,GSBytes *out){
    GSBytes list;GSStatus status=session_data_passwords(s,bytes,&list);if(status!=GS_OK)return status;
    /* A caller supplies the list ordinal; introduction uses the level byte. */
    size_t at=0;
    for(uint16_t i=0;i<level;i++){
        while(at<list.size&&list.data[at]&&list.data[at]!=255)at++;
        if(at>=list.size||list.data[at]==255)return GS_UNSUPPORTED;
        at++;
    }
    size_t end=at;while(end<list.size&&list.data[end]&&list.data[end]!=255)end++;
    if(end>=list.size||list.data[end]==255)return GS_UNSUPPORTED;
    *out=(GSBytes){list.data+at,end-at+1};return GS_OK;
}
GSStatus session_data_maps(GameServices *s,GSBytes *out){return session_data_view(s,session_maps,out);}
GSStatus game_session_construct(GameWorld *w,GameServices *s){
    if(!w||!s)return GS_INVALID;
    memset(&w->session,0,sizeof w->session);
    /* DATA defaults are independently checked by the build-time extractor. */
    for(size_t i=0;i<sizeof session_player_fields/sizeof *session_player_fields;i++){
        const SessionPlayerDefault *f=session_player_fields+i;
        GSBytes b;GSStatus status=session_data_view(s,f->data,&b);if(status!=GS_OK)return status;
        uint16_t value=(uint16_t)(b.data[0]|(uint16_t)b.data[1]<<8);
        memcpy((uint8_t*)&w->session.players+f->member,&value,2);
    }
    w->session.ready=1;return GS_OK;
}
