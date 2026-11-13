"""Directed cases found by exhaustive analysis, separate from the defect corpus."""
import ctypes as C,json,random,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from ice_fuzz import decode,load_native,Result
from dataprobe import IceDecoder,ice_encode_tokens,ice_pack235
from difftest import Regs,MEM_SIZE,Case,run
from emu import Machine
import nbuild

def main():
    start=time.perf_counter();m=Machine();native=load_native(nbuild.build())
    reference=nbuild.load_l1(nbuild.build('reference'));bridge=nbuild.load_l1(nbuild.build('bridge'))
    data=random.Random(32768).randbytes(32769)
    stream=ice_encode_tokens(data,[('literal',32768,-1)],[])
    status,output,result=decode(native,stream,bytes(len(data)))
    assert status==0 and output==data
    assert IceDecoder(stream,m.raw_image,b'').decode(len(stream)-1,len(data))==data
    mem=reference.ugh_memory().contents;C.memmove(mem,m.snapshot(),MEM_SIZE)
    C.memmove(C.addressof(mem)+0x50000,stream,len(stream));C.memset(C.addressof(mem)+0x70000,0,65536)
    r=Regs(ds=0x5000,es=0x7000,flags=0x602)
    assert reference.c_UnpackIceStream(C.byref(r))==0
    assert bytes(mem[0x70000:0x70000+len(data)])==data
    def setup(machine):machine.write(0x5000,0,stream)
    def check(machine,registers):assert machine.read(0x7000,0,len(data))==data
    case=Case('directed signed ICE literal 32769','GAME:UnpackIceStream',setup=setup,
              regs=dict(DS=0x5000,ES=0x7000,SI=0,DI=0xbeef),flags=0x602,check=check,
              out_regs=('AX','BX','CX','DX','BP','SI','DI','DF'))
    assert not run(case,m,bridge,True)
    header_data=b'ignored size high words'*3
    header_stream=bytearray(ice_pack235(header_data));header_stream[4:6]=b'\xa5\x5a';header_stream[8:10]=b'\xc3\x3c'
    status,output,_=decode(native,bytes(header_stream),bytes(len(header_data)))
    assert status==0 and output==header_data
    def header_setup(machine):machine.write(0x5000,0,bytes(header_stream))
    def header_check(machine,registers):assert machine.read(0x7000,0,len(header_data))==header_data
    case=Case('ignored ICE size high words','GAME:UnpackIceStream',setup=header_setup,
              regs=dict(DS=0x5000,ES=0x7000,SI=0,DI=0xbeef),flags=0x602,check=header_check,
              out_regs=('AX','BX','CX','DX','BP','SI','DI','DF'))
    assert not run(case,m,bridge,True)
    bad=[(b'',2,0),(b'I',2,0),(b'xx',1,2),(b'IC',2,2),(b'ICxx',1,4),(b'ICE!',2,4)]
    for raw,wanted,cursor in bad:
        status,output,result=decode(native,raw,bytes(16));assert status==wanted and result.source_cursor==cursor and output==bytes(16)
    magic=[]
    for cursor in (16,65534,65535):
        for raw in (b'xx',b'ICxx'):
            observations=[]
            for dll in (reference,bridge):
                mem=dll.ugh_memory().contents;C.memmove(mem,m.snapshot(),MEM_SIZE)
                # The word operand is physically contiguous at FFFF; SI wraps
                # before the next operand. Match the original operand rule.
                C.memmove(C.addressof(mem)+0x50000+cursor,raw[:2],2)
                if raw.startswith(b'IC'):
                    C.memmove(C.addressof(mem)+0x50000+((cursor+2)&65535),raw[2:],2)
                r=Regs(ds=0x5000,es=0x7000,si=cursor,di=0xbeef,flags=0xed7)
                code=dll.c_UnpackIceStream(C.byref(r));observations.append((code,bytes(r),bytes(mem)))
            assert observations[0]==observations[1]
            magic.append(dict(cursor=cursor,raw=raw.decode()))
    result=dict(signed_literal_32769='L0/bridge and L1/native/Python agree',ignored_high_size_words='L0/bridge/native agree',short_header_cases=len(bad),bad_magic_bridge_cases=magic,
                seconds=time.perf_counter()-start)
    (ROOT/'build/workers/pilot-ice/regressions.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
