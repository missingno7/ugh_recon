#include "session_support.h"
static void push(Regs *r,uint16_t v) { r->sp=(uint16_t)(r->sp-2); wr16(r->ss,r->sp,v); }

static uint16_t pop(Regs *r) { uint16_t v=rd16(r->ss,r->sp); r->sp=(uint16_t)(r->sp+2); return v; }

static void lodsw(Regs *r) { r->ax=rd16(r->ds,r->si); r->si=(uint16_t)(r->si+2*step(r)); }

static void cmp8(Regs *r,uint8_t a,uint8_t b) {
    uint8_t v=(uint8_t)(a-b);
    flag(r,CF,a<b); flag(r,OF,((a^b)&(a^v)&128)!=0);
    flag(r,AF,((a^b^v)&16)!=0); szp(r,v,8);
}

static uint16_t sar(uint16_t v,unsigned n) {
    return (uint16_t)((v>>n)|((v&0x8000u) ? (0xffffu<<(16-n)) : 0));
}

static int scene_far_call(Regs *r,uint16_t seg,uint16_t off,uint16_t ret) {
    push(r,r->cs); push(r,ret); int st=ugh_dispatch(seg,off,r);
    r->sp=(uint16_t)(r->sp+4); return st;
}

#define R(n) rd16(r->ds,D(n))
#define W(n,v) wr16(r->ds,D(n),(uint16_t)(v))
#define RX(n,i) rd16(r->ds,(uint16_t)(D(n)+(i)))
#define WX(n,i,v) wr16(r->ds,(uint16_t)(D(n)+(i)),(uint16_t)(v))
#define CALL(n,ret) do { int status=ugh_call_near(G(n),ret,r); if(status) return status; } while(0)

static int sq_password(Regs *r,uint16_t key){
 SessionPassword password;session_password_begin(&password);
 r->cx=logic(r,0,16);r->bx=R(PlayerArrayBytes);
 key=sq_word(key,(uint16_t)(r->bx-2u));r->si=rd16(r->ds,(uint16_t)(D(PasswordListPointers)+key));
 for(;;){
  session_password_candidate(&password);r->bx=logic(r,0,16);r->bp=logic(r,0,16);
  for(unsigned chars=0;chars<65536;chars++){
   set_al(r,rd8(r->ds,r->si));r->si=(uint16_t)(r->si+step(r));logic(r,(uint8_t)r->ax,8);
   SessionPasswordResult decision=session_password_byte((uint8_t)r->ax);
   if(sq_bool(decision==PASSWORD_END,!(uint8_t)r->ax))break;
   if(sq_bool(decision==PASSWORD_DEFAULT,(uint8_t)r->ax==255)){r->cx=logic(r,0,16);r->cx=sq_word(session_password_selected(&password,1),r->cx);return UGH_OK;}
   uint16_t carry=r->flags&CF;r->bx=add16(r,r->bx,1,0);flag(r,CF,carry);
   uint16_t index=sq_word((uint16_t)(password.length+1u),r->bx);
   uint8_t editor=rd8(r->ds,(uint16_t)(D(PasswordCompareBiasedBase)+index));
   int different=session_password_compare(&password,(uint8_t)r->ax,editor);
   if(sq_bool(different,(uint8_t)r->ax!=editor))r->bp=dec16(r,r->bp);
   sq_require(password.length==r->bx && password.misses==r->bp && password.level==r->cx);
   if(chars==65535)return UGH_BUDGET;
  }
  logic(r,r->bp,16);
  if(sq_bool(!session_password_has_misses(&password),!r->bp)){
   for(;;){
    sub16(r,r->bx,20,0);
    if(sq_bool(!session_password_needs_padding(&password),r->bx>=20)){r->cx=sq_word(session_password_selected(&password,0),r->cx);return UGH_OK;}
    set_al(r,32);uint8_t editor=rd8(r->ds,(uint16_t)(D(PasswordEditBuffer)+r->bx));
    int space=session_password_padding(&password,editor);
    if(sq_bool(!space,editor!=32))break;
    uint16_t carry=r->flags&CF;r->bx=add16(r,r->bx,1,0);flag(r,CF,carry);sq_require(password.length==r->bx);
   }
  }
  session_password_reject(&password);uint16_t carry=r->flags&CF;r->cx=add16(r,r->cx,1,0);flag(r,CF,carry);sq_require(password.level==r->cx);
 }
}
static int sq_erase_enemies(Regs *r){r->si=logic(r,0,16);for(unsigned slots=0;slots<32768;slots++) {
            sub16(r,RX(EnemyDescriptors,r->si),0xffff,0); if(r->flags&ZF) break;
            SessionLayerPlan plan=sq_layer_open(r,0,1,1);
            r->ax=RX(EnemySpriteIds,r->si); r->cx=RX(EnemyEraseSprite,r->si); sq_layer_store(r,&plan,0,0,r->ax);
            sub16(r,r->cx,0xffff,0);
            if(sq_bool(plan.result.restore,r->cx!=0xffff)) {
                r->ax=RX(EnemyPreviousDrawX,r->si); r->bx=RX(EnemyPreviousDrawY,r->si);
                sq_layer_request(r,&plan,1);CALL(RestoreSpriteBackground,G(RunGameFromPassword)+0x138);
            }
            sq_layer_finish(&plan);r->si=add16(r,r->si,2,0); if(slots==32767) return UGH_BUDGET;
        }return UGH_OK;}
static int sq_draw_enemies(Regs *r,int front) {
    r->si=logic(r,0,16);
    for(unsigned budget=0;budget<32768;budget++) {
        r->ax=RX(EnemyDescriptors,r->si); sub16(r,r->ax,0xffff,0); if(r->ax==0xffff) return UGH_OK;
        sub16(r,r->ax,D(Data_76E4),0); int special=r->ax==D(Data_76E4);
        if(!special) { sub16(r,r->ax,D(Data_76A8),0); special=r->ax==D(Data_76A8); }
        int enabled=session_enemy_layer((uint8_t)special,(uint8_t)front);SessionLayerPlan plan=sq_layer_open(r,0,0,enabled);
        if(sq_bool(enabled,special!=front)) {
            r->ax=RX(EnemySpriteIds,r->si); sub16(r,r->ax,0xffff,0);
            if(sq_bool(plan.result.store_position,r->ax!=0xffff)) {
                r->bx=RX(EnemyDrawX,r->si); r->cx=RX(EnemyDrawY,r->si);
                sq_layer_store(r,&plan,0,1,r->bx); sq_layer_store(r,&plan,0,2,r->cx);
                r->bx=sar(RX(EnemyX32,r->si),5); sq_layer_store(r,&plan,0,3,r->bx);
                r->cx=sar(RX(EnemyY32,r->si),5); sq_layer_store(r,&plan,0,4,r->cx);
                sub16(r,r->cx,192,0);
                if(sq_bool(plan.result.draw,(int16_t)r->cx<192)) { sq_layer_request(r,&plan,0);CALL(DrawTransparentSprite,G(RunGameFromPassword)+(front?0x302:0x293)); }
            }
        }
        sq_layer_finish(&plan);r->si=add16(r,r->si,2,0);
    }
    return UGH_BUDGET;
}

static int sq_erase_items(Regs *r){        r->si=22;
        do {SessionLayerPlan plan=sq_layer_open(r,1,1,1);
            r->ax=RX(FallingItemSprites,r->si); r->cx=RX(FallingItemEraseSprite,r->si); sq_layer_store(r,&plan,1,0,r->ax);
            sub16(r,r->cx,0xffff,0);
            if(sq_bool(plan.result.restore,r->cx!=0xffff)) {
                r->ax=RX(FallingItemPreviousDrawX,r->si); r->bx=RX(FallingItemPreviousDrawY,r->si);
                sq_layer_request(r,&plan,1);CALL(RestoreSpriteBackground,G(RunGameFromPassword)+0x15f);
            }
            sq_layer_finish(&plan);r->si=sub16(r,r->si,2,0);
        } while(!(r->flags&SF));return UGH_OK;}
static int sq_draw_items(Regs *r){        r->si=22;
        do {SessionLayerPlan plan=sq_layer_open(r,1,0,1);
            r->ax=RX(FallingItemSprites,r->si); sub16(r,r->ax,0xffff,0);
            if(sq_bool(plan.result.store_position,r->ax!=0xffff)) {
                r->bx=RX(FallingItemDrawX,r->si); r->cx=RX(FallingItemDrawY,r->si); sq_layer_store(r,&plan,1,1,r->bx); sq_layer_store(r,&plan,1,2,r->cx);
                r->bx=sar(RX(FallingItemX,r->si),5); sq_layer_store(r,&plan,1,3,r->bx); r->cx=sar(RX(FallingItemY,r->si),5); sq_layer_store(r,&plan,1,4,r->cx);
                sub16(r,r->cx,192,0); if(sq_bool(plan.result.draw,(int16_t)r->cx<192)) { sq_layer_request(r,&plan,0);CALL(DrawTransparentSprite,G(RunGameFromPassword)+0x348); }
            }
            sq_layer_finish(&plan);r->si=sub16(r,r->si,2,0);
        } while(!(r->flags&SF));return UGH_OK;}
static int sq_near(Regs *r,SessionRequest e){
 uint16_t target,ret;
 switch(e.action){
case SESSION_PREGAME:target=G(PlayPreGameDemo);ret=(uint16_t)(G(RunGameFromPassword)+0x50);break;
case SESSION_RESET_GAME:target=G(ResetScoreLivesAndMultiplier);ret=(uint16_t)(G(RunGameFromPassword)+0x5d);break;
case SESSION_BLACK_PALETTE:target=G(BlackenVgaPalette);ret=(uint16_t)(G(RunGameFromPassword)+0x60);break;
case SESSION_INITIALIZE_LEVEL:target=G(InitializeLevelDisplay);ret=(uint16_t)(G(RunGameFromPassword)+0x63);break;
case SESSION_FADE_UPLOAD:target=G(ScaleAndUploadFadedPalette);ret=(uint16_t)(G(RunGameFromPassword)+0x91);break;
case SESSION_WAIT_RETRACE:target=G(WaitNextVerticalRetrace);ret=(uint16_t)(G(RunGameFromPassword)+0x9e);break;
case SESSION_HUD:target=G(RefreshHudAndTimerBar);ret=(uint16_t)(G(RunGameFromPassword)+0xa1);break;
case SESSION_ERASE_PLAYER:target=G(RestorePlayerBackground);ret=(uint16_t)(G(RunGameFromPassword)+0xa6);break;
case SESSION_RESTORE_RAIN:target=G(RestoreRainBackground);ret=(uint16_t)(G(RunGameFromPassword)+0x171);break;
case SESSION_ADVANCE_WATER:target=G(AdvanceWaterSurface);ret=(uint16_t)(G(RunGameFromPassword)+0x174);break;
case SESSION_POLL_CONTROLS:target=G(PollPlayerControls);ret=(uint16_t)(G(RunGameFromPassword)+0x177);break;
case SESSION_PAUSE_RELEASE:target=G(PollKeyboardScanChange);ret=(uint16_t)(G(RunGameFromPassword)+0x181);break;
case SESSION_PAUSE_MAKE:target=G(PollKeyboardScanChange);ret=(uint16_t)(G(RunGameFromPassword)+0x188);break;
case SESSION_PAUSE_BREAK:target=G(PollKeyboardScanChange);ret=(uint16_t)(G(RunGameFromPassword)+0x18f);break;
case SESSION_MOVE_PLAYER:target=G(MovePlayerWithVgaCollisions);ret=(uint16_t)(G(RunGameFromPassword)+0x1ce);break;
case SESSION_UPDATE_ACTORS:target=G(DispatchActorUpdates);ret=(uint16_t)(G(RunGameFromPassword)+0x1da);break;
case SESSION_UPDATE_ENEMIES:target=G(DispatchEnemyStates);ret=(uint16_t)(G(RunGameFromPassword)+0x1dd);break;
case SESSION_UPDATE_ITEMS:target=G(DispatchFallingItems);ret=(uint16_t)(G(RunGameFromPassword)+0x1e0);break;
case SESSION_DRAW_PLAYER:target=G(AnimateAndDrawPlayer);ret=(uint16_t)(G(RunGameFromPassword)+0x29d);break;
case SESSION_ADVANCE_RAIN:target=G(AdvanceRainParticles);ret=(uint16_t)(G(RunGameFromPassword)+0x394);break;
case SESSION_DRAW_RAIN:target=G(DrawRainParticles);ret=(uint16_t)(G(RunGameFromPassword)+0x397);break;
case SESSION_DRAW_WATER:target=G(DrawWaterSurface);ret=(uint16_t)(G(RunGameFromPassword)+0x39a);break;
case SESSION_SWAP_PAGE:target=G(SwapAndDisplayVgaPage);ret=(uint16_t)(G(RunGameFromPassword)+0x39d);break;
default:abort();}
return ugh_call_near(target,ret,r);}

EXPORT int c_RunGameFromPassword(Regs *r){
 SessionProcess process;session_begin(&process);
 for(;;){
  SessionWorld before=sq_world(r,process.phase);SessionRequest e=session_next(&process,before);int status=0;
  switch(e.action){
  case SESSION_PASSWORD:status=sq_password(r,e.index);break;
  case SESSION_SELECT_LEVEL:W(CurrentLevelIndex,sq_word(e.value,r->cx));break;
  case SESSION_START_MUSIC:
   push(r,sq_word(e.value,0xa5));push(r,0);push(r,UGH_S_B3444_ext_3444);push(r,0);
   status=scene_far_call(r,UGH_S_C_StartMusicTrack,UGH_O_C_StartMusicTrack,G(RunGameFromPassword)+0x73);
   if(!status){r->sp=add16(r,r->sp,8,0);}break;
  case SESSION_STOP_INITIAL_MUSIC:case SESSION_STOP_LEVEL_MUSIC:
   if(e.action==SESSION_STOP_LEVEL_MUSIC){r->cx=R(ScreenFadeLevel);sub16(r,r->cx,0,0);sq_require((int16_t)r->cx<0);}
   push(r,sq_word(e.value,0x11));status=scene_far_call(r,UGH_S_C_StopMusicTrack,UGH_O_C_StopMusicTrack,(uint16_t)(G(RunGameFromPassword)+(e.action==SESSION_STOP_INITIAL_MUSIC?0x57:0x3a7)));
   if(!status){r->sp=add16(r,r->sp,2,0);}break;
  case SESSION_FADE_UPLOAD:case SESSION_WAIT_RETRACE:
   r->cx=R(ScreenFadeLevel);sub16(r,r->cx,0,0);sq_require((int16_t)r->cx>=0);sub16(r,r->cx,256,0);
   sq_require((e.action==SESSION_FADE_UPLOAD)==((int16_t)r->cx<=256));r->cx=sq_word(e.value,r->cx);status=sq_near(r,e);break;
  case SESSION_FADE_ADVANCE:r->cx=add16(r,r->cx,R(ScreenFadeStep),0);W(ScreenFadeLevel,sq_word(e.value,r->cx));break;
  case SESSION_ERASE_PLAYER_BEGIN:case SESSION_DRAW_PLAYER_BEGIN:r->bx=logic(r,0,16);break;
  case SESSION_ERASE_PLAYER_NEXT:case SESSION_DRAW_PLAYER_NEXT:case SESSION_MOVE_NEXT:
   r->bx=add16(r,r->bx,2,0);r->bx=sq_word(e.index,r->bx);
   if(e.action==SESSION_MOVE_NEXT){sub16(r,r->bx,R(PlayerCount),0);sq_bool(e.decision,r->bx==R(PlayerCount));}
   else {sub16(r,r->bx,R(PlayerArrayBytes),0);sq_bool(e.decision,r->bx!=R(PlayerArrayBytes));}break;
  case SESSION_ERASE_PLAYER:case SESSION_DRAW_PLAYER:case SESSION_MOVE_PLAYER:r->bx=sq_word(e.index,r->bx);status=sq_near(r,e);break;
  case SESSION_ERASE_ACTORS:status=actor_render_session_GAME_ERASE(r);break;
  case SESSION_DRAW_ACTORS:status=actor_render_session_GAME_DRAW(r);break;
  case SESSION_DRAW_OVERLAYS:status=actor_render_session_GAME_OVERLAY(r);break;
  case SESSION_ERASE_ENEMIES:status=sq_erase_enemies(r);break;
  case SESSION_ERASE_ITEMS:status=sq_erase_items(r);break;
  case SESSION_DRAW_ITEMS:status=sq_draw_items(r);break;
  case SESSION_DRAW_ENEMIES_BACK:status=sq_draw_enemies(r,0);break;
  case SESSION_DRAW_ENEMIES_FRONT:status=sq_draw_enemies(r,1);break;
  case SESSION_IO_POINT:status=platform_service_point_at(SERVICE_IO,r->cs,G(RunGameFromPassword)+0x174,r);break;
  case SESSION_ESCAPE:
   if(sq_bool(e.decision,(uint8_t)r->ax==1)){
    wr8(r->ds,D(LivesRemaining),0);sub16(r,R(ScreenFadeStep),0,0);
    if(sq_bool(e.index,(int16_t)R(ScreenFadeStep)>=0)){r->ax=sq_word(e.other,0xfffe);W(ScreenFadeStep,r->ax);W(ScreenFadeLevel,sq_word(e.value,add16(r,R(ScreenFadeLevel),r->ax,0)));}
   }break;
  case SESSION_MOVE_BEGIN:{
   sub16(r,R(ScreenFadeLevel),192,0);int move=(int16_t)R(ScreenFadeLevel)>192;
   if(!move){sub16(r,R(ScreenFadeStep),0,0);move=(int16_t)R(ScreenFadeStep)<=0;}
   if(sq_bool(e.decision,move)){r->bx=logic(r,0,16);}break;}
  case SESSION_OUTCOME:logic(r,rd8(r->ds,D(LevelCompletionMarker)),8);sq_bool(e.decision,!!(r->flags&SF));break;
  case SESSION_DECREMENT_LIVES:{
   uint8_t old=rd8(r->ds,D(LivesRemaining)),v=(uint8_t)(old-1);uint16_t carry=r->flags&CF;
   flag(r,OF,old==128);flag(r,AF,((old^v^1)&16)!=0);szp(r,v,8);flag(r,CF,carry);
   wr8(r->ds,D(LivesRemaining),(uint8_t)sq_word(e.value,v));sq_bool(e.decision,v && !(r->flags&SF));break;}
  case SESSION_RESET_MULTIPLIER:wr8(r->ds,D(ScoreMultiplier),(uint8_t)sq_word(e.value,1));break;
  case SESSION_INCREMENT_LEVEL:{
   r->ax=R(CurrentLevelIndex);uint16_t carry=r->flags&CF;r->ax=add16(r,r->ax,1,0);flag(r,CF,carry);W(CurrentLevelIndex,sq_word(e.value,r->ax));break;}
  case SESSION_TEST_LEVEL_LIMIT:
   r->bx=sub16(r,R(PlayerArrayBytes),2,0);r->bx=sq_word(e.index,r->bx);
   sub16(r,r->ax,RX(LevelCountsByPlayerMode,r->bx),0);sq_bool(e.decision,!!(r->flags&CF));break;
  case SESSION_RETURN:break;
  case SESSION_FINISHED:sq_require(session_complete(&process));return UGH_OK;
  case SESSION_INVALID:abort();
  default:status=sq_near(r,e);break;
  }
  if(status)return status;
  sq_require(session_acknowledge(&process,e.action,sq_world(r,process.phase)));
  /* Existing L1 verification guard, not a new native-game lifetime limit. */
  if(process.completed_frames==100000)return UGH_BUDGET;
 }
}
#undef CALL
#define CALL(target,owner,delta) do { int status=ugh_call_near(G(target),(uint16_t)(G(owner)+(delta)),r); if(status) return status; } while(0)
#define B(name) rd8(r->ds,D(name))
#define WB(name,v) wr8(r->ds,D(name),(uint8_t)(v))
#define RI(name,i) rd16(r->ds,(uint16_t)(D(name)+(i)))
#define WI(name,i,v) wr16(r->ds,(uint16_t)(D(name)+(i)),(uint16_t)(v))
static uint16_t sq_load_base(SessionLoadField f){switch(f){
case LF_PLATFORM_LEFT:return D(PlatformLeftEdges);
case LF_PLATFORM_RIGHT:return D(PlatformRightEdges);
case LF_PLATFORM_HEIGHT:return D(PlatformHeights);
case LF_PLATFORM_ARRIVAL:return D(PlatformArrivalPointsX);
case LF_PLATFORM_WAIT:return D(PlatformWaitingPointsX);
case LF_PLATFORM_SPAWN:return D(PlatformSpawnX);
case LF_PLATFORM_ICON:return D(PlatformDestinationIcons);
case LF_PLATFORM_OCCUPANT:return D(PlatformActorOccupants);
case LF_ACTOR_DESCRIPTOR:return D(ActorDescriptors);
case LF_ACTOR_PLATFORM:return D(ActorInitialPlatformIndices);
case LF_ACTOR_JOURNEY:return D(ActorJourneyCursors);
case LF_ACTOR_SPRITE:return D(ActorSpriteIds);
case LF_ACTOR_ERASE:return D(ActorEraseSprite);
case LF_ACTOR_OVERLAY:return D(ActorOverlayOrScriptCallbacks);
case LF_ACTOR_ERASE_OVERLAY:return D(ActorEraseOverlaySprite);
case LF_ACTOR_CALLBACK:return D(ActorUpdateOrScriptCursor);
case LF_ACTOR_X:return D(ActorX32);
case LF_ACTOR_Y:return D(ActorY32);
case LF_ENEMY_DESCRIPTOR:return D(EnemyDescriptors);
case LF_ENEMY_PLATFORM:return D(EnemyPlatformIndices);
case LF_ENEMY_X:return D(EnemyX32);
case LF_ENEMY_Y:return D(EnemyY32);
case LF_ENEMY_LIST:return D(EnemyAnimationOrDropLists);
case LF_ENEMY_DELAY:return D(EnemyInitialDelays);
case LF_ENEMY_SPEED:return D(EnemyHorizontalSpeeds);
case LF_ENEMY_DIRECTION:return D(EnemyDirectionOrTargetPlayer);
case LF_ENEMY_CALLBACK:return D(EnemyStateCallbacks);
default:abort();}}

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
EXPORT int c_LoadCurrentLevelState(Regs *r) {
    r->bx=sq_word(session_loader_mode_key(R(PlayerCount)),(uint16_t)((R(PlayerCount)-1u)*2u)); r->bx=RI(LevelOrderTables,r->bx);
    r->si=sq_word(session_loader_level_key(R(CurrentLevelIndex)),(uint16_t)(R(CurrentLevelIndex)*2u)); r->bx=rd16(r->ds,(uint16_t)(r->bx+r->si));
    r->si=24;
    do {
        r->ax=rd16(r->ds,(uint16_t)(r->bx+r->si)); WI(CurrentLevelRecord,r->si,r->ax);
        r->si=sq_word(session_record_previous(r->si),sub16(r,r->si,2,0));
    } while(sq_bool(session_record_more(r->si),!(r->si&0x8000)));
    wr16(r->cs,G(RendererScratchWord),r->ax); push(r,r->ds);
    r->si=R(CompressedTileMapsPointer); r->ds=rd16(r->ds,D(CompressedTileMapsPointer)+2);
    CALL(UnpackIceToScratch,LoadCurrentLevelState,0x2e);
    r->ds=r->es; r->si=rd16(r->cs,G(RendererScratchWord));
    r->dx=DATA_SEG; r->es=r->dx; r->di=D(Data_264C); r->cx=160;
    do {
        wr16(r->es,r->di,rd16(r->ds,r->si));
        r->si=sq_word(session_copy_next(r->si,!!(r->flags&DF)),(uint16_t)(r->si+2*step(r))); r->di=sq_word(session_copy_next(r->di,!!(r->flags&DF)),(uint16_t)(r->di+2*step(r))); r->cx--;
    } while(sq_bool(session_count_more(r->cx),r->cx));
    r->ds=pop(r);
    SessionPlayerSeed seed_PlayerX32=session_player_x(R(LevelPlayerOneStartX));r->ax=sub16(r,R(LevelPlayerOneStartX),512,0); W(PlayerX32,sq_word(seed_PlayerX32.fixed,r->ax));
    r->ax=sar(r->ax,5); W(PlayerPixelX,sq_word(seed_PlayerX32.pixel,r->ax)); W(PlayerCachedPixelX,sq_word(seed_PlayerX32.pixel,r->ax));
    r->ax=R(LevelPlayerOneStartY); CALL(ScaleLevelYToThreeQuarters,LoadCurrentLevelState,0x5b);
    SessionPlayerSeed seed_PlayerY32=session_player_y(r->ax);r->ax=sub16(r,r->ax,320,0); W(PlayerY32,sq_word(seed_PlayerY32.fixed,r->ax)); r->ax=sar(r->ax,5);
    W(PlayerYPixels,sq_word(seed_PlayerY32.pixel,r->ax)); W(PlayerCachedPixelY,sq_word(seed_PlayerY32.pixel,r->ax));
    SessionPlayerSeed seed_PlayerTwoFixedX=session_player_x(R(LevelPlayerTwoStartX));r->ax=sub16(r,R(LevelPlayerTwoStartX),512,0); W(PlayerTwoFixedX,sq_word(seed_PlayerTwoFixedX.fixed,r->ax));
    r->ax=sar(r->ax,5); W(PlayerTwoPixelX,sq_word(seed_PlayerTwoFixedX.pixel,r->ax)); W(PlayerTwoCachedPixelX,sq_word(seed_PlayerTwoFixedX.pixel,r->ax));
    r->ax=R(LevelPlayerTwoStartY); CALL(ScaleLevelYToThreeQuarters,LoadCurrentLevelState,0x82);
    SessionPlayerSeed seed_PlayerTwoFixedY=session_player_y(r->ax);r->ax=sub16(r,r->ax,320,0); W(PlayerTwoFixedY,sq_word(seed_PlayerTwoFixedY.fixed,r->ax)); r->ax=sar(r->ax,5);
    W(SecondPlayerYPixels,sq_word(seed_PlayerTwoFixedY.pixel,r->ax)); W(PlayerTwoCachedPixelY,sq_word(seed_PlayerTwoFixedY.pixel,r->ax));
    r->ax=0xffff;
    W(PlayerPlatformIndices,r->ax); W(ds_27FA,r->ax);
    W(PlayerAnimationCountdowns,r->ax); W(PlayerTwoAnimationCountdown,r->ax);
    W(PlayerSpriteIds,218); W(PlayerTwoSpriteId,224);
    W(HudCachedPlayerOneIconState,r->ax); W(HudCachedPlayerTwoIconState,r->ax); WB(HudFareClearPending,r->ax);
    r->ax=0;
    W(PlayerCarriedKinds,r->ax); W(PlayerTwoPassengerIconState,r->ax);
    W(PlayerDestinationIcons,r->ax); W(PlayerTwoDestinationIconIndex,r->ax);
    W(PlayerPassengerFares,r->ax); W(PlayerTwoFare,r->ax);
    W(PlayerHorizontalVelocities,r->ax); W(ds_2812,r->ax);
    W(PlayerVerticalVelocities,r->ax); W(ds_2816,r->ax);
    r->ax=R(WaterY32); CALL(ScaleLevelYToThreeQuarters,LoadCurrentLevelState,0xda);
    uint16_t water=session_water_cap(r->ax);sub16(r,r->ax,0x17e0,0); if(r->ax>0x17e0) r->ax=0x17e0;
    W(WaterY32,sq_word(water,r->ax)); r->ax=sar(r->ax,5); W(WaterYPixels,r->ax); W(PreviousWaterSurfaceY,r->ax);
    r->si=R(LevelPlatformList);{int status=sq_load_lists(r,LOAD_PLATFORMS);if(status)return status;}
    r->si=R(LevelActorList);{int status=sq_load_lists(r,LOAD_ACTORS);if(status)return status;}
    r->si=R(LevelEnemyList);{int status=sq_load_lists(r,LOAD_ENEMIES);if(status)return status;}
    r->bx=384; r->ax=logic(r,0,16);
    do {
        WI(RainParticleOffsets,r->bx,r->ax); WI(RainPreviousOffsets,r->bx,r->ax);
        r->bx=sq_word(session_record_previous(r->bx),sub16(r,r->bx,2,0));
    } while(sq_bool(session_record_more(r->bx),!(r->bx&0x8000)));
    cmp8(r,B(LevelRainDirection),0);
    if(sq_bool(session_rain_enabled(B(LevelRainDirection)),B(LevelRainDirection))) {
        r->bx=384;
        do {
            CALL(RespawnRainParticle,LoadCurrentLevelState,0x2b0);
            r->bx=sq_word(session_record_previous(r->bx),sub16(r,r->bx,2,0));
        } while(sq_bool(session_record_more(r->bx),!(r->bx&0x8000)));
        r->si=576;
        do {
            CALL(AdvanceRainParticles,LoadCurrentLevelState,0x2bb); r->si=sq_word(session_prewarm_previous(r->si),dec16(r,r->si));
        } while(sq_bool(session_record_more(r->si),!(r->si&0x8000)));
    }
    return UGH_OK;
}

EXPORT int c_InitializeLevelDisplay(Regs *r) {
    SessionDisplayProcess display;session_display_begin(&display);
    r->cx=196; r->di=R(LevelWorkspacePointer); r->es=RI(LevelWorkspacePointer,2); r->ax=logic(r,0,16);
    do { wr16(r->es,r->di,r->ax); r->di=sq_word(session_copy_next(r->di,!!(r->flags&DF)),(uint16_t)(r->di+2*step(r))); r->cx--; } while(sq_bool(session_count_more(r->cx),r->cx));
    W(LevelTimer,0x5a3b); r->ax=0xffff; W(ds_27C8,r->ax); W(ScreenFadeStep,2);
    uint8_t seed_HudCachedLives=session_display_byte(B(LivesRemaining));set_al(r,(uint8_t)(B(LivesRemaining)+11)); cmp8(r,(uint8_t)r->ax,100);
    if((uint8_t)r->ax>=100) set_al(r,(uint8_t)(r->ax-100));
    WB(HudCachedLives,sq_word(seed_HudCachedLives,(uint8_t)r->ax));
    uint8_t seed_HudCachedMultiplier=session_display_byte(B(ScoreMultiplier));set_al(r,(uint8_t)(B(ScoreMultiplier)+11)); cmp8(r,(uint8_t)r->ax,100);
    if((uint8_t)r->ax>=100) set_al(r,(uint8_t)(r->ax-100));
    WB(HudCachedMultiplier,sq_word(seed_HudCachedMultiplier,(uint8_t)r->ax));
    WB(HudCachedLevelCounter,99); W(HudCachedFare,9999);
    uint32_t score=session_display_score((uint32_t)R(ScoreLowWord)|((uint32_t)R(ScoreHighWord)<<16));r->ax=R(ScoreLowWord); r->dx=R(ScoreHighWord);
    r->ax=add16(r,r->ax,0xb207,0); r->dx=add16(r,r->dx,1,!!(r->flags&CF));
    sub16(r,r->dx,15,0); int reduce=r->dx>15;
    if(r->dx==15) { sub16(r,r->ax,0x4240,0); reduce=r->ax>0x4240; }
    if(reduce) { r->ax=sub16(r,r->ax,0x4240,0); r->dx=sub16(r,r->dx,15,!!(r->flags&CF)); }
    W(HudCachedScoreLow,sq_word((uint16_t)score,r->ax)); W(HudCachedScoreHigh,sq_word((uint16_t)(score>>16),r->dx)); W(HudDigitCursorY,194);
    sub16(r,R(PlayerCount),2,0); W(HudLivesX,sq_word(session_display_layout(R(PlayerCount),0),33));
    if(sq_bool(session_display_layout(R(PlayerCount),1)==114,R(PlayerCount)==2)) {
        W(HudScoreX,sq_word(session_display_layout(R(PlayerCount),1),114)); W(HudLevelCounterX,sq_word(session_display_layout(R(PlayerCount),2),169)); W(HudPlayerOneDestinationX,sq_word(session_display_layout(R(PlayerCount),3),199));
        W(HudPlayerOneIconX,sq_word(session_display_layout(R(PlayerCount),4),215)); W(HudFareX,sq_word(session_display_layout(R(PlayerCount),5),232)); W(HudMultiplierX,sq_word(session_display_layout(R(PlayerCount),6),305));
        W(HudPlayerTwoIconX,sq_word(session_display_layout(R(PlayerCount),7),258)); W(HudPlayerTwoDestinationX,sq_word(session_display_layout(R(PlayerCount),8),274));
    } else {
        W(HudScoreX,sq_word(session_display_layout(R(PlayerCount),1),118)); W(HudLevelCounterX,sq_word(session_display_layout(R(PlayerCount),2),177)); W(HudPlayerOneDestinationX,sq_word(session_display_layout(R(PlayerCount),3),208));
        W(HudPlayerOneIconX,sq_word(session_display_layout(R(PlayerCount),4),224)); W(HudFareX,sq_word(session_display_layout(R(PlayerCount),5),244)); W(HudMultiplierX,sq_word(session_display_layout(R(PlayerCount),6),290));
    }
    sq_require(session_display_next(&display)==0);sq_require(session_display_consume(&display,0));CALL(LoadCurrentLevelState,InitializeLevelDisplay,0xef);
    sq_require(session_display_next(&display)==1);sq_require(session_display_consume(&display,1));CALL(ShowLevelIntroduction,InitializeLevelDisplay,0xf2);
    sq_require(session_display_next(&display)==2);sq_require(session_display_consume(&display,2));CALL(ClearAllVgaPlanes,InitializeLevelDisplay,0xf5);
    sq_require(session_display_next(&display)==3);sq_require(session_display_consume(&display,3));CALL(BlackenVgaPalette,InitializeLevelDisplay,0xf8);
    sq_require(session_display_next(&display)==4);sq_require(session_display_consume(&display,4));CALL(DuplicateSourcePaletteHalves,InitializeLevelDisplay,0xfb);
    sq_require(session_display_next(&display)==5);sq_require(session_display_consume(&display,5));CALL(DrawTileMap,InitializeLevelDisplay,0xfe);
    sq_require(session_display_next(&display)==6);sq_require(session_display_consume(&display,6));CALL(SaveDrawPageBackground,InitializeLevelDisplay,0x101);
    sq_require(session_display_next(&display)==7);sq_require(session_display_consume(&display,7));CALL(SwapAndDisplayVgaPage,InitializeLevelDisplay,0x104);
    sq_require(session_display_next(&display)==8);sq_require(session_display_consume(&display,8));CALL(RestorePlayfieldBackground,InitializeLevelDisplay,0x107);
    sq_require(session_display_next(&display)==9);sq_require(session_display_consume(&display,9));CALL(DrawHudBorders,InitializeLevelDisplay,0x10a);
    sq_require(session_display_next(&display)==10);sq_require(session_display_consume(&display,10));CALL(DispatchEnemyStates,InitializeLevelDisplay,0x10d);
    sq_require(session_display_next(&display)==11);sq_require(session_display_consume(&display,11));CALL(DispatchActorUpdates,InitializeLevelDisplay,0x110);
    sq_require(session_display_next(&display)==12);sq_require(session_display_consume(&display,12));sq_require(session_display_complete(&display));return ugh_dispatch(r->cs,G(ResetSpriteEraseState),r);
}

EXPORT int c_ResetScoreLivesAndMultiplier(Regs *r) {
    wr8(r->ds,D(LivesRemaining),(uint8_t)sq_word(session_reset_value(0),3)); wr8(r->ds,D(ScoreMultiplier),(uint8_t)sq_word(session_reset_value(1),1));
    r->ax=logic(r,0,16);
    wr16(r->ds,D(ScoreLowWord),sq_word(session_reset_value(2),r->ax)); wr16(r->ds,D(ScoreHighWord),sq_word(session_reset_value(3),r->ax));
    return UGH_OK;
}

