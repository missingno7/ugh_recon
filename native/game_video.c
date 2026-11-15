#include "game_startup.h"
#include "game_defaults.h"
#include "pictures.h"
#include "ice.h"
#include <string.h>
#define TRY(call) do{GSStatus status=(call);if(status!=GS_OK)return status;}while(0)
static GSStatus control(GameServices *s,GSVideoRoute route,uint8_t v){return s->video.control_write(s->video_context,route,v);}
static GSStatus retrace(GameWorld *w,GameServices *s,int active) {
    if(active)TRY(game_startup_timer(w,s));
    GSEvent event;TRY(s->time.deliver(s->time_context,active?GS_RETRACE_ACTIVE:GS_RETRACE_INACTIVE,&event));
    VideoRetrace wait={1000000,(uint8_t)active};
    for(;;){uint8_t level;TRY(s->video.retrace_level(s->video_context,&level));int again=video_retrace_delivery(&wait,level);if(!again)return GS_OK;if(again<0)return GS_OVERFLOW;}
}
static GSStatus next_retrace(GameWorld *w,GameServices *s){TRY(retrace(w,s,video_retrace_level(0,0)));return retrace(w,s,video_retrace_level(0,1));}
static GSStatus swap(GameWorld *w,GameServices *s) {
    video_swap(&w->pages);TRY(retrace(w,s,0));
    TRY(control(s,GS_CRTC_INDEX,12));TRY(control(s,GS_CRTC_DATA,(uint8_t)(w->pages.displayed>>8)));
    TRY(control(s,GS_CRTC_INDEX,13));TRY(control(s,GS_CRTC_DATA,(uint8_t)w->pages.displayed));
    w->frames++;TRY(s->video.present(s->video_context));return s->time.pace(s->time_context);
}
GSStatus game_clear_video(GameWorld *w,GameServices *s) {
    (void)w;TRY(control(s,GS_SEQ_INDEX,2));TRY(control(s,GS_SEQ_DATA,video_all_planes()));
    VideoClearCursor cursor=video_clear_begin(0);
    do{TRY(s->video.store_word(s->video_context,cursor.position,0));video_clear_advance(&cursor);}while(cursor.remaining);
    return GS_OK;
}
static GSStatus configure(GameWorld *w,GameServices *s,int gameplay) {
    VideoGeometry geometry=video_geometry(gameplay);
    w->pages.height=geometry.pages.height;w->pages.plane_copy_bytes=geometry.pages.plane_copy_bytes;
    TRY(s->video.dac(s->video_context,(GSDacWrite){GS_DAC_SELECT,0}));
    for(unsigned i=0;i<video_blackening_batches();i++) {
        TRY(next_retrace(w,s));
        for(unsigned j=0;j<3*video_blackening_entries();j++)TRY(s->video.dac(s->video_context,(GSDacWrite){GS_DAC_COMPONENT,0}));
    }
    for(unsigned i=0;i<7;i++) {
        VideoRegisterSetting setting=video_mode_setting(i,gameplay);
        GSVideoRoute index=setting.device?GS_CRTC_INDEX:GS_SEQ_INDEX,data=setting.device?GS_CRTC_DATA:GS_SEQ_DATA;
        TRY(control(s,index,setting.index));uint8_t previous=0;
        if(setting.read_previous)TRY(s->video.control_read(s->video_context,data,&previous));
        TRY(control(s,data,video_register_value(setting,previous)));
    }
    TRY(next_retrace(w,s));TRY(control(s,GS_ATTRIBUTE_WRITE,16));uint8_t previous;
    TRY(s->video.control_read(s->video_context,GS_ATTRIBUTE_READ,&previous));
    TRY(control(s,GS_ATTRIBUTE_WRITE,video_attribute_mode(previous)));TRY(control(s,GS_ATTRIBUTE_WRITE,32));
    w->pages=geometry.pages;TRY(game_clear_video(w,s));return swap(w,s);
}
GSStatus game_picture_mode(GameWorld *w,GameServices *s){return configure(w,s,0);}
GSStatus game_gameplay_mode(GameWorld *w,GameServices *s){return configure(w,s,1);}
static GSStatus fade(GameWorld *w,GameServices *s,int out) {
    uint16_t factor=out?256:0;
    do {
        VideoClearCursor cursor=video_scale_begin();
        do{w->palette.faded[cursor.position]=video_palette_scale(w->palette.base[cursor.position],factor).value;video_scale_advance(&cursor);}while(cursor.remaining);
        TRY(next_retrace(w,s));TRY(s->video.dac(s->video_context,(GSDacWrite){GS_DAC_SELECT,0}));
        VideoPaletteRange range=video_palette_range(0,0,216,0);
        do{for(unsigned j=0;j<3;j++)TRY(s->video.dac(s->video_context,(GSDacWrite){GS_DAC_COMPONENT,w->palette.faded[video_palette_advance(&range)]}));}while(--range.entries);
        factor=video_fade_step(factor,out);
    }while(video_fade_continue(factor,out));return GS_OK;
}
static GSStatus wait_picture(GameWorld *w,GameServices *s,uint16_t remaining,uint8_t *scan) {
    VideoTimeout flow={0};uint16_t reply=0;
    for(;;)switch(video_timeout_next(&flow,reply)) {
    case VIDEO_WAIT_INITIAL_SCAN:TRY(game_poll_input(w,s));break;
    case VIDEO_WAIT_SERVICE:TRY(s->input.pump(s->input_context,GS_INPUT_WAIT));break;
    case VIDEO_WAIT_SCAN:TRY(game_poll_input(w,s));reply=w->input.change;break;
    case VIDEO_WAIT_SAMPLE:TRY(game_sample_input(w,s));reply=w->input.joysticks[0].buttons|w->input.joysticks[1].buttons;break;
    case VIDEO_WAIT_RETRACE:TRY(next_retrace(w,s));break;
    case VIDEO_WAIT_COUNT:remaining=video_wait_decrement(remaining);reply=remaining;break;
    case VIDEO_WAIT_DONE_DEFAULT:*scan=57;return GS_OK;
    default:*scan=(uint8_t)w->input.current_scan_storage;return GS_OK;
    }
}
GSStatus game_startup_pictures(GameWorld *w,GameServices *s) {
    for(unsigned index=0;index<4;index++) {
        PictureStartupItem item=pictures_startup_item(index);PictureShowFlow show={0};uint8_t scan=0;
        for(;;)switch(pictures_show_next(&show)) {
        case PICTURE_EXPAND: {
            GSBytes packed;TRY(game_picture_resource(s,item.picture,&packed));IceResult result;
            IceStatus status=ice_decode(packed.data,packed.size,w->scratch,sizeof w->scratch,&result);
            if(status!=ICE_OK)return GS_INVALID;
            PicturePaletteCopy copy=pictures_palette_begin(0,0);
            do{w->palette.base[copy.destination]=w->scratch[copy.source];w->palette.base[copy.destination+1]=w->scratch[copy.source+1];pictures_palette_advance(&copy);}while(copy.remaining);
            break;}
        case PICTURE_UPLOAD: {
            TRY(control(s,GS_SEQ_INDEX,2));VideoChunkyCursor cursor=video_chunky_begin(0,w->pages.draw,w->pages.plane_copy_bytes,0);
            do{TRY(control(s,GS_SEQ_DATA,video_chunky_mask(&cursor)));TRY(s->video.store(s->video_context,cursor.destination,w->scratch[cursor.source]));video_chunky_advance(&cursor);}while(cursor.remaining);
            TRY(control(s,GS_SEQ_DATA,video_all_planes()));break;}
        case PICTURE_SWAP:TRY(swap(w,s));break;
        case PICTURE_FADE_IN:TRY(fade(w,s,0));break;
        case PICTURE_WAIT:TRY(wait_picture(w,s,item.retraces,&scan));break;
        case PICTURE_FADE_OUT:TRY(fade(w,s,1));break;
        default:goto picture_done;
        }
picture_done:;
        int16_t result=pictures_input_result(scan);
        switch(pictures_startup_route(index,result<0,result==0)) {
        case PICTURE_SHUTDOWN:return GS_QUIT;
        case PICTURE_RETURN:return GS_OK;
        default:break;
        }
    }
    return GS_OK;
}

/* Typed additive entry points share the accepted startup implementation. */
GSStatus game_video_retrace(GameWorld *w,GameServices *s,int active){return retrace(w,s,active);}
GSStatus game_video_next(GameWorld *w,GameServices *s){return next_retrace(w,s);}
GSStatus game_video_swap(GameWorld *w,GameServices *s){return swap(w,s);}
GSStatus game_video_fade(GameWorld *w,GameServices *s,int out){return fade(w,s,out);}
GSStatus game_video_wait(GameWorld *w,GameServices *s,uint16_t count,uint8_t *scan){return wait_picture(w,s,count,scan);}
GSStatus game_show_picture(GameWorld *w,GameServices *s,unsigned index,uint16_t retraces,int16_t *result) {
    GSBytes packed;TRY(game_picture_resource(s,index,&packed));IceResult decoded;
    if(ice_decode(packed.data,packed.size,w->scratch,sizeof w->scratch,&decoded)!=ICE_OK)return GS_INVALID;
    PicturePaletteCopy copy=pictures_palette_begin(0,0);
    do{w->palette.base[copy.destination]=w->scratch[copy.source];w->palette.base[copy.destination+1]=w->scratch[copy.source+1];pictures_palette_advance(&copy);}while(copy.remaining);
    TRY(control(s,GS_SEQ_INDEX,2));VideoChunkyCursor cursor=video_chunky_begin(0,w->pages.draw,w->pages.plane_copy_bytes,0);
    do{TRY(control(s,GS_SEQ_DATA,video_chunky_mask(&cursor)));TRY(s->video.store(s->video_context,cursor.destination,w->scratch[cursor.source]));video_chunky_advance(&cursor);}while(cursor.remaining);
    TRY(control(s,GS_SEQ_DATA,video_all_planes()));TRY(swap(w,s));TRY(fade(w,s,0));
    uint8_t scan;TRY(wait_picture(w,s,retraces,&scan));TRY(fade(w,s,1));*result=pictures_input_result(scan);return GS_OK;
}
