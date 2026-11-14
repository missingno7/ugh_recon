#include "platform.h"
#include "../pictures.h"

static void push(Regs *r,uint16_t value) {r->sp=(uint16_t)(r->sp-2);wr16(r->ss,r->sp,value);}
static uint16_t pop(Regs *r) {uint16_t value=rd16(r->ss,r->sp);r->sp=(uint16_t)(r->sp+2);return value;}
#define PCALL(name,ret) do {int status=ugh_call_near(G(name),ret,r);if(status) return status;} while(0)

/* Source starts at resource byte0. The current ICE entry owns all bit/run
 * decoding and its malformed-stream behavior. Even bad magic returns normally
 * and the palette copy still runs over the stale scratch image. */
EXPORT int c_UnpackPictureAndCopyPalette(Regs *r)
{
 push(r,r->cx);push(r,r->ds);r->ds=r->si;r->si=logic(r,0,16);
 r->di=rd16(r->cs,G(IceScratchPointer));r->es=rd16(r->cs,G(IceScratchPointer)+2);
 PCALL(UnpackIceStream,G(UnpackPictureAndCopyPalette)+14);
 r->si=PICTURE_PIXELS;r->ds=pop(r);push(r,r->ds);r->cx=r->es;
 r->di=rd16(r->cs,G(PicturePaletteDestination));r->es=rd16(r->cs,G(PicturePaletteDestination)+2);
 r->ds=r->cx;
 PicturePaletteCopy copy=pictures_palette_begin(r->di,!!(r->flags&DF));r->cx=copy.remaining;
 do {
  uint16_t value=rd16(r->ds,copy.source);
  r->si=(uint16_t)(copy.source+2*copy.direction);
  wr16(r->es,copy.destination,value);
  pictures_palette_advance(&copy);r->di=copy.destination;r->cx=copy.remaining;
 } while(copy.remaining);
 r->ds=pop(r);r->cx=pop(r);return UGH_OK;
}

EXPORT int c_ShowPackedPictureAndWait(Regs *r)
{
 PictureShowFlow flow={0};push(r,r->cx);
 for(;;) switch(pictures_show_next(&flow)) {
 case PICTURE_EXPAND:PCALL(UnpackPictureAndCopyPalette,G(ShowPackedPictureAndWait)+4);break;
 case PICTURE_UPLOAD:PCALL(UploadChunkyImageToVgaPlanes,G(ShowPackedPictureAndWait)+7);break;
 case PICTURE_SWAP:PCALL(SwapAndDisplayVgaPage,G(ShowPackedPictureAndWait)+10);break;
 case PICTURE_FADE_IN:PCALL(FadePaletteIn,G(ShowPackedPictureAndWait)+13);r->cx=pop(r);break;
 case PICTURE_WAIT:PCALL(WaitForInputOrRetraceTimeout,G(ShowPackedPictureAndWait)+17);break;
 case PICTURE_FADE_OUT:push(r,r->ax);PCALL(FadePaletteOut,G(ShowPackedPictureAndWait)+21);break;
 default:
  r->ax=pop(r);set_al(r,(uint8_t)logic(r,r->ax&127,8));
  r->ax=(uint16_t)pictures_input_result((uint8_t)r->ax);logic(r,r->ax,16);return UGH_OK;
 }
}

static uint16_t resource_segment(PictureKind picture)
{
 switch(picture) {
 case PICTURE_PLAY_BYTE:return UGH_S_B2D9A_ext_2D9A;
 case PICTURE_BONES_PARK:return UGH_S_B2BF6_ext_2BF6;
 case PICTURE_PRESENT:return UGH_S_B2F9E_ext_2F9E;
 default:return UGH_S_B2FB7_ext_2FB7;
 }
}
EXPORT int c_ShowStartupPictures(Regs *r)
{
 for(unsigned index=0;index<4;index++) {
  PictureStartupItem item=pictures_startup_item(index);
  r->si=resource_segment(item.picture);r->cx=item.retraces;
  PCALL(ShowPackedPictureAndWait,(uint16_t)(G(ShowStartupPictures)+10+20*index));
  switch(pictures_startup_route(index,!!(r->flags&SF),!!(r->flags&ZF))) {
  case PICTURE_SHUTDOWN:return ugh_dispatch(r->cs,G(loc_4EE6),r);
  case PICTURE_RETURN:return UGH_OK;
  default:break;
  }
 }
 return UGH_OK;
}
