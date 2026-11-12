"""Score files/rows and composed menu glyph rendering; no absent callees/stubs."""
from difftest import Case
from emu import DATA_SEG

GENERAL=('AX','BX','CX','DX','SI','DI','BP')
ARITH=('CF','PF','AF','ZF','SF','OF')
LOGICAL=('CF','PF','ZF','SF','OF')
CASES=[]


def score_file(save,mode='normal',length=107,limit=0,ds=DATA_SEG):
    expected={}
    def setup(m):
        table=m.off('DGROUP:HighScoreRows')
        plain=m.read(DATA_SEG,table,107) if mode=='real' else bytes((i*73+19)&255 for i in range(107))
        m.write(ds,table,plain)
        m.write(ds,m.off('DGROUP:Data_0CF1'),b'UGH!.HI\0')
        m.write(ds,m.off('DGROUP:HighScoreFileHandle'),b'\xef\xbe')
        encoded=bytes((i*39+0xa6)&255 for i in range(length))
        if not save or mode=='existing': m.device.file('UGH!.HI',encoded)
        if mode=='missing': m.device.files[0].exists=0
        if mode=='error': m.device.dos_error=5
        if mode=='badname': m.write(ds,m.off('DGROUP:Data_0CF1'),b'X'*63)
        if mode=='files full':
            for i in range(8): m.device.file(f'OTHER{i}',b'stale')
        if mode=='handles full':
            for i in range(5,32): m.device.handles[i].active=1
        if mode=='occupied':
            for i in (5,6,8): m.device.handles[i].active=1
        m.device.io_limit=limit
        success=mode not in ('missing','error','badname','files full','handles full')
        n=min(107,limit or 107) if save else min(107,length,limit or 107)
        expected.update(plain=plain,encoded=encoded,success=success,n=n,
                        handle=7 if mode=='occupied' else 5)
    def check(m,r):
        e=expected
        table=m.read(ds,m.off('DGROUP:HighScoreRows'),107)
        if save:
            assert table==e['plain']
            assert not r['FLAGS']&1 and r['SI']==65535
            if e['success']:
                h=m.device.handles[e['handle']]
                f=m.device.files[h.file]
                assert h.active and h.mode==2 and h.position==e['n']
                assert f.length==e['n']
                assert bytes(f.data[:e['n']])==bytes(b^255 for b in e['plain'][:e['n']])
        elif e['success']:
            assert table==bytes(b^255 for b in e['encoded'][:e['n']]+e['plain'][e['n']:])
            assert not m.device.handles[e['handle']].active
            assert r['SI']==65535 and not r['FLAGS']&1
        else:
            assert table==e['plain'] and r['FLAGS']&1
        handle=int.from_bytes(m.read(ds,m.off('DGROUP:HighScoreFileHandle'),2),'little')
        assert handle==(e['handle'] if e['success'] else 0xbeef)
    label='SaveHighScores' if save else 'LoadHighScores'
    return Case(f'{label} {mode} length={length} limit={limit} DS={ds:04X}',
                'GAME:'+label,setup=setup,check=check,regs=dict(DS=ds),
                flags=0x602,out_regs=GENERAL+ARITH+('IF','DF'))


for save in (False,True):
    for mode in ('real','normal','existing','error','badname','handles full','occupied'):
        CASES.append(score_file(save,mode))
    if save: CASES.append(score_file(True,'files full'))
    else: CASES.append(score_file(False,'missing'))
    for limit in (1,53,106,107,108): CASES.append(score_file(save,limit=limit))
    CASES.append(score_file(save,ds=0x7600))
for length in (0,1,53,106,108,8192): CASES.append(score_file(False,length=length))


def qualify(candidate,stored,index=2,stride=21,ds=DATA_SEG):
    expected={}
    def setup(m):
        m.write(ds,m.off('DGROUP:HighScoreRowStride'),bytes((stride,)))
        base=(m.off('DGROUP:HighScoreRows')+14+(index&255)*stride)&65535
        m.write(ds,base,stored)
        m.write(ds,m.off('DGROUP:DecimalDigitBuffer'),candidate)
        expected['base']=base
    def check(m,r):
        assert bool(r['FLAGS']&1)==(candidate>=stored)
        assert r['BX']==expected['base'] and r['CX']==index
        last=next((i for i in range(6) if candidate[i]!=stored[i]),5)
        assert r['AX']&255==candidate[last]
        assert bool(r['FLAGS']&64)==(candidate[last]==stored[last])
    return Case(f'qualify {candidate.hex()}/{stored.hex()} index={index:04X} stride={stride}',
                'GAME:TestHighScoreQualification',setup=setup,check=check,
                regs=dict(DS=ds,CX=index),flags=0x602,
                out_regs=GENERAL+ARITH+('IF','DF'))


for pos in range(6):
    for a,b in ((0x20,0x30),(0x39,0x30),(0xff,0),(0,0xff),(0x80,0x7f),(0x7f,0x80)):
        aa=bytearray(b'123456'); bb=bytearray(aa)
        aa[pos]=a; bb[pos]=b
        CASES.append(qualify(bytes(aa),bytes(bb),index=0xa502))
for index,stride in ((0,21),(1,21),(3,21),(4,21),(255,255),(249,250),(0xff00,0),(0x8001,1)):
    CASES.append(qualify(b'000000',b'000000',index,stride))
CASES += [qualify(b'      ',b'      '),qualify(b'000000',b' 99999',ds=0x7600)]


def copy_row(index,stride=21,ds=DATA_SEG):
    expected={}
    def setup(m):
        m.write(ds,m.off('DGROUP:HighScoreRowStride'),bytes((stride,)))
        base=(m.off('DGROUP:HighScoreRows')+(index&255)*stride)&65535
        data=bytes((i*29+0x93)&255 for i in range(64))
        m.write(ds,base,data)
        expected.update(base=base,data=data)
    def check(m,r):
        data=expected['data']; base=expected['base']
        assert m.read(ds,base,64)==data[:21]+data[:20]+data[41:]
        assert r['BX']==(base+20)&65535 and r['DI']==(base+41)&65535
        assert r['DX']==65535 and r['CX']==index
    return Case(f'copy row index={index:04X} stride={stride} DS={ds:04X}',
                'GAME:CopyHighScoreRowDown',setup=setup,check=check,
                regs=dict(DS=ds,CX=index),flags=0x602,
                out_regs=GENERAL+ARITH+('IF','DF'))


for index,stride in ((0,21),(1,21),(2,21),(3,21),(4,21),(0xffff,255),
                     (249,250),(0xff00,0),(0x8001,1),(128,128)):
    CASES.append(copy_row(index,stride))
CASES.append(copy_row(3,ds=0x7600))


BANKS=('SpritePixels0To216Pointer','SpritePixels217To297Pointer',
       'SpritePixels298To546Pointer','SpritePixels547AndUpPointer')


def graphics(m,ds,water=200,real=False):
    m.write(ds,m.off('DGROUP:WaterYPixels'),(water&65535).to_bytes(2,'little'))
    m.ww('GAME:PlayfieldHeight',192)
    m.ww('GAME:DrawPagePointer',0xffd0)
    m.ww('GAME:FixedVgaPagePointer',0x6000)
    m.device.planes[:]=b'\xa5'*(4*65536)
    if not real:
        m.ww('GAME:SpriteDirectoryPointer',0x100)
        m.ww('GAME:SpriteDirectoryPointer',0x8500,2)
        for i in range(1024): m.write(0x8500,0x100+4*i,(i*2).to_bytes(2,'little')+b'\x01\x01')
        for i,bank in enumerate(BANKS):
            m.ww('GAME:'+bank,i*0x1000); m.ww('GAME:'+bank,0x9000,2)
        m.write(0x9000,0,bytes((i*17+3)&63 for i in range(65536)))


def signed(v): return v if v<32768 else v-65536


def render_pixel(m,planes,sprite,x,y,water):
    # Independent one-pixel fixture model; real sprites use differential checks.
    bank=sum(sprite>=v for v in (217,298,547))
    pixel=((bank*0x1000+2*sprite)*17+3)&63
    yy=y if signed(y)<192 else (y-192)&65535
    page=0xffd0 if signed(y)<192 else 0x6000
    if signed((water-yy)&65535)<0: pixel|=0x40
    address=(page+signed(x)//4+yy*96)&65535
    planes[(x&3)*65536+address]=pixel


def text_case(text,block=False,center=False,reverse=False,source=0x6000,
              ds=DATA_SEG,y=32,water=200,title=''):
    expected={}
    stream=(b'\xfe' if center else b'')+text
    def setup(m):
        graphics(m,ds,water)
        delta=-1 if reverse else 1
        for i,ch in enumerate(stream): m.write(ds,(source+delta*i)&65535,bytes((ch,)))
        # Parse the fixture, without running either implementation.
        p=0; yy=y; planes=bytearray(m.device.planes)
        while True:
            x=0; di=(source+delta*(p+1))&65535
            if stream[p]==254:
                p+=1
                n=next(i for i,b in enumerate(stream[p:]) if b in (0,13,253))
                x=((320-((n*16)&65535))&65535)//2
            while stream[p] not in (0,13,253):
                ch={142:91,153:92,154:93}.get(stream[p],stream[p])
                render_pixel(m,planes,ch+0x237,x,yy,water)
                x=(x+16)&65535; p+=1
            term=stream[p]; p+=1
            yy=(yy+{0:0,13:16,253:8}[term])&65535
            if not block or term==0: break
        expected.update(planes=planes,x=x,y=yy,di=di,si=(source+delta*p)&65535,term=term)
    def check(m,r):
        e=expected
        assert m.device.planes==e['planes']
        assert r['BX']==e['x'] and r['CX']==e['y']
        assert r['SI']==e['si'] and r['DI']==e['di'] and r['AX']&255==e['term']
        assert bool(r['FLAGS']&64)==(e['term']==0)
    label='DrawTextBlock' if block else 'DrawTextLine'
    return Case(f'{label} {title or stream[:16].hex()} length={len(stream)} center={center} '
                f'DF={reverse} source={source:04X} y={y:04X} water={water:04X}',
                'GAME:'+label,setup=setup,check=check,regs=dict(DS=ds,SI=source,CX=y),
                flags=0x602 if reverse else 0x202,
                out_regs=GENERAL+LOGICAL+('IF','DF'))


for term in (b'\0',b'\r',b'\xfd'):
    for center in (False,True):
        for reverse in (False,True):
            CASES.append(text_case(term,center=center,reverse=reverse))
            CASES.append(text_case(b'A\x8e\x99\x9aZ'+term,center=center,reverse=reverse))
for y,water in ((191,192),(192,0),(193,0),(65535,0),(32767,32768),(32768,32767)):
    CASES.append(text_case(b'A\r',y=y,water=water))
for count in (1,20,21,4096,4097):
    CASES.append(text_case(b'A'*count+b'\0',center=True,title=f'centering length {count}'))
CASES += [text_case(b'A\xfe\xff\x80\x01\0',ds=0x7600),
          text_case(b'ABC\0',source=65534,ds=0x7600),
          text_case(b'ABC\0',source=1,ds=0x7600,reverse=True),
          text_case(b'ABC\0',source=65534,ds=0x7600,center=True),
          text_case(b'\r\xfd\0',block=True),
          text_case(b'\xfeAB\r\xfeCD\xfdE\0',block=True),
          text_case(b'\xfeAB\r\xfeCD\xfdE\0',block=True,reverse=True),
          text_case(b'\xff\r\xfe\xfd\0',block=True,y=65530)]


for real in (False,True):
    for water in (0,1,200,65535):
        def setup(m,real=real,water=water): graphics(m,DATA_SEG,water,real)
        def check(m,r,real=real,water=water):
            assert (r['AX'],r['BX'],r['CX'])==(214,97,0)
            assert m.device.seq_index==2 and m.device.map_mask==15
            if not real:
                planes=bytearray(b'\xa5'*(4*65536))
                for sprite,x in ((215,16),(216,227),(214,97)):
                    render_pixel(m,planes,sprite,x,0,water)
                assert m.device.planes==planes
        CASES.append(Case(f'header real={real} water={water:04X}','GAME:DrawMenuHeaderSprites',
                          setup=setup,check=check,regs=dict(DS=DATA_SEG),flags=0x602 if water==65535 else 0x202,
                          out_regs=GENERAL+ARITH+('IF','DF')))


# Real menu blocks and ordinary level text use the actual rebuilt sprite directory
# and pixel banks, retaining their full dimensions rather than synthetic glyphs.
for name in ('Text_0AE4','Text_0B64','HighScoreRows','Text_0BF6','Data_50A3'):
    def setup(m): graphics(m,DATA_SEG,200,True)
    CASES.append(Case('rebuilt text '+name,'GAME:DrawTextBlock',setup=setup,
                      regs=lambda m,name=name:dict(DS=DATA_SEG,SI=m.off('DGROUP:'+name),CX=32),
                      out_regs=GENERAL+LOGICAL+('IF','DF')))
