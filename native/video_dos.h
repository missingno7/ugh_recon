#ifndef NATIVE_VIDEO_DOS_H
#define NATIVE_VIDEO_DOS_H
#include <stdint.h>

/* Borrowed state of the one existing video owner. Page positions are byte
 * offsets in each plane's aperture, not chunky pixel indices. Storage/bank
 * bindings belong to the platform and survive offset-only configuration. */
typedef struct VideoPages {
    uint16_t draw,displayed,background,fixed,height,plane_copy_bytes;
} VideoPages;
typedef struct VideoGeometry {VideoPages pages;uint8_t stride,split_line;} VideoGeometry;
VideoGeometry video_geometry(int gameplay);
void video_swap(VideoPages *pages);
typedef struct VideoRegisterSetting {uint8_t device,index,mask,bits,read_previous;} VideoRegisterSetting;
/* device 0: sequencer; 1: CRTC. Ordinals 0..6 are executed in order. */
VideoRegisterSetting video_mode_setting(unsigned ordinal,int gameplay);
uint8_t video_register_value(VideoRegisterSetting setting,uint8_t previous);
uint8_t video_attribute_mode(uint8_t previous);
uint8_t video_all_planes(void);

typedef struct VideoScaled {uint16_t low,high;uint8_t value;} VideoScaled;
VideoScaled video_palette_scale(uint8_t component,uint16_t factor);
typedef struct VideoPaletteRange {uint16_t cursor,entries;int8_t direction;} VideoPaletteRange;
VideoPaletteRange video_palette_range(uint16_t origin,uint8_t first,uint8_t last,int reverse);
uint16_t video_palette_advance(VideoPaletteRange *range);
uint16_t video_fade_step(uint16_t factor,int fading_out);
int video_fade_continue(uint16_t factor,int fading_out);
unsigned video_blackening_batches(void);
unsigned video_blackening_entries(void);
typedef struct VideoCopyCursor {uint16_t source,destination,remaining;int8_t direction;} VideoCopyCursor;
VideoCopyCursor video_duplicate_begin(uint16_t source,uint16_t destination,int reverse);
void video_duplicate_advance(VideoCopyCursor *cursor);
uint16_t video_duplicate_second(uint16_t destination);
typedef struct VideoDuplicateTransfer {uint16_t source,destinations[2];} VideoDuplicateTransfer;
/* Read the word once, then perform destinations[0], destinations[1] in order. */
VideoDuplicateTransfer video_duplicate_transfer(const VideoCopyCursor *cursor);
typedef struct VideoClearCursor {uint16_t position,remaining;int8_t direction;} VideoClearCursor;
VideoClearCursor video_clear_begin(int reverse);
void video_clear_advance(VideoClearCursor *cursor);
VideoClearCursor video_scale_begin(void);
void video_scale_advance(VideoClearCursor *cursor);
typedef struct VideoChunkyCursor {uint16_t source,destination;uint32_t remaining;uint8_t plane;int8_t direction;} VideoChunkyCursor;
VideoChunkyCursor video_chunky_begin(uint16_t source,uint16_t destination,uint16_t count,int reverse);
uint8_t video_chunky_mask(const VideoChunkyCursor *cursor);
void video_chunky_advance(VideoChunkyCursor *cursor);

/* Raw status is a level delivery. Compound waits request two levels in order.
 * An event backend may deliver the requested level without spinning. The
 * diagnostic budget matches L1; the DOS original has no timeout. */
typedef struct VideoRetrace {uint32_t budget;uint8_t active;} VideoRetrace;
int video_retrace_delivery(VideoRetrace *wait,uint8_t status);
int video_retrace_level(int through,unsigned phase);
uint16_t video_wait_decrement(uint16_t remaining);
typedef enum VideoWaitAction {VIDEO_WAIT_INITIAL_SCAN,VIDEO_WAIT_SERVICE,VIDEO_WAIT_SCAN,VIDEO_WAIT_SAMPLE,VIDEO_WAIT_RETRACE,VIDEO_WAIT_COUNT,VIDEO_WAIT_DONE_SCAN,VIDEO_WAIT_DONE_DEFAULT} VideoWaitAction;
typedef struct VideoTimeout {uint8_t stage;} VideoTimeout;
VideoWaitAction video_timeout_next(VideoTimeout *wait,uint16_t reply);
uint8_t video_critical_error_result(void);
#endif
