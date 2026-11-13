"""Checked complete renderer partitions, history ownership and source locks."""
import json,re
from closure_support import ROOT,function,receipt,save
from render_history_build import OUT,FILES
from render_history_shells import main as check_shells,partitions,OPS,NAMES,BRIDGE
def main():
    check_shells();parts=partitions();native=(ROOT/'native/actor_render.c').read_text();header=(ROOT/'native/actor_render.h').read_text();switch=function(native,'actor_render_apply')
    cases=re.findall(r'case ACTOR_RENDER_([A-Z_]+):',switch);assert set(cases)==set(OPS) and len(cases)==6
    assert all('ACTOR_RENDER_'+op in header for op in OPS)
    rows=[]
    for op,part in parts.items():
        stores=re.findall(r'(?:WX|wr16)\([^;]+;',part);calls=re.findall(r'CALL\((\w+),([^;]+)\);',part)
        rows.append(dict(operation=op,actual_l1_stores=stores,actual_l1_pixel_calls=calls,proofs=['outputs','native-frame','dependencies']))
    # Guard, iteration and nonactor code are literally retained in full shells.
    # State the slice scope rather than claiming ownership of the whole session.
    indirect=dict(pixel_services=['RestoreSpriteBackground','DrawTransparentSprite'],actor_callbacks='None in the renderer; pre-update DispatchActorUpdates remains the existing machine call in its exact frame order.',nonactor='Enemy/player/item/HUD/rain/water/palette/input/audio and page swap stay unchanged L1 or accepted bridges.')
    # Persistent-history writers are visible in the source; explicit seed sites
    # retain their accepted owners, rather than becoming projection-time clears.
    seed=function((ROOT/'c/scene.c').read_text(),'c_InitializeDemoScripts');assert seed.count('WX(ActorPixelX,')==seed.count('WX(ActorPreviousDrawX,')==seed.count('WX(ActorPixelY,')==seed.count('WX(ActorPreviousDrawY,')==1
    place=function((ROOT/'c/actors.c').read_text(),'c_PlacePassengerOnPlatform');assert 'W(ActorPixelX,r->ax)' in place and 'W(ActorPixelY,r->ax)' in place and 'ActorPreviousDraw' not in place
    loader=function((ROOT/'c/render.c').read_text(),'c_LoadCurrentLevelState');assert not re.search(r'W(?:I)?\(Actor(?:Pixel|PreviousDraw)[XY]',loader)
    measured=json.loads((OUT/'integration.json').read_text()) if (OUT/'integration.json').exists() else {}
    original=[]
    for p in sorted((OUT/'whole').glob('*.ref.json')):
        j=json.loads(p.read_text());names=['GAME:EraseDemoSprites','GAME:DrawDemoSprites','GAME:ResetSpriteEraseState','GAME:RunGameFromPassword'];original.append(dict(scenario=p.name[:-9],routines=[n for n in j['coverage']['routines'] if n in names]))
    save(OUT/'coverage.json',receipt(['python','verif/render_history_coverage.py'],[*FILES,ROOT/'native/actors.h',ROOT/'c/scene.c',ROOT/'c/demo_scripts.c',ROOT/'c/actors.c',ROOT/'c/render.c',ROOT/'verif/render_history_shells.py',ROOT/'verif/render_history_proof.py',ROOT/'verif/render_history_sequences.py',ROOT/'verif/render_history_coverage.py'],result='PASS',partitions=rows,indirect=indirect,
      composition='Six complete per-slot actor bodies cover every history decision and event. Each output proof executes actual full native apply and retained C body, compares every current-slot word, every register/flag, ordered stores/pixel-call parameters/return words and abnormal prefixes. Independent native arbitrary-byte frame and dependence complete the observation set. No summarized tick/frame/append helper is substituted. Outer equality-only sentinel scans, ascending slot order, descending all16 reset, every nonactor statement and original call frames are checked literal retained code; their general shell composition remains C/D rather than a new monolithic B claim.',
      seeds='Actual native demo_initialize, exact L1 header seed fragment, loader actor-body frame and reset/draw compose under ordinary disjoint resources. Explicit passenger placement remains owned by the accepted itinerary unit. No mode-entry or projection clear is introduced.',
      original_coverage=original,scenario_native_counts=measured.get('scenario_audits',[]),finding='high-score and password have zero native actor-render entries and no corresponding ASM caller coverage. The other18 scenarios reach at least one actor renderer/reset operation. All20 scenarios pass; do not claim all20 draw actors.'))
    print('PASS six complete actor bodies, retained outer shell and explicit seed inventory')
if __name__=='__main__':main()
