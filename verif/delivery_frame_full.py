"""Native byte-frame property with every unborrowed slot field arbitrary.

In particular a phase-agnostic helper reused by WAIT/QUESTION/APPROACH must not
earn its phase-preservation claim only at one seed phase. Keep the declared
read inputs/resource pointers; independently vary every other slot field.
"""
import argparse,concurrent.futures,json,subprocess,sys
from pathlib import Path
from closure_support import ROOT
from delivery_build import OUT
from delivery_pieces import pieces,SLOT_INPUTS,CONTRACTS
from delivery_scalar import make
from delivery_limits import cbmc,SMT

MEMBERS=['phase','journey','source_platform','destination_platform','position','sprite','overlay_sprite','animation',
         'waiting_pose','request_ticks','carrier','journey_wait','horizontal_step','floating_ticks','vertical_motion','quick_delivery_ticks']

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('piece',nargs='?',choices=pieces());p.add_argument('--all',action='store_true');p.add_argument('--timeout',type=int,default=600);a=p.parse_args()
    if a.all:
        def one(key):
            run=subprocess.run([sys.executable,__file__,key,'--timeout',str(a.timeout)],cwd=ROOT,capture_output=True,text=True)
            print(key+' '+run.stdout+run.stderr,flush=True);return run.returncode
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:codes=list(pool.map(one,pieces()))
        assert not any(codes);return
    if not a.piece:p.error('piece or --all required')
    folder=OUT/'frame-full'/a.piece;folder.mkdir(parents=True,exist_ok=True)
    code,inputs=make(a.piece,'frame',folder,'native')
    extra='PassengerStoneSlot unborrowed;\n'
    for member in MEMBERS:
        if member not in SLOT_INPUTS[a.piece]:extra+=f'native_slot.{member}=unborrowed.{member};\n'
    marker='size_t incoming,carrier;';assert code.count(marker)==1;code=code.replace(marker,extra+marker,1)
    wet='1' if a.piece=='rescue' else 'nondet_wet' if a.piece in ('begin-destination','begin-question','begin-approach') else '0'
    code=code.replace('unsigned wet=WET;','_Bool nondet_wet;unsigned wet='+wet+';')
    source=folder/'harness.c';source.write_text(code)
    question=int(a.piece in ('question-clock','contact-question'))
    loops='dl_ref0_contact.0:3,observed_actual_platform_player.0:3,observed_actual_pd_shell1_platform_player.0:3'
    result=cbmc(source,folder,[*inputs,Path(__file__)],unwind=40,timeout=a.timeout,
        defines=['-D__CPROVER__','-DACTOR_VERIFY',f'-DQUESTION={question}','-DUINT16_MAX=65535u'],extra=[*SMT,'--unwindset',loops,'--no-array-field-sensitivity'])
    print(json.dumps({k:result[k] for k in ['result','seconds','peak_private_bytes','failures']}),flush=True);assert result['result']=='PASS'
if __name__=='__main__':main()
