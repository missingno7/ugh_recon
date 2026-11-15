#include "game_startup.h"
#include "high_scores.h"
#define TRY(call) do {GSStatus status=(call);if(status!=GS_OK)return status;}while(0)
static GSStatus load_scores(GameWorld *w,GameServices *s) {
    HighFileFlow flow={0,0};GSFileReply reply={0,0};uint16_t handle=0;
    for(;;)switch(high_file_next(&flow,reply.failed)) {
    case HIGH_FILE_OPEN:TRY(s->files.open_scores(s->files_context,0,&reply));handle=reply.value;break;
    case HIGH_FILE_READ:
        w->front.file_handle_bytes[0]=(uint8_t)handle;
        w->front.file_handle_bytes[1]=(uint8_t)(handle>>8);
        TRY(s->files.read(s->files_context,handle,w->front.score_rows,high_file_size(),&reply));break;
    case HIGH_FILE_CLOSE:TRY(s->files.close(s->files_context,handle,&reply));break;
    case HIGH_FILE_COMPLEMENT: {
        HighDescending cursor=high_complement_begin();
        do {w->front.score_rows[cursor.position]=high_complement_byte(w->front.score_rows[cursor.position]);high_descending_advance(&cursor);}while(cursor.remaining);
        break;}
    default:return GS_OK;
    }
}
static GSStatus platform_action(GameWorld *w,GameServices *s,LifecycleRequest request,LifecycleProcess *process) {
    switch(request.action) {
    case LIFE_QUERY_VIDEO: {
        GSVideoModeReply reply;TRY(s->lifecycle.video_query(s->lifecycle_context,&reply));
        lifecycle_video_reply(process,reply.mode);return GS_OK;}
    case LIFE_SAVE_VIDEO:w->lifecycle.saved_bios_video_mode=(uint8_t)request.argument;return GS_OK;
    case LIFE_CPU_PROBE: {
        uint8_t reply;return s->lifecycle.request(s->lifecycle_context,(GSLifecycleRequest){GS_LIFECYCLE_CPU_QUERY,0},&reply);}
    case LIFE_INSTALL_ERROR_HANDLER:
        return s->lifecycle.binding(s->lifecycle_context,GS_BIND_CRITICAL_ERROR_FAIL,GS_VECTOR_INSTALL,(GSBinding){2},&w->critical_saved);
    case LIFE_LOAD_SCORES:return load_scores(w,s);
    case LIFE_SEED_RANDOM: {
        GSSeedReply reply;TRY(s->seed.read(s->seed_context,&reply));
        random_seed(&w->random,(RandomDosTime){reply.hours,reply.minutes,reply.seconds,reply.hundredths});return GS_OK;}
    case LIFE_SET_VIDEO:return s->lifecycle.video_set(s->lifecycle_context,(uint8_t)request.argument);
    case LIFE_PICTURE_VIDEO:return game_picture_mode(w,s);
    case LIFE_INSTALL_KEYBOARD:return game_install_input(w,s);
    case LIFE_CALIBRATE_CONTROLS:return game_calibrate_input(w,s);
    case LIFE_INITIALIZE_AUDIO:return game_initialize_audio(w,s);
    case LIFE_CLEAR_VIDEO:return game_clear_video(w,s);
    default:return GS_UNSUPPORTED;
    }
}
GameBootResult game_boot(GameWorld *w,GameServices *s) {
    GameBootResult result={GAME_BOOT_SLICE_END,GS_OK,LIFE_BIND_WORLD};
    LifecycleProcess *program=&w->lifecycle.continuation[LIFE_PROGRAM];
    lifecycle_begin(program,LIFE_PROGRAM);
    for(;;) {
        LifecycleRequest request=lifecycle_next(program);result.action=request.action;
        /* This is an explicit suspended lifecycle continuation, before the
         * first menu entry; no synthetic completion or shutdown is published. */
        if(request.action==LIFE_MAIN_MENU)return result;
        if(!lifecycle_consume(program,request.action)){result.status=GS_INVALID;break;}
        if(request.action==LIFE_BIND_WORLD)continue;
        if(request.action==LIFE_INITIALIZE_PLATFORM) {
            LifecycleProcess *platform=&w->lifecycle.continuation[LIFE_PLATFORM_INIT];
            lifecycle_begin(platform,LIFE_PLATFORM_INIT);
            for(;;) {
                LifecycleRequest next=lifecycle_next(platform);
                if(next.action==LIFE_FINISHED)break;
                result.action=next.action;
                if(!lifecycle_consume(platform,next.action)){result.status=GS_INVALID;break;}
                result.status=platform_action(w,s,next,platform);if(result.status!=GS_OK)break;
            }
        } else if(request.action==LIFE_STARTUP_PICTURES)result.status=game_startup_pictures(w,s);
        else if(request.action==LIFE_GAMEPLAY_VIDEO)result.status=game_gameplay_mode(w,s);
        else result.status=GS_UNSUPPORTED;
        if(result.status!=GS_OK)break;
    }
    result.kind=result.status==GS_UNSUPPORTED?GAME_BOOT_UNSUPPORTED:result.status==GS_QUIT?GAME_BOOT_QUIT:GAME_BOOT_SERVICE_ERROR;
    return result;
}
