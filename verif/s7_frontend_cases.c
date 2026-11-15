/* Composition checks for prefixes and live borrowers absent from frame corpus. */
#include "native/compose_front_end.h"
#include "native/game_defaults.h"
#include "native/game_startup.h"
#include "port/test/backend.h"
#include "port/resources.h"
#include "resource_manifest.h"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static GameWorld *w;static GSTestBackend *b;static GameServices s;static GSResourcePack pack;
static void reset(void) {
    gs_test_init(b);b->resources=gs_resources_operations();b->resource_context=&pack;s=gs_test_services(b);
    assert(game_world_construct(w,&s)==GS_OK);w->keyboard_saved=(GSBinding){1};
    w->pages=(VideoPages){.height=192,.plane_copy_bytes=0x4800,.draw=0x5a08,.displayed=0xa88,.background=0xa988};
    w->run.configuration.players=1;w->run.configuration.player_bytes=2;w->run.water_y=200;
    w->input.loop_limit=3;GSTestRun retraces[]={{0,1},{8,1}},absent[]={{255,10000}};
    assert(gs_test_stream(&b->retrace_samples,retraces,2,UINT32_MAX)==GS_OK);assert(gs_test_stream(&b->joystick,absent,1,UINT32_MAX)==GS_OK);
}
static GSStatus broken_write(void *context,uint16_t handle,const uint8_t *data,uint16_t count,GSFileReply *reply){(void)context;(void)handle;(void)data;(void)count;(void)reply;return GS_IO_ERROR;}
static unsigned file_actions[8],file_count,queue_actions[128],queue_count;
static void observe(void *context,GSTestEffect e){(void)context;if(e.kind==GST_FILE){assert(file_count<8);file_actions[file_count++]=e.a;}if(e.kind==GST_QUEUE){assert(queue_count<128);queue_actions[queue_count++]=e.a;}}
static void files(void) {
    uint8_t original[107];reset();memcpy(original,w->front.score_rows,107);
    b->recorder=observe;file_count=0;assert(game_front_scores_file(w,&s,0)==GS_OK);assert(file_count==1&&file_actions[0]==0x3d);assert(!memcmp(original,w->front.score_rows,107));
    for(unsigned failed=0;failed<3;failed++){
        reset();memcpy(original,w->front.score_rows,107);b->exists=1;b->length=3;b->scores[0]=0xaa;b->scores[1]=0xbb;b->scores[2]=0xcc;b->file_error=5;b->file_error_skip=failed;b->recorder=observe;file_count=0;
        assert(game_front_scores_file(w,&s,0)==GS_OK);assert(file_count==failed+1);
        assert(file_actions[0]==0x3d);if(failed)assert(file_actions[1]==0x3f);if(failed==2)assert(file_actions[2]==0x3e);
        if(failed<2)assert(!memcmp(original,w->front.score_rows,107));else{assert(!memcmp(w->front.score_rows,b->scores,3));assert(!memcmp(w->front.score_rows+3,original+3,104));}
    }
    reset();memcpy(original,w->front.score_rows,107);b->exists=1;b->length=3;b->scores[0]=0xaa;b->scores[1]=0xbb;b->scores[2]=0xcc;
    assert(game_front_scores_file(w,&s,0)==GS_OK);for(unsigned i=0;i<107;i++)assert(w->front.score_rows[i]==(uint8_t)((i<3?b->scores[i]:original[i])^255));assert(!b->handles[5].active);
    for(unsigned failed=0;failed<2;failed++) {
        reset();memcpy(original,w->front.score_rows,107);b->file_error=5;b->file_error_skip=failed;b->recorder=observe;file_count=0;
        assert(game_front_scores_file(w,&s,1)==GS_OK);assert(file_count==failed+1);assert(!memcmp(original,w->front.score_rows,107));assert(b->handles[5].active==failed);
    }
    reset();memcpy(original,w->front.score_rows,107);b->io_limit=7;assert(game_front_scores_file(w,&s,1)==GS_OK);assert(b->length==7&&b->handles[5].active);for(unsigned i=0;i<7;i++)assert(b->scores[i]==255u-(unsigned)original[i]);assert(!memcmp(original,w->front.score_rows,107));
    reset();memcpy(original,w->front.score_rows,107);s.files.write=broken_write;assert(game_front_scores_file(w,&s,1)==GS_IO_ERROR);for(unsigned i=0;i<107;i++)assert(w->front.score_rows[i]==255u-(unsigned)original[i]);assert(b->handles[5].active);
}
static void keys(const GSTestRun *input,unsigned count){assert(gs_test_stream(&b->bios,input,count,1)==GS_OK);}
static void editors(void) {
    reset();memcpy(w->front.name_entry,"ABCDEFGHIJKL",12);GSTestRun input[]={{'z',1},{13,1}};keys(input,2);b->recorder=observe;queue_count=0;
    assert(game_front_name(w,&s)==GS_OK);assert(!memcmp(w->front.name_entry,"Z CDEFGHIJKL",12));assert(queue_count==4&&queue_actions[0]==GS_QUEUE_PEEK&&queue_actions[1]==GS_QUEUE_TAKE);
    reset();memcpy(w->front.name_entry,"ABCDEFGHIJKL",12);GSTestRun enter[]={{13,1}};keys(enter,1);assert(game_front_name(w,&s)==GS_OK);assert(!memcmp(w->front.name_entry,"INCOGNITUSKL",12));
    reset();GSTestRun password[]={{8,1},{'!',1},{'a',20},{'b',1},{8,1},{'9',1},{13,1}};keys(password,7);assert(game_front_password(w,&s)==GS_OK);for(unsigned i=0;i<19;i++)assert(w->front.password[i]=='A');assert(w->front.password[19]=='9'&&!w->front.password[20]);assert(b->keyboard.token==2);
    reset();keys(enter,1);assert(game_front_password(w,&s)==GS_OK);assert(!memcmp(w->front.password,"NONE",4));for(unsigned i=4;i<20;i++)assert(w->front.password[i]==' ');
}
static void insertion(void) {
    reset();for(unsigned row=0;row<5;row++){memset(w->front.score_rows+21*row+14,'9',6);}memcpy(w->front.score_rows+21*4+14,"     1",6);w->front.score_rows[21*3+12]='X';w->front.score_rows[21*3+13]='Y';w->run.score=1;
    GSTestRun enter[]={{13,1}};keys(enter,1);assert(game_front_scores_insert(w,&s).status==GS_OK);assert(!w->run.score);assert(!memcmp(w->front.score_rows+21*4,"INCOGNITUS",10));assert(w->front.score_rows[21*4+12]=='X'&&w->front.score_rows[21*4+13]=='Y');assert(!memcmp(w->front.score_rows+21*4+14,"     1",6));assert(b->handles[5].active&&b->length==107);
    for(unsigned i=0;i<107;i++)assert(b->scores[i]==255u-(unsigned)w->front.score_rows[i]);
    reset();w->audio_reset.devices=1;w->run.score=999999;assert(game_front_scores_insert(w,&s).status==GS_UNSUPPORTED);assert(!w->frames&&w->run.score==999999&&!b->exists);
    reset();w->run.score=0;uint8_t original[107];memcpy(original,w->front.score_rows,107);assert(game_front_scores_insert(w,&s).status==GS_OK);assert(!memcmp(original,w->front.score_rows,107)&&!b->exists);
}
static GSStatus (*original_store)(void *,uint16_t,uint16_t);
static unsigned clear_seen;
static GSStatus live_clear(void *context,uint16_t address,uint16_t value){if(!clear_seen++){w->run.water_y=177;}return original_store(context,address,value);}
static GSStatus live_input(void *context,GSInputPollCut cut){(void)context;(void)cut;w->run.water_y=77;return GS_OK;}
static void pages(void) {
    reset();assert(game_picture_mode(w,&s)==GS_OK);
    for(unsigned i=0;i<4;i++){GameFrontResult result=game_front_picture(w,&s,(PictureKind)i,1);assert(result.status==GS_OK&&result.selection==0);}
    assert(w->frames==5);

    reset();w->run.water_y=123;original_store=s.video.store_word;s.video.store_word=live_clear;s.input.pump=live_input;clear_seen=0;
    GSTestRun scans[]={{0,1},{1,1}};assert(gs_test_stream(&b->scans,scans,2,1)==GS_OK);
    static const uint8_t intro[]={254,'T','E','S','T',0},password[]={'A',0};
    assert(game_front_introduction(w,&s,(GSBytes){intro,sizeof intro},(GSBytes){password,sizeof password})==GS_OK);assert(w->run.water_y==177);assert(w->frames==1);
    reset();GSTestRun escape[]={{0,1},{1,1}};assert(gs_test_stream(&b->scans,escape,2,1)==GS_OK);GameFrontResult result=game_front_credits(w,&s);assert(result.status==GS_OK&&result.selection==1&&w->frames==2);
    reset();result=game_front_credits(w,&s);assert(result.status==GS_OK&&result.selection==0&&w->frames>2);assert(!memcmp(w->palette.base,w->front_data.source_palette,384));assert(!memcmp(w->palette.base+384,w->front_data.source_palette,384));
}
int main(int argc,char **argv){
    if(argc!=2)return 2;char error[256];assert(gs_resources_open(&pack,argv[1],port_required_resources,PORT_REQUIRED_COUNT,error,sizeof error)==GS_OK);
    w=calloc(1,sizeof *w);b=calloc(1,sizeof *b);assert(w&&b);files();editors();insertion();pages();free(w);free(b);gs_resources_close(&pack);puts("PASS front-end prefixes, short tails, XOR, tie/row4 shift, name tails, BIOS handoffs, credits and live intro water");return 0;
}

