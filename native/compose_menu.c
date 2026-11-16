#include "compose_menu.h"
#include "compose_front_end.h"
#include "compose_demo.h"
#include "compose_audio.h"
#include "compose_session.h"
#include "game_startup.h"
#include "game_defaults.h"
#include <string.h>
#define TRY(call) do{GSStatus status=(call);if(status!=GS_OK)return status;}while(0)
static GSStatus wait_count(GameWorld *w,GameServices *s,uint16_t n){do{TRY(game_video_next(w,s));}while(--n);return GS_OK;}
static GSStatus restore(GameWorld *w,GameServices *s){return game_front_restore(w,s,(FrontRectangle){0,0,320,w->pages.height});}
static void duplicate(GameWorld *w){
    VideoCopyCursor c=video_duplicate_begin(0,0,0);
    do{VideoDuplicateTransfer t=video_duplicate_transfer(&c);for(unsigned j=0;j<2;j++){
        w->palette.base[t.destinations[j]]=w->front_data.source_palette[t.source];
        w->palette.base[t.destinations[j]+1]=w->front_data.source_palette[t.source+1];
    }video_duplicate_advance(&c);}while(c.remaining);
}
static GSStatus controls_draw(GameWorld *w,GameServices *s){
    TRY(restore(w,s));
    for(unsigned i=0;i<2;i++){
        MenusLabel plan=menus_label(2+i,w->run.configuration.control_mode[i]);GSBytes label;
        TRY(game_front_label(s,2,plan.index,&label));
        for(size_t j=0;j<label.size;j++){if(!label.data[j])break;if(j>=10)return GS_UNSUPPORTED;w->front.control_text[i][j]=label.data[j];}
    }
    uint8_t text[128];memcpy(text,w->front_data.controls,128);
    memcpy(text+15,w->front.control_text[0],10);memcpy(text+41,w->front.control_text[1],10);
    GameFrontText cursor={{text,sizeof text},0,0,80,0};TRY(game_front_text_block(w,s,&cursor));return game_video_swap(w,s);
}
GSStatus game_menu_controls(GameWorld *w,GameServices *s){
    w->run.water_y=menus_water(3);TRY(wait_count(w,s,40));TRY(controls_draw(w,s));TRY(game_video_fade(w,s,0));
    uint16_t remaining=2100;
    for(unsigned budget=0;budget<100000;budget++){
        TRY(game_video_next(w,s));if(!--remaining)return game_video_fade(w,s,1);
        TRY(game_poll_input(w,s));if(!w->input.change)continue;
        MenusControlKey key=menus_control_key((uint8_t)w->input.current_scan_storage);
        if(key==MENUS_CONTROL_QUIT)return game_video_fade(w,s,1);
        if(key!=MENUS_CONTROL_RESTART){
            unsigned player=key==MENUS_CONTROL_PLAYER0?0:1;uint16_t mode=w->run.configuration.control_mode[player];
            for(;;){MenusControlCandidate c=menus_control_next(mode);mode=c.mode;
                if(c.keyboard)break;
                if(c.index>2)return GS_UNSUPPORTED;
                if(menus_control_present(w->input.joysticks[c.index/2].present))break;
            }
            w->run.configuration.control_mode[player]=mode;TRY(controls_draw(w,s));
        }
        remaining=2100;
    }return GS_OVERFLOW;
}
void game_menu_begin(GameMenu *menu){memset(menu,0,sizeof *menu);}
void game_menu_session_return(GameMenu *menu,int completed){menu->reply.completed=(uint8_t)!!completed;}
static GSStatus game_over(GameWorld *w,GameServices *s){
    w->run.water_y=menus_water(3);
    GameFrontText text={{w->front_data.game_over,sizeof w->front_data.game_over},0,0,72,0};
    TRY(game_front_text_block(w,s,&text));TRY(game_video_swap(w,s));
    TRY(game_audio_music_stop(w,s,17).status);
    TRY(game_audio_effect(w,s,game_audio_game_over_resource(),225,1).status);
    TRY(game_video_fade(w,s,0));uint8_t scan;TRY(game_video_wait(w,s,700,&scan));
    return game_video_fade(w,s,1);
}
GameMenuResult game_menu_run(GameWorld *w,GameServices *s,GameMenu *menu){
    for(;;){MenusMainAction action=menus_main_next(&menu->process,menu->reply);GSStatus status=GS_OK;
        GameFrontResult front={GS_OK,0};GameDemoResult demo={GS_OK,0};int selection=0;
        switch(action){
        case MENUS_MAIN_STOP_MUSIC:status=game_audio_music_stop(w,s,17).status;break;
        case MENUS_MAIN_START_MUSIC:status=game_audio_music_start(w,s,game_audio_menu_resource(),0,165).status;break;
        case MENUS_MAIN_REVEAL:case MENUS_MAIN_ATTRACT:
            demo=game_demo_play(w,s,action==MENUS_MAIN_REVEAL?DEMO_PRESENT_REVEAL:DEMO_PRESENT_ATTRACT);status=demo.status;selection=demo.selection;goto selected;
        case MENUS_MAIN_CREDITS:front=game_front_credits(w,s);goto front_selected;
        case MENUS_MAIN_SCORES:front=game_front_scores_show(w,s);
front_selected:status=front.status;selection=front.selection;
selected:menu->reply.negative=selection<0;menu->reply.zero=selection==0;break;
        case MENUS_MAIN_PREPARE_PALETTE:duplicate(w);break;
        case MENUS_MAIN_PREPARE_SCREEN:
            w->run.water_y=menus_water(2);status=wait_count(w,s,40);
            if(status==GS_OK)status=game_clear_video(w,s);
            if(status==GS_OK)status=game_front_header(w,s);
            if(status==GS_OK)status=game_front_save_background(w,s);
            if(status==GS_OK)status=game_video_swap(w,s);
            if(status==GS_OK)status=restore(w,s);
            if(status==GS_OK)status=game_front_menu_draw(w,s);
            if(status==GS_OK)status=game_video_fade(w,s,0);break;
        case MENUS_MAIN_REDRAW:status=game_front_menu_draw(w,s);break;
        case MENUS_MAIN_RESET_TIMEOUT:menu->reply.remaining=2100;break;
        case MENUS_MAIN_WAIT:status=game_video_next(w,s);if(status==GS_OK)menu->reply.remaining--;break;
        case MENUS_MAIN_POLL:
            /* The loop's external opportunity precedes the keyboard poll's
             * own scan opportunity; a failure consumes only this prefix. */
            status=s->input.pump(s->input_context,GS_INPUT_WAIT);
            if(status==GS_OK)status=game_poll_input(w,s);
            menu->reply.changed=w->input.change;menu->reply.scan=(uint8_t)w->input.current_scan_storage;break;
        case MENUS_MAIN_RESTART_ATTRACT:case MENUS_MAIN_CONTROLS_FADE:case MENUS_MAIN_PLAY_FADE:status=game_video_fade(w,s,1);break;
        case MENUS_MAIN_CONTROLS:status=game_menu_controls(w,s);break;
        case MENUS_MAIN_PLAYERS:{FrontConfiguration c={0};c.players=w->run.configuration.players;menus_toggle_players(&c);w->run.configuration.players=c.players;w->run.configuration.player_bytes=c.player_bytes;break;}
        case MENUS_MAIN_DIFFICULTY:w->run.configuration.difficulty=menus_difficulty_next(w->run.configuration.difficulty);break;
        case MENUS_MAIN_PASSWORD:status=game_front_password(w,s);break;
        case MENUS_MAIN_SESSION:return (GameMenuResult){GAME_MENU_SESSION_ENTRY,GS_OK,action};
        case MENUS_MAIN_CLEAR_SESSION:status=game_clear_video(w,s);break;
        case MENUS_MAIN_CHECK_SESSION:break;
        case MENUS_MAIN_GAME_OVER:status=game_over(w,s);break;
        case MENUS_MAIN_COMPLETION:status=game_demo_play(w,s,DEMO_PRESENT_COMPLETION).status;break;
        case MENUS_MAIN_INSERT_SCORES:status=game_front_scores_insert(w,s).status;break;
        case MENUS_MAIN_EXIT_FADE:status=game_video_fade(w,s,1);if(status!=GS_OK)break;return (GameMenuResult){GAME_MENU_EXIT,GS_OK,action};
        case MENUS_MAIN_DONE:return (GameMenuResult){GAME_MENU_EXIT,GS_OK,action};
        case MENUS_MAIN_BOUND:status=GS_OVERFLOW;break;
        default:status=GS_UNSUPPORTED;break;
        }
        if(status!=GS_OK)return (GameMenuResult){GAME_MENU_FAILED,status,action};
    }
}
GSStatus game_menu_terminal(GameWorld *w,GameServices *s){
    uint16_t live_reply=0;terminal_tail_begin(&w->lifecycle.terminal);
    for(;;)switch(terminal_tail_next(&w->lifecycle.terminal)){
    case TERMINAL_STOP_SOUND:TRY(game_audio_terminal(w,s));break;
    case TERMINAL_RESTORE_VIDEO:TRY(s->lifecycle.video_set(s->lifecycle_context,terminal_tail_video_mode(w->lifecycle.saved_bios_video_mode)));break;
    case TERMINAL_RESTORE_INPUT:{GSBinding reply;TRY(s->input.vector(s->input_context,GS_VECTOR_RESTORE,w->keyboard_saved,&reply));TRY(s->input.flush(s->input_context,&live_reply));break;}
    case TERMINAL_EXIT:return s->lifecycle.terminate(s->lifecycle_context,(uint8_t)live_reply);
    default:return GS_INVALID;
    }
}
GameMenuResult game_main(GameWorld *w,GameServices *s,GameMenu *menu){
    GameBootResult boot=game_boot(w,s);
    if(boot.kind!=GAME_BOOT_SLICE_END){
        if(boot.kind==GAME_BOOT_QUIT){GSStatus status=game_menu_terminal(w,s);return (GameMenuResult){status==GS_OK?GAME_MENU_EXIT:GAME_MENU_FAILED,status,MENUS_MAIN_DONE};}
        return (GameMenuResult){GAME_MENU_FAILED,boot.status,MENUS_MAIN_DONE};
    }
    if(!lifecycle_consume(&w->lifecycle.continuation[LIFE_PROGRAM],LIFE_MAIN_MENU))return (GameMenuResult){GAME_MENU_FAILED,GS_INVALID,MENUS_MAIN_DONE};
    game_menu_begin(menu);GameMenuResult result=game_menu_run(w,s,menu);
    while(result.kind==GAME_MENU_SESSION_ENTRY){
        GameSessionResult session=game_session_run(w,s,GAME_SESSION_PASSWORD);
        if(session.kind!=GAME_SESSION_RETURNED){result.kind=GAME_MENU_FAILED;result.status=session.status;break;}
        game_menu_session_return(menu,w->run.level>=session_data_count(w->run.configuration.player_bytes));
        result=game_menu_run(w,s,menu);
    }
    if(result.kind==GAME_MENU_EXIT){
        LifecycleProcess *program=&w->lifecycle.continuation[LIFE_PROGRAM];LifecycleRequest r=lifecycle_next(program);
        if(r.action!=LIFE_SHUTDOWN_PLATFORM||!lifecycle_consume(program,r.action))result.status=GS_INVALID;
        else result.status=game_menu_terminal(w,s);
        if(result.status!=GS_OK)result.kind=GAME_MENU_FAILED;
    }return result;
}
