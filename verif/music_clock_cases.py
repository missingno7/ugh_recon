"""Extra direct L0 cases; fixed sources/tests remain independent and unchanged."""
from difftest import Case

CASES=[]
for bit in range(16):
    def setup(m,bit=bit):
        m.ww('SOUND:MainAdlxPlaying',1<<bit)
        m.ww('SOUND:MainAdlxSectionLoopEnabled',0xa55a)
        # Record-12 active flags are a different state word. They are not a gate.
        m.ww('SOUND:MainAdlxFlags',0)
    CASES.append(Case(f'disable full-word bit {bit}','C:DisableMusicSectionLoop',setup=setup,
        kind='far',out_regs=('AX','BX','CX','DX','SI','DI','BP','IF','DF')))
for ticks,origin,rate in [(0,0xffffffff,65535),(0x80000000,1,65535),
                          (0xffffffff,0xfffffffe,2),(420,419,420),(16,1,7),
                          (0,1,65535),(0,0x80000000,65535)]:
    def setup(m,ticks=ticks,origin=origin,rate=rate):
        for name,value in [('AdlxTickCount',ticks),('MainAdlxTimeOrigin',origin)]:
            m.ww('SOUND:'+name,value&65535);m.ww('SOUND:'+name,value>>16,2)
        m.ww('SOUND:MusicTicksPerUnit',rate)
        m.ww('SOUND:MainAdlxPlaying',0);m.ww('SOUND:SoundDeviceBits',0)
    CASES.append(Case(f'elapsed inactive {ticks:08X}-{origin:08X}/{rate}',
        'C:GetElapsedMusicTime',setup=setup,kind='far',out_regs=('AX','DX','SI','DI','BP','IF','DF')))
for value in [1<<(8*b+s) for b in range(4) for s in range(8)]:
    CASES.append(Case(f'swap isolated bit {value:08X}','C:SwapDwordByteOrder',kind='far',
        args=(value&65535,value>>16),out_regs=('AX','BX','CX','DX','SI','DI','BP','CF','PF','AF','ZF','SF','OF','IF','DF')))
