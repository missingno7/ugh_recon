"""Actual menu decision/transaction cuts; opaque services end each cut."""
from closure_support import ROOT,function
def sources():return [(ROOT/'c'/n).read_text() for n in ['menu.c','menu_helpers.c','scene.c']]
def password_editor_span(native=False):
 text=(ROOT/'native/bridge/menus_bridge.c').read_text() if native else sources()[0];body=function(text,'c_EditLevelPassword')
 start=body.index('        FrontEditCommand') if native else body.index('        compare_byte(r,(uint8_t)r->ax,8);')
 part=body[start:body.index('        return ugh_dispatch(r->cs,G(InstallKeyboardSequenceInterrupt)')]
 return part.replace('continue;','return 1;').replace('goto reset_blink;','return 2;')+'return 0;'
def selector_span():
 body=function(sources()[0],'c_RunMainMenuAndAttractLoop');start=body.index('        logic(r,r->ax>>8,8);');end=body.index('        MCALL(FadePaletteOut,G(RunMainMenuAndAttractLoop)+0xef);',start);part=body[start:end]
 # Replace only opaque branch bodies: their first native action is the cut.
 for scan,action in [('0x3f','MENUS_MAIN_CONTROLS_FADE'),('0x3e','MENUS_MAIN_PLAYERS'),('0x3d','MENUS_MAIN_DIFFICULTY'),('0x3c','MENUS_MAIN_PASSWORD')]:
  marker='if((uint8_t)r->ax=='+scan+') {';a=part.index(marker)+len(marker);depth=1;b=a
  while depth:
   if part[b]=='{':depth+=1
   elif part[b]=='}':depth-=1
   b+=1
  part=part[:a]+'return '+action+';'+part[b-1:]
 return part.replace('continue;','return MENUS_MAIN_WAIT;').replace('goto restart_attract;','return MENUS_MAIN_RESTART_ATTRACT;').replace('return ugh_dispatch(r->cs,G(FadePaletteOut),r);','return MENUS_MAIN_EXIT_FADE;').replace('goto timeout;','return MENUS_MAIN_RESET_TIMEOUT;')+'return MENUS_MAIN_PLAY_FADE;'
