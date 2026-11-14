"""Replay the complete retained register ABI; bind all writes and VGA services."""
import sys
from closure_support import ROOT,function
BRIDGE=ROOT/'native/bridge/player_physics_bridge.c'
NAMES=['MovePlayerWithVgaCollisions','SamplePlayerCollisionPixels']
def generated():
    scene=(ROOT/'c/scene.c').read_text()
    text='''#define R(n) rd16(r->ds,D(n))
#define W(n,v) physics_write(r,plan,D(n),(uint16_t)(v))
#define RX(n,i) rd16(r->ds,(uint16_t)(D(n)+(i)))
#define WX(n,i,v) physics_write(r,plan,(uint16_t)(D(n)+(i)),(uint16_t)(v))
#define CALL(n,ret) do { int status=physics_sample(r,plan,ret); if(status) return status; } while(0)
'''
    for helper in ['sar','push','pop','collision_address','select_collision_plane','limit_velocity','reflect_velocity']:
        body=function(scene,helper)
        if helper in ['select_collision_plane','reflect_velocity']:
            body=body.replace('Regs *r','Regs *r,PhysicsPlan *plan')
            body=body.replace('platform_out(', 'physics_out(r,plan,')
            body=body.replace('wr16(r->ds,offset,r->ax)', 'physics_write(r,plan,offset,r->ax)')
        text+=body+'\n'
    body=function(scene,'c_MovePlayerWithVgaCollisions')
    body=body.replace('{','{ PhysicsPlan storage;physics_open(r,&storage);PhysicsPlan *plan=&storage;',1)
    body=body.replace('select_collision_plane(r)', 'select_collision_plane(r,plan)')
    body=body.replace('reflect_velocity(r,', 'reflect_velocity(r,plan,')
    body=body.replace('platform_out(', 'physics_out(r,plan,')
    body=body.replace('return UGH_OK;', 'physics_complete(r,plan);return UGH_OK;')
    return text+body+'\n'
def main():
    marker='/* BEGIN CHECKED PLAYER PHYSICS SHELL */\n'
    expected=BRIDGE.read_text().split(marker)[0]+marker+generated()
    if '--write' in sys.argv:BRIDGE.write_text(expected)
    else:assert BRIDGE.read_text()==expected,'player physics retained shell drift'
    print('PASS complete physics shell, seven helpers, all store/port/sample bindings')
if __name__=='__main__':main()
