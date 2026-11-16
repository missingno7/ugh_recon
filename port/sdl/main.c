#ifdef UGH_PRODUCTION_MAIN
#include "backend.h"
#include "../resources.h"
#include "../../native/game_boot.h"
#include "../../native/compose_menu.h"
#include "resource_manifest.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int main(int argc,char **argv){
    const char *pack_path="ugh.res",*scores="UGH!.HI";int replay=0,headless=0,adlib=1,unpaced=0,boot_only=0;
    for(int n=1;n<argc;n++){
        if(!strcmp(argv[n],"--pack")&&n+1<argc)pack_path=argv[++n];
        else if(!strcmp(argv[n],"--scores")&&n+1<argc)scores=argv[++n];
        else if(!strcmp(argv[n],"--replay"))replay=1;
        else if(!strcmp(argv[n],"--boot-only"))boot_only=1;
        else if(!strcmp(argv[n],"--headless"))headless=1;
        else if(!strcmp(argv[n],"--no-adlib"))adlib=0;
        else if(!strcmp(argv[n],"--unpaced"))unpaced=1;
        else{fputs("usage: ugh-native [--pack FILE] [--scores FILE] [--replay] [--headless] [--no-adlib] [--unpaced]\n",stderr);return 2;}
    }
    GSResourcePack pack;char error[256];
    if(gs_resources_open(&pack,pack_path,port_required_resources,PORT_REQUIRED_COUNT,error,sizeof error)!=GS_OK){fprintf(stderr,"%s\n",error);return 2;}
    if(!SDL_Init(headless?0:SDL_INIT_VIDEO|SDL_INIT_AUDIO|SDL_INIT_GAMEPAD)){fprintf(stderr,"SDL: %s\n",SDL_GetError());gs_resources_close(&pack);return 2;}
    GSSdlVideo *video=calloc(1,sizeof *video);GSSdlAudio *audio=calloc(1,sizeof *audio);
    GSSdlInput *input=calloc(1,sizeof *input);GameWorld *world=calloc(1,sizeof *world);
    int code=2;if(!video||!audio||!input||!world)goto done;
    gs_video_init(video);gs_input_init(input);
    if((!headless&&gs_video_window(video,3)!=GS_OK)||gs_audio_init(audio,!headless)!=GS_OK)goto done;
    GSSdlTime time;gs_time_init(&time,!unpaced&&!headless);
    GSSdlFiles files;if(gs_files_init(&files,scores)!=GS_OK)goto done;
    GSSdlSeed seed={replay,{16,32,48,64}};GSSdlStartup platform;GameServices services;
    gs_sdl_startup(&platform,&services,video,input,&time,audio,&files,&seed,adlib);
    services.resources_context=&pack;services.resources=gs_resources_operations();
    GSStatus status=game_world_construct(world,&services);
    GameBootResult result={GAME_BOOT_SERVICE_ERROR,status,LIFE_BIND_WORLD};if(status==GS_OK){
        if(boot_only)result=game_boot(world,&services);
        else{GameMenu menu;GameMenuResult run=game_main(world,&services,&menu);
            result=(GameBootResult){run.kind==GAME_MENU_SESSION_ENTRY?GAME_BOOT_SLICE_END:run.kind==GAME_MENU_EXIT?GAME_BOOT_QUIT:GAME_BOOT_SERVICE_ERROR,run.status,LIFE_MAIN_MENU};}
    }
    /* Closing the window ends the run through GS_QUIT; that is a normal close. */
    int closed=result.kind==GAME_BOOT_SERVICE_ERROR&&result.status==GS_QUIT;
    printf("{\"result\":\"%s\",\"status\":%u,\"action\":%u,\"frames\":%u,\"presentations\":%llu}\n",result.kind==GAME_BOOT_SLICE_END?(boot_only?"slice_end":"session_entry"):result.kind==GAME_BOOT_QUIT?"exit":closed?"closed":"error",result.status,result.action,world->frames,(unsigned long long)platform.presentations);
    code=result.kind==GAME_BOOT_SLICE_END||closed?0:result.kind==GAME_BOOT_QUIT?platform.exit_code:1;
done:
    if(input)gs_input_close(input);
    if(audio)gs_audio_close(audio);
    if(video)gs_video_close(video);
    free(world);free(input);free(audio);free(video);gs_resources_close(&pack);SDL_Quit();return code;
}
#endif
