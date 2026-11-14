"""Actual literal branch spans, with explicit one-iteration loop cuts."""
from closure_support import ROOT,function

def pieces():
    raw=function((ROOT/'c/scene.c').read_text(),'c_MovePlayerWithVgaCollisions')
    body=raw[raw.index('{')+1:raw.rfind('}')]
    def span(first,last,start=0):
        a=body.index(first,start);b=body.index(last,a);return body[a:b]
    horizontal=span('        if((int8_t)(r->cx>>8)<0)', '        if(r->ax!=RX(PlayerPixelX,r->bx))')
    horizontal=horizontal.replace('        r->bp=r->di; r->ax=sar(r->di,5);','        r->bp=r->di; r->ax=sar(r->di,5);')
    left_setup=span('                uint8_t cl=(uint8_t)((uint8_t)r->cx-1);','                do {')
    right_setup=span('                    uint8_t cl=(uint8_t)((uint8_t)r->cx+1);','                    CALL(SamplePlayerCollisionPixels')
    vertical=span('    r->ax=RX(PlayerVerticalVelocities,r->bx);','    if(r->ax!=RX(PlayerYPixels,r->bx))')
    landing=span('            reflect_velocity(r,(uint16_t)(D(PlayerVerticalVelocities)+r->bx));','        } else r->bp=r->di;',body.index('vertical_limit:'))
    # The parent branch/loop conditions and their cursor updates remain literal.
    # Only break/backedge transfers become explicit continuation values.
    horizontal_prepare=horizontal+'''if(r->ax!=RX(PlayerPixelX,r->bx)) {
 r->bp=RX(PlayerX32,r->bx);
 if((int16_t)r->di<=(int16_t)r->bp) {
'''+left_setup+'''positive=0;
 } else positive=1;
 continuation=PP_HORIZONTAL_SCAN;
} else continuation=PP_HORIZONTAL_END;
'''
    vertical_prepare=vertical+'''if(r->ax!=RX(PlayerYPixels,r->bx)) {
 r->bp=RX(PlayerY32,r->bx);
 if((int16_t)r->di<=(int16_t)r->bp) {
 r->si=(uint16_t)(r->si-0x60);positive=0;
 } else positive=1;
 continuation=PP_VERTICAL_SCAN;
} else continuation=PP_VERTICAL_END;
'''
    horizontal_hit='''int hit=0,more=0;
if(!positive) {
 if(r->flags&SF) { r->bp=(uint16_t)((r->bp&0xffe0)+32); hit=1; }
 if(!hit){r->bp=(uint16_t)(r->bp-32);more=(int16_t)r->bp>(int16_t)r->di;}
} else {
 if(r->flags&SF) { r->bp&=0xffe0; hit=1; }
 if(!hit){r->bp=(uint16_t)(r->bp+32);more=(int16_t)r->bp<(int16_t)r->di;}
}
if(hit) {
'''+span('                reflect_velocity(r,(uint16_t)(D(PlayerHorizontalVelocities)+r->bx));','            } else r->bp=r->di;')+'''} else if(!more)r->bp=r->di;
continuation=more?PP_HORIZONTAL_SCAN:PP_HORIZONTAL_END;
'''
    vertical_hit='''int hit=0,more=0;
if(!positive) {
 if(r->flags&SF) { r->bp=(uint16_t)((r->bp&0xffe0)+32); hit=1; }
 if(!hit){r->bp=(uint16_t)(r->bp-32);more=(int16_t)r->bp>(int16_t)r->di;}
} else {
 if(r->flags&SF) { r->bp&=0xffe0; hit=1; }
 if(!hit){r->bp=(uint16_t)(r->bp+32);more=(int16_t)r->bp<(int16_t)r->di;}
}
if(hit) {
'''+landing+'''} else if(!more)r->bp=r->di;
continuation=more?PP_VERTICAL_SCAN:PP_VERTICAL_END;
'''
    result={
      'initial':body[:body.index('    if((int16_t)RX(PlayerPlatformIndices')]+'''if((int16_t)RX(PlayerPlatformIndices,r->bx)<0)continuation=PP_HORIZONTAL;else continuation=PP_VERTICAL;
''',
      'horizontal':horizontal_prepare,
      'horizontal-scan':'''if(positive) {
'''+right_setup+'''CALL(SamplePlayerCollisionPixels,(uint16_t)(G(MovePlayerWithVgaCollisions)+0x159));
} else {CALL(SamplePlayerCollisionPixels,(uint16_t)(G(MovePlayerWithVgaCollisions)+0x12f));}
continuation=PP_HORIZONTAL_HIT;
''',
      'horizontal-hit':horizontal_hit,
      'horizontal-end':span('        WX(PlayerX32,r->bx,r->bp);','    }\n    r->ax=RX(PlayerVerticalVelocities'),
      'vertical':vertical_prepare,
      'vertical-scan':'''if(positive) {
 r->si=(uint16_t)(r->si+0x60);
 CALL(SamplePlayerCollisionPixels,(uint16_t)(G(MovePlayerWithVgaCollisions)+0x2f1));
} else {CALL(SamplePlayerCollisionPixels,(uint16_t)(G(MovePlayerWithVgaCollisions)+0x2d4));}
continuation=PP_VERTICAL_HIT;
''',
      'vertical-hit':vertical_hit,
      'vertical-end':body[body.index('    WX(PlayerY32,r->bx,r->bp);'):body.rfind('    return UGH_OK;')],
    }
    return result

def adapt(body):
    body=body.replace('reflect_velocity(r,','reflect_velocity(r,plan,')
    body=body.replace('select_collision_plane(r)','select_collision_plane(r,plan)')
    return body.replace('platform_out(', 'physics_out(r,plan,')

def wrappers(key):
    import re
    from player_physics_pair import HELPERS
    body=pieces()[key];reference=body
    for name in HELPERS:reference=re.sub(r'\b'+name+r'\b','reference_'+name,reference)
    macros='''#define R(n) px_read(r->ds,D(n))
#define RX(n,i) px_read(r->ds,(uint16_t)(D(n)+(i)))
'''
    undef='\n'.join('#undef '+s for s in ['R','W','RX','WX','CALL'])+'\n'
    out=undef+macros+'''#define W(n,v) px_write(r->ds,D(n),(uint16_t)(v))
#define WX(n,i,v) px_write(r->ds,(uint16_t)(D(n)+(i)),(uint16_t)(v))
#define CALL(n,ret) do {int status=px_near(G(n),ret,r);if(status)return status;}while(0)
static int reference_piece(Regs *r) {
'''+reference+'return UGH_OK;}\n'
    out+=undef+macros+'''#define W(n,v) physics_write(r,plan,D(n),(uint16_t)(v))
#define WX(n,i,v) physics_write(r,plan,(uint16_t)(D(n)+(i)),(uint16_t)(v))
#define CALL(n,ret) do {int status=physics_sample(r,plan,ret);if(status)return status;}while(0)
static int bridge_piece(Regs *r,PhysicsPlan *plan) {
'''+adapt(body)+'return UGH_OK;}\n'+undef
    return out
