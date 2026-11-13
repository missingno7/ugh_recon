"""Exact L1 source partitions for passenger branch-stage proofs.

Each span is copied from maintained C, not a rewritten arithmetic model. The
same span is adapted by the checked full-handler shell generator. Entry setup
SI/DI assignments and the final return are recorded separately in the manifest.
"""
from closure_support import ROOT,function

def between(text,first,last):
    a=text.index(first);b=text.index(last,a);return text[a:b]

def suffix(text,first):
    return text[text.index(first):text.rfind("}")]

def pieces():
    a=(ROOT/'c/actors.c').read_text();s=(ROOT/'c/actors_states.c').read_text()
    wait=function(s,'c_UpdatePassengerPlatformWait');display=function(s,'display');approach=function(s,'c_UpdatePassengerApproach')
    carried=function(a,'c_UpdateCarriedPassenger');delivery=function(s,'c_DeliverPassenger')
    # tuple: native call; literal L1 span; group; phase; logical return relation.
    p={
        'submerged':('pd_submerged(&plan.slot,&plan.render,&plan.world)','return submerged(r);',1,'ACTOR_PLATFORM_WAIT','predicate'),
        'scan-empty':('pd_platform(&plan.slot,&plan.world,1)','return platform_player(r,1);',1,'ACTOR_PLATFORM_WAIT','scan'),
        'scan-any':('pd_platform(&plan.slot,&plan.world,0)','return platform_player(r,0);',1,'ACTOR_APPROACH','scan'),
        'tick':('pd_tick(&plan.result,&plan.slot)','return actor_tick(r);',1,'ACTOR_PLATFORM_WAIT','predicate'),
        'frame':('pd_frame(&plan.result,&plan.slot,(ActorAnimationKind)kind)','return frame(r,0,46u+2u*frame_piece_kind,0);',1,'ACTOR_PLATFORM_WAIT','success'),
        'water':('pd_water(&plan.result,&plan.slot,&plan.world,1)','return water_swap(r,1);',1,'ACTOR_PLATFORM_WAIT','void'),
        'contact-query':('pd_contact(&plan.slot,&plan.world)',between(wait,'    int status=ugh_call_near','    if(!(r->flags&SF))'),1,'ACTOR_PLATFORM_WAIT','contact'),
        'contact-water':('pd_contact_test(&plan.result,&plan.slot,&plan.world)',between(wait,'    int status=ugh_call_near','    int found=platform_player'),1,'ACTOR_PLATFORM_WAIT','gate'),
        'water-test':('pd_water_test(&plan.result,&plan.slot,&plan.render,&plan.world)','if(submerged(r)) return water_swap(r,1);',1,'ACTOR_PLATFORM_WAIT','gate'),
        'wait-motion':('pd_wait_motion(&plan.result,&plan.slot,&plan.render,&plan.world)',between(wait,'    if(actor_tick(r))','    int status=ugh_call_near'),1,'ACTOR_PLATFORM_WAIT','success'),
        'wait-request':('pd_wait_request(&plan.result,&plan.slot,&plan.world)',suffix(wait,'    int found=platform_player'),1,'ACTOR_PLATFORM_WAIT','void'),
        'destination-choice':('pd_destination_choice(&plan.result,&plan.slot,&plan.world)',between(display,'    if(!question) {','    if(actor_tick(r))'),1,'ACTOR_DESTINATION_REQUEST','gate'),
        'destination-clock':('pd_display_clock(PD_DESTINATION,&plan.result,&plan.slot,&plan.world)',suffix(display,'    if(actor_tick(r))'),1,'ACTOR_DESTINATION_REQUEST','void'),
        'question-clock':('pd_display_clock(PD_QUESTION,&plan.result,&plan.slot,&plan.world)',suffix(display,'    if(actor_tick(r))'),1,'ACTOR_QUESTION','void'),
        'approach-choice':('pd_approach_choice(&plan.result,&plan.slot,&plan.world)',between(approach,'    int found=platform_player','    r->cx=logic'),1,'ACTOR_APPROACH','gate'),
        'approach-motion':('pd_approach_motion(&plan.result,&plan.slot,&plan.render,&plan.world)',suffix(approach,'    r->cx=logic'),1,'ACTOR_APPROACH','void'),
        'fare':('pd_fare_decay(&plan.result,&plan.world,carrier)',between(carried,'    r->di=A(ActorPhaseOrDemoLoopCursor)','    r->ax=A(PassengerQuickDeliveryCountdowns)'),0,'ACTOR_CARRIED_PASSENGER','void'),
        'quick':('pd_quick_decay(&plan.result,&plan.slot)',between(carried,'    r->ax=A(PassengerQuickDeliveryCountdowns)','    r->ax=A(ActorDestinationPlatforms)'),0,'ACTOR_CARRIED_PASSENGER','void'),
        'carried-transition':('pd_carried_transition(&plan.result,&plan.slot,&plan.world,carrier)',suffix(carried,'    r->ax=A(ActorDestinationPlatforms)'),0,'ACTOR_CARRIED_PASSENGER','void'),
        'delivery-prefix':('pd_delivery_prefix(&plan.result,&plan.slot,&plan.world,incoming)',between(delivery,'    r->si=A(ActorDescriptors)','    uint32_t product='),1,'ACTOR_CARRIED_PASSENGER','carrier'),
        'product':('pd_fare_product(ram.players[6][0],ram.multiplier)',between(delivery,'    uint32_t product=','    W(ScoreLowWord'),1,'ACTOR_CARRIED_PASSENGER','product'),
        'award':('pd_award(&plan.result,&plan.world,carrier)',between(delivery,'    uint32_t product=','    logic(r,A(PassengerQuickDeliveryCountdowns)'),1,'ACTOR_WALK_TO_EXIT','void'),
        'delivery-reward':('pd_delivery_reward(&plan.result,&plan.slot,&plan.world,carrier)',suffix(delivery,'    logic(r,A(PassengerQuickDeliveryCountdowns)'),1,'ACTOR_WALK_TO_EXIT','void'),
        'finish':('pd_finish(&plan.result,&plan.slot,&plan.world)',suffix(delivery,'    r->di=A(ActorDestinationPlatformByteIndices)'),1,'ACTOR_WALK_TO_EXIT','void'),
    }
    for key,name,entry,phase in [('begin-wait','BeginPassengerPlatformWait','PD_BEGIN_WAIT','ACTOR_READ_JOURNEY'),
        ('begin-destination','BeginPassengerDestinationDisplay','PD_BEGIN_DESTINATION','ACTOR_READ_JOURNEY'),
        ('begin-question','BeginPassengerQuestionDisplay','PD_BEGIN_QUESTION','ACTOR_READ_JOURNEY'),
        ('begin-approach','BeginPassengerApproach','PD_BEGIN_APPROACH','ACTOR_READ_JOURNEY'),
        ('board','BoardPassenger','PD_BOARD','ACTOR_READ_JOURNEY'),('rescue','BoardWaterbornePassenger','PD_RESCUE','ACTOR_READ_JOURNEY')]:
        group=1 if key=='rescue' else 0;body=function(s if group else a,'c_'+name);body=body[body.index('{')+1:body.rfind('}')]
        p[key]=(f'plan.result=passenger_delivery_apply({entry},&plan.slot,&plan.render,&plan.world,incoming)',body,group,phase,'apply')
    for key,body,phase in [
        ('contact-destination',display,'ACTOR_DESTINATION_REQUEST'),
        ('contact-question',display,'ACTOR_QUESTION'),
        ('contact-approach',approach,'ACTOR_APPROACH')]:
        p[key]=('pd_contact_test(&plan.result,&plan.slot,&plan.world)',
                between(body,'    int status=ugh_call_near','    if(!question)' if body==display else '    int found=platform_player'),
                1,phase,'gate')
    return p

CONTRACTS={k:('tick','frame') for k in ['wait-motion','destination-clock','question-clock','approach-motion']}

# Read and potentially retained output fields. All remaining native slot/world
# fields are varied independently by the dependence profile.
SLOT_INPUTS={
 'submerged':[], 'scan-empty':['source_platform'],'scan-any':['source_platform'],
 'tick':['animation'], 'frame':['animation','sprite'], 'water':['source_platform','position','overlay_sprite'],
 'water-test':['source_platform','position','overlay_sprite'], 'contact-water':['position'], 'contact-query':['position'],
 'wait-motion':['phase','source_platform','position','sprite','animation','waiting_pose'],
 'wait-request':['source_platform'], 'destination-choice':['source_platform'],
 'destination-clock':['phase','source_platform','request_ticks','animation','sprite'],
 'question-clock':['phase','source_platform','request_ticks','animation','sprite'],
 'approach-choice':['source_platform'], 'approach-motion':['position','animation','sprite'],
 'fare':[], 'quick':['quick_delivery_ticks'], 'carried-transition':['destination_platform'],
 'delivery-prefix':['phase','carrier','position'], 'product':[], 'award':[], 'delivery-reward':['destination_platform','position','animation','quick_delivery_ticks'],
 'finish':['destination_platform','position','animation'],
}
SLOT_OUTPUTS={
 'tick':['animation'], 'frame':['animation.byte_offset','sprite'], 'water':['type','position.y32','overlay_sprite'], 'water-test':['type','position.y32','overlay_sprite'],
 'contact-water':['type'], 'wait-motion':['position.x32','sprite','animation','waiting_pose'],
 'destination-clock':['animation','sprite','request_ticks'], 'question-clock':['animation','sprite','request_ticks'],
 'approach-motion':['animation','sprite','position.x32'], 'quick':['quick_delivery_ticks'],
 'delivery-prefix':['phase','position.x32'],'delivery-reward':['position.y32','animation'],'finish':['position.y32','animation'],
}
for key in ['begin-wait','begin-destination','begin-question','begin-approach','board','rescue']:
    SLOT_INPUTS[key]=['phase','position','sprite','overlay_sprite','animation','source_platform','destination_platform','quick_delivery_ticks']
SLOT_OUTPUTS.update({
 'begin-wait':['phase','animation','waiting_pose','overlay_sprite'],
 'begin-destination':['phase','animation','overlay_sprite','request_ticks'],
 'begin-question':['phase','animation','overlay_sprite','request_ticks'],
 'begin-approach':['phase','animation','overlay_sprite'],
 'board':['phase','carrier','sprite','quick_delivery_ticks'],
 'rescue':['type','phase','carrier','sprite','quick_delivery_ticks'],
})
for key in ['contact-destination','contact-question','contact-approach']:
    SLOT_INPUTS[key]=SLOT_INPUTS['contact-water']
    SLOT_OUTPUTS[key]=SLOT_OUTPUTS['contact-water']

def adapt(body,group):
    """The full shell generator's exact identifier/context/store adaptation."""
    import re
    contextual={'actor_init','tail','state_jump','effect','frame','actor_tick','water_swap','display'}
    for callee in contextual:body=body.replace(callee+'(r,',callee+'(r,plan,').replace(callee+'(r)',callee+'(r,plan)')
    body=body.replace('ugh_dispatch(r->cs,target,r)','delivery_dispatch(r,plan,target)').replace('ugh_dispatch(r->cs,F(field),r)','delivery_dispatch(r,plan,F(field))')
    body=body.replace('ugh_dispatch(UGH_S_C_PlayAdlibEffect,UGH_O_C_PlayAdlibEffect,r)','delivery_sound(r,plan,UGH_S_C_PlayAdlibEffect,UGH_O_C_PlayAdlibEffect)')
    if 'ugh_call_near(' in body:body=body.replace('ugh_call_near(','delivery_near(r,plan,').replace(',r);',');')
    body=body.replace('wr8(r->ds,','delivery_write8(plan,r,')
    names=['shl','less','greater','actor_init','tail','state_jump','contact'] if group==0 else ['lt','gt','shift','inc','push','pop','effect','frame','actor_tick','submerged','water_swap','platform_player','display','tail']
    for name in names:body=re.sub(r'\b'+name+r'\b',f'pd_shell{group}_{name}',body)
    return body
