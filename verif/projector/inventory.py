"""Retain the committed census's raw binding/alias expressions for this freeze.

This is a separate static artifact step; it does not change the compiled world
or import live/uncommitted bridge files. Run after projector_evidence.py --all.
"""
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'verif'))
sys.path.insert(0,str(ROOT/'tools'))
import projector_evidence as evidence


def extract():
    import standalone_census as census
    import hostbuild
    destination=evidence.OUT/'inventory';destination.mkdir(parents=True,exist_ok=True)
    frozen=evidence.OUT/'frozen'
    old=(census.ROOT,census.OUT,hostbuild.ROOT)
    try:
        census.ROOT=frozen;census.OUT=destination;hostbuild.ROOT=frozen
        census.static_inventory()
    finally:census.ROOT,census.OUT,hostbuild.ROOT=old
    inputs=[Path(__file__),ROOT/'verif/standalone_census.py',frozen/'metadata/program-model.json']
    evidence.save(destination/'receipt.json',dict(result='PASS',baseline=json.loads((evidence.OUT/'baseline.json').read_text()),
        inputs={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
        scope='Raw accessor expressions and conservative candidate ownership from the frozen committed tree; no unknown alias is assigned a recovered owner.'))


if __name__=='__main__':
    if '--child' in sys.argv:extract()
    else:
        result=evidence.bounded([sys.executable,__file__,'--child'],'static-inventory')
        print(result['stdout'],end='')
