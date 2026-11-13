"""All shipped level orders/resources and symbolic raw decoding, clean-checkout runnable."""
import argparse,ctypes as C,json,struct,sys
from pathlib import Path
from closure_support import ROOT,compile_c,receipt,save,cbmc
from contacts_build import OUT
from contacts_reference import prepare_reference,expanded_image
sys.path.insert(0,str(ROOT/'tools'))
import dataprobe
from common import MZ

class Geometry(C.Structure):_fields_=[(n,C.c_uint16) for n in ['anchor_x','anchor_y','extent_x','extent_y']]
class Position(C.Structure):_fields_=[('x32',C.c_uint16),('y32',C.c_uint16)]
class Platform(C.Structure):_fields_=[(n,C.c_uint16) for n in ['left','right','surface_y','arrival_x','waiting_x','spawn_x','destination_icon','reserved_raw']]
class Actor(C.Structure):_fields_=[('geometry',Geometry),('initial_platform',C.c_uint16),('tail_raw',C.c_uint8*2)]
class Enemy(C.Structure):_fields_=[('kind',C.c_int),('geometry',Geometry),('raw',C.c_uint8*10),('raw_size',C.c_size_t)]
class Storage(C.Structure):_fields_=[('tiles',C.c_uint8*320),('platforms',Platform*10),('actors',Actor*16),('enemies',Enemy*5)]
class View(C.Structure):_fields_=[('raw',C.c_uint8*26),('objectives',C.c_uint8),('weather',C.c_uint8),('starts',Position*2),('water_y32',C.c_uint16),('water_increment',C.c_uint16),('tiles',C.POINTER(C.c_uint8)),('platforms',C.POINTER(Platform)),('platform_count',C.c_size_t),('actors',C.POINTER(Actor)),('actor_count',C.c_size_t),('enemies',C.POINTER(Enemy)),('enemy_count',C.c_size_t)]
def fields(value):return [getattr(value,n) for n,_ in value._fields_]
def geometry(d,offset):return list(struct.unpack_from('<4H',d,offset))

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--prove',action='store_true');parser.add_argument('--loader',action='store_true');parser.add_argument('--local-reference',action='store_true');a=parser.parse_args()
    folder=OUT/('level_cbmc' if a.prove else 'level_projection');folder.mkdir(parents=True,exist_ok=True)
    native=ROOT/'native/level_view.c';inputs=[native,ROOT/'native/level.h',ROOT/'native/geometry.h',Path(__file__)]
    if a.prove:
        source=ROOT/'verif/level_view_cbmc.c';harness=folder/'harness.c'
        harness.write_text(f'#include "{native.as_posix()}"\n'+source.read_text())
        result=cbmc(harness,folder,[*inputs,source],unwind=27,timeout=45)
        print(json.dumps({k:result[k] for k in ['result','seconds','failures']}));assert result['result']=='PASS';return
    shim=folder/'exports.c'
    shim.write_text('#include "level_projection.h"\nEXPORT uint8_t probe_ram[65568];\nuint8_t ugh_read(uint32_t address) { return probe_ram[address]; }\nvoid ugh_write(uint32_t address,uint8_t value) { probe_ram[address]=value; }\nEXPORT int project(uint16_t record,const uint8_t *maps,size_t size,LevelProjectionStorage *s,LevelDescription *v) { return level_bridge_project(0,record,maps,size,s,v); }\nEXPORT ObjectGeometry project_geometry(uint16_t descriptor,int item) { return level_bridge_geometry(0,descriptor,item); }\n')
    dll_path=folder/'projection.dll';bridge=ROOT/'native/bridge/level_view_bridge.c'
    built=compile_c([native,bridge,shim],dll_path,[ROOT/'c',ROOT/'native',ROOT/'native/bridge'],['-shared'])
    dll=C.CDLL(str(dll_path));ram=(C.c_uint8*65568).in_dll(dll,'probe_ram')
    dll.project.argtypes=[C.c_uint16,C.POINTER(C.c_uint8),C.c_size_t,C.POINTER(Storage),C.POINTER(View)]
    dll.project_geometry.argtypes=[C.c_uint16,C.c_int];dll.project_geometry.restype=Geometry
    image=expanded_image(local=a.local_reference)
    mz=MZ(image.read_bytes())
    lock=json.loads((ROOT/'metadata/oracle.json').read_text())
    import hashlib
    assert hashlib.sha256(image.read_bytes()).hexdigest()==lock['expanded']['file_sha256']
    maps,orders=dataprobe.levels(mz);d=mz.image[0x5c090:];C.memmove(ram,d,len(d))
    maps_buffer=(C.c_uint8*len(maps)).from_buffer_copy(maps)
    records=set();platforms=actors=enemies=0
    if a.loader:
        import difftest,nbuild
        from contacts_build import build
        from emu import DATA_SEG,MEM_SIZE
        prepare_reference(local=a.local_reference)
        variant=nbuild.load_l1(build());machine=difftest.Machine()
        memory=variant.ugh_memory().contents
    for entry in orders:
        # Decoder's checked order entries are independent of native projection.
        order_base=0x3349 if entry['players']==1 else 0x33d5
        record=struct.unpack_from('<H',d,order_base+2*(entry['number']-1))[0]
        records.add(record);storage=Storage();view=View()
        before=bytes(ram);assert dll.project(record,maps_buffer,len(maps),C.byref(storage),C.byref(view))==1
        assert bytes(ram)==before and bytes(view.raw)==d[record:record+26]
        assert [view.objectives,view.weather,view.water_y32,view.water_increment]==[entry['passengers'],entry['weather'],entry['water'],entry['water_delta']&65535]
        assert fields(view.starts[0])==entry['player1'] and fields(view.starts[1])==entry['player2']
        assert bytes(storage.tiles)==maps[entry['map_offset']:entry['map_offset']+320]
        assert (view.platform_count,view.actor_count,view.enemy_count)==tuple(len(entry[n]) for n in ['platforms','actors','enemies'])
        for i,p in enumerate(entry['platforms']):
            expected=list(p);y=p[2] if p[2]<32768 else p[2]-65536;expected[2]=(p[2]-y//4)&65535
            assert fields(storage.platforms[i])==expected;platforms+=1
        for i,p in enumerate(entry['actors']):
            assert fields(storage.actors[i].geometry)==geometry(d,p[0])
            assert storage.actors[i].initial_platform==p[1] and bytes(storage.actors[i].tail_raw)==struct.pack('<H',p[2]);actors+=1
        for i,p in enumerate(entry['enemies']):
            e=storage.enemies[i];assert e.kind=={0x7630:0,0x766c:1,0x76a8:2,0x76e4:3}[p[0]]
            assert fields(e.geometry)==geometry(d,p[0]) and bytes(e.raw)[:e.raw_size]==struct.pack('<'+'H'*len(p),*p);enemies+=1
        if a.loader:
            machine.reset();difftest.load_suite('menu').composition_fixture(machine)
            machine.ww('DGROUP:PlayerCount',entry['players']);machine.ww('DGROUP:CurrentLevelIndex',entry['number']-1)
            machine.ww('DGROUP:WaterSurfaceByteOffset',18000)
            initial=machine.prepare('GAME:LoadCurrentLevelState',{'DS':DATA_SEG})
            C.memmove(memory,machine.snapshot(),MEM_SIZE);variant.ugh_devices_reset()
            registers=difftest.Regs(**{n.lower():v for n,v in initial.items()})
            assert variant.c_LoadCurrentLevelState(C.byref(registers))==0
            def word(name,index=0):
                address=DATA_SEG*16+machine.off('DGROUP:'+name)+2*index
                return memory[address]+256*memory[address+1]
            for i in range(view.platform_count):
                platform=storage.platforms[i]
                assert [word(n,i) for n in ['PlatformLeftEdges','PlatformRightEdges','PlatformHeights','PlatformArrivalPointsX','PlatformWaitingPointsX','PlatformSpawnX','PlatformDestinationIcons']]==fields(platform)[:7]
                assert word('PlatformActorOccupants',i)==65535
            assert word('PlatformLeftEdges',view.platform_count)&32768
            for i,p in enumerate(entry['actors']):
                assert word('ActorDescriptors',i)==p[0] and word('ActorInitialPlatformIndices',i)==storage.actors[i].initial_platform
            assert word('ActorDescriptors',view.actor_count)==65535
            for i,p in enumerate(entry['enemies']):assert word('EnemyDescriptors',i)==p[0]
            assert word('EnemyDescriptors',view.enemy_count)==65535
            offset=DATA_SEG*16+machine.off('DGROUP:Data_264C')
            assert bytes(memory[offset:offset+320])==bytes(storage.tiles)
    for base,count,stride,item in [(0x7630,4,60,False),(0x7720,8,74,False),(0x7970,11,20,True)]:
        for i in range(count):
            offset=base+i*stride;expected=geometry(d,offset) if not item else [*struct.unpack_from('<2H',d,offset),3,3]
            assert fields(dll.project_geometry(offset,int(item)))==expected
    # Contiguous word bytes at FFFF, then effective-offset wrap for next word.
    for i in range(65568):ram[i]=(i*17+3)&255
    assert fields(dll.project_geometry(65535,0))==[ram[65535]+256*ram[65536],ram[1]+256*ram[2],ram[3]+256*ram[4],ram[5]+256*ram[6]]
    result=receipt(built['command'],[*inputs,bridge,ROOT/'native/bridge/level_projection.h',ROOT/'tools/dataprobe.py',ROOT/'verif/contacts_reference.py',image,ROOT/'metadata/oracle.json'],
        compiler_sha256=built['compiler_sha256'],
        result='PASS',orders=len(orders),unique_records=len(records),platforms=platforms,actors=actors,enemies=enemies,descriptors=23,descriptor_wrap=True,loader_comparisons=len(orders) if a.loader else 0,
        loader_build=json.loads((OUT/'build.json').read_text()) if a.loader else None)
    save(folder/'result.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ['inputs','command','loader_build']}))

if __name__=='__main__':main()
