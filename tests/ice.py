"""All five rebuilt ICE objects, independent Python decode, malformed magic and edge tokens."""
from difftest import Case
from emu import LOAD
from dataprobe import IceDecoder, ice_pack235


def case_for(frame):
    key=f'B{frame:04X}:IceStream_{frame:04X}'
    def check(m,r):
        s,o=m.address(key)
        stream=m.read(s,o,65536)
        n=int.from_bytes(stream[8:12],'big')
        endpoint=int.from_bytes(stream[4:8],'big')-1
        expected=IceDecoder(stream,m.raw_image,bytes(65536)).decode(endpoint,n)
        assert m.read(m.seg('ZERO:IceDecodeWorkspace'),0,n)==expected,'independent ICE decode differs'
    return Case(f'ICE {frame:04X} from rebuilt data','GAME:UnpackIceStream',
                regs=lambda m:dict(DS=m.seg(key),ES=m.seg('ZERO:IceDecodeWorkspace'),SI=0,DI=0xBEEF),check=check,
                out_regs=('AX','BX','CX','DX','BP','SI','DI','DF'))


CASES=[case_for(f) for f in (0x1A38,0x2BF6,0x2D9A,0x2F9E,0x2FB7)]


def synthetic(data):
    stream=ice_pack235(data)
    def setup(m): m.write(0x7500,0,stream)
    def check(m,r): assert m.read(0x7700,0,len(data))==data
    return Case(f'synthetic ICE {len(data)} bytes / {len(stream)} packed','GAME:UnpackIceStream',
                setup=setup,regs=dict(DS=0x7500,ES=0x7700,SI=0,DI=0xBEEF),check=check,
                out_regs=('AX','BX','CX','DX','BP','SI','DI','DF'),flags=0x602)


CASES += [synthetic(b'Z'),synthetic(b'A'*1034),synthetic(bytes(range(256))*8),
          synthetic(bytes((i*73+(i>>3)*19)&255 for i in range(2048)))]
for raw in (b'bad!',b'ICxx'):
    def setup(m,raw=raw): m.write(0x7500,0,raw)
    CASES.append(Case(f'bad ICE magic {raw!r}','GAME:UnpackIceStream',setup=setup,
                      regs=dict(DS=0x7500,ES=0x7700,SI=0,DI=0xBEEF),flags=0x602,
                      out_regs=('AX','BX','CX','DX','BP','SI','DI','DF')))
