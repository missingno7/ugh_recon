/* Test-only write/effect-driven projector. Live state is read at cold import and
 * explicit effect/publication hooks, NEVER to repair the world at a boundary.
 * The platform model is the producer under test, not reimplemented here.
 */
#include "platform.h"
#include "world.h"
#include "observer.h"
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <windows.h>

extern unsigned host_frame;
typedef unsigned long long U64;
typedef struct Binding {
    uint32_t address;size_t offset;unsigned width,native_width,shift,kind,domain,owner;
    const char *name;
} Binding;
typedef struct IdentityEntry {unsigned domain;uint16_t word;const char *label;} IdentityEntry;
typedef struct ServiceBinding {size_t historical,offset,width;unsigned group;const char *name;} ServiceBinding;
#include "bindings.inc"
#include "services.inc"
#define N_BINDINGS (sizeof bindings/sizeof bindings[0])
#define N_IDENTITIES (sizeof identities/sizeof identities[0])
#define N_SERVICES (sizeof service_bindings/sizeof service_bindings[0])
#define N_OWNERS (sizeof owner_names/sizeof owner_names[0])
#define DEVICE_BYTES offsetof(Devices,count)

static GameWorld world;
static ServiceState services;
static uint8_t baseline[UGH_MEM_SIZE],output[UGH_MEM_SIZE];
static uint8_t journal[UGH_MEM_SIZE],dirty[UGH_MEM_SIZE],typed_touched[UGH_MEM_SIZE];
static uint32_t last_frame[UGH_MEM_SIZE],binding_at[UGH_MEM_SIZE],id_by_word[6][65536];
static uint8_t device_baseline[DEVICE_BYTES],device_output[DEVICE_BYTES];
static ProjectEvent *events,*actual_events;static size_t nevents,nactual,event_capacity,actual_capacity;
static U64 writes[N_OWNERS],typed_bytes[N_OWNERS],touched[N_OWNERS],journal_writes,journal_bytes;
static U64 service_calls,service_changed_bytes,publication_calls,publication_bytes,write_hash=1469598103934665603ull;
static unsigned enabled,baseline_verified,boundaries,terminal_boundaries,controls_done,control_frame;
static uint32_t control_offsets[5];static unsigned control_kinds[5];
static const char *control_targets[5];
static U64 effect_hash=1469598103934665603ull;

static void fail(const char *why){fprintf(stderr,"projector: %s at frame %u\n",why,host_frame);fflush(stderr);ExitProcess(87);}
static int observed(uint32_t a){return a<0x80000u || a>=0x8fefeu;}
static uint32_t mask(unsigned width){return width==4?0xffffffffu:(1u<<(8*width))-1u;}
static uint32_t identity_word(const ProjectIdentity *p){
    if(!p->token)return p->unresolved;
    if(p->token>=N_IDENTITIES)fail("identity token out of registry");
    return identities[p->token].word;
}
static uint32_t value(const Binding *b){
    const uint8_t *at=(const uint8_t*)&world+b->offset;uint32_t v=0;
    if(b->kind)return identity_word((const ProjectIdentity*)at);
    if(b->native_width==1)v=*at;
    else if(b->native_width==2){uint16_t part;memcpy(&part,at,2);v=part;}
    else memcpy(&v,at,4);
    return (v>>b->shift)&mask(b->width);
}
static void assign(const Binding *b,uint32_t raw){
    uint8_t *at=(uint8_t*)&world+b->offset;
    if(b->kind){ProjectIdentity *p=(ProjectIdentity*)at;p->token=id_by_word[b->domain][raw&65535u];p->unresolved=(uint16_t)raw;return;}
    uint32_t old=0;
    if(b->native_width==1)old=*at;
    else if(b->native_width==2){uint16_t part;memcpy(&part,at,2);old=part;}
    else memcpy(&old,at,4);
    uint32_t bits=mask(b->width)<<b->shift;old=(old&~bits)|((raw<<b->shift)&bits);
    if(b->native_width==1)*at=(uint8_t)old;
    else if(b->native_width==2){uint16_t part=(uint16_t)old;memcpy(at,&part,2);}
    else memcpy(at,&old,4);
}
static void byte_write(uint32_t a,uint8_t v){
    if(a>=UGH_MEM_SIZE)fail("RAM write outside observation storage");
    write_hash=(write_hash^a)*1099511628211ull;write_hash=(write_hash^v)*1099511628211ull;
    uint32_t ident=binding_at[a];
    if(ident){const Binding *b=&bindings[ident-1];unsigned shift=8*(a-b->address);uint32_t old=value(b);
        assign(b,(old&~(255u<<shift))|((uint32_t)v<<shift));writes[b->owner]++;
        if(!typed_touched[a]){typed_touched[a]=1;touched[b->owner]++;}
    }else{
        journal_writes++;if(!dirty[a]){dirty[a]=1;journal_bytes++;}journal[a]=v;last_frame[a]=host_frame;
    }
}
void pr_write(uint32_t a,uint8_t v){
    if(!enabled)return;
    if(a>=0xa0000u && a<0xb0000u){
        for(unsigned p=0;p<4;p++)services.video.plane[p][(uint16_t)a]=ugh_devices.plane[p][(uint16_t)a];
    }else byte_write(a,v);
}
void pr_pointer_write(const uint8_t *p,uint8_t v){
    uintptr_t at=(uintptr_t)p,base=(uintptr_t)ugh_mem;
    if(enabled && at>=base && at-base<UGH_MEM_SIZE)byte_write((uint32_t)(at-base),v);
}
void pr_publish(const uint8_t *p,unsigned count){
    if(!enabled){return;}publication_calls++;publication_bytes+=count;
    for(unsigned i=0;i<count;i++)pr_pointer_write(p+i,p[i]);
}
void pr_vga_read(uint32_t a){if(enabled && a>=0xa0000u && a<0xb0000u)memcpy(services.video.latch,ugh_devices.latch,4);}
void pr_services(unsigned groups){
    if(!enabled){return;}service_calls++;
    for(unsigned i=0;i<N_SERVICES;i++){
        const ServiceBinding *b=&service_bindings[i];if(!(b->group&groups))continue;
        const uint8_t *source=(const uint8_t*)&ugh_devices+b->historical;uint8_t *destination=(uint8_t*)&services+b->offset;
        for(size_t j=0;j<b->width;j++)if(source[j]!=destination[j]){
            service_changed_bytes++;destination[j]=source[j];effect_hash=(effect_hash^((b->historical+j)*257u+source[j]))*1099511628211ull;
        }
    }
}
static void append(ProjectEvent **p,size_t *n,size_t *capacity,ProjectEvent event){
    if(*n==*capacity){size_t cap=*capacity?*capacity*2:4096;if(cap>16777216)fail("event journal capacity");
        void *next=realloc(*p,cap*sizeof(ProjectEvent));if(!next)fail("event journal allocation");*p=next;*capacity=cap;}
    (*p)[(*n)++]=event;
}
void pr_event(unsigned kind,uint16_t port,unsigned width,uint32_t v){
    if(enabled)append(&events,&nevents,&event_capacity,(ProjectEvent){kind,port,width,v});
}
static void serialize(void){
    memcpy(output,baseline,sizeof output);
    for(uint32_t a=0;a<UGH_MEM_SIZE;a++)if(dirty[a])output[a]=journal[a];
    for(unsigned i=0;i<N_BINDINGS;i++){
        const Binding *b=&bindings[i];uint32_t v=value(b);
        for(unsigned j=0;j<b->width;j++)output[b->address+j]=(uint8_t)(v>>(8*j));
    }
    memcpy(device_output,device_baseline,sizeof device_output);
    for(unsigned i=0;i<N_SERVICES;i++){
        const ServiceBinding *b=&service_bindings[i];
        if(b->historical+b->width<=DEVICE_BYTES)memcpy(device_output+b->historical,(uint8_t*)&services+b->offset,b->width);
    }
}
typedef struct Difference {unsigned kind;uint32_t offset;} Difference;
static Difference compare(void){
    serialize();
    for(uint32_t a=0;a<UGH_MEM_SIZE;a++)if(observed(a) && output[a]!=ugh_mem[a])return (Difference){1,a};
    const uint8_t *device=(const uint8_t*)&ugh_devices;
    for(uint32_t a=0;a<DEVICE_BYTES;a++)if(device_output[a]!=device[a])return (Difference){2,a};
    if(services.error!=ugh_devices.error)return (Difference){2,offsetof(Devices,error)};
    if(nevents!=nactual)return (Difference){3,(uint32_t)(nevents<nactual?nevents:nactual)};
    for(size_t i=0;i<nevents;i++)if(memcmp(events+i,actual_events+i,sizeof(ProjectEvent)))return (Difference){3,(uint32_t)i};
    return (Difference){0,0};
}
static void require_control(unsigned control,Difference difference){
    if(!difference.kind)fail("vacuous corruption control");
    control_offsets[control]=difference.offset;control_kinds[control]=difference.kind;
}
static void controls(void){
    if(controls_done || !getenv("PR_CONTROLS") || !host_frame)return;
    uint32_t stale=UGH_MEM_SIZE;unsigned identity=N_BINDINGS;
    uint32_t scratch=(uint32_t)UGH_S_ZERO_IceDecodeWorkspace*16u;
    for(uint32_t a=scratch;a<scratch+65536u;a++)if(observed(a) && dirty[a] && last_frame[a]<host_frame){stale=a;break;}
    for(unsigned i=0;i<N_BINDINGS;i++)if(bindings[i].kind && bindings[i].owner==2){
        ProjectIdentity *p=(ProjectIdentity*)((uint8_t*)&world+bindings[i].offset);
        if(p->token && identities[p->token].word && identities[p->token].word!=65535){identity=i;break;}
    }
    size_t second=1;while(second<nevents && !memcmp(events,events+second,sizeof(ProjectEvent)))second++;
    if(stale==UGH_MEM_SIZE || identity==N_BINDINGS || second==nevents)return;
    control_targets[0]="session.level";control_targets[1]="unclassified retained ICE-workspace byte";
    control_targets[2]="services.video.map_mask";control_targets[3]="cumulative ordered event journal";
    control_targets[4]=bindings[identity].name;
    uint16_t level=world.session.level;world.session.level^=1;require_control(0,compare());world.session.level=level;
    journal[stale]^=1;require_control(1,compare());journal[stale]^=1;
    services.video.map_mask^=1;require_control(2,compare());services.video.map_mask^=1;
    ProjectEvent temp=events[0];events[0]=events[second];events[second]=temp;require_control(3,compare());
    temp=events[0];events[0]=events[second];events[second]=temp;
    ProjectIdentity *p=(ProjectIdentity*)((uint8_t*)&world+bindings[identity].offset);
    identities[p->token].word^=1;require_control(4,compare());identities[p->token].word^=1;
    if(compare().kind){fail("corruption control not restored");}controls_done=1;control_frame=host_frame;
}
void pr_boundary(Regs *r,const char *terminal){
    if(!enabled)fail("boundary before cold import");
    for(unsigned i=0;i<ugh_devices.count;i++){
        const IoEvent *e=ugh_devices.log+i;append(&actual_events,&nactual,&actual_capacity,(ProjectEvent){e->kind,e->port,e->size,e->value});
    }
    Difference difference=compare();
    if(difference.kind){fprintf(stderr,"difference kind=%u offset=%u\n",difference.kind,difference.offset);fail("serialization differs");}
    /* The stack is excluded from RAM but the exposed return scalar is not. */
    uint32_t at=(uint32_t)r->ss*16+r->sp;
    if(output[at]!=ugh_mem[at] || output[at+1]!=ugh_mem[at+1])fail("return identity scalar differs");
    boundaries++;terminal_boundaries+=terminal!=NULL;controls();
}
static void dump(void){
    if(!enabled)return;
    if(getenv("PR_CONTROLS") && !controls_done)fail("controls never reached eligible boundary");
    const char *path=getenv("PR_RECEIPT");if(!path)return;FILE *f=fopen(path,"wb");if(!f)fail("receipt open");
    U64 baseline_bytes=0,unclassified=0,excluded=0;
    for(uint32_t a=0;a<UGH_MEM_SIZE;a++){
        if(!observed(a)){excluded++;continue;}
        if(!binding_at[a]){if(dirty[a])unclassified++;else baseline_bytes++;}
    }
    fprintf(f,"{\"baseline_verified\":%s,\"boundaries\":%u,\"terminal_boundaries\":%u,\"last_frame\":%u,\"owners\":[",baseline_verified?"true":"false",boundaries,terminal_boundaries,host_frame);
    for(unsigned i=0;i<N_OWNERS;i++)fprintf(f,"%s{\"name\":\"%s\",\"typed_bytes\":%llu,\"write_deliveries\":%llu,\"touched_bytes\":%llu}",i?",":"",owner_names[i],typed_bytes[i],writes[i],touched[i]);
    fprintf(f,"],\"baseline_unclassified_bytes\":%llu,\"journal_observed_bytes\":%llu,\"excluded_stack_bytes\":%llu,\"journal_total_bytes\":%llu,\"journal_write_deliveries\":%llu,\"write_hash\":\"%016llx\",\"effect_hash\":\"%016llx\",\"service_effect_cuts\":%llu,\"service_changed_bytes\":%llu,\"publication_calls\":%llu,\"publication_bytes\":%llu,\"events\":%llu,\"actual_events\":%llu,\"controls\":[",baseline_bytes,unclassified,excluded,journal_bytes,journal_writes,write_hash,effect_hash,service_calls,service_changed_bytes,publication_calls,publication_bytes,(U64)nevents,(U64)nactual);
    for(unsigned i=0;i<5;i++)fprintf(f,"%s{\"detected\":%s,\"frame\":%u,\"difference_kind\":%u,\"offset\":%u,\"target\":\"%s\"}",i?",":"",controls_done?"true":"false",control_frame,control_kinds[i],control_offsets[i],controls_done?control_targets[i]:"");
    fprintf(f,"]}\n");fclose(f);
}
void pr_verify_baseline(void){
    const char *path=getenv("PR_BASELINE");if(!path)fail("baseline path missing");FILE *f=fopen(path,"rb");if(!f)fail("baseline open");
    if(fread(baseline,1,sizeof baseline,f)!=sizeof baseline || fgetc(f)!=EOF){fail("baseline shape");}fclose(f);
    if(memcmp(baseline,ugh_mem,sizeof baseline))fail("independently relocated baseline differs before fixture setup");
    baseline_verified=1;
}
void pr_import(void){
    if(!baseline_verified)fail("cold import before independent baseline check");
    for(unsigned i=1;i<N_IDENTITIES;i++){
        if(identities[i].domain>=6 || id_by_word[identities[i].domain][identities[i].word])fail("identity registry duplicate");
        id_by_word[identities[i].domain][identities[i].word]=i;
    }
    /* Full-domain word identity roundtrip, independently of any fixture value. */
    for(unsigned dom=0;dom<6;dom++)for(unsigned w=0;w<65536;w++){
        ProjectIdentity p={id_by_word[dom][w],(uint16_t)w};if(identity_word(&p)!=w)fail("identity codec roundtrip");
    }
    for(unsigned i=0;i<N_BINDINGS;i++){
        const Binding *b=&bindings[i];uint32_t v=0;
        for(unsigned j=0;j<b->width;j++){
            uint32_t a=b->address+j;if(a>=UGH_MEM_SIZE || binding_at[a])fail("overlapping canonical bindings");binding_at[a]=i+1;
            v|=(uint32_t)ugh_mem[a]<<(8*j);typed_bytes[b->owner]++;
        }
        assign(b,v);if(value(b)!=v)fail("cold field codec");
    }
    for(uint32_t a=0;a<UGH_MEM_SIZE;a++)if(!binding_at[a] && baseline[a]!=ugh_mem[a]){
        dirty[a]=1;journal[a]=ugh_mem[a];last_frame[a]=host_frame;journal_bytes++;
    }
    memcpy(device_baseline,&ugh_devices,sizeof device_baseline);
    enabled=1;pr_services(255);
    if(ugh_devices.count)fail("cold fixture unexpectedly contains log events");
    if(atexit(dump))fail("atexit");
}
