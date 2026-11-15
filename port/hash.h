#ifndef UGH_PORT_HASH_H
#define UGH_PORT_HASH_H
#include <stddef.h>
#include <stdint.h>
void gs_sha256(const void *,size_t,uint8_t [32]);
#endif
