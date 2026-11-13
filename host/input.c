/* SDL set-1 mapping adapted from the read-only pre2 host. */
#include "host.h"
#include <ctype.h>
#include <string.h>
static uint8_t scans[4096],held[SDL_SCANCODE_COUNT];
static unsigned scan_head,scan_tail;
static uint16_t bios[256];
static unsigned bios_head,bios_tail;
static int bios_active;
static SDL_Gamepad *gamepad;
static int pad_held[6];
static int focused=1;
void host_enqueue(uint8_t scan) {
    if(scan_tail-scan_head==4096) host_fail("keyboard queue full");
    scans[scan_tail++%4096]=scan;
}
int host_take_scan(uint8_t *scan) {
    if(scan_head==scan_tail) return 0;
    *scan=scans[scan_head++%4096]; return 1;
}
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
static void send_key(SDL_Scancode key,int down) {
    int ext; uint8_t code=pc_scancode(key,&ext);
    if(!code) return;
    if(ext) host_enqueue(0xe0);
    host_enqueue((uint8_t)(code|(down?0:128)));
}
void host_input_release(void) {
    for(unsigned i=0;i<SDL_SCANCODE_COUNT;i++) if(held[i]) { send_key((SDL_Scancode)i,0); held[i]=0; }
    static const SDL_Scancode pad_keys[]={SDL_SCANCODE_LEFT,SDL_SCANCODE_RIGHT,SDL_SCANCODE_UP,SDL_SCANCODE_DOWN,SDL_SCANCODE_RCTRL,SDL_SCANCODE_F1};
    for(unsigned i=0;i<6;i++) if(pad_held[i]) { send_key(pad_keys[i],0); pad_held[i]=0; }
}
void host_gamepad_init(void) {
    int count=0; SDL_JoystickID *ids=SDL_GetGamepads(&count);
    if(count) gamepad=SDL_OpenGamepad(ids[0]);
    SDL_free(ids);
}
void host_input_pump(void) {
    if(host_headless) return;
    SDL_Event e;
    while(SDL_PollEvent(&e)) {
        if(e.type==SDL_EVENT_QUIT) host_quit=1;
        if(e.type==SDL_EVENT_WINDOW_FOCUS_LOST) { focused=0; host_input_release(); }
        if(e.type==SDL_EVENT_WINDOW_FOCUS_GAINED) focused=1;
        if(e.type==SDL_EVENT_GAMEPAD_ADDED && !gamepad) gamepad=SDL_OpenGamepad(e.gdevice.which);
        if(e.type==SDL_EVENT_GAMEPAD_REMOVED && gamepad && e.gdevice.which==SDL_GetGamepadID(gamepad)) {
            host_input_release(); SDL_CloseGamepad(gamepad); gamepad=NULL;
        }
        if(host_scripted) continue;
        if(e.type==SDL_EVENT_KEY_DOWN || e.type==SDL_EVENT_KEY_UP) {
            int down=e.type==SDL_EVENT_KEY_DOWN;
            if((unsigned)e.key.scancode<SDL_SCANCODE_COUNT) held[e.key.scancode]=(uint8_t)down;
            if(!bios_active) send_key(e.key.scancode,down);
            if(down && bios_active) {
                int ext; uint8_t code=pc_scancode(e.key.scancode,&ext);
                unsigned ascii=e.key.key<128?(unsigned)e.key.key:0;
                if(ascii>='a' && ascii<='z') ascii=(unsigned)toupper((int)ascii);
                if(e.key.scancode==SDL_SCANCODE_RETURN) ascii=13;
                if(e.key.scancode==SDL_SCANCODE_ESCAPE) ascii=27;
                if(e.key.scancode==SDL_SCANCODE_BACKSPACE) ascii=8;
                if(bios_tail-bios_head<256) bios[bios_tail++%256]=(uint16_t)(ascii+256*code);
            }
        }
    }
    if(gamepad && !host_scripted && focused && !bios_active) {
        int x=SDL_GetGamepadAxis(gamepad,SDL_GAMEPAD_AXIS_LEFTX),y=SDL_GetGamepadAxis(gamepad,SDL_GAMEPAD_AXIS_LEFTY);
        int now[]={x < -12000 || SDL_GetGamepadButton(gamepad,SDL_GAMEPAD_BUTTON_DPAD_LEFT),
            x > 12000 || SDL_GetGamepadButton(gamepad,SDL_GAMEPAD_BUTTON_DPAD_RIGHT),
            y < -12000 || SDL_GetGamepadButton(gamepad,SDL_GAMEPAD_BUTTON_DPAD_UP),
            y > 12000 || SDL_GetGamepadButton(gamepad,SDL_GAMEPAD_BUTTON_DPAD_DOWN),
            SDL_GetGamepadButton(gamepad,SDL_GAMEPAD_BUTTON_SOUTH),SDL_GetGamepadButton(gamepad,SDL_GAMEPAD_BUTTON_START)};
        static const SDL_Scancode keys[]={SDL_SCANCODE_LEFT,SDL_SCANCODE_RIGHT,SDL_SCANCODE_UP,SDL_SCANCODE_DOWN,SDL_SCANCODE_RCTRL,SDL_SCANCODE_F1};
        for(unsigned i=0;i<6;i++) if(now[i]!=pad_held[i]) { send_key(keys[i],now[i]); pad_held[i]=now[i]; }
    }
}
int host_live_interrupt(uint8_t n,Regs *r) {
    if(n==0x21 && r->ax==0x2509) {
        /* Both translated keyboard vector switches also flush the BIOS ring.
         * Mirror that device operation in the independent host BIOS queue. */
        bios_active=!(r->ds==GAME_SEG && r->dx==G(HandleKeyboardScanInterrupt));
        bios_head=bios_tail;
        scan_head=scan_tail;
        return -1;
    }
    if(n!=0x16 || (r->ax>>8)>1) return -1;
    unsigned ah=r->ax>>8; bios_active=1; host_input_pump();
    if(ah==1) { flag(r,ZF,bios_head==bios_tail); if(bios_head!=bios_tail) r->ax=bios[bios_head%256]; return UGH_OK; }
    while(bios_head==bios_tail && !host_quit) { host_input_pump(); SDL_Delay(5); }
    if(host_quit) return UGH_BUDGET;
    r->ax=bios[bios_head++%256];
    return UGH_OK;
}
void host_input_close(void) { SDL_CloseGamepad(gamepad); }


