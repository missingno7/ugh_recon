"""Prepare checked reference inputs under this worker from a clean checkout.

No cgen.generate(), canonical build writes, asset writes, or oracle relocking.
An existing fresh canonical reference is read if available; otherwise pinned
tools rebuild plain L0 / expand and repack a copy in the worker directory.
"""
import argparse,hashlib,importlib,json,sys
from closure_support import ROOT
sys.path.insert(0,str(ROOT/'tools'))
import cgen
OUT=ROOT/'build/workers/close-random/reference'
READ_SYMBOLS=cgen.read_symbols

def prepare_reference(local=False,fresh=False):
    chosen=ROOT/'build/link/plain'
    if local or fresh:chosen=OUT/'link/plain'
    else:
        try:READ_SYMBOLS(chosen)
        except (OSError,ValueError,KeyError):chosen=OUT/'link/plain'
    try:
        if fresh:raise FileNotFoundError('fresh worker rebuild requested')
        READ_SYMBOLS(chosen)
    except (OSError,ValueError,KeyError):
        if chosen!=OUT/'link/plain':raise
        builder=importlib.import_module('build');old=builder.WORK
        try:
            builder.WORK=OUT/'link';builder.build_variant('plain')
        finally:builder.WORK=old
        READ_SYMBOLS(chosen) # image, relocation set, sources and symbols checked
    def selected(directory=None):return READ_SYMBOLS(chosen if directory is None else directory)
    cgen.read_symbols=selected
    return chosen/'UGH.EXE'

def expanded_image(local=False,fresh=False):
    lock=json.loads((ROOT/'metadata/oracle.json').read_text())
    chosen=ROOT/'build/oracle/UGH_X.EXE'
    def valid(path):return path.exists() and hashlib.sha256(path.read_bytes()).hexdigest()==lock['expanded']['file_sha256']
    if local or fresh or not valid(chosen):chosen=OUT/'oracle/UGH_X.EXE'
    if fresh or not valid(chosen):
        oracle=importlib.import_module('oracle');old_work,old_expanded=oracle.WORK,oracle.EXPANDED
        try:
            oracle.WORK=chosen.parent;oracle.EXPANDED=chosen
            result=oracle.measure()
            if result!=lock:raise ValueError('worker oracle expansion/repack differs from immutable lock')
            (chosen.parent/'measurement.json').write_text(json.dumps(result,indent=2)+'\n')
        finally:oracle.WORK,oracle.EXPANDED=old_work,old_expanded
    return chosen

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--fresh',action='store_true');a=p.parse_args()
    print(prepare_reference(local=True,fresh=a.fresh));print(expanded_image(local=True,fresh=a.fresh))
