#include <string.h>
#include <stdio.h>
#include "ugh.h"
#include "actor_projection.h"
#include "demo_core.h"
int l1_AdvanceDemoScripts(Regs *r);
int l1_TestAllDemoScriptsFinished(Regs *r);
int demo_actual_gameplay_draw(Regs *r);
static uint8_t saved[UGH_MEM_SIZE],reference[UGH_MEM_SIZE];
static Regs demo_regs(void) {
    Regs r={0};r.ds=DATA_SEG;r.cs=GAME_SEG;r.ss=0x9000;r.sp=0x1000;r.flags=0x202;
    r.ax=0x1357;r.cx=0x2468;r.di=0x3579;r.es=0x7500;return r;
}
EXPORT int demo_compare_step(void) {
    memcpy(saved,ugh_mem,sizeof saved);Regs a=demo_regs(),b=a;
    int ra=l1_AdvanceDemoScripts(&a);memcpy(reference,ugh_mem,sizeof reference);
    memcpy(ugh_mem,saved,sizeof saved);int rb=c_AdvanceDemoScripts(&b);
    if(ra!=rb || memcmp(&a,&b,sizeof a) || memcmp(reference,ugh_mem,sizeof reference)) {
        fprintf(stderr,"step mismatch AX %04x/%04x CX %04x/%04x flags %04x/%04x status %d/%d\n",a.ax,b.ax,a.cx,b.cx,a.flags,b.flags,ra,rb);
        for(size_t i=0;i<sizeof saved;i++) if(reference[i]!=ugh_mem[i]) {fprintf(stderr,"RAM %zx %02x/%02x\n",i,reference[i],ugh_mem[i]);break;}
        return 0;
    }
    return 1;
}
EXPORT int demo_enumerate_scripts(void) {
    DemoResourceStorage resources;if(!actor_bridge_scripts(DATA_SEG,&resources)) return -1;
    memcpy(saved,ugh_mem,sizeof saved);
    unsigned steps=0;
    for(size_t script=0;script<resources.count;script++) {
        uint16_t base=resources.headers[script];
        wr16(DATA_SEG,D(ActorUpdateOrScriptCursor),(uint16_t)(base+8));
        wr16(DATA_SEG,(uint16_t)(D(ActorUpdateOrScriptCursor)+2),65535u);
        wr16(DATA_SEG,D(ActorAnimationCountdowns),1);
        wr16(DATA_SEG,D(ActorVerticalOrDemoPeriod),resources.scripts[script].period);
        wr16(DATA_SEG,D(ActorOverlayOrScriptCallbacks),rd16(DATA_SEG,(uint16_t)(base+6)));
        wr16(DATA_SEG,D(ActorMotionWaitOrDemoRepeats),0);
        wr16(DATA_SEG,D(ActorPhaseOrDemoLoopCursor),0xdead);
        wr16(DATA_SEG,D(ActorPlatformOrScriptDone),0);
        wr16(DATA_SEG,D(ActorX32),demo_pixel_position(resources.scripts[script].initial_pixel_x));
        wr16(DATA_SEG,D(ActorY32),demo_pixel_position(resources.scripts[script].initial_pixel_y));
        wr16(DATA_SEG,D(ActorSpriteIds),65535u);
        unsigned ticks=0;
        while(!rd16(DATA_SEG,D(ActorPlatformOrScriptDone))) {
            if(++ticks>200000 || !demo_compare_step()) return -2;
            steps++;
        }
        /* Stopped slots remain active and repeatedly reload their cadence. */
        for(unsigned n=0;n<5;n++) {if(!demo_compare_step()) return -3;steps++;}
        printf("script %04x code=%zu period=%u effect=%d ticks=%u\n",base,resources.scripts[script].code_size,resources.scripts[script].period,resources.scripts[script].effect,ticks);
    }
    return (int)steps;
}
EXPORT int demo_alias_checks(void) {
    static const unsigned expected[ACTOR_PHASE_COUNT]={0,8,0,1,2,2,0,4,0,0,0,0,0,4,16,0,0,32,2,2,0};
    unsigned checks=0;
    wr16(DATA_SEG,D(PlayerCount),2);
    for(unsigned phase=0;phase<ACTOR_PHASE_COUNT;phase++) {
        PassengerStoneSlot slot={0};
        wr16(DATA_SEG,D(ActorPhaseOrDemoLoopCursor),2);wr16(DATA_SEG,D(ActorMotionWaitOrDemoRepeats),0x89ab);
        if(actor_phase_aliases((ActorPhase)phase)!=expected[phase] || !actor_bridge_alias_project(DATA_SEG,0,(ActorPhase)phase,&slot)) return -1;
        for(unsigned bit=1;bit<=32;bit*=2) {
            uint16_t value=0x1234;int ok=actor_bridge_alias_read(&slot,(ActorAlias)bit,&value);
            if(ok!=!!(expected[phase]&bit)) return -2;
            if(ok && value!=(bit==4 ? 1 : bit<4 ? 2 : 0x89ab)) return -3;
            if(!ok && value!=0x1234) return -4;
            checks++;
        }
    }
    PassengerStoneSlot slot={0};wr16(DATA_SEG,D(ActorPhaseOrDemoLoopCursor),3);
    if(actor_bridge_alias_project(DATA_SEG,0,ACTOR_CARRIED_STONE,&slot)) return -5;
    return (int)checks;
}
EXPORT int demo_resource_checks(uint16_t record,unsigned expected_count) {
    ActorResourceStorage resources;ActorLevelStorage storage;LevelDescription level={0};
    level.actor_count=expected_count;
    if(!actor_bridge_resources(DATA_SEG,&resources) || !actor_bridge_level(DATA_SEG,record,&level,&resources,&storage)) return -1;
    for(unsigned i=0;i<8;i++) {
        const ActorType *type=&resources.types[i];uint16_t base=(uint16_t)(D(Data_7720)+74*i);
        if((unsigned)type->id!=i || type->geometry.anchor_x!=rd16(DATA_SEG,base) || type->geometry.anchor_y!=rd16(DATA_SEG,(uint16_t)(base+2)) ||
            type->geometry.extent_x!=rd16(DATA_SEG,(uint16_t)(base+4)) || type->geometry.extent_y!=rd16(DATA_SEG,(uint16_t)(base+6))) return -2;
        const uint16_t scalars[]={type->animation_period,type->initial_fare,type->minimum_fare,type->floating_lifetime,type->carried_kind};
        for(unsigned j=0;j<5;j++) if(scalars[j]!=rd16(DATA_SEG,(uint16_t)(base+62+2*j))) return -3;
        uint16_t pair=rd16(DATA_SEG,(uint16_t)(base+72));
        if(type->paired_type!=actor_bridge_type(&resources,pair)) return -4;
        for(unsigned j=0;j<6;j++) {
            uint16_t p=rd16(DATA_SEG,(uint16_t)(base+46+2*j));const ActorAnimation *a=&type->animations[j];
            for(size_t k=0;k<a->count;k++) if(a->sprites[k]!=rd16(DATA_SEG,(uint16_t)(p+2*k)) || a->sprites[k]==65535u) return -5;
            if(p && rd16(DATA_SEG,(uint16_t)(p+2*a->count))!=65535u) return -6;
        }
    }
    uint16_t p=rd16(DATA_SEG,(uint16_t)(record+4));
    for(unsigned i=0;i<expected_count;i++,p=(uint16_t)(p+6)) {
        const ActorLevelEntry *e=&storage.entries[i];
        if(e->type!=actor_bridge_type(&resources,rd16(DATA_SEG,p)) || e->initial_platform!=rd16(DATA_SEG,(uint16_t)(p+2))) return -7;
        if(e->type->id>=ACTOR_STONE) {if(e->journey.count) return -8;continue;}
        uint16_t base=rd16(DATA_SEG,(uint16_t)(p+4));
        for(size_t k=0;k<e->journey.count;k++) if(e->journey.legs[k].platform!=rd16(DATA_SEG,(uint16_t)(base+4*k)) || e->journey.legs[k].wait!=rd16(DATA_SEG,(uint16_t)(base+4*k+2))) return -9;
        if(rd16(DATA_SEG,(uint16_t)(base+4*e->journey.count))!=65535u) return -10;
    }
    return (int)expected_count;
}
EXPORT int demo_word_cases(void) {
    /* Complete scalar slices on actual compiled L1/native code, independent
     * of the shipped-resource bridge admission checks. */
    static const uint8_t bytes[16]={0,128,5,0,128,127,0,0,7,0,255,128,0,128,0,0};
    unsigned checks=0;
    for(unsigned mode=0;mode<3;mode++) for(unsigned value=0;value<65536;value++) {
        DemoMotionScript script={0,0,(uint16_t)(mode==1?value:0),DEMO_EFFECT_NONE,bytes,16};
        DemoMotionSlot slot={&script,mode==2?0:2,8,(uint16_t)(mode==2?value:0),(uint16_t)(mode==0?value:1),0,{(uint16_t)value,(uint16_t)~value},65535u};
        for(unsigned i=0;i<16;i++) wr8(DATA_SEG,(uint16_t)(0x4000+i),bytes[i]);
        wr16(DATA_SEG,D(ActorUpdateOrScriptCursor),(uint16_t)(0x4000+slot.cursor));
        wr16(DATA_SEG,(uint16_t)(D(ActorUpdateOrScriptCursor)+2),65535u);
        wr16(DATA_SEG,D(ActorMotionWaitOrDemoRepeats),slot.repeat_count);
        wr16(DATA_SEG,D(ActorPhaseOrDemoLoopCursor),0x4008);
        wr16(DATA_SEG,D(ActorAnimationCountdowns),slot.countdown);
        wr16(DATA_SEG,D(ActorVerticalOrDemoPeriod),script.period);
        wr16(DATA_SEG,D(ActorX32),slot.position.x32);wr16(DATA_SEG,D(ActorY32),slot.position.y32);
        wr16(DATA_SEG,D(ActorSpriteIds),slot.sprite);wr16(DATA_SEG,D(ActorPlatformOrScriptDone),0);
        wr16(DATA_SEG,D(ActorOverlayOrScriptCallbacks),G(IgnoreActorState));
        Regs r=demo_regs();DemoStep effects;
        if(l1_AdvanceDemoScripts(&r) || !demo_advance_slot(&slot,&effects)) return -1;
        if(slot.cursor!=rd16(DATA_SEG,D(ActorUpdateOrScriptCursor))-0x4000u || slot.repeat_count!=rd16(DATA_SEG,D(ActorMotionWaitOrDemoRepeats)) ||
            slot.repeat_start!=rd16(DATA_SEG,D(ActorPhaseOrDemoLoopCursor))-0x4000u || slot.countdown!=rd16(DATA_SEG,D(ActorAnimationCountdowns)) ||
            slot.position.x32!=rd16(DATA_SEG,D(ActorX32)) || slot.position.y32!=rd16(DATA_SEG,D(ActorY32)) || slot.sprite!=rd16(DATA_SEG,D(ActorSpriteIds)) ||
            slot.finished!=(rd16(DATA_SEG,D(ActorPlatformOrScriptDone))!=0)) return -2;
        checks++;
    }
    for(unsigned value=0;value<65536;value++) if(demo_pixel_position((uint16_t)value)!=(uint16_t)(value<<5)) return -3;
    for(unsigned value=0;value<256;value++) {
        int16_t delta=(int8_t)value;
        if(demo_delta((uint8_t)value)!=(uint16_t)((uint16_t)delta<<2)) return -4;
    }
    return (int)(checks+65536+256);
}
EXPORT int demo_cross_mode(void) {
    Regs r=demo_regs();r.si=0x1792;
    if(c_InitializeDemoScripts(&r)) return -1;
    ActorRenderStorage history;actor_bridge_render_project(DATA_SEG,&history);
    ActorRenderHistory before=history.slots[2];
    if(before.pixel_x!=320 || before.pixel_y!=106 || before.previous_x!=320 || before.previous_y!=106) return -2;
    wr16(DATA_SEG,D(PlayerCount),1);wr16(DATA_SEG,D(CurrentLevelIndex),0);
    if(c_LoadCurrentLevelState(&r)) return -3;
    if(c_DispatchActorUpdates(&r) || c_ResetSpriteEraseState(&r)) return -4;
    actor_bridge_render_project(DATA_SEG,&history);
    if(history.slots[2].pixel_x!=before.pixel_x || history.slots[2].pixel_y!=before.pixel_y) return -5;
    r.bx=4;if(c_UpdateStonePickupWait(&r)) return -6;
    if(rd16(DATA_SEG,(uint16_t)(D(ActorSpriteIds)+4))!=0x220) return -7;
    if(demo_actual_gameplay_draw(&r)) return -8;
    actor_bridge_render_project(DATA_SEG,&history);
    if(history.slots[2].previous_x!=before.pixel_x || history.slots[2].previous_y!=before.pixel_y) return -9;
    if(history.slots[2].pixel_x==before.pixel_x && history.slots[2].pixel_y==before.pixel_y) return -10;
    return 1;
}
