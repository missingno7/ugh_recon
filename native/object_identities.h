#ifndef NATIVE_OBJECT_IDENTITIES_H
#define NATIVE_OBJECT_IDENTITIES_H
#include "resource_world.h"
#include "resource_catalog.h"
#include "actor_pass.h"
#include "hazards.h"
/* Data identities and callable roles are separate domains. These values never
 * contain an executable coordinate. The provider admits shipped graph edges;
 * verification alone imports/exports historical descriptor/cursor words. */
typedef enum ObjectIdentityStatus {
 OBJECT_IDENTITY_OK, OBJECT_IDENTITY_UNSUPPORTED
} ObjectIdentityStatus;
typedef enum ObjectResourceKind {
 OBJECT_RESOURCE_UNSUPPORTED, OBJECT_ACTOR_DESCRIPTOR, OBJECT_ENEMY_DESCRIPTOR,
 OBJECT_ITEM_DESCRIPTOR, OBJECT_JOURNEY, OBJECT_SCRIPT, OBJECT_ANIMATION,
 OBJECT_DROP_LIST
} ObjectResourceKind;
typedef struct ObjectResourceIdentity {
 ObjectResourceKind kind;
 ResourceWorldToken view;
 uint16_t position;
} ObjectResourceIdentity;
typedef enum ItemCallbackRole {
 ITEM_CALLBACK_UNSUPPORTED, ITEM_CALLBACK_SPAWN, ITEM_CALLBACK_ADVANCE,
 ITEM_CALLBACK_LAND, ITEM_CALLBACK_COLLECT
} ItemCallbackRole;
typedef enum ObjectCallbackKind {
 OBJECT_CALLBACK_UNSUPPORTED, OBJECT_CALLBACK_ACTOR, OBJECT_CALLBACK_ENEMY,
 OBJECT_CALLBACK_ITEM, OBJECT_CALLBACK_DEMO_EFFECT, OBJECT_CALLBACK_EMPTY
} ObjectCallbackKind;
typedef struct ObjectCallbackIdentity {
 ObjectCallbackKind kind;
 ActorCallback actor;
 HazardEntry enemy;
 ItemCallbackRole item;
 ResourceToken effect;
} ObjectCallbackIdentity;
typedef enum ObjectLinkKind {
 OBJECT_LINK_UNSUPPORTED, OBJECT_LINK_RESOURCE, OBJECT_LINK_CALLBACK,
 OBJECT_LINK_SPRITE, OBJECT_LINK_END, OBJECT_LINK_EMPTY
} ObjectLinkKind;
typedef struct ObjectGraphLink {
 ResourceWorldToken source;
 uint16_t member;
 ObjectLinkKind kind;
 ObjectResourceIdentity resource;
 ObjectCallbackIdentity callback;
 ResourceToken sprite;
} ObjectGraphLink;
/* Construct only a registered family/view/position. A script header has position
 * zero; its cursors name opcode boundaries (including the stop). Journey
 * positions are leg boundaries, including the terminal platform marker. */
ObjectIdentityStatus object_resource_identity(ObjectResourceKind kind,
 ResourceWorldToken view,uint16_t position,ObjectResourceIdentity *identity);
ObjectIdentityStatus object_resource_read(ObjectResourceIdentity identity,
 uint16_t displacement,uint16_t *value);
ObjectIdentityStatus object_callback_identity(ObjectCallbackIdentity role,
 ObjectCallbackIdentity *identity);
/* The extracted graph is the typed shipped profile, not a decoder for code
 * words. Scalar resource operands are read live through object_resource_read. */
ObjectIdentityStatus object_graph_link(ResourceWorldToken source,
 uint16_t member,ObjectGraphLink *link);
size_t object_graph_link_count(void);
ObjectIdentityStatus object_graph_link_at(size_t index,ObjectGraphLink *link);
#endif
