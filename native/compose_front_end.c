#include "compose_front_end.h"
#include "compose_audio.h"
#include "game_startup.h"
#include "game_defaults.h"
#include "high_scores.h"
#include "menus.h"
#include "decimal.h"
#include "render_primitives.h"
#include <string.h>
#define TRY(call) do {GSStatus status=(call);if(status!=GS_OK)return status;} while(0)
static GSStatus control(GameServices *s,GSVideoRoute route,uint8_t v){return s->video.control_write(s->video_context,route,v);}
static GSStatus wait_count(GameWorld *w,GameServices *s,uint16_t count){do{TRY(game_video_next(w,s));}while(--count);return GS_OK;}
static GSStatus copy_mode(GameServices *s,int enabled) {
    uint8_t mode;if(enabled)TRY(control(s,GS_GC_INDEX,5));
    TRY(s->video.control_read(s->video_context,GS_GC_DATA,&mode));
    return control(s,GS_GC_DATA,(uint8_t)((mode&252u)+(enabled?1u:0u)));
}
GSStatus game_front_restore(GameWorld *w,GameServices *s,FrontRectangle rectangle) {
    TRY(copy_mode(s,1));RenderCopyRows rows=render_rectangle(rectangle.x,rectangle.y,rectangle.width,rectangle.height,w->pages.background,w->pages.draw);
    do{for(unsigned i=0;i<rows.width;i++){uint8_t value;TRY(s->video.copy(s->video_context,(uint16_t)(rows.source+i),(uint16_t)(rows.destination+i),&value));}render_next_row(&rows);}while(rows.remaining);
    return copy_mode(s,0);
}
static GSStatus restore_all(GameWorld *w,GameServices *s){return game_front_restore(w,s,(FrontRectangle){0,0,320,w->pages.height});}
GSStatus game_front_save_background(GameWorld *w,GameServices *s) {
    TRY(copy_mode(s,1));RenderCopyRequest copy=render_save(w->pages.draw,w->pages.background,w->pages.plane_copy_bytes,0);
    for(unsigned i=0;i<copy.count;i++){uint8_t value;TRY(s->video.copy(s->video_context,(uint16_t)(copy.source+i),(uint16_t)(copy.destination+i),&value));}
    return copy_mode(s,0);
}
GSStatus game_front_sprite_draw(GameWorld *w,GameServices *s,uint16_t sprite,uint16_t x,uint16_t y) {
    RenderSpritePlacement p=render_sprite_place(sprite,x,y,w->run.water_y,w->pages.height,w->pages.draw,w->pages.fixed);
    w->front_data.renderer_water=p.water;TRY(control(s,GS_SEQ_INDEX,2));
    w->front_data.renderer_plane=(uint16_t)(2u+256u*p.plane);
    GSBytes bank;uint16_t source,dimensions;TRY(game_front_sprite(s,sprite,&bank,&source,&dimensions));
    RenderSpriteCursor c;render_sprite_begin(&c,p,source,dimensions,0);
    do{TRY(control(s,GS_SEQ_DATA,c.plane));
        do{if(c.source>=bank.size)return GS_UNSUPPORTED;
            RenderPixelRequest pixel=render_sprite_pixel(&c,bank.data[c.source]);
            if(pixel.write)TRY(s->video.store(s->video_context,pixel.destination,pixel.value));
        }while(c.rows);
        render_sprite_column(&c);
    }while(c.columns);
    return control(s,GS_SEQ_DATA,15);
}
GSStatus game_front_header(GameWorld *w,GameServices *s) {
    uint16_t previous=0;for(unsigned i=0;i<3;i++){MenusHeaderItem item=menus_header_item(i,previous);TRY(game_front_sprite_draw(w,s,item.sprite,item.x,0));previous=item.sprite;}return GS_OK;
}
GSStatus game_front_text_line(GameWorld *w,GameServices *s,GameFrontText *text) {
    if(text->position>=text->bytes.size)return GS_UNSUPPORTED;
    text->x=0;uint8_t ch=text->bytes.data[text->position++];
    if(menus_text_centered(ch)) {
        size_t start=text->position,count=0;
        for(;;){if(text->position>=text->bytes.size)return GS_UNSUPPORTED;ch=text->bytes.data[text->position++];if(ch==0||ch==13||ch==253)break;count++;}
        text->x=menus_text_center_x((uint16_t)count);text->position=start;ch=text->bytes.data[text->position++];
    }
    for(;;){MenusTextStep item=menus_text_step(ch);
        if(item.kind!=MENUS_TEXT_GLYPH){text->y=menus_text_next_y(text->y,ch);text->delimiter=ch;return GS_OK;}
        TRY(game_front_sprite_draw(w,s,item.glyph,text->x,text->y));text->x=menus_text_next_x(text->x);
        if(text->position>=text->bytes.size)return GS_UNSUPPORTED;ch=text->bytes.data[text->position++];
    }
}
GSStatus game_front_text_block(GameWorld *w,GameServices *s,GameFrontText *text) {
    do{TRY(game_front_text_line(w,s,text));}while(text->delimiter);return GS_OK;
}
static GSStatus draw(GameWorld *w,GameServices *s,const uint8_t *bytes,size_t size,uint16_t y) {
    GameFrontText text={{bytes,size},0,0,y,0};return game_front_text_block(w,s,&text);
}
GSStatus game_front_recipient(GameWorld *w,GameServices *s,GameFrontRecipient recipient) {
    if(recipient==GAME_FRONT_SCAN_HANDLER)return game_install_input(w,s);
    if(recipient!=GAME_FRONT_BIOS_EDITOR)return GS_INVALID;
    GSBinding reply;TRY(s->input.vector(s->input_context,GS_VECTOR_RESTORE,w->keyboard_saved,&reply));
    uint16_t flushed;return s->input.flush(s->input_context,&flushed);
}
GSStatus game_front_scores_file(GameWorld *w,GameServices *s,int saving) {
    HighFileFlow flow={(uint8_t)!!saving,0};GSFileReply reply={0,0};uint16_t handle=0;
    for(;;)switch(high_file_next(&flow,reply.failed)) {
    case HIGH_FILE_OPEN:TRY(s->files.open_scores(s->files_context,0,&reply));handle=reply.value;break;
    case HIGH_FILE_CREATE:TRY(s->files.open_scores(s->files_context,1,&reply));handle=reply.value;break;
    case HIGH_FILE_READ:case HIGH_FILE_WRITE:
        w->front.file_handle_bytes[0]=(uint8_t)handle;w->front.file_handle_bytes[1]=(uint8_t)(handle>>8);
        if(saving)TRY(s->files.write(s->files_context,handle,w->front.score_rows,high_file_size(),&reply));
        else TRY(s->files.read(s->files_context,handle,w->front.score_rows,high_file_size(),&reply));break;
    case HIGH_FILE_CLOSE:TRY(s->files.close(s->files_context,handle,&reply));break;
    case HIGH_FILE_COMPLEMENT: {
        HighDescending c=high_complement_begin();do{w->front.score_rows[c.position]=high_complement_byte(w->front.score_rows[c.position]);high_descending_advance(&c);}while(c.remaining);break;}
    default:return GS_OK;
    }
}
GSStatus game_front_digits(GameWorld *w,uint32_t value,unsigned count) {
    uint8_t *d=w->front_data.divisors;DecimalDivisors divisors={d,d+1,d+2,d+4};DecimalOutput output={w->front_data.digits,7,0};
    DecimalResult result;if(count==2)result=decimal_two((uint8_t)value,&output,divisors);
    else if(count==4)result=decimal_four((uint16_t)value,&output,divisors);
    else if(count==6)result=decimal_six(value,&output,divisors);else return GS_INVALID;
    return result.status==DECIMAL_OK?GS_OK:GS_UNSUPPORTED;
}
static GSStatus copy_label(GameServices *s,unsigned kind,unsigned index,uint8_t *destination,size_t capacity) {
    GSBytes label;TRY(game_front_label(s,kind,index,&label));
    for(size_t i=0;i<label.size;i++){if(!label.data[i])return GS_OK;if(i>=capacity)return GS_UNSUPPORTED;destination[i]=label.data[i];}return GS_UNSUPPORTED;
}
GSStatus game_front_menu_draw(GameWorld *w,GameServices *s) {
    TRY(restore_all(w,s));
    TRY(copy_label(s,0,w->run.configuration.difficulty,w->front.difficulty_text,6));
    TRY(copy_label(s,1,(uint16_t)(w->run.configuration.players-1u),w->front.players_text,10));
    uint8_t text[128];memcpy(text,w->front_data.menu,128);memcpy(text+41,w->front.difficulty_text,6);memcpy(text+53,w->front.players_text,10);memcpy(text+106,w->front.password,21);
    TRY(draw(w,s,text,sizeof text,72));return game_video_swap(w,s);
}
static GSStatus entry_draw(GameWorld *w,GameServices *s,int name) {
    TRY(game_front_restore(w,s,front_entry_rectangle(name)));
    TRY(draw(w,s,name?w->front.name_entry:w->front.password,name?13:21,name?160:176));
    return game_video_swap(w,s);
}
static GSStatus edit(GameWorld *w,GameServices *s,int name) {
    NativeFrontEditor editor={0,0};uint16_t capacity=name?12:20;uint8_t *bytes=name?w->front.name_entry:w->front.password;
    for(unsigned budget=0;budget<100000;budget++) {
        TRY(game_video_retrace(w,s,1));FrontBlink blink=front_blink(editor.position,capacity,(uint8_t)editor.blink_word);
        editor.blink_word=(uint16_t)((editor.blink_word&65280u)|blink.counter);if(blink.write)bytes[editor.position]=blink.character;
        TRY(entry_draw(w,s,name));uint16_t word=0;GSStatus status=s->input.queue(s->input_context,GS_QUEUE_PEEK,&word);
        if(status==GS_EMPTY)continue;if(status!=GS_OK)return status;
        TRY(s->input.queue(s->input_context,GS_QUEUE_TAKE,&word));
        FrontEditCommand command=front_edit_command(editor.position,capacity,(uint8_t)word,name);
        if(command.kind==FRONT_EDIT_ERASE){for(unsigned i=0;i<command.erase_count;i++)bytes[command.erase[i]]=32;editor.position=command.position;editor.blink_word&=65280u;}
        else if(command.kind==FRONT_EDIT_STORE){bytes[editor.position]=command.character;editor.position=command.position;editor.blink_word&=65280u;}
        else if(command.kind==FRONT_EDIT_FINISH){
            if(command.clear_current){bytes[editor.position]=32;
                if(name)TRY(entry_draw(w,s,1));
                if(command.empty){if(name){for(unsigned i=0;i<5;i++){uint16_t v=high_default_name_word(i);bytes[2*i]=(uint8_t)v;bytes[2*i+1]=(uint8_t)(v>>8);}}else memcpy(bytes,"NONE",4);}
            }return GS_OK;
        }
    }return GS_OVERFLOW;
}
GSStatus game_front_password(GameWorld *w,GameServices *s) {
    TRY(game_front_recipient(w,s,GAME_FRONT_BIOS_EDITOR));TRY(restore_all(w,s));TRY(game_front_menu_draw(w,s));
    for(unsigned i=20;i;i--)w->front.password[i-1]=32;
    TRY(edit(w,s,0));return game_front_recipient(w,s,GAME_FRONT_SCAN_HANDLER);
}
GSStatus game_front_name(GameWorld *w,GameServices *s){return edit(w,s,1);}
static GameFrontResult outcome(GSStatus status,int16_t value){GameFrontResult result={status,value};return result;}
GameFrontResult game_front_picture(GameWorld *w,GameServices *s,PictureKind picture,uint16_t retraces) {
    int16_t selection=0;GSStatus status=game_show_picture(w,s,(unsigned)picture,retraces,&selection);return outcome(status,selection);
}
GameFrontResult game_front_scores_show(GameWorld *w,GameServices *s) {
    GSStatus status;uint8_t scan;w->run.water_y=200;
#define STEP(call) do{status=(call);if(status!=GS_OK)return outcome(status,0);}while(0)
    STEP(wait_count(w,s,40));STEP(game_clear_video(w,s));STEP(game_front_header(w,s));
    uint8_t text[118];memcpy(text,w->front_data.score_title,11);memcpy(text+11,w->front.score_rows,107);
    STEP(draw(w,s,text,sizeof text,80));STEP(game_video_swap(w,s));STEP(game_video_fade(w,s,0));
    STEP(game_video_wait(w,s,0x578,&scan));STEP(game_video_fade(w,s,1));return outcome(GS_OK,high_show_result(scan));
}
static GSStatus score_music(GameWorld *w,GameServices *s){
    TRY(game_audio_music_stop(w,s,17).status);
    return game_audio_music_start(w,s,game_audio_score_resource(),0,165).status;
}
GameFrontResult game_front_scores_insert(GameWorld *w,GameServices *s) {
    GSStatus status;STEP(game_front_digits(w,w->run.score,6));uint8_t significant=0;
    for(unsigned i=0;i<6;i++){HighFormatDigit digit=high_format_digit(w->front_data.digits[i],significant);w->front_data.digits[i]=digit.character;significant=digit.significant;}
    HighInsertion insertion={0,0,0,0};
    while(!insertion.done){size_t start=high_row_offset((uint8_t)insertion.row,w->front.row_stride,1);if(start+6>107)return outcome(GS_UNSUPPORTED,0);
        HighQualification test={0,0,0};do{high_compare_step(&test,w->front_data.digits[test.position],w->front.score_rows[start+test.position]);}while(!test.done);
        high_insertion_compare(&insertion,test.qualifies);
    }
    if(!insertion.accepted){w->run.score=0;return outcome(GS_OK,0);}
    do{HighCopy c=high_copy_begin(high_row_offset((uint8_t)insertion.shift,w->front.row_stride,0));
        do{if(c.source>=107||c.destination>=107)return outcome(GS_UNSUPPORTED,0);w->front.score_rows[c.destination]=w->front.score_rows[c.source];high_copy_advance(&c);}while(c.remaining);
    }while(high_shift_advance(&insertion));
    size_t start=high_row_offset((uint8_t)insertion.row,w->front.row_stride,1);
    HighDescending digits=high_digits_begin();do{w->front.score_rows[start+digits.position]=w->front_data.digits[digits.position];high_descending_advance(&digits);}while(digits.remaining);
    STEP(score_music(w,s));STEP(game_front_recipient(w,s,GAME_FRONT_BIOS_EDITOR));
    HighDescending blank=high_name_begin();do{w->front.name_entry[blank.position]=32;high_descending_advance(&blank);}while(blank.remaining);
    w->run.water_y=159;STEP(wait_count(w,s,40));STEP(game_clear_video(w,s));STEP(game_front_header(w,s));
    uint8_t prompt[87];memcpy(prompt,w->front_data.score_prompt,74);memcpy(prompt+74,w->front.name_entry,13);
    STEP(draw(w,s,prompt,sizeof prompt,80));STEP(game_front_save_background(w,s));STEP(game_video_swap(w,s));STEP(restore_all(w,s));STEP(game_video_fade(w,s,0));
    STEP(game_front_name(w,s));start=high_row_offset((uint8_t)insertion.row,w->front.row_stride,0);
    HighDescending name=high_name_begin();do{w->front.score_rows[start+name.position]=w->front.name_entry[name.position];high_descending_advance(&name);}while(name.remaining);
    STEP(game_front_recipient(w,s,GAME_FRONT_SCAN_HANDLER));STEP(game_video_fade(w,s,1));STEP(game_front_scores_file(w,s,1));
    GameFrontResult result=game_front_scores_show(w,s);if(result.status!=GS_OK)return result;w->run.score=0;return outcome(GS_OK,0);
}
static void duplicate_palette(GameWorld *w) {
    VideoCopyCursor c=video_duplicate_begin(0,0,0);do{VideoDuplicateTransfer t=video_duplicate_transfer(&c);for(unsigned j=0;j<2;j++){w->palette.base[t.destinations[j]]=w->front_data.source_palette[t.source];w->palette.base[t.destinations[j]+1]=w->front_data.source_palette[t.source+1];}video_duplicate_advance(&c);}while(c.remaining);
}
static GSStatus front_wait(GameWorld *w,GameServices *s,uint16_t remaining,uint8_t *scan,int *timeout) {
    VideoTimeout flow={0};uint16_t reply=0;
    for(;;)switch(video_timeout_next(&flow,reply)) {
    case VIDEO_WAIT_INITIAL_SCAN:TRY(game_poll_input(w,s));break;
    case VIDEO_WAIT_SERVICE:TRY(s->input.pump(s->input_context,GS_INPUT_WAIT));break;
    case VIDEO_WAIT_SCAN:TRY(game_poll_input(w,s));reply=w->input.change;break;
    case VIDEO_WAIT_SAMPLE:TRY(game_sample_input(w,s));reply=w->input.joysticks[0].buttons|w->input.joysticks[1].buttons;break;
    case VIDEO_WAIT_RETRACE:TRY(game_video_next(w,s));break;
    case VIDEO_WAIT_COUNT:remaining=video_wait_decrement(remaining);reply=remaining;break;
    case VIDEO_WAIT_DONE_DEFAULT:*scan=57;*timeout=!remaining;return GS_OK;
    default:*scan=(uint8_t)w->input.current_scan_storage;*timeout=!remaining;return GS_OK;
    }
}
static GSStatus wait_scan(GameWorld *w,GameServices *s) {
    InputWaitWork work={1000000,0};int changed=0;
    for(;;)switch(input_wait_next(&work,changed)) {
    case INPUT_WAIT_SCAN:TRY(game_poll_input(w,s));if(work.stage!=1)changed=!!w->input.change;break;
    case INPUT_WAIT_RETRACE:TRY(game_video_next(w,s));break;
    case INPUT_WAIT_SAMPLE:TRY(game_sample_input_trigger(w,s,8));changed=!!(w->input.joysticks[0].buttons|w->input.joysticks[1].buttons);break;
    case INPUT_WAIT_SERVICE:TRY(s->input.pump(s->input_context,GS_INPUT_WAIT));break;
    case INPUT_WAIT_DONE:return GS_OK;
    default:return GS_OVERFLOW;
    }
}
GameFrontResult game_front_credits(GameWorld *w,GameServices *s) {
    GSStatus status;w->run.water_y=200;duplicate_palette(w);size_t position=0;
    for(unsigned pages=0;pages<32768;pages++) {
        STEP(wait_count(w,s,40));STEP(game_clear_video(w,s));STEP(game_front_header(w,s));STEP(game_front_save_background(w,s));STEP(game_video_swap(w,s));STEP(restore_all(w,s));
        if(position>=453)return outcome(GS_UNSUPPORTED,0);if(w->front_data.credits[position]==255)return outcome(GS_OK,0);
        size_t end=position;uint16_t separators=0;
        for(;;){if(end>=453)return outcome(GS_UNSUPPORTED,0);uint8_t ch=w->front_data.credits[end++];if(!ch)break;if(ch==253||ch==13)separators++;}
        GameFrontText text={{w->front_data.credits,453},position,0,menus_center_credits(separators),0};STEP(game_front_text_block(w,s,&text));position=text.position;
        STEP(game_video_swap(w,s));STEP(game_video_fade(w,s,0));uint8_t scan;int timeout;STEP(front_wait(w,s,350,&scan,&timeout));STEP(game_video_fade(w,s,1));
        if(!timeout)return outcome(GS_OK,menus_credits_result(scan));
    }return outcome(GS_OVERFLOW,0);
}
GSStatus game_front_introduction(GameWorld *w,GameServices *s,GSBytes introduction,GSBytes password) {
    TRY(game_clear_video(w,s));uint16_t saved_y=w->run.water_y;w->run.water_y=175;
    TRY(game_front_digits(w,menus_level_ordinal((uint8_t)w->run.level),2));
    for(unsigned i=0;i<2;i++)w->front.level_characters[i]=menus_ascii_digit(w->front_data.digits[i]);
    uint8_t title[10];memcpy(title,w->front_data.level_title,10);memcpy(title+7,w->front.level_characters,2);
    GameFrontText text={{title,10},0,0,32,0};TRY(game_front_text_line(w,s,&text));
    text=(GameFrontText){introduction,0,0,(uint16_t)(text.y+32),0};TRY(game_front_text_block(w,s,&text));
    text=(GameFrontText){{w->front_data.password_title,12},0,0,160,0};TRY(game_front_text_line(w,s,&text));
    text=(GameFrontText){password,0,0,text.y,0};TRY(game_front_text_line(w,s,&text));TRY(game_video_swap(w,s));
    TRY(game_audio_music_stop(w,s,17).status);
    TRY(game_audio_effect(w,s,game_audio_intro_resource(),225,1).status);
    TRY(game_video_fade(w,s,0));TRY(wait_scan(w,s));
    w->run.water_y=saved_y;return game_video_fade(w,s,1);
}

