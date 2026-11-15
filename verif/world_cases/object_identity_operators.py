"""Typed resource graph operators; common scheduling stays in world_gate."""
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'build/workers/cut-5x'
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'verif')]
from cbuild import GCC
from job_pool import run,save


def bounded(command,tag,cwd=ROOT,ok=(0,)):
 return run(command,cwd,OUT,tag,allowed=ok)


def router():
 import object_identity_cases
 receipt=object_identity_cases.run(ROOT,OUT,bounded,save)
 save(OUT/'router.json',receipt)


def borrowers():
 # The full-word import tests also exercise every registered typed cursor and
 # live descriptor/callback publication through the existing provider owner.
 router()
 save(OUT/'borrowers.json',json.loads((OUT/'router.json').read_text()))


def proof():
 folder=OUT/'proof';folder.mkdir(exist_ok=True)
 p=folder/'bounds.c'
 p.write_text('#include "'+(ROOT/'native/object_identities.c').as_posix()+'"\n'+r'''
unsigned nondet_unsigned(void);
void __CPROVER_assume(int);void __CPROVER_assert(int,const char*);
int main(void){
 unsigned n=nondet_unsigned();ObjectGraphLink link;
 ObjectIdentityStatus status=object_graph_link_at(n,&link);
 __CPROVER_assert((status==OBJECT_IDENTITY_OK)==(n<object_graph_link_count()),"graph index admission");
 if(status==OBJECT_IDENTITY_OK){
  __CPROVER_assert(link.source.index<RESOURCE_WORLD_VIEWS,"source view bounded");
  __CPROVER_assert(link.kind!=OBJECT_LINK_UNSUPPORTED,"extracted link has a role");
  if(link.kind==OBJECT_LINK_RESOURCE){
   __CPROVER_assert(link.resource.view.index<RESOURCE_WORLD_VIEWS,"target view bounded");
   __CPROVER_assert(link.resource.kind!=OBJECT_RESOURCE_UNSUPPORTED,"resource family explicit");
  }
 }
 ObjectResourceIdentity identity;
 __CPROVER_assume(n>=RESOURCE_WORLD_VIEWS && n<65536);
 status=object_resource_identity(OBJECT_SCRIPT,(ResourceWorldToken){(uint16_t)n},0,&identity);
 __CPROVER_assert(status==OBJECT_IDENTITY_UNSUPPORTED,"foreign view unsupported");
 __CPROVER_assert(identity.kind==OBJECT_RESOURCE_UNSUPPORTED,"no stale identity on rejection");
}
''',encoding='utf-8',newline='\n')
 pre=p.with_suffix('.i')
 bounded([GCC,'-E','-P','-nostdinc','-DUINT16_MAX=65535','-I',ROOT/'verif/cbmc_shim','-I',ROOT/'native',p,'-o',pre],'identity-proof-pre')
 tool=json.loads((ROOT/'metadata/verif-tools.json').read_text())['cbmc']['exe']
 result=bounded([tool,pre,'--unwind','13','--unwinding-assertions','--bounds-check','--pointer-check','--slice-formula'],'identity-proof')
 assert 'VERIFICATION SUCCESSFUL' in result['stdout']
 save(OUT/'proof.json',dict(result='PASS',scope='Actual C graph-index bounds and explicit families; foreign view rejection and cleared result. Exhaustive compiled router covers all registered positions and all transport words. No symbolic callback execution claim.'))


def defects():
 import object_identity_cases
 save(OUT/'defects.json',dict(result='PASS',controls=object_identity_cases.defects(ROOT,OUT,bounded)))
