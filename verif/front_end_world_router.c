/* Independent physical/member oracle. No bridge binding table is reused. */
#include "front_end_world_bridge.h"
#include <stdio.h>
#include <string.h>
uint8_t ugh_mem[UGH_MEM_SIZE];
uint8_t ugh_read(uint32_t a){return ugh_mem[a];}
void ugh_write(uint32_t a,uint8_t v){ugh_mem[a]=v;}
uint8_t enemies_borrowed_byte(const uint8_t*p,uint32_t i){return p[i];}
void enemies_borrowed_store(uint8_t*p,uint32_t i,uint8_t v){p[i]=v;}
static uint8_t expected[UGH_MEM_SIZE],output[UGH_MEM_SIZE],wanted[UGH_MEM_SIZE];
static uint8_t *members[182];static unsigned addresses[182],count;
static void bind(unsigned at,uint8_t*p,unsigned n){for(unsigned i=0;i<n;i++){unsigned a=lin(DATA_SEG,(uint16_t)(at+i));members[count]=p+i;addresses[count++]=a;wanted[a]=1;}}
int main(void){NativeFrontEndWorld*w=native_front_end_world();
 bind(0xc86,w->score_rows,107);bind(0xc6d,w->name_entry,13);bind(0xb4e,w->password,21);
 bind(0xbfd,w->level_characters,2);bind(0xc7,&w->row_stride,1);bind(0xbb,w->file_handle_bytes,2);
 bind(0xb0d,w->difficulty_text,6);bind(0xb19,w->players_text,10);bind(0xb73,w->control_text[0],10);bind(0xb8d,w->control_text[1],10);
 if(count!=182||sizeof *w!=182)return 1;
 for(unsigned a=0;a<UGH_MEM_SIZE;a++)ugh_mem[a]=(uint8_t)(a*193u+(a>>8)*73u);
 memcpy(expected,ugh_mem,sizeof expected);frontend_cold_import(ugh_mem);
 if(frontend_owned_bytes()!=182)return 2;
 for(unsigned a=0;a<UGH_MEM_SIZE;a++)if(frontend_is_owned(a)!=(int)wanted[a])return 3;
 memcpy(output,ugh_mem,sizeof output);frontend_serialize(output);if(memcmp(output,expected,sizeof output))return 4;
 for(unsigned i=0;i<count;i++)for(unsigned v=0;v<256;v++){
  unsigned a=addresses[i];frontend_borrowed_store(ugh_mem,a,(uint8_t)v);expected[a]=(uint8_t)v;
  if(*members[i]!=v||frontend_borrowed_byte(ugh_mem+(a&~15u),a&15u)!=v)return 5;
  frontend_serialize(output);if(memcmp(output,expected,sizeof output)||frontend_check_serialization(output)!=UINT32_MAX)return 6;
 }
 for(unsigned i=0;i<count;i++)for(unsigned role=0;role<FRONTEND_BORROW_COUNT;role++)for(unsigned width=1;width<=4;width*=2){
  unsigned a=addresses[i];uint16_t pos=(uint16_t)(a-((uint32_t)DATA_SEG<<4));
  frontend_borrow_write((FrontEndBorrower)role,DATA_SEG,pos,width,0x89abcdefu);
  for(unsigned j=0;j<width;j++)expected[a+j]=(uint8_t)(0x89abcdefu>>(8*j));
  memcpy(output,ugh_mem,sizeof output);frontend_serialize(output);if(memcmp(output,expected,sizeof output))return 7;
  uint32_t mask=width==4?UINT32_MAX:((1u<<(8*width))-1u);
  if(frontend_borrow_read((FrontEndBorrower)role,(uint16_t)(DATA_SEG-1),(uint16_t)(pos+16),width)!=(0x89abcdefu&mask))return 8;
 }
 frontend_borrow_write(FRONTEND_BORROW_SESSION,DATA_SEG,0xb4d+1,2,0xbeef);
 if(w->password[0]!=0xef||w->password[1]!=0xbe)return 9;
 frontend_borrow_write(FRONTEND_BORROW_SCORES,DATA_SEG,0xc6f,2,0x7856);
 if(w->name_entry[2]!=0x56||w->name_entry[3]!=0x78)return 10;
 frontend_require_seal(ugh_mem);frontend_serialize(output);output[addresses[0]]^=1;
 if(frontend_check_serialization(output)!=addresses[0])return 11;
 printf("{\"bytes\":182,\"byte_values\":46592,\"straddles\":3276,\"roles\":6,\"aliases\":true}\n");return 0;
}
