/* Production objects, explicit API inputs and pack data. No machine fixture. */
#include "native/compose_audio.h"
#include "port/test/backend.h"
#include "port/resources.h"
#include "port/hash.h"
#include "resource_manifest.h"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#undef assert
#define assert(c) do{if(!(c)){fprintf(stderr,"check failed at line %u: %s\n",__LINE__,#c);exit(3);}}while(0)
static uint8_t ordered[2000000];static unsigned used;
static void record(void *context,GSTestEffect e){(void)context;if(e.kind==GST_OPL){assert(used<sizeof ordered);ordered[used++]=(uint8_t)e.b;}}
static void word(FILE *f,uint32_t v){for(unsigned i=0;i<4;i++)fputc((uint8_t)(v>>(8*i)),f);}
static void clock_record(FILE *f,GameWorld *w,unsigned slot){
    AudioState *a=&w->audio;word(f,a->ticks);word(f,a->time_origin);word(f,a->ticks_per_unit);word(f,a->playing);word(f,a->section_loop_enabled);
    word(f,a->channels[slot].deadline);word(f,a->channels[slot].cursor.index);word(f,a->channels[slot].control);
    word(f,a->timer_period);word(f,a->channels[slot].step_q8);word(f,a->current_channel);word(f,a->reserved_voices);
}
int main(int argc,char **argv){
    _set_error_mode(_OUT_TO_STDERR);
    if(argc!=3)return 2;GSResourcePack pack;char error[256],path[4096];
    if(gs_resources_open(&pack,argv[1],port_required_resources,PORT_REQUIRED_COUNT,error,sizeof error)!=GS_OK)return 2;
    GameWorld *w=calloc(1,sizeof *w);GSTestBackend *b=calloc(1,sizeof *b);assert(w&&b);unsigned row=0;
    for(unsigned effects=0;effects<2;effects++)for(unsigned resource=0;resource<11;resource++)for(unsigned config=0;config<(effects?6u:7u);config++,row++){
        gs_test_init(b);b->resources=gs_resources_operations();b->resource_context=&pack;b->recorder=record;
        GameServices s=gs_test_services(b);assert(game_world_construct(w,&s)==GS_OK);used=0;
        unsigned channels=w->audio_data[resource].data[18];
        const unsigned main_configs[7][4]={{0,12,1,1},{2,12,1,1},{9,12,1,1},{16,13,0,1},{257,12,1,1},{10,12,1,1},{2,13,0,2}};
        const unsigned effect_configs[6][3]={{8,0,1},{9,1,1},{10,1,2},{11,0,1},{8,1,1},{11,1,0}};
        unsigned reserved=effects?channels:main_configs[config][0],slot=effects?effect_configs[config][0]:main_configs[config][1];
        unsigned playing=effects?effect_configs[config][1]:main_configs[config][2],repeat=effects?effect_configs[config][2]:main_configs[config][3];
        for(unsigned i=0;i<9;i++){
            uint8_t data[20];for(unsigned j=0;j<20;j++)data[j]=(uint8_t)(i*31+j*17+3);
            for(unsigned which=0;which<2;which++){
                uint8_t p[20];for(unsigned j=0;j<20;j++)p[j]=data[which?19-j:j];AudioVoice *v=which?&w->audio.displaced[i]:&w->audio.live[i];
                memcpy(v->instrument,p,12);v->volume=(uint16_t)(p[12]|p[13]<<8);v->gain=(uint16_t)(p[14]|p[15]<<8);v->owner=(uint16_t)(p[16]|p[17]<<8);v->frequency=(uint16_t)(p[18]|p[19]<<8);
            }
        }
        w->audio.current_channel=(uint16_t)slot;w->audio.reserved_voices=(uint16_t)reserved;w->audio.playing=(uint16_t)playing;w->audio.ticks=0xfffffffc;
        AudioChannel *main=&w->audio.channels[12];main->control=1;main->repeats=(uint16_t)repeat;main->start=main->cursor=(AudioCursor){w->audio_data[resource].data,42};main->deadline=0xfffffffc;
        w->audio.playback_timer_handle=2;w->audio.fade.timer_handle=2;w->timer.count=3;w->timer.earliest=65536;
        for(unsigned i=0;i<16;i++){w->timer.by_handle[i]=(uint16_t)(i<=2?2*i:TIMER_FREE);w->timer.slots[i].interval=0x2000+2*i;w->timer.slots[i].handle=(uint16_t)(2*i);}
        unsigned selected=12;
        if(effects){selected=slot;w->audio_reset.devices=1;main->voice_count=9;
            w->audio.timer_period=(uint16_t)(slot==11?0x7fff:slot==8&&playing?100:playing?0x1843:0);
            AudioChannel *t=&w->audio.channels[slot];t->repeats=(uint16_t)repeat;t->start=t->cursor=main->start;t->volume=200;t->deadline=0xfffffffc;t->voice_count=(uint16_t)channels;t->first_voice=(uint16_t)(9-reserved);t->step_q8=256;t->control=(uint16_t)(repeat?5:7);
        }
        snprintf(path,sizeof path,"%s/clock-%u.bin",argv[2],row);FILE *f=fopen(path,"wb");assert(f);unsigned passes=0,burst;
        for(burst=1;burst<=20000;burst++){
            GSStatus status=game_audio_events(w,&s,selected);if(status!=GS_OK){fprintf(stderr,"resource=%u effects=%u config=%u burst=%u status=%u\n",resource,effects,config,burst,status);return 3;}
            clock_record(f,w,selected);if(effects&&w->audio.channels[selected].cursor.index==42)passes++;
            if(!(w->audio.channels[selected].control&1u)||(effects&&!repeat&&passes==2))break;
        }fclose(f);assert(burst<=20000);
        uint8_t hash[32];gs_sha256(ordered,used,hash);printf("{\"row\":%u,\"resource\":%u,\"effects\":%u,\"reserved\":%u,\"slot\":%u,\"playing\":%u,\"repeat\":%u,\"bursts\":%u,\"writes\":%u,\"opl\":\"",row,resource,effects,reserved,slot,playing,repeat,burst,used/2);
        for(unsigned i=0;i<32;i++)printf("%02x",hash[i]);puts("\"}");
    }free(w);free(b);gs_resources_close(&pack);return 0;
}
