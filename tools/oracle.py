"""Oracle lock for UGH.EXE: the packed file, its PKLITE 1.15 expansion, and the repack.

  python tools/oracle.py            check everything against metadata/oracle.json
  python tools/oracle.py --lock     write metadata/oracle.json (first time only; needs --force after)

The expanded executable is written to build/oracle/UGH_X.EXE for the other tools.
The original file in assets/ is only ever read.
"""
import json, shutil, sys
from common import *
from dos import dos

WORK = BUILD / 'oracle'
EXPANDED = WORK / 'UGH_X.EXE'


def expand():
    """PKLITE -x on a copy; returns the expanded bytes."""
    WORK.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(PACKED, EXPANDED)
    dos('PKLITE', ['-x', EXPANDED.name], WORK)
    return EXPANDED.read_bytes()


def repack(expanded):
    """PKLITE on a copy of the expanded file; returns the packed bytes."""
    tmp = WORK / 'REPACK.EXE'
    tmp.write_bytes(expanded)
    dos('PKLITE', [tmp.name], WORK)
    data = tmp.read_bytes()
    tmp.unlink()
    return data


def measure():
    packed = PACKED.read_bytes()
    expanded = expand()
    return {
        'packed': {'path': 'assets/dos/UGH.EXE', 'file_size': len(packed),
                   'file_sha256': sha256(packed), 'packer': 'PKLITE 1.15, standard mode'},
        'expanded': MZ(expanded).identity(),
        'repack_reproduces_packed': repack(expanded) == packed,
    }


def main():
    got = measure()
    path = META / 'oracle.json'
    if '--lock' in sys.argv:
        if path.exists() and '--force' not in sys.argv:
            sys.exit('metadata/oracle.json exists; relocking needs --force and a reason in the commit')
        path.write_text(json.dumps(got, indent=2) + '\n')
        print('locked', path)
        return
    want = json.loads(path.read_text())
    if got != want:
        for k in want:
            if got[k] != want[k]:
                print('MISMATCH', k, '\n  want', want[k], '\n  got ', got[k])
        sys.exit(1)
    if not got['repack_reproduces_packed']:
        sys.exit('repack does not reproduce the packed file')
    e = got['expanded']
    print(f"oracle ok: packed {got['packed']['file_size']} bytes, expanded {e['file_size']} bytes, "
          f"{e['header']['reloc_count']} relocations, repack byte exact")


if __name__ == '__main__':
    main()
