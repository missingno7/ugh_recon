"""Native session loader proof. Gameplay coverage is reported separately.

No expected record is opened by the native process. The independent literal
worker runs after it exits; comparison projects only the explicitly listed
loader-owned/borrowed fields, not frame/device equivalence.
"""
import argparse
import ctypes as C
import json
import struct
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'tools'), str(ROOT/'verif')]
import cgen
import nativebuild
import s7_session_record
from cbuild import GCC
from job_pool import run, save


def literal(out):
    import wholegame
    from difftest import load_dll, Regs
    from emu import MEM_SIZE
    out = Path(out)
    _, _, ranges = s7_session_record.projection()
    dll = load_dll(out/'literal.dll')
    scenario = wholegame.scenario(ROOT/'tests/levels/one-01.txt')
    m, initial = wholegame.fixture(scenario)
    memory = dll.ugh_memory().contents
    C.memmove(memory, m.snapshot(), MEM_SIZE)
    dll.ugh_devices_reset()
    device = dll.ugh_device_state().contents
    data = m.device.state(); C.memmove(C.addressof(device), data, len(data))
    def set_word(name, value):
        seg, off = m.address('DGROUP:'+name)
        memory[seg*16+off] = value & 255; memory[seg*16+off+1] = value >> 8
    with (out/'literal.bin').open('wb') as f:
        for players, count in [(1, 69), (2, 81)]:
            for level in range(count):
                set_word('PlayerCount', players); set_word('PlayerArrayBytes', players*2); set_word('CurrentLevelIndex', level)
                r = Regs(**{k.lower(): v for k, v in initial.items()})
                status = dll.c_LoadCurrentLevelState(C.byref(r))
                if status:
                    raise RuntimeError(('literal load', players, level, status))
                for at, size, _ in ranges:
                    f.write(bytes(memory[at:at+size]))
    print('literal loader records 150', flush=True)


def source(out):
    helpers, fields, ranges = s7_session_record.projection()
    # Only external semantic configuration enters the native constructor. Each
    # subsequent load retains previous owner fields, exposing stale-tail bugs.
    text = r'''
#include "native/compose_session.h"
#include "port/resources.h"
#include "port/test/backend.h"
#include "resource_manifest.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static uint8_t observation[0x110000];
static void put(unsigned a,unsigned value,unsigned n){for(unsigned i=0;i<n;i++)observation[a+i]=(uint8_t)(value>>(8*i));}
HELPERS
static void record(GameWorld *w,FILE *file){
 FIELDS
 RANGES
}
int main(int argc,char **argv){
 if(argc!=3)return 2;
 GSResourcePack pack;char error[256];
 if(gs_resources_open(&pack,argv[1],port_required_resources,PORT_REQUIRED_COUNT,error,sizeof error)!=GS_OK)return 2;
 GameWorld *w=calloc(1,sizeof *w);GSTestBackend *b=calloc(1,sizeof *b);if(!w||!b)return 2;
 gs_test_init(b);b->resources=gs_resources_operations();b->resource_context=&pack;GameServices s=gs_test_services(b);
 if(game_world_construct(w,&s)!=GS_OK)return 3;
 w->run.water_y=200;
 FILE *f=fopen(argv[2],"wb");if(!f)return 2;
 unsigned records=0;
 for(unsigned players=1;players<=2;players++)for(unsigned level=0;level<(players==1?69u:81u);level++){
  w->run.configuration.players=(uint16_t)players;w->run.configuration.player_bytes=(uint16_t)(2*players);w->run.level=(uint16_t)level;
  GSBytes password;if(session_data_password(&s,(uint16_t)(2*players),(uint16_t)level,&password)!=GS_OK)return 3;
  memset(w->front.password,32,20);memcpy(w->front.password,password.data,password.size-1);
  uint16_t selected=65535;if(game_session_password(w,&s,&selected)!=GS_OK||selected!=level)return 3;
  if(game_session_load(w,&s)!=GS_OK){fprintf(stderr,"load %u %u failed\n",players,level);return 3;}
  record(w,f);records++;
 }
 memset(w->front.password,'?',20);uint16_t fallback=65535;
 if(game_session_password(w,&s,&fallback)!=GS_OK||fallback!=0)return 3;
 /* Level addressing wraps as a word product; the persistent level stays live. */
 w->run.configuration.players=1;w->run.level=32768;
 if(game_session_load(w,&s)!=GS_OK||w->run.level!=32768)return 3;
 fclose(f);free(w);free(b);gs_resources_close(&pack);printf("native loader records %u\n",records);return 0;
}
'''
    writes = '\n'.join('if(fwrite(observation+%d,1,%d,file)!=%d)exit(9);' % (at, n, n) for at, n, _ in ranges)
    path = out/'loader.c'
    path.write_text(text.replace('HELPERS', helpers).replace('FIELDS', fields).replace('RANGES', writes))
    return path, ranges


def verify(out, build=True):
    out = Path(out).resolve(); out.mkdir(parents=True, exist_ok=True)
    prod = out/'production'
    if build:
        nativebuild.build('test', prod)
    audited=json.loads((prod/'nativebuild.json').read_text())
    assert audited['result']=='PASS' and audited['manifest']==nativebuild.sha(ROOT/'metadata/native-manifest.json')
    for name,digest in audited['inputs'].items():assert nativebuild.sha(ROOT/name)==digest,'stale production input: '+name
    manifest = json.loads((ROOT/'metadata/native-manifest.json').read_text())
    sources = manifest['core'] + manifest['backends']['test']
    objects = [prod/('object-%02d.o'%i) for i, s in enumerate(sources) if s != 'port/test/main.c']
    code, ranges = source(out)
    def record(tag, define=None):
        obj = out/(tag+'.o'); exe = out/(tag+'.exe'); binary = out/(tag+'.bin')
        flags = ['-D'+define] if define else []
        run([GCC, '-std=c11', '-O2', '-Wall', '-Wextra', '-Werror', '-Wno-misleading-indentation', *flags,
             '-I', ROOT, '-I', ROOT/'port', '-I', prod, '-c', code, '-o', obj], ROOT, out, tag+'-compile')
        run([GCC, *objects, obj, '-o', exe], ROOT, out, tag+'-link')
        print(run([exe, prod/'ugh.res', binary], ROOT, out, tag+'-run')['stdout'].strip(), flush=True)
        return binary.read_bytes()
    actual = record('native')
    # Independent expected state is generated only after the native child exits.
    print(run([sys.executable, __file__, '--literal', out], ROOT, out, 'literal')['stdout'].strip(), flush=True)
    expected = (out/'literal.bin').read_bytes()
    size = sum(n for _, n, _ in ranges)
    differences = []
    if len(actual) != len(expected):
        differences.append(dict(field='length', actual=len(actual), expected=len(expected)))
    for record_index in range(150):
        cursor = record_index*size
        for at, n, name in ranges:
            if actual[cursor:cursor+n] != expected[cursor:cursor+n]:
                differences.append(dict(record=record_index, field=name, address=hex(at),
                                        actual=actual[cursor:cursor+n].hex(), expected=expected[cursor:cursor+n].hex()))
            cursor += n
    controls = []
    if not differences:
        bad = record('miss-second', 'S7_SESSION_MISS_SECOND_PLAYER')
        assert bad != expected, 'missed second-player projection escaped'
        controls.append('missed second-player projection detected')
    cases=out/'cases.o';exe=out/'cases.exe'
    run([GCC,'-std=c11','-O2','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-I',ROOT,'-I',ROOT/'port','-I',prod,
         '-c',ROOT/'verif/s7_session_cases.c','-o',cases],ROOT,out,'cases-compile')
    run([GCC,*objects,cases,'-o',exe],ROOT,out,'cases-link')
    print(run([exe,prod/'ugh.res'],ROOT,out,'cases')['stdout'].strip(),flush=True)
    save(out/'receipt.json', dict(result='FAIL' if differences else 'PASS', loader_records=150,
                                 distinct_physical_records=81, bytes_per_record=size,
                                 evidence='field projection after loader; not full frame/device equivalence',
                                 differences=differences, controls=controls, gameplay_frames=0))
    print('loader differences', len(differences), differences[:15], flush=True)
    return not differences


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out', type=Path, default=ROOT/'build/workers/s7-session')
    p.add_argument('--no-build', action='store_true')
    p.add_argument('--literal', type=Path)
    args = p.parse_args()
    if args.literal:
        literal(args.literal)
    else:
        raise SystemExit(0 if verify(args.out, not args.no_build) else 1)
