"""Small actual-native-C transition properties. Scope is recorded per profile.

These are not a byte-RAM whole-session theorem. Literal scalar fragments and
the checked ABI cut inventory supply the seams; full caller composition is C/D.
"""
import argparse
from closure_support import ROOT,function
from sequencing_build import OUT
from sequencing_limits import cbmc

KEYS=['life-order','life-frame','life-dependence','life-consume','loader-scalar','display-byte',
 'display-score','password','render-output','render-frame','render-dependence','session-step',
 'session-frame','session-dependence','load-step','load-frame','load-dependence','display-order','protocol','session-order']
def check(e,label):return 'CHECK('+e+',"'+label+'");\n'
def common():
    render=(ROOT/'c/render.c').read_text();scene=(ROOT/'c/scene.c').read_text()
    return '#include "ugh.h"\n#include "'+(ROOT/'native/session.c').as_posix()+'"\n#include "'+(ROOT/'native/lifecycle.c').as_posix()+'"\n#define CHECK(c,m) __CPROVER_assert((c),(m))\n'+function(scene,'sar')+function(render,'cmp8')

def body(key):
    s='int main(void){'
    if key.startswith('life-'):
        s+='LifecycleProcess p;unsigned task,at;__CPROVER_assume(task<4);const unsigned lengths[]={6,12,1,2};__CPROVER_assume(at<lengths[task]);lifecycle_begin(&p,(LifecycleTask)task);p.cursor=(uint8_t)at;uint16_t mode;lifecycle_video_reply(&p,mode);LifecycleProcess before=p;'
        s+='const LifecycleAction expected[4][12]={{LIFE_BIND_WORLD,LIFE_INITIALIZE_PLATFORM,LIFE_STARTUP_PICTURES,LIFE_GAMEPLAY_VIDEO,LIFE_MAIN_MENU,LIFE_SHUTDOWN_PLATFORM},{LIFE_QUERY_VIDEO,LIFE_SAVE_VIDEO,LIFE_CPU_PROBE,LIFE_INSTALL_ERROR_HANDLER,LIFE_LOAD_SCORES,LIFE_SEED_RANDOM,LIFE_SET_VIDEO,LIFE_PICTURE_VIDEO,LIFE_INSTALL_KEYBOARD,LIFE_CALIBRATE_CONTROLS,LIFE_INITIALIZE_AUDIO,LIFE_CLEAR_VIDEO},{LIFE_SOUND_INITIALIZE_ADLIB},{LIFE_STOP_MUSIC,LIFE_SOUND_STOP}};LifecycleRequest e=lifecycle_next(&p);'
        if key=='life-order':
            s+=check('e.action==expected[task][at]','all lifecycle cuts in source order')
            s+='uint16_t arg=e.action==LIFE_SAVE_VIDEO?(mode&127u):e.action==LIFE_SET_VIDEO?19:e.action==LIFE_SOUND_INITIALIZE_ADLIB?1:e.action==LIFE_STOP_MUSIC?17:0;'
            s+=check('e.argument==arg','complete parameters including saved low seven bits and AdLib-only request')
        elif key=='life-frame':s+=check('p.task==before.task && p.cursor==before.cursor && p.saved_mode==before.saved_mode && !p.failed && p.pending','next frames every nonprotocol field')
        elif key=='life-dependence':
            s+='LifecycleProcess q=before;uint16_t other;if(e.action!=LIFE_SAVE_VIDEO)q.saved_mode=other;LifecycleRequest f=lifecycle_next(&q);'
            s+=check('e.action==f.action && e.argument==f.argument','inactive saved video mode is not a request input')
        else:
            s+=check('lifecycle_consume(&p,e.action) && p.cursor==at+1 && !p.pending && !p.failed','exactly one request consumed')
            s+=check('lifecycle_complete(&p)==(at+1==lengths[task])','no unconsumed request on completion')
    elif key=='loader-scalar':
        s+='uint16_t v,repeated;Regs regs,*r=&regs;r->ax=v;'
        # Keep the cap fragment and arithmetic helper actual, not an integer model of SAR.
        raw=function((ROOT/'c/render.c').read_text(),'c_LoadCurrentLevelState')
        fragment=raw[raw.index('    sub16(r,r->ax,0x17e0'):raw.index('    W(WaterY32')]
        s+=fragment+check('session_water_cap(v)==r->ax','actual unsigned water cap')
        s+='SessionPlayerSeed x=session_player_x(v),y=session_player_y(v);'
        s+=check('x.fixed==(uint16_t)(v-512u) && x.pixel==sar((uint16_t)(v-512u),5) && y.fixed==(uint16_t)(v-320u) && y.pixel==sar((uint16_t)(v-320u),5)','full raw player seeds and signed shifts')
        s+=check('session_loader_mode_key(v)==(uint16_t)((v-1u)*2u) && session_loader_level_key(v)==(uint16_t)(v*2u)','full word keys including wrap')
        s+=check('session_record_previous(v)==(uint16_t)(v-2u) && session_record_more(v)==(!(v&0x8000u)) && session_prewarm_previous(v)==(uint16_t)(v-1u)','backward copy, rain slot and 577 prewarm signed seams')
        s+=check('session_copy_next(v,0)==(uint16_t)(v+2u) && session_copy_next(v,1)==(uint16_t)(v-2u)','both direction flags and pointer wrap')
        s+=check('session_load_value(LOAD_TRIO_SPEED,v,repeated)==(uint16_t)(sar(v,2)-repeated)','fresh second word and signed first word')
        for a,delta in [('STONE_X',8),('STONE_Y',11),('TREE_X',16),('TREE_Y',24),('TRIO_X',16),('TRIO_Y',22)]:s+=check(f'session_load_value(LOAD_{a},v,repeated)==(uint16_t)((v-{delta}u)*32u)','full wrapped '+a)
        s+=check('session_load_value(LOAD_DINO_X,v,repeated)==(uint16_t)(v*32u) && session_load_value(LOAD_DINO_Y,v,repeated)==(uint16_t)(v-704u)','dino scale seam')
    elif key=='display-byte':
        s+='uint8_t input;Regs regs,*r=&regs;set_al(r,(uint8_t)(input+11));cmp8(r,(uint8_t)r->ax,100);if((uint8_t)r->ax>=100)set_al(r,(uint8_t)(r->ax-100));'
        s+=check('session_display_byte(input)==(uint8_t)r->ax','all 256 cached byte values; wrap before one subtraction')
        s+='uint16_t players;const uint16_t one[]={33,118,177,208,224,244,290,0,0};const uint16_t two[]={33,114,169,199,215,232,305,258,274};for(unsigned i=0;i<9;i++){'+check('session_display_layout(players,i)==(players==2?two[i]:one[i])','all player-count words and HUD layout outputs')+'}'
        s+=check('session_reset_value(0)==3 && session_reset_value(1)==1 && session_reset_value(2)==0 && session_reset_value(3)==0','reset publishes only original lives, multiplier and score values')
    elif key=='display-score':
        s+='uint32_t input;Regs regs,*r=&regs;r->ax=(uint16_t)input;r->dx=(uint16_t)(input>>16);'
        b=function((ROOT/'c/render.c').read_text(),'c_InitializeLevelDisplay');start=b.index('    r->ax=add16(r,r->ax,0xb207');end=b.index('    W(HudCachedScoreLow',start)
        s+=b[start:end]+check('session_display_score(input)==((uint32_t)r->ax|((uint32_t)r->dx<<16))','full 32-bit score, carry, strict threshold and single subtraction')
    elif key=='password':
        s+='SessionPassword p;uint8_t candidate,editor;uint16_t length,misses,level;p.length=length;p.misses=misses;p.level=level;int different=session_password_compare(&p,candidate,editor);'
        s+=check('p.length==(uint16_t)(length+1u) && p.misses==(uint16_t)(misses-(candidate!=editor)) && p.level==level && different==(candidate!=editor)','word mismatch decrement and full length wrap')
        s+=check('session_password_needs_padding(&p)==(p.length<20) && session_password_has_misses(&p)==(p.misses!=0)','unsigned padding and zero mismatch word')
        s+=check('session_password_selected(&p,1)==0 && session_password_selected(&p,0)==level','default sentinel and selected level are consumed outputs')
        s+=check('session_password_byte(candidate)==(!candidate?PASSWORD_END:candidate==255?PASSWORD_DEFAULT:PASSWORD_MORE)','all sentinel byte values')
    elif key.startswith('render-'):
        s+='SessionRenderView v;uint8_t enabled;SessionRenderView before=v;SessionRenderResult erase=session_erase_layer(v),draw=session_draw_layer(v,enabled);'
        if key=='render-output':
            s+=check('erase.store_erase && erase.erase_sprite==v.sprite && erase.restore==(v.erase_sprite!=65535) && erase.sprite==v.erase_sprite && erase.x==v.previous_x && erase.y==v.previous_y','erase unconditionally advances history and has no clipping')
            s+=check('draw.store_position==(enabled && v.sprite!=65535)','draw identity selection')
            s+='if(draw.store_position){'+check('draw.previous_x==v.pixel_x && draw.previous_y==v.pixel_y && draw.pixel_x==sar(v.position.x32,5) && draw.pixel_y==sar(v.position.y32,5) && draw.draw==((int16_t)draw.pixel_y<192) && draw.sprite==v.sprite && draw.x==draw.pixel_x && draw.y==draw.pixel_y','signed upper clip only; cached pre-update pixels')+'}'
        elif key=='render-frame':
            for f in ['position.x32','position.y32','sprite','erase_sprite','pixel_x','pixel_y','previous_x','previous_y']:s+=check('v.'+f+'==before.'+f,'every input field framed')
        else:
            s+='SessionRenderView other;other.position=v.position;other.sprite=v.sprite;other.pixel_x=v.pixel_x;other.pixel_y=v.pixel_y;SessionRenderResult d=session_draw_layer(other,enabled);'
            for f in ['store_position','draw','pixel_x','pixel_y','previous_x','previous_y','x','y','sprite']:s+=check('draw.'+f+'==d.'+f,'old erase and previous cache do not affect draw')
    elif key=='session-order':
        s+='SessionWorld w={0};w.fade_level=257;w.fade_rate=2;w.player_bytes=4;w.player_count=2;uint8_t rain;w.rain=rain;SessionProcess p;session_begin(&p);p.phase=SP_FRAME_BEGIN;'
        actions='WAIT_RETRACE HUD ERASE_PLAYER_BEGIN ERASE_PLAYER ERASE_PLAYER_NEXT ERASE_PLAYER ERASE_PLAYER_NEXT ERASE_ACTORS ERASE_ENEMIES ERASE_ITEMS RESTORE_RAIN ADVANCE_WATER IO_POINT POLL_CONTROLS ESCAPE MOVE_BEGIN MOVE_PLAYER MOVE_NEXT MOVE_PLAYER MOVE_NEXT UPDATE_ACTORS UPDATE_ENEMIES UPDATE_ITEMS DRAW_ACTORS DRAW_ENEMIES_BACK DRAW_PLAYER_BEGIN DRAW_PLAYER DRAW_PLAYER_NEXT DRAW_PLAYER DRAW_PLAYER_NEXT DRAW_ENEMIES_FRONT DRAW_ITEMS DRAW_OVERLAYS ADVANCE_RAIN DRAW_RAIN DRAW_WATER SWAP_PAGE'.split()
        s+='const SessionAction order[]={'+','.join('SESSION_'+a for a in actions)+'};for(unsigned i=0;i<sizeof(order)/sizeof(order[0]);i++){if(!rain && (order[i]==SESSION_RESTORE_RAIN || order[i]==SESSION_ADVANCE_RAIN || order[i]==SESSION_DRAW_RAIN))continue;SessionRequest e=session_next(&p,w);'
        s+=check('e.action==order[i]','two-player frame order, both rain branches, swap after water draw')+check('session_acknowledge(&p,e.action,w)','frame seam acknowledgement')+'}'
        s+=check('p.phase==SP_FRAME_BEGIN && p.completed_frames==1 && !p.pending','exact frame pacing continuation')
    elif key.startswith('session-'):
        s+='SessionProcess p;SessionWorld w;unsigned phase;__CPROVER_assume(phase<SP_DONE);p.phase=(SessionPhase)phase;p.pending=p.failed=0;SessionProcess before=p;SessionWorld original=w;SessionRequest e=session_next(&p,w);'
        if key=='session-frame':
            for f in ['phase','player_cursor','selected_level','completed_frames']:s+=check('p.'+f+'==before.'+f,'next only publishes request and protocol state')
            for f in ['fade_level','fade_rate','palette_reply','player_bytes','player_count','level','level_limit','password_reply','lives','completion','rain','scan']:s+=check('w.'+f+'==original.'+f,'world is framed')
        elif key=='session-dependence':
            s+='SessionWorld other=w;uint16_t unused;other.password_reply=unused;SessionProcess q=before;SessionRequest f=session_next(&q,other);'
            for f in ['action','index','value','other','decision']:s+=check('e.'+f+'==f.'+f,'password reply only read on acknowledgement')
        else:
            s+=check('e.action!=SESSION_INVALID && e.action!=SESSION_FINISHED && p.pending && !p.failed','all admitted phases publish one request')
            s+='if(phase==SP_FRAME_BEGIN){'+check('e.action==((int16_t)w.fade_level<0?SESSION_STOP_LEVEL_MUSIC:(int16_t)w.fade_level<=256?SESSION_FADE_UPLOAD:SESSION_WAIT_RETRACE)','signed fade branch seam')+'}'
            s+='if(phase==SP_DECREMENT_LIVES){'+check('e.value==(uint8_t)(w.lives-1u) && e.decision==(e.value!=0 && !(e.value&128))','DEC8 death restart condition')+'}'
            s+='if(phase==SP_TEST_LEVEL_LIMIT){'+check('e.index==(uint16_t)(w.player_bytes-2u) && e.decision==(w.level<w.level_limit)','unsigned postincrement level limit seam')+'}'
            s+='if(phase==SP_MOVE_NEXT){'+check('e.index==(uint16_t)(before.player_cursor+2u) && e.decision==(e.index==w.player_count)','retained equality-only movement loop')+'}'
            s+='if(phase==SP_ERASE_PLAYER_NEXT || phase==SP_DRAW_PLAYER_NEXT){'+check('e.index==(uint16_t)(before.player_cursor+2u) && e.decision==(e.index!=w.player_bytes)','equality-only page render loop')+'}'
            s+='if(phase==SP_FADE_ADVANCE){'+check('e.value==(uint16_t)(w.palette_reply+w.fade_rate)','raw returned palette count plus fresh fade step')+'}'
            s+='if(phase==SP_ESCAPE){'+check('e.decision==(w.scan==1) && e.index==((int16_t)w.fade_rate>=0) && e.value==(uint16_t)(w.fade_level-2u) && e.other==65534','escape writes and signed fade-direction guard')+'}'
            s+='if(phase==SP_MOVE_BEGIN){'+check('e.decision==((int16_t)w.fade_level>192 || (int16_t)w.fade_rate<=0)','raw signed movement enable thresholds')+'}'
            s+='if(phase==SP_SELECT_LEVEL){'+check('e.value==before.selected_level','selected password level is a published output')+'}'
            s+='if(phase==SP_START_MUSIC){'+check('e.value==165','original session track selector')+'}'
            s+='if(phase==SP_STOP_INITIAL_MUSIC || phase==SP_STOP_LEVEL_MUSIC){'+check('e.value==17','original stop selector')+'}'
            s+='if(phase==SP_INCREMENT_LEVEL){'+check('e.value==(uint16_t)(w.level+1u)','full level word wrap before the limit read')+'}'
            s+='if(phase==SP_OUTCOME){'+check('e.decision==((w.completion&128u)!=0)','completion marker sign bit')+'}'
            s+=check('session_acknowledge(&p,e.action,w) && !p.pending && !p.failed','every published action has a continuation')
            s+='if(phase==SP_INITIALIZE_LEVEL){'+check('p.completed_frames==0','the literal verification guard resets at every level')+'}'
            s+='else if(phase==SP_SWAP_PAGE){'+check('p.completed_frames==(uint32_t)(before.completed_frames+1u)','one completed frame counted after swap')+'}'
            s+='else{'+check('p.completed_frames==before.completed_frames','other cuts do not advance frame pacing')+'}'
            s+='if(phase==SP_POLL_CONTROLS){'+check('p.phase==(w.scan==25?SP_PAUSE_RELEASE:SP_ESCAPE)','pause entry uses actual input reply')+'}'
            s+='if(phase==SP_PAUSE_RELEASE){'+check('p.phase==(w.scan==153?SP_PAUSE_MAKE:SP_PAUSE_RELEASE)','pause first waits for exact break code')+'}'
            s+='if(phase==SP_PAUSE_MAKE){'+check('p.phase==((w.scan&128u)?SP_PAUSE_MAKE:SP_PAUSE_BREAK)','pause waits for make')+'}'
            s+='if(phase==SP_PAUSE_BREAK){'+check('p.phase==((w.scan&128u)?SP_ESCAPE:SP_PAUSE_BREAK)','pause waits for break then shares escape test')+'}'
    elif key.startswith('load-'):
        # A fixed record stage, with the other stages abstracted by their real
        # typed outputs. Never make all RAM or all physical slots symbolic.
        s+='SessionLoadRecord p;unsigned family,cursor,kind;__CPROVER_assume(family<3);__CPROVER_assume(kind<6);session_load_begin(&p,(SessionLoadFamily)family,0);'
        s+='if(family==0){__CPROVER_assume(kind==LOAD_ORDINARY && cursor<18);}else if(family==1){__CPROVER_assume((kind==LOAD_ORDINARY || kind==LOAD_STONE) && cursor<(kind==LOAD_STONE?17u:13u));}else{__CPROVER_assume(kind>=LOAD_TREE && cursor<(kind==LOAD_TREE?12u:kind==LOAD_BIRD?11u:kind==LOAD_DINO?10u:15u));}'
        s+='p.cursor=(uint8_t)cursor;p.record_class=(SessionLoadClass)kind;uint16_t sample,repeated,platform,slot;p.sample=sample;p.repeat=repeated;p.platform=platform;p.slot=slot;SessionLoadRecord before=p;SessionLoadRequest e=session_load_next(&p);'
        if key=='load-frame':
            for f in ['family','record_class','slot','sample','repeat','descriptor','platform','cursor','list_end','done']:s+=check('p.'+f+'==before.'+f,'every decoding input is framed by next')
        elif key=='load-dependence':
            s+='SessionLoadRecord q=before;uint16_t other;q.descriptor=other;SessionLoadRequest f=session_load_next(&q);'
            for f in ['action','field','arithmetic','slot','index','value']:s+=check('e.'+f+'==f.'+f,'cached descriptor is not a second input to decoding decisions')
        else:
            s+=check('e.action!=LOAD_INVALID && e.slot==slot && p.pending','every admitted branch stage emits exactly one slot-bound effect')
            s+='if(e.action==LOAD_READ_DESCRIPTOR){'+check('e.index==(kind==LOAD_STONE?16:8)','stone primary descriptor callback offset')+'}'
            s+='if(e.action==LOAD_READ_SPAWN || e.action==LOAD_READ_HEIGHT){'+check('e.index==(uint16_t)(platform*2u)','full wrapped platform index binding')+'}'
            s+='if(e.action==LOAD_CALLBACK){'+check('e.value==kind','opaque callback role is published')+'}'
            s+='uint16_t reply;'+check('session_load_accept(&p,e.action,reply,(SessionLoadClass)kind) && !p.pending && !p.failed','every decoder stage consumes exact action')
    elif key=='display-order':
        s+='SessionDisplayProcess p;session_display_begin(&p);unsigned i;for(i=0;i<13;i++){'+check('session_display_next(&p)==i && session_display_consume(&p,i)','all thirteen display services ordered')+'}'+check('session_display_complete(&p) && session_display_next(&p)==13','complete display with no leftover service')
    else:
        s+='SessionProcess p;SessionWorld w;session_begin(&p);SessionRequest e=session_next(&p,w);'+check('!session_complete(&p)','pending request prevents completion')
        s+='SessionRequest refused=session_next(&p,w);'+check('refused.action==SESSION_INVALID && p.failed && !session_acknowledge(&p,e.action,w)','unconsumed request cannot be overwritten')
        s+='SessionLoadRecord l;session_load_begin(&l,LOAD_ACTORS,0);SessionLoadRequest a=session_load_next(&l);(void)a;SessionLoadRequest b=session_load_next(&l);'+check('b.action==LOAD_INVALID && l.failed','decoder rejects unconsumed request')
    return s+'return 0;}\n'

def main():
    p=argparse.ArgumentParser();p.add_argument('key',choices=KEYS);p.add_argument('--reachability',action='store_true');a=p.parse_args()
    folder=OUT/('proof-reach' if a.reachability else 'proofs')/a.key;folder.mkdir(parents=True,exist_ok=True)
    code=common()+body(a.key)
    if a.reachability:code=code.replace('return 0;}','CHECK(0,"REACHED_FINAL_COMPARISON");return 0;}')
    h=folder/'harness.c';h.write_text(code)
    r=cbmc(h,folder,[ROOT/'native/session.c',ROOT/'native/session.h',ROOT/'native/lifecycle.c',ROOT/'native/lifecycle.h',ROOT/'c/render.c',ROOT/'c/scene.c',ROOT/'c/ugh.h',ROOT/'c/ugh_sym.h',ROOT/'verif/sequencing_proof.py'],unwind=48 if a.key=='session-order' else 18,timeout=600)
    print(a.key,r['result'],r['seconds'],flush=True)
    if a.reachability:assert r['result']=='FAIL' and r['failures'] and all('REACHED_FINAL_COMPARISON' in str(f) for f in r['failures'])
    else:assert r['result']=='PASS',r.get('failures')
if __name__=='__main__':main()
