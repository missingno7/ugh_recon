"""Real compiled defect controls; private-only requests must reach the bridge."""
from closure_support import save
from player_physics_build import OUT
from player_physics_cases import run
def main():
    mutations=[
      ('SAR6',('player_physics_sar(speed,6)','player_physics_sar(speed,5)'),False),
      ('horizontal-thrust',('speed-63u','speed-62u'),False),
      ('greater-component',('pp_signed(impact)>pp_signed(v->impact)','pp_signed(impact)<pp_signed(v->impact)'),False),
      ('left-probe-reuse',('static void pp_horizontal_scan(PlayerPhysicsProcess *p) {','static void pp_horizontal_scan(PlayerPhysicsProcess *p) {if(!p->positive)p->columns=(uint16_t)(p->columns-1u);'),True),
      ('selected-plane-only',('.kind=PP_READ_PLANE,.value=p->plane','.kind=PP_READ_PLANE,.value=(uint16_t)((p->plane+1u)&3u)'),True),
      ('probe-origin-only',('.probe={p->player->pixel_x,','.probe={(uint16_t)(p->player->pixel_x+1u),'),True),
      ('unconsumed-request',('p->stage=PP_FINISHED;','pp_append(p,(PlayerPhysicsEvent){.kind=PP_READ_PLANE,.value=0});p->stage=PP_FINISHED;'),True),
      ('sampler-XOR',('result|=samples[i]','result^=samples[i]'),False),
      ('surface-equality',('18u))<=0','18u))<0'),False),
    ]
    rows=[]
    for name,mutant,bridge in mutations:
        result,record=run(OUT/'mutants'/name,native_mutant=mutant)
        assert result.returncode and 'FAIL ' in result.stderr,(name,record)
        if bridge:assert 'bridge consumption/projection' in result.stderr,(name,record)
        row=dict(name=name,result='DETECTED_BY_BRIDGE' if bridge else 'DETECTED',mutation=mutant,receipt=str((OUT/'mutants'/name/'result.json').relative_to(OUT)),stderr=result.stderr.strip())
        rows.append(row);print(name,row['result'],flush=True)
    save(OUT/'mutants.json',rows)
if __name__=='__main__':main()
