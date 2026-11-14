#include "platform.h"
#include "../player_physics.h"
#include <stdlib.h>

typedef struct PhysicsPlan {
    PlayerPhysicsView player;
    PlayerPhysicsWorld world;
    PlayerPhysicsProcess process;
    LevelPlatform platforms[10];
    uint16_t index;
    int active;
} PhysicsPlan;
static void physics_require(int condition) {if(!condition)abort();}
static uint16_t physics_field(PhysicsPlan *p,PlayerPhysicsField field) {
    static const uint16_t bases[]={D(LevelTimer),D(PlayerImpactMagnitude),D(PlayerThrustAnimationRate),
        D(PlayerHorizontalVelocities),D(PlayerVerticalVelocities),D(PlayerX32),D(PlayerPixelX),
        D(PlayerPlatformIndices),D(PlayerY32),D(PlayerYPixels),D(ScreenFadeStep),D(ScreenFadeLevel)};
    return (uint16_t)(bases[field]+((field==PF_TIMER || field==PF_FADE_RATE || field==PF_FADE_LEVEL)?0:p->index));
}
static uint16_t physics_read(Regs *r,uint16_t base) {return rd16(r->ds,(uint16_t)(base+r->bx));}
static void physics_write(Regs *r,PhysicsPlan *p,uint16_t address,uint16_t expected) {
    uint16_t value=expected;
    if(p->active) {
        PlayerPhysicsEvent event=player_physics_poll(&p->process);
        physics_require(!p->process.failed && event.kind==PP_WRITE && physics_field(p,event.field)==address && event.value==expected);
        value=event.value;
    }
    wr16(r->ds,address,value);
}
static int physics_projection(Regs *r,PhysicsPlan *p) {
#ifdef ACTOR_VERIFY
    PlayerPhysicsView *v=&p->player;PlayerPhysicsWorld *w=&p->world;
    if(v->position.x32!=physics_read(r,D(PlayerX32)) || v->position.y32!=physics_read(r,D(PlayerY32)) ||
       v->pixel_x!=physics_read(r,D(PlayerPixelX)) || v->pixel_y!=physics_read(r,D(PlayerYPixels)) ||
       v->platform!=physics_read(r,D(PlayerPlatformIndices)) || v->velocity_x!=physics_read(r,D(PlayerHorizontalVelocities)) ||
       v->velocity_y!=physics_read(r,D(PlayerVerticalVelocities)) || v->impact!=physics_read(r,D(PlayerImpactMagnitude)) ||
       v->thrust!=physics_read(r,D(PlayerThrustAnimationRate)) || v->left!=physics_read(r,D(PlayerLeftInput)) ||
       v->right!=physics_read(r,D(PlayerRightInput)) || v->up!=physics_read(r,D(PlayerUpInput)) ||
       v->down!=physics_read(r,D(PlayerDownInput)) || w->timer!=rd16(r->ds,D(LevelTimer)) ||
       w->water_y!=rd16(r->ds,D(WaterYPixels)) || w->fade_rate!=rd16(r->ds,D(ScreenFadeStep)) ||
       w->fade_level!=rd16(r->ds,D(ScreenFadeLevel)))return 0;
#else
    (void)r;(void)p;
#endif
    return 1;
}
static void physics_out(Regs *r,PhysicsPlan *p,uint16_t port,unsigned width,uint16_t expected) {
    uint16_t value=expected;
    if(p->active) {
        PlayerPhysicsEvent event=player_physics_poll(&p->process);
        physics_require(!p->process.failed && width==1 && event.value==(uint8_t)expected &&
            ((event.kind==PP_SELECT_PLANE_REGISTER && port==0x3ce) || (event.kind==PP_READ_PLANE && port==0x3cf)));
        value=event.value;
    }
    platform_out(port,width,value);(void)r;
}
static int physics_sample(Regs *r,PhysicsPlan *p,uint16_t return_word) {
    if(p->active) {
        PlayerPhysicsEvent event=player_physics_poll(&p->process);PlayerCollisionProbe probe=event.probe;
        uint16_t x=(uint16_t)(probe.pixel_x+5u);
        uint16_t cell=player_physics_sar(x,2);
        uint16_t relative=(uint16_t)((int32_t)(int16_t)probe.pixel_y*(int16_t)rd16(r->ds,D(VgaRowStrideBytes))+cell);
        uint16_t origin=rd16(r->cs,G(BackgroundPagePointer));
        uint16_t segment=rd16(r->cs,(uint16_t)(G(BackgroundPagePointer)+2));
        uint16_t location=(uint16_t)(origin+relative+probe.columns+probe.rows*96u);
        physics_require(!p->process.failed && event.kind==PP_SAMPLE && r->es==segment && r->si==location && physics_projection(r,p));
    }
    int status=ugh_call_near(G(SamplePlayerCollisionPixels),return_word,r);
    if(p->active && !status)player_physics_reply(&p->process,(uint8_t)r->ax);
    return status;
}
static void physics_complete(Regs *r,PhysicsPlan *p) {
    if(!p->active)return;
    PlayerPhysicsEvent event=player_physics_poll(&p->process);
    physics_require(!p->process.failed && !p->process.awaiting_reply && event.kind==PP_DONE &&
        p->process.stage==PP_FINISHED && p->process.consumed==p->process.count && physics_projection(r,p));
}
static void physics_open(Regs *r,PhysicsPlan *p) {
    *p=(PhysicsPlan){0};
    if(r->ds!=DATA_SEG || r->cs!=GAME_SEG || (r->bx&1u) || r->bx>=4u)return;
    uint16_t difficulty=rd16(r->ds,D(SelectedDifficulty));
    if(difficulty>=3u)return; /* Corrupt lookup indices can alias live writes. */
    size_t count=0;
    for(;count<10;count++) {
        uint16_t index=(uint16_t)(2u*count);
        p->platforms[count]=(LevelPlatform){.left=rd16(r->ds,(uint16_t)(D(PlatformLeftEdges)+index)),
            .right=rd16(r->ds,(uint16_t)(D(PlatformRightEdges)+index)),.surface_y=rd16(r->ds,(uint16_t)(D(PlatformHeights)+index))};
        if((int16_t)p->platforms[count].left<0){count++;break;}
    }
    if(count==10 && (int16_t)p->platforms[9].left>=0)return;
    p->index=r->bx;
    p->player=(PlayerPhysicsView){.position={physics_read(r,D(PlayerX32)),physics_read(r,D(PlayerY32))},
        .pixel_x=physics_read(r,D(PlayerPixelX)),.pixel_y=physics_read(r,D(PlayerYPixels)),
        .platform=physics_read(r,D(PlayerPlatformIndices)),.velocity_x=physics_read(r,D(PlayerHorizontalVelocities)),
        .velocity_y=physics_read(r,D(PlayerVerticalVelocities)),.impact=physics_read(r,D(PlayerImpactMagnitude)),
        .thrust=physics_read(r,D(PlayerThrustAnimationRate)),.left=physics_read(r,D(PlayerLeftInput)),
        .right=physics_read(r,D(PlayerRightInput)),.up=physics_read(r,D(PlayerUpInput)),.down=physics_read(r,D(PlayerDownInput))};
    uint16_t limit_index=(uint16_t)(difficulty<<1);
    p->world=(PlayerPhysicsWorld){.timer=rd16(r->ds,D(LevelTimer)),.water_y=rd16(r->ds,D(WaterYPixels)),
        .impact_limit=rd16(r->ds,(uint16_t)(D(PlayerImpactLimits)+limit_index)),.fade_rate=rd16(r->ds,D(ScreenFadeStep)),
        .fade_level=rd16(r->ds,D(ScreenFadeLevel)),.rain=rd8(r->ds,D(LevelRainDirection)),.platforms=p->platforms,.platform_count=count};
    player_physics_begin(&p->process,&p->player,&p->world);p->active=1;
}

EXPORT int c_SamplePlayerCollisionPixels(Regs *r) {
    static const uint16_t delta[]={0,3,5,0x720,0x723,0x725,0x240,0x245,0x480,0x485};
    uint8_t samples[10];
    for(unsigned i=0;i<10;i++)samples[i]=rd8(r->es,(uint16_t)(r->si+delta[i]));
    set_al(r,(uint8_t)logic(r,player_collision_sample(samples),8));
    return UGH_OK;
}
/* BEGIN CHECKED PLAYER PHYSICS SHELL */
#define R(n) rd16(r->ds,D(n))
#define W(n,v) physics_write(r,plan,D(n),(uint16_t)(v))
#define RX(n,i) rd16(r->ds,(uint16_t)(D(n)+(i)))
#define WX(n,i,v) physics_write(r,plan,(uint16_t)(D(n)+(i)),(uint16_t)(v))
#define CALL(n,ret) do { int status=physics_sample(r,plan,ret); if(status) return status; } while(0)
static uint16_t sar(uint16_t v,unsigned n) {
    return (uint16_t)((v>>n)|((v&0x8000u) ? (0xffffu<<(16-n)) : 0));
}

static void push(Regs *r,uint16_t v) { r->sp=(uint16_t)(r->sp-2); wr16(r->ss,r->sp,v); }

static uint16_t pop(Regs *r) { uint16_t v=rd16(r->ss,r->sp); r->sp=(uint16_t)(r->sp+2); return v; }

static void collision_address(Regs *r) {
    r->ax=RX(PlayerYPixels,r->bx);
    int32_t product=(int32_t)(int16_t)r->ax*(int16_t)R(VgaRowStrideBytes);
    r->ax=(uint16_t)product; r->dx=(uint16_t)((uint32_t)product>>16);
    r->si=RX(PlayerPixelX,r->bx); r->si=(uint16_t)(r->si+5); r->si=sar(r->si,2);
    r->ax=(uint16_t)(r->ax+r->si);
    r->si=rd16(r->cs,G(BackgroundPagePointer));
    r->es=rd16(r->cs,(uint16_t)(G(BackgroundPagePointer)+2));
    r->si=(uint16_t)(r->si+r->ax);
}

static void select_collision_plane(Regs *r,PhysicsPlan *plan) {
    r->dx=0x3ce; set_al(r,4); physics_out(r,plan,r->dx,1,(uint8_t)r->ax);
    r->dx=(uint16_t)(r->dx+1);
    r->ax=(uint16_t)(RX(PlayerPixelX,r->bx)+0x25); r->ax=logic(r,r->ax&3,16);
}

static uint16_t limit_velocity(uint16_t v) {
    if((int16_t)v < -6144) return 0xe800;
    if((int16_t)v > 6144) return 0x1800;
    return v;
}

static void reflect_velocity(Regs *r,PhysicsPlan *plan,uint16_t offset) {
    r->ax=(uint16_t)(0-rd16(r->ds,offset)); r->ax=sar(r->ax,1);
    physics_write(r,plan,offset,r->ax); r->ax=(uint16_t)(r->ax<<1);
    if((int16_t)r->ax<0) r->ax=(uint16_t)(0-r->ax);
}

EXPORT int c_MovePlayerWithVgaCollisions(Regs *r) { PhysicsPlan storage;physics_open(r,&storage);PhysicsPlan *plan=&storage;
    W(LevelTimer,dec16(r,R(LevelTimer)));
    r->ax=logic(r,0,16); WX(PlayerImpactMagnitude,r->bx,0); WX(PlayerThrustAnimationRate,r->bx,0);
    r->cx=(uint16_t)(RX(PlayerYPixels,r->bx)-R(WaterYPixels)+18);
    if((int16_t)r->cx>0) r->cx=(uint16_t)((r->cx&255)|0x100);
    if((int16_t)RX(PlayerPlatformIndices,r->bx)<0) {
        if((int8_t)(r->cx>>8)<0) {
            set_al(r,rd8(r->ds,D(LevelRainDirection)));
            if((uint8_t)r->ax) {
                set_ah(r,0); r->ax=(uint16_t)((((r->ax-1)*2)-1)*32);
                WX(PlayerHorizontalVelocities,r->bx,RX(PlayerHorizontalVelocities,r->bx)+r->ax);
                r->ax=sar(r->ax,1); if((int16_t)r->ax<0) r->ax=(uint16_t)(0-r->ax);
                WX(PlayerVerticalVelocities,r->bx,RX(PlayerVerticalVelocities,r->bx)+r->ax);
            }
        }
        r->ax=RX(PlayerHorizontalVelocities,r->bx);
        if(RX(PlayerLeftInput,r->bx)) {
            r->ax=(uint16_t)(r->ax-63); WX(PlayerThrustAnimationRate,r->bx,RX(PlayerThrustAnimationRate,r->bx)+63);
        } else if(RX(PlayerRightInput,r->bx)) {
            r->ax=(uint16_t)(r->ax+63); WX(PlayerThrustAnimationRate,r->bx,RX(PlayerThrustAnimationRate,r->bx)+63);
        }
        r->ax=limit_velocity(r->ax); WX(PlayerHorizontalVelocities,r->bx,r->ax);
        r->ax=(uint16_t)(sar(r->ax,6)+RX(PlayerX32,r->bx));
        if((int16_t)r->ax<-512) { r->ax=0xfe00; WX(PlayerHorizontalVelocities,r->bx,0); }
        else if((int16_t)r->ax>9728) { r->ax=0x2600; WX(PlayerHorizontalVelocities,r->bx,0); }
        r->di=r->ax; push(r,r->cx);
        collision_address(r); select_collision_plane(r,plan);
        r->cx=(uint16_t)((r->cx&0xff00)|(uint8_t)r->ax); physics_out(r,plan,r->dx,1,(uint8_t)r->ax);
        r->bp=r->di; r->ax=sar(r->di,5);
        if(r->ax!=RX(PlayerPixelX,r->bx)) {
            r->bp=RX(PlayerX32,r->bx);
            int hit=0;
            if((int16_t)r->di<=(int16_t)r->bp) {
                uint8_t cl=(uint8_t)((uint8_t)r->cx-1);
                if((int8_t)cl<0) { cl&=3; r->si=(uint16_t)(r->si-1); }
                r->cx=(uint16_t)((r->cx&0xff00)|cl); set_al(r,cl); physics_out(r,plan,r->dx,1,cl);
                do {
                    CALL(SamplePlayerCollisionPixels,(uint16_t)(G(MovePlayerWithVgaCollisions)+0x12f));
                    if(r->flags&SF) { r->bp=(uint16_t)((r->bp&0xffe0)+32); hit=1; break; }
                    r->bp=(uint16_t)(r->bp-32);
                } while((int16_t)r->bp>(int16_t)r->di);
            } else {
                do {
                    uint8_t cl=(uint8_t)((uint8_t)r->cx+1);
                    if(cl>=4) { cl&=3; r->si=(uint16_t)(r->si+1); }
                    r->cx=(uint16_t)((r->cx&0xff00)|cl); set_al(r,cl); physics_out(r,plan,r->dx,1,cl);
                    CALL(SamplePlayerCollisionPixels,(uint16_t)(G(MovePlayerWithVgaCollisions)+0x159));
                    if(r->flags&SF) { r->bp&=0xffe0; hit=1; break; }
                    r->bp=(uint16_t)(r->bp+32);
                } while((int16_t)r->bp<(int16_t)r->di);
            }
            if(hit) {
                reflect_velocity(r,plan,(uint16_t)(D(PlayerHorizontalVelocities)+r->bx));
                WX(PlayerImpactMagnitude,r->bx,r->ax);
            } else r->bp=r->di;
        }
        WX(PlayerX32,r->bx,r->bp); r->bp=sar(r->bp,5); WX(PlayerPixelX,r->bx,r->bp);
        r->cx=pop(r);
    }
    r->ax=RX(PlayerVerticalVelocities,r->bx);
    int8_t water_state=(int8_t)(r->cx>>8);
    if(water_state>0) {
        W(LevelTimer,R(LevelTimer)-2);
        if((int16_t)r->ax>0) r->ax=(uint16_t)(r->ax-193);
        else { r->ax=(uint16_t)(r->ax-21); WX(PlayerPlatformIndices,r->bx,0xffff); }
    } else {
        if(water_state<0 && (int16_t)RX(PlayerPlatformIndices,r->bx)<0) {
            r->ax=(uint16_t)(r->ax+27); W(LevelTimer,R(LevelTimer)-2);
            if(RX(PlayerDownInput,r->bx)) {
                r->ax=(uint16_t)(r->ax+70); WX(PlayerThrustAnimationRate,r->bx,RX(PlayerThrustAnimationRate,r->bx)+90);
                goto vertical_limit;
            }
        }
        if(RX(PlayerUpInput,r->bx)) {
            W(LevelTimer,R(LevelTimer)-3); r->ax=(uint16_t)(r->ax-70);
            WX(PlayerThrustAnimationRate,r->bx,RX(PlayerThrustAnimationRate,r->bx)+90);
            WX(PlayerPlatformIndices,r->bx,0xffff);
        }
    }
vertical_limit:
    r->ax=limit_velocity(r->ax); WX(PlayerVerticalVelocities,r->bx,r->ax);
    r->ax=(uint16_t)(sar(r->ax,6)+RX(PlayerY32,r->bx));
    if((int16_t)r->ax<-608) { r->ax=0xfda0; WX(PlayerVerticalVelocities,r->bx,0); }
    else if((int16_t)r->ax>6112) { r->ax=0x17e0; WX(PlayerVerticalVelocities,r->bx,0); }
    if(water_state>0) {
        r->dx=(uint16_t)(sar(r->ax,5)-R(WaterYPixels)+18);
        if((int16_t)r->dx<=0) {
            WX(PlayerVerticalVelocities,r->bx,0); r->ax=(uint16_t)((R(WaterYPixels)<<5)-0x240);
        }
    }
    r->di=r->ax; select_collision_plane(r,plan); physics_out(r,plan,r->dx,1,(uint8_t)r->ax);
    collision_address(r); r->bp=r->di; r->ax=sar(r->di,5);
    if(r->ax!=RX(PlayerYPixels,r->bx)) {
        r->bp=RX(PlayerY32,r->bx); int hit=0;
        if((int16_t)r->di<=(int16_t)r->bp) {
            r->si=(uint16_t)(r->si-0x60);
            do {
                CALL(SamplePlayerCollisionPixels,(uint16_t)(G(MovePlayerWithVgaCollisions)+0x2d4));
                if(r->flags&SF) { r->bp=(uint16_t)((r->bp&0xffe0)+32); hit=1; break; }
                r->bp=(uint16_t)(r->bp-32);
            } while((int16_t)r->bp>(int16_t)r->di);
        } else {
            do {
                r->si=(uint16_t)(r->si+0x60);
                CALL(SamplePlayerCollisionPixels,(uint16_t)(G(MovePlayerWithVgaCollisions)+0x2f1));
                if(r->flags&SF) { r->bp&=0xffe0; hit=1; break; }
                r->bp=(uint16_t)(r->bp+32);
            } while((int16_t)r->bp<(int16_t)r->di);
        }
        if(hit) {
            reflect_velocity(r,plan,(uint16_t)(D(PlayerVerticalVelocities)+r->bx));
            if((int16_t)r->ax>(int16_t)RX(PlayerImpactMagnitude,r->bx)) WX(PlayerImpactMagnitude,r->bx,r->ax);
            if((int16_t)RX(PlayerVerticalVelocities,r->bx)<0) {
                r->ax=RX(PlayerImpactMagnitude,r->bx); r->si=(uint16_t)(R(SelectedDifficulty)<<1);
                if((int16_t)r->ax<(int16_t)RX(PlayerImpactLimits,r->si)) {
                    r->si=0; r->ax=(uint16_t)(sar(r->bp,5)+20);
                    for(unsigned budget=0;;budget++) {
                        if(budget==32768) return UGH_BUDGET;
                        if((int16_t)RX(PlatformLeftEdges,r->si)<0) break;
                        if(RX(PlatformHeights,r->si)==r->ax) {
                            r->cx=(uint16_t)(RX(PlayerPixelX,r->bx)+16);
                            if((int16_t)r->cx>=(int16_t)RX(PlatformLeftEdges,r->si) &&
                               (int16_t)r->cx<=(int16_t)RX(PlatformRightEdges,r->si)) {
                                r->si>>=1; WX(PlayerPlatformIndices,r->bx,r->si); r->ax=logic(r,0,16);
                                WX(PlayerHorizontalVelocities,r->bx,0); WX(PlayerVerticalVelocities,r->bx,0); break;
                            }
                        }
                        r->si=(uint16_t)(r->si+2);
                    }
                }
            }
        } else r->bp=r->di;
    }
    WX(PlayerY32,r->bx,r->bp); r->bp=sar(r->bp,5); WX(PlayerYPixels,r->bx,r->bp);
    r->ax=RX(PlayerImpactMagnitude,r->bx); r->si=(uint16_t)(R(SelectedDifficulty)<<1);
    sub16(r,r->ax,RX(PlayerImpactLimits,r->si),0);
    if((int16_t)r->ax>=(int16_t)RX(PlayerImpactLimits,r->si)) {
        sub16(r,R(ScreenFadeStep),0,0);
        if((int16_t)R(ScreenFadeStep)>=0) {
            r->ax=0xfffe; W(ScreenFadeStep,r->ax); W(ScreenFadeLevel,add16(r,R(ScreenFadeLevel),r->ax,0));
        }
    }
    physics_complete(r,plan);return UGH_OK;
}

