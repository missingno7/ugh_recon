NativeSessionWorld nondet_world(void);unsigned nondet_uint(void);uint8_t nondet_byte(void);
int main(void){
 world=nondet_world();unsigned member=nondet_uint(),lane=nondet_uint(),other=nondet_uint();
 __CPROVER_assume((member==0 || member==2) && lane<2 && other<sizeof world && other!=member+lane);
 SessionstateField f={0,member,2,1,2};
 uint16_t word;memcpy(&word,(uint8_t*)&world+member,2);
 uint8_t before=(uint8_t)(word>>(lane*8)),frame=((uint8_t*)&world)[other],value=nondet_byte();
 assert(sessionstate_field_get(&f,lane)==before);assert(((uint8_t*)&world)[other]==frame);
#ifdef SESSIONSTATE_PROOF_STORE
 sessionstate_field_put(&f,lane,value);assert(sessionstate_field_get(&f,lane)==value);assert(((uint8_t*)&world)[other]==frame);
#else
 (void)value;
#endif
}
