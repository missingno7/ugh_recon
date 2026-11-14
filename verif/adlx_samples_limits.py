"""Two per-worker solver permits plus the accepted 8GB/600s job wrapper."""
import msvcrt,time
from pathlib import Path
from adlx_loader_solver import cbmc as checked_cbmc
from closure_support import ROOT
def cbmc(harness,folder,inputs,**options):
    permits=ROOT/'build/workers/close-adlx-9/permits';permits.mkdir(parents=True,exist_ok=True)
    permit=None
    while permit is None:
        for index in range(2):
            candidate=(permits/f'{index}.lock').open('a+b');candidate.seek(0);candidate.write(b'0');candidate.flush();candidate.seek(0)
            try:msvcrt.locking(candidate.fileno(),msvcrt.LK_NBLCK,1);permit=candidate;break
            except OSError:candidate.close()
        if permit is None:time.sleep(.2)
    try:return checked_cbmc(harness,folder,[*inputs,Path(__file__)],**options)
    finally:permit.seek(0);msvcrt.locking(permit.fileno(),msvcrt.LK_UNLCK,1);permit.close()
