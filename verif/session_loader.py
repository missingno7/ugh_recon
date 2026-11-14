"""Checked level-loading ABI cuts; policy is in native/session.c."""
import re
from closure_support import ROOT,function

FIELDS='PlatformLeftEdges PlatformRightEdges PlatformHeights PlatformArrivalPointsX PlatformWaitingPointsX PlatformSpawnX PlatformDestinationIcons PlatformActorOccupants ActorDescriptors ActorInitialPlatformIndices ActorJourneyCursors ActorSpriteIds ActorEraseSprite ActorOverlayOrScriptCallbacks ActorEraseOverlaySprite ActorUpdateOrScriptCursor ActorX32 ActorY32 EnemyDescriptors EnemyPlatformIndices EnemyX32 EnemyY32 EnemyAnimationOrDropLists EnemyInitialDelays EnemyHorizontalSpeeds EnemyDirectionOrTargetPlayer EnemyStateCallbacks'.split()
def replace(s,a,b):assert s.count(a)==1,(a,s.count(a));return s.replace(a,b)
def lists():
    s='static uint16_t sq_load_base(SessionLoadField f){switch(f){\n'
    names='LF_PLATFORM_LEFT LF_PLATFORM_RIGHT LF_PLATFORM_HEIGHT LF_PLATFORM_ARRIVAL LF_PLATFORM_WAIT LF_PLATFORM_SPAWN LF_PLATFORM_ICON LF_PLATFORM_OCCUPANT LF_ACTOR_DESCRIPTOR LF_ACTOR_PLATFORM LF_ACTOR_JOURNEY LF_ACTOR_SPRITE LF_ACTOR_ERASE LF_ACTOR_OVERLAY LF_ACTOR_ERASE_OVERLAY LF_ACTOR_CALLBACK LF_ACTOR_X LF_ACTOR_Y LF_ENEMY_DESCRIPTOR LF_ENEMY_PLATFORM LF_ENEMY_X LF_ENEMY_Y LF_ENEMY_LIST LF_ENEMY_DELAY LF_ENEMY_SPEED LF_ENEMY_DIRECTION LF_ENEMY_CALLBACK'.split()
    for f,b in zip(names,FIELDS):s+=f'case {f}:return D({b});\n'
    s+='default:abort();}}\n'
    return s+r'''
static SessionLoadClass sq_load_class(SessionLoadFamily family,uint16_t descriptor){
 if(family==LOAD_ACTORS)return descriptor==D(Data_78DC)?LOAD_STONE:LOAD_ORDINARY;
 if(family!=LOAD_ENEMIES)return LOAD_ORDINARY;
 if(descriptor==D(Data_76E4))return LOAD_TREE;
 if(descriptor==D(Data_7630))return LOAD_BIRD;
 if(descriptor==D(Data_76A8))return LOAD_DINO;
 return LOAD_TRIOPTERUS;
}
static uint16_t sq_load_callback(SessionLoadClass kind){
 switch(kind){case LOAD_TREE:return G(InitializeFruitTreeAnimation);case LOAD_BIRD:return G(BeginBirdDelay);
 case LOAD_DINO:return G(InitializeDinoAnimation);case LOAD_TRIOPTERUS:return G(BeginTriopterusPatrol);default:abort();}
}
static int sq_load_lists(Regs *r,SessionLoadFamily family){
 r->di=logic(r,0,16);
 for(;;){
  SessionLoadRecord record;session_load_begin(&record,family,r->di);
  SessionLoadClass kind=LOAD_ORDINARY;uint16_t repeated=0,descriptor=0;
  for(;;){
   SessionLoadRequest e=session_load_next(&record);uint16_t reply=0;int status=0;
   sq_require(e.slot==r->di);
   switch(e.action){
   case LOAD_READ_LIST:
    lodsw(r);reply=r->ax;if(!record.cursor){descriptor=reply;kind=sq_load_class(family,reply);}break;
   case LOAD_READ_DESCRIPTOR:
    r->ax=rd16(r->ds,(uint16_t)(r->bx+sq_word(e.index,kind==LOAD_STONE?16:8)));reply=r->ax;break;
   case LOAD_READ_SPAWN:
    if(family==LOAD_ACTORS)r->bx=(uint16_t)(RI(ActorInitialPlatformIndices,r->di)*2u);
    r->bx=sq_word(e.index,r->bx);reply=RI(PlatformSpawnX,r->bx);break;
   case LOAD_READ_HEIGHT:r->bx=sq_word(e.index,r->bx);reply=RI(PlatformHeights,r->bx);break;
   case LOAD_READ_REPEAT:
    r->ax=(uint16_t)-sar(r->ax,2);repeated=rd16(r->ds,(uint16_t)(r->si-2));reply=repeated;break;
   case LOAD_SKIP:{
    uint16_t literal=family==LOAD_ENEMIES && kind==LOAD_DINO?4:2;
    r->si=(uint16_t)(r->si+sq_word(e.value,literal));break;}
   case LOAD_SCALE_Y:case LOAD_SCALE_SPEED:{
    uint16_t ret;
    if(family==LOAD_PLATFORMS)ret=0x10d;
    else if(kind==LOAD_DINO){r->ax=(uint16_t)(r->ax*32u);ret=0x233;}
    else {sq_require(kind==LOAD_BIRD);ret=0x205;}
    r->ax=sq_word(e.value,r->ax);
    status=ugh_call_near(e.action==LOAD_SCALE_Y?G(ScaleLevelYToThreeQuarters):G(ScaleLevelSpeedToThreeHalves),(uint16_t)(G(LoadCurrentLevelState)+ret),r);
    reply=r->ax;break;}
   case LOAD_STORE:{
    uint16_t value=r->ax;
    switch(e.arithmetic){
    case LOAD_SET_HIDDEN:r->ax=0xffff;value=r->ax;break;
    case LOAD_KEEP_ACCUMULATOR:value=e.field==LF_ENEMY_DIRECTION?(kind==LOAD_BIRD?1:0):0xffff;break;
    case LOAD_STONE_X:r->ax=(uint16_t)((reply=RI(PlatformSpawnX,r->bx))-8u);r->ax=(uint16_t)(r->ax*32u);value=r->ax;break;
    case LOAD_STONE_Y:r->ax=(uint16_t)((reply=RI(PlatformHeights,r->bx))-11u);r->ax=(uint16_t)(r->ax*32u);value=r->ax;break;
    case LOAD_TREE_X:case LOAD_TRIO_X:r->ax=(uint16_t)((RI(PlatformSpawnX,r->bx)-16u)*32u);value=r->ax;break;
    case LOAD_TREE_Y:r->ax=(uint16_t)((RI(PlatformHeights,r->bx)-24u)*32u);value=r->ax;break;
    case LOAD_TRIO_Y:r->ax=(uint16_t)((RI(PlatformHeights,r->bx)-22u)*32u);value=r->ax;break;
    case LOAD_DINO_X:r->ax=(uint16_t)(r->ax*32u);value=r->ax;break;
    case LOAD_DINO_Y:r->ax=sub16(r,r->ax,704,0);value=r->ax;break;
    case LOAD_TRIO_SPEED:r->ax=(uint16_t)(r->ax+repeated);r->ax=(uint16_t)-r->ax;value=r->ax;break;
    default:break;
    }
    wr16(r->ds,(uint16_t)(sq_load_base(e.field)+sq_word(e.slot,r->di)),sq_word(e.value,value));
    if(e.field==LF_PLATFORM_LEFT)r->ax=logic(r,r->ax,16);
    if(e.field==LF_ACTOR_DESCRIPTOR || e.field==LF_ENEMY_DESCRIPTOR){sub16(r,r->ax,0xffff,0);if(e.field==LF_ACTOR_DESCRIPTOR && r->ax!=0xffff)r->bx=r->ax;}
    if(e.field==LF_ENEMY_PLATFORM)r->bx=(uint16_t)(r->ax*2u);
    break;}
   case LOAD_CALLBACK:
    sq_require(e.value==(uint16_t)kind);wr16(r->ds,(uint16_t)(D(EnemyStateCallbacks)+e.slot),sq_load_callback((SessionLoadClass)e.value));break;
   case LOAD_END:break;
   default:abort();
   }
   if(status)return status;
   sq_require(session_load_accept(&record,e.action,reply,kind));
   sq_require(record.record_class==kind);
   if(e.action==LOAD_END){
    sq_require(record.descriptor==descriptor);
    int literal=family==LOAD_PLATFORMS?(descriptor&0x8000u)!=0:descriptor==0xffff;
    if(sq_bool(record.list_end,literal))return UGH_OK;
    r->di=(uint16_t)(r->di+2);break;
   }
  }
 }
}
'''

def generated():
    render=(ROOT/'c/render.c').read_text();items=(ROOT/'c/items_water.c').read_text()
    s='#undef CALL\n'+ '\n'.join(line for line in render.splitlines() if line.startswith(('#define RI(', '#define WI(', '#define WB(', '#define B(', '#define CALL(')))+'\n'+lists();b=function(render,'c_LoadCurrentLevelState')
    # Resource writes remain at matching cuts, before any immediately following read.
    start=b.index('    r->si=R(LevelPlatformList);');end=b.index('    r->bx=384;',start)
    b=b[:start]+'''    r->si=R(LevelPlatformList);{int status=sq_load_lists(r,LOAD_PLATFORMS);if(status)return status;}
    r->si=R(LevelActorList);{int status=sq_load_lists(r,LOAD_ACTORS);if(status)return status;}
    r->si=R(LevelEnemyList);{int status=sq_load_lists(r,LOAD_ENEMIES);if(status)return status;}
'''+b[end:]
    b=replace(b,'r->bx=(uint16_t)((R(PlayerCount)-1u)*2u);','r->bx=sq_word(session_loader_mode_key(R(PlayerCount)),(uint16_t)((R(PlayerCount)-1u)*2u));')
    b=replace(b,'r->si=(uint16_t)(R(CurrentLevelIndex)*2u);','r->si=sq_word(session_loader_level_key(R(CurrentLevelIndex)),(uint16_t)(R(CurrentLevelIndex)*2u));')
    b=replace(b,'r->si=sub16(r,r->si,2,0);','r->si=sq_word(session_record_previous(r->si),sub16(r,r->si,2,0));')
    b=b.replace('while(!(r->si&0x8000))','while(sq_bool(session_record_more(r->si),!(r->si&0x8000)))')
    b=replace(b,'r->si=(uint16_t)(r->si+2*step(r)); r->di=(uint16_t)(r->di+2*step(r)); r->cx--;','r->si=sq_word(session_copy_next(r->si,!!(r->flags&DF)),(uint16_t)(r->si+2*step(r))); r->di=sq_word(session_copy_next(r->di,!!(r->flags&DF)),(uint16_t)(r->di+2*step(r))); r->cx--;')
    b=replace(b,'while(r->cx);','while(sq_bool(session_count_more(r->cx),r->cx));')
    for raw,fixed,pixel,cached in [('LevelPlayerOneStartX','PlayerX32','PlayerPixelX','PlayerCachedPixelX'),('LevelPlayerTwoStartX','PlayerTwoFixedX','PlayerTwoPixelX','PlayerTwoCachedPixelX')]:
        old=f'r->ax=sub16(r,R({raw}),512,0); W({fixed},r->ax);'
        b=replace(b,old,f'SessionPlayerSeed seed_{fixed}=session_player_x(R({raw}));r->ax=sub16(r,R({raw}),512,0); W({fixed},sq_word(seed_{fixed}.fixed,r->ax));')
        b=replace(b,f'W({pixel},r->ax); W({cached},r->ax);',f'W({pixel},sq_word(seed_{fixed}.pixel,r->ax)); W({cached},sq_word(seed_{fixed}.pixel,r->ax));')
    for fixed,pixel,cached in [('PlayerY32','PlayerYPixels','PlayerCachedPixelY'),('PlayerTwoFixedY','SecondPlayerYPixels','PlayerTwoCachedPixelY')]:
        b=replace(b,f'r->ax=sub16(r,r->ax,320,0); W({fixed},r->ax);',f'SessionPlayerSeed seed_{fixed}=session_player_y(r->ax);r->ax=sub16(r,r->ax,320,0); W({fixed},sq_word(seed_{fixed}.fixed,r->ax));')
        b=replace(b,f'W({pixel},r->ax); W({cached},r->ax);',f'W({pixel},sq_word(seed_{fixed}.pixel,r->ax)); W({cached},sq_word(seed_{fixed}.pixel,r->ax));')
    b=replace(b,'    sub16(r,r->ax,0x17e0,0);','    uint16_t water=session_water_cap(r->ax);sub16(r,r->ax,0x17e0,0);')
    b=replace(b,'W(WaterY32,r->ax);','W(WaterY32,sq_word(water,r->ax));')
    b=b.replace('r->bx=sub16(r,r->bx,2,0);','r->bx=sq_word(session_record_previous(r->bx),sub16(r,r->bx,2,0));').replace('while(!(r->bx&0x8000))','while(sq_bool(session_record_more(r->bx),!(r->bx&0x8000)))')
    b=replace(b,'if(B(LevelRainDirection))','if(sq_bool(session_rain_enabled(B(LevelRainDirection)),B(LevelRainDirection)))')
    b=replace(b,'r->si=dec16(r,r->si);','r->si=sq_word(session_prewarm_previous(r->si),dec16(r,r->si));')
    s+=b+'\n'
    b=function(render,'c_InitializeLevelDisplay');b=replace(b,'    r->cx=196;','    SessionDisplayProcess display;session_display_begin(&display);\n    r->cx=196;')
    b=replace(b,'r->di=(uint16_t)(r->di+2*step(r));','r->di=sq_word(session_copy_next(r->di,!!(r->flags&DF)),(uint16_t)(r->di+2*step(r)));')
    b=replace(b,'while(r->cx);','while(sq_bool(session_count_more(r->cx),r->cx));')
    for field,raw in [('HudCachedLives','LivesRemaining'),('HudCachedMultiplier','ScoreMultiplier')]:
        b=replace(b,f'    set_al(r,(uint8_t)(B({raw})+11));',f'    uint8_t seed_{field}=session_display_byte(B({raw}));set_al(r,(uint8_t)(B({raw})+11));')
        b=replace(b,f'WB({field},r->ax);',f'WB({field},sq_word(seed_{field},(uint8_t)r->ax));')
    b=replace(b,'    r->ax=R(ScoreLowWord);','    uint32_t score=session_display_score((uint32_t)R(ScoreLowWord)|((uint32_t)R(ScoreHighWord)<<16));r->ax=R(ScoreLowWord);')
    b=replace(b,'W(HudCachedScoreLow,r->ax); W(HudCachedScoreHigh,r->dx);','W(HudCachedScoreLow,sq_word((uint16_t)score,r->ax)); W(HudCachedScoreHigh,sq_word((uint16_t)(score>>16),r->dx));')
    b=replace(b,'if(R(PlayerCount)==2)','if(sq_bool(session_display_layout(R(PlayerCount),1)==114,R(PlayerCount)==2))')
    layout=['HudLivesX','HudScoreX','HudLevelCounterX','HudPlayerOneDestinationX','HudPlayerOneIconX','HudFareX','HudMultiplierX','HudPlayerTwoIconX','HudPlayerTwoDestinationX']
    for i,field in enumerate(layout):b=re.sub(r'W\('+field+r',([0-9]+)\);',lambda m:'W('+field+',sq_word(session_display_layout(R(PlayerCount),'+str(i)+'),'+m[1]+'));',b)
    services=re.findall(r'CALL\((\w+),InitializeLevelDisplay,',b);assert len(services)==12
    for i,name in enumerate(services):
        b=replace(b,f'    CALL({name},',f'    sq_require(session_display_next(&display)=={i});sq_require(session_display_consume(&display,{i}));CALL({name},')
    b=replace(b,'    return ugh_dispatch','    sq_require(session_display_next(&display)==12);sq_require(session_display_consume(&display,12));sq_require(session_display_complete(&display));return ugh_dispatch')
    s+=b+'\n';b=function(items,'c_ResetScoreLivesAndMultiplier')
    b=replace(b,'D(LivesRemaining),3','D(LivesRemaining),(uint8_t)sq_word(session_reset_value(0),3)')
    b=replace(b,'D(ScoreMultiplier),1','D(ScoreMultiplier),(uint8_t)sq_word(session_reset_value(1),1)')
    b=replace(b,'D(ScoreLowWord),r->ax','D(ScoreLowWord),sq_word(session_reset_value(2),r->ax)')
    b=replace(b,'D(ScoreHighWord),r->ax','D(ScoreHighWord),sq_word(session_reset_value(3),r->ax)')
    s+=b+'\n'
    return s
