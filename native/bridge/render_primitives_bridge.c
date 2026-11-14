#include "render_primitives_support.h"
static void push(Regs *r,uint16_t v) { r->sp=(uint16_t)(r->sp-2); wr16(r->ss,r->sp,v); }

static uint16_t pop(Regs *r) { uint16_t v=rd16(r->ss,r->sp); r->sp=(uint16_t)(r->sp+2); return v; }

static uint8_t inc8(Regs *r,uint8_t a) {
    uint8_t v=(uint8_t)(a+1); flag(r,OF,a==127); flag(r,AF,((a^v^1)&16)!=0); szp(r,v,8); return v;
}

static void cmp8(Regs *r,uint8_t a,uint8_t b) {
    uint8_t v=(uint8_t)(a-b);
    flag(r,CF,a<b); flag(r,OF,((a^b)&(a^v)&128)!=0);
    flag(r,AF,((a^b^v)&16)!=0); szp(r,v,8);
}

static uint16_t sar_word(uint16_t v, unsigned n) {
    /* Explicit sign fill: negative odd coordinates round toward minus infinity. */
    return (uint16_t)((v >> n) | ((v & 0x8000u) ? (0xffffu << (16-n)) : 0));
}

static uint8_t dec_byte(Regs *r, uint8_t v) {
    uint8_t out=(uint8_t)(v-1);
    flag(r,OF,v==0x80); flag(r,AF,((v^1u^out)&16u)!=0);
    szp(r,out,8); return out; /* DEC preserves CF. */
}

static void copy_mode(Regs *r,int enable) {
    r->dx=enable?0x3ce:0x3cf;
    if(enable) { set_al(r,5); platform_out(r->dx,1,5); r->dx=0x3cf; }
    set_al(r,(uint8_t)platform_in(r->dx,1));
    set_al(r,(uint8_t)logic(r,(uint8_t)r->ax&0xfc,8));
    if(enable) set_al(r,(uint8_t)((uint8_t)r->ax+1));
    platform_out(r->dx,1,(uint8_t)r->ax);
}

#define CALL(target,owner,delta) do { int status=ugh_call_near(G(target),(uint16_t)(G(owner)+(delta)),r); if(status) return status; } while(0)
#define R(name) rd16(r->ds,D(name))
#define W(name,v) wr16(r->ds,D(name),(uint16_t)(v))
#define B(name) rd8(r->ds,D(name))
#define WB(name,v) wr8(r->ds,D(name),(uint8_t)(v))
#define RI(name,i) rd16(r->ds,(uint16_t)(D(name)+(i)))
#define WI(name,i,v) wr16(r->ds,(uint16_t)(D(name)+(i)),(uint16_t)(v))
EXPORT int c_DrawTransparentSprite(Regs *r) {
    RenderSpritePlacement placement=render_sprite_place(r->ax,r->bx,r->cx,rd16(r->ds,D(WaterYPixels)),rd16(r->cs,G(PlayfieldHeight)),rd16(r->cs,G(DrawPagePointer)),rd16(r->cs,G(FixedVgaPagePointer)));
    uint16_t id=r->ax, y=r->cx;
    uint16_t dest=rd16(r->cs,G(DrawPagePointer));
    if((int16_t)y >= (int16_t)rd16(r->cs,G(PlayfieldHeight))) {
        dest=rd16(r->cs,G(FixedVgaPagePointer)); y=(uint16_t)(y-192u);
    }
    uint16_t water=(uint16_t)(rd16(r->ds,D(WaterYPixels))-y);
    wr16(r->cs,G(RendererScratchWord),rp_word(placement.water,water));
    dest=(uint16_t)(dest+sar_word(r->bx,2)+(uint16_t)(y*96u));
    dest=rp_word(placement.destination,dest);y=rp_word(placement.y,y);
    platform_out(0x3c4,1,2);
    uint8_t plane=rp_byte(placement.plane,(uint8_t)(1u<<(r->bx&3u)));
    wr16(r->cs,G(SpritePlaneStateScratch),(uint16_t)((uint16_t)plane*256u+2));
    uint16_t directory=rd16(r->cs,G(SpriteDirectoryPointer));
    uint16_t dirseg=rd16(r->cs,G(SpriteDirectoryPointer)+2);
    directory=(uint16_t)(directory+rp_word(placement.directory_index,(uint16_t)(id*4u)));
    uint16_t offset=rd16(dirseg,directory), dimensions=rd16(dirseg,(uint16_t)(directory+2));
    uint16_t bank=G(SpritePixels0To216Pointer);
    if(id>=217) bank=G(SpritePixels217To297Pointer);
    if(id>=298) bank=G(SpritePixels298To546Pointer);
    if(id>=547) bank=G(SpritePixels547AndUpPointer);
    const uint16_t banks[4]={G(SpritePixels0To216Pointer),G(SpritePixels217To297Pointer),G(SpritePixels298To546Pointer),G(SpritePixels547AndUpPointer)};
    rp_require(placement.bank<4);bank=rp_word(banks[placement.bank],bank);
    uint16_t source=(uint16_t)(rd16(r->cs,bank)+offset), source_seg=rd16(r->cs,(uint16_t)(bank+2));
    uint8_t columns=(uint8_t)dimensions, height=(uint8_t)(dimensions>>8);
    RenderSpriteCursor cursor;render_sprite_begin(&cursor,placement,source,dimensions,(uint8_t)!!(r->flags&DF));
    r->bp=water;
    int crossing=(int16_t)water>=0 && (int16_t)water<height;
    int submerged=(int16_t)water<0;
    do {
        platform_out(0x3c5,1,rp_byte(cursor.plane,plane));
        uint16_t row_dest=dest;
        uint8_t rows=height;
        if(crossing) r->bp=rd16(r->cs,G(RendererScratchWord));
        do {
            uint8_t pixel=rd8(source_seg,rp_word(cursor.source,source));
            RenderPixelRequest request=render_sprite_pixel(&cursor,pixel);rp_require(request.write==(pixel!=0));
            source=(uint16_t)(source+step(r));source=rp_word(cursor.source,source);
            if(pixel) {
                if(submerged || (crossing && (r->bp&0x8000u))) pixel|=0x40;
                wr8(0xa000,rp_word(request.destination,row_dest),rp_byte(request.value,pixel));
            }
            row_dest=(uint16_t)(row_dest+96u);
            if(crossing) r->bp=(uint16_t)(r->bp-1);
            rows=(uint8_t)(rows-1);
            row_dest=rp_word(cursor.row_destination,row_dest);rows=rp_byte(cursor.rows,rows);
            if(crossing)r->bp=rp_word(cursor.water,r->bp);
        } while(rows);
        plane=(uint8_t)((plane<<1)&15u);
        flag(r,CF,0); /* AND AH,0Fh; later INC instructions preserve this. */
        if(!plane) { plane=1; dest=(uint16_t)(dest+1); }
        columns=dec_byte(r,columns);render_sprite_column(&cursor);
        plane=rp_byte(cursor.plane,plane);dest=rp_word(cursor.destination,dest);columns=rp_byte(cursor.columns,columns);
    } while(columns);
    platform_out(0x3c5,1,15);
    return UGH_OK;
}

EXPORT int c_DrawMapTile(Regs *r) {
    RenderDrawRequest request=render_map_tile(r->ax,r->dx);
    set_ah(r,0); push(r,r->si); push(r,r->ax); push(r,r->dx);
    r->bx=(uint16_t)((r->dx&255)*16u); push(r,r->ax);
    r->ax=(uint16_t)(12u*(r->dx>>8)); r->cx=r->ax; r->ax=pop(r);
    rp_draw(r,request);
    CALL(DrawTransparentSprite,DrawMapTile,0x17);
    r->dx=pop(r); r->ax=pop(r); r->si=pop(r); return UGH_OK;
}

EXPORT int c_DrawTileMap(Regs *r) {
    uint16_t ordinal=0;
    r->si=R(CurrentTileMapPointer); r->ds=rd16(r->ds,D(CurrentTileMapPointer)+2);
    r->dx&=255;
    do {
        r->dx&=0xff00;
        do {
            set_al(r,rd8(r->ds,r->si)); r->si=(uint16_t)(r->si+step(r));
            rp_require(ordinal<320);RenderDrawRequest request=render_map_cell(ordinal,(uint8_t)r->ax);
            r->dx=rp_word((uint16_t)((request.y/12u)*256u+request.x/16u),r->dx);set_al(r,rp_byte((uint8_t)request.sprite,(uint8_t)r->ax));ordinal++;
            CALL(DrawMapTile,DrawTileMap,0xc);
            r->dx=(uint16_t)((r->dx&0xff00)|inc8(r,(uint8_t)r->dx));
            cmp8(r,(uint8_t)r->dx,20);
        } while((uint8_t)r->dx!=20);
        r->dx=(uint16_t)((r->dx&255)|(uint16_t)inc8(r,(uint8_t)(r->dx>>8))*256u);
        cmp8(r,(uint8_t)(r->dx>>8),16);
    } while((r->dx>>8)!=16);
    rp_require(ordinal==320);return UGH_OK;
}

EXPORT int c_SaveDrawPageBackground(Regs *r) {
    copy_mode(r,1); uint16_t ds=r->ds;
    r->si=rd16(r->cs,G(DrawPagePointer)); r->ds=rd16(r->cs,(uint16_t)(G(DrawPagePointer)+2));
    r->di=rd16(r->cs,G(BackgroundPagePointer)); r->es=rd16(r->cs,(uint16_t)(G(BackgroundPagePointer)+2));
    r->cx=rd16(r->cs,G(VgaPlaneCopyByteCount));
    RenderCopyRequest copy=render_save(r->si,r->di,r->cx,(uint8_t)!!(r->flags&DF));
    r->si=rp_word(copy.source,r->si);r->di=rp_word(copy.destination,r->di);r->cx=rp_word(copy.count,r->cx);
    while(r->cx) { uint8_t v=rd8(r->ds,r->si); wr8(r->es,r->di,v); r->si=(uint16_t)(r->si+step(r)); r->di=(uint16_t)(r->di+step(r)); r->cx--; }
    r->si=rp_word(copy.source_end,r->si);r->di=rp_word(copy.destination_end,r->di);
    r->ds=ds; copy_mode(r,0); return UGH_OK;
}

EXPORT int c_RestorePlayfieldBackground(Regs *r) {
    RenderRectangleSpec request=render_playfield_rectangle(rd16(r->cs,G(PlayfieldHeight)));
    push(r,r->bx); push(r,r->si); r->ax=logic(r,0,16); r->bx=r->ax;
    r->cx=320; r->dx=rd16(r->cs,G(PlayfieldHeight));
    rp_rectangle(r,request);
    CALL(RestoreBackgroundRectangle,RestorePlayfieldBackground,0x11);
    r->si=pop(r); r->bx=pop(r); return UGH_OK;
}

EXPORT int c_RestoreBackgroundRectangle(Regs *r) {
    Regs saved=*r; copy_mode(r,1);
    uint16_t x=saved.ax,y=saved.bx;
    uint16_t quarter=(uint16_t)((x>>2)|((x&0x8000)?0xc000:0));
    uint16_t base=(uint16_t)(y*96+quarter);
    uint16_t src=(uint16_t)(base+rd16(r->cs,G(BackgroundPagePointer)));
    uint16_t dst=(uint16_t)(base+rd16(r->cs,G(DrawPagePointer)));
    uint16_t width=(uint16_t)((uint16_t)((uint16_t)((x&3)+saved.cx)+3)>>2);
    uint16_t rows=saved.dx;
    RenderCopyRows copy=render_rectangle(x,y,saved.cx,saved.dx,rd16(r->cs,G(BackgroundPagePointer)),rd16(r->cs,G(DrawPagePointer)));
    src=rp_word(copy.source,src);dst=rp_word(copy.destination,dst);width=rp_word(copy.width,width);rows=rp_word(copy.remaining,rows);
    do {
        flag(r,DF,0);
        for(unsigned i=0;i<width;i++) wr8(0xa000,(uint16_t)(dst+i),rd8(0xa000,(uint16_t)(src+i)));
        src=(uint16_t)(src+96); dst=(uint16_t)(dst+96); rows--;render_next_row(&copy);
        src=rp_word(copy.source,src);dst=rp_word(copy.destination,dst);rows=rp_word(copy.remaining,rows);
    } while(rows);
    copy_mode(r,0); uint16_t flags=r->flags; *r=saved; r->flags=flags; r->di=dst;
    return UGH_OK;
}

EXPORT int c_RestoreSpriteBackground(Regs *r) {
    uint16_t index=render_restore_sprite_index(r->cx);
    push(r,r->dx); push(r,r->si); push(r,r->ds);
    r->si=rd16(r->cs,G(SpriteDirectoryPointer)); r->ds=rd16(r->cs,G(SpriteDirectoryPointer)+2);
    r->si=rp_word(index,(uint16_t)(r->cx*4u)); r->cx=rd8(r->ds,(uint16_t)(r->si+2));
    r->dx=rd8(r->ds,(uint16_t)(r->si+3));
    RenderRectangleSpec request=render_sprite_rectangle(r->ax,r->bx,(uint16_t)(r->cx+r->dx*256u));rp_rectangle(r,request);
    CALL(RestoreBackgroundRectangle,RestoreSpriteBackground,0x1a);
    r->ds=pop(r); r->si=pop(r); r->dx=pop(r); return UGH_OK;
}

EXPORT int c_RestoreTileBackground(Regs *r) {
    RenderRectangleSpec request=render_tile_rectangle(r->ax,r->bx);
    r->ax=(uint16_t)(r->ax<<4); r->bx=(uint16_t)(r->bx*12); r->cx=16; r->dx=12;
    rp_rectangle(r,request);return c_RestoreBackgroundRectangle(r);
}

EXPORT int c_RestorePlayerBackground(Regs *r) {
    RPRestorePlayer plan=rp_restore_begin(r);
    push(r,r->ax); push(r,r->bx);
    r->cx=RI(PlayerCachedSpriteIds,r->bx); r->ax=RI(PlayerCachedPixelX,r->bx);
    sub16(r,r->ax,(uint16_t)-32,0);
    if((int16_t)r->ax>-32) {
        sub16(r,r->ax,320,0);
        if((int16_t)r->ax<320) {
            r->bx=RI(PlayerCachedPixelY,r->bx); sub16(r,r->bx,(uint16_t)-20,0);
            if((int16_t)r->bx>-20) {
                sub16(r,r->bx,192,0);
                if((int16_t)r->bx<192) { rp_restore_request(r,&plan);CALL(RestoreSpriteBackground,RestorePlayerBackground,0x32); }
            }
        }
    }
    rp_restore_complete(&plan);r->bx=pop(r); CALL(CachePlayerDrawState,RestorePlayerBackground,0x36);
    r->ax=pop(r); return UGH_OK;
}

EXPORT int c_AnimateAndDrawPlayer(Regs *r) {
    RPAnimation plan=rp_animation_begin(r);
    r->ax=RI(PlayerThrustAnimationRate,r->bx);
    if((int16_t)r->ax>90) r->ax=90;
    rp_animation_write(r,&plan,D(PlayerAnimationCountdowns),r->bx,sub16(r,RI(PlayerAnimationCountdowns,r->bx),r->ax,0));
    r->ax=RI(PlayerAnimationCountdowns,r->bx); sub16(r,r->ax,0,0);
    if((int16_t)r->ax<0) {
        r->ax=add16(r,r->ax,200,0); rp_animation_write(r,&plan,D(PlayerAnimationCountdowns),r->bx,r->ax);
        r->ax=(uint16_t)(RI(PlayerSpriteIds,r->bx)+1u);
        sub16(r,r->ax,RI(PlayerAnimationCycleEnds,r->bx),0);
        if((int16_t)r->ax>=(int16_t)RI(PlayerAnimationCycleEnds,r->bx)) r->ax=RI(PlayerAnimationCycleStarts,r->bx);
        rp_animation_write(r,&plan,D(PlayerSpriteIds),r->bx,r->ax);
    }
    r->ax=RI(PlayerSpriteIds,r->bx); push(r,r->bx);
    r->cx=RI(PlayerYPixels,r->bx); sub16(r,r->cx,(uint16_t)-20,0);
    if((int16_t)r->cx>-20) {
        sub16(r,r->cx,192,0);
        if((int16_t)r->cx<192) {
            r->bx=RI(PlayerPixelX,r->bx); sub16(r,r->bx,(uint16_t)-32,0);
            if((int16_t)r->bx>-32) {
                sub16(r,r->bx,320,0);
                if((int16_t)r->bx<320) { rp_animation_draw(r,&plan);CALL(DrawTransparentSprite,AnimateAndDrawPlayer,0x6e); }
            }
        }
    }
    r->bx=pop(r);rp_animation_complete(&plan);return UGH_OK;
}

EXPORT int c_CachePlayerDrawState(Regs *r) {
    RenderPlayerCache cache={0};
    rp_cache_write(r,&cache,0,r->bx,
         rd16(r->ds,(uint16_t)(D(PlayerSpriteIds)+r->bx)));
    rp_cache_write(r,&cache,1,r->bx,
         rd16(r->ds,(uint16_t)(D(PlayerPixelX)+r->bx)));
    rp_cache_write(r,&cache,2,r->bx,
         rd16(r->ds,(uint16_t)(D(PlayerYPixels)+r->bx)));
    return UGH_OK;
}

