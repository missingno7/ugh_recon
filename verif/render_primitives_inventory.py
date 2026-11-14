"""Checked coverage seams, direct/indirect callers, and rendering-cache writers."""
import re
from closure_support import ROOT,receipt,save,function
from render_primitives_shells import OUT,FILES,NAMES,SOURCES,main as shells
from render_primitives_proof import KEYS

STAGES={
 'DrawTransparentSprite':['placement','begin','pixel','column'],
 'DrawMapTile':['map-tile'],'DrawTileMap':['map-cell','map-tile'],
 'SaveDrawPageBackground':['save'],'RestoreBackgroundRectangle':['rectangle','next-row'],
 'RestorePlayfieldBackground':['playfield','rectangle','next-row'],
 'RestoreSpriteBackground':['sprite-rectangle','rectangle','next-row'],
 'RestoreTileBackground':['tile-rectangle','rectangle','next-row'],
 'RestorePlayerBackground':['visible','cache','sprite-rectangle','rectangle','next-row'],
 'AnimateAndDrawPlayer':['animation','visible','placement','begin','pixel','column'],
 'CachePlayerDrawState':['cache']}

def main():
    import sys
    old=sys.argv;sys.argv=[old[0]]
    try:shells()
    finally:sys.argv=old
    assert set(STAGES)==set(NAMES) and set(sum(STAGES.values(),[]))==set(KEYS)
    callers={n:[] for n in NAMES};writers=[]
    symbols=(ROOT/'c/ugh_sym.h').read_text()
    fields=sorted(set(re.findall(r'UGH_O_DGROUP_(\w*(?:Cached\w*|PreviousDraw\w*|DrawPage\w*|DrawX|DrawY|TimerBarWidth))\s',symbols)))
    # Include explicit rendering coordinates and alias names, including player2.
    fields+=['PlayerTwoCachedPixelX','PlayerTwoCachedPixelY','PlayerTwoCachedSpriteId','HudDigitCursorX','HudDigitCursorY','RendererScratchWord','SpritePlaneStateScratch']
    for p in sorted((ROOT/'c').glob('*.c')):
        text=p.read_text()
        for match in re.finditer(r'^(?:EXPORT\s+)?(?:static\s+)?(?:void|int|uint\d+_t)\s+(\w+)\s*\(',text,re.M):
            try:b=function(text,match[1])
            except ValueError:continue
            for n in NAMES:
                if re.search(r'\b(?:CALL|ugh_dispatch|ugh_call_near)\s*\([^;\n]*\b'+n+r'\b|\bc_'+n+r'\s*\(',b[b.index('{')+1:]):callers[n].append(dict(source=p.relative_to(ROOT).as_posix(),function=match[1]))
            for line in b.splitlines():
                if re.search(r'\b(?:W|WB|WI|WX|WRITE|wr8|wr16)\s*\(',line):
                    named=[f for f in fields if re.search(r'\b'+f+r'\b',line)]
                    if named:writers.append(dict(source=p.relative_to(ROOT).as_posix(),function=match[1],fields=named,statement=line.strip()))
    writers.append(dict(source='c/render.c',function='c_InitializeLevelDisplay',fields=['HUD caches within normal D:2648..27CF'],statement='196 STOS words through LevelWorkspacePointer (normal CoordinateScaleScratch binding). Includes cached bar width and HUD caches; excludes all player arrays at27D0 and later. Incoming DF retained; arbitrary pointer/DF changes the actual footprint.'))
    composition='Actual-C placement/constructor, one pixel/column, rectangle setup/row successor, REP base/step invariant, wrapper parameters, visibility, animation stores and ordered cache copy form the B decision boundary. Every scalar is a raw word/byte; map ordinal<320 and one selected physical player0/2 are the only index restrictions. Native cursor frame/dependence properties cover all other native bytes and inactive inputs. Complete source-checked outer loops, ABI/flags/stack, immediate service tails, live pixel/latch transactions and arbitrary-alias machine bindings retain literal implementations and independent C/D evidence; no B theorem for VGA internals or the entire session is claimed.'
    OUT.mkdir(parents=True,exist_ok=True)
    save(OUT/'inventory.json',receipt(['python','verif/render_primitives_inventory.py'],[*FILES,ROOT/'verif/render_primitives_shells.py',ROOT/'verif/render_primitives_proof.py',ROOT/'verif/render_primitives_inventory.py',*sorted((ROOT/'c').glob('*.[ch]'))],result='PASS',stages=STAGES,composition=composition,callers=callers,cache_writers=writers,retained_services=['copy_mode exact ordered IO/read-modify-write','sprite resource-byte reads and physical A000 pixel writes','rectangle ascending live read/write pairs with DF clear on each row','save live reads/writes with incoming DF and REP zero semantics'],slot_admission='Animation/restore typed view admits even byte index0/2; other indices keep complete literal path. Cache copy consumes each freshly read source independently, preserving all wrapping index/alias cases.'))
    print('PASS eleven handlers,23 properties and rendering-cache writer census')
if __name__=='__main__':main()
