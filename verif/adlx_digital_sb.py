"""Actual DSP/DMA/IRQ API against the committed SB2 fixture, without game patches."""
import sys,json,hashlib
from pathlib import Path
from closure_support import ROOT,function,receipt,save
from adlx_digital_build import OUT,build
import adlx_samples_sb as api

def main():
 source=(ROOT/'verif/adlx_samples_sb.py').read_text();source=source[source.index('def main():'):source.index('    # Fresh input-only witness')]
 source=source.replace("    pair('PrimeSampleDmaPlayback',sound)","    initial_buffer=bytes(dlls[0].ugh_memory().contents)\n    pair('PrimeSampleDmaPlayback',sound)")
 source+='''    memory=bytes(dlls[0].ugh_memory().contents)
    def word(name):
        at=sound*16+m.off('SOUND:'+name);return int.from_bytes(memory[at:at+2],'little')
    remaining=word('SampleMixPairsRemaining');produced=2*(512-remaining);buffer=word('DmaMixBufferOneOffset');pcm=bytes(models[0].pcm)
    assert len(pcm)==641 and produced==258 and models[0].blocks==1,(len(pcm),produced,models[0].blocks)
    assert pcm[produced:]==initial_buffer[sound*16+buffer+produced:sound*16+buffer+len(pcm)],'stale tail retained byte for byte'
    save(OUT/'digital-sb-api.json',receipt([sys.executable,'verif/adlx_digital_sb.py'],[Path(__file__),ROOT/'verif/adlx_samples_sb.py',ROOT/'verif/adlx_digital_build.py',ROOT/'native/adlx_digital.c',ROOT/'native/adlx_digital.h',ROOT/'native/bridge/adlx_digital_bridge.c',ROOT/'tools/emu.py',ROOT/'tools/wholegame.py'],result='PASS',scope='unreachable in the shipped program; API-level generated sample and installed vector',rows=rows,captured_bytes=len(pcm),blocks=models[0].blocks,produced_bytes=produced,stale_tail_bytes=len(pcm)-produced,pcm_sha256=hashlib.sha256(pcm).hexdigest()))
    print('PASS',len(pcm),'DMA bytes:',produced,'fresh,',len(pcm)-produced,'stale',flush=True)
'''
 env=dict(vars(api));env.update(OUT=OUT,build=build,__file__=__file__);exec(compile(source,__file__,'exec'),env);env['main']()
if __name__=='__main__':main()
