"""Static plus descriptor-indirect caller check before water witness selection."""
import hashlib,json,re,struct
from closure_support import ROOT,function,receipt,save
from water_build import OUT
from water_shells import NAMES
def main():
    import contacts_reference as reference
    reference.OUT=OUT/'reference';image=reference.expanded_image(local=True);raw=image.read_bytes()[0xa00:];data=raw[0x5c09*16:]
    source=(ROOT/'c/actors.c').read_text();states=(ROOT/'c/actors_states.c').read_text();descriptors=[]
    fields=[(0x0a,'UpdatePassengerResurfacing'),(0x0c,'BeginPassengerSinking'),(0x0e,'UpdatePassengerSinking'),(0x10,'BeginPassengerFloating'),(0x12,'UpdatePassengerFloating'),(0x14,'BeginPassengerDestinationDisplay'),(0x16,'UpdateFloatingDestinationDisplay'),(0x18,'BeginPassengerQuestionDisplay'),(0x1a,'UpdateFloatingQuestionDisplay'),(0x1c,'BeginPassengerApproach'),(0x1e,'UpdateFloatingPassengerApproach'),(0x20,'BoardWaterbornePassenger')]
    symbols=(ROOT/'c/ugh_sym.h').read_text()
    def address(name):return int(re.search(r'#define UGH_O_GAME_'+name+r' (0x[0-9A-Fa-f]+)u',symbols)[1],16)
    for identity in [0x776a,0x77fe,0x7892]:
        words=struct.unpack_from('<37H',data,identity)
        for field,name in fields:assert words[field//2]==address(name)
        assert words[18]==words[19]==address('IgnoreWaterbornePassengerState')
        assert words[22]==address('IgnoreActorState') and words[36]==identity-74
        descriptors.append(dict(identity=hex(identity),paired=hex(words[36]),callbacks={hex(f):n for f,n in fields},unused={'0x24':'IgnoreWaterbornePassengerState','0x26':'IgnoreWaterbornePassengerState'},retirement={'0x2c':'IgnoreActorState'},lifetime=words[34]))
    float_body=function(source,'c_UpdatePassengerFloating');assert 'sub16(r,r->si,D(Data_77FE),0);' in float_body and 'if(!(r->flags&ZF)) {' in float_body
    tails={}
    for n in NAMES:
        body=function(source,'c_'+n);tails[n]=re.findall(r'tail\(r,(0x[0-9a-f]+)\)',body)
    assert not any(field in ('0x24','0x26') for fields_ in tails.values() for field in fields_)
    board=function(states,'c_BoardWaterbornePassenger');assert board.index('PlayerPassengerFares')<board.index('F(0x48)')<board.index('F(0x22)')
    swap=function(states,'water_swap');assert 'return tail(r,8)' in swap
    direct={n:[] for n in NAMES}
    for path in sorted((ROOT/'c').glob('*.c')):
        for line,text in enumerate(path.read_text().splitlines(),1):
            for name in NAMES:
                if re.search(r'\bc_'+name+r'\(',text) and not text.startswith('EXPORT int c_'+name):direct[name].append(dict(file=path.relative_to(ROOT).as_posix(),line=line,text=text.strip()))
    measured=json.loads((OUT/'integration.json').read_text()) if (OUT/'integration.json').exists() else {}
    coverage=[]
    for path in sorted((OUT/'whole').glob('*.ref.json')):
        oracle=json.loads(path.read_text());coverage.append(dict(scenario=path.name[:-9],routines=[n for n in oracle['coverage']['routines'] if n in ['GAME:'+x for x in NAMES]]))
    save(OUT/'reachability.json',receipt(['python','verif/water_reachability.py'],[__file__,image,ROOT/'c/actors.c',ROOT/'c/actors_states.c',ROOT/'c/ugh_sym.h',ROOT/'docs/actor-storage.md'],result='PASS',descriptors=descriptors,literal_tails=tails,direct_call_sites=direct,original_coverage=coverage,scenario_native_counts=measured.get('scenario_audits',[]),
      finding='Only items-timer currently reaches water passengers in measured maintained scenarios (resurfacing). water/passenger/departure each have zero native entries AND zero ASM routine coverage. This contradicts the work-order coverage expectation and is reported rather than inferred from the scenario name.',
      second_pair='Normal entry through land-to-water swap -> resurfacing -> floating. 77FE skips FLOAT carrier search, so it cannot reach shared destination initializer through that transition; lifetime alone can sink it. Forced direct request/approach entry remains admitted and is not disguised as normally reachable.',
      noop='2195 exists only at water descriptor +24/+26. No normal water handler calls either field. Rescue loads fare/floor before pairing, then selects land +22; carried/delivery/exit therefore use the land type. Sink retirement uses water +2C=1C0E. An input-only 2195 witness is not justified under these invariants; direct no-op properties remain proved.',
      witness_decision='Other water transitions have feasible static/indirect callers. Extending the existing items-timer input trace is worth trying to reach floating/sinking; use a fixed input-only witness only if independently verified against L0.'))
    print('PASS static and indirect water caller/identity check')
if __name__=='__main__':main()
