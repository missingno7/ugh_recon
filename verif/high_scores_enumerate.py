"""Real compiled qualification, format and row-index finite domains."""
import ctypes as C,sys
from pathlib import Path
from closure_support import ROOT,function,compile_c,receipt,save
from high_scores_build import OUT
from high_scores_spans import sources,format_span,high_editor_span

def main():
    negative='--negative' in sys.argv;folder=OUT/('high-enumeration-negative' if negative else 'high-enumeration');folder.mkdir(parents=True,exist_ok=True)
    menu,helpers,services=sources();native=(ROOT/'native/high_scores.c').read_text();front=''
    if negative:native=native.replace('candidate>=stored','candidate>stored')
    code='#include "platform.h"\n#include "high_scores.h"\n#include "'+(ROOT/'native/bridge/front_end_support.h').as_posix()+'"\n'+native+front+'''
static uint8_t memory[65537];
uint8_t ugh_read(uint32_t address) {return memory[address];}
void ugh_write(uint32_t address,uint8_t value) {memory[address]=value;}
int ugh_call_near(uint16_t target,uint16_t ret,Regs *r) {(void)ret;if(target==G(GetHighScoreDigits)) {r->bx=D(HighScoreRows)+14;return 0;}return 1;}
'''
    code+=function(menu,'c_TestHighScoreQualification').replace('c_TestHighScoreQualification(','reference_qualify(')
    for n in ['GetHighScoreRow','GetHighScoreDigits']:code+=function(helpers,'c_'+n).replace('c_'+n+'(','reference_'+n+'(')
    code+='static void reference_format(Regs *r) {'+format_span()+'}\n'
    numeric=(ROOT/'c/render_primitives.c').read_text()
    for name in ['EncodeTwoDecimalDigits','EncodeFourDecimalDigits','EncodeSixDecimalDigits']:code+=function(numeric,'c_'+name)
    code+='''EXPORT uint32_t enumerate_scores(void) {
 memory[D(DecimalTenDivisor)]=10;memory[D(DecimalHundredDivisor)]=100;
 memory[D(DecimalThousandDivisor)]=232;memory[D(DecimalThousandDivisor)+1]=3;
 memory[D(DecimalTenThousandDivisor)]=16;memory[D(DecimalTenThousandDivisor)+1]=39;
 uint32_t count=0;for(uint32_t score=0;score<1000000;score++) {
  Regs r={0};r.ax=(uint16_t)score;r.dx=(uint16_t)(score>>16);r.si=D(DecimalDigitBuffer);
  if(c_EncodeSixDecimalDigits(&r)) return count;
  uint8_t raw[6],counter=0;for(unsigned i=0;i<6;i++) raw[i]=memory[D(DecimalDigitBuffer)+i];
  r.ax=0;for(unsigned i=0;i<6;i++) {r.si=(uint16_t)i;reference_format(&r);}
  for(unsigned i=0;i<6;i++) {HighFormatDigit result=high_format_digit(raw[i],counter);counter=result.significant;if(result.character!=memory[D(DecimalDigitBuffer)+i]) return count;}
  if(memory[D(DecimalDigitBuffer)+6]!=255) return count;
  count++;
 }return count;
}
'''
    code+='''EXPORT uint32_t enumerate_rows(void) {Regs r={0};uint32_t count=0;for(unsigned row=0;row<256;row++) for(unsigned stride=0;stride<256;stride++) for(unsigned digits=0;digits<2;digits++) {r.cx=(uint16_t)(0xa500u+row);memory[D(HighScoreRowStride)]=(uint8_t)stride;if(digits) reference_GetHighScoreDigits(&r);else reference_GetHighScoreRow(&r);if(r.bx!=(uint16_t)(D(HighScoreRows)+high_row_offset((uint8_t)row,(uint8_t)stride,(int)digits))) return count;count++;}return count;}
EXPORT uint32_t enumerate_format(void) {Regs r={0};uint32_t count=0;for(unsigned digit=0;digit<256;digit++) for(unsigned significant=0;significant<256;significant++) {r.si=0;r.ax=(uint16_t)(significant*256u);memory[D(DecimalDigitBuffer)]=(uint8_t)digit;reference_format(&r);HighFormatDigit result=high_format_digit((uint8_t)digit,(uint8_t)significant);if(result.character!=memory[D(DecimalDigitBuffer)] || result.significant!=(uint8_t)(r.ax>>8)) return count;count++;}return count;}
EXPORT uint32_t enumerate_qualification(void) {Regs r={0};uint32_t count=0;for(unsigned position=0;position<6;position++) for(unsigned a=0;a<256;a++) for(unsigned b=0;b<256;b++) {for(unsigned i=0;i<6;i++) {memory[D(DecimalDigitBuffer)+i]='3';memory[D(HighScoreRows)+14+i]='3';}memory[D(DecimalDigitBuffer)+position]=(uint8_t)a;memory[D(HighScoreRows)+14+position]=(uint8_t)b;r.cx=0;r.flags=0xed7;reference_qualify(&r);HighQualification result={0,0,0};while(!result.done) high_compare_step(&result,memory[D(DecimalDigitBuffer)+result.position],memory[D(HighScoreRows)+14+result.position]);if(!!(r.flags&CF)!=result.qualifies || (uint8_t)r.ax!=memory[D(DecimalDigitBuffer)+result.position]) return count;count++;}return count;}
'''
    # Full post-BIOS editor step, all positions and characters. Captured writes
    # include raw out-of-range addresses; none is clipped to the edit field.
    code+='''static uint32_t addresses[16];static uint8_t values[16];static unsigned count_writes;
static void capture_write(uint32_t address,uint8_t value) {addresses[count_writes]=address;values[count_writes++]=value;}
#define ugh_write capture_write
#define MCALL(n,ret) do {(void)(ret);} while(0)
static int reference_edit(Regs *r) {'''+high_editor_span()+'''}
static int actual_edit(Regs *r) {'''+high_editor_span(True)+'''}
EXPORT uint32_t enumerate_editor(void) {uint32_t count=0;for(unsigned position=0;position<65536;position++) for(unsigned ch=0;ch<256;ch++) {Regs r={0},s={0};r.si=(uint16_t)position;r.ax=(uint16_t)(0xa500u+ch);r.flags=0xed7;s=r;count_writes=0;int first=reference_edit(&r);unsigned n=count_writes;uint32_t expected_addresses[16];uint8_t expected_values[16];for(unsigned i=0;i<n;i++) {expected_addresses[i]=addresses[i];expected_values[i]=values[i];}count_writes=0;int second=actual_edit(&s);if(first!=second || r.ax!=s.ax || r.si!=s.si || r.flags!=s.flags || n!=count_writes) return count;for(unsigned i=0;i<n;i++) if(expected_addresses[i]!=addresses[i] || expected_values[i]!=values[i]) return count;count++;}return count;}
'''
    # Macro substitution cannot replace ugh.h's already parsed inline wr8/wr16.
    # Route all writes through the capture shim globally, with capture disabled
    # for other enumerations, instead.
    code=code.replace('static uint8_t memory[65537];','static uint8_t memory[65537];static int capturing;static uint32_t addresses[16];static uint8_t values[16];static unsigned count_writes;')
    code=code.replace('memory[address]=value;','if(capturing) {addresses[count_writes]=address;values[count_writes++]=value;}else memory[address]=value;')
    a=code.index('static uint32_t addresses[16];',code.index('EXPORT uint32_t enumerate_qualification'))
    b=code.index('static int reference_edit',a);code=code[:a]+'#define MCALL(n,ret) do {(void)(ret);} while(0)\n'+code[b:]
    code=code.replace('EXPORT uint32_t enumerate_editor(void) {uint32_t count=0;','EXPORT uint32_t enumerate_editor(void) {capturing=1;uint32_t count=0;')
    path=folder/'enumerate.c';path.write_text(code);dllpath=folder/'enumerate.dll';built=compile_c([path],dllpath,[ROOT/'c',ROOT/'native'],['-shared']);dll=C.CDLL(str(dllpath));rows={}
    for name,expected in [('rows',131072),('format',65536),('qualification',393216),('scores',1000000),('editor',16777216)]:
        f=getattr(dll,'enumerate_'+name);f.restype=C.c_uint32;n=f();rows[name]=n;print(name,n,flush=True)
        assert n<expected if negative and name=='qualification' else n==expected,(name,n)
    save(folder/'result.json',receipt([sys.executable,'verif/high_scores_enumerate.py',*sys.argv[1:]],[Path(__file__),ROOT/'verif/high_scores_spans.py',ROOT/'native/high_scores.c',ROOT/'native/high_scores.h',ROOT/'native/front_end.h',ROOT/'native/bridge/high_scores_bridge.c',ROOT/'native/bridge/front_end_support.h',ROOT/'c/menu.c',ROOT/'c/menu_helpers.c',ROOT/'c/render_primitives.c'],result='PASS',domains=rows,negative_detected=negative,build=built))
if __name__=='__main__':main()
