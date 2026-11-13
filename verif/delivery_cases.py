"""Additional actual-C carrier, scheduling and longer-resource matrices."""
import argparse,subprocess
from pathlib import Path
from closure_support import ROOT,compile_c,receipt,save
from delivery_build import OUT,pair

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--selection-mutant',action='store_true');a=p.parse_args()
    folder=OUT/('cases-selection-mutant' if a.selection_mutant else 'cases');inputs=pair(folder);source=ROOT/'verif/delivery_harness.c';raw=source.read_text()
    if a.selection_mutant:
        core=ROOT/'native/passenger_delivery.c';text=core.read_text();old='if(center==target) {result->next=PD_NEXT_BOARD;return;}'
        assert text.count(old)==1;mutant=folder/core.name;mutant.write_text(text.replace(old,'if(center==target) {result->next=PD_NEXT_BOARD;result->selected^=1;return;}'))
        inc=folder/'pair.inc';inc.write_text(inc.read_text().replace(core.as_posix(),mutant.as_posix()));inputs+=[mutant]
    # Expand only the RAM accessor's declared immutable vector resources, not
    # either implementation. Four live words instead of the symbolic bound two.
    raw=raw.replace('animation[4][3]','animation[4][5]').replace('0x0e20,0x0e2a,0x0e32,0x0e46','0x0e20,0x0e40,0x0e60,0x0e80')
    raw=raw.replace('address<vector_bases[i]+6u','address<vector_bases[i]+10u').replace('ram.animation[i][2]=65535u','ram.animation[i][4]=65535u')
    raw=raw.replace('ram.animation[i][1]=(uint16_t)(200+i);','ram.animation[i][1]=(uint16_t)(200+i);ram.animation[i][2]=(uint16_t)(300+i);ram.animation[i][3]=(uint16_t)(400+i);')
    extra='''
    /* Observe the native selected output itself, independently of the shell's
     * retained DI. The current production bridge does not bind this field at
     * its immediate tail; this is an explicit recorded continuation finding. */
    for(unsigned mode=1;mode<=7;mode+=2) for(unsigned count=1;count<=2;count++)
    for(unsigned p0=0;p0<2;p0++) for(unsigned p1=0;p1<2;p1++)
    for(unsigned busy0=0;busy0<2;busy0++) for(unsigned busy1=0;busy1<2;busy1++) {
        r=seed();ram.player_count=(uint16_t)count;ram.player_bytes=(uint16_t)(2u*count);ram.actor[4]=1;
        ram.players[3][0]=p0?0:65535u;ram.players[3][1]=p1?0:65535u;
        ram.players[4][0]=(uint16_t)busy0;ram.players[4][1]=(uint16_t)busy1;
        int empty=mode==1 || mode==5;int expected=-1;
        if(p0 && (!empty || !busy0)) expected=0;
        else if(count==2 && p1 && (!empty || !busy1)) expected=1;
        DeliveryPlan candidate;CHECK(delivery_prepare(&r,(PassengerDeliveryEntry)mode,&candidate),"prepare candidate fixture");
        CHECK(candidate.result.selected==expected,"native selected craft independently matches finite competition contract");
    }
    for(unsigned stored=0;stored<2;stored++) for(unsigned incoming=0;incoming<2;incoming++) {
        r=seed();ram.actor[4]=(uint16_t)(2u*stored);r.di=(uint16_t)(2u*incoming);
        ram.players[0][0]=1600;ram.players[0][1]=6400;ram.players[6][0]=700;ram.players[6][1]=900;
        ram.players[4][0]=7;ram.players[4][1]=9;ram.players[5][0]=11;ram.players[5][1]=13;
        ram.multiplier=65535u;ram.limit=0;compare(11,r);
        CHECK(ram.players[4][incoming]==0 && ram.players[5][incoming]==0,"delivery clears incoming craft");
        CHECK(ram.actor[10]==(uint16_t)((stored?6400u:1600u)+256u),"delivery positions from stored carrier");
        CHECK(((uint32_t)ram.score_high<<16|ram.score_low)==(stored?900u:700u)*65535u,"delivery awards stored carrier fare");
    }
    for(unsigned mode=0;mode<12;mode++) {
        r=seed();ram.player_count=1;ram.player_bytes=2;if(mode==8) ram.actor[0]=(uint16_t)(land_base+74u);compare(mode,r);
    }
    for(unsigned difficulty=0;difficulty<3;difficulty++) for(unsigned carrier=0;carrier<2;carrier++) {
        r=seed();ram.difficulty=(uint16_t)difficulty;ram.actor[4]=(uint16_t)(2u*carrier);r.di=(uint16_t)(2u*carrier);compare(11,r);
    }
    static const uint16_t timers[]={0,1,2,65535u},periods[]={0,1,65535u};
    for(unsigned mode=1;mode<=7;mode+=2) for(unsigned t=0;t<4;t++) for(unsigned p=0;p<3;p++) for(unsigned cursor=0;cursor<5;cursor++) {
        r=seed();ram.actor[17]=timers[t];ram.actor[16]=cursor==4?65534u:(uint16_t)(2u*cursor);ram.types[0][31]=periods[p];
        /* Non-due approach reads the current frame rather than incrementing. */
        if(mode==7 && timers[t]!=1 && cursor==4) ram.actor[16]=8;
        ram.actor[4]=1;compare(mode,r);
    }
    for(unsigned count=1;count<=2;count++) for(unsigned first=0;first<2;first++) for(unsigned second=0;second<2;second++) for(unsigned mode=1;mode<=7;mode+=2) {
        r=seed();ram.player_count=(uint16_t)count;ram.player_bytes=(uint16_t)(2u*count);ram.players[4][0]=(uint16_t)first;ram.players[4][1]=(uint16_t)second;compare(mode,r);
    }
'''
    marker='    for(unsigned test=0;test<6000;test++) {';assert raw.count(marker)==1;raw=raw.replace(marker,extra+marker)
    harness=folder/'harness.c';harness.write_text('#include "pair.inc"\n'+raw);exe=folder/'cases.exe';built=compile_c([harness],exe,[ROOT/'c',ROOT/'native',ROOT/'native/bridge'],['-DACTOR_VERIFY'])
    run=subprocess.run([str(exe)],capture_output=True,text=True)
    result=('DETECTED' if run.returncode==23 else 'MISSED') if a.selection_mutant else ('PASS' if run.returncode==0 else 'FAIL')
    save(folder/'result.json',receipt(built['command'],[*inputs,source,Path(__file__)],result=result,stdout=run.stdout,stderr=run.stderr,domain='Original finite/generated corpus plus independent native candidate fixture (four handlers x two player counts x sixteen match/busy combinations), all2x2 incoming/stored carriers, twelve one-player entries, all three difficulties/two carriers, animation timer/period/cursor and craft-competition matrices; four live words per vector.'))
    print(result+' '+run.stdout+run.stderr,flush=True);assert result in ('PASS','DETECTED')
if __name__=='__main__':main()
