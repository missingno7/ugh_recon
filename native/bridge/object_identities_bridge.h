#ifndef OBJECT_IDENTITIES_BRIDGE_H
#define OBJECT_IDENTITIES_BRIDGE_H
#include "../object_identities.h"
/* Verification-only transports, deliberately absent from native headers. No
 * mapping in this interface returns a function or invokes an entry adapter. */
typedef enum ObjectLegacyCallbackFamily {
 OBJECT_LEGACY_ACTOR, OBJECT_LEGACY_ENEMY, OBJECT_LEGACY_ITEM, OBJECT_LEGACY_EFFECT
} ObjectLegacyCallbackFamily;
typedef struct ObjectLegacyResource {ObjectResourceKind kind;ResourceWorldToken view;uint16_t word;} ObjectLegacyResource;
typedef struct ObjectLegacyCallback {ObjectLegacyCallbackFamily family;uint16_t word,role;} ObjectLegacyCallback;
ObjectIdentityStatus object_resource_from_legacy(ObjectResourceKind kind,uint16_t word,ObjectResourceIdentity *identity);
ObjectIdentityStatus object_resource_to_legacy(ObjectResourceIdentity identity,uint16_t *word);
ObjectIdentityStatus object_callback_from_legacy(ObjectLegacyCallbackFamily family,uint16_t word,ObjectCallbackIdentity *identity);
ObjectIdentityStatus object_callback_to_legacy(ObjectCallbackIdentity identity,uint16_t *word);
/* Read the resource operand on every visit, then type it in the verifier. This
 * preserves mutable resource views and never caches a frame-start callback. */
ObjectIdentityStatus object_live_link(ResourceWorldToken source,uint16_t member,ObjectGraphLink *link);
#endif
