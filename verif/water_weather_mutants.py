from closure_support import save
from water_weather_build import OUT
from water_weather_cases import run
def main():
    tests=[('phase',('s->phase^=1','s->phase^=0'),False),('countdown',('s->countdown&128u','s->countdown==0'),False),
     ('unsigned-boundary',('if(position>=boundary)','if((int16_t)position>=(int16_t)boundary)'),False),
     ('partial-modulo-test',('if(modulo&252u)','if(modulo>=4u)'),False),('edge-direction',('in.direction==1?319:0','in.direction!=0?319:0'),False),
     ('random-bound-only',('return (uint16_t)(320u+y)','return (uint16_t)(319u+y)'),True),
     ('mask-only',('WW_MASK,0,weather_plane_mask(p->modulo_four),0','WW_MASK,0,(uint8_t)(weather_plane_mask(p->modulo_four)+1u),0'),True),
     ('copy-position-only',('WW_COPY,0,0,p->previous','WW_COPY,0,0,(uint16_t)(p->previous+1u)'),True),
     ('unconsumed-request',('ww_store(&r,WW_MODULO,p->modulo_four);return r;','ww_store(&r,WW_MODULO,p->modulo_four);ww_append(&r,WW_RESTORE_ROW,0,0,0);return r;'),True),
     ('mark-position-only',('WW_MARK_ROW,0,0,(uint16_t)((uint8_t)s->previous_y*in.row_stride)','WW_MARK_ROW,0,0,(uint16_t)((uint8_t)s->previous_y*in.row_stride+1u)'),True),
     ('frame-selection-only',('WW_FRAME_TAIL,0,(uint16_t)(s->frame*2u)','WW_FRAME_TAIL,0,(uint16_t)(s->frame*2u+2u)'),True),
     ('frame-final-mask',('.kind=WW_MASK,.value=15','.kind=WW_MASK,.value=0'),True)]
    rows=[]
    for name,mutation,bridge in tests:
        result,record=run(OUT/'mutants'/name,mutation);assert result.returncode and 'FAIL ' in result.stderr,(name,record)
        if bridge:assert 'native bridge consumption/projection' in result.stderr,(name,record)
        rows.append(dict(name=name,result='DETECTED_BY_BRIDGE' if bridge else 'DETECTED',mutation=mutation,stderr=result.stderr.strip()));print(name,rows[-1]['result'],flush=True)
    save(OUT/'mutants.json',rows)
if __name__=='__main__':main()
