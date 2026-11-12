"""Static fixtures for demo callbacks/interpreter, erase state and collision reads.

No setup executes the oracle. Real-script cases read only rebuilt data. Missing
IgnoreActorState and gameplay callback families are not replaced by test stubs.
"""
import struct
from difftest import Case
from emu import DATA_SEG

GENERAL=('AX','BX','CX','DX','SI','DI','BP')
ARITH=('CF','PF','AF','ZF','SF','OF')
OUT=GENERAL+ARITH+('IF','DF')
CASES=[]


def word(m,s,o,v):
    m.write(s,o&65535,struct.pack('<H',v&65535))


for sprite,level in ((0,0x1234),(0x7ffe,4),(0x8000,0),(0xffff,0xffff),
                     (0x7fff,0),(0x7fff,3),(0x7fff,4),(0x7fff,0x8000),
                     (0x7fff,0x8003),(0x7fff,0xffff)):
    for ds in (DATA_SEG,0x7500):
        def setup(m,sprite=sprite,level=level,ds=ds):
            word(m,ds,m.off('DGROUP:ActorSpriteIds')+30,sprite)
            word(m,ds,m.off('DGROUP:ScreenFadeLevel'),level)
            word(m,ds,m.off('DGROUP:ScreenFadeStep'),0x1357)
        def check(m,r,sprite=sprite,level=level,ds=ds):
            def rd(name): return int.from_bytes(m.read(ds,m.off('DGROUP:'+name),2),'little')
            assert rd('ScreenFadeLevel')==((level-4)&65535 if sprite==0x7fff else level)
            assert rd('ScreenFadeStep')==(0xfffc if sprite==0x7fff else 0x1357)
        CASES.append(Case(f'fade sprite={sprite:04X} level={level:04X} DS={ds:04X}',
                    'GAME:StartDemoFadeWhenSpriteHidden',setup=setup,check=check,
                    regs=dict(DS=ds,BX=30),out_regs=OUT,flags=0x602))


def width_case(x,reverse=False,destination='built',ds=DATA_SEG):
    x&=65535
    def setup(m):
        word(m,ds,m.off('DGROUP:ActorX32')+2,x)
        if destination!='built':
            dest=m.off('DGROUP:ActorX32')+2 if destination=='alias' else 0xffff
            seg=ds if destination=='alias' else 0x9000
            m.ww('GAME:DemoRevealWidthPointer',dest)
            m.ww('GAME:DemoRevealWidthPointer',seg,2)
    def check(m,r):
        signed=x if x<32768 else x-65536
        width=320-(signed//32)
        expected=(min(width,127))&255
        seg=m.rw('GAME:DemoRevealWidthPointer',2)
        off=m.rw('GAME:DemoRevealWidthPointer')
        assert m.read(seg,off,1)==bytes((expected,))
        assert r['CX']==((signed//32)&65535)
        assert r['DI']==((off+(-1 if reverse else 1))&65535)
        full=(320-(signed//32))&65535
        assert r['AX']==((full&0xff00)|127 if width>127 else full)
    return Case(f'width X={x:04X} DF={reverse} dest={destination} DS={ds:04X}',
                'GAME:SetDemoRevealSpriteWidth',setup=setup,check=check,
                regs=dict(DS=ds,BX=2),out_regs=OUT,flags=0x602 if reverse else 0x202)


CASES += [width_case(x) for x in (-32768,-32767,-33,-32,-31,-1,0,1,6144,6175,
                                6176,6207,6208,10239,10240,10272,32767)]
CASES += [width_case(32767,True,'scratch',0x7500),width_case(-32768,False,'scratch'),
          width_case(10272,False,'alias'),width_case(6176,True,'alias')]

for flags in (0x202,0x602,0xad7):
    CASES.append(Case(f'unexplained RET flags={flags:04X}','GAME:loc_0B4E',
                     flags=flags,flag_inputs=ARITH,out_regs=OUT))


for ds,seed in ((DATA_SEG,None),(DATA_SEG,0x39),(0x7500,0xa7)):
    arrays=(('EnemySpriteIds',5),('EnemyEraseSprite',5),('ActorSpriteIds',16),
            ('ActorEraseSprite',16),('FallingItemSprites',12),('FallingItemEraseSprite',12))
    def setup(m,ds=ds,seed=seed):
        if seed is not None:
            # Poison the entire segment, including all adjacent cache arrays.
            m.write(ds,0,bytes((i*37+(i>>8)+seed)&255 for i in range(65536)))
    def check(m,r,ds=ds):
        for name,n in arrays:
            assert m.read(ds,m.off('DGROUP:'+name),2*n)==b'\xff\xff'*n
        assert r['AX']==65535 and r['SI']==65534
    CASES.append(Case(f'reset sprite caches DS={ds:04X} seed={seed}',
                     'GAME:ResetSpriteEraseState',setup=setup,check=check,
                     regs=dict(DS=ds),out_regs=OUT,flags=0x602))


SAMPLES=(0,3,5,0x720,0x723,0x725,0x240,0x245,0x480,0x485)


def sample_case(hot,value,vga=False,plane=0,wrap=False,alias=False):
    es=0x9fff if alias else (0xa000 if vga else 0x7500)
    si=0x10 if alias else (0xfffe if wrap else 0x100)
    def setup(m):
        if vga:
            m.device.read_map=plane
            # Make every plane's final latch distinct, including zero results.
            for p in range(4):
                for i,delta in enumerate(SAMPLES):
                    off=(si+delta+(es-0xa000)*16)&65535
                    m.device.planes[p*65536+off]=(value if i==hot else 0) if p==plane else (p*37+i+1)
        else:
            for i,delta in enumerate(SAMPLES):
                m.write(es,(si+delta)&65535,bytes((value if i==hot else 0,)))
    def check(m,r):
        assert r['AX']==0xab00+(value if hot is not None else 0)
        assert bool(r['FLAGS']&0x80)==bool(value&0x80) if hot is not None else not(r['FLAGS']&0x80)
    return Case(f'collision hot={hot} value={value:02X} VGA={vga} plane={plane} wrap={wrap} alias={alias}',
                'GAME:SamplePlayerCollisionPixels',setup=setup,check=check,
                regs=dict(ES=es,SI=si,AX=0xab34),out_regs=GENERAL+('CF','PF','ZF','SF','OF','IF','DF'),
                flags=0x602)


CASES += [sample_case(None,0),sample_case(None,0,True,3)]
CASES += [sample_case(i,1<<(i%8),True,i%4) for i in range(10)]
CASES += [sample_case(9,0xff,False,wrap=True),sample_case(0,0x80,True,2,alias=True)]
CASES += [sample_case(7,0x80,True,1,wrap=True)]


def script_case(title,records,repeat=0,restart=None,ticks=1,period=2,x=0x7fff,y=0xffff,
                callback='loc_0B4E',reverse=False,cursor=None,expected=None):
    """Records are data bytes; callback addresses always come from live symbols."""
    ds=DATA_SEG
    def setup(m):
        base=cursor(m) if cursor else 0x4000
        if reverse:
            m.write(ds,base,records[:2])
            m.write(ds,(base-2)&65535,records[2:3])
            m.write(ds,(base-3)&65535,records[3:4])
        else:
            for i,b in enumerate(records): m.write(ds,(base+i)&65535,bytes((b,)))
        for name,v in (('ActorUpdateOrScriptCursor',base),('ActorAnimationCountdowns',ticks),
                       ('ds_2C6D',period),('ds_2ACD',repeat),('ds_2A2D',0x4100 if restart else base),
                       ('ActorX32',x),('ActorY32',y),('ActorPlatformOrScriptDone',0x1357)):
            # A stream may alias X itself: leave the record's first word intact.
            if not(cursor and name=='ActorX32'): m.ww('DGROUP:'+name,v)
        m.ww('DGROUP:ActorUpdateOrScriptCursor',0xffff,2)
        m.ww('DGROUP:ActorOverlayOrScriptCallbacks',m.off('GAME:'+callback))
        m.ww('DGROUP:ScreenFadeLevel',2)
        if restart: m.write(ds,0x4100,restart)
    def check(m,r):
        assert r['BX']==2 and r['SI']==65535
        assert m.rw('DGROUP:ActorAnimationCountdowns')==((ticks-1)&65535 if ticks!=1 else period)
        if expected:
            for name,value in expected.items(): assert m.rw('DGROUP:'+name)==value,(name,m.rw('DGROUP:'+name),value)
    return Case(title,'GAME:AdvanceDemoScripts',setup=setup,check=check,
                regs=dict(DS=ds),out_regs=OUT,flags=0x602 if reverse else 0x202)


def record(sprite,dx,dy): return struct.pack('<HBB',sprite,dx&255,dy&255)
def words(*values): return struct.pack('<'+'H'*len(values),*values)


def empty_setup(m): m.ww('DGROUP:ActorUpdateOrScriptCursor',65535)
CASES.append(Case('empty demo cursor vector','GAME:AdvanceDemoScripts',setup=empty_setup,
                  regs=dict(DS=DATA_SEG),out_regs=OUT))
for ticks in (0,2,0x8000,0xffff):
    CASES.append(script_case(f'countdown only {ticks:04X}',b'',ticks=ticks))
CASES.append(script_case('untranslated callback is not reached on skipped tick',b'',
                         ticks=2,callback='IgnoreActorState'))

for dx,dy in ((-128,127),(-1,-128),(0,0),(1,-1),(127,1)):
    CASES.append(script_case(f'signed deltas {dx},{dy}',record(0x1234,dx,dy),
                   expected={'ActorSpriteIds':0x1234,'ActorX32':(0x7fff+4*dx)&65535,
                             'ActorY32':(0xffff+4*dy)&65535,'ActorUpdateOrScriptCursor':0x4004}))
CASES += [script_case('zero period reload',record(0,0,0),period=0),
          script_case('LODS source wraps through FFFF',record(0x1234,-1,1),
                      cursor=lambda m:0xfffc,expected={'ActorUpdateOrScriptCursor':0}),
          script_case('reverse LODS direction',record(0x7fff,-128,127),reverse=True,
                      callback='StartDemoFadeWhenSpriteHidden',
                      expected={'ActorUpdateOrScriptCursor':0x3ffc,'ScreenFadeLevel':0xfffe}),
          script_case('cursor aliases X word',record(0x1234,5,-3),
                      cursor=lambda m:m.off('DGROUP:ActorX32'),
                      callback='SetDemoRevealSpriteWidth',
                      expected={'ActorX32':0x1248}),
          script_case('install negative count',words(0xfffe)+record(7,1,2),
                      expected={'ds_2ACD':0xfffe,'ds_2A2D':0x4002,'ActorUpdateOrScriptCursor':0x4006}),
          script_case('successive negative counts',words(0x8001,0xffff)+record(7,1,2),
                      expected={'ds_2ACD':0xffff,'ds_2A2D':0x4004}),
          script_case('stop marker pins cursor',words(0x8000),
                      expected={'ActorUpdateOrScriptCursor':0x4000,'ActorPlatformOrScriptDone':0xffff}),
          script_case('repeat expires into next record',words(0x8000)+record(8,2,3),repeat=0xffff,
                      expected={'ds_2ACD':0,'ActorUpdateOrScriptCursor':0x4006})]
for repeat in (0xfffe,1,0x7fff,0x8000):
    CASES.append(script_case(f'repeat follows saved pointer {repeat:04X}',words(0x8000),
                 repeat=repeat,restart=record(0x7fff,0,0),callback='StartDemoFadeWhenSpriteHidden',
                 expected={'ds_2ACD':(repeat+1)&65535,'ActorUpdateOrScriptCursor':0x4104,'ScreenFadeLevel':0xfffe}))


def real_case(name,selector,repeat=0):
    def setup(m):
        base=m.off('DGROUP:'+name)
        p=base+8
        candidates={'start':p,'sprite':None,'hidden':None,'marker':None}
        # Parse static records only; this does not execute or unroll the game.
        end=m.off('DGROUP:Data_1E02') if name=='Data_1CBC' else m.off('DGROUP:Data_2586')
        while p<end:
            token=int.from_bytes(m.read(DATA_SEG,p,2),'little')
            if token<0x8000 and candidates['sprite'] is None: candidates['sprite']=p
            if token==0x7fff and candidates['hidden'] is None: candidates['hidden']=p
            if token==0x8000 and candidates['marker'] is None: candidates['marker']=p
            p+=4 if token<0x8000 else 2
        for key in ('sprite','marker',selector): assert candidates[key] is not None
        for target,delta in (('ActorX32',0),('ActorY32',2)):
            m.ww('DGROUP:'+target,(int.from_bytes(m.read(DATA_SEG,base+delta,2),'little')<<5)&65535)
        m.ww('DGROUP:ActorUpdateOrScriptCursor',candidates[selector])
        m.ww('DGROUP:ActorUpdateOrScriptCursor',65535,2)
        m.ww('DGROUP:ActorAnimationCountdowns',1)
        m.ww('DGROUP:ds_2C6D',int.from_bytes(m.read(DATA_SEG,base+4,2),'little'))
        m.ww('DGROUP:ActorOverlayOrScriptCallbacks',int.from_bytes(m.read(DATA_SEG,base+6,2),'little'))
        m.ww('DGROUP:ds_2ACD',repeat)
        m.ww('DGROUP:ds_2A2D',candidates['sprite'])
    return Case(f'rebuilt {name} {selector} repeat={repeat:04X}', 'GAME:AdvanceDemoScripts',
                setup=setup,regs=dict(DS=DATA_SEG),out_regs=OUT)


for name in ('Data_1CBC','Data_24E4'):
    CASES += [real_case(name,'start'),real_case(name,'hidden' if name=='Data_1CBC' else 'sprite'),real_case(name,'marker'),
              real_case(name,'marker',0xfffe),real_case(name,'marker',0xffff)]


def many_setup(m):
    for i in range(16):
        p=0x4000+i*4
        m.write(DATA_SEG,p,record(0x7fff if i%2 else 5,-i,i))
        for name,value in (('ActorUpdateOrScriptCursor',p),('ActorAnimationCountdowns',1 if i%3 else 2),
                           ('ds_2C6D',i),('ActorX32',i*0x1111),('ActorY32',0xffff-i),
                           ('ActorOverlayOrScriptCallbacks',m.off('GAME:StartDemoFadeWhenSpriteHidden'))):
            m.ww('DGROUP:'+name,value,i*2)
    m.ww('DGROUP:ActorUpdateOrScriptCursor',65535,32)
CASES.append(Case('sixteen mixed due/skipped scripts','GAME:AdvanceDemoScripts',setup=many_setup,
                  regs=dict(DS=DATA_SEG),out_regs=OUT))


def alternate_setup(m):
    ds=0x7500
    m.write(ds,0x4000,words(0xfffe)+record(0x7fff,-128,127))
    for name,value in (('ActorUpdateOrScriptCursor',0x4000),('ActorAnimationCountdowns',1),
                       ('ds_2C6D',0),('ActorX32',0x8000),('ActorY32',0xfffe),
                       ('ActorOverlayOrScriptCallbacks',m.off('GAME:SetDemoRevealSpriteWidth'))):
        word(m,ds,m.off('DGROUP:'+name),value)
    word(m,ds,m.off('DGROUP:ActorUpdateOrScriptCursor')+2,65535)
CASES.append(Case('interpreter uses dynamic DS','GAME:AdvanceDemoScripts',setup=alternate_setup,
                  regs=dict(DS=0x7500),out_regs=OUT))


# Shared-service integration cases.

for callbacks in ([],['IgnoreActorState'],['BeginStonePickupWait','IgnoreActorState']):
    def setup(m,callbacks=callbacks):
        for i,callback in enumerate(callbacks):
            m.ww('DGROUP:ActorDescriptors',m.off('DGROUP:Data_78DC'),2*i)
            m.ww('DGROUP:ActorUpdateOrScriptCursor',m.off('GAME:'+callback),2*i)
        m.ww('DGROUP:ActorDescriptors',0xffff,2*len(callbacks))
    CASES.append(Case('actor dispatcher '+str(callbacks),'GAME:DispatchActorUpdates',setup=setup,
        regs=dict(DS=DATA_SEG),out_regs=OUT))
# Untouched real header callback and real first records; setup never runs code.
for script in ('Data_1040','Data_1E02','Data_2586'):
    def setup(m,script=script):
        base=m.off('DGROUP:'+script)
        assert m.rw('DGROUP:'+script,6)==m.off('GAME:IgnoreActorState')
        for name,value in (('ActorUpdateOrScriptCursor',base+8),('ActorOverlayOrScriptCallbacks',m.rw('DGROUP:'+script,6)),
                           ('ActorAnimationCountdowns',1),('ActorAnimationByteOffsets',m.rw('DGROUP:'+script,4)),
                           ('ActorX32',m.rw('DGROUP:'+script)*32),('ActorY32',m.rw('DGROUP:'+script,2)*32),
                           ('ds_2ACD',0),('ds_2A2D',base+8)):
            m.ww('DGROUP:'+name,value)
        m.ww('DGROUP:ActorUpdateOrScriptCursor',65535,2)
    CASES.append(Case('integrated real script '+script,'GAME:AdvanceDemoScripts',setup=setup,
        regs=dict(DS=DATA_SEG),out_regs=OUT))

# Compose every already translated actor-table target with a returning original
# descriptor fixture from its own suite. Leading Ignore entries preserve the
# tested slot index (6); the sentinel follows it. No callback/table is stubbed.
from difftest import load_suite
from dataclasses import replace
actor_targets=('WaitForPassengerPlatform','PlacePassengerOnPlatform','AnimatePassengerArrival',
    'BeginPassengerPlatformWait','BeginPassengerDestinationDisplay','BeginPassengerQuestionDisplay',
    'BeginPassengerApproach','BoardPassenger','UpdateCarriedPassenger','WalkPassengerToExit',
    'BeginPassengerDeparture','AnimatePassengerDeparture','IgnoreActorState','BeginPassengerResurfacing',
    'UpdatePassengerResurfacing','BeginPassengerSinking','UpdatePassengerSinking','BeginPassengerFloating',
    'UpdatePassengerFloating','UpdateFloatingDestinationDisplay','UpdateFloatingQuestionDisplay',
    'UpdateFloatingPassengerApproach','IgnoreWaterbornePassengerState','BeginStonePickupWait',
    'AttachStoneToPlayer','WaitForStoneRelease','UpdateThrownStone')
actor_cases=load_suite('game_03_w00').CASES
for target in actor_targets:
    entry=next(c for c in actor_cases if c.routine=='GAME:'+target)
    def setup(m,entry=entry,target=target):
        entry.setup(m)
        for i in (0,2,4):
            m.ww('DGROUP:ActorDescriptors',m.off('DGROUP:Data_7720'),i)
            m.ww('DGROUP:ActorUpdateOrScriptCursor',m.off('GAME:IgnoreActorState'),i)
        m.ww('DGROUP:ActorUpdateOrScriptCursor',m.off('GAME:'+target),6)
        m.ww('DGROUP:ActorDescriptors',0xffff,8)
    CASES.append(replace(entry,routine='GAME:DispatchActorUpdates',title='actor dispatch native '+target,
        setup=setup,check=None,out_regs=OUT))
