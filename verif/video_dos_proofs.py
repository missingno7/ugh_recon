"""Actual-C split properties. Resource-limited; no whole-device state profile."""
import argparse
from pathlib import Path
from closure_support import ROOT,function
from video_dos_build import OUT
from video_dos_limits import cbmc
from video_dos_enumerate import scale_span
from adlx_lifetime_proofs import SOLVER

def main():
    p=argparse.ArgumentParser();p.add_argument('entry',choices=['scale','fade','range','retrace','duplicate','clear','chunky','swap','mode','timeout']);p.add_argument('--negative',action='store_true');a=p.parse_args()
    folder=OUT/f'proof-{a.entry}{"-negative" if a.negative else ""}';folder.mkdir(parents=True,exist_ok=True)
    native=(ROOT/'native/video_dos.c').read_text();bridge=(ROOT/'native/bridge/video_dos_bridge.c').read_text();video=(ROOT/'c/video.c').read_text();dos=(ROOT/'c/dos_input.c').read_text();game=(ROOT/'c/game_services.c').read_text()
    if a.negative:
        old,new={'scale':('(uint8_t)(product>>8)','(uint8_t)(product>>7)'), 'fade':('fading_out ? -4 : 4','fading_out ? -4 : 8'), 'range':('last-first','last-first-1u'), 'retrace':('status&8','status&4'), 'chunky':('1u<<cursor->plane','2u<<cursor->plane'), 'swap':('pages->displayed=draw','pages->displayed=pages->draw')}[a.entry]
        assert old in native;native=native.replace(old,new)
    code='#include "platform.h"\n#include "video_dos.h"\n#define CHECK(c,m) __CPROVER_assert(c,m)\nuint8_t nondet_u8(void);uint16_t nondet_u16(void);uint32_t nondet_u32(void);Regs nondet_regs(void);\n'+native
    unwind=8;extra=[]
    if a.entry=='scale':
        code+='''static uint8_t incoming,written;
uint8_t ugh_read(uint32_t address) {CHECK(address==(uint32_t)GAME_SEG*16+G(BaseRgbPalette),"only selected component read");return incoming;}
void ugh_write(uint32_t address,uint8_t value) {CHECK(address==(uint32_t)GAME_SEG*16+G(FadedRgbPalette),"only selected component written");written=value;}
static void reference(Regs *r) {'''+scale_span()+'''}
int main(void) {Regs r=nondet_regs();r.cs=GAME_SEG;r.bx=0;incoming=nondet_u8();r.cx=nondet_u16();reference(&r);VideoScaled actual=video_palette_scale(incoming,r.cx);CHECK(r.ax==actual.low && r.dx==actual.high && written==actual.value,"all product outputs");CHECK(!!(r.flags&CF)==(actual.high!=0) && !!(r.flags&OF)==(actual.high!=0),"MUL carry and overflow");return 0;}
'''
    elif a.entry=='fade':
        first=function(video,'c_FadePaletteIn');first=first[first.index('        r->cx=add16'):first.index('    return UGH_OK;')].replace('    } while(r->cx<=256);','return r->cx<=256;')
        second=function(video,'c_FadePaletteOut');second=second[second.index('        r->cx=sub16'):second.index('    r->cx=pop')].replace('    } while(!(r->flags&SF));','return !(r->flags&SF);')
        code+='static int first(Regs *r) {'+first+'}\nstatic int second(Regs *r) {'+second+'}\nint main(void) {uint16_t value=nondet_u16();Regs r=nondet_regs();r.cx=value;int out=nondet_u8()&1;int again=out ? second(&r) : first(&r);uint16_t actual=video_fade_step(value,out);CHECK(actual==r.cx && again==video_fade_continue(actual,out),"actual live-factor tail over all words and both directions");return 0;}'
    elif a.entry=='range':
        body=function(video,'upload_range');part=body[body.index('r->ds=r->es'):body.index('    do {')]
        code+='static uint8_t index_output;void platform_out(uint16_t port,unsigned size,uint32_t value) {CHECK(port==0x3c8 && size==1,"one DAC index byte");index_output=(uint8_t)value;}\n'+function(video,'inc')+'static void reference(Regs *r) {'+part+'}\nint main(void) {Regs r=nondet_regs();uint16_t origin=r.di,indices=r.bx;int reverse=!!(r.flags&DF);reference(&r);VideoPaletteRange range=video_palette_range(origin,(uint8_t)indices,(uint8_t)(indices>>8),reverse);CHECK(index_output==(uint8_t)indices && range.cursor==r.si && range.entries==r.cx,"inclusive wrapped byte range and unconditional forward first-entry offset");uint16_t at=video_palette_advance(&range);CHECK(at==r.si && range.cursor==(uint16_t)(r.si+(reverse ? -1 : 1)),"incoming direction byte traversal");return 0;}'
    elif a.entry=='retrace':
        part=function(dos,'retrace');part=part[part.index('        set_al'):part.index('    }\n    return UGH_BUDGET;')]
        code+='''Devices ugh_devices;static uint8_t delivered;
uint32_t platform_in(uint16_t port,unsigned size) {CHECK(port==0x3da && size==1,"one status delivery");return delivered;}
static int reference(Regs *r,int active,unsigned budget) {r->dx=0x3da;'''+part+'''return budget==999999 ? UGH_BUDGET : -1;}
int main(void) {Regs r=nondet_regs();delivered=nondet_u8();int active=nondet_u8()&1;unsigned budget=nondet_u32();__CPROVER_assume(budget<1000000);ugh_devices.error=0;int expected=reference(&r,active,budget);VideoRetrace wait={1000000-budget,(uint8_t)active};int again=video_retrace_delivery(&wait,delivered);int actual=again==0 ? UGH_OK : again<0 ? UGH_BUDGET : -1;CHECK(actual==expected && wait.budget==999999-budget,"actual status level predicate and diagnostic final poll");return 0;}
'''
    elif a.entry in ['duplicate','clear','chunky','swap']:
        # Ordered physical byte accesses model a single iteration, including
        # contiguous high bytes at FFFF. No whole-buffer disjointness needed.
        code+='''typedef struct Event {uint32_t address;uint8_t value;} Event;
static Event writes[2][4],reads[2][2];static unsigned nw[2],nr[2],side;static uint16_t word;
uint8_t ugh_read(uint32_t address) {CHECK(nr[side]<2,"read footprint");uint8_t value=(uint8_t)(word>>(8u*nr[side]));reads[side][nr[side]].address=address;reads[side][nr[side]].value=value;nr[side]++;return value;}
void ugh_write(uint32_t address,uint8_t value) {CHECK(nw[side]<4,"write footprint");writes[side][nw[side]].address=address;writes[side][nw[side]].value=value;nw[side]++;}
static void equal(Regs r,Regs s) {CHECK(r.ax==s.ax && r.bx==s.bx && r.cx==s.cx && r.dx==s.dx && r.si==s.si && r.di==s.di && r.bp==s.bp && r.sp==s.sp && r.cs==s.cs && r.ds==s.ds && r.es==s.es && r.ss==s.ss && r.ip==s.ip && r.flags==s.flags,"complete step ABI frame");CHECK(nr[0]==nr[1] && nw[0]==nw[1],"access counts");for(unsigned i=0;i<nr[0];i++) CHECK(reads[0][i].address==reads[1][i].address && reads[0][i].value==reads[1][i].value,"ordered read addresses");for(unsigned i=0;i<nw[0];i++) CHECK(writes[0][i].address==writes[1][i].address && writes[0][i].value==writes[1][i].value,"ordered physical byte writes");}
'''
        if a.entry=='duplicate':
            ref=function(dos,'c_DuplicateSourcePaletteHalves');ref=ref[ref.index('        r->ax=rd16'):ref.index('    } while')]
            actual=function(bridge,'c_DuplicateSourcePaletteHalves');actual=actual[actual.index('        VideoDuplicateTransfer'):actual.index('    } while')]
            code+='static void reference(Regs *r) {'+ref+'}\nstatic void actual(Regs *r) {VideoCopyCursor cursor={r->si,r->di,r->cx,(int8_t)(r->flags&DF ? -1 : 1)};'+actual+'}\nint main(void) {Regs r=nondet_regs();__CPROVER_assume(r.cx>=1 && r.cx<=192);Regs s=r;word=nondet_u16();side=0;reference(&r);side=1;actual(&s);equal(r,s);return 0;}'
        elif a.entry=='clear':
            ref=function(video,'c_ClearAllVgaPlanes');ref=ref[ref.index('        wr16'):ref.index('    } while')]
            actual=function(bridge,'c_ClearAllVgaPlanes');actual=actual[actual.index('        wr16'):actual.index('    } while')]
            code+='static void reference(Regs *r) {'+ref+'}\nstatic void actual(Regs *r) {VideoClearCursor cursor={r->di,r->cx,(int8_t)(r->flags&DF ? -1 : 1)};'+actual+'}\nint main(void) {Regs r=nondet_regs();r.ax=0;r.es=0xa000;__CPROVER_assume(r.cx>=1 && r.cx<=32768);Regs s=r;side=0;reference(&r);side=1;actual(&s);equal(r,s);return 0;}'
        elif a.entry=='chunky':
            ref=function(game,'c_UploadChunkyImageToVgaPlanes');ref=ref[ref.index('            set_al'):ref.index('        }\n        r->di=')]
            trailer=function(game,'c_UploadChunkyImageToVgaPlanes');trailer=trailer[trailer.index('        r->di='):trailer.index('    } while')]
            actual=function(bridge,'c_UploadChunkyImageToVgaPlanes');actual=actual[actual.index('        set_al(r,video_chunky_mask'):actual.index('    } while')]
            code+='''static Event ports[2];
void platform_out(uint16_t port,unsigned size,uint32_t value) {CHECK(size==1,"one mask byte");ports[side].address=port;ports[side].value=(uint8_t)value;}
static void reference(Regs *r,unsigned plane) {'''+ref+'if(plane==3) {'+trailer+'}}\nstatic void actual(Regs *r,VideoChunkyCursor cursor) {'+actual+'}\nint main(void) {Regs r=nondet_regs();unsigned plane=nondet_u8();__CPROVER_assume(plane<4);uint32_t remaining=nondet_u32();__CPROVER_assume(remaining>=1 && remaining<=65536);r.cx=(uint16_t)remaining;Regs s=r;word=nondet_u16();VideoChunkyCursor cursor={r.si,r.di,remaining,(uint8_t)plane,(int8_t)(r.flags&DF ? -1 : 1)};side=0;reference(&r,plane);side=1;actual(&s,cursor);equal(r,s);CHECK(ports[0].address==ports[1].address && ports[0].value==ports[1].value,"plane mask order 1,2,4,8");return 0;}'
        else:
            # Source and destination pointer cells are distinct fixed fields.
            code=code[:code.index('typedef struct Event')]
            ref=function(video,'c_SwapAndDisplayVgaPage');ref=ref[ref.index('    r->bx=rd16'):ref.index('    int status=call')]
            actual=function(bridge,'c_SwapAndDisplayVgaPage');actual=actual[actual.index('    VideoPages'):actual.index('    int status=call')]
            code+='''static uint8_t memory[2][4];static unsigned side;
uint8_t ugh_read(uint32_t address) {uint32_t at=address-(uint32_t)GAME_SEG*16-G(DisplayedVgaPagePointer);CHECK(at<2 || (at>=4 && at<6),"two page offset cells read");return memory[side][at<2 ? at : at-2];}
void ugh_write(uint32_t address,uint8_t value) {uint32_t at=address-(uint32_t)GAME_SEG*16-G(DisplayedVgaPagePointer);CHECK(at<2 || (at>=4 && at<6),"offset words only; bank words framed");memory[side][at<2 ? at : at-2]=value;}
static void reference(Regs *r) {'''+ref+'}\nstatic void actual(Regs *r) {'+actual+'}\nint main(void) {for(unsigned i=0;i<4;i++) memory[0][i]=memory[1][i]=nondet_u8();Regs r=nondet_regs();r.cs=GAME_SEG;Regs s=r;side=0;reference(&r);side=1;actual(&s);CHECK(r.bx==s.bx,"new displayed offset ABI");for(unsigned i=0;i<4;i++) CHECK(memory[0][i]==memory[1][i],"actual exchanged offsets");return 0;}'
    elif a.entry=='mode':
        for helper in ['inc','out_al','rmw']:code+=function(video,helper)
        code+='static int call(Regs *r,uint16_t target,uint16_t ret) {(void)r;(void)ret;return target==G(BlackenVgaPalette) ? 0 : 1;}\nint c_SwapAndDisplayVgaPage(Regs *r) {(void)r;return 0;}\n'
        code+=function(video,'configure').replace('configure(','reference(')+function(bridge,'configure').replace('configure(','actual(')
        code+='''typedef struct Event {uint32_t port,size,value;} Event;static Event events[2][32],stores[2][4];static unsigned side,count[2],nw[2],nr[2];static uint8_t delivered[5];
void platform_out(uint16_t port,unsigned size,uint32_t value) {CHECK(count[side]<32,"mode prefix event bound");events[side][count[side]].port=port;events[side][count[side]].size=size;events[side][count[side]].value=value;count[side]++;}
uint32_t platform_in(uint16_t port,unsigned size) {CHECK(nr[side]<5,"five RMW reads");uint8_t value=delivered[nr[side]++];platform_out(port,size,value);return value;}
uint8_t ugh_read(uint32_t at) {(void)at;CHECK(0,"no pointer RAM read before wait");return 0;}
void ugh_write(uint32_t at,uint8_t value) {CHECK(nw[side]<4,"only geometry header writes");stores[side][nw[side]].port=at;stores[side][nw[side]].value=value;nw[side]++;}
int main(void) {for(unsigned i=0;i<5;i++) delivered[i]=nondet_u8();Regs r=nondet_regs();Regs s=r;int gameplay=nondet_u8()&1;side=0;int first=reference(&r,gameplay);side=1;int second=actual(&s,gameplay);CHECK(first==second,"service stop");CHECK(r.ax==s.ax && r.dx==s.dx && r.flags==s.flags,"mode arithmetic flags");CHECK(count[0]==count[1] && nr[0]==nr[1] && nw[0]==nw[1],"prefix footprint");for(unsigned i=0;i<count[0];i++) CHECK(events[0][i].port==events[1][i].port && events[0][i].size==events[1][i].size && events[0][i].value==events[1][i].value,"all ordered mode writes and reads");for(unsigned i=0;i<nw[0];i++) CHECK(stores[0][i].port==stores[1][i].port && stores[0][i].value==stores[1][i].value,"height and copy count");return 0;}
'''
        unwind=33
    elif a.entry=='timeout':
        for helper in ['push','pop','call']:code+=function(video,helper)
        code+=function(video,'c_WaitForInputOrRetraceTimeout').replace('c_WaitForInputOrRetraceTimeout(','reference(')+function(bridge,'c_WaitForInputOrRetraceTimeout').replace('c_WaitForInputOrRetraceTimeout(','actual(')
        code+='''static uint8_t memory[2][64],changed[3],buttons[3];static unsigned side,scans[2],samples[2],count[2];static uint16_t targets[2][32],returns[2][32];
uint8_t ugh_read(uint32_t at) {CHECK(at<64,"canonical active frame read");return memory[side][at];}
void ugh_write(uint32_t at,uint8_t value) {CHECK(at<64,"canonical active frame write");memory[side][at]=value;}
int ugh_call_near(uint16_t target,uint16_t ret,Regs *r) {CHECK(count[side]<32,"call log bound");targets[side][count[side]]=target;returns[side][count[side]++]=ret;if(target==G(PollKeyboardScanChange)) {unsigned at=scans[side]++;if(at==0) r->ax=0x1234;else {CHECK(at<=3,"three classified scans");r->ax=(uint16_t)(0x5a+256u*changed[at-1]);}}else if(target==G(SampleJoystickAxesAndButtons)) {unsigned at=samples[side]++;CHECK(at<3,"three button samples");flag(r,ZF,!buttons[at]);}return 0;}
int platform_service_point_at(ServicePoint point,uint16_t bank,uint16_t at,Regs *r) {(void)bank;(void)r;CHECK(point==SERVICE_IO && at==G(loc_449B),"actual input service site");return 0;}
int main(void) {for(unsigned i=0;i<3;i++) {changed[i]=nondet_u8();buttons[i]=nondet_u8();}Regs r=nondet_regs();r.ss=0;r.sp=48;__CPROVER_assume(r.cx>=1 && r.cx<=3);Regs s=r;side=0;int first=reference(&r);side=1;int second=actual(&s);CHECK(first==second && r.ax==s.ax && r.cx==s.cx && r.dx==s.dx && r.sp==s.sp && r.flags==s.flags,"wait output and frame");CHECK(count[0]==count[1] && scans[0]==scans[1] && samples[0]==samples[1],"external service counts");for(unsigned i=0;i<count[0];i++) CHECK(targets[0][i]==targets[1][i] && returns[0][i]==returns[1][i],"call and return-site order");for(unsigned i=0;i<64;i++) CHECK(memory[0][i]==memory[1][i],"same temporary stack writes");return 0;}
'''
        unwind=65;extra=['--unwindset','reference.0:4,actual.0:18,video_timeout_next.0:3']
    harness=folder/'harness.c';harness.write_text(code)
    result=cbmc(harness,folder,[Path(__file__),ROOT/'verif/video_dos_enumerate.py',ROOT/'native/video_dos.c',ROOT/'native/video_dos.h',ROOT/'native/bridge/video_dos_bridge.c',ROOT/'c/video.c',ROOT/'c/dos_input.c',ROOT/'c/game_services.c'],unwind=unwind,timeout=60,extra=[*SOLVER,*extra])
    print(a.entry,result['result'],result['seconds'],result['failures'][:3],flush=True)
    assert result['result']==('FAIL' if a.negative else 'PASS'),result['result']
if __name__=='__main__':main()
