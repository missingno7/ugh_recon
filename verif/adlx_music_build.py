"""Accepted audio chain plus native music lifecycle/fade orchestration."""
import os,re
from pathlib import Path
from closure_support import ROOT,compile_c,hashes,save,function
OUT=ROOT/'build/workers/close-adlx-6'
BRIDGES=[ROOT/'native/bridge'/f'adlx_{name}_bridge.c' for name in ['main','effects','allocation','loader','sections','music']]
NAMES=[name for path in BRIDGES for name in re.findall(r'EXPORT int c_(\w+)\(',path.read_text())]
def build(reference=False):
    folder=OUT/f'{"reference" if reference else "variant"}_{os.getpid()}'
    folder.mkdir(parents=True,exist_ok=True);sources=[]
    for path in sorted((ROOT/'c').glob('*.c')):
        text=path.read_text();changed=False
        if not reference:
            for name in NAMES:
                text,n=re.subn(r'(EXPORT int )c_'+name+r'(?=\()',r'\1l1_'+name,text);changed|=bool(n)
        if changed:
            generated=folder/path.name;generated.write_text(text);sources.append(generated)
        else:sources.append(path)
    if not reference:
        for path in BRIDGES:
            text=path.read_text()
            for name in ['main','effects','allocation','loader','sections','music']:
                text=text.replace(f'#include "../adlx_{name}.h"',f'#include "{(ROOT/"native"/f"adlx_{name}.h").as_posix()}"')
            if 'effects_bridge.c' in path.name:
                text=text.replace('static int effects_bridge_literal','EXPORT uint32_t adlx_effects_audit[32];\nstatic int effects_bridge_literal',1)
                text=text.replace('switch(operation) {','adlx_effects_audit[17]++;\n switch(operation) {',1)
                text=text.replace('AudioState state;','adlx_effects_audit[16]++;\n AudioState state;',1)
                text=text.replace('return l1_RunEffectAdlxEvents(r);','return adlx_effects_audit[18]++, l1_RunEffectAdlxEvents(r);')
                text=text.replace('if(result.stop_request) {','if(result.stop_request) { adlx_effects_audit[19]++;',1)
            if 'allocation_bridge.c' in path.name:
                text=text.replace('typedef struct AllocationFrame','EXPORT uint32_t adlx_allocation_audit[16];\ntypedef struct AllocationFrame',1)
                text=text.replace('if(operation==AUDIO_ALLOCATION_STOP) return l1_', 'adlx_allocation_audit[8+operation]++;\n if(operation==AUDIO_ALLOCATION_STOP) return l1_',1)
                text=text.replace('AllocationFrame frame=allocation_enter(r,operation', 'adlx_allocation_audit[4+operation]++;\n AllocationFrame frame=allocation_enter(r,operation',1)
                text=text.replace('AudioEffectSelection choice=audio_effect_select(&state);','AudioEffectSelection choice=audio_effect_select(&state);adlx_allocation_audit[12+choice.replace]++;')
                for i,name in enumerate(['StopAdlibTrackChannel','RestoreAdlibVoiceAllocation','StartAdlibTrackChannel','PlayAdlibEffect']):
                    body=function(text,'c_'+name);text=text.replace(body,body.replace('{',f'{{adlx_allocation_audit[{i}]++;',1))
            if 'loader_bridge.c' in path.name:
                text=text.replace('typedef struct LoaderFrame','EXPORT uint32_t adlx_loader_audit[16];\ntypedef struct LoaderFrame',1)
                text=text.replace('return l1_LoadAdlibTrackData(r);','return adlx_loader_audit[2]++, l1_LoadAdlibTrackData(r);')
                text=text.replace('LoaderFrame frame=loader_enter(r,16,3);','adlx_loader_audit[1]++;\n LoaderFrame frame=loader_enter(r,16,3);',1)
                text=text.replace('if(result.main_map) {','if(result.main_map) {adlx_loader_audit[6]++;',1)
                text=text.replace('if(result.stage==AUDIO_ADLX_LOADED) {','if(result.stage==AUDIO_ADLX_LOADED) {adlx_loader_audit[5]++;',1)
                for i,name in [(0,'LoadAdlibTrackData'),(3,'LoadAdlibChannel'),(4,'ResetAdlibTrackChannelCursor')]:
                    body=function(text,'c_'+name);text=text.replace(body,body.replace('{',f'{{adlx_loader_audit[{i}]++;',1))
            if 'sections_bridge.c' in path.name:
                text=text.replace('typedef struct SectionFrame','EXPORT uint32_t adlx_sections_audit[16];\ntypedef struct SectionFrame',1)
                text=text.replace('return l1_ScanMusicEvents(r);','return adlx_sections_audit[4]++, l1_ScanMusicEvents(r);')
                text=text.replace('return l1_ApplyScannedMusicEvents(r);','return adlx_sections_audit[6]++, l1_ApplyScannedMusicEvents(r);')
                text=text.replace('SectionFrame f=section_enter(r,24,3);','adlx_sections_audit[3]++;\n SectionFrame f=section_enter(r,24,3);',1)
                text=text.replace('SectionFrame f=section_enter(r,0,1);','adlx_sections_audit[5]++;\n SectionFrame f=section_enter(r,0,1);',1)
                text=text.replace('if(audio_section_apply_due(&state)) {','if(audio_section_apply_due(&state)) {adlx_sections_audit[8]++;',1)
                for i,name in [(0,'ScanMusicEvents'),(1,'ApplyScannedMusicEvents'),(2,'TickAdlxPlayback')]:
                    body=function(text,'c_'+name);text=text.replace(body,body.replace('{',f'{{adlx_sections_audit[{i}]++;',1))
            if 'music_bridge.c' in path.name:
                text=text.replace('typedef struct MusicFrame','EXPORT uint32_t adlx_music_audit[16];\n'+'typedef struct MusicFrame',1)
                for i,name in enumerate(['StartMusicTrack','StopMusicTrack','SetMusicTrackVolume','ScheduleMusicFade','CancelMusicFade','AdvanceMusicFade','AdvanceGuardedSoundClock','SilenceAdlibOperators']):
                    body=function(text,'c_'+name);text=text.replace(body,body.replace('{',f'{{adlx_music_audit[{i}]++;',1))
                text=text.replace('status=platform_service_point_at(', 'adlx_music_audit[8]++;status=platform_service_point_at(',1)
            generated=folder/path.name;generated.write_text(text);sources.append(generated)
        sources += [ROOT/'native'/f'adlx_{name}.c' for name in ['main','effects','allocation','loader','sections','music']]
    dll=folder/'adlx.dll';result=compile_c(sources,dll,[ROOT/'c',ROOT/'native',ROOT/'native/bridge'],['-shared'])
    result['maintained_inputs']=hashes([*BRIDGES,*[ROOT/'native'/f'adlx_{n}.{ext}' for n in ['main','effects','allocation','loader','sections','music'] for ext in ['c','h']],
        ROOT/'native/audio.h',ROOT/'native/bridge/audio_projection.h',*sorted((ROOT/'c').glob('*.[ch]')),Path(__file__)])
    save(OUT/('reference-build.json' if reference else 'build.json'),result);return dll
if __name__=='__main__':print(build())
