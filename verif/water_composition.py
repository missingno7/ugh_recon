"""Actual three-unit tails vs L0, with child native/fallback audit counters."""
import ctypes as C,json,re,sys
from pathlib import Path
from closure_support import ROOT,compile_c,function,receipt,save
from water_build import OUT,build,includes
import contacts_reference as reference
reference.OUT=OUT/'reference'
sys.path.insert(0,str(ROOT/'tools'))
import difftest,nbuild
from emu import DATA_SEG
import delivery_shells,itinerary_shells

def instrumented():
    original=build();built=json.loads((OUT/'build.json').read_text());folder=original.parent/'composition';folder.mkdir();sources=[]
    for value in built['command'][built['command'].index('-o')+2:]:
        path=Path(value)
        if path.name in ('passenger_delivery_bridge.c','passenger_itinerary_bridge.c'):
            names=delivery_shells.NAMES if 'delivery' in path.name else itinerary_shells.NAMES;prefix='delivery' if 'delivery' in path.name else 'itinerary';text=includes(path.read_text(),path)
            text='#include "ugh.h"\nEXPORT uint32_t '+prefix+'_cross_audit['+str(2*len(names))+'];\n'+text
            for i,name in enumerate(names):
                old=function(text,'c_'+name);new=old.replace('{',f'{{{prefix}_cross_audit[{i}]++;',1).replace('l1_'+name+'(r)',f'({prefix}_cross_audit[{i+len(names)}]++,l1_{name}(r))');text=text.replace(old,new)
            path=folder/path.name;path.write_text(text)
        sources.append(path)
    dll=folder/'composition.dll';compile_c(sources,dll,[ROOT/'c',ROOT/'native',ROOT/'native/bridge'],['-shared','-DACTOR_VERIFY']);return nbuild.load_l1(dll)

def setup(pair,variant,selection):
    def arrange(m):
        suite=difftest.load_suite('actors_states');suite.fixture(m,actor=['Data_776A','Data_77FE','Data_7892'][pair]);at=suite.ACTOR
        for name,value in [('ActorPlatformOrScriptDone',3),('ActorSourcePlatformByteIndices',6),('ActorDestinationPlatforms',3),('ActorDestinationPlatformByteIndices',6),('ActorAnimationCountdowns',2),('ActorMotionWaitOrDemoRepeats',1),('ActorPhaseOrDemoLoopCursor',1),('ActorPixelY',100),('ActorVerticalOrDemoPeriod',65500)]:m.ww('DGROUP:'+name,value,at)
        m.ww('DGROUP:WaterYPixels',100);m.ww('DGROUP:PlayerCount',2);m.ww('DGROUP:PlayerArrayBytes',4);m.ww('DGROUP:ScoreMultiplier',1);m.ww('DGROUP:SelectedDifficulty',0);m.ww('DGROUP:MultiplierLimitsByDifficulty',0)
        anchor=m.rw('DGROUP:'+['Data_7720','Data_77B4','Data_7848'][pair]);cached=120-anchor;m.ww('DGROUP:ActorPixelX',cached,at);water_anchor=m.rw('DGROUP:'+['Data_776A','Data_77FE','Data_7892'][pair]);target=(cached+water_anchor-16)&65535
        for i in (0,2):
            for name,value in [('PlayerYPixels',82 if i==selection else 20),('PlayerVerticalVelocities',0),('PlayerCarriedKinds',0),('PlayerPixelX',target),('PlayerX32',target*32),('PlayerY32',82*32),('PlayerPlatformIndices',3)]:m.ww('DGROUP:'+name,value,i)
        m.ww('DGROUP:PlatformArrivalPointsX',120,6)
        m.write(DATA_SEG,suite.JOURNEY,(3).to_bytes(2,'little')+b'\0\0'+(3).to_bytes(2,'little')+b'\0\0'+b'\xff\xff'*4)
        if variant=='cross':m.ww('DGROUP:ActorY32',3000,at)
        if variant=='question':
            for i in (0,2):m.ww('DGROUP:PlayerYPixels',20,i)
        if variant=='inbound':
            m.ww('DGROUP:ActorDescriptors',m.off('DGROUP:'+['Data_7720','Data_77B4','Data_7848'][pair]),at);m.ww('DGROUP:ActorPixelY',150,at)
    return arrange

def main():
    reference.prepare_reference(local=True);dll=instrumented();machine=difftest.Machine();rows=[];output=('AX','BX','CX','DX','SI','DI','BP','CF','PF','ZF','SF','IF','DF')
    cases=[('UpdatePassengerResurfacing','cross'),('UpdatePassengerFloating','select'),('UpdateFloatingDestinationDisplay','select'),('UpdateFloatingDestinationDisplay','question'),('UpdateFloatingQuestionDisplay','question'),('UpdateFloatingPassengerApproach','select')]+[(n,'inbound') for n in ['UpdatePassengerPlatformWait','UpdatePassengerDestinationDisplay','UpdatePassengerQuestionDisplay','UpdatePassengerApproach']]
    for pair in range(3):
        for selection in (0,2):
            for name,variant in cases:
                for poison in (False,True):
                    case=difftest.Case(f'{name} pair{pair} craft{selection} {variant}','GAME:'+name,setup(pair,variant,selection),dict(DS=DATA_SEG,BX=6),output)
                    problems=difftest.run(case,machine,dll,poison);rows.append(dict(routine=name,pair=pair,craft=selection,variant=variant,poison=poison,problems=problems))
                    if problems:print(rows[-1],flush=True)
    traces=[]
    for pair in range(3):
        for selection in (0,2):
            machine.reset();setup(pair,'select',selection)(machine)
            for slot in (0,2,4):
                machine.ww('DGROUP:ActorDescriptors',machine.off('DGROUP:Data_7720'),slot);machine.ww('DGROUP:ActorUpdateOrScriptCursor',machine.off('GAME:IgnoreActorState'),slot)
            machine.ww('DGROUP:ActorUpdateOrScriptCursor',machine.off('GAME:UpdateFloatingPassengerApproach'),6)
            machine.write(DATA_SEG,machine.off('DGROUP:RemainingPassengerJourneys'),b'\1')
            reset=machine.reset;machine.reset=lambda:None;steps=[]
            try:
                for step in range(100):
                    before=machine.rw('DGROUP:ActorUpdateOrScriptCursor',6)
                    case=difftest.Case('coupled passenger dispatch chain','GAME:DispatchActorUpdates',None,dict(DS=DATA_SEG),output)
                    problems=difftest.run(case,machine,dll,False);steps.append(dict(step=step,before=before,after=machine.rw('DGROUP:ActorUpdateOrScriptCursor',6),problems=problems))
                    if problems:print('trace',pair,selection,steps[-1],flush=True);break
                    if steps[-1]['after']==machine.off('GAME:IgnoreActorState'):break
                assert not steps[-1]['problems'] and steps[-1]['after']==machine.off('GAME:IgnoreActorState'),steps[-1]
                assert machine.read(DATA_SEG,machine.off('DGROUP:RemainingPassengerJourneys'),1)==b'\0'
            finally:machine.reset=reset
            traces.append(dict(pair=pair,craft=selection,steps=steps,objective='decremented to zero after departure/read-journey'))
    audits={name:list((C.c_uint32*n).in_dll(dll,name)) for name,n in [('water_audit',20),('delivery_cross_audit',24),('itinerary_cross_audit',16)]}
    assert not any(audits['water_audit'][10:]) and not any(audits['delivery_cross_audit'][12:]) and not any(audits['itinerary_cross_audit'][8:]),audits
    save(OUT/'composition.json',receipt(['python','verif/water_composition.py'],[__file__,ROOT/'verif/water_build.py',ROOT/'native/passenger_water.c',ROOT/'native/bridge/passenger_water_bridge.c',ROOT/'native/passenger_delivery.c',ROOT/'native/bridge/passenger_delivery_bridge.c',ROOT/'native/passenger_itinerary.c',ROOT/'native/bridge/passenger_itinerary_bridge.c'],result='PASS' if all(not r['problems'] for r in rows) else 'FAIL',cases=rows,traces=traces,audits=audits))
    assert all(not r['problems'] for r in rows);print('PASS',len(rows),'L0 -> actual three-unit boundary cases and',len(traces),'unpatched dispatch chains',audits)
if __name__=='__main__':main()
