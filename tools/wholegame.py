"""Deterministic frame regression against the rebuilt original; never boots DOS.

References contain hashes, never RAM/video dumps. Long runs have address-ranged
Unicorn hooks only. Normal C comparisons require no emulation on a cache hit.
"""
import argparse
import ctypes as C
import hashlib
import json
import struct
import sys
import time
import copy
import tempfile
import functools
import gc
from pathlib import Path

from common import ROOT, sha256
from difftest import load_dll, Regs
from emu import Machine, Devices, DeviceState, IoEvent, MEM_SIZE, REG_NAMES, LOAD, NativeVga
from unicorn import UC_HOOK_CODE

VERSION = 1
VGA_ACCELERATOR = None
OUT = ROOT/'build/whole'
FRAME = 'GAME:SwapAndDisplayVgaPage'
POLL = 'GAME:PollKeyboardScanChange'
RETRACE = 'GAME:WaitVerticalRetraceActive'
SCALARS = ('CurrentLevelIndex','LivesRemaining','ScoreLowWord','ScoreHighWord',
           'PlayerPixelX','PlayerYPixels','ActorPlatformOrScriptDone','ActorX32','ActorY32',
           'ActorSpriteIds','PlayerPlatformIndices','ScreenFadeLevel','PlayerCount','ScreenFadeStep',
           'PlayerImpactMagnitude','LevelTimer','WaterYPixels','PlayerCarriedKinds','RemainingPassengerJourneys')
KEYS = dict(esc=1,enter=0x1c,space=0x39,q=0x10,c=0x2e,f1=0x3b,f2=0x3c,
            f3=0x3d,f4=0x3e,f5=0x3f,up=0x48,down=0x50,left=0x4b,right=0x4d)


def scenario(path):
    """Header `name value`, then `frame: scan ...` (hex, or key/+key/-key)."""
    s=dict(name=path.stem,entry='GAME:RunDosGame',frames=32,card='none',events={},joy_events={},joy_cycles={},cycles={},requires=[],expects={})
    def scan_words(words):
        scans=[]
        for word in words:
            release=word.startswith('-'); word=word.lstrip('+-')
            if word in ('up','down','left','right'): scans.append(0xe0)
            scans.append((KEYS[word] if word in KEYS else int(word,16)) | (128 if release else 0))
        return scans
    for line in path.read_text().splitlines():
        line=line.split('#',1)[0].strip()
        if not line: continue
        if ':' in line and line.split(':',1)[0].isdigit():
            frame,values=line.split(':',1)
            scans=[]
            for word in values.split():
                if word.startswith('sticks='):
                    s['joy_cycles'][int(frame)]=[joystick_wave(*map(int,pair.split(','))) for pair in word[7:].split(';')]; continue
                if word.startswith('stick='):
                    x,y=map(int,word[6:].split(',')); s['joy_events'][int(frame)]=joystick_wave(x,y); continue
                if word.startswith('joy='):
                    s['joy_events'][int(frame)]=[int(x,16) for x in word[4:].split(',')]; continue
                if word.startswith('cycle='):
                    s['cycles'][int(frame)]=[] if word[6:]=='off' else scan_words(word[6:].split(',')); continue
                scans.extend(scan_words([word]))
            s['events'][int(frame)]=scans
        else:
            k,v=line.split(None,1)
            if k=='requires': s[k].extend(v.split()); continue
            if k=='expect':
                name,value=v.split(); s['expects'][name]=int(value,0); continue
            if k not in ('entry','frames','card','players','bios','score','password','end','joystick','timing','death','scores'):
                raise ValueError('unknown scenario directive: '+k)
            s[k]=int(v) if k in ('frames','players') else v
    if s['card'] not in ('none','adlib'): raise ValueError('card must be none/adlib')
    if s.get('timing','pit-quantum-at-polls')!='pit-quantum-at-polls': raise ValueError('unknown timing policy')
    if not 1<=s['frames']<=16384: raise ValueError('frame bound 1..16384 required')
    return s


def joystick_wave(x,y):
    """Discrete axis values become fixed raw gameport discharge waveforms."""
    if x not in (-1,0,1) or y not in (-1,0,1): raise ValueError('stick axes must be -1/0/1')
    a,b=(2 if x<0 else 28 if x>0 else 9),(2 if y<0 else 28 if y>0 else 10)
    return [0xf0,0xf0]+[0xf0|(1 if t<a else 0)|(2 if t<b else 0) for t in range(max(a,b)+4)]


def fixture(s):
    m=Machine()
    m.device.script(0x3da,[0,8],cycles=0xffffffff)
    joystick=[int(x,16) for x in s['joystick'].split()] if s.get('joystick') else [255]*10000
    m.device.script(0x201,joystick,cycles=0xffffffff)
    m.device.script(0xfffe,[0x10203040],cycles=0xffffffff)
    m.device.script(0x388,[0xe0] if s['card']=='none' else [0,0xc0]+[0]*64,cycles=0xffffffff)
    m.write(0,0x20,struct.pack('<HH',0x100,0xf000))
    # Real temporary calibration handlers, before any periodic timer is installed.
    for site in ('loc_1163','loc_116B'):
        m.device.schedule(m.seg('SOUND:'+site),m.off('SOUND:'+site),clocks=65536)
    if s['entry']!='GAME:RunDosGame':
        # Explicit cold integration fixture, never extracted from an oracle run.
        for n,v in [('PlayfieldHeight',192),('VgaPlaneCopyByteCount',0x4800),
                    ('DrawPagePointer',0x5a08),('DisplayedVgaPagePointer',0xa88),
                    ('BackgroundPagePointer',0xa988)]: m.ww('GAME:'+n,v)
        for n in ('DrawPagePointer','DisplayedVgaPagePointer','BackgroundPagePointer'):
            m.ww('GAME:'+n,0xa000,2)
        for n,v in [('PlayerCount',s.get('players',1)),('PlayerArrayBytes',2*s.get('players',1)),
                    ('PlayerOneControlMode',0xffff),('PlayerTwoControlMode',0xffff),
                    ('JoystickSampleLoopLimit',3),('WaterYPixels',200)]: m.ww('DGROUP:'+n,v)
        m.wb('DGROUP:JoystickEnabledAxisMask',0)
        seg,off=m.address('GAME:HandleKeyboardScanInterrupt')
        m.write(0,0x24,struct.pack('<HH',off,seg))
        # No sound initialization runs when entering a component directly.
        m.device.irq_count=0
    if s.get('bios'):
        m.device.script(0xffff,[int(x,16) for x in s['bios'].split()])
    if s.get('scores'):
        if s['scores']!='blank': raise ValueError('unknown high-score file fixture')
        rows=bytearray(m.read(m.seg('DGROUP:HighScoreRows'),m.off('DGROUP:HighScoreRows'),107))
        for row in range(5): rows[14+21*row:20+21*row]=b' '*6
        m.device.file('UGH!.HI',bytes(b^255 for b in rows))
    if s.get('score'):
        score=int(s['score']); m.ww('DGROUP:ScoreLowWord',score&65535); m.ww('DGROUP:ScoreHighWord',score>>16)
    if s.get('password'):
        password=s['password'].encode('ascii')
        if len(password)>20: raise ValueError('password capacity')
        m.write(m.seg('DGROUP:PasswordEditBuffer'),m.off('DGROUP:PasswordEditBuffer'),password.ljust(20,b' '))
    initial=m.prepare(s['entry'],flags=0x202,kind='exit' if s.get('end')=='exit' else 'near')
    if VGA_ACCELERATOR is not None: VGA_ACCELERATOR.attach(m)
    return m,initial


class Clock:
    """Input uses real IRQ1, never writes game variables. Frame is a page flip.

    Events become eligible at that frame and are delivered one scan per keyboard
    poll. Original and C visit the same polling entry, independent of instruction
    counts. Calibration remains the finite service-point fixture above.
    """
    def __init__(self,s,m):
        self.s=s; self.frame=0; self.pending=[]; self.loaded=-1; self.cycle=[]; self.cycle_cursor=0
        self.joy_cycle=[]; self.joy_start=0
        self.poll=m.address(POLL); self.retrace=m.address(RETRACE)
        self.timer_sites=[self.retrace,m.address('SOUND:loc_1EA3')]
        for label,delta in [('C:StopSoundChannel',0x53),('C:StopMusicTrack',0x95),('C:LoadIffSample',0x4e7)]:
            seg,off=m.address(label); self.timer_sites.append((seg,off+delta))
        self.timer_segment=m.seg('TIMER:HandleTimerInterrupt')

    def service(self,dev,segment,offset,flags,read):
        if not flags&512 or dev.irq_cursor<dev.irq_count: return
        if (segment,offset) in self.timer_sites and not dev.pic_mask&1:
            vector=read(0,0x20,4)
            if int.from_bytes(vector[2:],'little')==self.timer_segment:
                dev.irq_cursor=0; dev.irq_count=1
                e=dev.irqs[0]; e.segment=segment; e.offset=offset; e.skip=0; e.irq=0
                e.clocks=dev.pit_divisor or 65536
            return
        if (segment,offset)!=self.poll: return
        if self.loaded!=self.frame:
            for f in range(self.loaded+1,self.frame+1):
                self.pending.extend(self.s['events'].get(f,[]))
                if f in self.s.get('cycles',{}): self.cycle=list(self.s['cycles'][f]); self.cycle_cursor=0
                if f in self.s.get('joy_cycles',{}): self.joy_cycle=self.s['joy_cycles'][f]; self.joy_start=f
                waveform=self.s.get('joy_events',{}).get(f)
                if waveform is None and self.joy_cycle: waveform=self.joy_cycle[(f-self.joy_start)%len(self.joy_cycle)]
                if waveform is not None:
                    if not waveform or len(waveform)>128: raise ValueError('joystick waveform capacity')
                    script=next(dev.scripts[i] for i in range(dev.script_count) if dev.scripts[i].port==0x201)
                    script.count=len(waveform); script.cursor=script.used=0; script.cycles=script.cycles_left=0xffffffff
                    for i,b in enumerate(waveform): script.runs[i].value=b; script.runs[i].repeat=1
            self.loaded=self.frame
        if not self.pending and self.cycle:
            self.pending.append(self.cycle[self.cycle_cursor]); self.cycle_cursor=(self.cycle_cursor+1)%len(self.cycle)
        if not self.pending or not flags&512 or dev.pic_mask&2: return
        if dev.irq_cursor<dev.irq_count: return
        # The consumed queue is a platform fixture, so reuse its bounded storage.
        scan=self.pending.pop(0)
        script=next((dev.scripts[i] for i in range(dev.script_count) if dev.scripts[i].port==0x60),None)
        if script is None:
            script=dev.scripts[dev.script_count]; dev.script_count+=1; script.port=0x60
        script.count=1; script.cursor=script.used=0; script.cycles=script.cycles_left=1
        script.runs[0].value=scan; script.runs[0].repeat=1
        dev.irq_cursor=0; dev.irq_count=1
        e=dev.irqs[0]; e.segment=segment; e.offset=offset; e.skip=0; e.irq=1; e.clocks=0


def compared_ram(ram,sp):
    # Same contract as difftest: only dedicated stack scratch is unobservable.
    return ram[:0x80000]+ram[0x80000+sp:]


def record(ram,device,events,rolling,m,sp,live_sp):
    rolling.update(events)
    vals={n:int.from_bytes(ram[m.seg('DGROUP:'+n)*16+m.off('DGROUP:'+n):
                                m.seg('DGROUP:'+n)*16+m.off('DGROUP:'+n)+(1 if n in ('LivesRemaining','RemainingPassengerJourneys') else 2)],'little') for n in SCALARS}
    vals['return']=int.from_bytes(ram[0x80000+live_sp:0x80002+live_sp],'little')
    return dict(ram=sha256(compared_ram(ram,sp)),device=sha256(device),
                log=rolling.hexdigest(),scalars=vals)


def identity(path,m):
    # Translation changes must compare to the SAME reference. Only oracle-side
    # semantics, the script and the image invalidate the reference.
    import unicorn
    from cbuild import GCC
    return sha256(m.raw_image+path.read_bytes()+str(VERSION).encode()+unicorn.__version__.encode()+
                  (ROOT/'tools/emu.py').read_bytes()+(ROOT/'tools/wholegame.py').read_bytes()+
                  sha256(GCC.read_bytes()).encode())


@functools.lru_cache(maxsize=1)
def routines():
    import coverage
    return coverage.inventory()


def trace_state(name,regs,ram,device,events,sp,m):
    a=regs['SS']*16+regs['SP']; ret=int.from_bytes(ram[a:a+2],'little')
    cs=m.seg(name) if name.startswith('GAME:') else int.from_bytes(ram[a+2:a+4],'little')
    choices=[(row['offset'],row['module']+':'+row['name']) for row in routines()
             if LOAD+row['frame']==cs and row['offset']<=ret]
    caller=max(choices)[1] if choices and ret!=0xfff0 else 'harness/unknown'
    return dict(routine=name,caller=caller,registers={k:regs[k] for k in ('AX','BX','CX','DX','SI','DI','BP','DS','ES','SS','SP')},
                ram=sha256(compared_ram(ram,sp)),device=sha256(device),log=sha256(events))


def original(s,m,initial,progress=False,stop=None,trace=None,resume=None):
    clock=Clock(s,m); records=[]; rolling=hashlib.sha256(); snapshots={}; entries=set(); sites=set(); edges=set(); pending=[None]
    frame_address=m.seg(FRAME)*16+m.off(FRAME)+0x2a
    service_addresses=[seg*16+off for seg,off in (clock.poll,clock.retrace)]
    service_addresses=sorted(set(service_addresses+[seg*16+off for seg,off in clock.timer_sites]))
    m.ranged_hooks()
    skip_service=set()
    skip_boundary=[False]
    if resume:
        records=list(resume['records']); m.restore(resume['ram'])
        C.memmove(C.addressof(m.device.raw),resume['device'],len(resume['device']))
        m.uc.context_restore(resume['context']); rolling=resume['rolling'].copy()
        clock=copy.deepcopy(resume['clock']); skip_boundary[0]=True
    def service(uc,address,size,user):
        if address in skip_service:
            skip_service.remove(address); return
        clock.service(m.device,m.reg('CS'),m.reg('IP'),m.reg('FLAGS'),m.read)
        if m.device.service(m,m.reg('CS'),m.reg('IP')):
            skip_service.add(address)
            m.resume_irq=True; uc.emu_stop()
    for a in service_addresses:
        # _code from ranged_hooks handles existing events first. This scheduler
        # prepares a new input event only after that has been consumed.
        m.uc.hook_add(UC_HOOK_CODE,service,begin=a,end=a)
    def boundary(uc,address,size,user):
        if skip_boundary[0]: skip_boundary[0]=False; return
        if m.device.error: raise RuntimeError('native VGA rejected an unsupported access width')
        ram=m.snapshot(); device=m.device.state()
        raw=b''.join(struct.pack('<4I',*e) for e in m.device.log)
        records.append(record(ram,device,raw,rolling,m,initial['SP'],m.reg('SP')))
        m.device.log.clear(); clock.frame=len(records)
        if progress: print(f'  original frame {len(records)} {records[-1]["scalars"]}',flush=True)
        if len(records)%32==0 or len(records)==1:
            snapshots[len(records)]=dict(ram=ram,device=device,context=m.uc.context_save(),rolling=rolling.copy(),
                                         clock=copy.deepcopy(clock),records=list(records))
        if trace is not None and len(records)==(stop or s['frames']):
            trace['final_ram']=ram; trace['final_device']=device
        if len(records)>=(stop or s['frames']): uc.emu_stop()
    m.uc.hook_add(UC_HOOK_CODE,boundary,begin=frame_address,end=frame_address)
    # Presence is a set, not an execution count. Retire each address hook as
    # soon as its entry/edge evidence is complete. In particular, keeping hooks
    # on ICE's bit readers would turn a few decompressions into millions of
    # Python callbacks even though their addresses are individually ranged.
    ledger=json.loads((ROOT/'build/workers/c-close/call-edges.json').read_text())
    obligations={}
    for row in ledger:
        if not row['verified'] and row['site'] is not None:
            obligations.setdefault(row['site'],set()).add(row['target'])
    entry_hooks={}; edge_hooks={}
    inline={'GAME:DecodeIceLiteralAndMatchStream','GAME:ReadIceBitToCarry','GAME:ReadIceBitsToDx'}
    rows=list(routines()); census={row['module']+':'+row['name'] for row in rows}
    for name in set().union(*obligations.values())-census if obligations else ():
        if name in m.symbols:
            seg,off=m.address(name); module,label=name.split(':',1)
            rows.append(dict(module=module,name=label,frame=seg-LOAD,offset=off))
    for row in rows:
        a=(LOAD+row['frame'])*16+row['offset']
        def entry(uc,address,size,user):
            if user in census: entries.add(user)
            if pending[0] is not None:
                site=pending[0]; edges.add((site,user)); pending[0]=None
                if site in obligations:
                    obligations[site].discard(user)
                    if not obligations[site] and site in edge_hooks: uc.hook_del(edge_hooks.pop(site))
            needed=any(user in targets for targets in obligations.values())
            if not needed and (trace is None or user in inline) and user in entry_hooks:
                uc.hook_del(entry_hooks.pop(user))
            if trace is not None and user in census and user not in inline and len(records)==(stop or s['frames'])-1:
                if len(trace.setdefault('entries',[]))>=20000: raise RuntimeError('diagnostic trace exceeds 20000 entries')
                regs={k:m.reg(k) for k in REG_NAMES}
                trace['entries'].append(trace_state(user,regs,m.snapshot(),m.device.state(),
                    b''.join(struct.pack('<4I',*e) for e in m.device.log),initial['SP'],m))
        name=row['module']+':'+row['name']
        entry_hooks[name]=m.uc.hook_add(UC_HOOK_CODE,entry,user_data=name,begin=a,end=a)
    for site in obligations:
        a=LOAD*16+int(site,16)
        def edge(uc,address,size,user): sites.add(user); pending[0]=user
        edge_hooks[site]=m.uc.hook_add(UC_HOOK_CODE,edge,user_data=site,begin=a,end=a)
    started=time.perf_counter()
    # Each resume has an instruction AND a wall bound. IRQs are finite here.
    while len(records)<(stop or s['frames']):
        m.resume_irq=False
        m.uc.emu_start(m.reg('CS')*16+m.reg('IP'),0,count=100_000_000,timeout=60_000_000)
        if m.error: raise m.error
        if m.device.error: raise RuntimeError('native VGA rejected an unsupported access width')
        if not m.resume_irq: break
        if time.perf_counter()-started>300: raise RuntimeError('scenario reference exceeds 300s budget')
    terminal=s.get('end')
    if terminal and ((terminal=='return' and m.returned) or (terminal=='exit' and m.terminal_exit)):
        boundary(m.uc,0,0,None); records[-1]['terminal']=terminal
    elif len(records)!=(stop or s['frames']):
        raise RuntimeError(f'original stopped after {len(records)} frames at {m.reg("CS"):04X}:{m.reg("IP"):04X}')
    elif terminal and not stop:
        raise RuntimeError(f'original failed to reach required {terminal} within frame bound')
    return records,dict(routines=sorted(entries),sites=sorted(sites),edges=sorted(edges)),snapshots


def native(s,m,initial,dll,reference,trace=None):
    mem=dll.ugh_memory().contents; dev=dll.ugh_device_state().contents
    C.memmove(mem,m.snapshot(),MEM_SIZE); dll.ugh_devices_reset()
    state=m.device.state(); C.memmove(C.addressof(dev),state,len(state))
    rolling=hashlib.sha256(); clock=Clock(s,m); records=[]; failure={}; errors=[]
    FRAME_CB=C.CFUNCTYPE(C.c_int,C.POINTER(Regs))
    SERVICE_CB=C.CFUNCTYPE(C.c_int,C.c_uint16,C.c_uint16,C.POINTER(Regs))
    ENTRY_CB=C.CFUNCTYPE(None,C.c_uint16,C.c_uint16,C.POINTER(Regs))
    routine_names={(LOAD+row['frame'],row['offset']):row['module']+':'+row['name'] for row in routines()}
    def entry(seg,off,rp):
        if trace is None or len(records)!=s['frames']-1 or (seg,off) not in routine_names: return
        if len(trace.setdefault('entries',[]))>=20000: errors.append('diagnostic trace exceeds 20000 entries'); return
        regs={k:getattr(rp.contents,k.lower()) for k in REG_NAMES}
        raw=C.string_at(C.addressof(dev)+DeviceState.log.offset,dev.count*C.sizeof(IoEvent))
        trace['entries'].append(trace_state(routine_names[seg,off],regs,bytes(mem),
            C.string_at(C.addressof(dev),DeviceState.count.offset),raw,initial['SP'],m))
    def boundary(rp):
        try:
            ram=bytes(mem); device=C.string_at(C.addressof(dev),DeviceState.count.offset)
            raw=C.string_at(C.addressof(dev)+DeviceState.log.offset,dev.count*C.sizeof(IoEvent))
            got=record(ram,device,raw,rolling,m,initial['SP'],rp.contents.sp)
            if terminal_capture[0]: got['terminal']=s['end']
            records.append(got); dev.count=0
            clock.frame=len(records)
            if got!=reference[len(records)-1] or dev.error:
                failure.update(frame=len(records),expected=reference[len(records)-1],actual=got,
                               ram=ram,device=device)
                return 2
            return 2 if len(records)==s['frames'] else 0
        except Exception as e: errors.append(str(e)); return 2
    def service(seg,off,rp):
        try:
            clock.service(dev,seg,off,rp.contents.flags,lambda seg,off,n:bytes(mem[seg*16+off:seg*16+off+n]))
            return 0
        except Exception as e: errors.append(str(e)); return 2
    cb=FRAME_CB(boundary); scb=SERVICE_CB(service)
    dll.ugh_set_frame_observer.argtypes=[FRAME_CB]; dll.ugh_set_frame_observer(cb)
    dll.ugh_set_service_observer.argtypes=[SERVICE_CB]; dll.ugh_set_service_observer(scb)
    ecb=ENTRY_CB(entry); dll.ugh_set_entry_observer.argtypes=[ENTRY_CB]
    dll.ugh_set_entry_observer(ecb if trace is not None else ENTRY_CB())
    r=Regs(**{k.lower():v for k,v in initial.items()})
    terminal_capture=[False]
    fn=getattr(dll,'c_'+s['entry'].split(':')[1]); fn.argtypes=[C.POINTER(Regs)]
    try:
        status=fn(C.byref(r))
        if s.get('end') and not failure and status==(5 if s['end']=='exit' else 0):
            if s['end']=='return': r.sp=(r.sp+2)&65535; r.ip=0xfff0
            terminal_capture[0]=True; boundary(C.pointer(r))
    finally:
        dll.ugh_set_frame_observer(FRAME_CB()); dll.ugh_set_service_observer(SERVICE_CB()); dll.ugh_set_entry_observer(ENTRY_CB())
    if errors: raise RuntimeError('; '.join(errors))
    expected_status=(5 if s['end']=='exit' else 0) if s.get('end') else 2
    if not failure and (len(records)!=len(reference) or status!=expected_status or dev.error):
        raise RuntimeError(f'C stopped status={status}, error={dev.error}, frames={len(records)}')
    return failure


def decode_differences(a,b,m):
    names=sorted((seg*16+off,name) for name in m.symbols for seg,off in [m.address(name)]
                 if not name.split(':')[1].startswith(('loc_','ds_','ss_','cs_')))
    import bisect
    addresses=[x[0] for x in names]; result=[]
    for i,(x,y) in enumerate(zip(a,b)):
        if x==y or 0x80000<=i<0x8fefe: continue
        j=bisect.bisect_right(addresses,i)-1
        label=f'{names[j][1]}+{i-names[j][0]:X}' if j>=0 else f'IVT/BIOS+{i:X}'
        result.append(f'{label}: original={x:02X} C={y:02X} (linear {i:05X})')
        if len(result)==24: break
    return result


def diagnose(s,failure,reference,snapshots,scratch):
    target=failure['frame']; dm,di=fixture(s); original_trace={}; native_trace={}
    candidates=[n for n in snapshots if n<target]
    checkpoint=snapshots[max(candidates)] if candidates else None
    if checkpoint is None and target>32:
        # Cache hits have no live checkpoints. One diagnostic replay creates
        # them, then the narrowed frame is replayed from the nearest checkpoint.
        _,_,saved=original(s,dm,di,stop=target-1)
        checkpoint=saved[max(saved)] if saved else None
        dm,di=fixture(s)
    original(s,dm,di,stop=target,trace=original_trace,resume=checkpoint)
    failure['differences']=decode_differences(original_trace['final_ram'],failure.pop('ram'),dm)
    device=failure.pop('device'); expected_device=original_trace['final_device']
    if device!=expected_device:
        offsets=[i for i,(x,y) in enumerate(zip(expected_device,device)) if x!=y]
        fields=[(getattr(DeviceState,n).offset,n) for n,_ in DeviceState._fields_]
        import bisect
        for i in offsets[:8]:
            base,name=fields[bisect.bisect_right([x[0] for x in fields],i)-1]
            failure['differences'].append(f'device.{name}+{i-base:X}: original={expected_device[i]:02X} C={device[i]:02X}')
    trace_dll=load_dll(scratch/'trace.dll',trace_dir=scratch/'sources')
    try:
        nm,ni=fixture(s); short=dict(s,frames=target)
        native(short,nm,ni,trace_dll,reference,trace=native_trace)
    finally:
        import _ctypes
        _ctypes.FreeLibrary(trace_dll._handle)
    asm=original_trace.get('entries',[]); portable=native_trace.get('entries',[])
    for i in range(max(len(asm),len(portable))):
        left=asm[i] if i<len(asm) else None; right=portable[i] if i<len(portable) else None
        if left and right and left['registers']!=right['registers'] and 'first_register_difference' not in failure:
            failure['first_register_difference']=dict(index=i,original=left,portable=right)
        # ABI scratch may differ before any observable effect. Keep the first
        # argument difference separately; narrow the effect using state/logs and
        # entry order rather than blaming an unused compiler scratch register.
        if left is None or right is None or any(left[k]!=right[k] for k in ('routine','ram','device','log')):
            failure['first_entry_difference']=dict(index=i,original=left,portable=right,
                previous_original=[x['routine'] for x in asm[max(0,i-4):i]],
                previous_portable=[x['routine'] for x in portable[max(0,i-4):i]])
            break
    failure['checkpoint_frame']=len(checkpoint['records']) if checkpoint else 0
    failure['trace_entries']=dict(original=len(asm),portable=len(portable))
    return failure


def run(args,dll,scratch):
    passed=True; total=time.perf_counter(); receipts=[]; witnesses={}; routines={}
    paths=sorted((ROOT/'tests/scenarios').glob('*.txt'))
    if args.scenarios:
        missing=set(args.scenarios)-{p.stem for p in paths}
        if missing: raise ValueError('unknown scenarios: '+', '.join(sorted(missing)))
        paths=[x for x in paths if x.stem in args.scenarios]
    if not paths: raise ValueError('no scenarios selected')
    for path in paths:
        s=scenario(path); started=time.perf_counter(); mode='cached'; failure=None; snapshots={}
        try:
            m,initial=fixture(s); key=identity(path,m); cache=OUT/(s['name']+'.ref.json')
            data=json.loads(cache.read_text()) if cache.exists() else {}
            if args.refresh or data.get('key')!=key:
                mode='reference'; frames,cov,snapshots=original(s,m,initial,args.progress)
                data=dict(key=key,version=VERSION,frames=frames,coverage=cov)
                temp=cache.with_suffix('.tmp')
                try:
                    temp.write_text(json.dumps(data,separators=(',',':'))+'\n'); temp.replace(cache)
                finally: temp.unlink(missing_ok=True)
            missing=set(s['requires'])-set(data['coverage']['routines'])
            if missing: raise RuntimeError('scenario did not exercise required routines: '+', '.join(sorted(missing)))
            for name,value in s['expects'].items():
                actual=data['frames'][-1]['scalars'].get(name)
                if actual!=value: raise RuntimeError(f'scenario end expectation {name}={value}, original reached {actual}')
            if s.get('death'):
                starts=[r['scalars'] for i,r in enumerate(data['frames']) if r['scalars']['ScreenFadeStep']==65534
                        and (i==0 or data['frames'][i-1]['scalars']['ScreenFadeStep']!=65534)]
                def caused(v):
                    if s['death']=='crash': return v['PlayerImpactMagnitude']>=2300
                    if s['death']=='water': return v['LevelTimer']&0x8000 and v['PlayerImpactMagnitude']==0 and v['PlayerYPixels']+18==v['WaterYPixels']
                    if s['death']=='bird': return 0<v['LevelTimer']<32768 and v['PlayerImpactMagnitude']==0
                    raise ValueError('unknown death witness')
                if not any(caused(v) for v in starts): raise RuntimeError('original did not reach required death witness: '+s['death'])
            m,initial=fixture(s)
            failure=native(s,m,initial,dll,data['frames'])
            if failure:
                failure=diagnose(s,failure,data['frames'],snapshots,scratch)
                (OUT/(s['name']+'.divergence.json')).write_text(json.dumps(failure,indent=2)+'\n')
                raise RuntimeError(f'first divergence frame {failure["frame"]}: '+
                                   ('; '.join(failure['differences'][:3]) or 'ordered log/scalars'))
            (OUT/(s['name']+'.divergence.json')).unlink(missing_ok=True)
            elapsed=time.perf_counter()-started
            count=len(data['frames'])
            flips=sum('terminal' not in row for row in data['frames'])
            terminal=(' + '+s['end']) if s.get('end') else ''
            print(f'PASS {s["name"]}: {flips} frames{terminal} {elapsed:.3f}s {flips/elapsed:.1f} fps [{mode}]',flush=True)
            receipts.append(dict(scenario=s['name'],seconds=elapsed,frames=flips,boundaries=count,bound=s['frames'],mode=mode,key=key))
            for site,target in data['coverage']['edges']:
                witnesses.setdefault((site,target),[]).append(s['name'])
            for name in data['coverage']['routines']: routines.setdefault(name,[]).append(s['name'])
        except Exception as e:
            elapsed=time.perf_counter()-started; passed=False
            print(f'FAIL {s["name"]}: {elapsed:.3f}s {e}',flush=True)
            receipts.append(dict(scenario=s['name'],seconds=elapsed,error=str(e)))
        finally:
            snapshots.clear(); gc.collect()
    result=dict(passed=passed,seconds=time.perf_counter()-total,scenarios=receipts)
    (OUT/'last-run.json').write_text(json.dumps(result,indent=2)+'\n')
    ledger=json.loads((ROOT/'build/workers/c-close/call-edges.json').read_text())
    previous_unverified=sum(not row['verified'] for row in ledger); closed=0
    for row in ledger:
        ws=witnesses.get((row['site'],row['target']),[])
        if ws:
            if not row['verified']: closed+=1
            row['verified']=True; row['witnesses']+=['wholegame: '+n for n in ws]; row['reason']=''
    files=sorted((ROOT/'c').glob('*.[ch]'))+[ROOT/'tools/wholegame.py',ROOT/'tools/emu.py',
          ROOT/'tools/cbuild.py',ROOT/'build/link/plain/UGH.EXE',ROOT/'build/workers/c-close/call-edges.json']+paths
    evidence=dict(passed=passed,inputs={str(p.relative_to(ROOT)):sha256(p.read_bytes()) for p in files},
                  routines=routines,previous_unverified=previous_unverified,closed=closed,edges=ledger)
    (OUT/'call-edges.json').write_text(json.dumps(evidence,separators=(',',':'))+'\n')
    # Prune only this tool's obsolete scenario artifacts; selected subsets never
    # delete references belonging to other maintained scenarios.
    maintained={p.stem for p in (ROOT/'tests/scenarios').glob('*.txt')}
    for pattern in ('*.ref.json','*.divergence.json'):
        for old in OUT.glob(pattern):
            if old.name.split('.',1)[0] not in maintained: old.unlink()
    return 0 if passed else 1


def main():
    started=time.perf_counter()
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('scenarios',nargs='*'); p.add_argument('--refresh',action='store_true')
    p.add_argument('--progress',action='store_true',help='diagnostic frame progress')
    p.add_argument('--python-vga',action='store_true',help='diagnostic: use the slower Python hardware callbacks')
    args=p.parse_args(); OUT.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.whole-',dir=OUT) as temporary:
        global VGA_ACCELERATOR
        scratch=Path(temporary); dll=None
        try:
            dll=load_dll(scratch/'core.dll')
            if not args.python_vga: VGA_ACCELERATOR=NativeVga(scratch)
            status=run(args,dll,scratch)
        finally:
            import _ctypes
            if dll is not None: _ctypes.FreeLibrary(dll._handle)
            if VGA_ACCELERATOR is not None: VGA_ACCELERATOR.close(); VGA_ACCELERATOR=None
    receipt=OUT/'last-run.json'; result=json.loads(receipt.read_text())
    result['total_wall_seconds']=time.perf_counter()-started; result['artifact_bytes']=0
    other=sum(p.stat().st_size for p in OUT.iterdir() if p.is_file() and p!=receipt)
    for _ in range(3): result['artifact_bytes']=other+len((json.dumps(result,indent=2)+'\n').encode())
    receipt.write_bytes((json.dumps(result,indent=2)+'\n').encode())
    return status


if __name__=='__main__': raise SystemExit(main())
