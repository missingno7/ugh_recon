/* Recorded physical key and pad inputs; expected set-1 bytes and common counts.
 * No engine bindings/commands are baked into the provider's fixtures. */
static const struct {SDL_Scancode key;int down,repeat;uint32_t text;} scan_events[]={
 {SDL_SCANCODE_A,1,0,'a'},{SDL_SCANCODE_A,1,1,'a'},{SDL_SCANCODE_A,0,0,0},
 {SDL_SCANCODE_UP,1,0,0},{SDL_SCANCODE_UP,0,0,0},
 {SDL_SCANCODE_RCTRL,1,0,0},{SDL_SCANCODE_RCTRL,0,0,0},
 {SDL_SCANCODE_KP_ENTER,1,0,0},{SDL_SCANCODE_KP_ENTER,0,0,0}
};
static const uint8_t scan_bytes[]={0x1e,0x1e,0x9e,0xe0,0x48,0xe0,0xc8,0xe0,0x1d,0xe0,0x9d,0xe0,0x1c,0xe0,0x9c};
static const struct {int16_t axis;uint16_t count;} axis_records[]={
 {-32768,250},{-16384,625},{-1,1000},{0,1000},{1,1000},{16384,1375},{32767,1750}
};
