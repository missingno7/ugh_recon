/* This executable links only the deterministic backend and the C runtime. */
#include "test/backend.h"
#include <stdio.h>
static GSTestBackend backend;
int main(void){
    gs_test_init(&backend);GameServices s=gs_test_services(&backend);uint8_t value;
    if(s.video.store(&backend,60000,0x95)!=GS_OK||s.video.read(&backend,60000,GS_COLLISION_READ,&value)!=GS_OK||value!=0x95)return 1;
    GSTestRun scans[]={{0xe0,1},{0xcb,1}};gs_test_stream(&backend.scans,scans,2,1);
    if(s.input.scan(&backend,&value)!=GS_OK||value!=0xe0)return 2;
    if(s.input.scan(&backend,&value)!=GS_OK||value!=0xcb)return 3;
    GSSeedReply seed;if(s.seed.read(&backend,&seed)!=GS_OK||seed.seconds!=48)return 4;
    GSEvent event;for(unsigned i=0;i<70;i++)if(s.time.deliver(&backend,GS_TIMER_OPPORTUNITY,&event)!=GS_OK)return 5;
    if(event.nanoseconds!=1000000000ull)return 6;
    GSFileReply file;if(s.files.open_scores(&backend,1,&file)!=GS_OK||file.failed)return 7;
    uint8_t bytes[]={1,2,3};if(s.files.write(&backend,file.value,bytes,3,&file)!=GS_OK||file.value!=3)return 8;
    if(s.lifecycle.terminate(&backend,42)!=GS_OK||backend.exit_code!=42)return 9;
    puts("PASS standalone backend: only C runtime, no assets or game objects");return 0;
}
