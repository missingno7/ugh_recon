NativeFrontEndWorld nondet_world(void);unsigned nondet_uint(void);uint8_t nondet_byte(void);
int main(void){
 world=nondet_world();unsigned member=nondet_uint(),lane=nondet_uint(),other=nondet_uint();
 __CPROVER_assume(member<sizeof world && lane<sizeof world-member && other<sizeof world && other!=member+lane);
 FrontEndField f={0,member,1,sizeof world-member,1};
 uint8_t before=((uint8_t*)&world)[member+lane],frame=((uint8_t*)&world)[other],value=nondet_byte();
 assert(frontend_field_get(&f,lane)==before);assert(((uint8_t*)&world)[other]==frame);
#ifdef FRONTEND_PROOF_STORE
 frontend_field_put(&f,lane,value);assert(frontend_field_get(&f,lane)==value);assert(((uint8_t*)&world)[other]==frame);
#else
 (void)value;
#endif
}
