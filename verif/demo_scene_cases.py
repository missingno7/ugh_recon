"""Compiled actual-C presentation effects, wrappers, runner and shared cuts."""
import subprocess
from closure_support import ROOT,compile_c,receipt,save
from demo_scene_build import OUT,pair
def run(folder,mutant=None,bridge_mutant=None):
    inputs=pair(folder);path=folder/'pair.inc';text=path.read_text()
    if mutant:text=text.replace((ROOT/'native/demo_presentation.c').as_posix(),mutant.as_posix())
    if bridge_mutant:
        old,new=bridge_mutant;assert old in text;text=text.replace(old,new)
    path.write_text(text)
    # Reuse the exact checked branch bodies from the proof generator, without
    # its symbolic main. These cases cover arbitrary phase cuts independently
    # of the finite whole-run service schedules above.
    from demo_scene_pieces import pieces,modern,reference
    functions='';keys=list(pieces())
    for index,key in enumerate(keys):
        piece=pieces()[key]
        functions+='\n#undef W\n#undef CALL\n#define W(n,v) wr16(r->ds,D(n),(uint16_t)(v))\n#define CALL(n,ret) do {int status=ugh_call_near(G(n),ret,r);if(status)return status;} while(0)\n'
        functions+=f'static int stage_ref_{index}(Regs *r) {{'+reference(piece['fragment'])+'return UGH_OK;}\n'
        functions+='\n#undef W\n#undef CALL\n#define W(n,v) dp_write(r,&plan,D(n),(uint16_t)(v))\n#define CALL(n,ret) do {dp_before(r,&plan,G(n));int status=ugh_call_near(G(n),ret,r);dp_resume(r,&plan);if(status)return status;} while(0)\n'
        functions+=f'static int stage_native_{index}(Regs *r) {{DemoScenePlan plan={{0}};plan.active=1;plan.cursor=(DemoPresentationCursor){{'+piece['kind']+','+piece['phase']+'};'+piece['seam']+modern(piece['fragment'])+'return UGH_OK;}\n'
    functions+='static int stage_execute(unsigned key,Regs *r,int native) {switch(key){\n'
    for index in range(len(keys)):functions+=f'case {index}:return native?stage_native_{index}(r):stage_ref_{index}(r);\n'
    functions+='}return UGH_UNSUPPORTED;}\nstatic void stage_cases(void);\n'
    raw=(ROOT/'verif/demo_scene_harness.c').read_text();a=raw.index('static int execute(');b=raw.index('static void compare(',a)
    raw=raw[:a]+functions+raw[a:];raw=raw.replace(' printf("PASS %llu presentation comparisons',' stage_cases();\n printf("PASS %llu presentation comparisons')
    raw+='''
static void stage_cases(void) {
 for(unsigned key=0;key<27;key++)for(unsigned test=0;test<400;test++) {
  Regs r=seed();r.cs=GAME_SEG;r.ds=DATA_SEG;r.ss=0x9000;r.sp=key==18 || key==25?0xffe:key==26?0xff8:0x1000;
  if(key==14)r.ax=65532u;actor_index=0;cut_services=1;cut_status=UGH_CONTROL_TRANSFER;
  const uint16_t edges[]={0,1,127,128,191,192,193,255,256,257,32767,32768,65532,65535};
  if(test<196){ram[0]=edges[test/14];ram[1]=edges[test%14];ram[3]=edges[(test/14+test%14)%14];}
  for(unsigned i=0;i<4;i++)arbitrary_ram[i]=word();arbitrary_after=r;arbitrary_after.ax=word();arbitrary_after.cx=word();arbitrary_after.flags=word();
  uint16_t before[38],after[38];for(unsigned i=0;i<38;i++)before[i]=ram[i];uint8_t byte_before=width_byte;Regs a=r,b=r;
  modern=0;observations=service_count=frames=0;int left=stage_execute(key,&a,0);expected_observations=observations;
  for(unsigned i=0;i<38;i++){after[i]=ram[i];ram[i]=before[i];}uint8_t byte_after=width_byte;width_byte=byte_before;
  modern=1;observations=service_count=frames=0;int right=stage_execute(key,&b,1);
  CHECK(left==right && equal_regs(a,b) && observations==expected_observations,"complete independent branch-cut state");
  for(unsigned i=0;i<38;i++)CHECK(ram[i]==after[i],"branch-cut RAM frame");CHECK(width_byte==byte_after,"branch-cut byte frame");comparisons++;
 }
}
'''
    source=folder/'harness.c';source.write_text('#include "pair.inc"\n'+raw)
    exe=folder/'cases.exe';built=compile_c([source],exe,[ROOT/'c',ROOT/'native',ROOT/'native/bridge'],['-DACTOR_VERIFY','-Wno-unused-function','-Wno-misleading-indentation','-Wno-parentheses'])
    value=subprocess.run([str(exe)],capture_output=True,text=True)
    result=receipt(built['command'],[*inputs,ROOT/'verif/demo_scene_harness.c',ROOT/'verif/demo_scene_cases.py',ROOT/'verif/demo_scene_pieces.py']+([mutant] if mutant else []),result='PASS' if not value.returncode else 'FAIL',stdout=value.stdout,stderr=value.stderr,returncode=value.returncode);return value,result
def main():
    value,result=run(OUT/'cases');save(OUT/'cases/result.json',result);print(value.stdout+value.stderr);assert not value.returncode
if __name__=='__main__':main()
