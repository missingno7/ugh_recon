"""Collect receipts without replacing sources or importing unowned work."""
import json,shutil
from closure_support import ROOT,save
from sequencing_build import OUT
def main():
    marker=json.loads((OUT/'snapshot.json').read_text());snapshot=ROOT/marker['snapshot'];artifacts=snapshot/OUT.relative_to(ROOT)
    for source in artifacts.iterdir():
        if source.name in ['reference','host-promotion','rain-scenarios']:continue
        if source.is_dir():shutil.copytree(source,OUT/source.name,dirs_exist_ok=True)
        elif source.suffix=='.json':shutil.copyfile(source,OUT/source.name)
    save(OUT/'baseline-replay.json',dict(result='PASS',**marker,source_snapshot=str(snapshot.relative_to(ROOT))))
    print('Collected committed-baseline receipts',marker['revision'])
if __name__=='__main__':main()
