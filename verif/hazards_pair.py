"""Extract independent maintained L1 bodies; no instruction/arithmetic models."""
import re
from pathlib import Path
from closure_support import ROOT,function
from hazards_build import NAMES,ENTRIES,OUT

def pair(folder):
    folder.mkdir(parents=True,exist_ok=True)
    text=f'#include "{(ROOT/"c/ugh.h").as_posix()}"\n'
    text+='uint16_t hz_read(uint16_t,uint16_t);void hz_write(uint16_t,uint16_t,uint16_t);\n#define rd16 hz_read\n#define wr16 hz_write\n'
    helpers=[['shl','inc','less','greater','enemy_init','enemy_frame','score','enemy_wait','state_jump','tail','contact'],
             ['lt','gt','shift','push','pop','effect','frame','enemy_stone','enemy_player','face_player','enemy_tick','recover','tail'],
             ['cell']]
    paths=[]
    for group,module in enumerate(['actors.c','actors_states.c','items_water.c']):
        path=ROOT/'c'/module;paths.append(path);raw=path.read_text()
        selected=[n for n in NAMES if re.search(r'EXPORT int c_'+n+r'\(',raw)]
        extra=['FindThrownStoneHittingEnemy','FindPlayerTouchingEnemy'] if group==0 else []
        names=helpers[group]+['c_'+n for n in selected+extra]
        for name in helpers[group]:text+=f'#define {name} ref{group}_{name}\n'
        text+='\n'.join(line for line in raw.splitlines() if line.startswith('#define '))+'\n'
        if group==0:text+='static int state_jump(Regs *,uint16_t);\n'
        if group<2:text+='static int tail(Regs *,unsigned);\n'
        for name in names:
            body=function(raw,name)
            body=re.sub(r'\bc_(\w+)\b',r'reference_\1',body)
            text+=body+'\n'
        for name in helpers[group]+['READ','WRITE','A','W','DESC','R','B','F']:text+=f'#undef {name}\n'
    text+='#ifdef CONTACT_CONTRACT\n#define contact_players contract_players\n#define contact_stones contract_stones\n#endif\n'
    text+=f'#include "{(ROOT/"native/hazards.c").as_posix()}"\n'
    text+='#undef contact_players\n#undef contact_stones\n'
    text+=f'#include "{(ROOT/"native/contacts.c").as_posix()}"\n'
    text+='static uint16_t code(HazardEntry entry) { switch(entry) { case H_ZERO:return 0; case H_IGNORE:return G(IgnoreActorState);\n'
    for name,entry in ENTRIES.items():text+=f'case {entry}:return G({name});\n'
    text+='default:return 0; }}\n'
    text+='static int reference_step(HazardEntry entry,Regs *r) { switch(entry) {\n'
    for name,entry in ENTRIES.items():text+=f'case {entry}:return reference_{name}(r);\n'
    text+='default:return 0; }}\n'
    (folder/'pair.inc').write_text(text)
    return paths+[ROOT/'native/hazards.c',ROOT/'native/hazards.h',ROOT/'native/contacts.c',ROOT/'native/contacts.h',
        ROOT/'native/geometry.h',ROOT/'native/level.h',ROOT/'c/ugh.h',ROOT/'c/ugh_sym.h',Path(__file__)]
