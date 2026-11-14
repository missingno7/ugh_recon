"""Additional input-only L0/native cases, without editing maintained suites."""
from dataclasses import replace
import difftest

def cases():
    scene=difftest.load_suite('scene');result=[];delta=(0,3,5,0x720,0x723,0x725,0x240,0x245,0x480,0x485)
    for mask in range(1024):
        def setup(m,mask=mask):
            origin=0xfffe if mask&1 else 0x100;plane=mask&3;m.device.read_map=plane
            for channel in range(4):
                for i,d in enumerate(delta):m.device.planes[channel*65536+((origin+d)&65535)]=((128 if mask&(1<<i) else 0)|(i+1)) if channel==plane else channel*31+i
        def check(m,r,mask=mask):assert r['AX']==0xab00+15+(128 if mask else 0)
        result.append(difftest.Case('all ten-sample high bits '+str(mask),'GAME:SamplePlayerCollisionPixels',setup=setup,check=check,
            regs=dict(ES=0xa000,SI=0xfffe if mask&1 else 0x100,AX=0xab34),out_regs=tuple(r for r in scene.OUT if r!='AF'),flags=0x602))
    for slot in (0,2):
        for direction in range(4):
            for mask in (0,1,2,3,0x155,0x2aa,0x200,1023):
                hv=(-6144,6144,0,0)[direction];vv=(0,0,-6144,6144)[direction]
                case=scene.move_case('generated first probe mask '+str(mask),slot=slot,hv=hv,vv=vv)
                def setup(m,case=case,direction=direction,mask=mask):
                    case.setup(m);m.device.planes[:]=bytes(4*65536)
                    origin=0x2000+80*96+(100+5)//4
                    if direction==0:plane=0
                    elif direction==1:plane=2
                    else:plane=1;origin+=-96 if direction==2 else 96
                    for i,d in enumerate(delta):m.device.planes[plane*65536+((origin+d)&65535)]=128 if mask&(1<<i) else 0
                result.append(replace(case,setup=setup))
    # Out-of-table difficulty can wrap its limit read onto a word the operation
    # changes. Native import must decline; literal compatibility keeps the bug.
    for name in ['PlayerImpactMagnitude','PlayerHorizontalVelocities','PlayerVerticalVelocities','PlayerPlatformIndices']:
        for slot in (0,2):
            def difficulty(m,name=name,slot=slot):return ((m.off('DGROUP:'+name)+slot-m.off('DGROUP:PlayerImpactLimits'))//2)&65535
            case=scene.move_case('invalid difficulty aliases '+name,slot=slot)
            def setup(m,case=case,difficulty=difficulty):case.setup(m);m.ww('DGROUP:SelectedDifficulty',difficulty(m))
            result.append(replace(case,setup=setup))
    return result
