#include "player_physics.h"

static int pp_signed(uint16_t value) {return value<32768u?(int)value:(int)value-65536;}
uint16_t player_physics_sar(uint16_t value,unsigned count) {
    return (uint16_t)((value>>count)|((value&32768u)?(65535u<<(16u-count)):0u));
}
uint16_t player_physics_limit(uint16_t value) {
    if(pp_signed(value)<-6144)return 0xe800;
    if(pp_signed(value)>6144)return 0x1800;
    return value;
}
uint16_t player_physics_reflect(uint16_t *velocity) {
    *velocity=player_physics_sar((uint16_t)(0u-*velocity),1);
    uint16_t magnitude=(uint16_t)(*velocity*2u);
    return pp_signed(magnitude)<0?(uint16_t)(0u-magnitude):magnitude;
}
uint8_t player_collision_sample(const uint8_t samples[10]) {
    uint8_t result=samples[0];
    for(unsigned i=1;i<10;i++)result|=samples[i];
    return result;
}
static void pp_append(PlayerPhysicsProcess *p,PlayerPhysicsEvent event) {
    if(p->count>=32){p->failed=1;return;}
    p->journal[p->count++]=event;
}
static void pp_write(PlayerPhysicsProcess *p,PlayerPhysicsField field,uint16_t value) {
    PlayerPhysicsView *v=p->player;PlayerPhysicsWorld *w=p->world;
    switch(field) {
    case PF_TIMER:w->timer=value;break;case PF_IMPACT:v->impact=value;break;
    case PF_THRUST:v->thrust=value;break;case PF_VX:v->velocity_x=value;break;
    case PF_VY:v->velocity_y=value;break;case PF_X:v->position.x32=value;break;
    case PF_PIXEL_X:v->pixel_x=value;break;case PF_PLATFORM:v->platform=value;break;
    case PF_Y:v->position.y32=value;break;case PF_PIXEL_Y:v->pixel_y=value;break;
    case PF_FADE_RATE:w->fade_rate=value;break;case PF_FADE_LEVEL:w->fade_level=value;break;
    }
    pp_append(p,(PlayerPhysicsEvent){.kind=PP_WRITE,.field=field,.value=value});
}
static void pp_plane(PlayerPhysicsProcess *p,int select) {
    if(select)pp_append(p,(PlayerPhysicsEvent){.kind=PP_SELECT_PLANE_REGISTER,.value=4});
    pp_append(p,(PlayerPhysicsEvent){.kind=PP_READ_PLANE,.value=p->plane});
}
static void pp_probe(PlayerPhysicsProcess *p) {
    pp_append(p,(PlayerPhysicsEvent){.kind=PP_SAMPLE,.probe={p->player->pixel_x,
        p->player->pixel_y,p->columns,p->rows}});
}
static void pp_initial(PlayerPhysicsProcess *p) {
    PlayerPhysicsView *v=p->player;PlayerPhysicsWorld *w=p->world;
    pp_write(p,PF_TIMER,(uint16_t)(w->timer-1u));
    pp_write(p,PF_IMPACT,0);pp_write(p,PF_THRUST,0);
    uint16_t surface=(uint16_t)(v->pixel_y-w->water_y+18u);
    if(pp_signed(surface)>0)surface=(uint16_t)((surface&255u)|256u);
    p->water_state=(surface>>8)<128u?(int)(surface>>8):(int)(surface>>8)-256;
    p->stage=pp_signed(v->platform)<0?PP_HORIZONTAL:PP_VERTICAL;
}
static void pp_horizontal(PlayerPhysicsProcess *p) {
    PlayerPhysicsView *v=p->player;PlayerPhysicsWorld *w=p->world;
    if(p->water_state<0 && w->rain) {
        uint16_t wind=(uint16_t)((((unsigned)w->rain-1u)*2u-1u)*32u);
        pp_write(p,PF_VX,(uint16_t)(v->velocity_x+wind));
        uint16_t fall=player_physics_sar(wind,1);
        if(pp_signed(fall)<0)fall=(uint16_t)(0u-fall);
        pp_write(p,PF_VY,(uint16_t)(v->velocity_y+fall));
    }
    uint16_t speed=v->velocity_x;
    if(v->left){speed=(uint16_t)(speed-63u);pp_write(p,PF_THRUST,(uint16_t)(v->thrust+63u));}
    else if(v->right){speed=(uint16_t)(speed+63u);pp_write(p,PF_THRUST,(uint16_t)(v->thrust+63u));}
    speed=player_physics_limit(speed);pp_write(p,PF_VX,speed);
    uint16_t candidate=(uint16_t)(v->position.x32+player_physics_sar(speed,6));
    if(pp_signed(candidate)<-512){candidate=0xfe00;pp_write(p,PF_VX,0);}
    else if(pp_signed(candidate)>9728){candidate=0x2600;pp_write(p,PF_VX,0);}
    p->candidate=candidate;p->cursor=candidate;p->plane=(uint16_t)((v->pixel_x+37u)&3u);
    p->columns=p->rows=0;pp_plane(p,1);
    if(player_physics_sar(candidate,5)==v->pixel_x){p->stage=PP_HORIZONTAL_END;return;}
    p->cursor=v->position.x32;p->positive=pp_signed(candidate)>pp_signed(p->cursor);
    if(!p->positive) {
        p->plane=(uint16_t)((p->plane-1u)&255u);
        if(p->plane&128u){p->plane&=3u;p->columns=(uint16_t)(p->columns-1u);}
        pp_plane(p,0);
    }
    p->stage=PP_HORIZONTAL_SCAN;
}
static void pp_horizontal_scan(PlayerPhysicsProcess *p) {
    if(p->positive) {
        p->plane=(uint16_t)((p->plane+1u)&255u);
        if(p->plane>=4u){p->plane&=3u;p->columns=(uint16_t)(p->columns+1u);}
        pp_plane(p,0);
    }
    pp_probe(p);p->stage=PP_HORIZONTAL_HIT;
}
static void pp_horizontal_hit(PlayerPhysicsProcess *p) {
    if(p->sample&128u) {
        p->cursor=p->positive?(uint16_t)(p->cursor&0xffe0u):(uint16_t)((p->cursor&0xffe0u)+32u);
        uint16_t speed=p->player->velocity_x,impact=player_physics_reflect(&speed);
        pp_write(p,PF_VX,speed);pp_write(p,PF_IMPACT,impact);p->stage=PP_HORIZONTAL_END;
    } else {
        p->cursor=(uint16_t)(p->cursor+(p->positive?32u:65504u));
        int more=p->positive?pp_signed(p->cursor)<pp_signed(p->candidate):pp_signed(p->cursor)>pp_signed(p->candidate);
        p->stage=more?PP_HORIZONTAL_SCAN:PP_HORIZONTAL_END;
        if(!more)p->cursor=p->candidate;
    }
}
static void pp_horizontal_end(PlayerPhysicsProcess *p) {
    pp_write(p,PF_X,p->cursor);pp_write(p,PF_PIXEL_X,player_physics_sar(p->cursor,5));p->stage=PP_VERTICAL;
}
static void pp_vertical(PlayerPhysicsProcess *p) {
    PlayerPhysicsView *v=p->player;PlayerPhysicsWorld *w=p->world;uint16_t speed=v->velocity_y;
    if(p->water_state>0) {
        pp_write(p,PF_TIMER,(uint16_t)(w->timer-2u));
        if(pp_signed(speed)>0)speed=(uint16_t)(speed-193u);
        else{speed=(uint16_t)(speed-21u);pp_write(p,PF_PLATFORM,65535);}
    } else {
        if(p->water_state<0 && pp_signed(v->platform)<0) {
            speed=(uint16_t)(speed+27u);pp_write(p,PF_TIMER,(uint16_t)(w->timer-2u));
            if(v->down) {
                speed=(uint16_t)(speed+70u);pp_write(p,PF_THRUST,(uint16_t)(v->thrust+90u));goto limit;
            }
        }
        if(v->up) {
            pp_write(p,PF_TIMER,(uint16_t)(w->timer-3u));speed=(uint16_t)(speed-70u);
            pp_write(p,PF_THRUST,(uint16_t)(v->thrust+90u));pp_write(p,PF_PLATFORM,65535);
        }
    }
limit:
    speed=player_physics_limit(speed);pp_write(p,PF_VY,speed);
    uint16_t candidate=(uint16_t)(v->position.y32+player_physics_sar(speed,6));
    if(pp_signed(candidate)<-608){candidate=0xfda0;pp_write(p,PF_VY,0);}
    else if(pp_signed(candidate)>6112){candidate=0x17e0;pp_write(p,PF_VY,0);}
    if(p->water_state>0 && pp_signed((uint16_t)(player_physics_sar(candidate,5)-w->water_y+18u))<=0) {
        pp_write(p,PF_VY,0);candidate=(uint16_t)(w->water_y*32u-0x240u);
    }
    p->candidate=candidate;p->cursor=candidate;p->plane=(uint16_t)((v->pixel_x+37u)&3u);
    p->columns=p->rows=0;pp_plane(p,1);
    if(player_physics_sar(candidate,5)==v->pixel_y){p->stage=PP_VERTICAL_END;return;}
    p->cursor=v->position.y32;p->positive=pp_signed(candidate)>pp_signed(p->cursor);
    if(!p->positive)p->rows=65535;
    p->stage=PP_VERTICAL_SCAN;
}
static void pp_vertical_scan(PlayerPhysicsProcess *p) {
    if(p->positive)p->rows=(uint16_t)(p->rows+1u);
    pp_probe(p);p->stage=PP_VERTICAL_HIT;
}
static int pp_platform_decision(const LevelPlatform *platform,uint16_t height,uint16_t center) {
    if(pp_signed(platform->left)<0)return -1;
    return platform->surface_y==height && pp_signed(center)>=pp_signed(platform->left) && pp_signed(center)<=pp_signed(platform->right);
}
static int pp_find_platform(const PlayerPhysicsWorld *w,uint16_t pixel_x,uint16_t cursor) {
    uint16_t height=(uint16_t)(player_physics_sar(cursor,5)+20u);
    uint16_t center=(uint16_t)(pixel_x+16u);
    for(size_t i=0;i<w->platform_count;i++) {
        const LevelPlatform *platform=&w->platforms[i];
        int decision=pp_platform_decision(platform,height,center);
        if(decision<0)break;
        if(decision)return (int)i;
    }
    return -1;
}
static void pp_vertical_hit(PlayerPhysicsProcess *p) {
    PlayerPhysicsView *v=p->player;PlayerPhysicsWorld *w=p->world;
    if(p->sample&128u) {
        p->cursor=p->positive?(uint16_t)(p->cursor&0xffe0u):(uint16_t)((p->cursor&0xffe0u)+32u);
        uint16_t speed=v->velocity_y,impact=player_physics_reflect(&speed);pp_write(p,PF_VY,speed);
        if(pp_signed(impact)>pp_signed(v->impact))pp_write(p,PF_IMPACT,impact);
        if(pp_signed(v->velocity_y)<0 && pp_signed(v->impact)<pp_signed(w->impact_limit)) {
            int selected=pp_find_platform(w,v->pixel_x,p->cursor);
            if(selected>=0){pp_write(p,PF_PLATFORM,(uint16_t)selected);pp_write(p,PF_VX,0);pp_write(p,PF_VY,0);}
        }
        p->stage=PP_VERTICAL_END;
    } else {
        p->cursor=(uint16_t)(p->cursor+(p->positive?32u:65504u));
        int more=p->positive?pp_signed(p->cursor)<pp_signed(p->candidate):pp_signed(p->cursor)>pp_signed(p->candidate);
        p->stage=more?PP_VERTICAL_SCAN:PP_VERTICAL_END;
        if(!more)p->cursor=p->candidate;
    }
}
static void pp_vertical_end(PlayerPhysicsProcess *p) {
    pp_write(p,PF_Y,p->cursor);pp_write(p,PF_PIXEL_Y,player_physics_sar(p->cursor,5));
    if(pp_signed(p->player->impact)>=pp_signed(p->world->impact_limit) && pp_signed(p->world->fade_rate)>=0) {
        pp_write(p,PF_FADE_RATE,65534);pp_write(p,PF_FADE_LEVEL,(uint16_t)(p->world->fade_level-2u));
    }
    p->stage=PP_FINISHED;
}
void player_physics_begin(PlayerPhysicsProcess *p,PlayerPhysicsView *v,PlayerPhysicsWorld *w) {
    *p=(PlayerPhysicsProcess){.player=v,.world=w,.stage=PP_INITIAL};
}
PlayerPhysicsEvent player_physics_poll(PlayerPhysicsProcess *p) {
    if(p->awaiting_reply){p->failed=1;return (PlayerPhysicsEvent){.kind=PP_DONE};}
    while(p->consumed==p->count && p->stage!=PP_FINISHED && !p->failed) {
        p->count=p->consumed=0;
        switch(p->stage) {
        case PP_INITIAL:pp_initial(p);break;case PP_HORIZONTAL:pp_horizontal(p);break;
        case PP_HORIZONTAL_SCAN:pp_horizontal_scan(p);break;case PP_HORIZONTAL_HIT:pp_horizontal_hit(p);break;
        case PP_HORIZONTAL_END:pp_horizontal_end(p);break;case PP_VERTICAL:pp_vertical(p);break;
        case PP_VERTICAL_SCAN:pp_vertical_scan(p);break;case PP_VERTICAL_HIT:pp_vertical_hit(p);break;
        case PP_VERTICAL_END:pp_vertical_end(p);break;case PP_FINISHED:break;
        }
    }
    if(p->consumed==p->count)return (PlayerPhysicsEvent){.kind=PP_DONE};
    PlayerPhysicsEvent event=p->journal[p->consumed++];
    if(event.kind==PP_SAMPLE)p->awaiting_reply=1;
    return event;
}
void player_physics_reply(PlayerPhysicsProcess *p,uint8_t sample) {
    if(!p->awaiting_reply){p->failed=1;return;}
    p->sample=sample;p->awaiting_reply=0;
}
