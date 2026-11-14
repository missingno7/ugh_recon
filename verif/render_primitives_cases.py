"""Compile the actual-C property pairs and sweep full scalar slices."""
import json,re,subprocess
from closure_support import ROOT,compile_c,receipt,save,function
from render_primitives_shells import OUT,FILES
from render_primitives_proof import output,KEYS,COMMON,original

def main():
    folder=OUT/'cases';folder.mkdir(parents=True,exist_ok=True)
    common=COMMON.replace('RENDER_C',(ROOT/'native/render_primitives.c').as_posix())
    common=common.replace('#define CHECK(c,m) __CPROVER_assert((c),(m))','''#define CHECK(c,m) do{if(!(c)){fprintf(stderr,"FAIL %s: %s word=%u axis=%u\\n",case_name,m,domain,axis);exit(3);}}while(0)''')
    prefix='''#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static const char *case_name;static unsigned domain,axis;static unsigned long long comparisons;
static unsigned random_state=0x934abb01u;
static unsigned random_word(void){random_state^=random_state<<13;random_state^=random_state>>17;random_state^=random_state<<5;return random_state&65535u;}
static void fill(void *p,size_t n){unsigned char *b=p;while(n--)*b++=(unsigned char)random_word();}
#define __CPROVER_assume(c) do{if(!(c))return;}while(0)
'''
    code=prefix+common+original('render_primitives','sar_word')+original('render_primitives','dec_byte')
    code+='''static void initialize(Regs *r,ProofMemory *m){fill(r,sizeof(*r));fill(m,sizeof(*m));
 if(axis==0)r->ax=(uint16_t)domain;if(axis==1)r->bx=(uint16_t)domain;
 if(axis==2)r->cx=(uint16_t)domain;if(axis==3)r->dx=(uint16_t)domain;
 if(axis>=4 && axis<4+sizeof(*m)/2){uint16_t v=(uint16_t)domain;memcpy((unsigned char *)m+2*(axis-4),&v,sizeof(v));}
}
'''
    for key in KEYS:
        body=function(output(key),'main').replace('int main(void)','static void case_'+key.replace('-','_')+'(void)')
        body=body.replace('Regs arbitrary;','Regs arbitrary;').replace('ProofMemory any;','ProofMemory any;initialize(&arbitrary,&any);')
        body=body.replace('uint8_t byte;','uint8_t byte=(uint8_t)domain;').replace('uint16_t dimensions_input;','uint16_t dimensions_input=(uint16_t)domain;')
        body=body.replace(',source_seg;',',source_seg=(uint16_t)random_word();')
        # Every unconstrained local in the proof gets a deterministic independent
        # generated value here; the primary scalar is explicitly swept above.
        pattern=r'\b(uint16_t|uint8_t|RenderSpriteCursor|RenderSpritePlacement|RenderCopyRows)\s+([a-zA-Z_]\w*(?:,[a-zA-Z_]\w*)*)\s*;'
        def initialize_local(m):
            typ,names=m.groups();parts=[]
            for name in names.split(','):
                if typ.startswith('Render'):parts.append(typ+' '+name+';fill(&'+name+',sizeof('+name+'));')
                else:parts.append(typ+' '+name+'=('+typ+')'+('domain%320u' if name=='ordinal' else 'random_word()')+';')
            return ''.join(parts)
        body=re.sub(pattern,initialize_local,body)
        body=body.replace('return 0;','comparisons++;return;')
        code+=body+'\n'
    code+='int main(void){for(axis=0;axis<4+sizeof(ProofMemory)/2;axis++)for(domain=0;domain<65536;domain++){\n'
    for key in KEYS:code+='case_name="'+key+'";case_'+key.replace('-','_')+'();\n'
    code+='}printf("PASS %llu actual-C scalar-slice comparisons; full word and byte primary domains\\n",comparisons);return 0;}\n'
    harness=folder/'cases.c';harness.write_text(code);exe=folder/'cases.exe'
    built=compile_c([harness],exe,[ROOT/'c',ROOT/'native'],['-Wno-unused-function','-Wno-unused-variable','-Wno-unused-but-set-variable','-Wno-misleading-indentation'])
    p=subprocess.run([str(exe)],capture_output=True,text=True)
    save(folder/'result.json',receipt(['python','verif/render_primitives_cases.py'],[*FILES,ROOT/'c/render.c',ROOT/'c/render_primitives.c',ROOT/'verif/render_primitives_proof.py',ROOT/'verif/render_primitives_cases.py'],result='PASS' if not p.returncode else 'FAIL',stdout=p.stdout,stderr=p.stderr,build=built,scope='Complete individual 16-bit primary slices with other inputs generated independently, not a Cartesian input enumeration. VGA transactions remain services; full physical image/RAM is compared independently.'))
    print(p.stdout+p.stderr,flush=True);assert not p.returncode
if __name__=='__main__':main()
