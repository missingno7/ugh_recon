#include "backend.h"
#include "../resources.h"
#include "../../native/game_boot.h"
#include "../../native/compose_menu.h"
#include "resource_manifest.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int main(int argc,char **argv) {
    const char *pack_path="ugh.res";int replay=0,adlib=1,boot_only=0;
    for(int i=1;i<argc;i++) {
        if(!strcmp(argv[i],"--pack")&&i+1<argc)pack_path=argv[++i];
        else if(!strcmp(argv[i],"--replay"))replay=1;
        else if(!strcmp(argv[i],"--boot-only"))boot_only=1;
        else if(!strcmp(argv[i],"--no-adlib"))adlib=0;
        else {fputs("usage: ugh-native [--pack FILE] [--replay] [--boot-only] [--no-adlib]\n",stderr);return 2;}
    }
    GSResourcePack pack;char error[256];
    if(gs_resources_open(&pack,pack_path,port_required_resources,PORT_REQUIRED_COUNT,error,sizeof error)!=GS_OK){fprintf(stderr,"%s\n",error);return 2;}
    GSTestBackend *backend=calloc(1,sizeof *backend);GameWorld *world=calloc(1,sizeof *world);
    if(!backend||!world){free(backend);free(world);gs_resources_close(&pack);return 2;}
    gs_test_init(backend);gs_test_startup(backend,adlib);
    backend->live_seed=(uint8_t)!replay;
    backend->resources=gs_resources_operations();backend->resource_context=&pack;
    GameServices services=gs_test_services(backend);GSStatus status=game_world_construct(world,&services);
    GameBootResult result={GAME_BOOT_SERVICE_ERROR,status,LIFE_BIND_WORLD};
    if(status==GS_OK){
        if(boot_only)result=game_boot(world,&services);
        else{GameMenu menu;GameMenuResult run=game_main(world,&services,&menu);
            result=(GameBootResult){run.kind==GAME_MENU_SESSION_ENTRY?GAME_BOOT_SLICE_END:run.kind==GAME_MENU_EXIT?GAME_BOOT_QUIT:GAME_BOOT_SERVICE_ERROR,run.status,LIFE_MAIN_MENU};}
    }
    printf("{\"result\":\"%s\",\"status\":%u,\"action\":%u,\"frames\":%u,\"seed_word0\":%u}\n",result.kind==GAME_BOOT_SLICE_END?(boot_only?"slice_end":"session_entry"):result.kind==GAME_BOOT_QUIT?"exit":"error",result.status,result.action,world->frames,world->random.word[0]);
    int code=result.kind==GAME_BOOT_QUIT?backend->exit_code:result.kind==GAME_BOOT_SLICE_END?0:1;
    free(world);free(backend);gs_resources_close(&pack);return code;
}
