#include "video_dos.h"
VideoGeometry video_geometry(int gameplay)
{
    VideoGeometry result={{0x3e80,0,0x7d00,0,200,0x3e80},0x28,0x8f};
    if(gameplay) {VideoPages pages={0x5a08,0x0a88,0xa988,0,192,0x4800};result.pages=pages;result.stride=0x30;result.split_line=0x7f;}
    return result;
}
void video_swap(VideoPages *pages) {uint16_t draw=pages->draw;pages->draw=pages->displayed;pages->displayed=draw;}
VideoRegisterSetting video_mode_setting(unsigned ordinal,int gameplay)
{
    static const VideoRegisterSetting settings[]={
        {0,4,0xf7,0,1},{1,0x14,0xbf,0,1},{1,0x17,0xff,0x40,1},
        {1,0x13,0,0,0},{1,0x18,0,0,0},{1,7,0xef,0x10,1},{1,9,0xbf,0,1}};
    VideoRegisterSetting result=settings[ordinal];VideoGeometry geometry=video_geometry(gameplay);
    if(ordinal==3) result.bits=geometry.stride;
    if(ordinal==4) result.bits=geometry.split_line;
    return result;
}
uint8_t video_register_value(VideoRegisterSetting setting,uint8_t previous) {return (uint8_t)((previous&setting.mask)|setting.bits);}
uint8_t video_attribute_mode(uint8_t previous) {return (uint8_t)(previous|32u);}
uint8_t video_all_planes(void) {return 15;}
VideoScaled video_palette_scale(uint8_t component,uint16_t factor)
{
    uint32_t product=(uint32_t)component*factor;
    /* AH of the wrapping product, not saturation or a six-bit mask. */
    VideoScaled result={(uint16_t)product,(uint16_t)(product>>16),(uint8_t)(product>>8)};return result;
}
VideoPaletteRange video_palette_range(uint16_t origin,uint8_t first,uint8_t last,int reverse)
{
    /* Inclusive byte subtraction wraps before widening; reverse only changes
     * component traversal, never the initial first*3 addition. */
    VideoPaletteRange result={(uint16_t)(origin+3u*first),(uint16_t)((uint8_t)(last-first)+1u),(int8_t)(reverse ? -1 : 1)};return result;
}
uint16_t video_palette_advance(VideoPaletteRange *range) {uint16_t before=range->cursor;range->cursor=(uint16_t)(range->cursor+range->direction);return before;}
uint16_t video_fade_step(uint16_t factor,int fading_out) {return (uint16_t)(factor+(fading_out ? -4 : 4));}
int video_fade_continue(uint16_t factor,int fading_out) {return fading_out ? (int16_t)factor>=0 : factor<=256;}
unsigned video_blackening_batches(void) {return 8;}
unsigned video_blackening_entries(void) {return 32;}
VideoCopyCursor video_duplicate_begin(uint16_t source,uint16_t destination,int reverse) {VideoCopyCursor cursor={source,destination,192,(int8_t)(reverse ? -1 : 1)};return cursor;}
void video_duplicate_advance(VideoCopyCursor *cursor) {cursor->source=(uint16_t)(cursor->source+2*cursor->direction);cursor->destination=(uint16_t)(cursor->destination+2*cursor->direction);cursor->remaining--;}
uint16_t video_duplicate_second(uint16_t destination) {return (uint16_t)(destination+384u);}
VideoDuplicateTransfer video_duplicate_transfer(const VideoCopyCursor *cursor)
{
    /* Second-half-first stores retain source/destination alias effects. */
    VideoDuplicateTransfer transfer={cursor->source,{video_duplicate_second(cursor->destination),cursor->destination}};return transfer;
}
VideoClearCursor video_clear_begin(int reverse) {VideoClearCursor cursor={0,32768,(int8_t)(reverse ? -1 : 1)};return cursor;}
void video_clear_advance(VideoClearCursor *cursor) {cursor->position=(uint16_t)(cursor->position+2*cursor->direction);cursor->remaining--;}
VideoClearCursor video_scale_begin(void) {VideoClearCursor cursor={767,768,-1};return cursor;}
void video_scale_advance(VideoClearCursor *cursor) {cursor->position=(uint16_t)(cursor->position-1u);cursor->remaining--;}
VideoChunkyCursor video_chunky_begin(uint16_t source,uint16_t destination,uint16_t count,int reverse) {VideoChunkyCursor cursor={source,destination,count ? count : 65536u,0,(int8_t)(reverse ? -1 : 1)};return cursor;}
uint8_t video_chunky_mask(const VideoChunkyCursor *cursor) {return (uint8_t)(1u<<cursor->plane);}
void video_chunky_advance(VideoChunkyCursor *cursor)
{
    cursor->source=(uint16_t)(cursor->source+cursor->direction);
    if(++cursor->plane==4) {cursor->plane=0;cursor->destination=(uint16_t)(cursor->destination+cursor->direction);cursor->remaining--;}
}
int video_retrace_delivery(VideoRetrace *wait,uint8_t status)
{
    if(!wait->budget) return -1;
    wait->budget--;
    if(!!(status&8)==wait->active) return 0;
    return wait->budget ? 1 : -1;
}
int video_retrace_level(int through,unsigned phase) {return through ? phase==0 : phase!=0;}
uint16_t video_wait_decrement(uint16_t remaining) {return (uint16_t)(remaining-1u);}
VideoWaitAction video_timeout_next(VideoTimeout *wait,uint16_t reply)
{
    for(;;) switch(wait->stage++) {
    case 0:return VIDEO_WAIT_INITIAL_SCAN;
    case 1:return VIDEO_WAIT_SERVICE;
    case 2:return VIDEO_WAIT_SCAN;
    case 3:if(reply) return VIDEO_WAIT_DONE_SCAN;return VIDEO_WAIT_SAMPLE;
    case 4:if(reply) return VIDEO_WAIT_DONE_DEFAULT;return VIDEO_WAIT_RETRACE;
    case 5:return VIDEO_WAIT_COUNT;
    default:if(!reply) return VIDEO_WAIT_DONE_DEFAULT;wait->stage=1;break;
    }
}
uint8_t video_critical_error_result(void) {return 3;}
