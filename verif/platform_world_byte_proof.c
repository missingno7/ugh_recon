NativePlatformsWorld nondet_world(void);unsigned nondet_uint(void);uint8_t nondet_byte(void);
int main(void){
 world=nondet_world();unsigned member=nondet_uint(),index=nondet_uint(),lane=nondet_uint(),other=nondet_uint();
 __CPROVER_assume(member+2<=sizeof(NativePlatform) && member<sizeof(NativePlatform) && index<10 && lane<2 && other<sizeof world);
 unsigned at=member+index*sizeof(NativePlatform);__CPROVER_assume(other<at || other>=at+2);
 PlatformsField f={0,member,2,10,sizeof(NativePlatform)};unsigned position=index*2+lane;
 uint16_t before,after;memcpy(&before,(uint8_t*)&world+at,2);uint8_t frame=((uint8_t*)&world)[other],value=nondet_byte();
 assert(platforms_field_get(&f,position)==(uint8_t)(before>>(lane*8)));assert(((uint8_t*)&world)[other]==frame);
#ifdef PLATFORMS_PROOF_STORE
 platforms_field_put(&f,position,value);assert(platforms_field_get(&f,position)==value);assert(((uint8_t*)&world)[other]==frame);
 memcpy(&after,(uint8_t*)&world+at,2);assert(after==(uint16_t)((before&~(255u<<(lane*8)))|((unsigned)value<<(lane*8))));
#else
 (void)after;(void)value;
#endif
}
