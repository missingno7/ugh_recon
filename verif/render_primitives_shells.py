"""Checked copies of the eleven complete ABI shells, with native request cuts."""
import argparse
from closure_support import ROOT,function

OUT=ROOT/'build/workers/close-stones-11'
BRIDGE=ROOT/'native/bridge/render_primitives_bridge.c'
NAMES=['DrawTransparentSprite','DrawMapTile','DrawTileMap','SaveDrawPageBackground','RestorePlayfieldBackground','RestoreBackgroundRectangle','RestoreSpriteBackground','RestoreTileBackground','RestorePlayerBackground','AnimateAndDrawPlayer','CachePlayerDrawState']
SOURCES={name:('render_primitives' if name in ['DrawTransparentSprite','SaveDrawPageBackground','RestoreBackgroundRectangle','RestoreTileBackground','CachePlayerDrawState'] else 'render') for name in NAMES}
FILES=[ROOT/'native/render_primitives.h',ROOT/'native/render_primitives.c',ROOT/'native/bridge/render_primitives_support.h',BRIDGE]

def replace(text,old,new):
    assert text.count(old)==1,(old,text.count(old));return text.replace(old,new)

def body(name):
    b=function((ROOT/'c'/f'{SOURCES[name]}.c').read_text(),'c_'+name)
    if name=='DrawTransparentSprite':
        b=replace(b,'    uint16_t id=r->ax, y=r->cx;','''    RenderSpritePlacement placement=render_sprite_place(r->ax,r->bx,r->cx,rd16(r->ds,D(WaterYPixels)),rd16(r->cs,G(PlayfieldHeight)),rd16(r->cs,G(DrawPagePointer)),rd16(r->cs,G(FixedVgaPagePointer)));
    uint16_t id=r->ax, y=r->cx;''')
        b=replace(b,'wr16(r->cs,G(RendererScratchWord),water);','wr16(r->cs,G(RendererScratchWord),rp_word(placement.water,water));')
        b=replace(b,'    platform_out(0x3c4,1,2);','    dest=rp_word(placement.destination,dest);y=rp_word(placement.y,y);\n    platform_out(0x3c4,1,2);')
        b=replace(b,'uint8_t plane=(uint8_t)(1u<<(r->bx&3u));','uint8_t plane=rp_byte(placement.plane,(uint8_t)(1u<<(r->bx&3u)));')
        b=replace(b,'(uint16_t)(id*4u)','rp_word(placement.directory_index,(uint16_t)(id*4u))')
        b=replace(b,'    uint16_t source=(uint16_t)', '''    const uint16_t banks[4]={G(SpritePixels0To216Pointer),G(SpritePixels217To297Pointer),G(SpritePixels298To546Pointer),G(SpritePixels547AndUpPointer)};
    rp_require(placement.bank<4);bank=rp_word(banks[placement.bank],bank);
    uint16_t source=(uint16_t)''')
        b=replace(b,'    r->bp=water;','    RenderSpriteCursor cursor;render_sprite_begin(&cursor,placement,source,dimensions,(uint8_t)!!(r->flags&DF));\n    r->bp=water;')
        b=replace(b,'        platform_out(0x3c5,1,plane);','        platform_out(0x3c5,1,rp_byte(cursor.plane,plane));')
        b=replace(b,'            uint8_t pixel=rd8(source_seg,source); source=(uint16_t)(source+step(r));','''            uint8_t pixel=rd8(source_seg,rp_word(cursor.source,source));
            RenderPixelRequest request=render_sprite_pixel(&cursor,pixel);rp_require(request.write==(pixel!=0));
            source=(uint16_t)(source+step(r));source=rp_word(cursor.source,source);''')
        b=replace(b,'wr8(0xa000,row_dest,pixel);','wr8(0xa000,rp_word(request.destination,row_dest),rp_byte(request.value,pixel));')
        b=replace(b,'            rows=(uint8_t)(rows-1);','''            rows=(uint8_t)(rows-1);
            row_dest=rp_word(cursor.row_destination,row_dest);rows=rp_byte(cursor.rows,rows);
            if(crossing)r->bp=rp_word(cursor.water,r->bp);''')
        b=replace(b,'        columns=dec_byte(r,columns);','''        columns=dec_byte(r,columns);render_sprite_column(&cursor);
        plane=rp_byte(cursor.plane,plane);dest=rp_word(cursor.destination,dest);columns=rp_byte(cursor.columns,columns);''')
    if name=='RestoreBackgroundRectangle':
        b=replace(b,'    uint16_t rows=saved.dx;','''    uint16_t rows=saved.dx;
    RenderCopyRows copy=render_rectangle(x,y,saved.cx,saved.dx,rd16(r->cs,G(BackgroundPagePointer)),rd16(r->cs,G(DrawPagePointer)));
    src=rp_word(copy.source,src);dst=rp_word(copy.destination,dst);width=rp_word(copy.width,width);rows=rp_word(copy.remaining,rows);''')
        b=replace(b,'src=(uint16_t)(src+96); dst=(uint16_t)(dst+96); rows--;','''src=(uint16_t)(src+96); dst=(uint16_t)(dst+96); rows--;render_next_row(&copy);
        src=rp_word(copy.source,src);dst=rp_word(copy.destination,dst);rows=rp_word(copy.remaining,rows);''')
    if name=='SaveDrawPageBackground':
        b=replace(b,'    while(r->cx)', '''    RenderCopyRequest copy=render_save(r->si,r->di,r->cx,(uint8_t)!!(r->flags&DF));
    r->si=rp_word(copy.source,r->si);r->di=rp_word(copy.destination,r->di);r->cx=rp_word(copy.count,r->cx);
    while(r->cx)''')
        b=replace(b,'    r->ds=ds;','    r->si=rp_word(copy.source_end,r->si);r->di=rp_word(copy.destination_end,r->di);\n    r->ds=ds;')
    if name=='DrawMapTile':
        b=replace(b,'    set_ah(r,0);','    RenderDrawRequest request=render_map_tile(r->ax,r->dx);\n    set_ah(r,0);')
        b=replace(b,'    CALL(DrawTransparentSprite','    rp_draw(r,request);\n    CALL(DrawTransparentSprite')
    if name=='DrawTileMap':
        b=replace(b,'    r->si=R(CurrentTileMapPointer);','    uint16_t ordinal=0;\n    r->si=R(CurrentTileMapPointer);')
        b=replace(b,'            CALL(DrawMapTile', '''            rp_require(ordinal<320);RenderDrawRequest request=render_map_cell(ordinal,(uint8_t)r->ax);
            r->dx=rp_word((uint16_t)((request.y/12u)*256u+request.x/16u),r->dx);set_al(r,rp_byte((uint8_t)request.sprite,(uint8_t)r->ax));ordinal++;
            CALL(DrawMapTile''')
        b=replace(b,'    return UGH_OK;','    rp_require(ordinal==320);return UGH_OK;')
    if name=='RestorePlayfieldBackground':
        b=replace(b,'    push(r,r->bx);','    RenderRectangleSpec request=render_playfield_rectangle(rd16(r->cs,G(PlayfieldHeight)));\n    push(r,r->bx);')
        b=replace(b,'    CALL(RestoreBackgroundRectangle','    rp_rectangle(r,request);\n    CALL(RestoreBackgroundRectangle')
    if name=='RestoreTileBackground':
        b=replace(b,'    r->ax=(uint16_t)', '    RenderRectangleSpec request=render_tile_rectangle(r->ax,r->bx);\n    r->ax=(uint16_t)')
        b=replace(b,'    return c_RestoreBackgroundRectangle(r);','    rp_rectangle(r,request);return c_RestoreBackgroundRectangle(r);')
    if name=='RestoreSpriteBackground':
        b=replace(b,'    push(r,r->dx);','    uint16_t index=render_restore_sprite_index(r->cx);\n    push(r,r->dx);')
        b=replace(b,'r->si=(uint16_t)(r->cx*4u);','r->si=rp_word(index,(uint16_t)(r->cx*4u));')
        b=replace(b,'    CALL(RestoreBackgroundRectangle','    RenderRectangleSpec request=render_sprite_rectangle(r->ax,r->bx,(uint16_t)(r->cx+r->dx*256u));rp_rectangle(r,request);\n    CALL(RestoreBackgroundRectangle')
    if name=='RestorePlayerBackground':
        b=replace(b,'    push(r,r->ax);','    RPRestorePlayer plan=rp_restore_begin(r);\n    push(r,r->ax);')
        b=replace(b,'{ CALL(RestoreSpriteBackground','{ rp_restore_request(r,&plan);CALL(RestoreSpriteBackground')
        b=replace(b,'    r->bx=pop(r); CALL(CachePlayerDrawState','    rp_restore_complete(&plan);r->bx=pop(r); CALL(CachePlayerDrawState')
    if name=='AnimateAndDrawPlayer':
        b=replace(b,'    r->ax=RI(PlayerThrustAnimationRate,r->bx);','    RPAnimation plan=rp_animation_begin(r);\n    r->ax=RI(PlayerThrustAnimationRate,r->bx);')
        b=b.replace('WI(PlayerAnimationCountdowns,r->bx,','rp_animation_write(r,&plan,D(PlayerAnimationCountdowns),r->bx,').replace('WI(PlayerSpriteIds,r->bx,','rp_animation_write(r,&plan,D(PlayerSpriteIds),r->bx,')
        b=replace(b,'{ CALL(DrawTransparentSprite','{ rp_animation_draw(r,&plan);CALL(DrawTransparentSprite')
        b=replace(b,'    r->bx=pop(r); return UGH_OK;','    r->bx=pop(r);rp_animation_complete(&plan);return UGH_OK;')
    if name=='CachePlayerDrawState':
        b=replace(b,'    wr16(r->ds,(uint16_t)(D(PlayerCachedSpriteIds)+r->bx),','    RenderPlayerCache cache={0};\n    rp_cache_write(r,&cache,0,r->bx,')
        b=replace(b,'    wr16(r->ds,(uint16_t)(D(PlayerCachedPixelX)+r->bx),','    rp_cache_write(r,&cache,1,r->bx,')
        b=replace(b,'    wr16(r->ds,(uint16_t)(D(PlayerCachedPixelY)+r->bx),','    rp_cache_write(r,&cache,2,r->bx,')
    return b

def generate():
    s='#include "render_primitives_support.h"\n'
    for source,names in [('render',['push','pop','inc8','cmp8']),('render_primitives',['sar_word','dec_byte','copy_mode'])]:
        for name in names:s+=function((ROOT/'c'/f'{source}.c').read_text(),name)+'\n'
    s+='\n'.join(x for x in (ROOT/'c/render.c').read_text().splitlines() if x.startswith('#define '))+'\n'
    for name in NAMES:s+=body(name)+'\n'
    return s

def main():
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args();s=generate()
    if a.write:BRIDGE.write_text(s)
    assert BRIDGE.read_text()==s,'generated ABI shell differs from source-checked recipe'
    print('PASS eleven complete ABI shells and retained pixel transactions')
if __name__=='__main__':main()
