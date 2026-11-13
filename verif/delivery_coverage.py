"""Fail-closed source partition and orchestration inventory for split proofs.

This is a static composition check, not another solver claim. Every nontrivial
L1 statement in the six updating handlers belongs to a literal proved span;
only descriptor/source-index loads and the existing display selector remain.
"""
import hashlib,json,re
from closure_support import ROOT,function,receipt,save
from delivery_build import OUT,NAMES
from delivery_pieces import pieces,adapt,CONTRACTS
from delivery_shells import shells

def compact(text):return re.sub(r'\s+','',text)
def digest(text):return hashlib.sha256(text.encode()).hexdigest()
def main():
    p=pieces();a=(ROOT/'c/actors.c').read_text();s=(ROOT/'c/actors_states.c').read_text()
    rows=[]
    partitions=[
        ('UpdatePassengerPlatformWait',s,['water-test','wait-motion','contact-water','wait-request'],
         'r->di=A(ActorSourcePlatformByteIndices); r->si=A(ActorDescriptors);'),
        ('display',s,['water-test','contact-destination','destination-choice','destination-clock'],
         'r->si=A(ActorDescriptors);'),
        ('UpdatePassengerApproach',s,['water-test','contact-approach','approach-choice','approach-motion'],
         'r->si=A(ActorDescriptors);'),
        ('UpdateCarriedPassenger',a,['fare','quick','carried-transition'],''),
        ('DeliverPassenger',s,['delivery-prefix','award','delivery-reward'],''),
    ]
    for name,source,keys,remainder in partitions:
        body=function(source,name if name=='display' else 'c_'+name)
        body=body[body.index('{')+1:body.rfind('}')]
        spans=[]
        for key in keys:
            literal=p[key][1];assert body.count(literal)==1,(name,key)
            spans.append(dict(piece=key,sha256=digest(literal)));body=body.replace(literal,'',1)
        assert compact(body)==compact(remainder),(name,body)
        rows.append(dict(handler=name,pieces=spans,only_remaining_setup=remainder))
    # Both wrappers of the shared display routine must use the exact selector.
    for name,selector in [('UpdatePassengerDestinationDisplay',0),('UpdatePassengerQuestionDisplay',1)]:
        body=function(s,'c_'+name);assert compact(body[body.index('{')+1:body.rfind('}')])==f'returndisplay(r,{selector});'
    assert p['contact-destination'][1]==p['contact-question'][1]
    # The checked full shell is generated from these actual functions. Each
    # extracted stage's exact adaptation must occur verbatim inside that shell.
    actual_shell=shells()
    for key,(_,body,group,_,_) in p.items():
        if key in ['submerged','scan-empty','scan-any','tick','frame','water']:continue
        assert compact(adapt(body,group)) in compact(actual_shell),(key,'shell adaptation differs')
    core=ROOT/'native/passenger_delivery.c';native=core.read_text()
    assert '->writes' not in native.replace(function(native,'pd_emit'),'') and '.writes' not in native.replace(function(native,'pd_emit'),''),'native caller must not inspect hidden append payload'
    wiring={
        'PD_WAIT':'''if(pd_water_test(&result,slot,render,world)) break;
 if(!pd_wait_motion(&result,slot,render,world)) break;
 if(!pd_contact_test(&result,slot,world)) pd_wait_request(&result,slot,world);break;''',
        'PD_DESTINATION:case PD_QUESTION':'''if(pd_water_test(&result,slot,render,world) || pd_contact_test(&result,slot,world)) break;
 if(entry==PD_DESTINATION && pd_destination_choice(&result,slot,world)) break;
 pd_display_clock(entry,&result,slot,world);break;''',
        'PD_APPROACH':'''if(pd_water_test(&result,slot,render,world) || pd_contact_test(&result,slot,world)) break;
 if(!pd_approach_choice(&result,slot,world)) pd_approach_motion(&result,slot,render,world);break;''',
        'PD_CARRIED':'''{uint16_t carrier;if(!actor_alias_value(slot,ACTOR_ALIAS_CARRIER,&carrier)) {result.failed=1;break;}
 pd_fare_decay(&result,world,carrier);pd_quick_decay(&result,slot);
 pd_carried_transition(&result,slot,world,carrier);break;}''',
        'PD_DELIVER':'''{uint16_t carrier=pd_delivery_prefix(&result,slot,world,incoming_craft);
 if(!result.failed) {pd_award(&result,world,carrier);pd_delivery_reward(&result,slot,world,carrier);}}''',
    }
    apply=function(native,'passenger_delivery_apply')
    for key,expected in wiring.items():
        start=apply.index('case '+key+':')+len('case '+key+':')
        end=apply.find('\n    case ',start)
        if end<0:end=apply.rfind('\n    }')
        assert compact(apply[start:end])==compact(expected),(key,apply[start:end])
    coverage=dict(result='PASS',partitions=rows,native_wiring=wiring,
        actual_public_step_sha256=digest(apply),pieces={k:dict(native_call=v[0],source_sha256=digest(v[1]),phase=v[3],seams=CONTRACTS.get(k,[])) for k,v in p.items()},
        coverage='Output covers every owned typed state cell, ordered journal/store, complete registers/flags/continuation and all controls/services at the cut. Frame covers all other native/resource/history bytes and an arbitrary other RAM byte/slot. Dependence varies unborrowed slot fields, inactive aliases and retained renderer histories. Tick/frame/contact/product seams assert actual input equality and admit arbitrary shared outputs; separate helper theorems discharge them. Dependence observes an arbitrary append position through the separately proved actual pd_emit lemma, preserving all append arguments/counts without a duplicated symbolic journal array. Literal partitions and exact native wiring compose these properties by branch order; append theorem lifts a stage from the zero-length test journal to any admitted prefix. Immediate tails and item/audio child effects compose with their separately owned contracts, not an unproved second native snapshot.',
        assumptions='Disjoint ordinary storage, fixed selected physical slot0 (uniform constant-offset indexing; arbitrary-other-slot byte frame), one/two players, ten platforms, registered immutable animation resources and checked descriptor/callback identities. No reachability, scalar magnitude, idle history or item availability assumption.')
    save(OUT/'coverage.json',receipt(['python','verif/delivery_coverage.py'],[ROOT/'verif/delivery_coverage.py',ROOT/'verif/delivery_pieces.py',ROOT/'verif/delivery_shells.py',core,ROOT/'native/bridge/passenger_delivery_bridge.c',ROOT/'c/actors.c',ROOT/'c/actors_states.c'],**coverage))
    print('PASS literal partitions and native orchestration',flush=True)
if __name__=='__main__':main()
