"""Literal branch-stage cuts and their declared equality seams."""
import re
from closure_support import ROOT,function

def pieces():
    source=(ROOT/'c/scene.c').read_text();body=function(source,'c_RunScriptedDemo');result={}
    def section(a,b):
        start=body.index(a);end=body.index(b,start);return body[start:end]
    def add(name,phase,fragment,kind='DEMO_PRESENT_RUN',seam=''):
        result[name]=dict(phase=phase,kind=kind,fragment=fragment,seam=seam)
    add('initialize','DP_INITIALIZE','CALL(InitializeDemoScripts,G(RunScriptedDemo)+3);')
    add('clear-before-poll','DP_CLEAR_EXIT',section('r->ax=logic(r,0,16); W(DemoExitCode','    for(unsigned budget='))
    add('frame-header','DP_LOOP',section('r->cx=R(ScreenFadeLevel);','        CALL(EraseDemoSprites'))
    add('palette-result','DP_PALETTE_AFTER','r->cx=add16(r,r->cx,R(ScreenFadeStep),0); W(ScreenFadeLevel,r->cx);',seam='plan.observed.palette_work=r->cx;')
    for name,target,ret,phase in [('erase','EraseDemoSprites','0x3f','DP_ERASE'),('advance','AdvanceDemoScripts','0x50','DP_ADVANCE'),('draw','DrawDemoSprites','0x53','DP_DRAW'),('swap','SwapAndDisplayVgaPage','0x56','DP_SWAP'),('completion-test','TestAllDemoScriptsFinished','0x59','DP_TEST')]:
        fragment=f'CALL({target},G(RunScriptedDemo)+{ret});';assert fragment in body;add(name,phase,fragment)
    add('water-cut','DP_WATER',section('sub16(r,R(WaterYPixels),192,0);','        CALL(DrawDemoSprites'))
    fade=section('sub16(r,R(ScreenFadeStep),0,0);','    }\n    return UGH_BUDGET;')
    inputs=section('if(!(r->flags&CF)) {','        sub16(r,R(ScreenFadeStep),0,0);')
    add('finished-result','DP_TEST_AFTER',inputs+fade,seam='plan.observed.finished=(r->flags&CF)!=0;')
    a=inputs.index('if(r->flags&ZF) {');b=inputs.rindex('\n        }');joystick=inputs[a:b]
    add('joystick-result','DP_JOYSTICK_AFTER',joystick+fade,seam='plan.observed.joystick_idle=(r->flags&ZF)!=0;')
    keyboard=inputs[inputs.index('logic(r,r->ax>>8,8);'):inputs.index('            } else W(DemoExitCode,0);')]
    add('keyboard-result','DP_KEYBOARD_AFTER',keyboard+fade,seam='plan.observed.key_word=r->ax;')
    add('fade-check','DP_FADE_CHECK',fade)
    add('fade-level','DP_FADE_LEVEL','W(ScreenFadeLevel,add16(r,R(ScreenFadeLevel),r->ax,0));',seam='r->ax=65532u;')
    for name,entry,kind in [('reveal','PlaySpriteRevealDemo','DEMO_PRESENT_REVEAL'),('pregame','PlayPreGameDemo','DEMO_PRESENT_PREGAME'),('attract','PlayAttractDemo','DEMO_PRESENT_ATTRACT'),('completion','PlayGameCompletionDemo','DEMO_PRESENT_COMPLETION')]:
        full=function(source,'c_'+entry);inner=full[full.index('{')+1:full.rfind('}')]
        add(name+'-prepare','DP_PREPARE',inner,kind)
        start=inner.index('r->si=D(') if name!='completion' else inner.index('push(r,0x11);')
        add(name+'-prepared','DP_MUSIC_STOP' if name=='completion' else 'DP_VECTOR',inner[start:],kind)
        if name=='reveal':
            add('reveal-cleanup','DP_REVEAL_X',inner[inner.index('push(r,r->flags);'):],kind)
            add('reveal-return','DP_WRAPPER_DONE','r->flags=pop(r); return UGH_OK;',kind,seam='r->sp=0xffe;')
        if name=='completion':
            start=inner.index('r->sp=add16(r,r->sp,2,0);');add('completion-stopped','DP_MUSIC_START','int st;\n'+inner[start:],kind,seam='r->sp=0xffe;')
            start=inner.index('r->sp=add16(r,r->sp,8,0);');add('completion-started','DP_VECTOR',inner[start:],kind,seam='r->sp=0xff8;')
    return result

def modern(fragment):
    text=fragment
    text=re.sub(r'r->si=D\((DemoTable_\w+)\);',r'r->si=dp_vector(r,&plan,D(\1));',text)
    text=text.replace('scene_far_call(r,','scene_far_call(r,&plan,')
    text=text.replace('push(r,0x11);','push(r,dp_music_value(r,&plan,DP_SERVICE_MUSIC_STOP,0x11));')
    text=text.replace('push(r,0xa5);','push(r,dp_music_value(r,&plan,DP_SERVICE_MUSIC_START,0xa5));')
    text=text.replace('return c_RunScriptedDemo(r);','return dp_tail(r,&plan,1);')
    text=text.replace('return ugh_dispatch(r->cs,G(RunScriptedDemo),r);','return dp_tail(r,&plan,0);')
    text=text.replace('continue;','{dp_repeat(r,&plan);return UGH_OK;}')
    text=text.replace('return UGH_OK;','dp_finish(r,&plan);return UGH_OK;') if 'continue;' not in fragment else text.replace('return UGH_OK; }','dp_finish(r,&plan);return UGH_OK; }')
    # The last store is the natural outer-loop backedge, even in a cut beginning
    # after the preceding step store. No iteration counter/flags are invented.
    final='W(ScreenFadeLevel,add16(r,R(ScreenFadeLevel),r->ax,0));'
    if final in text:text=text.replace(final,final+'dp_repeat(r,&plan);')
    return text

def reference(fragment):
    text=fragment.replace('continue;','return UGH_OK;')
    for helper in ['push','pop','scene_far_call']:text=re.sub(r'\b'+helper+r'\b','reference_'+helper,text)
    text=text.replace('return c_RunScriptedDemo(r);','return ps_direct(r);')
    return text
