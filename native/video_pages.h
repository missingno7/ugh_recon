#ifndef NATIVE_VIDEO_PAGES_H
#define NATIVE_VIDEO_PAGES_H
#include <stdint.h>
/* Storage identities are opaque to the game. The verification provider maps
 * their historical words; offset-only configuration/swap preserves each bank. */
typedef struct VideoBankIdentity {uint16_t value;} VideoBankIdentity;
typedef struct VideoPageBinding {uint16_t position;VideoBankIdentity bank;} VideoPageBinding;
typedef struct NativeVideoPages {
 uint16_t height,copy_count;
 VideoPageBinding fixed,displayed,draw,background;
} NativeVideoPages;
NativeVideoPages *native_video_pages(void);

typedef enum VideoControlRoute {
 VIDEO_SEQ_INDEX,VIDEO_SEQ_DATA,VIDEO_CRTC_INDEX,VIDEO_CRTC_DATA,
 VIDEO_ATTRIBUTE_WRITE,VIDEO_ATTRIBUTE_READ,VIDEO_CONTROL_INVALID
} VideoControlRoute;
typedef struct VideoByteReply {uint8_t value;int status;} VideoByteReply;
void video_service_control_write(VideoControlRoute route,uint8_t value);
VideoByteReply video_service_control_read(VideoControlRoute route);
/* Each source read is live and loads all four hardware latches when applicable.
 * A word store reduces its starting offset once; its high byte is at address+1,
 * including a crossing of the aperture. Neither service clips to a page. */
typedef struct VideoCellAddress {VideoBankIdentity bank;uint16_t position;} VideoCellAddress;
uint8_t video_service_source_byte(VideoCellAddress address);
void video_service_store_byte(VideoCellAddress address,uint8_t value);
void video_service_store_word(VideoCellAddress address,uint16_t value);
VideoByteReply video_service_retrace_level(void);
typedef struct VideoServiceContext VideoServiceContext;
typedef enum VideoServiceCut {VIDEO_CUT_ACTIVE_RETRACE,VIDEO_CUT_INPUT_TIMEOUT} VideoServiceCut;
int video_service_cut(VideoServiceCut cut,VideoServiceContext *context);
int video_service_frame_end(VideoServiceContext *context);
#endif
