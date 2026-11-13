"""Near-RET hooks, unsigned score addresses, and live overlapping menu copies."""
from difftest import Case
from emu import DATA_SEG

GENERAL=('AX','BX','CX','DX','SI','DI','BP')
ARITH=('CF','PF','AF','ZF','SF','OF')
LOGICAL=('CF','PF','ZF','SF','OF')  # AND leaves AF undefined.
CASES=[]

# The four actual near RETs preserve even deliberately unusual register/flag
# inputs. Extra stack words stand for opaque caller storage, not a far frame.
for label in ('loc_001C','loc_001D','loc_001E','loc_001F'):
    for flags in (0x202,0xED7,0x602,0x8D7):
        CASES.append(Case(f'{label} near return flags={flags:04X}',f'GAME:{label}',
                          flags=flags,flag_inputs=ARITH,args=(0xBEEF,0xDEAD,0x1234),
                          out_regs=GENERAL+ARITH+('IF','DF')))


def score_case(label,index,stride=None,ds=DATA_SEG):
    bias=14 if label=='GetHighScoreDigits' else 0
    def setup(m):
        if stride is not None:
            m.write(ds,m.off('DGROUP:HighScoreRowStride'),bytes((stride,)))
    def check(m,r):
        actual_stride=m.read(ds,m.off('DGROUP:HighScoreRowStride'),1)[0]
        expected=(m.off('DGROUP:HighScoreRows')+bias+(index&255)*actual_stride)&65535
        assert r['AX']==r['BX']==expected
        assert r['CX']==index
    return Case(f'{label} CX={index:04X} stride={stride} DS={ds:04X}',f'GAME:{label}',
                setup=setup,check=check,regs=dict(CX=index,DS=ds),flags=0x602,
                out_regs=GENERAL+ARITH+('IF','DF'))


for label in ('GetHighScoreRow','GetHighScoreDigits'):
    # Normal callers use the rebuilt byte stride and row indices zero to four.
    CASES += [score_case(label,i) for i in range(5)]
    for index,stride in ((0xFF00,255),(0xAB01,0),(0xAB01,1),(0xAB04,21),
                         (0x007F,127),(0x0080,255),(0x00FF,128),(0xFFFF,255),
                         (0x00F0,255),(0x00F5,255),(0x00F6,255),(0x0080,1),
                         (0x00FF,1),(0x0001,255),(0xFF7F,255)):
        CASES.append(score_case(label,index,stride))
    # Dynamic DS must supply the stride, not its symbol's usual storage bank.
    CASES.append(score_case(label,0xFEFD,253,0x7500))


def real_menu(table,index):
    expected={}
    def setup(m):
        source=m.rw('DGROUP:'+table,2*index)
        text=bytearray()
        for n in range(65536):
            ch=m.read(DATA_SEG,(source+n)&65535,1)[0]
            if ch==0: break
            text.append(ch)
        else: raise AssertionError('rebuilt menu string has no NUL')
        expected['text']=bytes(text)
        expected['source']=source
        m.write(DATA_SEG,0x7000,b'~'*64)
    def check(m,r):
        text=expected['text']
        assert m.read(DATA_SEG,0x7000,64)==text+b'~'*(64-len(text))
        assert r['SI']==(expected['source']+len(text)+1)&65535
        assert r['DI']==0x7000+len(text)
    return Case(f'rebuilt {table}[{index}]','GAME:CopyIndexedMenuString',setup=setup,
                regs=lambda m:dict(DS=DATA_SEG,SI=m.off('DGROUP:'+table),BX=index,DI=0x7000),
                check=check,out_regs=GENERAL+LOGICAL+('IF','DF'))


for table,count in (('DifficultyLabelPointers',3),('PlayerCountLabelPointers',2),
                    ('ControlModeLabelPointers',3)):
    CASES += [real_menu(table,i) for i in range(count)]


def synthetic(title,text,source=0x2100,dest=0x3100,table=0x1000,index=0,
              reverse=False,full_cycle=False,ds=0x7500):
    delta=-1 if reverse else 1
    expected={}
    def setup(m):
        buf=bytearray(b'~'*65536)
        if full_cycle:
            # 65535 copied bytes, one NUL, and an identity overlap. The pointer
            # word's bytes are nonzero, so the scan crosses the whole bank.
            buf[:]=b'\x01'*65536
            buf[(source-1)&65535]=0
        else:
            for i,ch in enumerate(text+b'\0'):
                buf[(source+delta*i)&65535]=ch
        ptr=(table+2*index)&65535
        buf[ptr]=source&255
        if ptr!=65535:
            buf[ptr+1]=source>>8
        m.write(ds,0,buf)
        if ptr==65535:
            # One word operand crosses the linear boundary, without wrapping
            # the second byte to offset zero as separate byte loads would.
            m.write(ds,65536,bytes((source>>8,)))
        # Independent bytearray model keeps read/write ordering under overlap;
        # this is static fixture processing, never execution of the oracle.
        si,di=source,dest
        for n in range(65537):
            ch=buf[si]
            si=(si+delta)&65535
            if ch==0: break
            buf[di]=ch
            di=(di+delta)&65535
        else: raise AssertionError('fixture overwrote its terminator')
        expected.update(buf=bytes(buf),si=si,di=di)
    def check(m,r):
        assert m.read(ds,0,65536)==expected['buf']
        assert r['SI']==expected['si'] and r['DI']==expected['di']
        assert r['BX']==(2*index)&65535 and r['AX']==0xAB00
        assert r['ES']==ds
    return Case(title,'GAME:CopyIndexedMenuString',setup=setup,check=check,
                regs=dict(DS=ds,ES=0x7700,AX=0xABEF,SI=table,DI=dest,BX=index),
                flags=0x602 if reverse else 0x202,
                ranges=((ds,0,65536),),  # Includes aliases of dedicated-stack scratch.
                out_regs=GENERAL+LOGICAL+('IF','DF'))


CASES += [
    synthetic('empty preserves stale field',b''),
    synthetic('one byte no NUL store',b'Q'),
    synthetic('unsigned bytes and short stale field',bytes((1,127,128,254,255))),
    synthetic('reverse empty',b'',reverse=True),
    synthetic('reverse high bytes',b'A\xFFZ',reverse=True),
    synthetic('source wraps forward',b'wrap',source=0xFFFE),
    synthetic('destination wraps forward',b'wrap',dest=0xFFFE),
    synthetic('source and destination wrap backward',b'back',source=1,dest=0x20,
              reverse=True),
    synthetic('destination wraps backward',b'back',dest=1,reverse=True),
    synthetic('doubling index wraps',b'index',index=0x8001),
    synthetic('table addition wraps unaligned',b'table',table=0xFFFF,index=1),
    synthetic('pointer word straddles segment end',b'word',table=0xFFFF),
    synthetic('wrapped index selects straddling word',b'word',table=1,index=0xFFFF),
    synthetic('straddling word above one megabyte',b'A20',table=0xFFFF,ds=0xFFFF),
    synthetic('source identical to destination',b'identity',dest=0x2100),
    synthetic('forward overlap consumes original suffix',b'overlap',dest=0x20FF),
    synthetic('reverse overlap consumes original suffix',b'overlap',dest=0x2101,reverse=True),
    synthetic('copy overwrites already consumed table',b'ptr',dest=0x1000),
    synthetic('65535 bytes traverse entire segment',b'',source=0x0101,dest=0x0101,
              table=0x2000,full_cycle=True),
]
