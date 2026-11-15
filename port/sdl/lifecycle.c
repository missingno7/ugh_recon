#include "backend.h"
/* No fabricated startup, teardown or external-hook success. Step7 must connect
 * the existing lifetime/terminal prefixes to the typed providers. */
static GSStatus request(void *ctx,GSLifecycleRequest action,uint8_t *reply) {
    (void)ctx;(void)action;(void)reply;return GS_UNSUPPORTED;
}
static GSStatus binding(void *ctx,GSLifecycleBindingRole role,GSVectorOp op,GSBinding value,GSBinding *reply){(void)ctx;(void)role;(void)op;(void)value;(void)reply;return GS_UNSUPPORTED;}
GSLifecycleOps gs_lifecycle_operations(void){return (GSLifecycleOps){request,binding,NULL,NULL,NULL};}
