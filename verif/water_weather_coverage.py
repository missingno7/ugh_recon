"""Checked native/L1 wiring, pixel service cuts and complete named water access census."""
import re,hashlib
from closure_support import ROOT,function,receipt,save
from water_weather_build import OUT,FILES
from water_weather_shells import NAMES,SOURCES,main as shells
def accesses():
    result=[]
    for path in sorted((ROOT/'c').glob('*.c')):
        source=path.read_text()
        for match in re.finditer(r'^(?:EXPORT\s+)?(?:static\s+)?(?:void|int|uint\d+_t|int\d+_t)\s+(\w+)\s*\(',source,re.M):
            name=match[1]
            try:body=function(source,name)
            except ValueError:continue
            body=re.sub(r'/\*.*?\*/|//[^\n]*','',body,flags=re.S)
            fields=[n for n in ['WaterY32','WaterYPixels','PreviousWaterSurfaceY','WaterSurfaceStep'] if re.search(r'\b'+n+r'\b',body)]
            if not fields:continue
            reads=[n for n in fields if re.search(r'\b(?:R|RI|READ)\('+n+r'\b|rd(?:8|16)\([^;\n]*?D\('+n+r'\)',body)]
            writes=[n for n in fields if re.search(r'\b(?:W|WI|WB)\('+n+r'\b|wr(?:8|16)\([^;\n]*?D\('+n+r'\)',body)]
            result.append(dict(source=path.relative_to(ROOT).as_posix(),function=name,reads=reads,writes=writes))
    result.append(dict(source='c/render.c',function='c_LoadCurrentLevelState',dynamic_write='Backward26-byte CurrentLevelRecord copy also initializes WaterY32 and WaterSurfaceStep from the level record; subsequent explicit scaling/cap writes WaterY32 and pixel/previous Y.'))
    for helper in ['surface_y','submerged','water_swap']:
        callers=[]
        for path in sorted((ROOT/'c').glob('*.c')):
            source=path.read_text()
            for match in re.finditer(r'^(?:EXPORT\s+)?(?:static\s+)?(?:void|int|uint\d+_t|int\d+_t)\s+(\w+)\s*\(',source,re.M):
                if match[1]==helper:continue
                try:body=function(source,match[1])
                except ValueError:continue
                if re.search(r'\b'+helper+r'\s*\(',body):callers.append(path.name+':'+match[1])
        result.append(dict(shared_reader=helper,callers=callers))
    return result
def main():
    OUT.mkdir(parents=True,exist_ok=True);shells();native=(ROOT/'native/water_weather.c').read_text();items=(ROOT/'c/items_water.c').read_text();rows=[]
    for i in range(3):
        pattern=re.search(r'static const char water_frame'+str(i)+r'\[\]\s*=([^;]+);',items)[1]
        expected=''.join(re.findall(r'"([ABCDE]+)"',pattern));actual=''.join(re.findall(r'"([ABCDE]+)"',re.search(r'static const char weather_frame'+str(i)+r'\[\]\s*=([^;]+);',native)[1]))
        assert len(expected)==320 and actual==expected;rows.append(dict(frame=i,cells=320,sha256=hashlib.sha256(expected.encode()).hexdigest()))
    frame=function(items,'water_tail');assert 'for(unsigned plane=0;plane<4;plane++)' in frame and 'for(unsigned x=0;x<80;x++)' in frame
    literal={n:function((ROOT/'c'/f'{SOURCES[n]}.c').read_text(),'c_'+n) for n in NAMES}
    assert 'r->bx=79;' in literal[NAMES[0]] and 'rd8(r->ds,(uint16_t)(r->bx+r->si))' in literal[NAMES[0]] and 'while(!(r->flags&SF))' in literal[NAMES[0]]
    assert 'r->cx&0xfc' in literal['AdvanceRainParticles'] and 'unsigned shift=r->cx&31u;' in literal['DrawRainParticles']
    assert 'r->bx=(uint16_t)((R(WaterYPixels)+1u)*2u)' in literal['AdvanceRainParticles']
    assert 'r->bx=(uint16_t)(rd16(r->ds,D(WaterYPixels))*2u)' in literal['DrawRainParticles']
    assert 'r->bx=(uint16_t)((rd16(r->ds,D(WaterYPixels))+1)*2)' in literal['RestoreRainBackground']
    assert literal['RespawnRainParticle'].count('CALL(NextRandomBelowAx,')==1
    assert 'ww_append(&r,WW_RANDOM,0,weather_random_bound(y),0)' in function(native,'weather_particle_request')
    assert 'if(position>=boundary)' in function(native,'weather_particle_advance')
    for key,helpers in [('water_weather_advance',['ww_store','ww_append']),('water_weather_marked',['ww_store','ww_append']),('weather_particle_advance',['ww_store','ww_append'])]:
        body=function(native,key);assert all(h+'(' in body for h in helpers)
    # Native event cursor controls the complete stream, not just its byte value.
    cursor=function(native,'weather_frame_next');assert 'c->plane*80+c->column' in cursor and 'if(++c->column==80)' in cursor and 'if(c->plane==4)' in cursor and '.value=15' in cursor
    bridge=(ROOT/'native/bridge/water_weather_bridge.c').read_text();assert 'ww_projection(&data,p)' in function(bridge,'ww_tail') and 'p->service_pending=1' in function(bridge,'ww_random')
    census=accesses();bindings=[]
    for p in sorted((ROOT/'native/bridge').glob('*.c')):
        fields=[n for n in ['WaterY32','WaterYPixels'] if re.search(r'D\('+n+r'\)',p.read_text())]
        if fields:bindings.append(dict(bridge=p.relative_to(ROOT).as_posix(),fields=fields))
    save(OUT/'coverage.json',receipt(['python','verif/water_weather_coverage.py'],[*FILES,ROOT/'verif/water_weather_coverage.py',ROOT/'verif/water_weather_shells.py',ROOT/'verif/water_weather_proof.py',*sorted((ROOT/'c').glob('*.c'))],result='PASS',recipes=rows,water_accesses=census,native_bindings=bindings,
      composition='Actual output pieces cover the entire water advance with the unchanged80-cell pixel service contracted at equal input/working-state cuts, full-word animation preparation, post-mark pending update, each rain motion/respawn/draw/restore operation, every frame-cell recipe and cursor transition. Independent native/resource byte frames and inactive-input dependence complete state coverage. Full-word index/post-test and masked-shift properties compose the descending physical-slot loop; per-slot output permits arbitrary physical index<193. The checked complete ABI shells retain flags/registers/stack and fixed pixel-service setup/teardown. Request address/width/value and selected frame/mask are consumed from native results; pending RNG/pixel work and unconsumed normal output are rejected. Actual pixel/latch services, RNG recurrence and complete-loop composition retain their existing contracts and independent full-RAM C/D comparisons. No claim of a formal VGA implementation or unrestricted malformed-resource alias theorem.'))
    print('PASS nine handlers,960 color operands, indexed loop/stream wiring and water reader/writer census')
if __name__=='__main__':main()
