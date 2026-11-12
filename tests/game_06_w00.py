"""Supported game-06 leaves; unsupported device entries are recorded in REPORT.md."""
import random
from difftest import Case
from emu import DATA_SEG
from dataprobe import IceDecoder, ice_pack235

GENERAL=('AX','BX','CX','DX','SI','DI','BP')
ARITH=('CF','PF','AF','ZF','SF','OF')
ALL=GENERAL+ARITH+('IF','DF')
CASES=[]


def palette_case(title,source,dest,reverse=False,ds=DATA_SEG,real=False):
    ss,so=source
    es,di=dest
    def setup(m):
        # Alternate DS proves that the pointer cells are read through incoming DS.
        if not real:
            m.write(ss,0,bytes((i*37+(i>>8)*13+91)&255 for i in range(65536)))
        for key,value in (('DGROUP:BasePalettePointer',di),
                          ('DGROUP:PaletteSourcePointer',so)):
            off=m.off(key)
            m.write(ds,off,value.to_bytes(2,'little')+
                    (es if 'Base' in key else ss).to_bytes(2,'little'))
    def check(m,r):
        assert r['CX']==0
        delta=-384 if reverse else 384
        assert r['SI']==(so+delta)&65535
        assert r['DI']==(di+delta)&65535
    return Case(title,'GAME:DuplicateSourcePaletteHalves',setup=setup,
                regs=dict(DS=ds),flags=0x602 if reverse else 0x202,
                ranges=((es,0,65537),),out_regs=ALL,check=check)


CASES += [
    palette_case('palette disjoint forward',(0x7500,0x200),(0x7700,0x400)),
    palette_case('palette disjoint backward',(0x7500,0x400),(0x7700,0x400),True),
    palette_case('palette source and destination wrap',(0x7500,0xff80),(0x7700,0xff00)),
    palette_case('palette odd source and destination wrap',(0x7500,0xffff),(0x7700,0xffff)),
    palette_case('palette odd backward word boundary',(0x7500,0xffff),(0x7700,0xffff),True),
    palette_case('palette backward wraps',(0x7500,0x80),(0x7700,0x80),True),
    palette_case('palette alternate DS',(0x7500,0x200),(0x7700,0x400),ds=0x7300),
    palette_case('palette exact alias',(0x7500,0x200),(0x7500,0x200)),
    palette_case('palette physical alias through distinct segments',(0x7500,0x200),(0x7510,0x100)),
    palette_case('palette forward overlap propagates',(0x7500,0x200),(0x7500,0x202)),
    palette_case('palette backward overlap propagates',(0x7500,0x400),(0x7500,0x3fe),True),
    palette_case('palette second-half write aliases source',(0x7500,0x400),(0x7500,0x280)),
]


def built_palette():
    original={}
    def setup(m):
        ss=m.rw('DGROUP:PaletteSourcePointer',2)
        so=m.rw('DGROUP:PaletteSourcePointer')
        original['source']=m.read(ss,so,384)
        original['dest']=(m.rw('DGROUP:BasePalettePointer',2),m.rw('DGROUP:BasePalettePointer'))
        original['si']=(so+384)&65535
    def check(m,r):
        es,di=original['dest']
        assert m.read(es,di,768)==original['source']*2
        assert r['SI']==original['si'] and r['DI']==(di+384)&65535
    return Case('palette real rebuilt pointers and colors','GAME:DuplicateSourcePaletteHalves',
                setup=setup,regs=dict(DS=DATA_SEG),out_regs=ALL,check=check)


CASES.append(built_palette())


def ice_real(frame):
    key=f'B{frame:04X}:IceStream_{frame:04X}'
    def check(m,r):
        s,o=m.address(key)
        stream=m.read(s,o,65536)
        n=int.from_bytes(stream[8:12],'big')
        end=int.from_bytes(stream[4:8],'big')-1
        expected=IceDecoder(stream,m.raw_image,bytes(65536)).decode(end,n)
        assert m.read(m.seg('ZERO:IceDecodeWorkspace'),0,n)==expected
        assert r['ES']==m.seg('ZERO:IceDecodeWorkspace')
    return Case(f'ICE scratch real {frame:04X}','GAME:UnpackIceToScratch',
                regs=lambda m:dict(DS=m.seg(key),SI=0,DI=0xbeef),flags=0x602,
                out_regs=GENERAL+('DF','IF'),check=check)


CASES += [ice_real(frame) for frame in (0x1a38,0x2bf6,0x2d9a,0x2f9e,0x2fb7)]


def ice_synthetic(data):
    stream=ice_pack235(data)
    def setup(m):
        m.write(0x7500,0,stream)
        m.write(m.seg('ZERO:IceDecodeWorkspace'),0,bytes([0xa7])*65536)
    def check(m,r):
        assert m.read(m.seg('ZERO:IceDecodeWorkspace'),0,len(data))==data
        assert m.read(m.seg('ZERO:IceDecodeWorkspace'),len(data),16)==bytes([0xa7])*16
        assert r['DI']==65535
    return Case(f'ICE scratch synthetic {len(data)}','GAME:UnpackIceToScratch',setup=setup,
                regs=dict(DS=0x7500,SI=0,DI=0xf00d,ES=0x7700),flags=0x602,
                out_regs=GENERAL+('DF','IF'),check=check)


CASES += [ice_synthetic(b'Z'),ice_synthetic(b'A'*1034),
          ice_synthetic(bytes(range(256))*8)]
for raw,offset in ((b'bad!',0),(b'ICxx',0),(b'bad!',0xfffc),(b'ICxx',0xfffc)):
    for reverse in (False,True):
        def setup(m,raw=raw,offset=offset):
            m.write(0x7500,offset,raw)
            m.write(m.seg('ZERO:IceDecodeWorkspace'),0,bytes([0x7d])*65536)
        def check(m,r,raw=raw,offset=offset):
            assert r['SI']==(offset+(4 if raw[:2]==b'IC' else 2))&65535
            assert r['DI']==0 and not (r['FLAGS']&0x400)
            assert m.read(m.seg('ZERO:IceDecodeWorkspace'),0,65536)==bytes([0x7d])*65536
        CASES.append(Case(f'ICE scratch rejected {raw!r} SI={offset:04x} DF={reverse}',
                          'GAME:UnpackIceToScratch',setup=setup,
                          regs=dict(DS=0x7500,SI=offset,DI=0xbeef),
                          flags=0x602 if reverse else 0x202,
                          out_regs=GENERAL+('DF','IF'),check=check))


for flags in (0x2,0x202,0x602,0xed7):
    def check(m,r):
        assert r['AX']&255==3
    CASES.append(Case(f'critical error IRET flags={flags:04x}','GAME:FailDosCriticalError',
                      kind='iret',flags=flags,out_regs=ALL,check=check))


def rng_case(bound,state):
    expected={}
    def setup(m):
        old=state
        if old is None:
            old=tuple(m.rw(f'GAME:RandomStateWord{i}') for i in range(4))
        else:
            for i,v in enumerate(old): m.ww(f'GAME:RandomStateWord{i}',v)
        # Independent recurrence with a full-width running sum and explicit divmod.
        carry,a=divmod(bound+old[0],65536)
        values=[]
        for v in old[1:]:
            carry,n=divmod(v+a+carry,65536)
            values.append(n)
            # State1/2/3 feed the next sum; state0 retains its first partial sum.
            a=n
        first=(bound+old[0])&65535
        new0=(first+values[-1]+carry)&65535
        expected['state']=(new0,*values)
        expected['ax']=(new0*bound)//65536
    def check(m,r):
        assert tuple(m.rw(f'GAME:RandomStateWord{i}') for i in range(4))==expected['state']
        assert r['AX']==expected['ax']
        assert bool(r['FLAGS']&1)==bool(expected['ax'])
        assert bool(r['FLAGS']&0x800)==bool(expected['ax'])
        if bound: assert r['AX']<bound
    return Case(f'RNG bound={bound:04x} state={state}','GAME:NextRandomBelowAx',setup=setup,
                regs=dict(AX=bound),out_regs=GENERAL+('CF','OF','IF','DF'),check=check)


CASES += [rng_case(bound,None) for bound in (0,1,2,0x140,0x7fff,0x8000,0xffff)]
CASES += [rng_case(bound,state) for bound,state in (
    (0,(0,0,0,0)),(0,(0xffff,)*4),(1,(0xffff,)*4),
    (0xffff,(1,0,0,0)),(0xffff,(0xffff,)*4),
    (0x8000,(0x8000,0x7fff,0x8000,0xffff)),
    (2,(0xfffe,0xffff,0,0xffff)),(0xffff,(0,1,0xfffe,1)),
)]
seed=random.Random(0x6a00)
CASES += [rng_case(seed.randrange(65536),tuple(seed.randrange(65536) for _ in range(4)))
          for _ in range(12)]


for mask,flags,ax in ((0,0x2,0),(1,0x203,0xabcd),(5,0x602,0xff00),(15,0x8d7,0x1234)):
    def setup(m,mask=mask):
        m.device.map_mask=mask
        m.device.seq_index=7
    def check(m,r,ax=ax):
        assert r['AX']==((ax&0xff00)|15) and r['DX']==0x3c5
        assert m.device.seq_index==2 and m.device.map_mask==15
        assert m.device.log==[(1,0x3c4,1,2),(1,0x3c5,1,15)]
    CASES.append(Case(f'VGA enable mask={mask} flags={flags:04x}','GAME:EnableAllVgaWritePlanes',
                      setup=setup,regs=dict(AX=ax),flags=flags,flag_inputs=('CF',),
                      out_regs=ALL,check=check))
