"""Deterministic generated inputs, independent packer/decoder, and seeded defects."""
import argparse,ctypes as C,hashlib,json,random,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import nbuild
from difftest import Regs,MEM_SIZE
from emu import Machine
from dataprobe import IceDecoder,ice_pack235,ice_encode_tokens
OUT=ROOT/'build/workers/pilot-ice'

class Result(C.Structure):
    _fields_=[('source_cursor',C.c_size_t),('destination_cursor',C.c_size_t),
              ('bytes_written',C.c_size_t),('tokens',C.c_uint)]

def load_native(path):
    dll=C.CDLL(str(path));fn=dll.ice_decode
    fn.argtypes=[C.c_void_p,C.c_size_t,C.c_void_p,C.c_size_t,C.POINTER(Result)]
    return fn

def decode(fn,stream,seed,size=None):
    source=C.create_string_buffer(stream)
    output=C.create_string_buffer(seed,len(seed));result=Result()
    status=fn(source,len(stream),output,len(seed) if size is None else size,C.byref(result))
    return status,output.raw,result

def corpus(count,m):
    rng=random.Random(0x1ce235);rows=[]
    for frame in (0x1a38,0x2bf6,0x2d9a,0x2f9e,0x2fb7):
        segment,offset=m.address(f'B{frame:04X}:IceStream_{frame:04X}')
        raw=m.read(segment,offset,65536);n=int.from_bytes(raw[4:8],'big')
        stream=raw[:n];data=IceDecoder(stream,m.raw_image,b'').decode(n-1,int.from_bytes(stream[8:12],'big'))
        rows.append(('real',stream,data))
    for i in range(count):
        n=rng.randrange(1,769);kind=i%5
        if kind==0:data=rng.randbytes(n)
        elif kind==1:data=bytes([rng.randrange(256)])*n
        elif kind==2:
            pattern=rng.randbytes(rng.randrange(1,33));data=(pattern*(n//len(pattern)+1))[:n]
        elif kind==3:data=bytes((j*j+i)&255 for j in range(n))
        else:data=bytes(rng.randrange(4) for _ in range(n))
        rows.append(('generated',ice_pack235(data),data))
    for n in (1,2,3,4,5,7,8,9,10,14,15,269,270,271,1033,1034,32767,32768,32769,64768,65535,65536):
        data=(bytes(range(256))*(n//256+1))[:n]
        rows.append(('edge',ice_pack235(data),data))
    return rows

def run(count,mutants):
    m=Machine();rows=corpus(count,m)
    native=load_native(nbuild.build());reference=nbuild.load_l1(nbuild.build('reference'))
    mem=reference.ugh_memory().contents;C.memmove(mem,m.snapshot(),MEM_SIZE)
    reference.c_UnpackIceStream.argtypes=[C.POINTER(Regs)]
    start=time.perf_counter();counts={};accepted_mutations=0;rejected_mutations=0
    rng=random.Random(235);mutated=[];all_mutations=[];python_mutations=0;python_rejections=0
    for i in range(1000):
        _,raw,_=rows[5+i%count];stream=bytearray(raw)
        at=rng.randrange(len(stream));stream[at]^=1<<rng.randrange(8)
        all_mutations.append(bytes(stream))
        # Full L1 runs only when bounded native storage establishes there is no
        # wrap/outside read. All mutations also get a one-iteration comparison
        # below; unbounded corrupt execution is deliberately not attempted.
        status,_,_=decode(native,bytes(stream),bytes(2048))
        if status in (0,1):mutated.append(('mutated',bytes(stream),None));accepted_mutations+=1
        else:rejected_mutations+=1
    rows+=mutated
    def check(fn,stream,expected=None,full=True):
        source=stream.ljust(65536,b'\0');seed=bytes((i*17+3)&255 for i in range(65536))
        status,output,result=decode(fn,source,seed)
        C.memmove(C.addressof(mem)+0x50000,source,65536);C.memmove(C.addressof(mem)+0x70000,seed,65536)
        r=Regs(ax=0xa1,bx=0xb2,cx=0xc3,dx=0xd4,bp=0xb5,ds=0x5000,es=0x7000,di=0xbeef,flags=0xed7)
        code=reference.c_UnpackIceStream(C.byref(r))
        expected_r=Regs(ax=0xa1,bx=0xb2,cx=0xc3,dx=0xd4,bp=0xb5,ds=0x5000,es=0x7000,di=0xbeef,flags=0xad7)
        expected_r.si=result.source_cursor if status in (0,1) else 10
        if status==0:expected_r.di=result.destination_cursor
        if status not in (0,1,4) or code!=(2 if status==4 else 0) or bytes(r)!=bytes(expected_r) or bytes(mem[0x70000:0x80000])!=output:return False
        if expected is not None and output[:len(expected)]!=expected:return False
        return True
    for kind,stream,data in rows:
        if not check(native,stream,data):raise AssertionError((kind,len(stream),hashlib.sha256(stream).hexdigest()))
        if data is not None and len(data)<65536:
            independent=IceDecoder(stream,m.raw_image,b'').decode(len(stream)-1,len(data))
            if independent!=data:raise AssertionError('Python disagreement')
        if kind=='mutated':
            try:
                declared=int.from_bytes(stream[8:12],'big')
                independent=IceDecoder(stream,m.raw_image,b'').decode(len(stream)-1,declared)
            except ValueError:python_rejections+=1
            else:
                status,output,_=decode(native,stream,bytes(max(declared,1)))
                if status or independent!=output:raise AssertionError('mutated Python disagreement')
                python_mutations+=1
        counts[kind]=counts.get(kind,0)+1
    # A malformed but terminating source-cursor wrap. Backward reads cross
    # zero to 65535 in the fixed input window; seed references are intentional.
    wrap=bytearray(65536);wrap[:12]=b'ICE!'+(1).to_bytes(4,'big')+(3).to_bytes(4,'big')
    if not check(native,bytes(wrap)):raise AssertionError('input wrap')
    counts['source_wrap']=1
    defects={}
    if mutants:
        original=(ROOT/'native/ice.c').read_text()
        replacements={
          'rare_length':('return bases[kind]+take_bits(reader,widths[kind]);','return bases[kind]+take_bits(reader,widths[kind])+(kind==4);'),
          'refill_carry':('((byte << 1) | bit)','(byte << 1)'),
          'cursor_wrap':('return (index + 65535u) & 65535u;','return index ? index-1 : 0;'),
          'signed_literal_boundary':('minus_one > 32768','minus_one >= 32768'),
          'offset_bit_order':('return take_bits(reader,wide ? 9 : 6)+(wide ? 65 : 1);','unsigned v=take_bits(reader,wide ? 9 : 6); if(wide) v=((v & 1u)<<8) | (v>>1); return v+(wide ? 65 : 1);')}
        for name,(old,new) in replacements.items():
            assert old in original
            path=OUT/f'mutant_{name}.c'
            path.write_text(original.replace(old,new).replace('#include "ice.h"',f'#include "{(ROOT/"native/ice.h").as_posix()}"'))
            fn=load_native(nbuild.build(source=path,tag='_'+name));found={}
            # Check native against known expected data; do not run divergent
            # full-ring corrupt decoders to their 2-million-token limit.
            for kind,stream,data in rows:
                if data is None:continue
                if found.get(kind):continue
                status,output,result=decode(fn,stream,bytes(max(len(data),1)))
                if status!=0 or output!=data:found[kind]=dict(stream_sha256=hashlib.sha256(stream).hexdigest(),status=status)
            # Full-ring corrupt mutant execution is covered by bounded checks.
            proof=subprocess.run([sys.executable,str(ROOT/'verif/ice_evidence.py'),'--native',str(path)],capture_output=True,text=True)
            if proof.returncode:raise RuntimeError(proof.stdout+proof.stderr)
            proof_result=json.loads(proof.stdout)
            defects[name]=dict(differential=found,primitives=proof_result['primitives'],bounded=proof_result['bounded'])
    import ice_evidence
    bounded_mutations=ice_evidence.bounded(streams=all_mutations)
    result=dict(counts=counts,mutations=dict(accepted=accepted_mutations,rejected_outside_small_buffer_contract=rejected_mutations,
                python_agreed=python_mutations,python_rejected=python_rejections,bounded=bounded_mutations),
                seconds=time.perf_counter()-start,seed='0x1ce235 / 235',defects=defects)
    (OUT/'generated.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--count',type=int,default=3000)
    parser.add_argument('--mutants',action='store_true');args=parser.parse_args();run(args.count,args.mutants)
