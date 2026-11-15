/* Included after the actual get/put functions; valid descriptor geometry only. */
NativeRunWorld nondet_world(void);unsigned nondet_uint(void);uint8_t nondet_byte(void);
int main(void){
 world=nondet_world();unsigned width=nondet_uint(),member=nondet_uint(),index=nondet_uint(),lane=nondet_uint(),other=nondet_uint();
 __CPROVER_assume((width==1 || width==2 || width==4) && index<320 && lane<width);
 __CPROVER_assume(member<sizeof world && index*width+member+width<=sizeof world && other<sizeof world);
 unsigned at=member+index*width;__CPROVER_assume(other<at || other>=at+width);
 RunField field={0,member,width,index+1};unsigned position=index*width+lane;
 uint32_t before=0,after=0;
 if(width==1)before=((uint8_t*)&world)[at];else if(width==2){uint16_t v;memcpy(&v,(uint8_t*)&world+at,2);before=v;}else memcpy(&before,(uint8_t*)&world+at,4);
 uint8_t frame=((uint8_t*)&world)[other],value=nondet_byte();
 assert(run_field_get(&field,position)==(uint8_t)(before>>(lane*8)));
 assert(((uint8_t*)&world)[other]==frame);
#ifdef RUN_PROOF_STORE
 run_field_put(&field,position,value);
 assert(run_field_get(&field,position)==value);assert(((uint8_t*)&world)[other]==frame);
 if(width==1)after=((uint8_t*)&world)[at];else if(width==2){uint16_t v;memcpy(&v,(uint8_t*)&world+at,2);after=v;}else memcpy(&after,(uint8_t*)&world+at,4);
 assert(after==((before&~(255u<<(lane*8)))|((uint32_t)value<<(lane*8))));
#else
 (void)after;(void)value;
#endif
}
