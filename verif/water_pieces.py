"""Literal water branch partitions and declared slot read/write footprints."""
from closure_support import ROOT,function

def between(body,first,last):return body[body.index(first):body.index(last,body.index(first))]
def suffix(body,first):return body[body.index(first):body.rfind('}')]

def pieces():
    source=(ROOT/'c/actors.c').read_text();r=function(source,'c_UpdatePassengerResurfacing');s=function(source,'c_UpdatePassengerSinking');f=function(source,'c_UpdatePassengerFloating');d=function(source,'c_UpdateFloatingDestinationDisplay');q=function(source,'c_UpdateFloatingQuestionDisplay');a=function(source,'c_UpdateFloatingPassengerApproach')
    p={
      'tick':('pw_tick(&out,&slot)','return actor_tick(r);','ACTOR_RESURFACING','tick'),
      'frame':('pw_frame(&out,&slot,(ActorAnimationKind)kind)','return actor_frame(r,46u+2u*piece_kind);','ACTOR_RESURFACING','success'),
      'surface':('pw_surface(&out,&slot,&render,&world)','surface_y(r);','ACTOR_FLOATING','void'),
      'animate-idle':('pw_animate(&out,&slot,ACTOR_IDLE_ANIMATION,0)',between(r,'    r->si=A(ActorDescriptors);','    r->cx=sub16'),'ACTOR_RESURFACING','success'),
      'animate-sink':('pw_animate(&out,&slot,ACTOR_IDLE_ANIMATION,0)',between(s,'    r->si=A(ActorDescriptors);','    r->ax=add16'),'ACTOR_SINKING','success'),
      'animate-request':('pw_animate(&out,&slot,ACTOR_REQUEST_ANIMATION,0)',between(f,'    r->si=A(ActorDescriptors);','    surface_y(r);'),'ACTOR_FLOATING','success'),
      'animate-conditional':('pw_animate(&out,&slot,ACTOR_REQUEST_ANIMATION,1)',between(d,'    if(actor_tick(r))','    uint16_t count='),'ACTOR_FLOATING_DESTINATION_REQUEST','success'),
      'resurface-motion':('pw_resurface_motion(&out,&slot,&render,&world)',between(r,'    r->cx=sub16','    sub16(r,A(ActorVerticalOrDemoPeriod)'),'ACTOR_RESURFACING','motion'),
      'resurface-cross':('pw_resurface_cross(&out,&slot,&world)',suffix(r,'    sub16(r,A(ActorVerticalOrDemoPeriod)'),'ACTOR_RESURFACING','void'),
      'sink-motion':('pw_sink_motion(&out,&slot)',suffix(s,'    r->ax=add16(r,A(ActorVerticalOrDemoPeriod)'),'ACTOR_SINKING','void'),
      'float-select':('pw_float_select(&out,&slot,&world)',between(f,'sub16(r,r->si,D(Data_77FE),0);','    uint16_t count='),'ACTOR_FLOATING','void'),
      'float-expire':('pw_float_expire(&out,&slot)',suffix(f,'    uint16_t count='),'ACTOR_FLOATING','void'),
      'destination-gate':('pw_destination_gate(&out,&world)',between(d,'    r->cx=sub16','    if(actor_tick(r))'),'ACTOR_FLOATING_DESTINATION_REQUEST','gate'),
      'destination-clock':('pw_request_clock(&out,&slot,PW_DESTINATION)',suffix(d,'    uint16_t count='),'ACTOR_FLOATING_DESTINATION_REQUEST','void'),
      'question-clock':('pw_request_clock(&out,&slot,PW_QUESTION)',suffix(q,'    uint16_t count='),'ACTOR_FLOATING_QUESTION','void'),
      'approach-select':('pw_approach_select(&out,&world)',between(a,'r->di=logic(r,0,16);','    r->cx=logic(r,0,16);'),'ACTOR_FLOATING_APPROACH','gate'),
      'approach-motion':('pw_approach_motion(&out,&slot,&render,&world)',suffix(a,'    r->cx=logic(r,0,16);'),'ACTOR_FLOATING_APPROACH','void'),
    }
    for key,name,entry in [('begin-resurface','BeginPassengerResurfacing','PW_BEGIN_RESURFACE'),('begin-sink','BeginPassengerSinking','PW_BEGIN_SINK'),('begin-float','BeginPassengerFloating','PW_BEGIN_FLOAT'),('ignore','IgnoreWaterbornePassengerState','PW_IGNORE')]:
        body=function(source,'c_'+name);body=body[body.index('{')+1:body.rfind('}')]
        p[key]=(f'out=passenger_water_apply({entry},&slot,&render,&world)',body,'ACTOR_READ_JOURNEY','apply')
    return p

CONTRACTED={'animate-idle','animate-sink','animate-request','animate-conditional','approach-motion'}
INPUTS={
 'tick':['animation'],'frame':['animation','sprite'],'surface':['position'],
 'animate-idle':['animation','sprite'],'animate-sink':['animation','sprite'],'animate-request':['animation','sprite'],'animate-conditional':['animation','sprite'],
 'resurface-motion':['position','vertical_motion'],'resurface-cross':['position','vertical_motion'],
 'sink-motion':['phase','position','vertical_motion','sprite'],
 'float-select':[],'float-expire':['phase','floating_ticks'],
 'destination-gate':[],'destination-clock':['phase','request_ticks'],'question-clock':['phase','request_ticks'],
 'approach-select':[],'approach-motion':['position','animation','sprite'],
 'begin-resurface':['source_platform'],'begin-sink':[],'begin-float':[],'ignore':[]}
OUTPUTS={
 'tick':['animation'],'frame':['animation.byte_offset','sprite'],'surface':['position.y32'],
 'animate-idle':['animation','sprite'],'animate-sink':['animation','sprite'],'animate-request':['animation','sprite'],'animate-conditional':['animation','sprite'],
 'resurface-motion':['position.y32','vertical_motion'],'resurface-cross':['position.y32'],
 'sink-motion':['phase','position.y32','vertical_motion','sprite'],
 'float-select':[],'float-expire':['floating_ticks'],'destination-gate':[],
 'destination-clock':['request_ticks'],'question-clock':['request_ticks'],'approach-select':[],
 'approach-motion':['position.x32','animation','sprite'],
 'begin-resurface':['phase','animation','overlay_sprite','vertical_motion'],
 'begin-sink':['phase','animation','overlay_sprite','vertical_motion'],'begin-float':['phase','animation','floating_ticks'],'ignore':[]}
MEMBERS=['phase','journey','source_platform','destination_platform','position','sprite','overlay_sprite','animation','waiting_pose','request_ticks','carrier','journey_wait','horizontal_step','floating_ticks','vertical_motion','quick_delivery_ticks']
RAM={'phase':['ActorUpdateOrScriptCursor'],'position.y32':['ActorY32'],'position.x32':['ActorX32'],'vertical_motion':['ActorVerticalOrDemoPeriod'],'sprite':['ActorSpriteIds'],'overlay_sprite':['ActorOverlayOrScriptCallbacks'],'animation':['ActorAnimationByteOffsets','ActorAnimationCountdowns'],'animation.byte_offset':['ActorAnimationByteOffsets'],'floating_ticks':['ActorMotionWaitOrDemoRepeats'],'request_ticks':['ActorPhaseOrDemoLoopCursor']}
