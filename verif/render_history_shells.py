"""Check/generate retained L1 shells and exact inline actor partitions."""
import re,sys
from pathlib import Path
from closure_support import ROOT,function
BRIDGE=ROOT/'native/bridge/actor_render_bridge.c'
NAMES=['RunGameFromPassword','EraseDemoSprites','DrawDemoSprites','ResetSpriteEraseState']
OPS=['GAME_ERASE','GAME_DRAW','GAME_OVERLAY','DEMO_ERASE','DEMO_DRAW','RESET']

def loop_body(text,start):
    begin=text.index('{',start); depth=1;end=begin+1
    while depth:
        if text[end]=='{':depth+=1
        if text[end]=='}':depth-=1
        end+=1
    return begin+1,end-1

def partitions():
    scene=(ROOT/'c/scene.c').read_text();demo=(ROOT/'c/demo_scripts.c').read_text()
    game=function(scene,'c_RunGameFromPassword');parts={}
    loops=list(re.finditer(r'for\(unsigned slots=0;slots<32768;slots\+\+\)',game))
    actors=[]
    for match in loops:
        a,b=loop_body(game,match.start())
        if 'RX(ActorDescriptors,r->si)' in game[a:b]:actors.append((a,b))
    assert len(actors)==3
    for op,(a,b) in zip(OPS[:3],actors):
        body=game[a:b];head='\n            sub16(r,RX(ActorDescriptors,r->si),0xffff,0); if(r->flags&ZF) break;'
        tail='\n            r->si=add16(r,r->si,2,0); if(slots==32767) return UGH_BUDGET;\n        '
        assert body.startswith(head) and body.endswith(tail)
        parts[op]=body[len(head):-len(tail)]
    for op,name in [('DEMO_ERASE','EraseDemoSprites'),('DEMO_DRAW','DrawDemoSprites')]:
        body=function(scene,'c_'+name);a=body.index('        r->ax=RX(ActorSpriteIds,r->si);');b=body.index('        r->si=add16(r,r->si,2,0);',a)
        parts[op]=body[a:b]
    reset=function(demo,'c_ResetSpriteEraseState');a=reset.index('        wr16(r->ds,(uint16_t)(D(ActorSpriteIds)');b=reset.index('        r->si=sub16(r,r->si,2,0);',a)
    parts['RESET']=reset[a:b]
    return parts

def adapt(text):
    text=re.sub(r'WX\((Actor\w+),r->si,([^;]+)\);',r'ar_write(r,&plan,(uint16_t)(D(\1)+r->si),\2);',text)
    text=re.sub(r'wr16\(r->ds,\(uint16_t\)\(D\((Actor\w+)\)\+r->si\),r->ax\);',r'ar_write(r,&plan,(uint16_t)(D(\1)+r->si),r->ax);',text)
    text=re.sub(r'CALL\((RestoreSpriteBackground|DrawTransparentSprite),([^;]+)\);',r'AR_CALL(\1,\2);',text)
    return text

def gameplay_cuts(native=False):
    game=function((ROOT/'c/scene.c').read_text(),'c_RunGameFromPassword');loops=[]
    for match in re.finditer(r'for\(unsigned slots=0;slots<32768;slots\+\+\)',game):
        a,b=loop_body(game,match.start())
        if 'RX(ActorDescriptors,r->si)' in game[a:b]:loops.append(game[match.start():b+1])
    assert len(loops)==3;out=''
    for op,body in zip(OPS[:3],loops):
        if native:
            fragment=partitions()[op];assert body.count(fragment)==1
            body=body.replace(fragment,'\n{RenderPlan plan;ar_open(r,&plan,ACTOR_RENDER_'+op+');\n'+adapt(fragment)+'\nar_finish(r,&plan);}\n')
        out+='EXPORT int render_history_'+op+'(Regs *r) {r->si=logic(r,0,16);'+body+'return UGH_OK;}\n'
    return out

def generated():
    scene=(ROOT/'c/scene.c').read_text();demo=(ROOT/'c/demo_scripts.c').read_text();parts=partitions();out=''
    for helper in ['sar','push','scene_far_call','draw_enemy_layer']:out+=function(scene,helper)+'\n'
    for name in NAMES:
        text=function(demo if name=='ResetSpriteEraseState' else scene,'c_'+name)
        for op,fragment in parts.items():
            if fragment not in text:continue
            assert text.count(fragment)==1,(name,op)
            inserted='\n        { RenderPlan plan; ar_open(r,&plan,ACTOR_RENDER_'+op+');\n'+adapt(fragment)+'\n          ar_finish(r,&plan); }\n'
            text=text.replace(fragment,inserted)
        out+=text+'\n'
    return out

def main():
    marker='/* BEGIN CHECKED L1 SHELLS */\n';prefix=BRIDGE.read_text().split(marker)[0];expected=prefix+marker+generated()
    if '--write' in sys.argv:BRIDGE.write_text(expected)
    else:assert BRIDGE.read_text()==expected,'retained renderer shell drift'
    print('PASS six actual actor partitions and four full retained shells')
if __name__=='__main__':main()
