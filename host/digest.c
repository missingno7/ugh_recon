/* Same boundaries, stack exclusion and raw device/log bytes as wholegame.record.
 * Windows CNG is used only for SHA256, never for gameplay state. */
#include "host.h"
#include <windows.h>
#include <bcrypt.h>
#include <stddef.h>
static BCRYPT_ALG_HANDLE algorithm;
static BCRYPT_HASH_HANDLE rolling;
static void check(NTSTATUS s) { if(s<0) host_fail("SHA256 service failed"); }
void host_digest_init(void) {
    check(BCryptOpenAlgorithmProvider(&algorithm,BCRYPT_SHA256_ALGORITHM,NULL,0));
    check(BCryptCreateHash(algorithm,&rolling,NULL,0,NULL,0,0));
}
static void update(BCRYPT_HASH_HANDLE h,const void *p,unsigned size) {
    if(size) check(BCryptHashData(h,(PUCHAR)p,size,0));
}
static void finish(BCRYPT_HASH_HANDLE h,char hex[65]) {
    uint8_t bytes[32]; check(BCryptFinishHash(h,bytes,32,0)); BCryptDestroyHash(h);
    for(unsigned i=0;i<32;i++) sprintf(hex+2*i,"%02x",bytes[i]);
}
void host_sha256(const void *p,unsigned size,char hex[65]) {
    BCRYPT_HASH_HANDLE h; check(BCryptCreateHash(algorithm,&h,NULL,0,NULL,0,0));
    update(h,p,size); finish(h,hex);
}
void host_digest(Regs *r,const char *terminal) {
    Devices *d=&ugh_devices; BCRYPT_HASH_HANDLE h; char ram[65],device[65],log[65];
    check(BCryptCreateHash(algorithm,&h,NULL,0,NULL,0,0));
    update(h,ugh_mem,0x80000); update(h,ugh_mem+0x8fefe,UGH_MEM_SIZE-0x8fefe); finish(h,ram);
    host_sha256(d,offsetof(Devices,count),device);
    update(rolling,d->log,d->count*sizeof(IoEvent));
    check(BCryptDuplicateHash(rolling,&h,NULL,0,0)); finish(h,log);
    printf("{\"ram\":\"%s\",\"device\":\"%s\",\"log\":\"%s\",\"scalars\":{",ram,device,log);
    static const char *names[]={"CurrentLevelIndex","LivesRemaining","ScoreLowWord","ScoreHighWord",
        "PlayerPixelX","PlayerYPixels","ActorPlatformOrScriptDone","ActorX32","ActorY32","ActorSpriteIds",
        "PlayerPlatformIndices","ScreenFadeLevel","PlayerCount","ScreenFadeStep","PlayerImpactMagnitude",
        "LevelTimer","WaterYPixels","PlayerCarriedKinds","RemainingPassengerJourneys"};
    for(unsigned i=0;i<sizeof names/sizeof names[0];i++) {
        char name[128]; snprintf(name,sizeof name,"DGROUP:%s",names[i]); HostSymbol s=host_symbol(name);
        unsigned v=(i==1 || i==18)?rd8(s.segment,s.offset):rd16(s.segment,s.offset);
        printf("\"%s\":%u,",names[i],v);
    }
    printf("\"return\":%u}",rd16(0x8000,r->sp));
    if(terminal) printf(",\"terminal\":\"%s\"",terminal);
    puts("}");
}
void host_digest_close(void) { BCryptDestroyHash(rolling); BCryptCloseAlgorithmProvider(algorithm,0); }
