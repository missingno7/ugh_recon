"""Compiled actual-C stages, every digit pair and complete word-pair bar domain."""
import re,subprocess
from closure_support import ROOT,compile_c,receipt,save
from hud_shells import OUT,FILES
from hud_proof import common,output,STAGES,BYTE_MEMBERS

def main():
    folder=OUT/'cases';folder.mkdir(parents=True,exist_ok=True)
    prefix='''#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static unsigned domain,axis;static const char *case_name;
static unsigned long long checks;
static unsigned random_state=0x75912cab;
static unsigned random_word(void){random_state^=random_state<<13;random_state^=random_state>>17;random_state^=random_state<<5;return random_state&65535u;}
static void fill(void *p,size_t n){unsigned char *b=p;while(n--)*b++=(unsigned char)random_word();}
#define __CPROVER_assume(c) do{if(!(c))return;}while(0)
'''
    c=common().replace('#define CHECK(c,m) __CPROVER_assert((c),(m))','#define CHECK(c,m) do{if(!(c)){fprintf(stderr,"FAIL %s %s word=%u axis=%u\\n",case_name,m,domain,axis);exit(3);}}while(0)')
    code=prefix+c+'static HudValues fixture;static Regs fixture_regs;static unsigned char current_input,old_input;\n'
    reset='''#undef R
#undef rd16
#undef rd8
#undef CALL
#undef platform_out
#define R(n) sample16(r->ds,D(n))
#define rd16 sample16
#define rd8 sample8
#define CALL(n,o,d) ref_call(G(n),r)
'''
    keys=[*STAGES,'digit','advance','border','changed','bar-grow','bar-shrink']
    for key in keys:
        text=output(key)[len(common()):].replace('reference(', 'reference_'+key.replace('-','_')+'(').replace('ignored_out','ignored_out_'+key.replace('-','_'))
        text=text.replace('int main(void)','static void case_'+key.replace('-','_')+'(void)')
        text=text.replace('HudValues v;','HudValues v=fixture;').replace('HudValues any;','HudValues any=fixture;').replace('Regs arbitrary;','Regs arbitrary=fixture_regs;').replace('Regs r;','Regs r=fixture_regs;')
        text=text.replace('unsigned watch;__CPROVER_assume(watch<8);if(watch<modern.count)','for(unsigned watch=0;watch<modern.count;watch++)')
        text=text.replace('uint8_t a,b;','uint8_t a=current_input,b=old_input;')
        text=text.replace('return 0;','checks++;return;')
        code+=reset+text+'\n'
    code+='''static void initialize(void){fill(&fixture,sizeof(fixture));fill(&fixture_regs,sizeof(fixture_regs));
 if(axis<sizeof(fixture)/2){uint16_t value=(uint16_t)domain;memcpy((unsigned char *)&fixture+2*axis,&value,sizeof(value));}
'''
    for f in BYTE_MEMBERS:code+=f'fixture.{f}&=255u;\n'
    code+='''current_input=(unsigned char)domain;old_input=(unsigned char)random_word();}
int main(void){
 for(axis=0;axis<sizeof(fixture)/2;axis++)for(domain=0;domain<65536;domain++){
 initialize();
'''
    for key in STAGES:code+=f'case_name="{key}";case_{key.replace("-","_")}();\n'
    code+='''}
 printf("PASS %llu actual-C stage scalar-slice comparisons\\n",checks);fflush(stdout);
 memset(&fixture,0,sizeof(fixture));memset(&fixture_regs,0,sizeof(fixture_regs));
 for(domain=0;domain<65536;domain++){
 fixture_regs.ax=(uint16_t)domain;fixture.cursor_x=(uint16_t)domain;fixture.cursor_y=194;
 case_name="digit";case_digit();case_name="advance";case_advance();
 current_input=(unsigned char)domain;old_input=(unsigned char)(domain>>8);
 fixture.cursor_x=0xfffc;fixture_regs.si=0xffff;case_name="changed";case_changed();
 fixture.players=(uint16_t)domain;case_name="border";case_border();
 }
 printf("PASS all65536 current/previous digit byte pairs; all raw glyph AX/cursor/player-count words\\n");fflush(stdout);
 unsigned long long start=checks;
 for(unsigned width=0;width<65536;width++)for(unsigned previous=0;previous<65536;previous++){
 fixture_regs.ax=(uint16_t)width;fixture.bar_width=(uint16_t)previous;case_name="bar-grow";case_bar_grow();case_name="bar-shrink";case_bar_shrink();
 }
 printf("PASS %llu changed bar word pairs (complete65536x65536 domain, equal pairs emit no bar request)\\n",checks-start);
 return 0;}
'''
    harness=folder/'cases.c';harness.write_text(code);exe=folder/'cases.exe'
    built=compile_c([harness],exe,[ROOT/'c',ROOT/'native'],['-Wno-unused-function','-Wno-unused-variable','-Wno-unused-but-set-variable','-Wno-unused-label','-Wno-misleading-indentation'])
    p=subprocess.run([str(exe)],capture_output=True,text=True,timeout=600)
    save(folder/'result.json',receipt(['python','verif/hud_cases.py'],[*FILES,ROOT/'native/render_primitives.h',ROOT/'c/render.c',ROOT/'verif/hud_proof.py',ROOT/'verif/hud_cases.py'],result='PASS' if not p.returncode else 'FAIL',stdout=p.stdout,stderr=p.stderr,build=built,scope='C for full scalar slices with independently generated other fields. A for complete current/previous digit byte pairs at stated cursor/index and complete unequal bar-width/previous-width word pairs at the pure scalar decision boundary. Not A for the HUD component or physical transactions.'))
    print(p.stdout+p.stderr,flush=True);assert not p.returncode
if __name__=='__main__':main()
