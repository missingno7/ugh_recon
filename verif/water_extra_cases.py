"""Independent complete eligibility/competition and exact-boundary fixtures."""
import subprocess
from pathlib import Path
from closure_support import ROOT,compile_c,receipt,save
from water_build import OUT,pair
EXTRA=r'''
 for(unsigned pair=0;pair<3;pair++) for(unsigned count=1;count<=2;count++) for(unsigned mask=0;mask<64;mask++) for(unsigned which=0;which<3;which++) {
  Regs r=seed(pair);ram.players=(uint16_t)count;ram.actor[9]=1;ram.actor[4]=1;
  for(unsigned i=0;i<2;i++) {
   ram.craft[1][i]=(mask&(1u<<(3*i)))?78:79;
   ram.craft[2][i]=(mask&(2u<<(3*i)))?0:65535u;
   ram.craft[3][i]=(mask&(4u<<(3*i)))?0:7;
   ram.craft[0][i]=82;
  }
  unsigned mode=which==0?5:which==1?8:6;WaterRam before=ram;compare(mode,r);ram=before;
  int expected=-1;
  if(which<2 && (which==1 || pair!=1)) for(unsigned i=0;i<count;i++) {
   int eligible=ram.craft[1][i]==78 && !ram.craft[3][i] && (which==1 || !ram.craft[2][i]);
   if(eligible) {expected=(int)i;break;}
  }
  WaterPlan p;CHECK(water_prepare(&r,(PassengerWaterEntry)mode,&p),"independent candidate preparation");
  CHECK(p.result.selected==expected,"native selected craft equals independent complete eligibility table");
  if(which==0 && pair==1) CHECK(p.result.next==PW_NEXT_SINK,"second water identity times out despite eligible craft");
 }
 static const uint16_t edges[]={0,1,31,32,63,64,65,0x17ff,0x1800,0x1801,0x7fff,0x8000,0xe7ff,0xe800,0xe801,0xffc0,0xffff};
 for(unsigned mode=1;mode<=8;mode++) for(unsigned i=0;i<sizeof(edges)/sizeof(edges[0]);i++) for(unsigned j=0;j<sizeof(edges)/sizeof(edges[0]);j++) {
  Regs r=seed((i+j)%3);ram.actor[22]=edges[i];ram.actor[11]=edges[j];ram.actor[14]=edges[j];ram.surface=edges[i];
  ram.actor[9]=ram.actor[4]=edges[j];ram.actor[17]=edges[i];ram.type[31]=edges[j];
  if(ram.actor[17]==1) ram.actor[16]=65534u;compare(mode,r);
 }
'''
def run(folder,mutant=None):
    inputs=pair(folder)
    if mutant:
        original=ROOT/'native/passenger_water.c';inc=folder/'pair.inc';inc.write_text(inc.read_text().replace(original.as_posix(),mutant.as_posix()))
    raw=(ROOT/'verif/water_harness.c').read_text();marker=' for(unsigned test=0;test<12000;test++)';assert raw.count(marker)==1;raw=raw.replace(marker,EXTRA+marker,1)
    source=folder/'harness.c';source.write_text('#include "pair.inc"\n'+raw);exe=folder/'cases.exe';built=compile_c([source],exe,[ROOT/'c',ROOT/'native',ROOT/'native/bridge'],['-DACTOR_VERIFY','-Wno-unused-function','-Wno-misleading-indentation']);value=subprocess.run([str(exe)],capture_output=True,text=True)
    return value,receipt(built['command'],[*inputs,ROOT/'verif/water_harness.c',Path(__file__)]+([mutant] if mutant else []),result=('DETECTED' if value.returncode==23 else 'MISSED') if mutant else ('PASS' if not value.returncode else 'FAIL'),stdout=value.stdout,stderr=value.stderr)
def main():
    folder=OUT/'extra-cases';value,result=run(folder);save(folder/'result.json',result);print(value.stdout+value.stderr);assert not value.returncode
if __name__=='__main__':main()
