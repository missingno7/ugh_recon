#include "pictures.h"

PicturePaletteCopy pictures_palette_begin(uint16_t destination,int backwards)
{
 PicturePaletteCopy copy={PICTURE_PIXELS,destination,PICTURE_PALETTE_BYTES/2,
                          (int8_t)(backwards ? -1 : 1)};
 return copy;
}
void pictures_palette_advance(PicturePaletteCopy *copy)
{
 copy->source=(uint16_t)(copy->source+2*copy->direction);
 copy->destination=(uint16_t)(copy->destination+2*copy->direction);
 copy->remaining--;
}
PictureShowAction pictures_show_next(PictureShowFlow *flow)
{
 static const PictureShowAction actions[]={PICTURE_EXPAND,PICTURE_UPLOAD,PICTURE_SWAP,
     PICTURE_FADE_IN,PICTURE_WAIT,PICTURE_FADE_OUT};
 if(flow->position>=sizeof actions/sizeof actions[0]) return PICTURE_SHOW_DONE;
 return actions[flow->position++];
}
int16_t pictures_input_result(uint8_t scan)
{
 scan&=127;
 return scan==1 ? 1 : scan==16 ? -1 : 0;
}
PictureStartupItem pictures_startup_item(unsigned index)
{
 static const PictureStartupItem items[]={
  {PICTURE_PLAY_BYTE,280},{PICTURE_BONES_PARK,280},
  {PICTURE_PRESENT,140},{PICTURE_TITLE,420}};
 return items[index];
}
PictureStartupRoute pictures_startup_route(unsigned index,int negative,int zero)
{
 if(negative) return PICTURE_SHUTDOWN;
 if(index==3 || !zero) return PICTURE_RETURN;
 return PICTURE_NEXT;
}
