"""Actual independent L1 and native/bridge C in one translation unit."""
import re
from closure_support import ROOT,function
from player_physics_build import FILES,includes
HELPERS=['sar','push','pop','collision_address','select_collision_plane','limit_velocity','reflect_velocity']
def pair(folder):
    folder.mkdir(parents=True,exist_ok=True)
    scene=(ROOT/'c/scene.c').read_text();samples=(ROOT/'c/demo_scripts.c').read_text()
    out='#include "ugh.h"\n#include "platform.h"\n'
    out+='uint16_t px_read(uint16_t,uint16_t);uint8_t px_read8(uint16_t,uint16_t);void px_write(uint16_t,uint16_t,uint16_t);void px_out(uint16_t,unsigned,uint32_t);int px_near(uint16_t,uint16_t,Regs *);void px_abort(void);\n'
    out+='#define rd16 px_read\n#define rd8 px_read8\n#define wr16 px_write\n#define platform_out px_out\n#define ugh_call_near px_near\n#define abort px_abort\n'
    out+='#include "'+(ROOT/'native/player_physics.c').as_posix()+'"\n'
    out+='\n'.join(line for line in scene.splitlines() if line.startswith('#define '))+'\n'
    for name in [*HELPERS,'c_MovePlayerWithVgaCollisions','c_SamplePlayerCollisionPixels']:
        body=function(samples if name=='c_SamplePlayerCollisionPixels' else scene,name)
        for helper in [*HELPERS,'c_MovePlayerWithVgaCollisions','c_SamplePlayerCollisionPixels']:
            body=re.sub(r'\b'+helper+r'\b','reference_'+helper,body)
        out+=body+'\n'
    out+='\n'.join('#undef '+s for s in ['R','W','RX','WX','CALL'])+'\n'
    bridge=includes((ROOT/'native/bridge/player_physics_bridge.c').read_text(),ROOT/'native/bridge/player_physics_bridge.c').replace('#include <stdlib.h>','')
    out+=bridge
    (folder/'pair.inc').write_text(out)
    return [*FILES,ROOT/'c/scene.c',ROOT/'c/demo_scripts.c',ROOT/'c/ugh.h',ROOT/'c/ugh_sym.h',ROOT/'c/platform.h',ROOT/'verif/player_physics_shells.py',ROOT/'verif/player_physics_pair.py']
