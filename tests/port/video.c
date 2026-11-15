#include "sdl/backend.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
/* The oracle compiles the unchanged host_render body with this narrow test-only
 * device-shaped input. It imports no game functions or state owners. */
typedef struct {uint8_t plane[4][65536],dac[768],crtc[25];} OracleDevice;
OracleDevice ugh_devices;
void host_render(uint32_t *);
static GSSdlVideo video;
static uint32_t expected[64000],actual[64000];
static int compare(void){
 memcpy(ugh_devices.plane,video.planes,sizeof video.planes);memcpy(ugh_devices.dac,video.dac,sizeof video.dac);memcpy(ugh_devices.crtc,video.crtc,sizeof video.crtc);
 host_render(expected);gs_video_rgb(&video,actual);
 for(unsigned i=0;i<64000;i++)if(actual[i]!=expected[i]){fprintf(stderr,"RGB first difference pixel %u: %08x / %08x\n",i,actual[i],expected[i]);return 1;}
 return 0;
}
int main(int argc,char **argv){
 if(argc!=3)return 2;
 gs_video_init(&video);FILE *file=fopen(argv[1],"rb");if(!file)return 3;
 if(fread(video.planes,1,sizeof video.planes,file)!=sizeof video.planes||fread(video.dac,1,768,file)!=768||fread(video.crtc,1,25,file)!=25||fgetc(file)!=EOF)return 4;
 fclose(file);
 if(compare())return 5;
 unsigned colored=0;for(unsigned i=0;i<64000;i++)colored+=actual[i]!=0xff000000u;if(colored<100)return 6;
 file=fopen(argv[2],"wb");if(!file||fwrite(expected,4,64000,file)!=64000||fclose(file))return 7;
 for(unsigned p=0;p<4;p++)for(unsigned cell=0;cell<65536;cell++)video.planes[p][cell]=(uint8_t)(cell*13u+p*71u);
 for(unsigned c=0;c<768;c++)video.dac[c]=(uint8_t)((c*31u)&63);
 const unsigned starts[]={0,0xa88,0x5a08,0xffff},pitches[]={0,40,48,255},splits[]={0,15,383,1023};
 for(unsigned a=0;a<4;a++)for(unsigned b=0;b<4;b++)for(unsigned c=0;c<4;c++){
  video.crtc[12]=(uint8_t)(starts[a]>>8);video.crtc[13]=(uint8_t)starts[a];video.crtc[19]=(uint8_t)pitches[b];video.crtc[24]=(uint8_t)splits[c];video.crtc[7]=(uint8_t)((splits[c]>>4)&16);video.crtc[9]=(uint8_t)((splits[c]>>3)&64);
  if(compare())return 8;
 }puts("PASS picture RGB +64 page/pitch/split cases");return 0;
}
