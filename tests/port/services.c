#include "sdl/backend.h"
#include "resources.h"
#include "hash.h"
#include "resource_manifest.h"
#include "golden_input.h"
#include "opl_sequence.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define CHECK(x) do{if(!(x)){fprintf(stderr,"FAIL %s:%u: %s\n",__FILE__,__LINE__,#x);return 1;}}while(0)
static GSStatus clock_sink(void *ctx,GSClockDelivery value){unsigned *n=ctx;*n=*n*3+value+1;return GS_OK;}
static int time_input(void) {
 GSSdlTime time;gs_time_init(&time,0);GSTimeOps t=gs_time_operations();GSEvent event;
 for(unsigned i=0;i<7000;i++){
  CHECK(t.deliver(&time,GS_INPUT_OPPORTUNITY,&event)==GS_OK&&event.tick==i);
  CHECK(t.deliver(&time,GS_RETRACE_INACTIVE,&event)==GS_OK&&event.tick==i);
  CHECK(t.deliver(&time,GS_RETRACE_ACTIVE,&event)==GS_OK&&event.tick==i+1);
  CHECK(t.deliver(&time,GS_TIMER_OPPORTUNITY,&event)==GS_OK&&event.tick==i+1);
 }CHECK(event.nanoseconds==100000000000ull);
 uint64_t tick=time.tick;CHECK(t.suspend(&time,1)==GS_OK);CHECK(t.deliver(&time,GS_RETRACE_ACTIVE,&event)==GS_EMPTY&&time.tick==tick);
 CHECK(t.suspend(&time,0)==GS_OK);CHECK(t.deliver(&time,GS_RETRACE_ACTIVE,&event)==GS_OK&&time.tick==tick+1);
 uint64_t retrace_tick=time.retrace_tick;
 for(unsigned i=0;i<3;i++)CHECK(t.deliver(&time,GS_TIMER_OPPORTUNITY,&event)==GS_OK);
 CHECK(time.retrace_tick==retrace_tick&&time.tick==tick+3);
 CHECK(t.deliver(&time,GS_INPUT_OPPORTUNITY,&event)==GS_OK&&time.tick==tick+3);
 CHECK(t.pace(&time)==GS_OK);
 CHECK(t.deliver(&time,(GSEventKind)-1,&event)==GS_INVALID);
 GSSdlTime paced;gs_time_init(&paced,1);uint64_t wall=SDL_GetTicksNS();
 CHECK(t.deliver(&paced,GS_RETRACE_ACTIVE,&event)==GS_OK&&t.pace(&paced)==GS_OK&&paced.tick==1);
 CHECK(SDL_GetTicksNS()-wall>=14000000ull);
 CHECK(gs_lifecycle_operations().request(NULL,(GSLifecycleRequest){GS_LIFECYCLE_START,0},NULL)==GS_UNSUPPORTED);
 GSSdlInput in;gs_input_init(&in);GSInputOps ops=gs_input_operations();GSBinding reply;
 CHECK(ops.vector(&in,GS_VECTOR_CAPTURE,(GSBinding){0},&reply)==GS_OK&&reply.token==1);
 CHECK(ops.vector(&in,GS_VECTOR_INSTALL,(GSBinding){2},&reply)==GS_OK);
 for(unsigned i=0;i<sizeof scan_events/sizeof *scan_events;i++)CHECK(gs_input_key(&in,scan_events[i].key,scan_events[i].down,scan_events[i].repeat,scan_events[i].text)==GS_OK);
 for(unsigned i=0;i<sizeof scan_bytes;i++){uint8_t byte=0;CHECK(ops.scan(&in,&byte)==GS_OK&&byte==scan_bytes[i]);}
 uint8_t byte;CHECK(ops.scan(&in,&byte)==GS_EMPTY);
 CHECK(gs_input_key(&in,SDL_SCANCODE_LEFT,1,0,0)==GS_OK);
 CHECK(gs_input_focus_lost(&in)==GS_OK);
 static const uint8_t releases[]={0xe0,0x4b,0xe0,0xcb};
 for(unsigned i=0;i<sizeof releases;i++)CHECK(ops.scan(&in,&byte)==GS_OK&&byte==releases[i]);
 CHECK(ops.vector(&in,GS_VECTOR_RESTORE,(GSBinding){1},&reply)==GS_OK);
 CHECK(gs_input_key(&in,SDL_SCANCODE_A,1,0,'a')==GS_OK);uint16_t word=0;
 CHECK(ops.queue(&in,GS_QUEUE_PEEK,&word)==GS_OK&&word==0x1e41);
 CHECK(ops.queue(&in,GS_QUEUE_TAKE,&word)==GS_OK&&word==0x1e41);
 CHECK(ops.queue(&in,GS_QUEUE_TAKE,&word)==GS_EMPTY);
 in.flush_reply=0xabcd;CHECK(ops.flush(&in,&word)==GS_OK&&word==0xabcd);
 CHECK(gs_input_key(&in,SDL_SCANCODE_BACKSPACE,1,0,0)==GS_OK);
 CHECK(ops.queue(&in,GS_QUEUE_TAKE,&word)==GS_OK&&word==0x0e08);
 CHECK(ops.vector(&in,GS_VECTOR_INSTALL,(GSBinding){2},&reply)==GS_OK);
 CHECK(gs_input_key(&in,SDL_SCANCODE_BACKSPACE,0,0,0)==GS_OK&&ops.scan(&in,&byte)==GS_EMPTY);
 in.scan_head=0;in.scan_tail=4095;CHECK(gs_input_key(&in,SDL_SCANCODE_UP,1,0,0)==GS_OVERFLOW&&in.scan_tail==4095);
 CHECK(ops.vector(&in,GS_VECTOR_RESTORE,(GSBinding){99},&reply)==GS_UNSUPPORTED);
 for(unsigned i=0;i<sizeof axis_records/sizeof *axis_records;i++)CHECK(gs_input_axis_count(axis_records[i].axis)==axis_records[i].count);
 for(int x=-32768;x<=32767;x++) {
  uint16_t count=gs_input_axis_count((int16_t)x);CHECK(count>=250&&count<=1750);
  if(x>-32768)CHECK(count>=gs_input_axis_count((int16_t)(x-1)));
 }
 CHECK(gs_input_gamepad(&in,0,1,-32768,32767,3)==GS_OK);CHECK(gs_input_gamepad(&in,1,1,0,16384,2)==GS_OK);
 CHECK(ops.presence(&in,&byte)==GS_OK&&byte==0x40);CHECK(ops.buttons(&in,0,&word)==GS_OK&&word==0x30);CHECK(ops.buttons(&in,1,&word)==GS_OK&&word==0x80);
 GSJoystickCounts counts;CHECK(ops.counts(&in,2000,15,&counts)==GS_OK);
 static const uint16_t expected[]={250,1750,1000,1375};
 for(unsigned i=0;i<4;i++)CHECK(counts.counts[i]==expected[i]&&counts.latched[i]==2000-expected[i]);
 CHECK(counts.remaining==250);
 CHECK(ops.counts(&in,0,15,&counts)==GS_OK&&counts.counts[0]==250&&counts.remaining==(uint16_t)(0-1750));
 CHECK(gs_input_gamepad(&in,1,0,0,0,0)==GS_OK);CHECK(ops.presence(&in,&byte)==GS_OK&&byte==0xcc);
 CHECK(ops.buttons(&in,1,&word)==GS_OK&&word==0);CHECK(ops.counts(&in,2000,3,&counts)==GS_OK&&counts.counts[2]==2000);
 GSSdlSeed seed={1,{0x10,0x20,0x30,0x40}};GSSeedReply value;CHECK(gs_seed_operations().read(&seed,&value)==GS_OK&&memcmp(&value,&seed.replay,sizeof value)==0);
 seed.fixed=0;CHECK(gs_seed_operations().read(&seed,&value)==GS_OK&&value.seconds<=60&&value.minutes<60&&value.hours<24);
 CHECK(ops.pump(&in,(GSInputPollCut)-1)==GS_UNSUPPORTED);
 GSStatus pumped=ops.pump(&in,GS_INPUT_SCAN);CHECK(pumped==GS_OK||pumped==GS_QUIT);
 gs_input_close(&in);return 0;
}
static int video_transactions(void) {
 static GSSdlVideo v;gs_video_init(&v);GSVideoOps ops=gs_video_operations();uint8_t byte;
 CHECK(ops.control_write(&v,GS_SEQ_INDEX,2)==GS_OK);CHECK(ops.control_write(&v,GS_SEQ_DATA,5)==GS_OK);
 CHECK(ops.store(&v,0xffff,0xa5)==GS_OK&&v.planes[0][65535]==0xa5&&v.planes[2][65535]==0xa5&&v.planes[1][65535]==0);
 CHECK(ops.store_word(&v,10,0x1234)==GS_OK&&v.planes[0][10]==0x34&&v.planes[2][11]==0x12);
 CHECK(ops.store_word(&v,65535,0x5678)==GS_UNSUPPORTED&&v.planes[0][65535]==0x78&&v.planes[0][0]==0);
 v.planes[0][123]=0x11;v.planes[1][123]=0x22;v.planes[2][123]=0x44;v.planes[3][123]=0x88;
 CHECK(ops.control_write(&v,GS_GC_INDEX,4)==GS_OK&&ops.control_write(&v,GS_GC_DATA,3)==GS_OK);
 CHECK(ops.read(&v,123,GS_COLLISION_READ,&byte)==GS_OK&&byte==0x88&&v.latches[0]==0x11);
 v.gc[5]=1;v.map_mask=15;CHECK(ops.copy(&v,123,124,&byte)==GS_OK&&byte==0x88);
 CHECK(ops.copy(&v,124,125,&byte)==GS_OK&&v.planes[0][125]==0x11&&v.planes[3][125]==0x88);
 v.gc[5]=0;v.gc[3]=0x10;v.gc[8]=0x40;v.planes[3][200]=0x81;
 CHECK(ops.water_mark(&v,200,&byte)==GS_OK&&byte==0x81&&v.planes[3][200]==0xc1);
 v.attribute_phase=1;v.retrace=1;CHECK(ops.retrace_level(&v,&byte)==GS_OK&&byte==8&&!v.attribute_phase);
 CHECK(ops.dac(&v,(GSDacWrite){GS_DAC_SELECT,255})==GS_OK);
 for(unsigned i=0;i<4;i++)CHECK(ops.dac(&v,(GSDacWrite){GS_DAC_COMPONENT,(uint8_t)(64+i)})==GS_OK);
 CHECK(v.dac_index==0&&v.dac_component==1&&v.dac[765]==0&&v.dac[767]==2&&v.dac[0]==3);
 CHECK(ops.compatibility(&v)==GS_UNSUPPORTED);
 CHECK(ops.present(&v)==GS_OK);
 CHECK(SDL_SetHint(SDL_HINT_RENDER_DRIVER,"software"));
 CHECK(gs_video_window(&v,1)==GS_OK&&ops.present(&v)==GS_OK);
 gs_video_close(&v);return 0;
}
static int files_test(const char *path) {
 remove(path);GSSdlFiles files;CHECK(gs_files_init(&files,path)==GS_OK);GSFilesOps ops=gs_files_operations();GSFileReply reply;
 CHECK(ops.open_scores(&files,0,&reply)==GS_OK&&reply.failed&&reply.value==2);
 CHECK(ops.open_scores(&files,1,&reply)==GS_OK&&!reply.failed);uint16_t handle=reply.value;
 uint8_t bytes[107];for(unsigned i=0;i<107;i++)bytes[i]=(uint8_t)i;
 CHECK(ops.write(&files,handle,bytes,107,&reply)==GS_OK&&!reply.failed&&reply.value==107);
 CHECK(ops.persist(&files)==GS_OK&&files.handles[handle].open&&handle==5);
 GSSdlFiles loaded;CHECK(gs_files_init(&loaded,path)==GS_OK&&loaded.length==107&&!memcmp(loaded.data,bytes,107));
 CHECK(ops.open_scores(&files,0,&reply)==GS_OK&&!reply.failed);uint16_t read=reply.value;memset(bytes,0xcc,sizeof bytes);
 CHECK(ops.write(&files,read,bytes,0,&reply)==GS_OK&&reply.failed&&reply.value==5);
 CHECK(ops.read(&files,read,bytes,106,&reply)==GS_OK&&reply.value==106&&bytes[106]==0xcc);
 CHECK(ops.open_scores(&files,1,&reply)==GS_OK&&!reply.failed); /* truncate under the old read handle */
 CHECK(ops.read(&files,read,bytes,107,&reply)==GS_OK&&reply.value==0);
 CHECK(ops.close(&files,read,&reply)==GS_OK&&!reply.failed);CHECK(ops.close(&files,read,&reply)==GS_OK&&reply.failed);
 for(unsigned n=0;n<32;n++)CHECK(ops.open_scores(&files,1,&reply)==GS_OK);
 CHECK(reply.failed&&reply.value==4);unsigned open=0;
 for(unsigned i=5;i<32;i++)open+=files.handles[i].open;
 CHECK(open==27);
 remove(path);return 0;
}
static int audio_test(const char *path) {
 FILE *file=fopen(path,"rb");CHECK(file);GSSdlAudio audio;CHECK(gs_audio_init(&audio,0)==GS_OK);GSAudioOps ops=gs_audio_operations();unsigned event=0,nonzero=0;
 for(unsigned frame=0;frame<OPL_GOLDEN_FRAMES;frame++) {
  while(event<sizeof opl_sequence/sizeof *opl_sequence&&opl_sequence[event].frame==frame){CHECK(ops.opl(&audio,(GSRegisterWrite){opl_sequence[event].reg,opl_sequence[event].value})==GS_OK);event++;}
  int16_t actual[2],expected[2];CHECK(gs_audio_generate(&audio,actual,1)==GS_OK);CHECK(fread(expected,4,1,file)==1&&!memcmp(actual,expected,4));nonzero+=actual[0]!=0||actual[1]!=0;
 }CHECK(nonzero>100&&fgetc(file)==EOF);fclose(file);
 CHECK(audio.registers==sizeof opl_sequence/sizeof *opl_sequence);CHECK(audio.frames==4800);
 CHECK(ops.clock(&audio,GS_CLOCK_TIMER)==GS_UNSUPPORTED);unsigned delivered=0;audio.clock_sink=clock_sink;audio.clock_context=&delivered;
 CHECK(ops.clock(&audio,GS_CLOCK_TIMER)==GS_OK&&ops.clock(&audio,GS_CLOCK_BIOS_CHAIN)==GS_OK&&delivered==5);
 CHECK(ops.advance(&audio,1000000000)==GS_OK&&audio.frames==52800);gs_audio_close(&audio);
 CHECK(gs_audio_init(&audio,1)==GS_OK);CHECK(ops.advance(&audio,1000000)==GS_OK);gs_audio_close(&audio);return 0;
}
static int pack_test(const char *path,int expected_failure) {
 GSResourcePack pack;char error[256];GSStatus result=gs_resources_open(&pack,path,port_required_resources,PORT_REQUIRED_COUNT,error,sizeof error);
 if(expected_failure){CHECK(result!=GS_OK&&!pack.storage&&strstr(error,"resource pack:"));printf("REJECTED %s\n",error);return 0;}
 CHECK(result==GS_OK);GSResourceOps ops=gs_resources_operations();GSBytes view;GSResourceClass kind;GSMutableBytes mutable;
 CHECK(ops.view(&pack,UINT64_C(0x200000000),&view,&kind)==GS_OK&&view.size==60&&kind==GS_IMMUTABLE);
 CHECK(ops.mutable_view(&pack,UINT64_C(0x200000000),&mutable)==GS_UNSUPPORTED);
 CHECK(ops.mutable_view(&pack,UINT64_C(0x1000000d6),&mutable)==GS_OK&&mutable.size==4);uint8_t before=mutable.data[2];mutable.data[2]^=0xff;
 unsigned changed=255u-before;
 CHECK(ops.view(&pack,UINT64_C(0x1000000d6),&view,&kind)==GS_OK&&(unsigned)view.data[2]==changed);
 unsigned aliases=0;
 for(size_t i=0;i<PORT_REQUIRED_COUNT;i++)if((port_required_resources[i].id>>32)==4){
  CHECK(ops.view(&pack,port_required_resources[i].id,&view,&kind)==GS_OK);
  if(view.data==mutable.data&&view.size>=4){CHECK((unsigned)view.data[2]==changed);aliases++;}
 }
 CHECK(aliases>0);
 CHECK(ops.view(&pack,UINT64_C(0x200000001),&view,&kind)==GS_OK&&view.size==5);
 CHECK(ops.view(&pack,UINT64_MAX,&view,&kind)==GS_UNSUPPORTED);gs_resources_close(&pack);return 0;
}
int main(int argc,char **argv) {
 if(argc<2)return 2;
 CHECK(SDL_Init(SDL_INIT_AUDIO|SDL_INIT_EVENTS|SDL_INIT_VIDEO|SDL_INIT_GAMEPAD));
 if(!strcmp(argv[1],"unit")){CHECK(argc==3);CHECK(time_input()==0);CHECK(video_transactions()==0);CHECK(files_test(argv[2])==0);puts("PASS unit");return 0;}
 if(!strcmp(argv[1],"audio")){CHECK(argc==3);CHECK(audio_test(argv[2])==0);puts("PASS audio");return 0;}
 if(!strcmp(argv[1],"pack")){CHECK(argc==3);return pack_test(argv[2],0);}
 if(!strcmp(argv[1],"reject")){CHECK(argc==3);return pack_test(argv[2],1);}
 return 2;
}
