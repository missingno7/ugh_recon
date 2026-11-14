"""Every shipped password through native editing and the literal session lookup cut."""
import sys,ctypes as C,json,hashlib
from pathlib import Path
from closure_support import ROOT,function,compile_c,receipt,save
from menus_build import OUT
sys.path.insert(0,str(ROOT/'tools'))
import contacts_reference,difftest
contacts_reference.OUT=OUT/'reference'

def main():
 negative='--negative' in sys.argv;folder=OUT/('passwords-negative' if negative else 'passwords');folder.mkdir(parents=True,exist_ok=True);plain=contacts_reference.prepare_reference(local=True);m=difftest.Machine()
 body=function((ROOT/'c/scene.c').read_text(),'c_RunGameFromPassword');part=body[body.index('    r->cx=logic'):body.index('selected:')]
 if negative:part=part.replace('if((uint8_t)r->ax!=rd8','if((uint8_t)r->ax==rd8')
 source='#include "platform.h"\n#include "high_scores.h"\n#include <string.h>\n'+(ROOT/'native/high_scores.c').read_text()+'''
static uint8_t memory[65537];
uint8_t ugh_read(uint32_t address) {return memory[address];}
void ugh_write(uint32_t address,uint8_t value) {memory[address]=value;}
#define R(n) rd16(r->ds,D(n))
EXPORT void load_data(const uint8_t *data) {memcpy(memory,data,65537);}
static int select_password(Regs *r) {'''+part+'''selected:return 0;}
EXPORT uint32_t select_case(uint16_t players,const uint8_t *input,unsigned count,int edit) {
 for(unsigned i=0;i<20;i++) memory[D(PasswordEditBuffer)+i]=32;
 if(edit) {
  uint16_t position=0;for(unsigned i=0;i<count;i++) {FrontEditCommand command=front_edit_command(position,20,input[i],0);
   if(command.kind==FRONT_EDIT_ERASE) for(unsigned k=0;k<command.erase_count;k++) memory[(uint16_t)(D(PasswordEditBuffer)+command.erase[k])]=32;
   if(command.kind==FRONT_EDIT_STORE) memory[D(PasswordEditBuffer)+position]=command.character;
   position=command.position;
  }
 }else for(unsigned i=0;i<count && i<20;i++) memory[D(PasswordEditBuffer)+i]=input[i];
 memory[D(PlayerArrayBytes)]=(uint8_t)(players*2);memory[D(PlayerArrayBytes)+1]=0;
 Regs r={0};if(select_password(&r)) return 0x10000u;return r.cx;
}
'''
 helper=folder/'passwords.c';helper.write_text(source);path=folder/'passwords.dll';built=compile_c([helper],path,[ROOT/'c',ROOT/'native'],['-shared']);dll=C.CDLL(str(path));dll.load_data.argtypes=[C.c_void_p];dll.load_data(m.read(m.seg('DGROUP:PlayerCount'),0,65537));dll.select_case.argtypes=[C.c_uint16,C.c_void_p,C.c_uint,C.c_int];dll.select_case.restype=C.c_uint32;rows=[];mismatches=0
 for players,total in [(1,69),(2,81)]:
  position=m.rw('DGROUP:PasswordListPointers',2*(players-1));items=[]
  for index in range(total):
   text=bytearray()
   while True:
    ch=m.read(m.seg('DGROUP:PlayerCount'),position,1)[0];position+=1
    if not ch:break
    text.append(ch)
   items.append(bytes(text))
  assert len(set(items))==total
  cases=[]
  for index,text in enumerate(items):
   cases.extend([(text,index,0,'exact'),(text.lower(),index,1,'native lowercase edit')])
   for variant in [text[:-1],b'!'+text,text+b'X' if len(text)<20 else text[:19]+b'X',text+b'\0' if len(text)<20 else b'NONE']:
    expected=items.index(variant) if variant in items else 0;cases.append((variant,expected,0,'invalid/prefix/tail'))
  cases.extend([(b'NONE',0,0,'default'),(b'',0,0,'all spaces'),(b'CAV!ITY',0,1,'filtered punctuation')])
  for text,expected,edit,kind in cases:
   actual=dll.select_case(players,text,len(text),edit);rows.append(dict(players=players,input=text.hex(),edit=edit,kind=kind,expected=expected,actual=actual));mismatches+=actual!=expected
 assert mismatches>0 if negative else mismatches==0,mismatches
 save(folder/'result.json',receipt([sys.executable,'verif/menus_passwords.py',*sys.argv[1:]],[Path(__file__),ROOT/'native/high_scores.c',ROOT/'native/high_scores.h',ROOT/'native/front_end.h',ROOT/'c/scene.c',helper,plain],result='PASS',cases=rows,mismatches=mismatches,negative_detected=negative,scope='Actual RunGameFromPassword selection prefix only; session remains an external service. No production session adapter changed.',build=built));print('PASS',len(rows),'password/edit/session-cut cases; negative',negative,'mismatches',mismatches)
if __name__=='__main__':main()
