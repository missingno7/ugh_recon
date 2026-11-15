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

static GSStatus front_view(GameServices *s,GameFrontDataView spec,GSBytes *out) {
    GSBytes bytes;GSResourceClass kind;
    GSStatus status=s->resources.view(s->resources_context,spec.resource,&bytes,&kind);
    if(status!=GS_OK)return status;
    if(spec.offset>bytes.size||spec.size>bytes.size-spec.offset)return GS_INVALID;
    *out=(GSBytes){bytes.data+spec.offset,spec.size};return GS_OK;
}
GSStatus game_front_sprite(GameServices *s,unsigned sprite,GSBytes *bank,uint16_t *offset,uint16_t *dimensions) {
    if(sprite>=662)return GS_UNSUPPORTED;
    GSBytes record;GSResourceClass kind;
    GSStatus status=s->resources.view(s->resources_context,(UINT64_C(1)<<32)|sprite,&record,&kind);
    if(status!=GS_OK)return status;
    if(record.size!=4)return GS_INVALID;
    *offset=(uint16_t)(record.data[0]|(uint16_t)record.data[1]<<8);
    *dimensions=(uint16_t)(record.data[2]|(uint16_t)record.data[3]<<8);
    return front_view(s,game_front_banks[sprite>=547?3:sprite>=298?2:sprite>=217?1:0],bank);
}
GSStatus game_front_label(GameServices *s,unsigned kind,unsigned index,GSBytes *out) {
    static const unsigned counts[]={3,2,3},starts[]={0,3,5};
    if(kind>=3||index>=counts[kind])return GS_UNSUPPORTED;
    return front_view(s,game_front_labels[starts[kind]+index],out);
}
