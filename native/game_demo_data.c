#include "compose_demo.h"
#include "game_defaults.h"
#include "actor_resources.h"
#include <string.h>
typedef struct GameDemoDataView {GSResourceId resource;size_t offset,size;} GameDemoDataView;
typedef struct GameDemoSpec {ObjectResourceIdentity identity;GameDemoDataView data;size_t offset;uint16_t effect;} GameDemoSpec;
typedef struct GameDemoVector {DemoPresentationKind kind;size_t count;ObjectResourceIdentity scripts[15];} GameDemoVector;
typedef struct GameDemoBoundary {uint16_t view,position;} GameDemoBoundary;
#include "demo_data.h"
static GSStatus data_view(GameServices *s,GameDemoDataView v,GSBytes *out){
    GSBytes bytes;GSResourceClass kind;GSStatus status=s->resources.view(s->resources_context,v.resource,&bytes,&kind);
    if(status!=GS_OK)return status;
    if(v.offset>bytes.size||v.size>bytes.size-v.offset)return GS_INVALID;
    *out=(GSBytes){bytes.data+v.offset,v.size};return GS_OK;
}
static uint16_t data_word(const uint8_t *b){return (uint16_t)(b[0]|(uint16_t)b[1]<<8);}
GSStatus game_demo_construct(GameWorld *w,GameServices *s){
    if(!w||!s||!s->resources.view)return GS_INVALID;
    /* Zero DATA defaults, checked independently by the build-time admission. */
    memset(&w->actors,0,sizeof w->actors);memset(&w->enemies,0,sizeof w->enemies);memset(&w->items,0,sizeof w->items);
    memset(&w->demo_resources,0,sizeof w->demo_resources);
    for(size_t i=0;i<GAME_DEMO_SCRIPTS;i++){
        const GameDemoSpec *spec=demo_specs+i;GSBytes b;GSStatus status=data_view(s,spec->data,&b);if(status!=GS_OK)return status;
        if(spec->offset>GAME_DEMO_RESOURCE_BYTES||b.size>GAME_DEMO_RESOURCE_BYTES-spec->offset)return GS_INVALID;
        memcpy(w->demo_resources.bytes+spec->offset,b.data,b.size);
        w->demo_resources.scripts[i]=(GameDemoResource){spec->identity,{.kind=OBJECT_CALLBACK_DEMO_EFFECT,.effect={RESOURCE_DEMO_EFFECT,spec->effect}},spec->offset,b.size};
    }
    for(unsigned i=0;i<RESOURCE_SPRITE_RECORDS;i++){
        GSBytes bank;uint16_t source,dimensions;GSStatus status=game_front_sprite(s,i,&bank,&source,&dimensions);if(status!=GS_OK)return status;
        w->sprite_catalog.sprites[i]=(ResourceSpriteRecord){source,dimensions};
    }
#define DEFAULT(name,member) do{GSBytes b;GSStatus status=data_view(s,demo_default_##name,&b);if(status!=GS_OK)return status;w->member=b.size==1?b.data[0]:data_word(b.data);}while(0)
    DEFAULT(WaterSurfaceFrameCountdown,presentation.weather.countdown);
    DEFAULT(WaterSurfaceFrame,presentation.weather.frame);
    DEFAULT(WaterSurfaceByteOffset,presentation.weather.byte_offset);
    DEFAULT(DemoExitCode,demo_exit);DEFAULT(VgaRowStrideBytes,demo_resources.row_stride);
#undef DEFAULT
    w->demo_resources.ready=1;return GS_OK;
}
GSStatus game_demo_resource(GameWorld *w,ObjectResourceIdentity id,GSBytes *out){
    if(!w||!out||!w->demo_resources.ready||id.kind!=OBJECT_SCRIPT)return GS_UNSUPPORTED;
    int admitted=0;
    for(size_t i=0;i<sizeof demo_boundaries/sizeof *demo_boundaries;i++)if(demo_boundaries[i].view==id.view.index&&demo_boundaries[i].position==id.position){admitted=1;break;}
    if(!admitted)return GS_UNSUPPORTED;
    for(size_t i=0;i<GAME_DEMO_SCRIPTS;i++){
        const GameDemoResource *r=w->demo_resources.scripts+i;
        if(id.view.index!=r->identity.view.index)continue;
        /* A header or a live opcode boundary is admitted. Never admit an
         * interior byte merely because it is inside the resource allocation. */
        if(r->offset>GAME_DEMO_RESOURCE_BYTES||r->size>GAME_DEMO_RESOURCE_BYTES-r->offset||r->size<10)return GS_UNSUPPORTED;
        uint8_t *b=w->demo_resources.bytes+r->offset;
        DemoMotionScript script={.code=b+8,.code_size=r->size-8};
        if(id.position && (id.position<8||!demo_script_boundary(&script,id.position-8)))return GS_UNSUPPORTED;
        *out=(GSBytes){b+id.position,r->size-id.position};return GS_OK;
    }return GS_UNSUPPORTED;
}
GSStatus game_demo_vector(DemoPresentationKind kind,ObjectResourceIdentity *out,size_t *count){
    if(!out||!count)return GS_INVALID;
    for(size_t i=0;i<sizeof demo_vectors/sizeof *demo_vectors;i++)if(demo_vectors[i].kind==kind){
        *count=demo_vectors[i].count;memcpy(out,demo_vectors[i].scripts,*count*sizeof *out);return GS_OK;
    }return GS_UNSUPPORTED;
}
/* Borrow compressed map DATA through the same admitted pack as every script. */
GSStatus game_demo_map_resource(GameServices *s,GSBytes *out){return data_view(s,demo_maps,out);}
