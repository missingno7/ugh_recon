#include "backend.h"
#include <stdio.h>
#include <string.h>
#include <windows.h>
GSStatus gs_files_init(GSSdlFiles *f,const char *path) {
    if(!path||strlen(path)>=sizeof f->path-32)return GS_INVALID;
    memset(f,0,sizeof *f);strcpy(f->path,path);
    FILE *in=fopen(path,"rb");if(!in){
        DWORD attributes=GetFileAttributesA(path),error=GetLastError();
        return attributes==INVALID_FILE_ATTRIBUTES&&(error==ERROR_FILE_NOT_FOUND||error==ERROR_PATH_NOT_FOUND)?GS_OK:GS_IO_ERROR;
    }
    size_t count=fread(f->data,1,107,in);int extra=fgetc(in),failed=ferror(in);fclose(in);
    if(extra!=EOF||failed)return GS_INVALID;
    f->exists=1;f->length=(uint16_t)count;return GS_OK;
}
static GSStatus persist(void *ctx);
static GSStatus open_scores(void *ctx,int create,GSFileReply *reply) {
    GSSdlFiles *f=ctx;if(!reply)return GS_INVALID;
    if(!create&&!f->exists){*reply=(GSFileReply){2,1};return GS_OK;}
    for(unsigned i=5;i<32;i++)if(!f->handles[i].open) {
        f->handles[i].open=1;f->handles[i].write=(uint8_t)!!create;f->handles[i].position=0;
        if(create){f->exists=1;f->length=0;f->dirty=1;}
        *reply=(GSFileReply){(uint16_t)i,0};return GS_OK;
    }*reply=(GSFileReply){4,1};return GS_OK;
}
static int valid(GSSdlFiles *f,uint16_t handle){return handle>=5&&handle<32&&f->handles[handle].open;}
static GSStatus read_scores(void *ctx,uint16_t handle,uint8_t *bytes,uint16_t count,GSFileReply *reply) {
    GSSdlFiles *f=ctx;if(!reply||(!bytes&&count))return GS_INVALID;
    if(!valid(f,handle)){*reply=(GSFileReply){6,1};return GS_OK;}
    unsigned pos=f->handles[handle].position,n=pos<f->length?f->length-pos:0;if(n>count)n=count;
    if(n)memcpy(bytes,f->data+pos,n);
    f->handles[handle].position=(uint16_t)(pos+n);*reply=(GSFileReply){(uint16_t)n,0};return GS_OK;
}
static GSStatus write_scores(void *ctx,uint16_t handle,const uint8_t *bytes,uint16_t count,GSFileReply *reply) {
    GSSdlFiles *f=ctx;if(!reply||(!bytes&&count))return GS_INVALID;
    if(!valid(f,handle)){*reply=(GSFileReply){6,1};return GS_OK;}
    if(!f->handles[handle].write){*reply=(GSFileReply){5,1};return GS_OK;}
    unsigned pos=f->handles[handle].position;if(count>107-pos)return GS_UNSUPPORTED;
    if(count)memcpy(f->data+pos,bytes,count);
    f->handles[handle].position=(uint16_t)(pos+count);
    if(!count||f->length<pos+count)f->length=(uint16_t)(pos+count);
    f->dirty=1;*reply=(GSFileReply){count,0};
    /* DOS writes reach the file at once, and the original never closes its
     * save handle, so write through to disk here rather than on close. */
    return persist(ctx);
}
static GSStatus close_scores(void *ctx,uint16_t handle,GSFileReply *reply) {
    GSSdlFiles *f=ctx;if(!reply)return GS_INVALID;
    if(!valid(f,handle)){*reply=(GSFileReply){6,1};return GS_OK;}
    f->handles[handle].open=0;*reply=(GSFileReply){0,0};return GS_OK;
}
static GSStatus persist(void *ctx) {
    GSSdlFiles *f=ctx;if(!f->dirty)return GS_OK;
    char path[4096];if(snprintf(path,sizeof path,"%s.tmp.%lu",f->path,GetCurrentProcessId())>=(int)sizeof path)return GS_INVALID;
    FILE *out=fopen(path,"wb");if(!out)return GS_IO_ERROR;
    int ok=fwrite(f->data,1,f->length,out)==f->length;
    if(fflush(out))ok=0;
    if(fclose(out))ok=0;
    if(!ok){DeleteFileA(path);return GS_IO_ERROR;}
    if(!MoveFileExA(path,f->path,MOVEFILE_REPLACE_EXISTING|MOVEFILE_WRITE_THROUGH)){DeleteFileA(path);return GS_IO_ERROR;}
    f->dirty=0;return GS_OK;
}
GSFilesOps gs_files_operations(void){return (GSFilesOps){open_scores,read_scores,write_scores,close_scores,persist};}
