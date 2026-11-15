void palette_service_dac(PaletteDacWrite request){
#if PALETTE_TEST_FAULT == 2
 static unsigned held,done;static uint8_t pending;
 if(!done && request.kind==PALETTE_DAC_COMPONENT){
  if(held){
   platform_out(0x3c9,1,pending==request.value?pending:request.value);
   platform_out(0x3c9,1,pending==request.value?request.value:pending);
   if(pending!=request.value)done=1;
   held=0;return;
  }
  if(!ugh_devices.dac_component){pending=request.value;held=1;return;}
 }
#endif
#if PALETTE_TEST_FAULT == 4
 static unsigned dropped;
 if(!dropped && request.kind==PALETTE_DAC_COMPONENT && request.value){dropped=1;return;}
#endif
#if PALETTE_TEST_FAULT == 5
 ugh_devices.map_mask=0;
#endif
#if PALETTE_TEST_FAULT == 6
 ugh_devices.read_map=0;
#endif
 platform_out(request.kind==PALETTE_DAC_SELECT?0x3c8:0x3c9,1,request.value);
}
