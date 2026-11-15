"""Retarget the accepted stale-after-stone fault to the current physics borrower.
No oracle, positive case or production source changes. Platform cut5D replaced
physics' player_read16 with platforms_read16, so the old injected read is dormant.
"""
def source(text):
 needle="   elif tag=='collision-order' and p.name=='player_physics_bridge.c':"
 assert text.count(needle)==1
 injection=r"""   elif tag=='stale-after-stone' and p.name=='platform_world_bridge.c':
    text='#include <stdint.h>\nextern uint16_t player_test_stale_velocity(void);\n'+text
    needle='uint32_t result=0,address=lin(bank,position);';assert text.count(needle)==1
    text=text.replace(needle,needle+'if(borrower==PLATFORMS_BORROW_PHYSICS && width==2 && address==A(PlayerHorizontalVelocities))return player_test_stale_velocity();');changed=True
"""
 text=text.replace(needle,injection+needle)
 old="text=text.replace(needle,needle+'if(borrower==PLAYER_BORROW_PHYSICS && width==2 && address==A(PlayerHorizontalVelocities))return stale.player[0].velocity_x;');changed=True"
 assert text.count(old)==1
 text=text.replace(old,old+";text+="+repr('\nuint16_t player_test_stale_velocity(void){return stale.player[0].velocity_x;}\n'))
 return text

def install(adapter):adapter.SOURCE_ADAPTERS['player_world_cases']=source
