"""Build the session-owned adapter from checked ABI fragments and native control."""
import argparse,re
from closure_support import ROOT,function
OUT=ROOT/'build/workers/close-stones-12/session'
BRIDGE=ROOT/'native/bridge/session_bridge.c'
FILES=[ROOT/'native/session.h',ROOT/'native/session.c',ROOT/'native/bridge/session_support.h',ROOT/'native/bridge/session_actor_render.h',BRIDGE]
NAMES=['RunGameFromPassword','InitializeLevelDisplay','LoadCurrentLevelState','ResetScoreLivesAndMultiplier']

def replace(text,old,new):assert text.count(old)==1,(old,text.count(old));return text.replace(old,new)
def loop_body(text,start):
    a=text.index('{',start);depth=1;b=a+1
    while depth:
        depth+=(text[b]=='{')-(text[b]=='}');b+=1
    return a+1,b-1
def layer_functions():
    raw=(ROOT/'c/scene.c').read_text();game=function(raw,'c_RunGameFromPassword');loops=[]
    for m in re.finditer(r'for\(unsigned slots=0;slots<32768;slots\+\+\)',game):
        a,b=loop_body(game,m.start())
        if 'RX(EnemyDescriptors,r->si)' in game[a:b]:loops.append(game[m.start():b+1])
    assert len(loops)==1;erase=loops[0]
    at=erase.index('            r->ax=RX(EnemySpriteIds,r->si);')
    erase=erase[:at]+'            SessionLayerPlan plan=sq_layer_open(r,0,1,1);\n'+erase[at:]
    erase=replace(erase,'WX(EnemyEraseSprite,r->si,r->ax);','sq_layer_store(r,&plan,0,0,r->ax);')
    erase=replace(erase,'if(r->cx!=0xffff)','if(sq_bool(plan.result.restore,r->cx!=0xffff))')
    erase=replace(erase,'                CALL(RestoreSpriteBackground','                sq_layer_request(r,&plan,1);CALL(RestoreSpriteBackground')
    erase=replace(erase,'            r->si=add16(r,r->si,2,0);','            sq_layer_finish(&plan);r->si=add16(r,r->si,2,0);')
    out='static int sq_erase_enemies(Regs *r){r->si=logic(r,0,16);'+erase+'return UGH_OK;}\n'
    draw=function(raw,'draw_enemy_layer').replace('draw_enemy_layer','sq_draw_enemies')
    draw=replace(draw,'        if(special!=front) {','        int enabled=session_enemy_layer((uint8_t)special,(uint8_t)front);SessionLayerPlan plan=sq_layer_open(r,0,0,enabled);\n        if(sq_bool(enabled,special!=front)) {')
    for i,field in enumerate(['EnemyPreviousDrawX','EnemyPreviousDrawY','EnemyDrawX','EnemyDrawY'],1):
        pattern=r'WX\('+field+r',r->si,([^;]+)\);';assert len(re.findall(pattern,draw))==1;draw=re.sub(pattern,lambda m:f'sq_layer_store(r,&plan,0,{i},'+m[1]+');',draw)
    draw=replace(draw,'if(r->ax!=0xffff)','if(sq_bool(plan.result.store_position,r->ax!=0xffff))')
    draw=replace(draw,'if((int16_t)r->cx<192)','if(sq_bool(plan.result.draw,(int16_t)r->cx<192))')
    draw=replace(draw,'{ CALL(DrawTransparentSprite','{ sq_layer_request(r,&plan,0);CALL(DrawTransparentSprite')
    draw=replace(draw,'        r->si=add16(r,r->si,2,0);','        sq_layer_finish(&plan);r->si=add16(r,r->si,2,0);');out+=draw+'\n'
    for erase_mode,start in [(True,'        r->si=22;'),(False,'        r->si=22;')]:
        # There are exactly two descending item passes in the source.
        a=game.index(start) if erase_mode else game.index(start,game.index(start)+1)
        end=game.index('        } while(!(r->flags&SF));',a)+len('        } while(!(r->flags&SF));')
        body=game[a:end];body=replace(body,'        do {','        do {SessionLayerPlan plan=sq_layer_open(r,1,'+str(int(erase_mode))+',1);')
        if erase_mode:
            body=replace(body,'WX(FallingItemEraseSprite,r->si,r->ax);','sq_layer_store(r,&plan,1,0,r->ax);')
            body=replace(body,'if(r->cx!=0xffff)','if(sq_bool(plan.result.restore,r->cx!=0xffff))')
            body=replace(body,'                CALL(RestoreSpriteBackground','                sq_layer_request(r,&plan,1);CALL(RestoreSpriteBackground')
        else:
            for i,field in enumerate(['FallingItemPreviousDrawX','FallingItemPreviousDrawY','FallingItemDrawX','FallingItemDrawY'],1):
                pattern=r'WX\('+field+r',r->si,([^;]+)\);';assert len(re.findall(pattern,body))==1;body=re.sub(pattern,lambda m:f'sq_layer_store(r,&plan,1,{i},'+m[1]+');',body)
            body=replace(body,'if(r->ax!=0xffff)','if(sq_bool(plan.result.store_position,r->ax!=0xffff))')
            body=replace(body,'if((int16_t)r->cx<192)','if(sq_bool(plan.result.draw,(int16_t)r->cx<192))')
            body=replace(body,'{ CALL(DrawTransparentSprite','{ sq_layer_request(r,&plan,0);CALL(DrawTransparentSprite')
        body=replace(body,'            r->si=sub16(r,r->si,2,0);','            sq_layer_finish(&plan);r->si=sub16(r,r->si,2,0);')
        out+='static int sq_'+('erase' if erase_mode else 'draw')+'_items(Regs *r){'+body+'return UGH_OK;}\n'
    return out

def password():
    return r'''
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
'''

NEAR=[('SESSION_PREGAME','PlayPreGameDemo',0x50),('SESSION_RESET_GAME','ResetScoreLivesAndMultiplier',0x5d),('SESSION_BLACK_PALETTE','BlackenVgaPalette',0x60),('SESSION_INITIALIZE_LEVEL','InitializeLevelDisplay',0x63),('SESSION_FADE_UPLOAD','ScaleAndUploadFadedPalette',0x91),('SESSION_WAIT_RETRACE','WaitNextVerticalRetrace',0x9e),('SESSION_HUD','RefreshHudAndTimerBar',0xa1),('SESSION_ERASE_PLAYER','RestorePlayerBackground',0xa6),('SESSION_RESTORE_RAIN','RestoreRainBackground',0x171),('SESSION_ADVANCE_WATER','AdvanceWaterSurface',0x174),('SESSION_POLL_CONTROLS','PollPlayerControls',0x177),('SESSION_PAUSE_RELEASE','PollKeyboardScanChange',0x181),('SESSION_PAUSE_MAKE','PollKeyboardScanChange',0x188),('SESSION_PAUSE_BREAK','PollKeyboardScanChange',0x18f),('SESSION_MOVE_PLAYER','MovePlayerWithVgaCollisions',0x1ce),('SESSION_UPDATE_ACTORS','DispatchActorUpdates',0x1da),('SESSION_UPDATE_ENEMIES','DispatchEnemyStates',0x1dd),('SESSION_UPDATE_ITEMS','DispatchFallingItems',0x1e0),('SESSION_DRAW_PLAYER','AnimateAndDrawPlayer',0x29d),('SESSION_ADVANCE_RAIN','AdvanceRainParticles',0x394),('SESSION_DRAW_RAIN','DrawRainParticles',0x397),('SESSION_DRAW_WATER','DrawWaterSurface',0x39a),('SESSION_SWAP_PAGE','SwapAndDisplayVgaPage',0x39d)]

def generated():
    raw=(ROOT/'c/scene.c').read_text();render=(ROOT/'c/render.c').read_text()
    out='#include "session_support.h"\n'
    for source,name in [(render,'push'),(render,'pop'),(render,'lodsw'),(render,'cmp8'),(raw,'sar'),(raw,'scene_far_call')]:out+=function(source,name)+'\n'
    out+='\n'.join(s for s in raw.splitlines() if s.startswith('#define '))+'\n'+password()+layer_functions()
    out+='''static int sq_near(Regs *r,SessionRequest e){
 uint16_t target,ret;
 switch(e.action){
'''
    for action,name,offset in NEAR:out+=f'case {action}:target=G({name});ret=(uint16_t)(G(RunGameFromPassword)+0x{offset:x});break;\n'
    out+='default:abort();}\nreturn ugh_call_near(target,ret,r);}\n'
    out+=r'''
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
'''
    from session_loader import generated as loader_generated
    return out+loader_generated()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');a=ap.parse_args();s=generated()
    if a.write:BRIDGE.write_text(s)
    assert BRIDGE.read_text()==s;print('PASS session-owned event adapter, password cuts and four layer passes')
if __name__=='__main__':main()
