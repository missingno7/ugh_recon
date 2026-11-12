"""Byte census of the expanded executable.

  python tools/census.py            print the region table and totals; fail if coverage is not exact
  python tools/census.py --relocs   also list the relocation table in file order, grouped into runs

Regions are the curated entries of metadata/regions.json, keyed by segment frame. Every byte of
the load image must belong to exactly one region, and every frame value found at a relocation
site must be a region start.
"""
import collections, sys
from common import *

EXPANDED = BUILD / 'oracle' / 'UGH_X.EXE'


def census():
    mz = MZ(EXPANDED.read_bytes())
    if mz.identity() != load_json('oracle.json')['expanded']:
        sys.exit('build/oracle/UGH_X.EXE is not the locked expansion; run tools/oracle.py')
    regions = load_json('regions.json')['regions']
    frames = [int(r['frame'], 16) for r in regions]
    errors = []
    if frames != sorted(set(frames)) or frames[0] != 0:
        errors.append('region frames must start at 0000 and ascend without repeats')
    values = sorted({mz.word(s) for s in mz.sites})
    errors += [f'relocation value {v:04X} is not a region frame' for v in values if v not in frames]
    errors += [f'region frame {f:04X} is not evidenced by a relocation value' for f in frames if f not in values]
    ends = [f * 16 for f in frames[1:]] + [len(mz.image)]
    rows = []
    for r, f, end in zip(regions, frames, ends):
        start = f * 16
        body = mz.image[start:end]
        rows.append(dict(r, start=start, size=len(body),
                         sites=sum(1 for s in mz.sites if start <= s < end),
                         refs=sum(1 for s in mz.sites if mz.word(s) == f),
                         zero=body.count(0)))
    if sum(r['size'] for r in rows) != len(mz.image):
        errors.append('regions do not cover the image exactly')
    return mz, rows, errors


def reloc_runs(mz, rows):
    """Relocation sites in file order, cut where the site address drops or the owner changes."""
    starts = [r['start'] for r in rows]
    def owner(site):
        return rows[max(i for i, s in enumerate(starts) if s <= site)]['frame']
    runs = []
    for site in mz.sites:
        if runs and site > runs[-1][-1] and owner(site) == owner(runs[-1][0]):
            runs[-1].append(site)
        else:
            runs.append([site])
    return [(owner(run[0]), run) for run in runs]


def main():
    mz, rows, errors = census()
    print(f'frame linear    size class    sites refs zero%  name')
    totals = collections.Counter()
    for r in rows:
        totals[r['class']] += r['size']
        print(f"{r['frame']:5} {r['start']:06X} {r['size']:7} {r['class']:8} {r['sites']:5} {r['refs']:4} "
              f"{100 * r['zero'] // max(r['size'], 1):5}  {r['name']}")
    print()
    print(f"header {mz.header_size} bytes ({mz.hdr['reloc_count']} relocations), image {len(mz.image)} bytes, "
          f"bss and stack beyond the file {mz.hdr['min_alloc'] * 16} bytes")
    for cls, n in sorted(totals.items(), key=lambda kv: -kv[1]):
        print(f'  {cls:8} {n:7} bytes  {100 * n / len(mz.image):5.1f}%')
    if '--relocs' in sys.argv:
        print('\nrelocation table in file order:')
        for frame, run in reloc_runs(mz, rows):
            print(f'  {frame}  {len(run):3} sites  {run[0]:06X}..{run[-1]:06X}')
    for e in errors:
        print('ERROR', e)
    sys.exit(1 if errors else 0)


if __name__ == '__main__':
    main()
