"""Behavioral controls in private copies; compile errors never earn detection."""
from closure_support import ROOT,save
from render_history_build import OUT
from render_history_cases import run
def main():
    text=(ROOT/'native/actor_render.c').read_text()
    changes={
      'logical-sar':('((value & 32768u) ? 63488u : 0)','0'),
      'new-position-as-previous':('history->previous_x = history->pixel_x;','history->previous_x = render_pixel(input->position.x32);'),
      'hidden-clears-cache':('if(input->sprite == (operation == ACTOR_RENDER_GAME_DRAW ? ACTOR_HIDDEN_SPRITE : DEMO_HIDDEN_SPRITE)) break;','if(input->sprite == (operation == ACTOR_RENDER_GAME_DRAW ? ACTOR_HIDDEN_SPRITE : DEMO_HIDDEN_SPRITE)) {history->pixel_x=0;break;}'),
      'game-lower-equality':('render_signed(history->pixel_y) <= -11','render_signed(history->pixel_y) < -11'),
      'game-upper-equality':('render_signed(history->pixel_y) >= 192','render_signed(history->pixel_y) > 192'),
      'demo-upper-x-equality':('render_signed(history->pixel_x) >= 320','render_signed(history->pixel_x) > 320'),
      'unsigned-erase-y':('render_signed(history->previous_y) < 192','history->previous_y < 192u'),
      'wrong-erase-generation':('history->previous_x,history->previous_y,old','history->pixel_x,history->pixel_y,old'),
      'demo-erase-hidden':('old != DEMO_HIDDEN_SPRITE','old != ACTOR_HIDDEN_SPRITE'),
      'unconditional-overlay-swap':('if(old == ACTOR_HIDDEN_SPRITE) break;','if(old == ACTOR_HIDDEN_SPRITE) {history->erase_overlay_sprite=input->overlay_sprite;render_store(&result,ACTOR_RENDER_ERASE_OVERLAY,input->overlay_sprite);break;}'),
      'overlay-clip':('input->sprite != ACTOR_HIDDEN_SPRITE && input->overlay_sprite != ACTOR_HIDDEN_SPRITE','input->sprite != ACTOR_HIDDEN_SPRITE && input->overlay_sprite != ACTOR_HIDDEN_SPRITE && render_signed(history->pixel_y)<192'),
      'overlay-offset-wrap':('(uint16_t)(history->pixel_y-13u)','(uint16_t)(history->pixel_y-12u)'),
      'request-order':('render_store(&result,ACTOR_RENDER_ERASE_OVERLAY,input->overlay_sprite);','render_store(&result,ACTOR_RENDER_ERASE_OVERLAY,input->overlay_sprite);\n            if(result.count==3) {ActorRenderEvent e=result.events[1];result.events[1]=result.events[2];result.events[2]=e;}'),
      'reset-clears-overlay':('case ACTOR_RENDER_RESET:','case ACTOR_RENDER_RESET:\n        history->erase_overlay_sprite=65535u;'),
      'reset-keeps-simulation-sprite':('render_store(&result,ACTOR_RENDER_CURRENT_SPRITE,ACTOR_HIDDEN_SPRITE);',''),
      'unconsumed-extra-event':('    return result;','    if(operation==ACTOR_RENDER_GAME_OVERLAY) render_store(&result,ACTOR_RENDER_PIXEL_X,history->pixel_x);\n    return result;'),
      'private-unpublished-history':('    return result;','    if(operation==ACTOR_RENDER_RESET) history->previous_y^=1u;\n    return result;'),
    }
    rows=[]
    for name,(old,new) in changes.items():
        assert old in text,name;folder=OUT/'mutants'/name;folder.mkdir(parents=True,exist_ok=True);path=folder/'actor_render.c';path.write_text(text.replace(old,new))
        value,result=run(folder,mutant=path);assert value.returncode==23,(name,value.returncode,value.stdout,value.stderr)
        result.update(result='DETECTED',mutant=name);save(folder/'result.json',result);rows.append(result);print(name+' DETECTED',flush=True)
    for name,change in {
      'native-request-only':('ActorRenderEvent event=ar_next(plan,restore?ACTOR_RENDER_RESTORE:ACTOR_RENDER_DRAW);','ActorRenderEvent event=ar_next(plan,restore?ACTOR_RENDER_RESTORE:ACTOR_RENDER_DRAW);event.x^=1u;'),
      'native-store-only':('ActorRenderEvent event=ar_next(plan,ACTOR_RENDER_STORE);','ActorRenderEvent event=ar_next(plan,ACTOR_RENDER_STORE);event.value^=1u;'),
    }.items():
        folder=OUT/'mutants'/name;folder.mkdir(parents=True,exist_ok=True);value,result=run(folder,bridge_mutant=change);assert value.returncode==23,(name,value.returncode)
        result.update(result='DETECTED',mutant=name);save(folder/'result.json',result);rows.append(result);print(name+' DETECTED',flush=True)
    save(OUT/'mutants.json',rows)
if __name__=='__main__':main()
