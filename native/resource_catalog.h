#ifndef NATIVE_RESOURCE_CATALOG_H
#define NATIVE_RESOURCE_CATALOG_H
#include <stddef.h>
#include <stdint.h>
#include "actors.h"
enum { RESOURCE_SPRITE_RECORDS=662,RESOURCE_CODEC_BYTES=60 };
typedef enum ResourceKind {RESOURCE_SPRITE_RECORD=1,RESOURCE_CODEC_TABLE,RESOURCE_DEMO_EFFECT} ResourceKind;
typedef struct ResourceToken {ResourceKind kind;uint16_t index;} ResourceToken;
typedef struct ResourceSpriteRecord {uint16_t source_offset,dimensions;} ResourceSpriteRecord;
typedef struct ResourceTableView {const uint8_t *bytes;size_t size;int16_t first_index;uint8_t entry_width;} ResourceTableView;
typedef struct NativeResourceCatalog {ResourceSpriteRecord sprites[RESOURCE_SPRITE_RECORDS];} NativeResourceCatalog;
typedef enum ResourceStatus {RESOURCE_OK,RESOURCE_INVALID,RESOURCE_IMMUTABLE} ResourceStatus;
/* Bootstrap access belongs to the provider. Consumers borrow the APIs below. */
NativeResourceCatalog *native_resource_catalog(void);
/* Provider initialization, once per cold resource lifetime; not a game store. */
void resource_provider_load_codec(const uint8_t bytes[RESOURCE_CODEC_BYTES]);
int resource_token_valid(ResourceToken token);
ResourceStatus resource_sprite(ResourceToken token,ResourceSpriteRecord *view);
ResourceStatus resource_table(ResourceToken token,ResourceTableView *view);
ResourceStatus resource_effect(ResourceToken token,DemoMotionEffect *effect);
ResourceStatus resource_read(ResourceToken token,unsigned lane,uint8_t *value);
ResourceStatus resource_store(ResourceToken token,unsigned lane,uint8_t value);
#endif
