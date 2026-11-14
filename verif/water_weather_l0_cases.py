"""Input-only inherited VGA-mode/latch cases, checked against rebuilt L0."""
import difftest
def cases():
    result=[];data_segment=difftest.load_suite('scene').DATA_SEG
    for mode in range(4):
      for read_mode in (0,8):
       for mask in (0,5,15):
        for name in ['AdvanceWaterSurface','RestoreRainBackground']:
         def setup(m,mode=mode,read_mode=read_mode,mask=mask):
            for n,v in [('WaterY32',64),('WaterYPixels',1),('PreviousWaterSurfaceY',7),('WaterSurfaceStep',31),('VgaRowStrideBytes',0x1260),('WaterStepPhase',0xa500)]:m.ww('DGROUP:'+n,v)
            m.wb('DGROUP:WaterRestorePending',0);m.wb('DGROUP:WaterSurfaceFrameCountdown',0x80)
            m.ww('GAME:BackgroundPagePointer',0xfff0);m.ww('GAME:BackgroundPagePointer',0xa000,2)
            m.ww('GAME:DrawPagePointer',0x4020);m.ww('GAME:DrawPagePointer',0x7500,2)
            for i,v in enumerate([0xfffc,0,1]):m.ww('DGROUP:RainPreviousOffsets',v,2*i)
            m.device.planes[:]=bytes((i*29+(i//65536)*17+71)&255 for i in range(4*65536))
            m.device.map_mask=mask;m.device.gc[5]=mode|read_mode;m.device.gc[2]=10;m.device.gc[7]=5;m.device.gc[0]=3;m.device.gc[1]=2;m.device.gc[3]=0x1b;m.device.gc[8]=0xa5
         result.append(difftest.Case(f'{name} inherited write={mode} read={read_mode} map={mask}', 'GAME:'+name,setup=setup,
             regs=dict(DS=data_segment),out_regs=('AX','BX','CX','DX','SI','DI','BP','DS','ES','CF','PF','ZF','SF','OF','IF','DF'),flags=0x602))
    return result
