"""Actual accepted actor_types history projector, all16 arbitrary histories."""
import json
from closure_support import ROOT,function
from render_history_build import OUT
from render_history_limits import cbmc,SMT
def main():
    source=ROOT/'native/bridge/actor_resources_bridge.c';raw=source.read_text();folder=OUT/'projection';folder.mkdir(parents=True,exist_ok=True)
    code='#include "'+(ROOT/'c/ugh.h').as_posix()+'"\n#include "'+(ROOT/'native/bridge/actor_projection.h').as_posix()+'"\n'
    code+='''void __CPROVER_assert(_Bool,const char *);void __CPROVER_assume(_Bool);
static uint16_t words[6][16],segment;
static uint16_t project_read(uint16_t bank,uint16_t address) {
 __CPROVER_assert(bank==segment,"only the supplied segment");
 const uint16_t bases[]={D(ActorPixelX),D(ActorPixelY),D(ActorPreviousDrawX),D(ActorPreviousDrawY),D(ActorEraseSprite),D(ActorEraseOverlaySprite)};
 for(unsigned i=0;i<6;i++) if(address>=bases[i] && address<bases[i]+32u) {
  __CPROVER_assert(!((address-bases[i])&1u),"word alignment");return words[i][(address-bases[i])/2u];
 }
 __CPROVER_assert(0,"complete read footprint");return 0;
}
#define rd16 project_read
'''+function(raw,'actor_read')+function(raw,'actor_bridge_render_project')+'''
int main(void) {
 uint16_t input[6][16],supplied_segment;segment=supplied_segment;
 for(unsigned i=0;i<6;i++)for(unsigned j=0;j<16;j++)words[i][j]=input[i][j];
 struct Guarded {uint16_t front;ActorRenderStorage storage;uint16_t back;} output;
 uint16_t a,b;output.front=a;output.back=b;actor_bridge_render_project(segment,&output.storage);
 unsigned slot;__CPROVER_assume(slot<16);ActorRenderHistory h=output.storage.slots[slot];
 __CPROVER_assert(h.pixel_x==input[0][slot] && h.pixel_y==input[1][slot] && h.previous_x==input[2][slot] && h.previous_y==input[3][slot] && h.erase_sprite==input[4][slot] && h.erase_overlay_sprite==input[5][slot],"all six fields retain arbitrary stale bit patterns at any physical slot");
 __CPROVER_assert(output.front==a && output.back==b,"projection output frame");
 unsigned field,index;__CPROVER_assume(field<6 && index<16);__CPROVER_assert(words[field][index]==input[field][index],"projection never mutates history RAM");
 return 0;
}
'''
    path=folder/'harness.c';path.write_text(code)
    result=cbmc(path,folder,[source,ROOT/'native/bridge/actor_projection.h',ROOT/'native/actors.h',ROOT/'c/ugh.h',ROOT/'c/ugh_sym.h',ROOT/'verif/render_history_projection.py'],unwind=18,timeout=600,defines=['-D__CPROVER__','-DUINT16_MAX=65535u'],extra=SMT)
    print(json.dumps({k:result[k] for k in ['result','seconds','peak_private_bytes','failures']}),flush=True);assert result['result']=='PASS'
if __name__=='__main__':main()
