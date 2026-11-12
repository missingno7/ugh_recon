"""Tree/item state and four-plane water tails, using only static fixtures.

The tail entries need a saved DS before the normal near return. The one-shot
prepare wrapper constructs that original frame; it changes no execution or
comparison hooks and supplies the same incoming SP/words to both implementations.
"""
from difftest import Case
from emu import DATA_SEG, STACK_SEG

GENERAL=('AX','BX','CX','DX','SI','DI','BP')
ARITH=('CF','PF','ZF','SF','OF')
ALL=GENERAL+ARITH+('DF','IF')
CASES=[]


def tree_case(count,end,slot=0,bank=DATA_SEG):
    def setup(m):
        desc=m.off('DGROUP:Data_76E4')
        if bank!=DATA_SEG:
            m.write(bank,desc,m.read(DATA_SEG,desc,60))
        def put(name,value,delta=0):
            m.write(bank,(m.off('DGROUP:'+name)+delta)&65535,(value&65535).to_bytes(2,'little'))
        put('EnemyDescriptors',desc,slot)
        put('EnemyStateCounters',count,slot)
        put('EnemyAnimationOrDropLists',0x6000,slot)
        put('EnemyStateCallbacks',0xA55A,slot)
        m.write(bank,0x6000,end.to_bytes(2,'little'))
    def check(m,r):
        o=(m.off('DGROUP:EnemyStateCounters')+slot)&65535
        assert int.from_bytes(m.read(bank,o,2),'little')==(count-1)&65535
        target=int.from_bytes(m.read(bank,m.off('DGROUP:EnemyStateCallbacks')+slot,2),'little')
        expected=(m.off('GAME:IgnoreExhaustedTree') if end==65535 else m.off('GAME:UpdateFruitTreeAnimation')) if count==1 else 0xA55A
        assert target==expected
    return Case(f'tree count={count:04x} list={end:04x} slot={slot} DS={bank:04x}',
                'GAME:AdvanceTreeRewardCooldown',setup=setup,regs=dict(DS=bank,BX=slot),
                out_regs=ALL+('AF',),check=check,flags=0x603,flag_inputs=('CF',))


for count,end,slot in ((0,65535,0),(1,65535,22),(1,0,2),(2,65535,4),(0x8000,0,6),(0xFFFF,0,8)):
    CASES.append(tree_case(count,end,slot))
CASES.append(tree_case(1,0x8000,2,0x7400))
clear_carry_tree=tree_case(2,0,10)
clear_carry_tree.title+=' CF clear'
clear_carry_tree.flags=0x602
CASES.append(clear_carry_tree)
CASES.append(Case('exhausted tree preserves all state','GAME:IgnoreExhaustedTree',out_regs=ALL+('AF',),flags=0x603,flag_inputs=('CF',)))
CASES.append(Case('exhausted tree preserves clear carry','GAME:IgnoreExhaustedTree',out_regs=ALL+('AF',),flags=0x202,flag_inputs=('CF',)))


def spawn_case(free=22,sprite=65535,x=0x1234,y=0x5678,dx=9,desc='Data_7970',geometry=None):
    def setup(m):
        for i in range(0,24,2): m.ww('DGROUP:FallingItemSprites',0x100+i,i)
        if free is not None: m.ww('DGROUP:FallingItemSprites',sprite,free)
        if geometry:
            for delta,value in geometry: m.ww('DGROUP:'+desc,value,delta)
    def regs(m):
        return dict(DS=DATA_SEG,SI=m.off('DGROUP:'+desc),AX=x,BP=y,CX=0xFFED,DX=dx,
                    BX=m.off('GAME:IgnoreExhaustedTree') if free is None else 0xBEEF)
    def check(m,r):
        if free is None:
            assert r['BX']==0xFFFE
            return
        width=m.rw('DGROUP:'+desc); height=m.rw('DGROUP:'+desc,2)
        assert m.rw('DGROUP:FallingItemX',free)==(x-(width<<5))&65535
        assert m.rw('DGROUP:FallingItemY',free)==(y-(height<<4))&65535
        assert m.rw('DGROUP:FallingItemVerticalStep',free)==(-(dx+m.rw('DGROUP:'+desc,12)))&65535
    return Case(f'spawn free={free}, sprite={sprite:04x}, desc={desc}, geom={geometry}',
                'GAME:SpawnFallingItem',setup=setup,regs=regs,out_regs=ALL+('AF',),check=check)


CASES += [spawn_case(),spawn_case(0,0x8000),spawn_case(10,0xFFFE),
          spawn_case(2,x=0,y=0,dx=0xFFF2),spawn_case(20,dx=0x7FF2),
          spawn_case(6,geometry=((0,0xFFFF),(2,0x8001),(12,0xFFFF))),spawn_case(None)]
for desc in ('Data_7984','Data_7998','Data_79AC','Data_79C0','Data_79D4','Data_79E8','Data_79FC','Data_7A10','FallingDescriptor_7A24','FallingDescriptor_7A38'):
    CASES.append(spawn_case(12,desc=desc))


def spawn_alias_setup(m):
    for i in range(0,24,2): m.ww('DGROUP:FallingItemSprites',0x100+i,i)
    m.ww('DGROUP:FallingItemSprites',0x8000)
    # Descriptor overlaps its output pointer cell: the first store changes the
    # width BEFORE it is read. Other descriptor words are static fixture values.
    for delta,value in ((0,7),(2,16),(6,m.off('GAME:AdvanceFallingItem')),(12,4),(16,0x120)):
        m.ww('DGROUP:FallingItemDescriptors',value,delta)


def spawn_alias_check(m,r):
    assert m.rw('DGROUP:FallingItemX')==(100-(m.off('DGROUP:FallingItemDescriptors')<<5))&65535
    assert m.rw('DGROUP:FallingItemY')==(200-(16<<4))&65535


CASES.append(Case('spawn descriptor aliases its output pointer','GAME:SpawnFallingItem',
                  setup=spawn_alias_setup,regs=lambda m:dict(DS=DATA_SEG,SI=m.off('DGROUP:FallingItemDescriptors'),AX=100,BP=200,CX=1,DX=2),
                  out_regs=ALL+('AF',),check=spawn_alias_check))


multiple_free=spawn_case(10,0x8000)
multiple_setup=multiple_free.setup
def setup_multiple_free(m):
    multiple_setup(m)
    m.ww('DGROUP:FallingItemSprites',0xFFFF,0)
multiple_free.setup=setup_multiple_free
multiple_free.title='spawn chooses higher of two negative slots'
CASES.append(multiple_free)


for slot,bank in ((0,DATA_SEG),(22,DATA_SEG),(4,0x7400)):
    def setup(m,slot=slot,bank=bank):
        desc=m.off('DGROUP:Data_7970')
        m.write(bank,desc,m.read(DATA_SEG,desc,20))
        m.write(bank,m.off('DGROUP:FallingItemDescriptors')+slot,desc.to_bytes(2,'little'))
        m.write(bank,m.off('DGROUP:FallingItemMotionOrLifetime')+slot,b'\xff\xff')
    def check(m,r,slot=slot,bank=bank):
        assert int.from_bytes(m.read(bank,m.off('DGROUP:FallingItemMotionOrLifetime')+slot,2),'little')==560
    CASES.append(Case(f'land slot={slot} DS={bank:04x}','GAME:LandFallingItem',setup=setup,
                      regs=dict(DS=bank,BX=slot),out_regs=ALL+('AF',),check=check,flags=0x603,flag_inputs=('CF',)))


def flight_case(title,x=1000,y=1000,hstep=0,vstep=-4,platforms=(),slot=0,width=8,height=16,bank=DATA_SEG):
    def setup(m):
        desc=m.off('DGROUP:Data_7970')
        m.write(bank,desc,m.read(DATA_SEG,desc,20))
        def put(name,value,delta=0):
            m.write(bank,(m.off('DGROUP:'+name)+delta)&65535,(value&65535).to_bytes(2,'little'))
        put('Data_7970',width); put('Data_7970',height,2)
        for name,value in (('FallingItemDescriptors',desc),('FallingItemX',x),('FallingItemY',y),
                           ('FallingItemMotionOrLifetime',hstep),('FallingItemVerticalStep',vstep),
                           ('FallingItemSprites',0x117),('FallingItemCallbacks',m.off('GAME:AdvanceFallingItem'))):
            put(name,value,slot)
        for i,(left,right,py) in enumerate(platforms):
            put('PlatformLeftEdges',left,2*i); put('PlatformRightEdges',right,2*i); put('PlatformHeights',py,2*i)
        put('PlatformLeftEdges',0x8000,len(platforms)*2)
    return Case(title,'GAME:AdvanceFallingItem',setup=setup,regs=dict(DS=bank,BX=slot),
                out_regs=GENERAL+('CF','PF','ZF','SF','DF','IF'),flags=0x602)


# X boundaries, unsigned wrap into signed space, ascending bypass, gravity wrap,
# signed Y cutoff, and negative Y converted with SAR rather than unsigned shift.
for x in (-513,-512,-511,0x27FF,0x2800,0x2801,0x7FFF,0x8000):
    CASES.append(flight_case(f'flight X boundary {x}',x=x))
CASES += [flight_case('X addition wraps',x=0x7FFF,hstep=0x8001),
          flight_case('upward Y wraps',y=0,vstep=-4),
          flight_case('rising bypasses bottom cutoff',y=0x2000,vstep=-4),
          flight_case('gravity wraps to negative',vstep=0x7FFF),
          flight_case('gravity wraps to zero',vstep=-3),
          flight_case('Y just below cutoff',y=0x17FC,vstep=0),
          flight_case('Y cutoff equal',y=0x17FD,vstep=0),
          flight_case('Y cutoff above',y=0x17FE,vstep=0),
          flight_case('Y signed wrap',y=0x7FFF,vstep=0),
          flight_case('negative Y SAR',y=0xFFDF,vstep=0),
          flight_case('alternate DS and slot',slot=22,bank=0x7400)]
# Bottom crosses from 47 to 48, center=39; exact inequalities on all four sides.
for title,platform in (
    ('old bottom equality rejects',(0,100,47)),
    ('new bottom not yet at platform',(0,100,49)),
    ('new bottom equality lands',(0,100,48)),
    ('left equality lands',(39,100,48)),
    ('left miss',(40,100,48)),
    ('right equality lands',(0,38,48)),
    ('right miss',(0,37,48))):
    CASES.append(flight_case(title,x=1000,y=1023,vstep=0,platforms=(platform,)))
CASES.append(flight_case('skip four rejects then land',x=1000,y=1023,vstep=0,slot=22,
                         platforms=((0,100,47),(0,100,49),(40,100,48),(0,37,48),(39,38,48))))
CASES.append(flight_case('negative platform height and geometry wrap',x=0,y=0xFFE0,vstep=32,
                         width=0xFFFF,height=0xFFFF,platforms=((0,100,0xFFFF),)))


for bank in (DATA_SEG,0x7400):
    def setup(m,bank=bank):
        for name,value in (('LivesRemaining',0xA5),('ScoreMultiplier',0xBEEF),('ScoreLowWord',0xFFFF),('ScoreHighWord',0x1234)):
            m.write(bank,m.off('DGROUP:'+name),value.to_bytes(2,'little'))
    def check(m,r,bank=bank):
        assert m.read(bank,m.off('DGROUP:ScoreMultiplier'),2)==b'\x01\xbe'
        assert m.read(bank,m.off('DGROUP:ScoreLowWord'),4)==bytes(4)
    CASES.append(Case(f'reset DS={bank:04x}','GAME:ResetScoreLivesAndMultiplier',setup=setup,
                      regs=dict(DS=bank),out_regs=ALL,check=check))


def water_case(frame,countdown,y=17,stride=96,page=0,segment=0xA000,bank=DATA_SEG,target=None):
    def setup(m):
        for name,value in (('WaterSurfaceFrame',frame),('WaterYPixels',y),('VgaRowStrideBytes',stride)):
            m.write(bank,m.off('DGROUP:'+name),value.to_bytes(2,'little'))
        m.write(bank,m.off('DGROUP:WaterSurfaceFrameCountdown'),bytes((countdown,)))
        m.ww('GAME:DrawPagePointer',page); m.ww('GAME:DrawPagePointer',segment,2)
        if target is not None:
            m.ww('GAME:WaterSurfaceDispatchWords',m.off(f'GAME:DrawWaterSurfaceFrame{target}'),frame*2)
        m.device.planes[:]=bytes((i*29+77)&255 for i in range(4*65536))
    def check(m,r):
        offset=(y&255)*(stride&255)
        assert int.from_bytes(m.read(bank,m.off('DGROUP:WaterSurfaceByteOffset'),2),'little')==offset
        count=(countdown-1)&255
        assert m.read(bank,m.off('DGROUP:WaterSurfaceFrameCountdown'),1)[0]==(6 if count&128 else count)
        assert m.device.map_mask==15
        assert [v for kind,port,size,v in m.device.log if port==0x3C5]==[1,2,4,8,15]
    return Case(f'water frame={frame} count={countdown:02x} Y={y:04x} stride={stride:04x} page={page:04x} seg={segment:04x} DS={bank:04x} target={target}',
                'GAME:DrawWaterSurface',setup=setup,regs=dict(DS=bank),out_regs=ALL,check=check,flags=0x602)


for frame in range(3):
    for count in (0,1,6,0x7F,0x80,0x81,0xFF): CASES.append(water_case(frame,count))
CASES += [water_case(0,1,y=0xABFF,stride=0x1250,page=0xFFF0),
          water_case(1,1,y=0x8000,stride=0xFFFF,page=0xFFF0),
          water_case(2,1,y=0xFFFF,stride=0xFFFF,page=0xFFF0),
          water_case(0,1,y=0,stride=0,page=7,segment=0x9FFF),
          water_case(2,1,bank=0x7400),water_case(0,1,target=2),
          water_case(1,1,segment=0x7500,page=0xFFF0),
          water_case(0x8000,1)]


def tail_case(frame,start=0,colors=(0x5401,0x5655,0x5857),mask=1):
    def setup(m):
        m.device.seq_index=2; m.device.map_mask=mask
        m.device.planes[:]=bytes((i*13+91)&255 for i in range(4*65536))
    def regs(m):
        original=m.prepare
        def prepare(*args,**kwargs):
            m.prepare=original
            initial=original(*args,**kwargs)
            initial['SP']=(initial['SP']-2)&65535
            m.write(STACK_SEG,initial['SP'],(0x7340).to_bytes(2,'little'))
            m.setreg('SP',initial['SP'])
            return initial
        m.prepare=prepare
        return dict(DS=0xA000,DI=start,DX=0x3C5,AX=colors[0],BX=colors[1],CX=colors[2])
    return Case(f'water tail {frame} DI={start:04x} colors={colors} mask={mask}',
                f'GAME:DrawWaterSurfaceFrame{frame}',setup=setup,regs=regs,out_regs=ALL,flags=0x602)


for frame in range(3):
    CASES += [tail_case(frame),tail_case(frame,0xFFF0),
              tail_case(frame,13,(0xD581,0x2011,0xF0A3),1)]


# Shared-service integration cases.

for slots in ([],[0],[0,3,11]):
    def setup(m,slots=slots):
        for i in range(12):m.ww('DGROUP:FallingItemSprites',0xfffe if i in slots else 0xffff,2*i)
        for i in slots:
            m.ww('DGROUP:FallingItemCallbacks',m.off('GAME:LandFallingItem'),2*i)
            m.ww('DGROUP:FallingItemDescriptors',m.off('DGROUP:Data_7970'),2*i)
    CASES.append(Case('falling dispatcher '+str(slots),'GAME:DispatchFallingItems',setup=setup,
        regs=dict(DS=0x6c19),out_regs=('AX','BX','CX','DX','SI','DI','BP','CF','PF','AF','ZF','SF','OF','IF','DF')))
for x in (0xfe00,0x2800):
    def setup(m,x=x):
        for i in range(12):m.ww('DGROUP:FallingItemSprites',0xffff,2*i)
        for i in (0,11):
            m.ww('DGROUP:FallingItemSprites',0xfffe,2*i)
            m.ww('DGROUP:FallingItemCallbacks',m.off('GAME:AdvanceFallingItem'),2*i)
            m.ww('DGROUP:FallingItemDescriptors',m.off('DGROUP:Data_7970'),2*i)
            m.ww('DGROUP:FallingItemX',x,2*i);m.ww('DGROUP:FallingItemMotionOrLifetime',0,2*i)
    CASES.append(Case(f'falling dispatcher native flight signed boundary {x:04x}',
        'GAME:DispatchFallingItems',setup=setup,regs=dict(DS=0x6c19),flags=0x602,
        out_regs=('AX','BX','CX','DX','SI','DI','BP','CF','PF','AF','ZF','SF','OF','IF','DF')))
