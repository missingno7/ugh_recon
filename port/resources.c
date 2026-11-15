#include "resources.h"
#include "hash.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static uint32_t u32(const uint8_t*p){return p[0]|(uint32_t)p[1]<<8|(uint32_t)p[2]<<16|(uint32_t)p[3]<<24;}
static uint64_t u64(const uint8_t*p){return u32(p)|(uint64_t)u32(p+4)<<32;}
static GSStatus reject(GSResourcePack *pack,char *error,size_t size,const char *reason){gs_resources_close(pack);if(error&&size)snprintf(error,size,"resource pack: %s",reason);return GS_INVALID;}
void gs_resources_close(GSResourcePack *pack){free(pack->storage);memset(pack,0,sizeof *pack);}
GSStatus gs_resources_open(GSResourcePack *pack,const char *path,const GSRequiredResource *required,size_t required_count,char *error,size_t error_size) {
 if(!pack||!path)return GS_INVALID;
 memset(pack,0,sizeof *pack);if(!required||!required_count)return reject(pack,error,error_size,"required admission manifest missing");
 FILE *file=fopen(path,"rb");if(!file)return reject(pack,error,error_size,"cannot open required file");
 if(fseek(file,0,SEEK_END)){fclose(file);return reject(pack,error,error_size,"cannot size file");}
 long length=ftell(file);if(length<128||length>16*1024*1024){fclose(file);return reject(pack,error,error_size,"invalid size");}
 rewind(file);pack->storage=malloc((size_t)length);if(!pack->storage){fclose(file);return reject(pack,error,error_size,"allocation failed");}
 size_t got=fread(pack->storage,1,(size_t)length,file);int io=ferror(file);fclose(file);if(got!=(size_t)length||io)return reject(pack,error,error_size,"short read");
 pack->size=(size_t)length;uint8_t *p=pack->storage;
 if(memcmp(p,"UGHRES1\0",8)||u32(p+8)!=1||u32(p+12)!=64)return reject(pack,error,error_size,"unsupported magic/version");
 uint8_t zero[16]={0};if(u32(p+20)||memcmp(p+112,zero,16)||u64(p+24)!=128||u64(p+40)!=(uint64_t)length)return reject(pack,error,error_size,"invalid header");
 pack->count=u32(p+16);uint64_t payload=128ull+64ull*pack->count;
 if(payload>(uint64_t)length||payload!=u64(p+32))return reject(pack,error,error_size,"invalid table bounds");
 pack->payload=(size_t)payload;uint8_t hash[32];gs_sha256(p+128,pack->payload-128,hash);if(memcmp(hash,p+48,32))return reject(pack,error,error_size,"table hash mismatch");
 gs_sha256(p+pack->payload,pack->size-pack->payload,hash);if(memcmp(hash,p+80,32))return reject(pack,error,error_size,"payload hash mismatch");
 if(pack->count!=required_count)return reject(pack,error,error_size,"required ID set differs");
 uint64_t previous=0;
 for(uint32_t i=0;i<pack->count;i++) {
  uint8_t *entry=p+128+64u*i;uint64_t id=u64(entry),offset=u64(entry+16),size=u64(entry+24);uint32_t kind=u32(entry+8);
  if(!id||(i&&id<=previous)||u32(entry+12)||kind<GS_IMMUTABLE||kind>GS_OPAQUE_MUTABLE)return reject(pack,error,error_size,"invalid or duplicate ID/class");
  previous=id;if(offset>pack->size-pack->payload||size>pack->size-pack->payload-offset)return reject(pack,error,error_size,"resource bounds overflow");
  const GSRequiredResource *r=required+i;
  if(r->id!=id||r->classification!=kind||r->size!=size||r->payload_offset!=offset||memcmp(r->sha256,entry+32,32))return reject(pack,error,error_size,"required ID/hash/class/alias missing or changed");
  gs_sha256(p+pack->payload+(size_t)offset,(size_t)size,hash);if(memcmp(hash,entry+32,32))return reject(pack,error,error_size,"resource hash mismatch");
 }
 /* Canonical payload has no hidden/unreferenced bytes. Admission also pins each
  * view's file-relative offset above, so equal bytes cannot detach a live alias. */
 size_t extent=pack->size-pack->payload;uint8_t *covered=calloc(extent?extent:1,1);
 if(!covered)return reject(pack,error,error_size,"coverage allocation failed");
 for(uint32_t i=0;i<pack->count;i++){const uint8_t *e=p+128+64u*i;memset(covered+(size_t)u64(e+16),1,(size_t)u64(e+24));}
 for(size_t i=0;i<extent;i++)if(!covered[i]){free(covered);return reject(pack,error,error_size,"unreferenced payload bytes");}
 free(covered);
 /* Refuse a writable alias of any immutable view, even a rehashed table. */
 for(uint32_t i=0;i<pack->count;i++) {
  const uint8_t *a=p+128+64u*i;if(u32(a+8)!=GS_IMMUTABLE)continue;
  uint64_t lo=u64(a+16),hi=lo+u64(a+24);if(lo==hi)continue;
  for(uint32_t j=0;j<pack->count;j++){const uint8_t*b=p+128+64u*j;if(u32(b+8)==GS_IMMUTABLE)continue;uint64_t x=u64(b+16),y=x+u64(b+24);if(lo<y&&x<hi)return reject(pack,error,error_size,"immutable view has writable alias");}
 }
 if(error&&error_size)*error=0;
 return GS_OK;
}
static const uint8_t *find(GSResourcePack *pack,GSResourceId id){
 size_t lo=0,hi=pack->count;while(lo<hi){size_t mid=lo+(hi-lo)/2;const uint8_t*e=pack->storage+128+64*mid;uint64_t value=u64(e);if(value==id)return e;if(value<id)lo=mid+1;else hi=mid;}return NULL;
}
static GSStatus view(void *ctx,GSResourceId id,GSBytes *bytes,GSResourceClass *kind){GSResourcePack*p=ctx;if(!p||!p->storage||!bytes||!kind)return GS_INVALID;const uint8_t*e=find(p,id);if(!e)return GS_UNSUPPORTED;*bytes=(GSBytes){p->storage+p->payload+(size_t)u64(e+16),(size_t)u64(e+24)};*kind=(GSResourceClass)u32(e+8);return GS_OK;}
static GSStatus mutable_view(void *ctx,GSResourceId id,GSMutableBytes *bytes){GSBytes read;GSResourceClass kind;if(!bytes)return GS_INVALID;GSStatus status=view(ctx,id,&read,&kind);if(status!=GS_OK)return status;if(kind==GS_IMMUTABLE)return GS_UNSUPPORTED;*bytes=(GSMutableBytes){(uint8_t*)read.data,read.size};return GS_OK;}
GSResourceOps gs_resources_operations(void){return (GSResourceOps){view,mutable_view};}
