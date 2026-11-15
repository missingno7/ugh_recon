NativeEnemyWorld nondet_world(void);unsigned nondet_uint(void);uint8_t nondet_byte(void);
int main(void){
 world=nondet_world();unsigned member=nondet_uint(),index=nondet_uint(),lane=nondet_uint(),other=nondet_uint();
 __CPROVER_assume(member+2<=sizeof(NativeEnemySlot) && member<sizeof(NativeEnemySlot) && index<5 && lane<2 && other<sizeof world);
 unsigned at=member+index*sizeof(NativeEnemySlot);__CPROVER_assume(other<at || other>=at+2);
 EnemiesField f={0,member,2,5,sizeof(NativeEnemySlot)};unsigned position=index*2+lane;
 uint16_t before,after;memcpy(&before,(uint8_t*)&world+at,2);uint8_t frame=((uint8_t*)&world)[other],value=nondet_byte();
 assert(enemies_field_get(&f,position)==(uint8_t)(before>>(lane*8)));assert(((uint8_t*)&world)[other]==frame);
#ifdef ENEMIES_PROOF_STORE
 enemies_field_put(&f,position,value);assert(enemies_field_get(&f,position)==value);assert(((uint8_t*)&world)[other]==frame);
 memcpy(&after,(uint8_t*)&world+at,2);assert(after==(uint16_t)((before&~(255u<<(lane*8)))|((unsigned)value<<(lane*8))));
#else
 (void)after;(void)value;
#endif
}
