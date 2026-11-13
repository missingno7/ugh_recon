"""Actual C stage output/frame/dependence proofs with checked relational seams."""
import argparse,json,re
from pathlib import Path
from closure_support import ROOT,function,save
from delivery_build import OUT,pair
from delivery_limits import cbmc,SMT
from delivery_pieces import pieces,adapt,CONTRACTS,SLOT_INPUTS,SLOT_OUTPUTS

def macros(group,shell):
    write='delivery_write16(plan,r,' if shell else 'dl_write(r->ds,'
    if group==0:
        return f'''#define READ(n,i) dl_read(r->ds,(uint16_t)(D(n)+(i)))
#define WRITE(n,i,v) {write}(uint16_t)(D(n)+(i)),(uint16_t)(v))
#define A(n) READ(n,r->bx)
#define W(n,v) WRITE(n,r->bx,v)
#define DESC(n) dl_read(r->ds,(uint16_t)(r->si+(n)))
'''
    return f'''#define R(n,i) dl_read(r->ds,(uint16_t)(D(n)+(i)))
#define W(n,i,v) {write}(uint16_t)(D(n)+(i)),(uint16_t)(v))
#define A(n) R(n,r->bx)
#define B(n,v) W(n,r->bx,v)
#define F(n) dl_read(r->ds,(uint16_t)(r->si+(n)))
'''

def functions(fragment,group):
    # Both wrappers contain the identical maintained span. Only the already
    # checked machine-shell adaptation changes stores/helpers on the native side.
    names=['shl','less','greater','actor_init','tail','state_jump','contact'] if group==0 else ['lt','gt','shift','inc','push','pop','effect','frame','actor_tick','submerged','water_swap','platform_player','display','tail']
    ref=fragment
    for n in names:ref=re.sub(r'\b'+n+r'\b',f'dl_ref{group}_{n}',ref)
    undef='\n'.join('#undef '+n for n in ['READ','WRITE','A','W','DESC','R','B','F'])+'\n'
    common='int question=QUESTION;(void)question;\n'
    if re.search(r'\bstatus\s*=',fragment) and not re.search(r'\bint\s+status\b',fragment):common+='int status=0;\n'
    ref=macros(group,False)+'static int ref_piece(Regs *r) {\n'+common+ref+'\nreturn UGH_OK;\n}\n'+undef
    native=macros(group,True)+'static int bridge_piece(Regs *r,DeliveryPlan *plan) {\n(void)plan;\n'+common+adapt(fragment,group)+'\nreturn UGH_OK;\n}\n'+undef
    return ref+native

CONTRACT_HEADER='''
typedef struct PieceContract {
 uint16_t dec,reload,cursor,sprite,ax,di,flags;
 _Bool due,reset;
} PieceContract;
static PieceContract contract;
static unsigned ntick,nframe,rtick,rframe,stick,sframe;
static uint16_t tick_count,tick_cursor,tick_period,frame_cursor,frame_kind;
'''
CONTRACT_IMPL='''
static int pd_tick(PassengerDeliveryResult *result,PassengerStoneSlot *slot) {
 CHECK(++ntick==1,"one tick seam");tick_count=slot->animation.countdown;tick_cursor=slot->animation.byte_offset;tick_period=slot->type->animation_period;
 slot->animation.countdown=contract.dec;pd_emit(result,PD_TICK,0,contract.dec);
 if(!contract.due) return 0;
 slot->animation.countdown=contract.reload;pd_emit(result,PD_TICK,0,contract.reload);
 slot->animation.byte_offset=contract.cursor;pd_emit(result,PD_CURSOR,0,contract.cursor);return 1;
}
static int piece_tick(Regs *r,int shell,DeliveryPlan *plan) {
 if(shell) CHECK(++stick==1,"one shell tick seam");else CHECK(++rtick==1,"one reference tick seam");
 CHECK(ntick==1 && dl_read(r->ds,D(ActorAnimationCountdowns))==tick_count && dl_read(r->ds,D(ActorAnimationByteOffsets))==tick_cursor && dl_read(r->ds,(uint16_t)(r->si+62))==tick_period,"tick input equality at the seam");
 if(shell) delivery_write16(plan,r,D(ActorAnimationCountdowns),contract.dec);else dl_write(r->ds,D(ActorAnimationCountdowns),contract.dec);
 if(contract.due) {
  if(shell) {delivery_write16(plan,r,D(ActorAnimationCountdowns),contract.reload);delivery_write16(plan,r,D(ActorAnimationByteOffsets),contract.cursor);}
  else {dl_write(r->ds,D(ActorAnimationCountdowns),contract.reload);dl_write(r->ds,D(ActorAnimationByteOffsets),contract.cursor);}
 }
 r->ax=contract.ax;r->flags=contract.flags;return contract.due;
}
static int dl_ref1_actor_tick(Regs *r) {return piece_tick(r,0,0);}
static int pd_shell1_actor_tick(Regs *r,DeliveryPlan *plan) {return piece_tick(r,1,plan);}
static int pd_frame(PassengerDeliveryResult *result,PassengerStoneSlot *slot,ActorAnimationKind kind) {
 CHECK(++nframe==1,"one frame seam");frame_cursor=slot->animation.byte_offset;frame_kind=(uint16_t)kind;
 if(contract.reset) {slot->animation.byte_offset=contract.cursor;pd_emit(result,PD_CURSOR,0,contract.cursor);}
 slot->sprite=contract.sprite;pd_emit(result,PD_SPRITE,0,contract.sprite);return 1;
}
static int piece_frame(Regs *r,int shell,DeliveryPlan *plan,int enemy,unsigned field,int directional) {
 if(shell) CHECK(++sframe==1,"one shell frame seam");else CHECK(++rframe==1,"one reference frame seam");
 CHECK(nframe==1 && !enemy && !directional && field==46u+2u*frame_kind && dl_read(r->ds,D(ActorAnimationByteOffsets))==frame_cursor,"animation input and selected vector equality at the seam");
 if(contract.reset) {
  if(shell) delivery_write16(plan,r,D(ActorAnimationByteOffsets),contract.cursor);else dl_write(r->ds,D(ActorAnimationByteOffsets),contract.cursor);
 }
 if(shell) delivery_write16(plan,r,D(ActorSpriteIds),contract.sprite);else dl_write(r->ds,D(ActorSpriteIds),contract.sprite);
 r->ax=contract.sprite;r->di=contract.di;r->flags=contract.flags;return UGH_OK;
}
static int dl_ref1_frame(Regs *r,int enemy,unsigned field,int directional) {return piece_frame(r,0,0,enemy,field,directional);}
static int pd_shell1_frame(Regs *r,DeliveryPlan *plan,int enemy,unsigned field,int directional) {return piece_frame(r,1,plan,enemy,field,directional);}
'''

def observe_scans(text):
    for name,prototype in [('platform_player','static int dl_ref1_platform_player(Regs *r,int empty);'),('pd_shell1_platform_player','static int pd_shell1_platform_player(Regs *r,int empty);')]:
        body=function(text,name);actual=re.sub(r'\b'+name+r'(?=\s*\()', 'observed_actual_'+name,body,count=1)
        text=text.replace(body,prototype+'\n'+actual,1)
    return text

SCAN_IMPL='''
static int dl_ref1_platform_player(Regs *r,int empty) {
 int status=observed_actual_platform_player(r,empty);scan_calls++;scan_selected=status==1?r->di/2u:-1;return status;
}
static int pd_shell1_platform_player(Regs *r,int empty) {
 int status=observed_actual_pd_shell1_platform_player(r,empty);scan_calls++;scan_selected=status==1?r->di/2u:-1;return status;
}
'''

CONTACT_HEADER='''
static int contact_index;static uint16_t contact_boundary,contact_cx,contact_dx,contact_bp,contact_flags;
static unsigned native_queries,reference_queries,shell_queries;static uint16_t query_input[11];
'''
CONTACT_IMPL='''
ContactSelection contact_players(ObjectPosition object,ObjectGeometry geometry,const ObjectPosition players[2],uint16_t count) {
 CHECK(++native_queries==1,"one native contact mapping");
 uint16_t args[11]={object.x32,object.y32,geometry.anchor_x,geometry.anchor_y,geometry.extent_x,geometry.extent_y,players[0].x32,players[0].y32,players[1].x32,players[1].y32,count};
 for(unsigned i=0;i<11;i++) query_input[i]=args[i];
 CHECK(contact_index>=-1 && contact_index<(int)count,"closed contact result range");
 return (ContactSelection){contact_index,contact_boundary};
}
static int piece_contact_query(Regs *r) {
 if(modern_calls) CHECK(++shell_queries==1,"one shell contact call");else CHECK(++reference_queries==1,"one reference contact call");
 r->si=dl_read(r->ds,D(ActorDescriptors));ObjectGeometry g=level_bridge_geometry(r->ds,r->si,0);
 uint16_t args[11]={dl_read(r->ds,D(ActorX32)),dl_read(r->ds,D(ActorY32)),g.anchor_x,g.anchor_y,g.extent_x,g.extent_y,
  dl_read(r->ds,D(PlayerX32)),dl_read(r->ds,D(PlayerY32)),dl_read(r->ds,(uint16_t)(D(PlayerX32)+2)),dl_read(r->ds,(uint16_t)(D(PlayerY32)+2)),dl_read(r->ds,D(PlayerCount))};
 CHECK(native_queries==1,"native contact was requested");
 for(unsigned i=0;i<11;i++) CHECK(query_input[i]==args[i],"all actual contact query arguments equal at the seam");
 r->di=contact_index<0?65535u:(uint16_t)(2u*(unsigned)contact_index);
 r->ax=contact_index<0?contact_boundary:dl_read(r->ds,(uint16_t)(D(PlayerPlatformIndices)+r->di));
 r->cx=contact_cx;r->dx=contact_dx;r->bp=contact_bp;flag(r,AF,contact_flags&AF);logic(r,r->di,16);return UGH_OK;
}
'''

SLOT_RAM={'type':['ActorDescriptors'],'phase':['ActorUpdateOrScriptCursor'],'position.x32':['ActorX32'],'position.y32':['ActorY32'],'animation.byte_offset':['ActorAnimationByteOffsets'],
 'sprite':['ActorSpriteIds'],'overlay_sprite':['ActorOverlayOrScriptCallbacks'],'animation':['ActorAnimationByteOffsets','ActorAnimationCountdowns'],
 'waiting_pose':['ActorPhaseOrDemoLoopCursor'],'request_ticks':['ActorPhaseOrDemoLoopCursor'],'carrier':['ActorPhaseOrDemoLoopCursor'],'quick_delivery_ticks':['PassengerQuickDeliveryCountdowns']}

def raw_frame_allowed(key):
    words=[];bytes_=[]
    for field in SLOT_OUTPUTS.get(key,[]):words += ['D('+n+')' for n in SLOT_RAM[field]]
    if key in ('water','water-test','board','rescue'):words.append('(uint16_t)(D(PlatformActorOccupants)+2u*plan.slot.source_platform)')
    if key=='fare':words.append('(uint16_t)(D(PlayerPassengerFares)+2u*carrier)')
    if key in ('board','rescue'):
        words += ['(uint16_t)(D('+n+')+2u*incoming)' for n in ['PlayerPassengerFares','PlayerMinimumFares','PlayerCarriedKinds','PlayerDestinationIcons']]
    if key=='delivery-prefix':
        words+=['(uint16_t)(D('+n+')+2u*incoming)' for n in ['PlayerCarriedKinds','PlayerDestinationIcons']]
    if key=='award':words+=['D(ScoreLowWord)','D(ScoreHighWord)']
    if key in ('delivery-reward','finish'):bytes_.append('D(HudFareClearPending)')
    terms=[f'(frame_bank==DATA_SEG && (frame_off=={n} || frame_off==(uint16_t)({n}+1u)))' for n in words]
    terms += [f'(frame_bank==DATA_SEG && frame_off=={n})' for n in bytes_]
    if key.startswith('contact-'):terms.append('(frame_bank==1 && frame_off>=36862u && frame_off<36864u)')
    if key=='delivery-reward':terms.append('(frame_bank==1 && frame_off>=36848u && frame_off<36864u)')
    return ' || '.join(terms) if terms else '0'

def contract_pair(text):
    # Rename only definitions; actual caller expressions remain untouched.
    for name in ['pd_tick','pd_frame','actor_tick','frame','pd_shell1_actor_tick','pd_shell1_frame']:
        body=function(text,name);sig=body[:body.index('{')].strip()
        actual=re.sub(r'\b'+name+r'(?=\s*\()', 'piece_actual_'+name,body,count=1)
        prototype=sig+';\n'
        if name=='actor_tick':prototype='static int dl_ref1_actor_tick(Regs *r);\n'
        if name=='frame':prototype='static int dl_ref1_frame(Regs *r,int enemy,unsigned field,int directional);\n'
        text=text.replace(body,prototype+actual,1)
    return text

def native_call(call,relation,variable='nret'):
    return (f'int {variable}=0;{call};\n' if relation in ('void','apply') else f'{"uint32_t" if relation=="product" else "int"} {variable}={call};\n')

def world_outputs(key,base='plan.world'):
    if key=='fare':return [base+'.craft[carrier].fare']
    if key in ('board','rescue'):return [base+'.craft[incoming].'+n for n in ['fare','minimum_fare','carried_kind','destination_icon']]
    if key=='delivery-prefix':return [base+'.craft[incoming].carried_kind',base+'.craft[incoming].destination_icon']
    if key=='award':return [base+'.score']
    if key in ('delivery-reward','finish'):return [base+'.hud_clear']
    return []

def native_outputs(key):
    return ['plan.slot.'+n for n in SLOT_OUTPUTS.get(key,[])]+world_outputs(key)

def projected_outputs(key):
    """Caller-side seam contract, discharged by output + byte frame proofs.

    The actual full projection predicate has its own output/frame/dependence
    profiles. Do not inline every unmodified field into each output theorem.
    """
    checks=['plan->consumed==plan->result.count']
    for field in SLOT_OUTPUTS.get(key,[]):
        if field=='type':checks+=['(plan->slot.type==&plan->types[0] || plan->slot.type==&plan->types[1])','delivery_word(r,D(ActorDescriptors),0)==delivery_identity(plan->slot.type->id)']
        elif field=='phase':checks+=['plan->slot.phase==plan->published_phase','delivery_word(r,D(ActorUpdateOrScriptCursor),0)==delivery_phase((uint16_t)plan->slot.phase)']
        elif field=='carrier':checks+=['(actor_phase_aliases(plan->slot.phase)&ACTOR_ALIAS_CARRIER)!=0','plan->slot.carrier==(size_t)(delivery_word(r,D(ActorPhaseOrDemoLoopCursor),0)/2u)']
        elif field=='animation':checks+=['plan->slot.animation.byte_offset==delivery_word(r,D(ActorAnimationByteOffsets),0)','plan->slot.animation.countdown==delivery_word(r,D(ActorAnimationCountdowns),0)']
        else:checks.append(f'plan->slot.{field}==delivery_word(r,D({SLOT_RAM[field][0]}),0)')
    for field in world_outputs(key):
        value=field.replace('plan.world','plan->world').replace('[carrier]','[seam_carrier]').replace('[incoming]','[seam_incoming]')
        if field.endswith('.score'):checks.append(f'{value}==((uint32_t)dl_read(r->ds,D(ScoreLowWord))|((uint32_t)dl_read(r->ds,D(ScoreHighWord))<<16))')
        elif field.endswith('.hud_clear'):checks.append(f'{value}==dl_byte(r->ds,D(HudFareClearPending))')
        else:
            name={'fare':'PlayerPassengerFares','minimum_fare':'PlayerMinimumFares','carried_kind':'PlayerCarriedKinds','destination_icon':'PlayerDestinationIcons'}[field.split('.')[-1]]
            index='seam_carrier' if '[carrier]' in field else 'seam_incoming'
            checks.append(f'{value}==delivery_word(r,D({name}),(uint16_t)(2u*{index}))')
    # Short-circuit avoids reading a carrier member under a wrong phase tag.
    return 'static int delivery_projection(DeliveryPlan *plan,Regs *r) {\nreturn '+' &&\n'.join(checks)+';\n}\n'

def make(key,mode,folder,frame_part='both'):
    call,fragment,group,phase,relation=pieces()[key];inputs=pair(folder)
    inc=folder/'pair.inc';text=inc.read_text();path=ROOT/'native/passenger_delivery.c'
    text=text.replace('#include "'+path.as_posix()+'"',path.read_text())
    contracted=key in CONTRACTS
    contact_contract=key.startswith('contact-')
    product_contract=key=='award'
    if product_contract:
        body=function(text,'pd_fare_product');text=text.replace(body,'static uint32_t pd_fare_product(uint16_t fare,uint16_t multiplier);\n'+body.replace('pd_fare_product(','actual_pd_fare_product(',1),1)
        old='(uint32_t)r->ax*R(ScoreMultiplier,0)';assert old in fragment
        fragment=fragment.replace(old,'piece_product(r->ax,R(ScoreMultiplier,0),0)')
    if contact_contract:
        contact_path=ROOT/'native/contacts.c';contact_source=contact_path.read_text()
        contact_source=contact_source.replace(function(contact_source,'contact_players'),re.sub(r'\bcontact_players(?=\s*\()', 'actual_contact_players',function(contact_source,'contact_players'),count=1))
        text=text.replace('#include "'+contact_path.as_posix()+'"',contact_source)
    if contracted:text=contract_pair(text)
    text=observe_scans(text)
    text=text.replace(function(text,'delivery_projection'),projected_outputs(key))
    if mode=='dependencies':
        # The independent real pd_emit theorem proves append at every prefix.
        # Observe an arbitrary appended cell without constructing two arrays
        # of conditionally updated complete journals in a caller dependence
        # proof. All caller code and all append arguments remain actual C.
        original_emit=function(text,'pd_emit')
        text=text.replace(original_emit,'''static void pd_emit(PassengerDeliveryResult *result,PassengerDeliveryField field,size_t index,uint16_t value) {
 CHECK(result->count<32,"append lemma prefix bound");
 if(result->count==dep_index) {dep_seen[dep_epoch]=1;dep_observed[dep_epoch]=(PassengerDeliveryWrite){field,index,value};}
 result->count++;
}
''',1)
    elif mode=='frame' and frame_part!='ram':
        # The real append frame theorem owns precisely count and the newly
        # appended cell. A caller frame theorem can hide those owned stores:
        # the native callers never read journal payload. Retain the exact
        # count/bound; output profiles still execute the real emitter.
        text=text.replace(function(text,'pd_emit'),'''static void pd_emit(PassengerDeliveryResult *result,PassengerDeliveryField field,size_t index,uint16_t value) {
 (void)field;(void)index;(void)value;
 CHECK(result->count<32,"append lemma prefix bound");result->count++;
}
''',1)
    inc.write_text(text)
    original=ROOT/'verif/delivery_harness.c';prefix=original.read_text().split('int ugh_dispatch(')[0]
    prefix=prefix.replace('stores[64]','stores[16]').replace('store_count<64','store_count<16')
    if key=='frame':
        prefix=prefix.replace('    for(unsigned i=0;i<4;i++) if(address>=vector_bases[i]', '''    if(address>=general_base && (uint32_t)address<=(uint32_t)general_base+2u*general_count) {
        CHECK(!((address-general_base)&1u),"general frame word alignment");return general_frames[(address-general_base)/2u];
    }
    for(unsigned i=0;i<4;i++) if(address>=vector_bases[i]''',1)
    prefix=prefix.replace('if(!(bank==DATA_SEG && address>=D(FallingItemDescriptors) && address<D(FallingItemVerticalStep)+24u)) record(bank,address,value,0);','record(bank,address,value,0);')
    prefix=prefix.replace('void dl_write(uint16_t bank,uint16_t address,uint16_t value) {','''void dl_write(uint16_t bank,uint16_t address,uint16_t value) {
    if(frame_watch && bank==frame_bank) {if(frame_off==address) frame_value=(uint8_t)value;if(frame_off==(uint16_t)(address+1u)) frame_value=(uint8_t)(value>>8);}
''')
    prefix=prefix.replace('void dl_byte_write(uint16_t bank,uint16_t address,uint8_t value) {','''void dl_byte_write(uint16_t bank,uint16_t address,uint8_t value) {
    if(frame_watch && bank==frame_bank && frame_off==address) frame_value=value;
''')
    # Native scalar frame/dependence runs do not execute the machine recorder;
    # its bounded trace is present only in the output-property profile.
    header='#include "ugh.h"\n#include "'+(ROOT/'native/passenger_delivery.h').as_posix()+'"\n'
    header+='void __CPROVER_assert(_Bool,const char *);void __CPROVER_assume(_Bool);\n#define CHECK(c,m) __CPROVER_assert((c),(m))\n'
    header+='static unsigned scan_calls;static int scan_selected;\nstatic uint16_t frame_bank,frame_off;static uint8_t frame_value;static int frame_watch;\n'
    if mode=='dependencies':header+='static size_t dep_index;static unsigned dep_epoch;static _Bool dep_seen[2];static PassengerDeliveryWrite dep_observed[2];\n'
    header+='static size_t seam_carrier,seam_incoming;\n'
    header+='static _Bool item_exhausted;static int sound_status;static Regs item_result,audio_result;static unsigned audio_calls;\n'
    if key=='frame':header+='static unsigned frame_piece_kind;static uint16_t *general_frames;static uint16_t general_base;static size_t general_count;\n'
    if contracted:header+=CONTRACT_HEADER
    if product_contract:header+='static uint32_t product_value;static uint16_t product_fare,product_multiplier;static unsigned native_products,reference_products,shell_products;\n'
    if contact_contract:header+=CONTACT_HEADER+'\nstatic int piece_contact_query(Regs *r);\n#define CONTACT_QUERY(r) piece_contact_query(r)\n'
    else:header+='#define CONTACT_QUERY(r) (modern_calls?c_FindPlayerTouchingActor(r):l1_FindPlayerTouchingActor(r))\n'
    code=header+'#include "pair.inc"\n'+prefix+'\n'+(ROOT/'verif/delivery_scalar_support.c').read_text()
    if contracted:code+=CONTRACT_IMPL
    if contact_contract:code+=CONTACT_IMPL
    if product_contract:
        code+='''static uint32_t pd_fare_product(uint16_t fare,uint16_t multiplier) {
 CHECK(++native_products==1,"one native fare product");product_fare=fare;product_multiplier=multiplier;return product_value;
}
static uint32_t piece_product(uint16_t fare,uint16_t multiplier,int unused) {
 (void)unused;if(modern_calls) CHECK(++shell_products==1,"one shell fare product");else CHECK(++reference_products==1,"one reference fare product");
 CHECK(native_products==1 && fare==product_fare && multiplier==product_multiplier,"fare and multiplier equality at multiplication seam");return product_value;
}
'''
    code+=SCAN_IMPL
    code+=functions(fragment,group)
    if mode=='frame' and frame_part=='ram':
        # Input equality is a separate output-property seam. This frame
        # theorem needs only the closed helper's store footprint; running the
        # native side again would introduce an irrelevant branch cross-product.
        discard=['CHECK(ntick==1 &&','CHECK(nframe==1 &&','CHECK(native_queries==1,',
                 'CHECK(native_products==1 &&','for(unsigned i=0;i<11;i++) CHECK(query_input[i]==args[i],']
        code='\n'.join(line for line in code.splitlines() if not any(line.lstrip().startswith(s) for s in discard))+'\n'
    code+='''int main(void) {
 DeliveryRam arbitrary;ram=arbitrary;DeliveryPlan plan;
 unsigned pair;__CPROVER_assume(pair<3);unsigned wet=WET;
 uint16_t arbitrary_stack[8];for(unsigned i=0;i<8;i++) stack_words[i]=arbitrary_stack[i];
 __CPROVER_assume(ram.player_count==1 || ram.player_count==2);
 __CPROVER_assume(ram.difficulty<3);
 for(unsigned i=0;i<4;i++) for(unsigned j=0;j<2;j++) __CPROVER_assume(ram.animation[i][j]!=65535u);
'''
    source_live=key in ('water','water-test','wait-motion','wait-request','destination-choice','question-clock','scan-empty','scan-any','approach-choice','board','rescue')
    dest_live=key in ('board','rescue','delivery-reward','finish')
    if source_live:code+='__CPROVER_assume(ram.actor[5]<10);ram.actor[7]=(uint16_t)(2u*ram.actor[5]);\n'
    if dest_live:code+='__CPROVER_assume(ram.actor[6]<10);ram.actor[8]=(uint16_t)(2u*ram.actor[6]);\n'
    if phase=='ACTOR_CARRIED_PASSENGER':code+='__CPROVER_assume(ram.actor[4]==0 || (ram.actor[4]==2 && ram.player_count==2));\n'
    if key in ('begin-destination','begin-question','begin-approach'):code+='wet=(_Bool)wet;\n'
    code+=f'seed_piece(&plan,{phase},wet,pair);\n'
    if mode=='frame' and frame_part!='ram':
        code+='PassengerStoneSlot retained_aliases;unsigned live_aliases=actor_phase_aliases(plan.slot.phase);\n'
        for member,bit in [('waiting_pose','WAITING_POSE'),('request_ticks','REQUEST_TICKS'),('carrier','CARRIER'),('journey_wait','JOURNEY_WAIT'),('horizontal_step','HORIZONTAL_STEP'),('floating_ticks','FLOATING_TICKS')]:
            code+=f'if(!(live_aliases&ACTOR_ALIAS_{bit})) plan.slot.{member}=retained_aliases.{member};\n'
    if key=='frame':
        code+='''unsigned kind;__CPROVER_assume(kind<4);frame_piece_kind=kind;
 uint16_t frame_bank_values[257];general_frames=frame_bank_values;
 size_t frame_count;uint16_t frame_base;__CPROVER_assume(frame_count>0 && frame_count<256);
 __CPROVER_assume(frame_base>=0x0e20u && (uint32_t)frame_base+2u*frame_count<0x1020u);
 general_base=frame_base;general_count=frame_count;ram.types[0][23+kind]=frame_base;
 __CPROVER_assume(!(ram.actor[16]&1u) && ram.actor[16]/2u<=frame_count);
 __CPROVER_assume(frame_bank_values[0]!=65535u);
 if(ram.actor[16]/2u<frame_count) __CPROVER_assume(frame_bank_values[ram.actor[16]/2u]!=65535u);
 frame_bank_values[frame_count]=65535u;
 plan.types[0].animations[kind].sprites=frame_bank_values;plan.types[0].animations[kind].count=frame_count;
'''
    code+='''size_t incoming,carrier;__CPROVER_assume(incoming<ram.player_count);__CPROVER_assume(carrier<ram.player_count);
'''
    if phase=='ACTOR_CARRIED_PASSENGER':code+='carrier=ram.actor[4]/2u;\n'
    code+='seam_carrier=carrier;seam_incoming=incoming;\n'
    if key=='approach-motion':code+='plan.result.selected=(int)carrier;\n'
    if key=='destination-clock':code+='int selected;__CPROVER_assume(selected>=-1 && selected<2);plan.result.selected=selected;\n'
    if contracted:
        code+='''PieceContract arbitrary_contract;contract=arbitrary_contract;
 ntick=nframe=rtick=rframe=stick=sframe=0;
'''
    if contact_contract:
        code+='''int choice;uint16_t boundary,qcx,qdx,qbp,qflags;__CPROVER_assume(choice>=-1 && choice<(int)ram.player_count);
 contact_index=choice;contact_boundary=boundary;contact_cx=qcx;contact_dx=qdx;contact_bp=qbp;contact_flags=qflags;
 native_queries=reference_queries=shell_queries=0;
'''
    if product_contract:code+='uint32_t arbitrary_product;product_value=arbitrary_product;native_products=reference_products=shell_products=0;\n'
    if key=='delivery-reward':code+='''_Bool exhausted;int sound;Regs item_regs,audio_regs;item_exhausted=exhausted;sound_status=sound;item_result=item_regs;audio_result=audio_regs;
'''
    if mode=='dependencies':
        code+='''size_t arbitrary_entry;__CPROVER_assume(arbitrary_entry<32);dep_index=arbitrary_entry;dep_epoch=0;dep_seen[0]=dep_seen[1]=0;
 PassengerStoneSlot independent;PassengerDeliveryWorld other_world=plan.world;
 ActorRenderHistory independent_render;independent_render.pixel_x=plan.render.pixel_x;independent_render.pixel_y=plan.render.pixel_y;
 PassengerStoneSlot before_slot=plan.slot;PassengerDeliveryResult before_result=plan.result;
 independent.type=plan.slot.type;
'''
        for n in SLOT_INPUTS[key]:code+=f'independent.{n}=plan.slot.{n};\n'
        code+=native_call(call,relation)
        if contracted:code+='unsigned first_tick=ntick,first_frame=nframe;uint16_t tc=tick_count,to=tick_cursor,tp=tick_period,fc=frame_cursor,fk=frame_kind;ntick=nframe=0;\n'
        if contact_contract:code+='uint16_t first_args[11];for(unsigned i=0;i<11;i++) first_args[i]=query_input[i];unsigned first_queries=native_queries;native_queries=0;\n'
        if product_contract:code+='uint16_t first_fare=product_fare,first_multiplier=product_multiplier;native_products=0;\n'
        second=call.replace('&plan.slot','&independent').replace('&plan.world','&other_world').replace('&plan.result','&other_result').replace('&plan.render','&independent_render')
        # Apply entries create fresh results and use the alternate slot as input.
        second=second.replace('plan.result=','other_result=')
        code+='PassengerDeliveryResult other_result=before_result;dep_epoch=1;\n'+native_call(second,relation,'second_return')
        code+='CHECK(nret==second_return,"other fields do not change stage control");\n'
        if contracted:code+='CHECK(ntick==first_tick && nframe==first_frame && (!ntick || (tc==tick_count && to==tick_cursor && tp==tick_period)) && (!nframe || (fc==frame_cursor && fk==frame_kind)),"other fields do not change helper seam arguments");\n'
        if contact_contract:code+='CHECK(native_queries==first_queries,"contact mapping dependence");for(unsigned i=0;i<11;i++) CHECK(query_input[i]==first_args[i],"contact argument dependence");\n'
        if product_contract:code+='CHECK(native_products==1 && product_fare==first_fare && product_multiplier==first_multiplier,"fare product argument dependence");\n'
        for n in SLOT_OUTPUTS.get(key,[]):
            if n=='animation':code+='CHECK(plan.slot.animation.byte_offset==independent.animation.byte_offset && plan.slot.animation.countdown==independent.animation.countdown,"animation dependence");\n'
            else:code+=f'CHECK(plan.slot.{n}==independent.{n},"slot output dependence");\n'
        for n in world_outputs(key):code+=f'CHECK({n}=={n.replace("plan.world","other_world")},"world output dependence");\n'
        code+='''CHECK(plan.result.count==other_result.count && plan.result.next==other_result.next && plan.result.selected==other_result.selected && plan.result.failed==other_result.failed && plan.result.spawn_bonus==other_result.spawn_bonus && plan.result.bonus_sound==other_result.bonus_sound && plan.result.finish_pending==other_result.finish_pending && plan.result.launch.x32==other_result.launch.x32 && plan.result.launch.y32==other_result.launch.y32,"all result/control dependence");
 CHECK(dep_seen[0]==dep_seen[1],"same arbitrary append position exists");
 if(dep_seen[0]) CHECK(dep_observed[0].field==dep_observed[1].field && dep_observed[0].index==dep_observed[1].index && dep_observed[0].value==dep_observed[1].value,"every arbitrary live journal entry has the same dependence, through the proved append lemma");
 (void)before_slot;
'''
    elif mode=='frame':
        if frame_part!='ram':code+='''unsigned object,probe;__CPROVER_assume(object<OBJECTS);
 uint8_t *cell=object==0?(uint8_t *)&plan.slot:object==1?(uint8_t *)&plan.world:object==2?(uint8_t *)&plan.render:object==3?(uint8_t *)plan.types:object==4?(uint8_t *)plan.platforms:RESULT_CELL;
 size_t length=object==0?sizeof(plan.slot):object==1?sizeof(plan.world):object==2?sizeof(plan.render):object==3?sizeof(plan.types):object==4?sizeof(plan.platforms):RESULT_LENGTH;
 __CPROVER_assume(probe<length);cell+=probe;uint8_t before=*cell;
'''+native_call(call,relation)
        allowed=[]
        for n in native_outputs(key):allowed.append(f'(object=={0 if n.startswith("plan.slot") else 1} && cell>=(uint8_t *)&{n} && cell<(uint8_t *)&{n}+sizeof({n}))')
        for n in ['count','next','selected','failed','spawn_bonus','bonus_sound','finish_pending','launch']:
            # Control outputs are checked independently, not blindly allowed in
            # the publication property. Their frame excludes only typed cells.
            allowed.append(f'(object==5 && cell>=(uint8_t *)&plan.result.{n} && cell<(uint8_t *)&plan.result.{n}+sizeof(plan.result.{n}))')
        allowed.append('(object==5 && cell>=(uint8_t *)plan.result.writes && cell<(uint8_t *)plan.result.writes+plan.result.count*sizeof(plan.result.writes[0]))')
        if frame_part!='ram':code+='if(!('+' ||\n'.join(allowed)+')) CHECK(*cell==before,"every other native state/resource/result byte unchanged");\n(void)nret;\n'
        if frame_part!='native':
            code+='''Regs r;r.ds=DATA_SEG;r.cs=GAME_SEG;r.ss=1;r.sp=36864u;r.bx=0;r.si=ram.actor[0];r.di=(uint16_t)(2u*carrier);
'''
            if key=='wait-motion':code+='r.di=ram.actor[7];\n'
            if key in ('board','rescue','delivery-prefix'):code+='r.di=(uint16_t)(2u*incoming);\n'
            if key=='product':code+='r.ax=ram.players[6][0];\n'
            if key=='award':code+='r.ax=ram.players[6][carrier];\n'
            code+='''uint16_t arbitrary_bank,arbitrary_offset;uint8_t arbitrary_byte;frame_bank=arbitrary_bank;frame_off=arbitrary_offset;frame_value=arbitrary_byte;frame_watch=1;
 modern_calls=0;store_count=tail_calls=near_calls=0;ref_piece(&r);
'''
            code+=f'if(!({raw_frame_allowed(key)})) CHECK(frame_value==arbitrary_byte,"every other RAM byte, including other physical slots and HUD high byte, unchanged");\n'
    else:
        code+='''DeliveryRam initial=ram;Regs r; r.ds=DATA_SEG;r.cs=GAME_SEG;r.ss=1;r.sp=36864u;r.bx=0;
 r.si=ram.actor[0];r.di=(uint16_t)(2u*carrier);
'''
        if key=='wait-motion':code+='r.di=ram.actor[7];\n'
        if key in ('board','rescue','delivery-prefix'):code+='r.di=(uint16_t)(2u*incoming);\n'
        if key=='product':code+='r.ax=ram.players[6][0];\n'
        if key=='award':code+='r.ax=ram.players[6][carrier];\n'
        code+='Regs bridge=r;uint16_t saved_stack[8];for(unsigned i=0;i<8;i++) saved_stack[i]=stack_words[i];\n'
        code+=native_call(call,relation)
        code+='''CHECK(!plan.result.failed,"admitted native stage");
 store_count=tail_calls=near_calls=scan_calls=audio_calls=0;modern_calls=0;int expected_status=ref_piece(&r);
 unsigned ref_scans=scan_calls;int ref_selection=scan_selected;
 unsigned ref_count=store_count,ref_tail_count=tail_calls,ref_near_count=near_calls,ref_audio_count=audio_calls;uint16_t ref_target=tail_target;Regs ref_service=service_arguments;
 ram=initial;for(unsigned i=0;i<8;i++) stack_words[i]=saved_stack[i];expected_store_count=ref_count;
 store_count=tail_calls=near_calls=scan_calls=audio_calls=0;modern_calls=1;int actual_status=bridge_piece(&bridge,&plan);
 CHECK(actual_status==expected_status || (ref_near_count && item_exhausted && expected_status==UGH_BAD_CALLBACK && actual_status==UGH_CONTROL_TRANSFER),"same stage status or established full-pool refinement");
 CHECK(store_count==ref_count && tail_calls==ref_tail_count && near_calls==ref_near_count && audio_calls==ref_audio_count,"same ordered stores and service multiplicity");
 CHECK(scan_calls==ref_scans && (!ref_scans || scan_selected==ref_selection),"same actual scan at the seam");
 CHECK(!plan.bad && plan.consumed==plan.result.count,"entire native stage journal consumed");
 if(!plan.tail_seen && !ref_near_count) CHECK(delivery_projection(&plan,&bridge),"active native working-state projection at the matching cut");
 CHECK(result_target(plan.result.next)==(ref_tail_count?ref_target:0),"native next request matches the actual L1 cut");
 CHECK(plan.result.spawn_bonus==(ref_near_count!=0) && plan.result.bonus_sound==(ref_near_count!=0) && plan.result.finish_pending==(ref_near_count && (item_exhausted || sound_status)),"complete native service/control result");
 if(!actual_status) CHECK(delivery_complete(&plan),"normal completion consumes every request and pending finish");
 if(ref_near_count) CHECK(plan.result.launch.x32==ref_service.ax && plan.result.launch.y32==ref_service.bp && !ref_service.cx && !ref_service.dx,"item request arguments at seam");
 else CHECK(!plan.result.launch.x32 && !plan.result.launch.y32,"no spurious launch output");
 CHECK(r.ax==bridge.ax && r.bx==bridge.bx && r.cx==bridge.cx && r.dx==bridge.dx && r.si==bridge.si && r.di==bridge.di && r.bp==bridge.bp && r.sp==bridge.sp && r.cs==bridge.cs && r.ds==bridge.ds && r.es==bridge.es && r.ss==bridge.ss && r.ip==bridge.ip && r.flags==bridge.flags,"complete register/flag/continuation output");
'''
        if relation=='predicate':code+='CHECK(nret==expected_status,"predicate equality");\n'
        if relation=='scan':code+='CHECK((nret>=0)==(expected_status==1) && (nret<0 || 2u*(unsigned)nret==r.di),"scan selection equality");\n'
        if relation=='gate':code+='CHECK((nret!=0)==(ref_tail_count!=0),"branch exit equality");\n'
        if relation=='success':code+='CHECK(nret==1,"motion stage completed");\n'
        if relation=='carrier':code+='CHECK(2u*(unsigned)nret==r.di,"stored carrier equality at delivery seam");\n'
        if relation=='contact':code+='CHECK(nret==(r.di==65535u?-1:(int)(r.di/2u)),"contact result mapping equality");\n'
        if relation=='product':code+='CHECK(nret==((uint32_t)r.ax|((uint32_t)r.dx<<16)),"actual 16-bit fare MUL value equality");\n'
        if contracted:code+='CHECK(ntick==rtick && ntick==stick && nframe==rframe && nframe==sframe,"all contracted helper seams consumed");\n'
        if contact_contract:code+='CHECK(native_queries==reference_queries && native_queries==shell_queries,"all contact seams consumed");\n'
        if product_contract:code+='CHECK(native_products==reference_products && native_products==shell_products,"all fare-product seams consumed");\n'
        if key in ('wait-request','destination-choice','approach-choice','question-clock'):expect='ref_scans?ref_selection:-1'
        elif key=='destination-clock':expect='selected'
        elif key=='approach-motion':expect='(int)carrier'
        elif key=='carried-transition':expect='ref_tail_count?(int)carrier:-1'
        else:expect='-1'
        code+=f'CHECK(plan.result.selected==({expect}),"native selected result is observed independently of final machine DI");\n'
    if key=='frame':
        code=code.replace('OBJECTS','7').replace('RESULT_CELL','object==5?(uint8_t *)&plan.result:(uint8_t *)frame_bank_values').replace('RESULT_LENGTH','object==5?sizeof(plan.result):sizeof(frame_bank_values)')
    else:code=code.replace('OBJECTS','6').replace('RESULT_CELL','(uint8_t *)&plan.result').replace('RESULT_LENGTH','sizeof(plan.result)')
    code+='return 0;}\n'
    if mode in ('frame','dependencies'):
        # These theorems execute native code, not the machine bridge. Keep
        # the working objects separate from the bridge's 4x256-word frame
        # scratch instead of making every typed field store an aggregate
        # update of the entire DeliveryPlan object. This changes storage only.
        marker='int main(void) {';head,body=code.split(marker,1)
        for member,name in [('slot','native_slot'),('world','native_world'),('render','native_render'),('result','native_result')]:
            body=body.replace('plan.'+member,name)
        seam=f'seed_piece(&plan,{phase},wet,pair);\n'
        assert body.count(seam)==1
        body=body.replace(seam,seam+'''PassengerStoneSlot native_slot=plan.slot;
 PassengerDeliveryWorld native_world=plan.world;ActorRenderHistory native_render=plan.render;
 PassengerDeliveryResult native_result=plan.result;
''',1)
        code=head+marker+body
    return code,inputs+[original,ROOT/'verif/delivery_pieces.py',ROOT/'verif/delivery_scalar_support.c',Path(__file__)]

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('piece',choices=pieces());p.add_argument('mode',choices=['outputs','frame','dependencies']);p.add_argument('--frame-part',choices=['both','native','ram'],default='both');p.add_argument('--timeout',type=int,default=120);a=p.parse_args()
    folder=OUT/'scalar'/(a.piece+'-'+a.mode+('-'+a.frame_part if a.mode=='frame' and a.frame_part!='both' else ''));folder.mkdir(parents=True,exist_ok=True)
    code,inputs=make(a.piece,a.mode,folder,a.frame_part);source=folder/'harness.c';source.write_text(code)
    wet='1' if a.piece=='rescue' else 'nondet_wet' if a.piece in ('begin-destination','begin-question','begin-approach') else '0'
    code=code.replace('unsigned wet=WET;','_Bool nondet_wet;unsigned wet='+wet+';');source.write_text(code)
    question='1' if a.piece in ('question-clock','contact-question') else '0'
    frame_loops='piece_actual_frame.0:3,piece_actual_pd_shell1_frame.0:3' if a.piece in CONTRACTS else 'dl_ref1_frame.0:3,pd_shell1_frame.0:3'
    loops='dl_ref0_contact.0:3,observed_actual_platform_player.0:3,observed_actual_pd_shell1_platform_player.0:3,'+frame_loops
    result=cbmc(source,folder,inputs,unwind=40,timeout=a.timeout,defines=['-D__CPROVER__','-DACTOR_VERIFY',f'-DQUESTION={question}','-DUINT16_MAX=65535u'],extra=[*SMT,'--unwindset',loops,'--no-array-field-sensitivity'])
    print(json.dumps({k:result[k] for k in ['result','seconds','peak_private_bytes','failures']}),flush=True);assert result['result']=='PASS'
if __name__=='__main__':main()
