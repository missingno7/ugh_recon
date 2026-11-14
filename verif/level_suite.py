"""Independent level-coverage gate. Default game gates and maintained tools stay unchanged.

python verif/level_suite.py --generate
python verif/level_suite.py --all
python verif/level_suite.py --group audio --all
python verif/level_suite.py --group deep --all

References use tools.wholegame.fixture/original/identity and the reconstructed
ASM image, never a native executable. Cached data lives in build/levels, separate
from build/whole. --all pins committed HEAD plus this suite and runs serially;
every child has an owned 8-GiB/600-s Windows Job. New groups start at the program
entry; the original openings use the cold/password fixture. Extra hooks only
read state/count entries. New scenario directories pin their script bytes to LF.
"""
import argparse,ctypes as C,gc,hashlib,io,json,os,re,shutil,subprocess,sys,tarfile,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build/workers/close-stones-17'
CACHE=ROOT/'build/levels'
SUITE=ROOT/'tests/levels'
sys.path.insert(0,str(ROOT/'tools'))
from closure_support import hashes,save
import ice_scratch as runner
runner.OUT=OUT
bounded=runner.bounded
SCHEMA=2
GROUP="openings"

def set_group(group):
    global GROUP,SUITE,CACHE,OUT,SCHEMA
    GROUP=group;SCHEMA=1 if group=="openings" else 2;suffix={"openings":"","audio":"-audio","deep":"-deep"}[group]
    SUITE=ROOT/("tests/levels"+suffix);CACHE=ROOT/("build/levels"+suffix)
    OUT=ROOT/"build/workers/close-stones-17"/group;runner.OUT=OUT

def suite_files():
    return [Path(__file__),*[p for folder in ROOT.glob("tests/levels*") if folder.is_dir() for p in sorted(folder.iterdir()) if p.is_file()]]

def resources():
    import cgen,dataprobe
    mz,symbols=cgen.read_symbols();maps,orders=dataprobe.levels(mz)
    return mz,symbols,maps,orders

def selection():
    orders=resources()[3];one=[r for r in orders if r['players']==1]
    known={r['record'] for r in one}
    return one+[r for r in orders if r['players']==2 and r['record'] not in known]

def generate():
    SUITE.mkdir(parents=True,exist_ok=True);rows=selection();assert len(rows)==81
    for r in rows:
        name=f"{'one' if r['players']==1 else 'two'}-{r['number']:02d}"
        second=' 11' if r['players']==2 else ''
        second_up=' -11' if r['players']==2 else ''
        second_right=' 20' if r['players']==2 else ''
        second_right_up=' -20' if r['players']==2 else ''
        second_down=' 2c' if r['players']==2 else ''
        second_down_up=' -2c' if r['players']==2 else ''
        second_action=' 1d' if r['players']==2 else ''
        second_action_up=' -1d' if r['players']==2 else ''
        text=f'''# Physical record {r['record']}; {r['players']}P order {r['number']}; map {r['map']}; {r['title']}
# Shipped password, standard cold-session fixture; no level-state patching.
timing pit-quantum-at-polls
entry GAME:RunGameFromPassword
password {r['password']}
players {r['players']}
frames 160
card none
1: cycle=enter,-enter
8: cycle=off -enter
104: up{second}
120: -up{second_up} right{second_right}
136: -right{second_right_up} down{second_down}
144: -down{second_down_up} 52{second_action}
145: -52{second_action_up}
148: left
156: -left
requires GAME:LoadCurrentLevelState GAME:InitializeLevelDisplay GAME:DrawTileMap GAME:DispatchActorUpdates GAME:DrawWaterSurface GAME:MovePlayerWithVgaCollisions
'''
        (SUITE/(name+'.txt')).write_text(text,encoding='utf-8')
    if not (SUITE/'README.md').exists():(SUITE/'README.md').write_text('''# Optional level coverage

This suite is separate from the default twenty scenarios. It covers all 69
one-player positions, followed by the 12 two-player positions whose physical
records are absent from the one-player order (12,18,...,78). Passwords and
record identities come from the freshly reconstructed resource tables.

Run `python tools/build.py`, then `python verif/level_suite.py --all`.
`--generate` deterministically regenerates these input-only scripts. References
are generated with the maintained reconstructed-ASM runner into `build/levels`;
neither native nor literal host output is used as an expected result. The driver
then compares both hosts, preserving the maintained RAM/device/ordered-log and
scalar observation model. No default tool directory or behavior is changed.

Each 160-boundary script supplies a password through the existing session path,
skips presentations with Enter, then supplies short keyboard thrust/direction
and action bursts. Two-player extras also move player two. Coverage reports
successful loader returns and actual routine-entry counts (including presentation
calls). Gameplay requirements establish that the selected record was drawn and
simulated; a listed password alone is not credited as level coverage.
''',encoding='utf-8')
    print('Generated',len(rows),'scenarios',flush=True)

def expected(path,orders=None):
    import wholegame
    s=wholegame.scenario(path);orders=orders or resources()[3]
    matches=[r for r in orders if r['players']==s.get('players',1) and r['password']==s.get('password','CAVITY')]
    assert len(matches)==1,(path.name,'password identity');return s,matches[0]

def coverage_contract(path,data):
    manifest=SUITE/'coverage.json'
    if not manifest.exists():return
    goal=json.loads(manifest.read_text()).get(path.stem,{})
    observed=data['inventory']
    for name,minimum in goal.get('calls',{}).items():
        assert observed['calls'].get(name,0)>=minimum,(path.stem,'unreached',name)
    for name,minimum in goal.get('cuts',{}).items():
        assert observed.get('cuts',{}).get(name,{}).get('count',0)>=minimum,(path.stem,'unreached branch cut',name)
    for wanted in goal.get('loads',[]):
        assert any(all(load.get(k)==v for k,v in wanted.items()) for load in observed['loads']),(path.stem,'missing load',wanted)
    for name,value in goal.get('final',{}).items():
        assert data['frames'][-1]['scalars'][name]==value,(path.stem,'final scalar',name)
    for wanted in goal.get('audio',[]):
        from emu import LOAD
        assert any(event['entry']==wanted['entry'] and event['arguments'][:2]==[int(wanted['offset'],16),LOAD+int(wanted['frame'],16)] and event['device']&1 for event in observed.get('audio',[])),(path.stem,'missing active AdLib request',wanted)


def reference(names,refresh=False):
    import wholegame as whole
    from emu import NativeVga
    from unicorn import UC_HOOK_CODE
    CACHE.mkdir(parents=True,exist_ok=True);OUT.mkdir(parents=True,exist_ok=True)
    ledger=ROOT/'build/workers/c-close/call-edges.json'
    # Optional old coverage-attribution data is not an oracle dependency.
    # Redirect that one read to a private empty ledger, without modifying tools.
    local=OUT/'reference-ledger.json';save(local,[])
    class ReadRoot(type(ROOT)):
        def __truediv__(self,value):
            if str(value)=='build/workers/c-close/call-edges.json':return local
            return super().__truediv__(value)
    whole.ROOT=ReadRoot(ROOT)
    work=OUT/('reference-'+str(os.getpid()));work.mkdir(parents=True,exist_ok=True)
    accelerator=NativeVga(work);whole.VGA_ACCELERATOR=accelerator
    orders=resources()[3];rows=[]
    try:
        for name in names:
            path=SUITE/(name+'.txt');s,target=expected(path,orders);started=time.perf_counter()
            m,initial=whole.fixture(s);key=whole.identity(path,m);cache=CACHE/(name+'.ref.json')
            old=json.loads(cache.read_text()) if cache.exists() else {}
            if not refresh and old.get('key')==key and old.get('suite_version')==SCHEMA:
                assert old['target']['record']==target['record'];coverage_contract(path,old);rows.append(dict(scenario=name,mode='cached',seconds=time.perf_counter()-started));continue
            frame=[0];loads=[];calls={};first={};ticks=[];audio=[];cuts={}
            names_to_count=['InitializeLevelDisplay','LoadCurrentLevelState','MovePlayerWithVgaCollisions',
                'DispatchActorUpdates','DrawTileMap','DrawWaterSurface','AdvanceRainParticles','DrawRainParticles',
                'Passenger_Wait','Passenger_Request','Passenger_Approach','Passenger_Carried',
                'Passenger_Delivered','Passenger_Floating','Passenger_Sinking']
            # Include every real actor handler, without guessing labels from prose.
            import re
            native_exports=set()
            for component in ['passenger_delivery','passenger_water','passenger_itinerary','stones','hazards']:
                cert=json.loads((ROOT/'metadata/closure'/f'{component}.json').read_text())
                for p in cert['native']['files']:
                    if '/bridge/' in p:native_exports.update(re.findall(r'\bEXPORT\s+int\s+c_(\w+)\s*\(', (ROOT/p).read_text()))
            names_to_count+=sorted(native_exports)
            for n in sorted(set(names_to_count)):
                symbol='GAME:'+n
                if symbol not in m.symbols:continue
                seg,off=m.address(symbol)
                def entry(uc,address,size,user):
                    calls[user]=calls.get(user,0)+1;first.setdefault(user,frame[0])
                m.uc.hook_add(UC_HOOK_CODE,entry,user_data=n,begin=seg*16+off,end=seg*16+off)
            # Far cdecl API entries: arguments start after the four-byte return.
            for symbol in ['C:StartMusicTrack','C:PlayAdlibEffect','C:ScanMusicEvents']:
                aseg,aoff=m.address(symbol)
                def audio_entry(uc,address,size,user):
                    sp=m.reg('SP');ss=m.reg('SS')
                    args=[int.from_bytes(m.read(ss,(sp+4+2*i)&65535,2),'little') for i in range(4)]
                    audio.append(dict(entry=user,frame=frame[0],arguments=args,caller=[int.from_bytes(m.read(ss,sp,2),'little'),int.from_bytes(m.read(ss,(sp+2)&65535,2),'little')],device=m.rw('SOUND:SoundDeviceBits')))
                m.uc.hook_add(UC_HOOK_CODE,audio_entry,user_data=symbol,begin=aseg*16+aoff,end=aseg*16+aoff)
            if name=='dino-adlib':
                # Count the real ADD to player velocity, not just its handler.
                from capstone import Cs,CS_ARCH_X86,CS_MODE_16
                cseg,coff=m.address('GAME:loc_2A36')
                instruction=next(Cs(CS_ARCH_X86,CS_MODE_16).disasm(m.read(cseg,coff,8),coff))
                assert instruction.mnemonic=='add' and 'di' in instruction.op_str and instruction.op_str.endswith(', ax')
                assert hex(m.off('DGROUP:PlayerHorizontalVelocities')) in instruction.op_str
                cuts['GAME:loc_2A36']=dict(count=0,first_frame=None,addends={})
                def dino_force(uc,address,size,user):
                    ax=m.reg('AX');assert ax in (41,65495)
                    item=cuts['GAME:loc_2A36'];item['count']+=1
                    if item['first_frame'] is None:item['first_frame']=frame[0]
                    key=f'{ax:04X}';item['addends'][key]=item['addends'].get(key,0)+1
                m.uc.hook_add(UC_HOOK_CODE,dino_force,begin=cseg*16+coff,end=cseg*16+coff)
            def loaded(uc,address,size,user):
                players=m.rw('DGROUP:PlayerCount');index=m.rw('DGROUP:CurrentLevelIndex')
                table=int.from_bytes(m.read(m.seg('DGROUP:LevelOrderTables'),m.off('DGROUP:LevelOrderTables')+(players-1)*2,2),'little')
                pointer=int.from_bytes(m.read(m.seg('DGROUP:LevelOrderTables'),table+index*2,2),'little')
                raw=m.read(m.seg('DGROUP:CurrentLevelRecord'),m.off('DGROUP:CurrentLevelRecord'),26)
                source=m.read(m.seg('DGROUP:LevelOrderTables'),pointer,26)
                # Loader replaces the record's water word with its scaled/capped
                # working value. All other record bytes retain the copied seed.
                assert raw[:21]==source[:21] and raw[23:]==source[23:],'loader record copy'
                loads.append(dict(frame=frame[0],players=players,number=index+1,record=f'{pointer:04X}',water=m.rw('DGROUP:WaterYPixels')))
            # This is the real post-call cut, checked from rebuilt instruction bytes.
            seg,off=m.address('GAME:InitializeLevelDisplay');load_seg,load_off=m.address('GAME:LoadCurrentLevelState')
            from capstone import Cs,CS_ARCH_X86,CS_MODE_16
            matches=[]
            for ins in Cs(CS_ARCH_X86,CS_MODE_16).disasm(m.read(seg,off,512),off):
                if ins.mnemonic=='call' and ins.op_str==hex(load_off):matches.append(ins.address+ins.size)
            assert len(matches)==1,matches
            m.uc.hook_add(UC_HOOK_CODE,loaded,begin=seg*16+matches[0],end=seg*16+matches[0])
            swap_seg,swap_off=m.address(whole.FRAME)
            def boundary(uc,address,size,user):
                frame[0]+=1
                if os.environ.get('LEVEL_SUITE_PROGRESS'):(OUT/('progress-'+name+'.txt')).write_text(str(frame[0])+' '+str(m.reg('CS'))+':'+str(m.reg('IP')))
                if calls.get('MovePlayerWithVgaCollisions',0):
                    ticks.append(dict(frame=frame[0],x=m.rw('DGROUP:PlayerPixelX'),y=m.rw('DGROUP:PlayerYPixels'),
                        carried=m.rw('DGROUP:PlayerCarriedKinds'),water=m.rw('DGROUP:WaterYPixels')))
            m.uc.hook_add(UC_HOOK_CODE,boundary,begin=swap_seg*16+swap_off+0x2a,end=swap_seg*16+swap_off+0x2a)
            frames,coverage,snapshots=whole.original(s,m,initial,progress=bool(os.environ.get("LEVEL_SUITE_PROGRESS")))
            reached=any(l['record']==target['record'] and l['players']==target['players'] and l['number']==target['number'] for l in loads)
            missing=set(s['requires'])-set(coverage['routines'])
            if not reached or missing:save(OUT/(name+'-coverage-negative.json'),dict(scenario=name,loads=loads,calls=calls,first=first,audio=audio,missing=sorted(missing),target_reached=reached,final=frames[-1]))
            assert reached,(name,loads,'wrong level')
            assert not missing,(name,missing)
            data=dict(key=key,version=whole.VERSION,suite_version=SCHEMA,frames=frames,coverage=coverage,
                target={k:target[k] for k in ['record','players','number','password','map','title','weather','water','water_delta']},
                inventory=dict(loads=loads,calls=calls,first=first,movement=ticks,audio=audio,cuts=cuts,
                               successful_load_cut=f'{seg:04X}:{matches[0]:04X}'),
                provenance=dict(source='reconstructed-ASM via tools.wholegame.original',image_sha256=hashlib.sha256(m.raw_image).hexdigest(),
                    tools=hashes([ROOT/'tools/wholegame.py',ROOT/'tools/emu.py',Path(__file__)])))
            coverage_contract(path,data);save(cache,data);snapshots.clear();rows.append(dict(scenario=name,mode='reference',seconds=time.perf_counter()-started))
            print('REF',name,target['record'],len(frames),'frames',round(rows[-1]['seconds'],3),'s',flush=True)
            del m,snapshots;gc.collect()
    finally:whole.VGA_ACCELERATOR=None;accelerator.close()
    save(OUT/('reference-'+names[0]+'.json'),dict(result='PASS',scenarios=rows))

def first_difference(actual,expected):
    return next((i for i in range(max(len(actual),len(expected))) if
        (actual[i] if i<len(actual) else None)!=(expected[i] if i<len(expected) else None)),None)

def check(variant,names):
    receipt=json.loads((ROOT/'build/host/hostbuild.json').read_text())
    assert receipt['variant']=={'native':'native-bridged','literal':'literal'}[variant]
    exe=ROOT/'build/host/ugh.exe';assert hashlib.sha256(exe.read_bytes()).hexdigest()==receipt['executable_sha256']
    rows=[];mz,_,_,orders=resources()
    import wholegame
    from types import SimpleNamespace
    for name in names:
        path=SUITE/(name+'.txt');s,target=expected(path,orders)
        ref=json.loads((CACHE/(name+'.ref.json')).read_text())
        coverage_contract(path,ref)
        assert ref['key']==wholegame.identity(path,SimpleNamespace(raw_image=mz.image)),name+' stale reference'
        command=[exe,'--headless',str(s['frames']),'--script',path,'--timeout','30']
        result=bounded(command,variant+'-'+name,ok=range(-2**32,2**32))
        got=[];parse_error=None
        for line in result['stdout'].splitlines():
            try:got.append(json.loads(line))
            except json.JSONDecodeError:parse_error=line;break
        wanted=ref['frames'];index=first_difference(got,wanted)
        passed=result['returncode']==0 and index is None and parse_error is None
        row=dict(scenario=name,variant=variant,record=target['record'],passed=passed,boundaries=len(got),expected=len(wanted),seconds=result['seconds'],
                 executable_sha256=receipt['executable_sha256'],reference_key=ref['key'])
        if not passed:
            row.update(frame=index+1 if index is not None else len(got)+1,
                expected_record=wanted[index] if index is not None and index<len(wanted) else None,
                actual_record=got[index] if index is not None and index<len(got) else None,
                returncode=result['returncode'],stderr=result['stderr'],malformed_record=parse_error)
            repro=OUT/'findings'/(name+'-'+variant+'.txt');repro.parent.mkdir(parents=True,exist_ok=True)
            bound=min(row['frame'],s['frames'])
            text=re.sub(r'^frames \d+$','frames '+str(bound),path.read_text(),flags=re.M)
            text='\n'.join(line for line in text.splitlines() if not re.match(r'^\d+:',line) or int(line.split(':')[0])<bound)+'\n'
            repro.write_text(text,encoding='utf-8');row['reproduction']=str(repro.relative_to(ROOT))
            save(OUT/(variant+'-'+name+'.divergence.json'),row)
        rows.append(row);print(('PASS' if passed else 'DIVERGENCE'),variant,name,flush=True)
    save(OUT/('check-'+variant+'-'+names[0]+'.json'),dict(result='PASS' if all(r['passed'] for r in rows) else 'DIVERGENCES',scenarios=rows))
    return all(r['passed'] for r in rows)

def controls():
    import copy
    rows=[];ref=json.loads((CACHE/'one-01.ref.json').read_text())['frames']
    assert first_difference(ref,ref) is None
    for key in ['ram','device','log','scalars']:
        changed=copy.deepcopy(ref)
        if key=='scalars':changed[2][key]['LivesRemaining']^=1
        else:changed[2][key]='0'*64 if changed[2][key]!='0'*64 else '1'*64
        assert first_difference(changed,ref)==2
        rows.append(dict(mutation=key,detected_frame=3))
    assert first_difference(ref[:-1],ref)==len(ref)-1
    assert first_difference([*ref,ref[-1]],ref)==len(ref)
    rows.extend([dict(mutation='missing frame',detected_frame=len(ref)),dict(mutation='extra frame',detected_frame=len(ref)+1)])
    baseline=OUT
    if (OUT/'baseline.json').exists():baseline=ROOT/json.loads((OUT/'baseline.json').read_text())['path']/OUT.relative_to(ROOT)
    rechecked=0
    for variant in ['native','literal']:
        for path in sorted(SUITE.glob('*.txt')):
            log=baseline/(variant+'-'+path.stem+'.json')
            if not log.exists():continue
            result=json.loads(log.read_text());actual=[json.loads(line) for line in result['stdout'].splitlines()]
            expected_frames=json.loads((CACHE/(path.stem+'.ref.json')).read_text())['frames']
            assert result['returncode']==0 and first_difference(actual,expected_frames) is None
            rechecked+=1
    save(OUT/'comparison-controls.json',dict(result='PASS',mutations=rows,actual_host_outputs_rechecked=rechecked))
    print('Controls PASS',len(rows),'negative cases;',rechecked,'actual host outputs rechecked',flush=True)

def branch_report():
    from emu import LOAD
    refs={p.stem:json.loads((CACHE/(p.stem+'.ref.json')).read_text()) for p in sorted(SUITE.glob('*.txt'))}
    entries=set()
    for component in ['passenger_delivery','passenger_water','passenger_itinerary','stones','hazards']:
        cert=json.loads((ROOT/'metadata/closure'/f'{component}.json').read_text())
        for file in cert['native']['files']:
            if '/bridge/' in file:entries.update(re.findall(r'\bEXPORT\s+int\s+c_(\w+)\s*\(', (ROOT/file).read_text()))
    lines=['Counts are reference routine entries, including zero calls. Frames are completed page flips.',
        '', '| Entry | '+' | '.join(refs)+' |','|---|'+'---:|'*len(refs)]
    for name in sorted(entries):
        lines.append('| '+name+' | '+' | '.join(str(r['inventory']['calls'].get(name,0)) for r in refs.values())+' |')
    audio=[]
    for name,r in refs.items():
        groups={}
        for event in r['inventory'].get('audio',[]):
            args=event['arguments'];entry=event['entry']
            key=(entry,args[0],args[1],*args[2:],*event['caller'],event['device'])
            if key not in groups:groups[key]=dict(scenario=name,entry=entry,arguments=args,caller=event['caller'],device=event['device'],count=0,first_frame=event['frame'])
            groups[key]['count']+=1
        audio.extend(groups.values())
    save(OUT/'audio-requests.json',audio)
    lines+=['','| Scenario | Audio entry | Resource / scan bounds | Remaining args | Caller | Device bits | Count | First flip |','|---|---|---|---|---|---:|---:|---:|']
    for e in audio:
        a=e['arguments'];resource=f'{a[1]-LOAD:04X}:{a[0]:04X}' if e['entry']!='C:ScanMusicEvents' else str(a[:2])
        lines.append(f"| {e['scenario']} | {e['entry']} | {resource} | {a[2:]} | {e['caller'][1]-LOAD:04X}:{e['caller'][0]:04X} | {e['device']} | {e['count']} | {e['first_frame']} |")
    lines+=['','Additional branch cuts (only instrumented cases are listed):']
    for name,r in refs.items():
        for cut,counts in r['inventory'].get('cuts',{}).items():lines.append(f"- {name}, {cut}: {counts}")
    (OUT/'BRANCHES.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')


def inventory():
    orders=resources()[3];records={r['record']:dict(record=r['record'],title=r['title'],map=r['map'],weather=r['weather'],orders=[],observed=[]) for r in orders}
    for r in orders:records[r['record']]['orders'].append(dict(players=r['players'],number=r['number'],password=r['password']))
    checks={label:json.loads((OUT/('check-'+label+'.json')).read_text()) for label in ['native','literal']}
    checked={label:{r['scenario']:r for r in data['scenarios']} for label,data in checks.items()}
    for path in sorted(SUITE.glob('*.txt')):
        ref=json.loads((CACHE/(path.stem+'.ref.json')).read_text())
        for load in ref['inventory']['loads']:
            records[load['record']]['observed'].append(dict(scenario=path.stem,**load,
                 native=checked['native'][path.stem]['passed'],literal=checked['literal'][path.stem]['passed']))
    result=dict(total_records=len(records),covered_records=sum(bool(r['observed']) for r in records.values()),
        one_player_positions=sorted({l['number'] for r in records.values() for l in r['observed'] if l['players']==1}),
        two_player_positions=sorted({l['number'] for r in records.values() for l in r['observed'] if l['players']==2}),
        records=list(records.values()),checks=checks,scope='Successful original loader returns, with both host frame matches separately recorded; rendered attract/demo maps are not counted.')
    save(OUT/'inventory.json',result)
    lines=['| Record | Map | Weather | Order:password | Observed scenario | Native / literal |','|---|---:|---:|---|---|---|']
    for r in records.values():
        lines.append('| '+r['record']+' | '+str(r['map'])+' | '+str(r['weather'])+' | '+
           '; '.join(str(o['players'])+'P '+str(o['number'])+':'+o['password'] for o in r['orders'])+' | '+
           ', '.join(l['scenario'] for l in r['observed'])+' | '+
           ', '.join(('PASS' if l['native'] else 'DIVERGED')+' / '+('PASS' if l['literal'] else 'DIVERGED') for l in r['observed'])+' |')
    (OUT/'LEVELS.md').write_text(str(result['covered_records'])+'/81 physical records initialized.\n\n'+'\n'.join(lines)+'\n',encoding='utf-8')
    save(OUT/'branch-counts.json',{p.stem:json.loads((CACHE/(p.stem+'.ref.json')).read_text())['inventory'] for p in sorted(SUITE.glob('*.txt'))})
    if GROUP!='openings':branch_report()
    print('Inventory',result['covered_records'],'/81',flush=True)

def snapshot():
    revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    target=OUT/('baseline-'+revision[:12]);target.mkdir(parents=True,exist_ok=True)
    pin=target/'.level-baseline.json'
    if not pin.exists():
        archive=subprocess.check_output(['git','archive','--format=tar',revision],cwd=ROOT)
        with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
            for member in tar.getmembers():
                if not member.isfile():continue
                p=(target/member.name).resolve();assert p.is_relative_to(target.resolve())
                data=tar.extractfile(member).read();current=ROOT/member.name
                if current.is_file() and current.read_bytes().replace(b'\r\n',b'\n')==data.replace(b'\r\n',b'\n'):data=current.read_bytes()
                p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
        save(pin,dict(revision=revision,purpose='Committed baseline plus optional level-suite files only.'))
    for p in suite_files():
        if not p.is_file():continue
        dest=target/p.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
    dest=target/CACHE.relative_to(ROOT);dest.mkdir(parents=True,exist_ok=True)
    for p in CACHE.glob('*.ref.json'):shutil.copyfile(p,dest/p.name)
    save(OUT/'baseline.json',dict(revision=revision,path=str(target.relative_to(ROOT)),overlay=hashes(suite_files())))
    return target

def all_runs():
    target=snapshot();bounded([sys.executable,'tools/build.py'],'build-original',cwd=target)
    names=[p.stem for p in sorted(SUITE.glob('*.txt'))]
    batch=8 if GROUP=="openings" else 1
    for start in range(0,len(names),batch):bounded([sys.executable,'verif/level_suite.py','--group',GROUP,'--reference',*names[start:start+batch],'--internal'],'references-'+str(start),cwd=target)
    inner=target/OUT.relative_to(ROOT)
    for label in ['native','literal']:
        bounded([sys.executable,'tools/hostbuild.py',*(['--literal'] if label=='literal' else [])],'build-'+label,cwd=target)
        rows=[]
        for start in range(0,len(names),8):
            group=names[start:start+8]
            result_path=inner/('check-'+label+'-'+group[0]+'.json');result_path.unlink(missing_ok=True)
            bounded([sys.executable,'verif/level_suite.py','--group',GROUP,'--check',label,*group,'--internal'],'check-'+label+'-'+str(start),cwd=target,ok=(0,1))
            rows.extend(json.loads(result_path.read_text())['scenarios'])
        save(inner/('check-'+label+'.json'),dict(result='PASS' if all(r['passed'] for r in rows) else 'DIVERGENCES',scenarios=rows))
    bounded([sys.executable,'verif/level_suite.py','--group',GROUP,'--inventory','--internal'],'inventory',cwd=target)
    CACHE.mkdir(parents=True,exist_ok=True)
    for p in (target/CACHE.relative_to(ROOT)).glob('*.ref.json'):shutil.copyfile(p,CACHE/p.name)
    for n in ['check-native.json','check-literal.json','inventory.json','LEVELS.md','branch-counts.json',*(['BRANCHES.md','audio-requests.json'] if GROUP!='openings' else [])]:shutil.copyfile(inner/n,OUT/n)
    save(OUT/'acceptance.json',dict(result='PASS' if all(json.loads((OUT/('check-'+v+'.json')).read_text())['result']=='PASS' for v in ['native','literal']) else 'DIVERGENCES',
         baseline=json.loads((OUT/'baseline.json').read_text()),cache_inputs=hashes(list(CACHE.glob('*.ref.json'))),scope='Both actual host binaries vs reconstructed-ASM references, serial 8-GiB/600-s children.'))
    if GROUP=='openings':bounded([sys.executable,__file__,'--controls','--internal'],'controls')
    return json.loads((OUT/'acceptance.json').read_text())['result']=='PASS'

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--generate',action='store_true');p.add_argument('--all',action='store_true')
    p.add_argument('--reference',nargs='+');p.add_argument('--refresh',action='store_true');p.add_argument('--check',nargs='+');p.add_argument('--inventory',action='store_true');p.add_argument('--controls',action='store_true')
    p.add_argument('--group',choices=['openings','audio','deep'],default='openings')
    p.add_argument('--internal',action='store_true',help=argparse.SUPPRESS)
    a=p.parse_args();set_group(a.group);OUT.mkdir(parents=True,exist_ok=True)
    if (a.reference or a.check or a.inventory or a.controls) and not a.internal:
        row=bounded([sys.executable,__file__,*sys.argv[1:],'--internal'],'child-'+('reference' if a.reference else 'check' if a.check else 'inventory' if a.inventory else 'controls'),ok=(0,1))
        raise SystemExit(row['returncode'])
    if a.generate:
        if GROUP!="openings":p.error("--generate regenerates only the 81 opening scripts")
        generate()
    if a.reference:reference(a.reference,a.refresh)
    if a.check and not check(a.check[0],a.check[1:]):raise SystemExit(1)
    if a.inventory:inventory()
    if a.controls:controls()
    if a.all and not all_runs():raise SystemExit(1)

if __name__=='__main__':main()
