"""Git merge driver for closure certificates (metadata/closure/*.json).

Usage (set by `python tools/cert_merge.py --install`):
    git config merge.certjson.driver "python tools/cert_merge.py %O %A %B"

Parallel cuts relock overlapping certificates. A three-way, field-wise merge:
- fields changed on one side only take that side;
- verification_inputs and dependencies take the union of keys. Their hash values are
  recomputed afterwards by `python verif/contract_locks.py --refresh`, then
  `python tools/closure.py` must pass;
- evidence_refreshed takes the union of notes, ours first;
- list members inside `native` take the union;
- any other field changed differently on both sides is a real conflict. The driver
  leaves ours in place and exits 1, so git reports the conflict.
"""
import json
import subprocess
import sys

UNION_MAPS = ('verification_inputs', 'dependencies')


def merge(base, ours, theirs):
    out, bad = dict(ours), []
    for key in sorted(set(ours) | set(theirs)):
        b, o, t = base.get(key), ours.get(key), theirs.get(key)
        if o == t or t == b:
            continue
        if o == b:
            if t is None:
                out.pop(key, None)
            else:
                out[key] = t
            continue
        if key in UNION_MAPS and isinstance(o, dict) and isinstance(t, dict):
            merged = dict(o)
            for name, value in t.items():
                merged.setdefault(name, value)
            out[key] = merged
        elif key == 'evidence_refreshed' and isinstance(o, list) and isinstance(t, list):
            out[key] = o + [note for note in t if note not in o]
        elif key == 'native' and isinstance(o, dict) and isinstance(t, dict):
            merged = dict(o)
            for name in set(o) | set(t):
                ov, tv = o.get(name), t.get(name)
                if isinstance(ov, list) and isinstance(tv, list):
                    merged[name] = ov + [x for x in tv if x not in ov]
                elif ov != tv:
                    bad.append('native.' + name)
            out[key] = merged
        else:
            bad.append(key)
    return out, bad


def main(argv):
    if argv[1:] == ['--install']:
        subprocess.run(['git', 'config', 'merge.certjson.name', 'closure certificate field merge'], check=True)
        subprocess.run(['git', 'config', 'merge.certjson.driver',
                        'python tools/cert_merge.py %O %A %B'], check=True)
        print('installed merge.certjson driver')
        return 0
    base_path, ours_path, theirs_path = argv[1:4]
    load = lambda p: json.loads(open(p, encoding='utf-8').read() or '{}')
    out, bad = merge(load(base_path), load(ours_path), load(theirs_path))
    if bad:
        sys.stderr.write('cert_merge: real conflict in ' + ', '.join(bad) + '\n')
        return 1
    with open(ours_path, 'w', encoding='utf-8', newline='\n') as handle:
        handle.write(json.dumps(out, indent=2, ensure_ascii=True) + '\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
