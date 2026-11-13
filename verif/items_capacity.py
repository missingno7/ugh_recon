"""Static shipped-source envelope; B, with explicit source/lifecycle assumptions.

The integer stone lemmas are models, not CBMC on the stone implementation.
They are linked by the stated static review of every thrown-stone writer.
Flight enumeration executes maintained native C (linked to L1 by step proof).
"""
import json,re,struct,subprocess,sys
from pathlib import Path
from closure_support import ROOT,compile_c,receipt,save
from items_build import OUT
import contacts_reference
contacts_reference.OUT=OUT/'reference'
from contacts_reference import expanded_image
sys.path.insert(0,str(ROOT/'tools'))
from common import MZ
import dataprobe
manifest=json.loads((ROOT/'metadata/verif-tools.json').read_text())
sys.path.insert(0,re.search(r'[A-Za-z]:[/\\]\S+',manifest['z3']['install'])[0])
import z3
assert z3.get_version_string()==manifest['z3']['version']

def main():
    folder=OUT/'capacity';folder.mkdir(parents=True,exist_ok=True)
    inputs=[ROOT/'native/items.c',ROOT/'native/items.h',ROOT/'native/contacts.c',ROOT/'native/contacts.h',ROOT/'native/geometry.h',ROOT/'native/level.h',ROOT/'verif/items_capacity.c',Path(__file__)]
    exe=folder/'capacity.exe';built=compile_c([inputs[0],inputs[2],inputs[-2]],exe,[ROOT/'native'])
    run=subprocess.run([str(exe)],capture_output=True,text=True);assert run.returncode==0,run.stderr
    flight=json.loads(run.stdout)
    # Stone v'=v+2, y'=y+v': E=v*v+2*v-4*y is invariant.
    # Descending-contact NEG/SAR halve the speed or negate it, reducing E.
    y,v=z3.Ints('y v');energy=lambda y,v:v*v+2*v-4*y
    solver=z3.Solver();solver.add(energy(y+v+2,v+2)!=energy(y,v));assert solver.check()==z3.unsat
    solver=z3.Solver();solver.add(v>=0,energy(y,-v)>energy(y,v));assert solver.check()==z3.unsat
    solver=z3.Solver();half=-((v+1)/2);solver.add(v>=0,v<=512,energy(y,half)>energy(y,v));assert solver.check()==z3.unsat
    # Throw: |v|<=192, y>=-464. E<=39104; active stored y<=6256.
    # Thus all descending contact speeds <512, even allowing one gravity step.
    solver=z3.Solver();solver.add(y<=6256,energy(y,v)<=39104,v>=510);assert solver.check()==z3.unsat
    mz=MZ(expanded_image().read_bytes());_,orders=dataprobe.levels(mz);d=mz.image[0x5c090:]
    word=lambda at:struct.unpack_from('<H',d,at)[0]
    descriptor_rows=[]
    for i in range(11):
        values=list(struct.unpack_from('<10H',d,0x7970+20*i));descriptor_rows.append(values)
        assert values[:2]==[8,16] and 14<=values[6]<=71
    for ordinal in range(6):
        base=0x7720+ordinal*74;assert word(base+62)==7
        for field in [54,56]:
            cursor=word(base+field);length=0
            while word(cursor+2*length)!=65535:length+=1
            assert length==9
    rows=[];reward_lists=set();small_gaps=[]
    for entry in orders:
        assert all(24<=p[2]-p[2]//4<=180 for p in entry['platforms'])
        passengers=[]
        for descriptor,platform,cursor in entry['actors']:
            if descriptor==0x78dc:continue
            waits=[]
            while word(cursor)!=65535:
                waits.append(word(cursor+2));cursor+=4
            # A delivery consumes the NEXT leg's platform. The final leg has
            # no next destination and produces no further delivery/reward.
            times=[0] if len(waits)>1 else []
            for wait in waits[1:-1]:
                # Retained nine-frame animations: departure 1+8*7=57;
                # arrival through its sentinel 1+9*7=64; destination wait 140.
                # Omitting walks, travel and extra state visits weakens the bound.
                gap=57+64+140+wait+wait//2
                times.append(times[-1]+gap);small_gaps.append(gap)
            bound=max([sum(0<=t-start<700 for t in times) for start in times] or [0])
            passengers.append(dict(deliveries=len(times),minimal_times=times,bound=bound))
        trees=0
        for enemy in entry['enemies']:
            if enemy[0]!=0x76e4:continue
            trees+=1;cursor=enemy[2];rewards=[]
            while word(cursor)!=65535:rewards.append((word(cursor)-0x7970)//20);cursor+=2
            reward_lists.add(tuple(rewards))
            assert rewards==[0,8,5,7,6,1,4,3,2]
        total=trees*4+sum(p['bound'] for p in passengers)
        # Tree cooldown 210 alone suffices: five spawns span >=840 updates.
        # The six-update contact cadence would tighten this and is unnecessary.
        assert total<=12
        rows.append(dict(players=entry['players'],level=entry['number'],tree_bound=4*trees,passengers=passengers,total=total))
    # Static source identities also demonstrate that the life descriptor is not
    # produced by either shipped spawn source. Do not invent a play witness.
    assert word(0x7a38+18)==2 and all(9 not in r for r in reward_lists)
    result=receipt(['python','verif/items_capacity.py'],[*inputs,ROOT/'c/actors.c',ROOT/'c/actors_states.c',ROOT/'c/scene.c',ROOT/'c/render.c',ROOT/'src/asm/GAME.ASM',ROOT/'src/data/DGDATA.ASM',ROOT/'tools/dataprobe.py'],
        result='PASS',level='B',flight=flight,maximum_post_spawn_bound=max(r['total'] for r in rows),maximum_pre_spawn_bound=max(r['total'] for r in rows)-1,
        minimal_interdelivery_gap=min(small_gaps),orders=rows,descriptors=descriptor_rows,
        reward_lists=[list(r) for r in reward_lists],unspawned_descriptor_ordinals=[9],
        static_assumptions=[
            'Serialized shipped gameplay, intact loader/descriptor/itinerary state; no external state or arbitrary callback injection.',
            'Craft position bounds -608..6112 and velocity +/-6144 at ThrowCarriedStone; stone initial y=craftY+144, v=SAR5(craftVy).',
            'Thrown-stone gravity preserves E=v*v+2*v-4*y; descending enemy contacts only NEG or SAR(NEG,1); landing ends thrown phase.',
            'Tree contact gives enemyY-256 <= stoneY <= enemyY+640; item initialY=stoneY-256, treeY=32*platformY-768; all platformY>=24.',
            'Flight launch speed <=135 (71 plus SAR2 of the bounced stone speed); no repeated flight entry after landing.',
            'Between consecutive deliveries for one actor, next-leg scaled wait, complete nine-frame departure and arrival animations and 140 destination countdown cannot be bypassed.',
            'Every active frame dispatches items after all actor/tree spawns; level/retry initialization clears item sprites. Pause freezes producers and consumers together.',
            '700 is a strict lifetime window, including a pending pre-dispatch update; counts above include the new spawn, hence at most 11 occupied before allocation.'],
        compiler=built,z3_version=z3.get_version_string())
    save(folder/'result.json',result)
    print(json.dumps({k:result[k] for k in ['result','flight','maximum_post_spawn_bound','maximum_pre_spawn_bound','minimal_interdelivery_gap','unspawned_descriptor_ordinals']}))

if __name__=='__main__':main()
