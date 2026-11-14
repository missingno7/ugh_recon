"""Read-only scenario VGA census. Only this file and close-stones-13 output are owned.

Generated copies wrap real service definitions (including direct calls), physical
VGA accesses and operand boundaries. Maintained C/native/tools are never edited.
Frame zero is the interval before the first page flip; no synthetic game inputs
or state resets are inserted. Census bookkeeping is outside emulated RAM/Devices.
"""
import argparse,ctypes as C,hashlib,json,os,re,shutil,struct,subprocess,sys,time
from pathlib import Path
from closure_support import ROOT,compile_c,hashes,receipt,save,function
OUT=ROOT/'build/workers/close-stones-13'
sys.path.insert(0,str(ROOT/'tools'))
COMPONENTS=['render_primitives','hud','water_weather','actor_render','player_physics','video_dos']

CENSUS_C=r'''
#include "platform.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "census.h"
void ugh_devices_reset(void);
#define MAX_STATE 4096
typedef unsigned long long U64;
typedef struct State {unsigned service,count,first;unsigned char controls[11];uint16_t args[6];} State;
typedef struct Metrics {U64 reads,writes,outside,offscreen,padding,nonaperture,operand_cross,copy_writes,recent,prior,same,foreign_latch,wrap_steps,initial_wrap,dependent,foreign_any,reductions;unsigned first_reduce,reduce_value,first_wrap,first_out,first_addr,first_recent,first_src,first_dst,off_frame,off_address;uint16_t out_args[6],reduce_args[6];uint32_t out_pages[4];unsigned char out_controls[11];U64 modes[4],read_modes[2],rops[4],masks[16],bit_masks[256];} Metrics;
typedef struct CopyStats {U64 calls,overlap,interval_overlap,recent,prior,same,foreign;unsigned first_overlap,first_recent,first_src,first_dst;} CopyStats;
typedef struct Context {unsigned service,call;uint32_t pages[4];uint16_t args[6];unsigned count,pitch,height;unsigned copy_id,minsrc,maxsrc,mindst,maxdst,overlap,last[2],valid[2];U64 recent,prior,same,foreign;} Context;
typedef struct Geometry {unsigned service,count,first;uint32_t pages[4];unsigned bytes,height,pitch;} Geometry;
static Geometry geometries[2048];static unsigned ngeometries;
static U64 black_wait[256][3];static unsigned black_wait_first[256][3],dimension_first[65536];
static unsigned tilemaps[1024][3],ntilemaps;static uint8_t tilebytes[1024][320];
static U64 segments[65536];static unsigned segment_first[65536];
static unsigned sprite_meta[4096][4],nsprite_meta;
static U64 unscoped_reads,unscoped_writes;
static State states[MAX_STATE];static unsigned nstates,frame,serial,depth,enabled,reply_mutation;
static Context stack[128];static Metrics metric[VC_SERVICES];static CopyStats copies[VC_SERVICES];
static unsigned last_frame[4][65536],last_call[4][65536],src_tag[65536],dst_tag[65536];
static unsigned latch_frame[4],latch_call[4],latch_address,latch_reader;
static U64 entries[VC_SERVICES],returns[256],probe_sites[65536],probe_reads[11];
static unsigned levels[1024][5],nlevels,mask_width[257],sprite_dimensions[65536];
static unsigned rawword(uint16_t seg,uint16_t at){unsigned a=(unsigned)seg*16+at;return ugh_mem[a]+256u*ugh_mem[a+1];}
static void controls(unsigned char *c){memcpy(c,ugh_devices.gc,9);c[9]=ugh_devices.map_mask;c[10]=ugh_devices.read_map;}
static int copy_service(unsigned s){return s==VC_SAVE || s==VC_RECTANGLE || s==VC_RAIN_RESTORE;}
static void fail(void){fprintf(stderr,"census bookkeeping bound/error\n");abort();}
EXPORT void vc_reset(unsigned mutation){
 memset(states,0,sizeof states);memset(metric,0,sizeof metric);memset(copies,0,sizeof copies);memset(entries,0,sizeof entries);
 memset(last_frame,0,sizeof last_frame);memset(last_call,0,sizeof last_call);memset(src_tag,0,sizeof src_tag);memset(dst_tag,0,sizeof dst_tag);
 memset(latch_frame,0,sizeof latch_frame);memset(latch_call,0,sizeof latch_call);memset(returns,0,sizeof returns);memset(probe_sites,0,sizeof probe_sites);memset(probe_reads,0,sizeof probe_reads);memset(sprite_dimensions,0,sizeof sprite_dimensions);memset(mask_width,0,sizeof mask_width);
 memset(geometries,0,sizeof geometries);memset(black_wait,0,sizeof black_wait);memset(black_wait_first,0,sizeof black_wait_first);memset(dimension_first,255,sizeof dimension_first);
 memset(segments,0,sizeof segments);memset(segment_first,0,sizeof segment_first);
 nstates=frame=serial=depth=nlevels=ngeometries=ntilemaps=nsprite_meta=0;unscoped_reads=unscoped_writes=0;enabled=1;reply_mutation=mutation;latch_address=latch_reader=0;
}
void vc_enter(unsigned s,Regs *r){
 if(!enabled)return;if(depth>=128 || s>=VC_SERVICES)fail();
 unsigned char key[11];controls(key);unsigned i;
 for(i=0;i<nstates;i++)if(states[i].service==s && !memcmp(states[i].controls,key,11))break;
 if(i==nstates){if(nstates>=MAX_STATE)fail();State *p=&states[nstates++];p->service=s;p->first=frame;memcpy(p->controls,key,11);p->args[0]=r->ax;p->args[1]=r->bx;p->args[2]=r->cx;p->args[3]=r->dx;p->args[4]=r->si;p->args[5]=r->di;}
 states[i].count++;entries[s]++;
 Context *c=&stack[depth++];memset(c,0,sizeof *c);c->service=s;c->call=++serial;
 c->args[0]=r->ax;c->args[1]=r->bx;c->args[2]=r->cx;c->args[3]=r->dx;c->args[4]=r->si;c->args[5]=r->di;
 const uint16_t bases[]={G(DrawPagePointer),G(DisplayedVgaPagePointer),G(BackgroundPagePointer),G(FixedVgaPagePointer)};
 for(unsigned j=0;j<4;j++)c->pages[j]=rawword(GAME_SEG,bases[j]+2)*16u+rawword(GAME_SEG,bases[j]);
 c->count=rawword(GAME_SEG,G(VgaPlaneCopyByteCount));c->height=rawword(GAME_SEG,G(PlayfieldHeight));c->pitch=c->height==192?96:80;
 for(i=0;i<ngeometries;i++)if(geometries[i].service==s && geometries[i].bytes==c->count && geometries[i].height==c->height && !memcmp(geometries[i].pages,c->pages,sizeof c->pages))break;
 if(i==ngeometries){if(i>=2048)fail();Geometry *g=&geometries[ngeometries++];g->service=s;g->first=frame;g->bytes=c->count;g->height=c->height;g->pitch=c->pitch;memcpy(g->pages,c->pages,sizeof c->pages);}geometries[i].count++;
 if(s==VC_WAIT_ACTIVE){for(unsigned j=0;j+1<depth;j++)if(stack[j].service==VC_BLACKEN){unsigned a=ugh_devices.dac_index,b=ugh_devices.dac_component;if(!black_wait[a][b])black_wait_first[a][b]=frame;black_wait[a][b]++;break;}}
 if(s==VC_SPRITE || s==VC_RECTANGLE){
  int x=(int16_t)r->ax,y=(int16_t)r->bx;unsigned page=0;if(s==VC_SPRITE){x=(int16_t)r->bx;y=(int16_t)r->cx;if(y>=(int16_t)c->height){page=3;y=(int16_t)(y-192);}}else page=2;
  int quarter=x>=0?x/4:-((-x+3)/4);int position=(int)(c->pages[page]-0xa0000u)+y*96+quarter;if(position<0 || position>65535)metric[s].initial_wrap++;
  unsigned raw=(uint16_t)y*96u+(uint16_t)quarter,overflow=raw>65535u,value=raw;
  if(s==VC_SPRITE){raw=(uint16_t)c->pages[page]+(uint16_t)quarter+(uint16_t)((uint16_t)y*96u);if(raw>65535u){overflow=1;value=raw;}}
  else {unsigned src=(uint16_t)c->pages[2]+(uint16_t)raw,dst=(uint16_t)c->pages[0]+(uint16_t)raw;if(src>65535u || dst>65535u){overflow=1;value=src>65535u?src:dst;}}
  if(overflow){Metrics *m=&metric[s];if(!m->reductions){m->first_reduce=frame;m->reduce_value=value;memcpy(m->reduce_args,c->args,sizeof c->args);}m->reductions++;}
 }
 c->minsrc=c->mindst=0xffffffffu;
 if(copy_service(s)){c->copy_id=c->call;copies[s].calls++;}
 if(s==VC_SAMPLE){unsigned ret=rawword(r->ss,r->sp);probe_sites[ret]++;}
 if(s==VC_TILEMAP){if(ntilemaps>=1024)fail();unsigned offset=rawword(r->ds,D(CurrentTileMapPointer)),segment=rawword(r->ds,D(CurrentTileMapPointer)+2);tilemaps[ntilemaps][0]=frame;tilemaps[ntilemaps][1]=segment;tilemaps[ntilemaps][2]=offset;memcpy(tilebytes[ntilemaps++],ugh_mem+segment*16+offset,320);}
 if(s==VC_SPRITE){unsigned dir=rawword(GAME_SEG,G(SpriteDirectoryPointer)),seg=rawword(GAME_SEG,G(SpriteDirectoryPointer)+2);unsigned d=rawword((uint16_t)seg,(uint16_t)(dir+r->ax*4u+2u));if(!sprite_dimensions[d])dimension_first[d]=frame;sprite_dimensions[d]++;mask_width[d&255]++;unsigned j;for(j=0;j<nsprite_meta;j++)if(sprite_meta[j][0]==r->ax && sprite_meta[j][1]==d)break;if(j==nsprite_meta){if(j>=4096)fail();sprite_meta[j][0]=r->ax;sprite_meta[j][1]=d;sprite_meta[j][3]=frame;nsprite_meta++;}sprite_meta[j][2]++;}
}
static void memory_access(uint32_t a,int write){
 if(!enabled || !depth)return;Context *c=&stack[depth-1];Metrics *m=&metric[c->service];
 if(write)m->writes++;else m->reads++;
 int aperture=a>=0xa0000u && a<0xb0000u;
 if(!aperture){m->nonaperture++;return;}
 if(c->valid[write] && ((a>c->last[write] && a-c->last[write]>32768u) || (a<c->last[write] && c->last[write]-a>32768u))){if(!m->wrap_steps)m->first_wrap=frame;m->wrap_steps++;}c->valid[write]=1;c->last[write]=a;
 unsigned allocated=0,visible=0,background=0;
 for(unsigned j=0;j<3;j++)if(a>=c->pages[j] && a-c->pages[j]<c->count){allocated=1;unsigned d=a-c->pages[j];if(j==2)background=1;else if(d/c->pitch<c->height && d%c->pitch<80)visible=1;}
 if(c->height==192 && a>=c->pages[3] && a-c->pages[3]<8u*96u){allocated=1;if((a-c->pages[3])%96u<80)visible=1;}
 if(!allocated){if(!m->outside){m->first_out=frame;m->first_addr=a;memcpy(m->out_args,c->args,sizeof c->args);memcpy(m->out_pages,c->pages,sizeof c->pages);controls(m->out_controls);}m->outside++;}
 if(!visible && !background){if(!m->offscreen){m->off_frame=frame;m->off_address=a;}m->offscreen++;}
 if(allocated && !visible && !background)m->padding++;
 if(write){m->modes[ugh_devices.gc[5]&3]++;m->rops[(ugh_devices.gc[3]>>3)&3]++;m->masks[ugh_devices.map_mask&15]++;m->bit_masks[ugh_devices.gc[8]]++;}
 else m->read_modes[(ugh_devices.gc[5]>>3)&1]++;
}
void vc_read(uint32_t a){
 if(!enabled)return;unsigned o=(uint16_t)a;if(!depth){unscoped_reads++;for(unsigned p=0;p<4;p++){latch_frame[p]=last_frame[p][o];latch_call[p]=last_call[p][o];}latch_address=a;latch_reader=0;return;}memory_access(a,0);Context *c=&stack[depth-1];
 for(unsigned p=0;p<4;p++){latch_frame[p]=last_frame[p][o];latch_call[p]=last_call[p][o];}
 latch_address=a;latch_reader=c->call;
 if(c->service==VC_SAMPLE)probe_reads[0]++;
 if(c->copy_id){src_tag[o]=c->copy_id;if(dst_tag[o]==c->copy_id)c->overlap=1;if(a<c->minsrc)c->minsrc=a;if(a>c->maxsrc)c->maxsrc=a;}
}
void vc_write(uint32_t a,uint8_t value){
 if(!enabled)return;unsigned o=(uint16_t)a;if(!depth){unscoped_writes++;for(unsigned p=0;p<4;p++)if(ugh_devices.map_mask&(1u<<p)){last_frame[p][o]=frame+1;last_call[p][o]=0;}return;}memory_access(a,1);Context *c=&stack[depth-1];Metrics *m=&metric[c->service];unsigned mode=ugh_devices.gc[5]&3,mask=ugh_devices.gc[8];
 if(mode==3){unsigned n=ugh_devices.gc[3]&7;mask&=(uint8_t)((value>>n)|(value<<(8-n)));}
 if(mode==1 || mask!=255 || ((ugh_devices.gc[3]>>3)&3)){m->dependent++;if(latch_reader!=c->call)m->foreign_any++;}
 if(c->copy_id){dst_tag[o]=c->copy_id;if(src_tag[o]==c->copy_id)c->overlap=1;if(a<c->mindst)c->mindst=a;if(a>c->maxdst)c->maxdst=a;}
 if(mode==1 || mask==0){
  m->copy_writes++;unsigned recent=0,prior=0,same=0;
  for(unsigned p=0;p<4;p++)if((ugh_devices.map_mask&(1u<<p)) && latch_frame[p]==frame+1){recent=1;if(latch_call[p]==c->call)same=1;else prior=1;}
  if(recent){if(!m->recent){m->first_recent=frame;m->first_src=latch_address;m->first_dst=a;}m->recent++;c->recent++;}
  if(prior){m->prior++;c->prior++;}if(same){m->same++;c->same++;}
  if(latch_reader!=c->call){m->foreign_latch++;c->foreign++;}
 }
 for(unsigned p=0;p<4;p++)if(ugh_devices.map_mask&(1u<<p)){last_frame[p][o]=frame+1;last_call[p][o]=c->call;}
}
void vc_operand(uint16_t seg,uint16_t off,unsigned width){
 if(!enabled || !depth)return;unsigned a=(unsigned)seg*16u+off;
 if(a>=0xa0000u && a<0xb0000u){if(!segments[seg])segment_first[seg]=frame;segments[seg]++;}
 if(a>=0xa0000u && a<0xb0000u && a+width>0xb0000u)metric[stack[depth-1].service].operand_cross++;
 /* A word's high byte is contiguous, even when it leaves A000:FFFF. */
 if(a==0xaffffu && width>1)metric[stack[depth-1].service].nonaperture+=width-1;
}
void vc_leave(unsigned s,Regs *r,int status){
 if(!enabled)return;if(!depth || stack[depth-1].service!=s)fail();Context *c=&stack[depth-1];
 if(c->copy_id){CopyStats *q=&copies[s];if(c->overlap){if(!q->overlap)q->first_overlap=frame;q->overlap++;}if(c->minsrc!=0xffffffffu && c->mindst!=0xffffffffu && c->minsrc<=c->maxdst && c->mindst<=c->maxsrc)q->interval_overlap++;
  if(c->recent){if(!q->recent){q->first_recent=frame;q->first_src=metric[s].first_src;q->first_dst=metric[s].first_dst;}q->recent++;}if(c->prior)q->prior++;if(c->same)q->same++;if(c->foreign)q->foreign++;
 }
 if(s==VC_SAMPLE){returns[(uint8_t)r->ax]++;if(reply_mutation){uint8_t v=(uint8_t)r->ax;if(reply_mutation==1)v^=127;else if(reply_mutation==2)v&=127;set_al(r,(uint8_t)logic(r,v,8));}}
 if(s==VC_LEVEL && !status && nlevels<1024){unsigned players=rawword(DATA_SEG,D(PlayerCount)),index=rawword(DATA_SEG,D(CurrentLevelIndex));unsigned table=rawword(DATA_SEG,(uint16_t)(D(LevelOrderTables)+(uint16_t)((players-1u)*2u)));unsigned record=rawword(DATA_SEG,(uint16_t)(table+index*2u));levels[nlevels][0]=frame;levels[nlevels][1]=players;levels[nlevels][2]=index;levels[nlevels][3]=record;levels[nlevels++][4]=rawword(DATA_SEG,D(WaterYPixels));}
 depth--;if(s==VC_SWAP)frame++;
}
static void array(FILE *f,const U64 *a,unsigned n){fputc('[',f);for(unsigned i=0;i<n;i++)fprintf(f,"%s%llu",i?",":"",a[i]);fputc(']',f);}
EXPORT void vc_dump(const char *path){
 FILE *f=fopen(path,"wb");if(!f)fail();fprintf(f,"{\"frames\":%u,\"unscoped_reads\":%llu,\"unscoped_writes\":%llu,\"services\":[",frame,unscoped_reads,unscoped_writes);
 for(unsigned s=0;s<VC_SERVICES;s++){Metrics *m=&metric[s];CopyStats *q=&copies[s];fprintf(f,"%s{\"id\":%u,\"entries\":%llu,\"states\":[",s?",":"",s,entries[s]);unsigned n=0;
  for(unsigned i=0;i<nstates;i++)if(states[i].service==s){State *p=&states[i];fprintf(f,"%s{\"count\":%u,\"frame\":%u,\"controls\":[",n++?",":"",p->count,p->first);for(unsigned j=0;j<11;j++)fprintf(f,"%s%u",j?",":"",p->controls[j]);fprintf(f,"],\"args\":[");for(unsigned j=0;j<6;j++)fprintf(f,"%s%u",j?",":"",p->args[j]);fprintf(f,"]}");}
  fprintf(f,"],\"memory\":{\"reads\":%llu,\"writes\":%llu,\"outside_pages\":%llu,\"outside_pixels_and_background\":%llu,\"padding\":%llu,\"nonaperture\":%llu,\"operand_cross\":%llu,\"first_out_frame\":%u,\"first_out_address\":%u,\"copy_writes\":%llu,\"recent_writes\":%llu,\"prior_service_writes\":%llu,\"same_copy_writes\":%llu,\"foreign_latch\":%llu,\"recent_frame\":%u,\"recent_src\":%u,\"recent_dst\":%u,\"write_modes\":",m->reads,m->writes,m->outside,m->offscreen,m->padding,m->nonaperture,m->operand_cross,m->first_out,m->first_addr,m->copy_writes,m->recent,m->prior,m->same,m->foreign_latch,m->first_recent,m->first_src,m->first_dst);
  array(f,m->modes,4);fprintf(f,",\"read_modes\":");array(f,m->read_modes,2);fprintf(f,",\"rops\":");array(f,m->rops,4);fprintf(f,",\"map_masks\":");array(f,m->masks,16);fprintf(f,",\"bit_masks\":");array(f,m->bit_masks,256);fprintf(f,",\"wrap_steps\":%llu,\"initial_wrap\":%llu,\"first_wrap\":%u,\"latch_dependent_writes\":%llu,\"foreign_latch_any\":%llu,\"offscreen_frame\":%u,\"offscreen_address\":%u,\"address_generation_reductions\":%llu,\"first_reduce_frame\":%u,\"first_reduce_value\":%u,\"reduce_args\":[",m->wrap_steps,m->initial_wrap,m->first_wrap,m->dependent,m->foreign_any,m->off_frame,m->off_address,m->reductions,m->first_reduce,m->reduce_value);for(unsigned j=0;j<6;j++)fprintf(f,"%s%u",j?",":"",m->reduce_args[j]);fprintf(f,"],\"out_args\":[");for(unsigned j=0;j<6;j++)fprintf(f,"%s%u",j?",":"",m->out_args[j]);fprintf(f,"],\"out_pages\":[");for(unsigned j=0;j<4;j++)fprintf(f,"%s%u",j?",":"",m->out_pages[j]);fprintf(f,"],\"out_controls\":[");for(unsigned j=0;j<11;j++)fprintf(f,"%s%u",j?",":"",m->out_controls[j]);fprintf(f,"]");
  fprintf(f,"},\"copies\":{\"calls\":%llu,\"overlap\":%llu,\"interval_overlap\":%llu,\"recent\":%llu,\"prior\":%llu,\"same\":%llu,\"foreign\":%llu,\"first_overlap\":%u,\"first_recent\":%u,\"first_src\":%u,\"first_dst\":%u}}",q->calls,q->overlap,q->interval_overlap,q->recent,q->prior,q->same,q->foreign,q->first_overlap,q->first_recent,q->first_src,q->first_dst);
 }
 fprintf(f,"],\"collision_returns\":");array(f,returns,256);fprintf(f,",\"collision_reads\":%llu,\"probe_sites\":[",probe_reads[0]);unsigned n=0;for(unsigned i=0;i<65536;i++)if(probe_sites[i])fprintf(f,"%s[%u,%llu]",n++?",":"",i,probe_sites[i]);
 fprintf(f,"],\"levels\":[");for(unsigned i=0;i<nlevels;i++)fprintf(f,"%s[%u,%u,%u,%u,%u]",i?",":"",levels[i][0],levels[i][1],levels[i][2],levels[i][3],levels[i][4]);
 fprintf(f,"],\"sprite_dimensions\":[");n=0;for(unsigned i=0;i<65536;i++)if(sprite_dimensions[i])fprintf(f,"%s[%u,%u,%u]",n++?",":"",i,sprite_dimensions[i],dimension_first[i]);fprintf(f,"],\"blackening_wait_dac\":[");n=0;for(unsigned a=0;a<256;a++)for(unsigned b=0;b<3;b++)if(black_wait[a][b])fprintf(f,"%s[%u,%u,%llu,%u]",n++?",":"",a,b,black_wait[a][b],black_wait_first[a][b]);
 fprintf(f,"],\"geometry\":[");for(unsigned i=0;i<ngeometries;i++){Geometry *g=&geometries[i];fprintf(f,"%s{\"service\":%u,\"count\":%u,\"frame\":%u,\"pages\":[%u,%u,%u,%u],\"bytes\":%u,\"height\":%u,\"pitch\":%u}",i?",":"",g->service,g->count,g->first,g->pages[0],g->pages[1],g->pages[2],g->pages[3],g->bytes,g->height,g->pitch);}fprintf(f,"],\"tilemaps\":[");for(unsigned i=0;i<ntilemaps;i++){fprintf(f,"%s{\"frame\":%u,\"segment\":%u,\"offset\":%u,\"hex\":\"",i?",":"",tilemaps[i][0],tilemaps[i][1],tilemaps[i][2]);for(unsigned j=0;j<320;j++)fprintf(f,"%02x",tilebytes[i][j]);fprintf(f,"\"}");}fprintf(f,"],\"vga_segments\":[");n=0;for(unsigned i=0;i<65536;i++)if(segments[i])fprintf(f,"%s[%u,%llu,%u]",n++?",":"",i,segments[i],segment_first[i]);fprintf(f,"],\"sprite_metadata\":[");for(unsigned i=0;i<nsprite_meta;i++)fprintf(f,"%s[%u,%u,%u,%u]",i?",":"",sprite_meta[i][0],sprite_meta[i][1],sprite_meta[i][2],sprite_meta[i][3]);fprintf(f,"]}\n");fclose(f);
}
EXPORT int vc_selftest(void){
 ugh_devices_reset();vc_reset(0);Regs r={0};r.cs=GAME_SEG;r.ds=DATA_SEG;
 vc_enter(VC_SPRITE,&r);ugh_write(0xa0064,41);vc_leave(VC_SPRITE,&r,0);
 vc_enter(VC_SAVE,&r);ugh_devices.gc[5]=1;ugh_write(0xa0065,ugh_read(0xa0064));ugh_write(0xa0066,ugh_read(0xa0065));vc_leave(VC_SAVE,&r,0);
 if(copies[VC_SAVE].overlap!=1 || copies[VC_SAVE].recent!=1 || copies[VC_SAVE].prior!=1 || copies[VC_SAVE].same!=1 || copies[VC_SAVE].foreign)fail();
 vc_enter(VC_SAVE,&r);ugh_write(0xa00c8,0);vc_leave(VC_SAVE,&r,0);if(copies[VC_SAVE].foreign!=1)fail();
 vc_enter(VC_RECTANGLE,&r);wr16(0xa000,0xffff,0);rd8(0xa000,0xffff);rd8(0xa000,0);vc_leave(VC_RECTANGLE,&r,0);if(metric[VC_RECTANGLE].operand_cross!=1 || metric[VC_RECTANGLE].wrap_steps!=1)fail();
 enabled=0;return 1;
}
'''

def selected():
    import hostbuild
    units=hostbuild.selected_units();assert len(units)==41,(len(units),'new committed baseline must be reviewed')
    names=[]
    for u in units:
        if u['component'] in COMPONENTS:
            names += [(u['component'],n) for n in u['exports']]
    names += [('actor_render','actor_render_session_'+p) for p in ['GAME_ERASE','GAME_DRAW','GAME_OVERLAY']]
    names += [('session','c_LoadCurrentLevelState')]
    return units,names

def build():
    OUT.mkdir(parents=True,exist_ok=True);folder=OUT/'instrumented';folder.mkdir(exist_ok=True);units,names=selected()
    ids={n:i for i,(unit,n) in enumerate(names)}
    header='#ifndef CENSUS_H\n#define CENSUS_H\nvoid vc_enter(unsigned,Regs *);void vc_leave(unsigned,Regs *,int);void vc_read(uint32_t);void vc_write(uint32_t,uint8_t);void vc_operand(uint16_t,uint16_t,unsigned);\n'
    aliases={'SAVE':'c_SaveDrawPageBackground','RECTANGLE':'c_RestoreBackgroundRectangle','RAIN_RESTORE':'c_RestoreRainBackground','SAMPLE':'c_SamplePlayerCollisionPixels','SWAP':'c_SwapAndDisplayVgaPage','LEVEL':'c_LoadCurrentLevelState','SPRITE':'c_DrawTransparentSprite','BLACKEN':'c_BlackenVgaPalette','WAIT_ACTIVE':'c_WaitVerticalRetraceActive','TILEMAP':'c_DrawTileMap'}
    for key,name in aliases.items():header+=f'#define VC_{key} {ids[name]}\n'
    header+=f'#define VC_SERVICES {len(names)}\n#endif\n';(folder/'census.h').write_text(header);(folder/'census.c').write_text(CENSUS_C)
    exports=[n[2:] for u in units for n in u['exports']];sources=[]
    for p in sorted((ROOT/'c').iterdir()):
        if p.suffix not in ['.c','.h','.inc']:continue
        text=p.read_text()
        if p.suffix=='.c':
            for n in exports:text=re.sub(r'(\bEXPORT\s+int\s+)c_'+re.escape(n)+r'(?=\s*\()',r'\1l1_'+n,text)
        if p.name=='memory.c':
            text=text.replace('uint16_t o=(uint16_t)a;','vc_read(a);uint16_t o=(uint16_t)a;',1)
            text=text.replace('unsigned rotate=','vc_write(a,v);unsigned rotate=',1)
            text='#include "platform.h"\n#include "census.h"\n'+text
        if p.name=='ugh.h':
            at='/* Platform aperture access is physical,';text=text.replace(at,'void vc_operand(uint16_t,uint16_t,unsigned);\n'+at)
            text=text.replace('return ugh_read(lin(s,o));','vc_operand(s,o,1);return ugh_read(lin(s,o));')
            text=text.replace('uint32_t a=lin(s,o); uint16_t low','vc_operand(s,o,2);uint32_t a=lin(s,o); uint16_t low')
            text=text.replace('uint32_t a=lin(s,o),v=0;','vc_operand(s,o,4);uint32_t a=lin(s,o),v=0;')
            text=text.replace('{ ugh_write(lin(s,o),v); }','{ vc_operand(s,o,1);ugh_write(lin(s,o),v); }')
            text=text.replace('uint32_t a=lin(s,o); ugh_write(a,','vc_operand(s,o,2);uint32_t a=lin(s,o); ugh_write(a,')
            text=text.replace('uint32_t a=lin(s,o);\n    for(unsigned i=0;i<4;i++) ugh_write','vc_operand(s,o,4);uint32_t a=lin(s,o);\n    for(unsigned i=0;i<4;i++) ugh_write')
        target=folder/p.name;target.write_text(text)
        if p.suffix=='.c':sources.append(target)
    wrappers=[]
    for u in units:
        p=u['bridge'];text=p.read_text()
        text=re.sub(r'#include "([^"]+)"',lambda m:'#include "'+(p.parent/m[1]).resolve().as_posix()+'"' if (p.parent/m[1]).is_file() and not (p.parent/m[1]).resolve().is_relative_to(ROOT/'c') else m[0],text)
        for unit,n in names:
            if unit!=u['component']:continue
            b=function(text,n);renamed=re.sub(r'\b'+re.escape(n)+r'(?=\s*\()', 'observed_'+n,b,count=1)
            text=text.replace(b,renamed);wrappers.append(f'EXPORT int {n}(Regs *r){{vc_enter({ids[n]},r);int status=observed_{n}(r);vc_leave({ids[n]},r,status);return status;}}\n')
        if any(unit==u['component'] for unit,n in names):text='#include "platform.h"\n#include "census.h"\n'+text+'\n'+''.join(wrappers);wrappers=[]
        target=folder/p.name;target.write_text(text);sources.extend([u['native'],target])
    fallback=folder/'fallbacks.h';fallback.write_text('#include "ugh.h"\n'+''.join('int l1_'+n+'(Regs *);\n' for n in exports))
    dll=folder/'vga-census.dll';result=compile_c([*sources,folder/'census.c'],dll,[folder,ROOT/'native',ROOT/'native/bridge'],['-shared','-include',str(fallback),'-Wno-misleading-indentation'])
    result.update(services=names,revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),maintained_inputs=hashes([Path(__file__),*sorted((ROOT/'c').glob('*')),*sorted((ROOT/'native').rglob('*.[ch]')),*[ROOT/'metadata/closure'/f"{u['component']}.json" for u in units],ROOT/'tools/wholegame.py',ROOT/'tools/emu.py']))
    shutil.copyfile(Path(__file__),OUT/'driver-used.py')
    save(OUT/'build.json',result);return dll

def prepare():
    import contacts_reference
    contacts_reference.OUT=OUT/'reference';return contacts_reference.prepare_reference(local=False)

def reference(path,m):
    import wholegame
    key=wholegame.identity(path,m)
    candidates=[ROOT/'build/whole'/f'{path.stem}.ref.json',ROOT/'build/workers/close-stones-12/rain/random-rain.ref.json',OUT/'references'/f'{path.stem}.ref.json']
    for p in candidates:
        if p.exists():
            j=json.loads(p.read_text())
            if j.get('key')==key:return j,p
    raise RuntimeError('No current independent reference: '+str(path))

def one(name,mutation=0):
    import wholegame,nbuild
    prepare();path=ROOT/'verif/random_rain.txt' if name=='random-rain' else ROOT/'tests/scenarios'/f'{name}.txt'
    s=wholegame.scenario(path);s['name']=name;m,initial=wholegame.fixture(s);ref,refpath=reference(path,m)
    j=json.loads((OUT/'build.json').read_text())
    for n,h in j['maintained_inputs'].items():
        p=Path(n) if Path(n).is_absolute() else ROOT/n
        if hashlib.sha256(p.read_bytes()).hexdigest()!=h:raise RuntimeError('census build input changed; rebuild: '+n)
    dll=nbuild.load_l1(j['command'][j['command'].index('-o')+1]);dll.vc_reset.argtypes=[C.c_uint];dll.vc_reset(mutation)
    palette=dict(components=0,over63=0,maximum=0);original_record=wholegame.record
    def observe_record(ram,device,events,*args,**kwargs):
        for kind,port,width,value in struct.iter_unpack('<IIII',events):
            if kind==1 and port<=0x3c9<port+width:
                component=(value>>(8*(0x3c9-port)))&255;palette['components']+=1;palette['over63']+=component>63;palette['maximum']=max(palette['maximum'],component)
        return original_record(ram,device,events,*args,**kwargs)
    wholegame.record=observe_record;started=time.perf_counter()
    try:failure=wholegame.native(s,m,initial,dll,ref['frames'])
    finally:wholegame.record=original_record
    seconds=time.perf_counter()-started
    result=OUT/f'{name}-m{mutation}.json';dll.vc_dump.argtypes=[C.c_char_p];dll.vc_dump(str(result).encode());raw=json.loads(result.read_text());raw.update(scenario=name,mutation=mutation,seconds=seconds,matched_reference=not bool(failure),reference=str(refpath),reference_key=ref['key'],failure={k:v for k,v in failure.items() if k not in ['ram','device']})
    raw['build_receipt_sha256']=hashlib.sha256((OUT/'build.json').read_bytes()).hexdigest();raw['driver_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();raw['palette_components']=palette
    save(result,raw);print(('PASS' if not failure else 'DIVERGED'),name,'mutation',mutation,round(seconds,3),flush=True)
    if mutation<2:assert not failure
    return raw

def bounded(command,seconds=600):
    from windows_job import WindowsJob,ExtendedLimits
    start=time.perf_counter()
    with WindowsJob() as job:
        limits=ExtendedLimits();limits.basic.flags=0x2000|0x100|0x200;limits.process_memory=limits.job_memory=8*1024**3
        if not job.kernel.SetInformationJobObject(job.handle,9,C.byref(limits),C.sizeof(limits)):raise C.WinError(C.get_last_error())
        p=subprocess.Popen(command,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True);job.assign(p)
        try:out,_=p.communicate(timeout=seconds)
        except subprocess.TimeoutExpired:job.terminate();out,_=p.communicate();save(OUT/f'negative-{time.time_ns()}.json',dict(command=command,result='TIMEOUT',seconds=seconds,output=out));raise RuntimeError('census child timeout')
        print(out,flush=True)
        if p.returncode:save(OUT/f'negative-{time.time_ns()}.json',dict(command=command,result='ERROR',returncode=p.returncode,output=out));raise RuntimeError('census child failed')
    return time.perf_counter()-start

def selftest():
    import nbuild
    j=json.loads((OUT/'build.json').read_text());dll=nbuild.load_l1(j['command'][j['command'].index('-o')+1]);assert dll.vc_selftest()==1
    dll.vc_dump.argtypes=[C.c_char_p];dll.vc_dump(str(OUT/'selftest-observations.json').encode())
    save(OUT/'selftest.json',receipt([sys.executable,__file__,'--selftest'],[__file__,OUT/'build.json'],result='PASS',scope='Synthetic observer controls only: same-plane same-frame read-after-write; same-copy reuse and overlap; foreign inherited latch; aperture word crossing and access wrap. No synthetic observation is included in shipped totals.'))
    print('PASS synthetic observer controls',flush=True)

def decode_controls(c):
    return dict(write_mode=c[5]&3,read_mode=(c[5]>>3)&1,bit_mask=c[8],rotate=c[3]&7,function=(c[3]>>3)&3,
                set_reset=c[0],enable_set_reset=c[1],colour_compare=c[2],dont_care=c[7],map_mask=c[9],read_map=c[10],gc4=c[4],gc5=c[5])

def level_inventory(data):
    prepare();import cgen,dataprobe
    mz,_=cgen.read_symbols();maps,orders=dataprobe.levels(mz);byrecord={r['record']:dict(record=r['record'],title=r['title'],map=r['map'],orders=[],observed=[]) for r in orders}
    for row in orders:byrecord[row['record']]['orders'].append(dict(players=row['players'],number=row['number'],password=row['password']))
    rendered={}
    for scenario in data:
        for frame,players,index,record,water in scenario['levels']:
            key=f'{record:04X}';assert key in byrecord,key
            byrecord[key]['observed'].append(dict(scenario=scenario['scenario'],frame=frame,players=players,number=index+1,water=water))
        for row in scenario['tilemaps']:
            matches=[i for i in range(100) if maps[320*i:320*i+320]==bytes.fromhex(row['hex'])]
            assert matches,('unidentified map',scenario['scenario'],row['frame'])
            for i in matches:rendered.setdefault(i,[]).append(dict(scenario=scenario['scenario'],frame=row['frame']))
    result=dict(records=list(byrecord.values()),maps_rendered=rendered,covered_records=sum(bool(r['observed']) for r in byrecord.values()),total_records=len(byrecord),
      ordered_coverage={str(p):sorted({r['number'] for record in byrecord.values() for r in record['observed'] if r['players']==p}) for p in [1,2]},
      scope='A successful LoadCurrentLevelState identifies an initialized level. Demo/attract maps are recorded separately and do not establish simulation coverage of levels using those maps.')
    save(OUT/'levels.json',result);return result

def summarize():
    build=json.loads((OUT/'build.json').read_text());names=build['services'];paths=[OUT/(p.stem+'-m0.json') for p in sorted((ROOT/'tests/scenarios').glob('*.txt'))]+[OUT/'random-rain-m0.json']
    data=[json.loads(p.read_text()) for p in paths];assert len(data)==21 and all(d['matched_reference'] for d in data)
    assert all(d['unscoped_reads']==d['unscoped_writes']==0 for d in data),'unexpected VGA access outside the selected service wrappers'
    for d in data:assert d['build_receipt_sha256']==hashlib.sha256((OUT/'build.json').read_bytes()).hexdigest()
    default=tuple([0]*8+[255,15,0]);keys=sorted({tuple(s['controls']) for d in data for r in d['services'] for s in r['states']});keynames={k:'S'+str(i) for i,k in enumerate(keys)}
    services=[];tables=[]
    for sid,(unit,name) in enumerate(names):
        states={};total=0;metrics={};copies={};examples=[]
        for d in data:
            r=d['services'][sid];assert r['id']==sid and sum(s['count'] for s in r['states'])==r['entries'];total+=r['entries']
            for s in r['states']:
                key=tuple(s['controls']);v=states.setdefault(key,dict(state=keynames[key],controls=list(key),count=0,first=dict(scenario=d['scenario'],frame=s['frame'],args=s['args'])));v['count']+=s['count']
            for k,v in r['memory'].items():
                if k in ['reads','writes','outside_pages','outside_pixels_and_background','padding','nonaperture','operand_cross','copy_writes','recent_writes','prior_service_writes','same_copy_writes','foreign_latch','wrap_steps','initial_wrap','latch_dependent_writes','foreign_latch_any','address_generation_reductions']:metrics[k]=metrics.get(k,0)+v
                elif k in ['write_modes','read_modes','rops','map_masks','bit_masks']:
                    target=metrics.setdefault(k,[0]*len(v))
                    for i,n in enumerate(v):target[i]+=n
            for k,v in r['copies'].items():
                if k in ['calls','overlap','interval_overlap','recent','prior','same','foreign']:copies[k]=copies.get(k,0)+v
            if r['memory']['outside_pages']:examples.append(dict(kind='outside_pages',scenario=d['scenario'],frame=r['memory']['first_out_frame'],address=r['memory']['first_out_address'],controls=decode_controls(r['memory']['out_controls']),args=r['memory']['out_args'],pages=r['memory']['out_pages']))
            if r['memory']['address_generation_reductions']:examples.append(dict(kind='address_generation_reduction',scenario=d['scenario'],frame=r['memory']['first_reduce_frame'],raw_value=r['memory']['first_reduce_value'],args=r['memory']['reduce_args']))
            if r['copies']['recent']:examples.append(dict(kind='copy_current_frame',scenario=d['scenario'],frame=r['copies']['first_recent'],source=r['copies']['first_src'],destination=r['copies']['first_dst']))
        record=dict(component=unit,service=name,entries=total,classification='unreached' if not total else 'default only' if set(states)=={default} else 'non-default observed',states=list(states.values()),memory=metrics,copies=copies,examples=examples);services.append(record)
        tables+=['### '+unit+' / '+name,'',f'Entries: {total}. Complete entry tuple: **{record["classification"]}**.','', '| State | Count | First scenario | Frame | AX BX CX DX SI DI |','|---|---:|---|---:|---|']
        for s in states.values():tables.append('| '+s['state']+' | '+str(s['count'])+' | '+s['first']['scenario']+' | '+str(s['first']['frame'])+' | '+' '.join(f'{v:04X}' for v in s['first']['args'])+' |')
        if not states:tables.append('| none observed | 0 | — | — | no default-state claim |')
        tables.append('')
    levels=level_inventory(data)
    reply=[sum(d['collision_returns'][i] for d in data) for i in range(256)];probes=sum(reply);reads=sum(d['collision_reads'] for d in data);assert reads==10*probes
    low=json.loads((OUT/'low-bits.json').read_text());assert low['result']=='PASS'
    upper=json.loads((OUT/'water-physics-m2.json').read_text());assert not upper['matched_reference'],'upper-bit control must diverge'
    sprite_variants={};zero_dimensions=[];dac=[];segments={}
    for d in data:
        for sprite,dimensions,count,frame in d['sprite_metadata']:
            sprite_variants.setdefault(sprite,{}).setdefault(dimensions,dict(scenario=d['scenario'],frame=frame,count=0))['count']+=count
            if not dimensions&255 or not dimensions>>8:zero_dimensions.append(dict(scenario=d['scenario'],frame=frame,sprite=sprite,dimensions=dimensions,count=count))
        dac.extend(dict(scenario=d['scenario'],index=i,component=c,count=n,frame=f) for i,c,n,f in d['blackening_wait_dac'])
        for segment,count,frame in d['vga_segments']:
            segments.setdefault(str(segment),dict(count=0,scenario=d['scenario'],frame=frame))['count']+=count
    summary=dict(result='PASS',revision=build['revision'],scenarios=[dict(name=d['scenario'],entry=__import__('wholegame').scenario(ROOT/'verif/random_rain.txt' if d['scenario']=='random-rain' else ROOT/'tests/scenarios'/(d['scenario']+'.txt'))['entry'],frames=d['frames'],seconds=d['seconds'],levels=d['levels']) for d in data],states=[dict(id=keynames[k],raw=list(k),**decode_controls(k)) for k in keys],services=services,
      collision=dict(samples=probes,reads=reads,return_histogram=reply,lower_7_bits='XOR7F plus recomputed logical flags: all21 scenarios still match the independent frame/RAM/device/IO reference',upper_bit_control=dict(scenario='water-physics',boundary=upper['failure']['frame']),
        caller_scope='Four near-call sites in MovePlayerWithVgaCollisions consume SF/bit7. Native player_physics_reply stores the full sample; pp_horizontal_hit and pp_vertical_hit inspect sample&128. Exported sampler still returns the full OR byte; no contract is narrowed.'),levels=levels,
      address_scope='Physical VGA accesses only. Word operand crossing; per-invocation per-direction jumps exceeding32768 (access-stream wrap); signed initial sprite/rectangle envelope; and separately derived literal unsigned word reductions at sprite/rectangle initial address generation. Offscreen/padding and allocated-page-union counts are separate. These are measurements, not a universal absence proof.',
      sprite_metadata=dict(zero_dimensions=zero_dimensions,mutable_identities={str(k):v for k,v in sprite_variants.items() if len(v)>1}),dac_wait_states=dac,vga_operand_segments=segments,
      palette_components=dict(count=sum(d['palette_components']['components'] for d in data),over63=sum(d['palette_components']['over63'] for d in data),maximum=max(d['palette_components']['maximum'] for d in data)),
      unchanged='No certificates, native code, maintained tools or documents changed. Generated copies instrument all56 selected definitions, including direct calls and three actor pass adapters. Memory attribution is to deepest selected service; entry states count every wrapper.',
      default_definition='Device model reset: GC[0..7]=0, GC[8]=FF, sequencer map mask=F, read map=0. Read-map and map-mask variation is distinguished from inherited writer logic. This is the reconstructed backend reset model, not a measurement of a real BIOS register initialization.',
      inputs=hashes([__file__,OUT/'build.json',OUT/'run.json',OUT/'low-bits.json',OUT/'selftest.json',*paths,OUT/'water-physics-m2.json',ROOT/'build/workers/close-adlx-16/PORT_CONTRACT.md']))
    save(OUT/'census.json',summary)
    legend=['| ID | Write | Read | Bit mask | Rotate | Function | Set/reset | Enable | Compare | Care | Map mask | Read map |','|---|---:|---:|---|---:|---:|---|---|---|---|---|---:|']
    for k in keys:
        c=decode_controls(k);legend.append('| '+' | '.join([keynames[k],str(c['write_mode']),str(c['read_mode']),f'{c["bit_mask"]:02X}',str(c['rotate']),str(c['function']),f'{c["set_reset"]:02X}',f'{c["enable_set_reset"]:02X}',f'{c["colour_compare"]:02X}',f'{c["dont_care"]:02X}',f'{c["map_mask"]:X}',str(c['read_map'])])+' |')
    (OUT/'SERVICE_STATES.md').write_text('# Service entry state census\n\nFrames are completed flips before entry (zero-based); each state count is an entry count.\n\n'+'\n'.join(legend)+'\n\n'+'\n'.join(tables),encoding='utf-8')
    lines=['| Service | Read bytes | Write bytes | Outside allocated pages | Outside pixels/background | Offset reductions | Operand crossing | Access wraps |','|---|---:|---:|---:|---:|---:|---:|---:|']
    for r in services:
        m=r['memory']
        if m['reads'] or m['writes']:lines.append('| '+r['service']+' | '+' | '.join(str(m[k]) for k in ['reads','writes','outside_pages','outside_pixels_and_background','address_generation_reductions','operand_cross','wrap_steps'])+' |')
    (OUT/'ADDRESSES.md').write_text('# Address census\n\n'+'\n'.join(lines)+'\n\n'+json.dumps([dict(service=r['service'],examples=r['examples']) for r in services if r['examples']],indent=2)+'\n',encoding='utf-8')
    levelrows=['| Record | Title | Map | 1P / 2P number:password | Initialized by scenarios |','|---|---|---:|---|---|']
    for r in levels['records']:
        order=' / '.join(str(o['players'])+'P '+str(o['number'])+':'+o['password'] for o in r['orders'])
        observed=', '.join(sorted({o['scenario'] for o in r['observed']})) or '**not covered**'
        levelrows.append('| '+r['record']+' | '+r['title'].replace('|','/')+' | '+str(r['map'])+' | '+order+' | '+observed+' |')
    (OUT/'LEVELS.md').write_text('# Level coverage\n\n'+str(levels['covered_records'])+'/'+str(levels['total_records'])+' physical records initialized. A rendered attract map does not count as a simulated level.\n\n'+'\n'.join(levelrows)+'\n',encoding='utf-8')
    print('PASS summary:',len(services),'services,',len(keys),'distinct control tuples,',probes,'collision replies,',levels['covered_records'],'levels',flush=True)

def main():
    p=argparse.ArgumentParser();p.add_argument('--build',action='store_true');p.add_argument('--one');p.add_argument('--mutation',type=int,default=0);p.add_argument('--all',action='store_true');p.add_argument('--low-bits',action='store_true');p.add_argument('--selftest',action='store_true');p.add_argument('--summarize',action='store_true');a=p.parse_args();OUT.mkdir(parents=True,exist_ok=True)
    if a.build:print(build(),flush=True)
    if a.selftest:selftest()
    if a.one:one(a.one,a.mutation)
    if a.all or a.low_bits:
        names=[p.stem for p in sorted((ROOT/'tests/scenarios').glob('*.txt'))]+['random-rain'];assert len(names)==21
        mutation=1 if a.low_bits else 0
        for n in names:bounded([sys.executable,__file__,'--one',n,'--mutation',str(mutation)])
        save(OUT/('low-bits.json' if mutation else 'run.json'),receipt([sys.executable,__file__,'--low-bits' if mutation else '--all'],[__file__,ROOT/'tools/wholegame.py',ROOT/'tools/emu.py',OUT/'build.json',*sorted((ROOT/'tests/scenarios').glob('*.txt')),ROOT/'verif/random_rain.txt'],result='PASS',scenarios=names))
    if a.summarize:summarize()
if __name__=='__main__':main()
