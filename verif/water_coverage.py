"""Checked literal source partitions, native wiring and cross-unit tail table."""
import hashlib,re
from closure_support import ROOT,function,receipt,save
from water_build import OUT
from water_pieces import pieces
from water_shells import shells,adapt
def compact(text):return re.sub(r'\s+','',text)
def main():
    source=(ROOT/'c/actors.c').read_text();core=ROOT/'native/passenger_water.c';native=core.read_text();p=pieces();rows=[]
    groups=[
      ('UpdatePassengerResurfacing',['animate-idle','resurface-motion','resurface-cross'],''),
      ('UpdatePassengerSinking',['animate-sink','sink-motion'],''),
      ('UpdatePassengerFloating',['animate-request','surface','float-select','float-expire'],''),
      ('UpdateFloatingDestinationDisplay',['surface','destination-gate','animate-conditional','destination-clock'],'r->si=A(ActorDescriptors);'),
      ('UpdateFloatingQuestionDisplay',['surface','animate-conditional','question-clock'],'r->si=A(ActorDescriptors);'),
      ('UpdateFloatingPassengerApproach',['surface','approach-select','approach-motion'],'r->si=A(ActorDescriptors);'),
    ]
    for name,keys,remaining in groups:
        body=function(source,'c_'+name);body=body[body.index('{')+1:body.rfind('}')]
        for key in keys:
            span=p[key][1];assert body.count(span)==1,(name,key);body=body.replace(span,'',1)
        assert compact(body)==compact(remaining),(name,body)
        rows.append(dict(handler=name,pieces=keys,only_remaining_setup=remaining))
    fullshell=shells()
    for key,(_,body,_,_) in p.items():
        if key in ['tick','frame','surface','ignore']:continue
        assert compact(adapt(body)) in compact(fullshell),(key,'full shell adaptation')
    stripped=native.replace(function(native,'pw_emit'),'');assert '->writes' not in stripped and '.writes' not in stripped,'caller may not read hidden journal payload'
    wiring={
      'PW_RESURFACE':'''if(!pw_animate(&out,slot,ACTOR_IDLE_ANIMATION,0)) break;
       pw_resurface_motion(&out,slot,render,world);pw_resurface_cross(&out,slot,world);break;''',
      'PW_SINK':'''if(pw_animate(&out,slot,ACTOR_IDLE_ANIMATION,0)) pw_sink_motion(&out,slot);break;''',
      'PW_FLOAT':'''if(!pw_animate(&out,slot,ACTOR_REQUEST_ANIMATION,0)) break;
       pw_surface(&out,slot,render,world);pw_float_select(&out,slot,world);
       if(out.next==PW_NEXT_NONE) pw_float_expire(&out,slot);break;''',
      'PW_DESTINATION:case PW_QUESTION':'''pw_surface(&out,slot,render,world);
       if(entry==PW_DESTINATION && pw_destination_gate(&out,world)) break;
       if(!pw_animate(&out,slot,ACTOR_REQUEST_ANIMATION,1)) break;
       pw_request_clock(&out,slot,entry);break;''',
      'PW_APPROACH':'''pw_surface(&out,slot,render,world);if(!pw_approach_select(&out,world)) pw_approach_motion(&out,slot,render,world);break;''',
    }
    apply=function(native,'passenger_water_apply')
    for key,wanted in wiring.items():
        start=apply.index('case '+key+':')+len('case '+key+':');end=apply.index('\n    case ',start)
        assert compact(apply[start:end])==compact(wanted),(key,apply[start:end])
    tails=[dict(next=n,target=t,owner=o) for n,t,o in [
      ('FLOAT','BeginPassengerFloating','passenger_water'),('SINK','BeginPassengerSinking','passenger_water'),
      ('DESTINATION','BeginPassengerDestinationDisplay','passenger_delivery'),('QUESTION','BeginPassengerQuestionDisplay','passenger_delivery'),
      ('APPROACH','BeginPassengerApproach','passenger_delivery'),('BOARD','BoardWaterbornePassenger','passenger_delivery')]]
    save(OUT/'coverage.json',receipt(['python','verif/water_coverage.py'],[ROOT/'verif/water_coverage.py',ROOT/'verif/water_pieces.py',ROOT/'verif/water_shells.py',core,ROOT/'native/bridge/passenger_water_bridge.c',ROOT/'c/actors.c'],
      result='PASS',partitions=rows,wiring=wiring,tails=tails,actual_public_step_sha256=hashlib.sha256(apply.encode()).hexdigest(),
      composition='Actual output plus independent native/RAM byte frames and dependence cover all owned and retained state, full machine registers/flags/store order, next/selected/failure. Frame-full varies every unborrowed slot field, including phase for phase-agnostic reused helpers. Actual primitive tick/frame/append theorems discharge shared arbitrary-output seams with asserted input equality. Literal partitions and exact native branch order compose at the journal and pre-tail cut; complete projection has independent actual-code properties. Append at arbitrary prefix lifts zero-prefix stage checks, and native callers do not read hidden payload. Closed delivery/itinerary transitions compose through actual exported bridge entries; normal second-pair and no-op reachability is separately audited.'))
    print('PASS water literal partitions and native wiring')
if __name__=='__main__':main()
