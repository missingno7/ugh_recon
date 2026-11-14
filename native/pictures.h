#ifndef NATIVE_PICTURES_H
#define NATIVE_PICTURES_H
#include <stdint.h>

enum {PICTURE_WIDTH=320,PICTURE_HEIGHT=200,PICTURE_PIXELS=64000,
      PICTURE_PALETTE_BYTES=768,PICTURE_DECODED_BYTES=64768};

/* Borrowed decoded picture storage, not a second image/palette owner.
 * ICE expansion remains the existing decompression service. Its output has
 * no inner image header: pixels then256 RGB6 triples. Copy words in order;
 * aliases intentionally propagate, and each cursor wraps independently. */
typedef struct PicturePaletteCopy {
 uint16_t source,destination,remaining;
 int8_t direction;
} PicturePaletteCopy;
PicturePaletteCopy pictures_palette_begin(uint16_t destination,int backwards);
void pictures_palette_advance(PicturePaletteCopy *copy);

typedef enum PictureShowAction {
 PICTURE_EXPAND,PICTURE_UPLOAD,PICTURE_SWAP,PICTURE_FADE_IN,
 PICTURE_WAIT,PICTURE_FADE_OUT,PICTURE_SHOW_DONE
} PictureShowAction;
typedef struct PictureShowFlow {unsigned position;} PictureShowFlow;
PictureShowAction pictures_show_next(PictureShowFlow *flow);
int16_t pictures_input_result(uint8_t scan);

typedef enum PictureKind {
 PICTURE_PLAY_BYTE,PICTURE_BONES_PARK,PICTURE_PRESENT,PICTURE_TITLE
} PictureKind;
typedef struct PictureStartupItem {PictureKind picture;uint16_t retraces;} PictureStartupItem;
typedef enum PictureStartupRoute {PICTURE_NEXT,PICTURE_RETURN,PICTURE_SHUTDOWN} PictureStartupRoute;
/* Index0..3 is supplied by the four-item startup sequence. A negative reply
 * takes priority over zero, including inconsistent service result flags. */
PictureStartupItem pictures_startup_item(unsigned index);
PictureStartupRoute pictures_startup_route(unsigned index,int negative,int zero);
#endif
