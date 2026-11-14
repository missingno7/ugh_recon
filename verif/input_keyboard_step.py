"""One actual matcher iteration; complete IRQ remains compiled evidence."""
import sys
from pathlib import Path
from closure_support import ROOT,function
from input_build import OUT
from input_limits import cbmc
import input_proofs

def main():
 mode=sys.argv[1] if len(sys.argv)>1 else 'outputs';negative='--negative' in sys.argv;folder=OUT/f'proof-key-step-{mode}{"-negative" if negative else ""}';folder.mkdir(parents=True,exist_ok=True)
 def cut(harness,ignored,inputs,**options):
  code=harness.read_text();body=function((ROOT/'c/dos_input.c').read_text(),'c_HandleKeyboardScanInterrupt');part=body[body.index('        if(rd8(DATA_SEG'):body.index('        if(budget==32767)')].replace('break;','goto stopped;')
  reference='static int reference_candidate(uint16_t index,uint8_t *incoming,unsigned budget) {uint16_t si=0,bx=index;uint8_t matches=*incoming,scan=delivered;int reset=0;'+part+'*incoming=matches;return budget==32767 ? 3 : 0;stopped:*incoming=matches;return reset ? 1 : 2;}\n'
  run=function(code,'input_key_run');changed=run.replace('        switch(request.action)', '''        if(request.action==INPUT_KEY_BOUND) return 3;
        if(request.action==INPUT_KEY_WRITE_INDEX) return 1;
        if(request.action==INPUT_KEY_READ_INDEX) return 2;
        if(request.action==INPUT_KEY_READ_TABLE && request.position==11 && work->stage==1) return 0;
        switch(request.action)''');assert run!=changed;code=code.replace(run,changed)
  old=function(code,'main').rstrip('\r\n');new='''int main(void) {memory[0]=nondet_packet();__CPROVER_assume(memory[0].table[3]<=20);memory[1]=memory[0];delivered=nondet_u8();uint8_t matches=nondet_u8();unsigned budget=nondet_u16();__CPROVER_assume(budget<32768);InputKeyWork work=input_key_begin(delivered,memory[0].index,0);work.matches=matches;work.budget=32768-budget;Regs first=nondet_regs();first.cs=GAME_SEG;Regs second=first;selected=0;int expected=reference_candidate(memory[0].index,&matches,budget);selected=1;'''
  if mode=='dependence':new+='second=nondet_regs();'
  new+='int actual=input_key_run(&second,DATA_SEG,&work,0);CHECK(actual==expected && matches==work.matches,"actual candidate outcome, wrapped match count and final iteration budget");'
  if mode!='frame':new+='''unsigned at=nondet_u16();__CPROVER_assume(at<270);CHECK(memory[0].table[at]==memory[1].table[at],"all candidate/table bytes");at=nondet_u8();__CPROVER_assume(at<24);CHECK(memory[0].actions[at]==memory[1].actions[at],"all action bytes, including high-byte preservation");CHECK(memory[0].index==memory[1].index && memory[0].latest==memory[1].latest,"index and scan latch unchanged before continuation/reset handoff");'''
  if mode=='frame':new+='CHECK(first.ax==second.ax && first.bx==second.bx && first.cx==second.cx && first.dx==second.dx && first.si==second.si && first.di==second.di && first.bp==second.bp && first.sp==second.sp && first.cs==second.cs && first.ds==second.ds && first.es==second.es && first.ss==second.ss && first.ip==second.ip && first.flags==second.flags,"complete candidate register/flag frame");'
  new+='CHECK(counts[0]==0 && counts[1]==0,"candidate decision has no hardware operation");return 0;}'
  assert old in code;code=code.replace(old,reference+new);target=folder/'harness.c';target.write_text(code);options['unwind']=4;options['timeout']=60;options['extra']=[*input_proofs.SOLVER,'--unwindset','input_key_run.0:12,input_key_next.0:3'];return cbmc(target,folder,[*inputs,Path(__file__)],**options)
 input_proofs.cbmc=cut;sys.argv=['input_proofs.py','keyboard',mode,*(['--negative'] if negative else [])];input_proofs.main()
if __name__=='__main__':main()
