#include "backend.h"
#include <string.h>
/* Set1 key table reused from the read-only host/input.c. Recipient/joystick
 * state below is typed provider state and has no dependency on that host. */
static uint8_t pc_scancode(SDL_Scancode s, int *extended)
{
    *extended = 0;
    switch (s) {
    case SDL_SCANCODE_ESCAPE: return 0x01;
    case SDL_SCANCODE_1: return 0x02; case SDL_SCANCODE_2: return 0x03; case SDL_SCANCODE_3: return 0x04;
    case SDL_SCANCODE_4: return 0x05; case SDL_SCANCODE_5: return 0x06; case SDL_SCANCODE_6: return 0x07;
    case SDL_SCANCODE_7: return 0x08; case SDL_SCANCODE_8: return 0x09; case SDL_SCANCODE_9: return 0x0A;
    case SDL_SCANCODE_0: return 0x0B; case SDL_SCANCODE_MINUS: return 0x0C; case SDL_SCANCODE_EQUALS: return 0x0D;
    case SDL_SCANCODE_BACKSPACE: return 0x0E; case SDL_SCANCODE_TAB: return 0x0F;
    case SDL_SCANCODE_Q: return 0x10; case SDL_SCANCODE_W: return 0x11; case SDL_SCANCODE_E: return 0x12;
    case SDL_SCANCODE_R: return 0x13; case SDL_SCANCODE_T: return 0x14; case SDL_SCANCODE_Y: return 0x15;
    case SDL_SCANCODE_U: return 0x16; case SDL_SCANCODE_I: return 0x17; case SDL_SCANCODE_O: return 0x18;
    case SDL_SCANCODE_P: return 0x19; case SDL_SCANCODE_RETURN: return 0x1C; case SDL_SCANCODE_LCTRL: return 0x1D;
    case SDL_SCANCODE_A: return 0x1E; case SDL_SCANCODE_S: return 0x1F; case SDL_SCANCODE_D: return 0x20;
    case SDL_SCANCODE_F: return 0x21; case SDL_SCANCODE_G: return 0x22; case SDL_SCANCODE_H: return 0x23;
    case SDL_SCANCODE_J: return 0x24; case SDL_SCANCODE_K: return 0x25; case SDL_SCANCODE_L: return 0x26;
    case SDL_SCANCODE_LSHIFT: return 0x2A; case SDL_SCANCODE_Z: return 0x2C; case SDL_SCANCODE_X: return 0x2D;
    case SDL_SCANCODE_C: return 0x2E; case SDL_SCANCODE_V: return 0x2F; case SDL_SCANCODE_B: return 0x30;
    case SDL_SCANCODE_N: return 0x31; case SDL_SCANCODE_M: return 0x32; case SDL_SCANCODE_RSHIFT: return 0x36;
    case SDL_SCANCODE_LALT: return 0x38; case SDL_SCANCODE_SPACE: return 0x39;
    case SDL_SCANCODE_F1: return 0x3B; case SDL_SCANCODE_F2: return 0x3C; case SDL_SCANCODE_F3: return 0x3D;
    case SDL_SCANCODE_F4: return 0x3E; case SDL_SCANCODE_F5: return 0x3F; case SDL_SCANCODE_F6: return 0x40;
    case SDL_SCANCODE_F7: return 0x41; case SDL_SCANCODE_F8: return 0x42; case SDL_SCANCODE_F9: return 0x43;
    case SDL_SCANCODE_F10: return 0x44;
    case SDL_SCANCODE_LEFTBRACKET: return 0x1A; case SDL_SCANCODE_RIGHTBRACKET: return 0x1B;
    case SDL_SCANCODE_SEMICOLON: return 0x27; case SDL_SCANCODE_APOSTROPHE: return 0x28;
    case SDL_SCANCODE_GRAVE: return 0x29; case SDL_SCANCODE_BACKSLASH: return 0x2B;
    case SDL_SCANCODE_COMMA: return 0x33; case SDL_SCANCODE_PERIOD: return 0x34;
    case SDL_SCANCODE_SLASH: return 0x35; case SDL_SCANCODE_KP_MULTIPLY: return 0x37;
    case SDL_SCANCODE_CAPSLOCK: return 0x3A; case SDL_SCANCODE_NUMLOCKCLEAR: return 0x45;
    case SDL_SCANCODE_SCROLLLOCK: return 0x46; case SDL_SCANCODE_F11: return 0x57;
    case SDL_SCANCODE_F12: return 0x58;
    case SDL_SCANCODE_KP_7: return 0x47; case SDL_SCANCODE_KP_8: return 0x48;
    case SDL_SCANCODE_KP_9: return 0x49; case SDL_SCANCODE_KP_MINUS: return 0x4A;
    case SDL_SCANCODE_KP_4: return 0x4B; case SDL_SCANCODE_KP_5: return 0x4C;
    case SDL_SCANCODE_KP_6: return 0x4D; case SDL_SCANCODE_KP_PLUS: return 0x4E;
    case SDL_SCANCODE_KP_1: return 0x4F; case SDL_SCANCODE_KP_2: return 0x50;
    case SDL_SCANCODE_KP_3: return 0x51; case SDL_SCANCODE_KP_0: return 0x52;
    case SDL_SCANCODE_KP_PERIOD: return 0x53;
    /* the extended group: E0h, then the code of the numeric-pad / left-hand key it doubles */
    case SDL_SCANCODE_UP: *extended = 1; return 0x48; case SDL_SCANCODE_LEFT: *extended = 1; return 0x4B;
    case SDL_SCANCODE_RIGHT: *extended = 1; return 0x4D; case SDL_SCANCODE_DOWN: *extended = 1; return 0x50;
    case SDL_SCANCODE_HOME: *extended = 1; return 0x47; case SDL_SCANCODE_PAGEUP: *extended = 1; return 0x49;
    case SDL_SCANCODE_END: *extended = 1; return 0x4F; case SDL_SCANCODE_PAGEDOWN: *extended = 1; return 0x51;
    case SDL_SCANCODE_INSERT: *extended = 1; return 0x52; case SDL_SCANCODE_DELETE: *extended = 1; return 0x53;
    case SDL_SCANCODE_RCTRL: *extended = 1; return 0x1D; case SDL_SCANCODE_RALT: *extended = 1; return 0x38;
    case SDL_SCANCODE_KP_ENTER: *extended = 1; return 0x1C; case SDL_SCANCODE_KP_DIVIDE: *extended = 1; return 0x35;
    default: return 0;
    }
}

void gs_input_init(GSSdlInput *in) {memset(in,0,sizeof *in);in->installed.token=1;in->editor=1;in->focused=1;}
GSStatus gs_input_key(GSSdlInput *in,SDL_Scancode key,int down,int repeat,uint32_t text) {
 if((unsigned)key>=SDL_SCANCODE_COUNT)return GS_UNSUPPORTED;
 int ext;uint8_t code=pc_scancode(key,&ext);if(!code)return GS_UNSUPPORTED;
 if(!repeat && in->held[key]==!!down)return GS_OK;
 if(in->editor) {
  if(down){
   if(in->bios_tail-in->bios_head==256)return GS_OVERFLOW;
   unsigned ascii=text<128?text:0;if(ascii>='a'&&ascii<='z')ascii-=32;
   if(key==SDL_SCANCODE_RETURN||key==SDL_SCANCODE_KP_ENTER)ascii=13;
   if(key==SDL_SCANCODE_ESCAPE)ascii=27;
   if(key==SDL_SCANCODE_BACKSPACE)ascii=8;
   in->bios[in->bios_tail++%256]=(uint16_t)(ascii+256*code);
  }
 } else {
  if(4096u-(in->scan_tail-in->scan_head)<(unsigned)(ext?2:1))return GS_OVERFLOW;
  if(ext)in->scans[in->scan_tail++%4096]=0xe0;
  in->scans[in->scan_tail++%4096]=(uint8_t)(code|(down?0:128));
 }
 in->held[key]=(uint8_t)!!down;return GS_OK;
}
GSStatus gs_input_focus_lost(GSSdlInput *in) {
 in->focused=0;
 for(unsigned k=0;k<SDL_SCANCODE_COUNT;k++)if(in->held[k]) {
  GSStatus status=gs_input_key(in,(SDL_Scancode)k,0,0,0);if(status!=GS_OK)return status;
 }return GS_OK;
}
GSStatus gs_input_editor(GSSdlInput *in,int active) {
 /* Retire physical holds before changing recipients; a later stale key-up must
  * not leak a break into the newly installed recipient. */
 memset(in->held,0,sizeof in->held);in->scan_head=in->scan_tail;in->bios_head=in->bios_tail;
 in->editor=(uint8_t)!!active;return GS_OK;
}
GSStatus gs_input_gamepad(GSSdlInput *in,unsigned stick,int present,int16_t x,int16_t y,uint8_t buttons) {
 if(stick>=2)return GS_INVALID;
 in->present[stick]=(uint8_t)!!present;in->axes[2*stick]=x;in->axes[2*stick+1]=y;in->buttons[stick]=present?(buttons&3):0;return GS_OK;
}
/* Virtual discharge units: neutral1000, signed endpoints250/1750. Calibration
 * and samples use the same units. No deadzone or direction policy is supplied. */
uint16_t gs_input_axis_count(int16_t axis) {
 if(axis<0)return (uint16_t)(1000+(int32_t)axis*750/32768);
 return (uint16_t)(1000+(int32_t)axis*750/32767);
}
static GSStatus scan(void *ctx,uint8_t *byte) {
 GSSdlInput *in=ctx;if(!byte)return GS_INVALID;
 if(in->scan_head==in->scan_tail)return GS_EMPTY;
 *byte=in->scans[in->scan_head++%4096];return GS_OK;
}
static GSStatus acknowledge(void *ctx){(void)ctx;return GS_OK;}
static GSStatus queue(void *ctx,GSQueueOp op,uint16_t *word) {
 GSSdlInput *in=ctx;if(!word||(unsigned)op>GS_QUEUE_TAKE)return GS_INVALID;
 if(in->bios_head==in->bios_tail)return GS_EMPTY;
 *word=in->bios[in->bios_head%256];if(op==GS_QUEUE_TAKE)in->bios_head++;return GS_OK;
}
static GSStatus flush(void *ctx,uint16_t *reply){GSSdlInput *in=ctx;if(!reply)return GS_INVALID;in->bios_head=in->bios_tail;*reply=in->flush_reply;return GS_OK;}
static GSStatus vector(void *ctx,GSVectorOp op,GSBinding binding,GSBinding *reply) {
 GSSdlInput *in=ctx;if(!reply)return GS_INVALID;
 if(op==GS_VECTOR_CAPTURE){*reply=in->installed;return GS_OK;}
 if(op!=GS_VECTOR_INSTALL&&op!=GS_VECTOR_RESTORE)return GS_INVALID;
 if(binding.token!=1&&binding.token!=2)return GS_UNSUPPORTED;
 in->installed=binding;*reply=binding;return gs_input_editor(in,binding.token==1);
}
static GSStatus start(void *ctx,uint8_t trigger){(void)ctx;(void)trigger;return GS_OK;}
static GSStatus presence(void *ctx,uint8_t *reply) {
 GSSdlInput *in=ctx;if(!reply)return GS_INVALID;
 *reply=(uint8_t)((0xf0^((unsigned)in->buttons[0]<<4)^((unsigned)in->buttons[1]<<6))|(in->present[0]?0:3)|(in->present[1]?0:12));return GS_OK;
}
static GSStatus buttons(void *ctx,unsigned stick,uint16_t *reply) {
 GSSdlInput *in=ctx;if(!reply||stick>=2)return GS_INVALID;
 *reply=(uint16_t)(in->buttons[stick]<<(stick?6:4));return GS_OK;
}
static GSStatus counts(void *ctx,uint16_t limit,uint8_t enabled,GSJoystickCounts *reply) {
 GSSdlInput *in=ctx;if(!reply)return GS_INVALID;
 if(enabled&0xf0)return GS_UNSUPPORTED;
 uint32_t cycles=limit?limit:65536u,latest=0;int incomplete=0,any=0;
 memset(reply,0,sizeof *reply);
 for(unsigned a=0;a<4;a++) {
  if(enabled&(1u<<a)) {
   any=1;unsigned n=in->present[a/2]?gs_input_axis_count(in->axes[a]):cycles;
   if(n>=cycles)incomplete=1;
   else {reply->latched[a]=(uint16_t)(limit-n);if(latest<n)latest=n;}
  }
  reply->counts[a]=(uint16_t)(limit-reply->latched[a]);
 }
 reply->remaining=(uint16_t)(!any||incomplete?0:limit-latest);return GS_OK;
}
static void open_pads(GSSdlInput *in) {
 int count=0;SDL_JoystickID *ids=SDL_GetGamepads(&count);
 for(int k=0;k<count;k++) {
  int known=0;for(unsigned j=0;j<2;j++)if(in->pads[j]&&SDL_GetGamepadID(in->pads[j])==ids[k])known=1;
  if(!known)for(unsigned j=0;j<2;j++)if(!in->pads[j]){in->pads[j]=SDL_OpenGamepad(ids[k]);break;}
 }SDL_free(ids);
}
static GSStatus pump(void *ctx,GSInputPollCut cut) {
 if((unsigned)cut>GS_INPUT_WAIT)return GS_UNSUPPORTED;
 GSSdlInput *in=ctx;SDL_Event event;
 while(SDL_PollEvent(&event)) {
  GSStatus status=GS_OK;
  if(event.type==SDL_EVENT_QUIT)in->quit=1;
  else if(event.type==SDL_EVENT_WINDOW_FOCUS_GAINED)in->focused=1;
  else if(event.type==SDL_EVENT_WINDOW_FOCUS_LOST)status=gs_input_focus_lost(in);
  else if(event.type==SDL_EVENT_KEY_DOWN||event.type==SDL_EVENT_KEY_UP)
   status=gs_input_key(in,event.key.scancode,event.type==SDL_EVENT_KEY_DOWN,event.key.repeat,(uint32_t)event.key.key);
  else if(event.type==SDL_EVENT_GAMEPAD_REMOVED)for(unsigned j=0;j<2;j++)if(in->pads[j]&&SDL_GetGamepadID(in->pads[j])==event.gdevice.which){SDL_CloseGamepad(in->pads[j]);in->pads[j]=NULL;gs_input_gamepad(in,j,0,0,0,0);}
  if(status!=GS_OK&&status!=GS_UNSUPPORTED)return status;
 }
 open_pads(in);
 for(unsigned j=0;j<2;j++)if(in->pads[j])gs_input_gamepad(in,j,1,
  in->focused?SDL_GetGamepadAxis(in->pads[j],SDL_GAMEPAD_AXIS_LEFTX):0,in->focused?SDL_GetGamepadAxis(in->pads[j],SDL_GAMEPAD_AXIS_LEFTY):0,
  in->focused?(uint8_t)(SDL_GetGamepadButton(in->pads[j],SDL_GAMEPAD_BUTTON_SOUTH)|(SDL_GetGamepadButton(in->pads[j],SDL_GAMEPAD_BUTTON_EAST)<<1)):0);
 return in->quit?GS_QUIT:GS_OK;
}
void gs_input_close(GSSdlInput *in){for(unsigned j=0;j<2;j++){SDL_CloseGamepad(in->pads[j]);in->pads[j]=NULL;}}
GSInputOps gs_input_operations(void){return (GSInputOps){scan,acknowledge,queue,flush,vector,start,presence,buttons,counts,pump,NULL};}
