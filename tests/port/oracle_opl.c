/* Independent direct provider oracle. Links only the pinned synthesizer. */
#include <stdint.h>
#include <stdio.h>
#include "opl3.h"
#include "opl_sequence.h"
int main(int argc,char **argv) {
 if(argc!=2)return 2;
 FILE *file=fopen(argv[1],"wb");if(!file)return 3;
 opl3_chip chip;OPL3_Reset(&chip,48000);unsigned event=0;
 for(unsigned frame=0;frame<OPL_GOLDEN_FRAMES;frame++){
  while(event<sizeof opl_sequence/sizeof *opl_sequence&&opl_sequence[event].frame==frame){OPL3_WriteRegBuffered(&chip,opl_sequence[event].reg,opl_sequence[event].value);event++;}
  int16_t sample[2];OPL3_GenerateStream(&chip,sample,1);if(fwrite(sample,4,1,file)!=1)return 4;
 }return fclose(file)?5:0;
}
