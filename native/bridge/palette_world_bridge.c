#include "platform.h"
#include "palette_world_bridge.h"
#include "audio_world_bridge.h"
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
static unsigned active;
static const uint8_t seal=0xa5;
static int palette_index(uint32_t address,unsigned *index){
 uint32_t base=lin(GAME_SEG,G(BaseRgbPalette)),faded=lin(GAME_SEG,G(FadedRgbPalette));
 if(address>=base && address-base<PALETTE_COMPONENTS){*index=(unsigned)(address-base);return 1;}
 if(address>=faded && address-faded<PALETTE_COMPONENTS){*index=PALETTE_COMPONENTS+(unsigned)(address-faded);return 1;}
 return 0;
}
static uint8_t palette_get(unsigned index){
 NativePaletteWorld *w=native_palette_world();
 return index<PALETTE_COMPONENTS?w->base[index]:w->faded[index-PALETTE_COMPONENTS];
}
static void palette_put(unsigned index,uint8_t value){
 NativePaletteWorld *w=native_palette_world();
 if(index<PALETTE_COMPONENTS)w->base[index]=value;else w->faded[index-PALETTE_COMPONENTS]=value;
}
int palette_is_owned(uint32_t address){unsigned i;return active && palette_index(address,&i);}
int palette_shared_read(uint32_t address,uint8_t *value){unsigned i;if(!active || !palette_index(address,&i))return 0;*value=palette_get(i);
#if PALETTE_TEST_FAULT == 3
 if(i<PALETTE_COMPONENTS)*value=0;
#endif
 return 1;}
int palette_shared_write(uint32_t address,uint8_t value){unsigned i;if(!active || !palette_index(address,&i))return 0;palette_put(i,value);return 1;}
static uint32_t palette_address(unsigned index){return index<PALETTE_COMPONENTS?lin(GAME_SEG,(uint16_t)(G(BaseRgbPalette)+index)):lin(GAME_SEG,(uint16_t)(G(FadedRgbPalette)+index-PALETTE_COMPONENTS));}
void palette_cold_import(uint8_t *memory){
 active=0;
 for(unsigned i=0;i<2u*PALETTE_COMPONENTS;i++)palette_put(i,memory[palette_address(i)]);
 for(unsigned i=0;i<2u*PALETTE_COMPONENTS;i++)memory[palette_address(i)]=seal;
 active=1;
}
void palette_require_seal(const uint8_t *memory){
 if(!active)return;
 for(unsigned i=0;i<2u*PALETTE_COMPONENTS;i++)if(memory[palette_address(i)]!=seal){fputs("palette: sealed RAM violation\n",stderr);abort();}
}
unsigned palette_owned_bytes(void){return active?2u*PALETTE_COMPONENTS:0;}
void palette_serialize(uint8_t *output){
 if(!active)return;
 for(unsigned i=0;i<2u*PALETTE_COMPONENTS;i++)output[palette_address(i)]=seal;
 unsigned emitted=0;
 for(unsigned i=0;i<2u*PALETTE_COMPONENTS;i++){
#if PALETTE_TEST_FAULT == 1
  if(!i)continue;
#endif
  output[palette_address(i)]=palette_get(i);emitted++;
 }
 if(emitted!=palette_owned_bytes()){fputs("palette: missed serialization\n",stderr);exit(88);}
}
uint32_t palette_check_serialization(const uint8_t *output){
 if(active)for(unsigned i=0;i<2u*PALETTE_COMPONENTS;i++)if(output[palette_address(i)]!=palette_get(i))return palette_address(i);
 return UINT32_MAX;
}
uint8_t palette_borrowed_byte(const uint8_t *window,uint32_t index){
 size_t p=(size_t)window,base=(size_t)ugh_mem;
 if(p>=base && p-base+index<UGH_MEM_SIZE){uint8_t value;if(palette_shared_read((uint32_t)(p-base+index),&value))return value;}
 return audio_borrowed_byte(window,index);
}
void palette_borrowed_store(uint8_t *window,uint32_t index,uint8_t value){
 size_t p=(size_t)window,base=(size_t)ugh_mem;
 if(p>=base && p-base+index<UGH_MEM_SIZE && palette_shared_write((uint32_t)(p-base+index),value))return;
 audio_borrowed_store(window,index,value);
}
int palette_peer_deliver(PalettePeerRole role,uint16_t return_identity,Regs *r){
 if(r->cs!=GAME_SEG)return UGH_BAD_CALLBACK;
 r->sp=(uint16_t)(r->sp-2);wr16(r->ss,r->sp,return_identity);
 int status;
 switch(role){
 case PALETTE_PEER_WaitNextVerticalRetrace:status=c_WaitNextVerticalRetrace(r);break;
 case PALETTE_PEER_ScaleAndUploadFadedPalette:status=c_ScaleAndUploadFadedPalette(r);break;
 default:return UGH_BAD_CALLBACK;
 }
 if(status)return status;
 r->sp=(uint16_t)(r->sp+2);return UGH_OK;
}
