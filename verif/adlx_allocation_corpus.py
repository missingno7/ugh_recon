"""Replay all eleven shipped ADLX streams with native END lifecycle."""
import adlx_effects_corpus as corpus
import ctypes as C,json
from pathlib import Path
from closure_support import receipt,save
from adlx_allocation_build import OUT,build
corpus.OUT=OUT;corpus.build=build;corpus.contacts_reference.OUT=OUT/'reference'
def main():
    loaded=[];original=corpus.nbuild.load_l1
    def tracked(*args,**kwargs):
        dll=original(*args,**kwargs);loaded.append(dll);return dll
    corpus.nbuild.load_l1=tracked
    corpus.main()
    counts=list((C.c_uint32*16).in_dll(loaded[0],'adlx_allocation_audit'))
    assert not sum(counts[8:11]),counts
    save(OUT/'allocation-corpus.json',receipt(['python','verif/adlx_allocation_corpus.py'],[Path(__file__)],
        result='PASS',allocation_audit=counts))
    print('allocation audit:',counts,flush=True)
if __name__=='__main__':main()
