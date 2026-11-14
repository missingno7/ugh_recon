"""Actual C branch-stage properties; no model of VGA pixels is substituted."""
import argparse
from closure_support import ROOT,function
from render_primitives_shells import OUT,FILES
from render_primitives_limits import cbmc

def original(file,name):return function((ROOT/'c'/f'{file}.c').read_text(),name)
def between(text,start,end):return text[text.index(start):text.index(end,text.index(start))]

COMMON=r'''
#include "ugh.h"
#include "RENDER_C"
#define CHECK(c,m) __CPROVER_assert((c),(m))
typedef struct ProofMemory {
 uint16_t countdown,sprite,start,end,rate,x,y,cached_sprite,cached_x,cached_y;
 uint16_t background,draw,fixed,height,surface,directory,directory_segment;
 uint16_t countdown_first;unsigned stores;
} ProofMemory;
static ProofMemory memory;
static uint8_t sampled,write_value;static uint16_t read_position,write_position;static unsigned writes;
static uint16_t directory_dimensions;static unsigned reading_directory;
static uint16_t selected_slot;
static uint16_t sample16(uint16_t segment,uint16_t at){
 (void)segment;
 switch((uint16_t)(at-selected_slot)){
 case D(PlayerAnimationCountdowns):return memory.countdown;
 case D(PlayerSpriteIds):return memory.sprite;
 case D(PlayerAnimationCycleStarts):return memory.start;
 case D(PlayerAnimationCycleEnds):return memory.end;
 case D(PlayerThrustAnimationRate):return memory.rate;
 case D(PlayerPixelX):return memory.x;case D(PlayerYPixels):return memory.y;
 case D(PlayerCachedSpriteIds):return memory.cached_sprite;
 case D(PlayerCachedPixelX):return memory.cached_x;case D(PlayerCachedPixelY):return memory.cached_y;
 default:break;
 }
 switch(at){case D(WaterYPixels):return memory.surface;
 case G(BackgroundPagePointer):return memory.background;case G(DrawPagePointer):return memory.draw;
 case G(FixedVgaPagePointer):return memory.fixed;case G(PlayfieldHeight):return memory.height;
 case G(SpriteDirectoryPointer):return memory.directory;case G(SpriteDirectoryPointer)+2:return memory.directory_segment;
 default:CHECK(0,"complete normalized word resource binding");return 0;
 }
}
static void store16(uint16_t segment,uint16_t at,uint16_t v){
 (void)segment;
 switch((uint16_t)(at-selected_slot)){
 case D(PlayerAnimationCountdowns):if(!memory.stores)memory.countdown_first=v;memory.stores++;memory.countdown=v;break;
 case D(PlayerSpriteIds):memory.stores++;memory.sprite=v;break;
 case D(PlayerCachedSpriteIds):memory.cached_sprite=v;break;
 case D(PlayerCachedPixelX):memory.cached_x=v;break;
 case D(PlayerCachedPixelY):memory.cached_y=v;break;
 default:CHECK(at==G(RendererScratchWord) || at==G(SpritePlaneStateScratch),"complete normalized store binding");
 }
}
static uint8_t sample8(uint16_t segment,uint16_t at){(void)segment;read_position=at;return reading_directory?(uint8_t)(directory_dimensions>>((at&1u)*8u)):sampled;}
static void store8(uint16_t segment,uint16_t at,uint8_t value){(void)segment;write_position=at;write_value=value;writes++;}
static void no_push(Regs *r,uint16_t value){(void)r;(void)value;}
static uint16_t return_word;
static uint16_t no_pop(Regs *r){(void)r;return return_word;}
#define rd16 sample16
#define wr16 store16
#define rd8 sample8
#define wr8 store8
#define push no_push
#define pop no_pop
#define R(n) rd16(r->ds,D(n))
#define RI(n,i) rd16(r->ds,(uint16_t)(D(n)+(i)))
#define WI(n,i,v) wr16(r->ds,(uint16_t)(D(n)+(i)),(uint16_t)(v))
'''

def output(key):
    code=COMMON.replace('RENDER_C',(ROOT/'native/render_primitives.c').as_posix())
    pixel=original('render_primitives','c_DrawTransparentSprite')
    rect=original('render_primitives','c_RestoreBackgroundRectangle')
    code+=original('render_primitives','sar_word')+original('render_primitives','dec_byte')
    code+='int main(void){Regs arbitrary;Regs *r=&arbitrary;ProofMemory any;memory=any;memory.stores=0;writes=0;uint8_t byte;sampled=byte;uint16_t dimensions_input;directory_dimensions=dimensions_input;reading_directory=0;uint8_t selected;selected_slot=(uint16_t)((selected&1u)*2u);\n'
    if key=='placement':
        fragment=between(pixel,'    uint16_t id=r->ax, y=r->cx;','    platform_out(0x3c4,1,2);')
        code+='uint16_t sprite=r->ax,x=r->bx,original_y=r->cx;\n'+fragment
        code+='RenderSpritePlacement p=render_sprite_place(sprite,x,original_y,memory.surface,memory.height,memory.draw,memory.fixed);CHECK(p.destination==dest && p.water==water && p.y==y,"page/Y/SAR2/water/offset seam");\n'
        code+=between(pixel,'    uint8_t plane=','    uint16_t directory=')
        code+=between(pixel,'    uint16_t bank=','    uint16_t source=')
        code+='uint16_t banks[4]={G(SpritePixels0To216Pointer),G(SpritePixels217To297Pointer),G(SpritePixels298To546Pointer),G(SpritePixels547AndUpPointer)};CHECK(p.bank<4 && banks[p.bank]==bank && p.plane==plane,"full unsigned bank and initial mask seam");\n'
        # The actual directory expression is tested at the scalar cut.
        code+='uint16_t directory=memory.directory;'+between(pixel,'    directory=(uint16_t)','    uint16_t offset=')
        code+='CHECK(directory==(uint16_t)(memory.directory+p.directory_index),"wrapping directory index seam");'
    elif key=='begin':
        code+='RenderSpritePlacement p;uint16_t source,dimensions;uint8_t backward;RenderSpriteCursor c;render_sprite_begin(&c,p,source,dimensions,backward);uint16_t water=p.water;\n'
        code+=between(pixel,'    uint8_t columns=','    do {')
        code+='CHECK(c.source==source && c.destination==p.destination && c.row_destination==p.destination && c.water==r->bp && c.initial_water==water && c.plane==p.plane && c.columns==columns && c.rows==height && c.height==height && c.crossing==crossing && c.submerged==submerged && c.backward==backward,"complete constructor and signed water mode seam");'
    elif key=='pixel':
        code+='RenderSpriteCursor c;uint16_t source=c.source,row_dest=c.row_destination,source_seg;uint8_t rows=c.rows;int crossing=c.crossing,submerged=c.submerged;r->bp=c.water;if(c.backward)r->flags|=DF;else r->flags&=(uint16_t)~DF;\n'
        code+='RenderPixelRequest e=render_sprite_pixel(&c,sampled);\n'
        code+=between(pixel,'            uint8_t pixel=','        } while(rows);')
        code+='CHECK(e.source==read_position && e.write==writes,"source request and transparent skip seam");if(writes)CHECK(e.destination==write_position && e.value==write_value,"water tint/value/destination seam");CHECK(c.source==source && c.row_destination==row_dest && c.water==r->bp && c.rows==rows,"complete row continuation seam");'
    elif key=='column':
        code+='RenderSpriteCursor c;uint8_t plane=c.plane,columns=c.columns;uint16_t dest=c.destination;\n'
        code+=between(pixel,'        plane=(uint8_t)','    } while(columns);')
        code+='render_sprite_column(&c);CHECK(c.plane==plane && c.destination==dest && c.columns==columns && c.rows==c.height && c.row_destination==dest && (!c.crossing || c.water==c.initial_water),"mask rollover and column/reset seam");'
    elif key=='rectangle':
        code+='Regs saved=*r;\n'+between(rect,'    uint16_t x=','    do {')
        code+='RenderCopyRows c=render_rectangle(saved.ax,saved.bx,saved.cx,saved.dx,memory.background,memory.draw);CHECK(c.source==src && c.destination==dst && c.width==width && c.remaining==rows,"complete rectangle request seam");'
    elif key=='next-row':
        code+='RenderCopyRows c;uint16_t src=c.source,dst=c.destination,rows=c.remaining;\n'
        code+=between(rect,'        src=(uint16_t)','    } while(rows);')
        code+='render_next_row(&c);CHECK(c.source==src && c.destination==dst && c.remaining==rows,"full-word row cycle including zero seam");'
    elif key=='save':
        save=original('render_primitives','c_SaveDrawPageBackground')
        code+='uint16_t source=r->si,destination=r->di,count=r->cx;RenderCopyRequest before=render_save(source,destination,count,(uint8_t)!!(r->flags&DF));CHECK(before.source==source && before.destination==destination && before.count==count,"complete copy request prefix");if(!count)CHECK(before.source_end==source && before.destination_end==destination,"zero REP base");else{\n'
        fragment=between(save,'uint8_t v=rd8',' }\n    r->ds=')
        code+=fragment+'\nRenderCopyRequest after=render_save(r->si,r->di,r->cx,(uint8_t)!!(r->flags&DF));CHECK(before.source_end==after.source_end && before.destination_end==after.destination_end && r->cx==(uint16_t)(count-1u),"actual REP step and full-count endpoint invariant");CHECK(read_position==source && write_position==destination && write_value==sampled && writes==1,"live read before same-value write cut");}'
    elif key=='map-tile':
        code+='RenderDrawRequest e=render_map_tile(r->ax,r->dx);return_word=(uint8_t)r->ax;\n'
        code+=between(original('render','c_DrawMapTile'),'    set_ah(r,0);','    CALL(')
        code+='CHECK(e.draw && e.sprite==r->ax && e.x==r->bx && e.y==r->cx,"complete map tile sprite request seam");'
    elif key=='map-cell':
        code+='uint16_t ordinal;__CPROVER_assume(ordinal<320);uint8_t tile;RenderDrawRequest e=render_map_cell(ordinal,tile);r->dx=(uint16_t)((ordinal/20u)*256u+ordinal%20u);r->ax=tile;RenderDrawRequest actual=render_map_tile(r->ax,r->dx);CHECK(e.sprite==actual.sprite && e.x==actual.x && e.y==actual.y && e.draw,"tilemap/member wrapper seam");\n'
        tile=original('render','c_DrawTileMap');code+=between(tile,'    r->dx&=255;','    do {')+between(tile,'        r->dx&=0xff00;','        do {')
        code+='CHECK(r->dx==0,"actual outer/inner initialization clears both coordinate bytes");'
    elif key in ['tile-rectangle','playfield']:
        if key=='tile-rectangle':
            code+='RenderRectangleSpec e=render_tile_rectangle(r->ax,r->bx);'+between(original('render_primitives','c_RestoreTileBackground'),'    r->ax=','    return ')
        else:
            code+='RenderRectangleSpec e=render_playfield_rectangle(memory.height);'+between(original('render','c_RestorePlayfieldBackground'),'    push(r,r->bx);','    CALL(')
        code+='CHECK(e.x==r->ax && e.y==r->bx && e.width==r->cx && e.height==r->dx,"complete rectangle wrapper request seam");'
    elif key=='sprite-rectangle':
        code+='reading_directory=1;uint16_t sprite=r->cx;uint16_t discarded=memory.directory;'+between(original('render','c_RestoreSpriteBackground'),'    push(r,r->dx);','    CALL(')
        code+='CHECK(r->si==render_restore_sprite_index(sprite),"loaded directory offset is discarded seam");RenderRectangleSpec e=render_sprite_rectangle(r->ax,r->bx,(uint16_t)(r->cx+256u*r->dx));CHECK(e.x==r->ax && e.y==r->bx && e.width==r->cx && e.height==r->dx,"raw zero dimensions remain zero in restore request");(void)discarded;'
    elif key=='visible':
        code+='RenderPlayerCache cache={memory.cached_sprite,memory.cached_x,memory.cached_y};RenderDrawRequest e=render_player_restore(cache);unsigned called=0;r->bx=selected_slot;\n#define CALL(n,o,d) do{called++;CHECK(e.sprite==r->cx && e.x==r->ax && e.y==r->bx,"visible restore parameters seam");}while(0)\n'
        code+=between(original('render','c_RestorePlayerBackground'),'    r->cx=RI','    r->bx=pop(r);')
        code+='CHECK(e.draw==called,"all signed wrapper gates seam");'
    elif key=='animation':
        code+='RenderPlayerAnimation p={memory.countdown,memory.sprite,memory.start,memory.end,memory.rate,memory.x,memory.y};RenderAnimationResult e=render_player_animation(p);r->bx=selected_slot;\n'
        code+=between(original('render','c_AnimateAndDrawPlayer'),'    r->ax=RI(PlayerThrust','    r->ax=RI(PlayerSpriteIds,r->bx); push')
        code+='CHECK(e.countdown_first==memory.countdown_first && e.countdown==memory.countdown && e.sprite==memory.sprite && memory.stores==(e.advance?3u:1u),"all ordered animation stores seam");CHECK(e.request.draw==render_player_visible(p.x,p.y) && e.request.x==p.x && e.request.y==p.y && e.request.sprite==e.sprite,"animation/visible request seam");'
    elif key=='cache':
        code+='RenderPlayerCache c={memory.cached_sprite,memory.cached_x,memory.cached_y};render_cache_store(&c,0,memory.sprite);render_cache_store(&c,1,memory.x);render_cache_store(&c,2,memory.y);r->bx=selected_slot;\n'
        b=original('render_primitives','c_CachePlayerDrawState');code+=b[b.index('{')+1:b.index('    return UGH_OK;')]
        code+='CHECK(c.sprite==memory.cached_sprite && c.x==memory.cached_x && c.y==memory.cached_y,"complete ordered cache projection seam");'
    else:raise ValueError(key)
    return code+'return 0;}\n'

MUTATING={'pixel':('RenderSpriteCursor',['source','row_destination','water','rows']),
 'column':('RenderSpriteCursor',['plane','destination','columns','rows','row_destination','water']),
 'next-row':('RenderCopyRows',['source','destination','remaining']),
 'cache':('RenderPlayerCache',['sprite','x','y'])}
CALLS={'pixel':'RenderPixelRequest e=render_sprite_pixel(&c,pixel);(void)e;',
 'column':'render_sprite_column(&c);','next-row':'render_next_row(&c);','cache':'render_cache_store(&c,field,value);'}

def frame(key):
    typ,fields=MUTATING[key]
    code='#include "'+(ROOT/'native/render_primitives.c').as_posix()+'"\n#define CHECK(c,m) __CPROVER_assert((c),(m))\nint main(void){'+typ+' c;'+typ+' before=c;uint8_t pixel,field;uint16_t value;'+CALLS[key]
    code+='size_t watch;__CPROVER_assume(watch<sizeof(c));unsigned allowed=0;\n'
    for f in fields:
        condition='1' if key!='cache' else f'field=={fields.index(f)}'
        code+=f'if({condition} && watch>=(size_t)((unsigned char *)&c.{f}-(unsigned char *)&c) && watch<(size_t)((unsigned char *)&c.{f}-(unsigned char *)&c)+sizeof(c.{f}))allowed=1;\n'
    code+='if(!allowed)CHECK(((unsigned char *)&c)[watch]==((unsigned char *)&before)[watch],"arbitrary other byte including high bytes and padding frame");return 0;}'
    return '#include <stddef.h>\n'+code

def dependence(key):
    typ,fields=MUTATING[key]
    relevant={'pixel':['source','row_destination','water','rows','crossing','submerged','backward'],
        'column':['plane','destination','columns','height','crossing','water','initial_water'],
        'next-row':['source','destination','remaining'],'cache':[]}[key]
    code='#include "'+(ROOT/'native/render_primitives.c').as_posix()+'"\n#define CHECK(c,m) __CPROVER_assert((c),(m))\nint main(void){'+typ+' c,other;uint8_t pixel,field;uint16_t value;\n'
    for f in relevant:code+=f'other.{f}=c.{f};\n'
    first=CALLS[key];second=first.replace('&c,','&other,').replace('&c)','&other)').replace(' e=',' f=').replace('(void)e','(void)f')
    code+=first+second
    if key=='pixel':code+='CHECK(e.source==f.source && e.destination==f.destination && e.value==f.value && e.write==f.write,"event dependence on declared inputs only");'
    for f in fields:
        condition='1' if key!='cache' else f'field=={fields.index(f)}'
        code+=f'if({condition})CHECK(c.{f}==other.{f},"published state dependence");'
    return code+'return 0;}'

KEYS=['placement','begin','pixel','column','rectangle','next-row','save','map-tile','map-cell','tile-rectangle','playfield','sprite-rectangle','visible','animation','cache']
def main():
    ap=argparse.ArgumentParser();ap.add_argument('key',choices=KEYS);ap.add_argument('mode',choices=['output','frame','dependence'],default='output',nargs='?');ap.add_argument('--timeout',type=int,default=600);ap.add_argument('--reachability',action='store_true');a=ap.parse_args()
    folder=OUT/('reachability' if a.reachability else 'proofs')/(a.key+'-'+a.mode);folder.mkdir(parents=True,exist_ok=True)
    code=output(a.key) if a.mode=='output' else frame(a.key) if a.mode=='frame' else dependence(a.key)
    if a.reachability:
        assert a.mode=='output';at=code.rindex('return 0;');code=code[:at]+'CHECK(0,"REACHED_FINAL_COMPARISON");'+code[at:]
    harness=folder/'harness.c';harness.write_text(code)
    result=cbmc(harness,folder,[*FILES,ROOT/'c/render.c',ROOT/'c/render_primitives.c',ROOT/'c/ugh.h',ROOT/'c/ugh_sym.h',ROOT/'verif/render_primitives_proof.py'],unwind=8,timeout=a.timeout)
    print(result['result'],a.key,a.mode,result['seconds'],flush=True)
    if a.reachability:assert result['result']=='FAIL' and result['failures'] and all('REACHED_FINAL_COMPARISON' in str(f) for f in result['failures']),result.get('failures')
    else:assert result['result']=='PASS',result.get('failures')
if __name__=='__main__':main()
