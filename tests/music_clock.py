"""SOUND state reset and three original Borland huge-model C entry contracts."""
from difftest import Case

PRESERVED=('SI','DI','BP')
CASES=[]
for df in (False,True):
    def setup(m):
        s,o=m.address('SOUND:ext_0664')
        m.write(s,o,bytes((i*31+0xA5)&255 for i in range(0x500)))
    CASES.append(Case(f'clear sound DF={df}','SOUND:ClearSoundState',setup=setup,kind='far',
                      flags=0x602 if df else 0x202,
                      out_regs=('AX','BX','CX','DX','SI','DI','BP','CF','PF','ZF','SF','OF','DF')))

for x in (0,1,0xFFFFFFFF,0x80000000,0x01234567,0xA55A5AA5):
    CASES.append(Case(f'swap {x:08X}','C:SwapDwordByteOrder',kind='far',
                      args=(x&65535,x>>16),out_regs=('AX','DX')+PRESERVED))

for playing,loop in ((0,0),(0,0xFFFF),(1,1),(2,0x8000),(0x8000,5),(0xFFFF,0xFFFF)):
    def setup(m,playing=playing,loop=loop):
        m.ww('SOUND:MainAdlxPlaying',playing)
        m.ww('SOUND:MainAdlxSectionLoopEnabled',loop)
    CASES.append(Case(f'disable section playing={playing:04X}, loop={loop:04X}',
                      'C:DisableMusicSectionLoop',setup=setup,kind='far',out_regs=('AX',)+PRESERVED))

for ticks,origin,rate in ((0,0,1),(0,1,1),(0xFFFFFFFF,0,65535),(0x80000000,0,420),
                           (0x10000,0xFFFF,420),(0x10,0xFFFFFFF0,7),(0xFEED1234,0x12345678,1)):
    def setup(m,ticks=ticks,origin=origin,rate=rate):
        m.ww('SOUND:AdlxTickCount',ticks); m.ww('SOUND:AdlxTickCount',ticks>>16,2)
        m.ww('SOUND:MainAdlxTimeOrigin',origin); m.ww('SOUND:MainAdlxTimeOrigin',origin>>16,2)
        m.ww('SOUND:MusicTicksPerUnit',rate)
    CASES.append(Case(f'elapsed {ticks:08X}-{origin:08X}/{rate}',
                      'C:GetElapsedMusicTime',setup=setup,kind='far',out_regs=('AX','DX')+PRESERVED))
