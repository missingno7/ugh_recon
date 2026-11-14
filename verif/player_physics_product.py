"""Enumerate the entire pair of word operands in the actual product expressions."""
import subprocess
from closure_support import ROOT,function,compile_c,receipt,save
from player_physics_build import OUT,FILES
def main():
    folder=OUT/'product-enumeration';folder.mkdir(parents=True,exist_ok=True)
    original='(int32_t)(int16_t)r->ax*(int16_t)R(VgaRowStrideBytes)'
    borrowed='(int32_t)(int16_t)probe.pixel_y*(int16_t)rd16(r->ds,D(VgaRowStrideBytes))'
    assert original in function((ROOT/'c/scene.c').read_text(),'collision_address')
    assert borrowed in function((ROOT/'native/bridge/player_physics_bridge.c').read_text(),'physics_sample')
    text='''#include "ugh.h"
#include "'''+(ROOT/'native/player_physics.h').as_posix()+'''"
#include <stdio.h>
#include <stdlib.h>
#define R(n) row
#define rd16(s,o) row
static __attribute__((noinline)) int32_t actual(uint16_t y,uint16_t row) {
 Regs storage,*r=&storage;PlayerCollisionProbe probe;r->ax=y;probe.pixel_y=y;
 int32_t left='''+original+';int32_t right='+borrowed+''';
 if(left!=right || left< -1073709056 || left>1073741824)exit(1);
 return left;
}
int main(void) {
 uint64_t pairs=0,checksum=0;
 for(uint32_t y=0;y<65536u;y++)for(uint32_t row=0;row<65536u;row++){checksum+=(uint32_t)actual((uint16_t)y,(uint16_t)row);pairs++;}
 if(pairs!=4294967296ull || checksum!=2147418112ull*4294967296ull+1073741824ull)return 1;
 printf("PASS %llu operand pairs; identical actual signed products and exact range [-1073709056,1073741824]; checksum %llu\\n",(unsigned long long)pairs,(unsigned long long)checksum);
 return 0;
}
'''
    source=folder/'harness.c';source.write_text(text);exe=folder/'product.exe'
    built=compile_c([source],exe,[ROOT/'c',ROOT/'native']);run=subprocess.run([str(exe)],capture_output=True,text=True,timeout=600)
    save(folder/'result.json',receipt(built['command'],[*FILES,ROOT/'c/scene.c',ROOT/'verif/player_physics_product.py'],result='PASS' if not run.returncode else 'FAIL',stdout=run.stdout,stderr=run.stderr,returncode=run.returncode,domain=dict(operands=2,bits_each=16,combinations=4294967296),level='A',limitations='Only the extracted scalar expressions and range, not the complete collision service or craft update.'))
    print(run.stdout+run.stderr,flush=True);assert not run.returncode
if __name__=='__main__':main()
