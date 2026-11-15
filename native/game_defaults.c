#include "game_defaults.h"
#include "boot_data.h"
#include <string.h>
GSStatus game_default_copy(GameServices *s,GameDefaultField field,void *out,size_t size) {
    if((unsigned)field>=GD_COUNT||!out)return GS_INVALID;
    if(size!=game_default_sizes[field])return GS_INVALID;
    for(size_t i=0;i<sizeof game_default_specs/sizeof *game_default_specs;i++) {
        const GameDefaultSpec *r=&game_default_specs[i];if(r->field!=field)continue;
        GSBytes bytes;GSResourceClass kind;
        GSStatus status=s->resources.view(s->resources_context,r->resource,&bytes,&kind);
        if(status!=GS_OK)return status;
        if(r->offset>bytes.size||r->size>bytes.size-r->offset||r->destination>size||r->size>size-r->destination)return GS_INVALID;
        memcpy((uint8_t*)out+r->destination,bytes.data+r->offset,r->size);
    }
    return GS_OK;
}
GSStatus game_picture_resource(GameServices *s,unsigned index,GSBytes *bytes) {
    if(index>=4)return GS_INVALID;
    GSResourceClass kind;
    return s->resources.view(s->resources_context,game_picture_ids[index],bytes,&kind);
}
