#include "platform.h"
#include "../video_dos.h"
/* Hardware/ABI adapter; borrowed page and palette cells retain their owner. */
static void push(Regs *r,uint16_t x) {
    r->sp=(uint16_t)(r->sp-2); wr16(r->ss,r->sp,x);
}

static uint16_t pop(Regs *r) {
    uint16_t x=rd16(r->ss,r->sp); r->sp=(uint16_t)(r->sp+2); return x;
}

static uint16_t inc(Regs *r,uint16_t x) {
    uint16_t cf=r->flags&CF; x=add16(r,x,1,0); flag(r,CF,cf); return x;
}

static uint8_t dec8(Regs *r,uint8_t x) {
    uint8_t v=(uint8_t)(x-1); flag(r,OF,x==0x80);
    flag(r,AF,((x^v^1)&16)!=0); szp(r,v,8); return v;
}

static int call(Regs *r,uint16_t target,uint16_t ret) {
    return ugh_call_near(target,ret,r);
}

static int upload_range(Regs *r) {
    push(r,r->cx); push(r,r->ds); r->ds=r->es; r->si=r->di;
    set_ah(r,0); logic(r,0,8); r->cx&=255; logic(r,0,8); flag(r,IF,0);
    r->dx=0x3c8; set_al(r,(uint8_t)r->bx); platform_out(r->dx,1,(uint8_t)r->ax);
    r->dx=inc(r,r->dx);
    for(unsigned i=0;i<3;i++) r->si=add16(r,r->si,r->ax,0);
    uint8_t lo=(uint8_t)r->bx,hi=(uint8_t)(r->bx>>8);
    VideoPaletteRange range=video_palette_range(r->di,lo,hi,!!(r->flags&DF));
    uint8_t n=(uint8_t)(hi-lo);
    flag(r,CF,hi<lo); flag(r,OF,((hi^lo)&(hi^n)&128)!=0);
    flag(r,AF,((hi^lo^n)&16)!=0); szp(r,n,8);
    r->cx=n; inc(r,r->cx);r->cx=range.entries;
    do {
        for(unsigned j=0;j<3;j++) {
            set_al(r,rd8(r->ds,video_palette_advance(&range)));r->si=range.cursor;
            platform_out(r->dx,1,(uint8_t)r->ax);
        }
        r->cx--;
    } while(r->cx);
    flag(r,IF,1); r->ds=pop(r); r->cx=pop(r); return UGH_OK;
}

static void out_al(Regs *r,uint16_t port,uint8_t value) {
    r->dx=port; set_al(r,value); platform_out(port,1,value);
}

static int configure(Regs *r,int gameplay) {
    uint16_t start=gameplay?G(ConfigureVgaGameplayPages):G(ConfigureVgaPicturePages);
    VideoGeometry geometry=video_geometry(gameplay);
    wr16(r->cs,G(PlayfieldHeight),geometry.pages.height);wr16(r->cs,G(VgaPlaneCopyByteCount),geometry.pages.plane_copy_bytes);
    int status=call(r,G(BlackenVgaPalette),(uint16_t)(start+17));if(status) return status;
    for(unsigned ordinal=0;ordinal<7;ordinal++) {
        VideoRegisterSetting setting=video_mode_setting(ordinal,gameplay);uint16_t port=setting.device ? 0x3d4 : 0x3c4;
        out_al(r,port,setting.index);
        if(setting.read_previous) {
            r->dx=(uint16_t)(port+1);set_al(r,(uint8_t)platform_in(r->dx,1));uint8_t previous=(uint8_t)r->ax;
            set_al(r,(uint8_t)logic(r,previous&setting.mask,8));logic(r,(uint8_t)r->ax|setting.bits,8);set_al(r,video_register_value(setting,previous));platform_out(r->dx,1,(uint8_t)r->ax);
        } else out_al(r,(uint16_t)(port+1),setting.bits);
    }
    status=call(r,G(WaitNextVerticalRetrace),(uint16_t)(start+91)); if(status) return status;
    out_al(r,0x3c0,0x10); r->dx=inc(r,r->dx);
    set_al(r,(uint8_t)platform_in(r->dx,1)); set_al(r,(uint8_t)logic(r,video_attribute_mode((uint8_t)r->ax),8));
    r->dx=dec16(r,r->dx); platform_out(r->dx,1,(uint8_t)r->ax); out_al(r,r->dx,0x20);
    r->ax=logic(r,0,16); wr16(r->cs,G(FixedVgaPagePointer),geometry.pages.fixed);
    if(gameplay) r->ax=add16(r,r->ax,0xa88,0);
    wr16(r->cs,G(DisplayedVgaPagePointer),geometry.pages.displayed);
    if(gameplay) r->ax=add16(r,r->ax,0x4f80,0);
    wr16(r->cs,G(DrawPagePointer),geometry.pages.draw);
    if(gameplay) r->ax=add16(r,r->ax,0x4f80,0);
    wr16(r->cs,G(BackgroundPagePointer),geometry.pages.background);
    status=call(r,G(ClearAllVgaPlanes),(uint16_t)(start+(gameplay?136:133))); if(status) return status;
    return c_SwapAndDisplayVgaPage(r);
}

static int retrace(Regs *r,int active) {
    r->dx=0x3da;VideoRetrace wait={1000000,(uint8_t)active};
    for(;;) {
        set_al(r,(uint8_t)platform_in(r->dx,1));if(ugh_devices.error) return UGH_UNSUPPORTED;
        uint8_t delivered=(uint8_t)r->ax;set_al(r,(uint8_t)logic(r,delivered&8,8));
        int again=video_retrace_delivery(&wait,delivered);if(!again) return UGH_OK;if(again<0) return UGH_BUDGET;
    }
}
EXPORT int c_BlackenVgaPalette(Regs *r) {
    r->dx=0x3c8; set_al(r,(uint8_t)logic(r,0,8)); platform_out(r->dx,1,0);
    r->dx=inc(r,r->dx); r->cx=(uint16_t)((r->cx&255)|(video_blackening_batches()<<8));
    do {
        push(r,r->dx);
        int status=call(r,G(WaitNextVerticalRetrace),G(BlackenVgaPalette)+13); if(status) return status;
        r->dx=pop(r); flag(r,IF,0); set_al(r,(uint8_t)logic(r,0,8));
        r->cx=(uint16_t)((r->cx&0xff00)|video_blackening_entries());
        do {
            for(unsigned j=0;j<3;j++) platform_out(r->dx,1,(uint8_t)r->ax);
            r->cx=(uint16_t)((r->cx&0xff00)|dec8(r,(uint8_t)r->cx));
        } while(r->cx&255);
        flag(r,IF,1); r->cx=(uint16_t)((uint16_t)dec8(r,(uint8_t)(r->cx>>8))<<8);
    } while(r->cx>>8);
    return UGH_OK;
}

EXPORT int c_UploadBasePalette(Regs *r) {
    r->di=rd16(r->ds,D(BasePalettePointer)); r->es=rd16(r->ds,D(BasePalettePointer)+2);
    int status=call(r,G(WaitNextVerticalRetrace),G(UploadBasePalette)+7); if(status) return status;
    r->bx=0xff00; return upload_range(r);
}

EXPORT int c_DuplicateSourcePaletteHalves(Regs *r) {
    uint16_t saved_ds=r->ds;
    r->di=rd16(r->ds,D(BasePalettePointer));
    r->es=rd16(r->ds,(uint16_t)(D(BasePalettePointer)+2));
    r->si=rd16(r->ds,D(PaletteSourcePointer));
    r->ds=rd16(r->ds,(uint16_t)(D(PaletteSourcePointer)+2));
    VideoCopyCursor cursor=video_duplicate_begin(r->si,r->di,!!(r->flags&DF));r->cx=cursor.remaining;
    do {
        VideoDuplicateTransfer transfer=video_duplicate_transfer(&cursor);
        r->ax=rd16(r->ds,transfer.source);
        r->si=(uint16_t)(cursor.source+2*cursor.direction);
        wr16(r->es,transfer.destinations[0],r->ax);
        wr16(r->es,transfer.destinations[1],r->ax);
        video_duplicate_advance(&cursor);r->di=cursor.destination;
        r->cx=cursor.remaining;
    } while(r->cx);
    r->ds=saved_ds;
    return UGH_OK;
}

EXPORT int c_ScaleAndUploadFadedPalette(Regs *r) {
    VideoClearCursor cursor=video_scale_begin();r->bx=cursor.position;
    do {
        set_al(r,rd8(r->cs,(uint16_t)(G(BaseRgbPalette)+r->bx))); set_ah(r,0);
        VideoScaled scaled=video_palette_scale((uint8_t)r->ax,r->cx);
        r->ax=scaled.low; r->dx=scaled.high;
        flag(r,CF,r->dx!=0); flag(r,OF,r->dx!=0);
        wr8(r->cs,(uint16_t)(G(FadedRgbPalette)+r->bx),(uint8_t)(r->ax>>8));
        dec16(r,r->bx);video_scale_advance(&cursor);r->bx=cursor.position;
    } while(cursor.remaining);
    r->di=rd16(r->ds,D(FadedPalettePointer)); r->es=rd16(r->ds,D(FadedPalettePointer)+2);
    r->bx=0xd800;
    int status=call(r,G(WaitNextVerticalRetrace),G(ScaleAndUploadFadedPalette)+30); if(status) return status;
    return upload_range(r);
}

EXPORT int c_FadePaletteIn(Regs *r) {
    r->cx=logic(r,0,16);
    do {
        int st=call(r,G(ScaleAndUploadFadedPalette),G(FadePaletteIn)+5);
        if(st) return st;
        add16(r,r->cx,4,0);r->cx=video_fade_step(r->cx,0); sub16(r,r->cx,256,0);
    } while(video_fade_continue(r->cx,0));
    return UGH_OK;
}

EXPORT int c_FadePaletteOut(Regs *r) {
    push(r,r->cx); r->cx=256;
    do {
        int st=call(r,G(ScaleAndUploadFadedPalette),G(FadePaletteOut)+7);
        if(st) return st;
        sub16(r,r->cx,4,0);r->cx=video_fade_step(r->cx,1);
    } while(video_fade_continue(r->cx,1));
    r->cx=pop(r); return UGH_OK;
}

EXPORT int c_ClearAllVgaPlanes(Regs *r) {
    int status=call(r,G(EnableAllVgaWritePlanes),G(ClearAllVgaPlanes)+3); if(status) return status;
    r->es=0xa000; r->di=logic(r,0,16); r->ax=r->di; VideoClearCursor cursor=video_clear_begin(!!(r->flags&DF));r->cx=cursor.remaining;
    do {
        wr16(r->es,r->di,r->ax); video_clear_advance(&cursor);r->di=cursor.position;r->cx=cursor.remaining;
    } while(r->cx);
    return UGH_OK;
}

EXPORT int c_EnableAllVgaWritePlanes(Regs *r) {
    r->dx=0x3c4;
    set_al(r,2);
    platform_out(r->dx,1,(uint8_t)r->ax);
    uint16_t cf=r->flags&CF;
    r->dx=add16(r,r->dx,1,0);
    flag(r,CF,cf);
    set_al(r,video_all_planes());
    platform_out(r->dx,1,(uint8_t)r->ax);
    return UGH_OK;
}

EXPORT int c_ConfigureVgaGameplayPages(Regs *r) { return configure(r,1); }

EXPORT int c_ConfigureVgaPicturePages(Regs *r) { return configure(r,0); }

EXPORT int c_SwapAndDisplayVgaPage(Regs *r) {
    push(r,r->ax); push(r,r->bx); push(r,r->dx);
    VideoPages pages={0};pages.displayed=rd16(r->cs,G(DisplayedVgaPagePointer));pages.draw=rd16(r->cs,G(DrawPagePointer));video_swap(&pages);
    r->bx=pages.displayed;wr16(r->cs,G(DrawPagePointer),pages.draw);wr16(r->cs,G(DisplayedVgaPagePointer),pages.displayed);
    int status=call(r,G(WaitVerticalRetraceInactive),G(SwapAndDisplayVgaPage)+21); if(status) return status;
    r->dx=0x3d4; set_al(r,12); platform_out(r->dx,1,(uint8_t)r->ax);
    r->dx=inc(r,r->dx); set_al(r,(uint8_t)(r->bx>>8)); platform_out(r->dx,1,(uint8_t)r->ax);
    r->dx=dec16(r,r->dx); set_al(r,13); platform_out(r->dx,1,(uint8_t)r->ax);
    r->dx=inc(r,r->dx); set_al(r,(uint8_t)r->bx); platform_out(r->dx,1,(uint8_t)r->ax);
    r->dx=pop(r); r->bx=pop(r); r->ax=pop(r); return platform_frame_boundary(r);
}

EXPORT int c_UploadChunkyImageToVgaPlanes(Regs *r) {
    uint16_t ds=r->ds;
    r->di=rd16(GAME_SEG,G(DrawPagePointer)); r->es=rd16(GAME_SEG,G(DrawPagePointer)+2);
    r->cx=rd16(GAME_SEG,G(VgaPlaneCopyByteCount));
    r->si=rd16(ds,D(DecodedImagePointer)); r->ds=rd16(ds,D(DecodedImagePointer)+2);
    r->dx=0x3c4; set_al(r,2); platform_out(r->dx,1,2);
    /* INC DX flags survive all LODS/MOVS/LOOPs and the final MOV/OUT. */
    uint16_t cf=r->flags&CF;
    r->dx=add16(r,r->dx,1,0); flag(r,CF,cf);
    VideoChunkyCursor cursor=video_chunky_begin(r->si,r->di,r->cx,!!(r->flags&DF));
    do {
        set_al(r,video_chunky_mask(&cursor));platform_out(r->dx,1,(uint8_t)r->ax);
        uint8_t pixel=rd8(r->ds,cursor.source);r->si=(uint16_t)(cursor.source+cursor.direction);
        if(cursor.plane<3) set_al(r,pixel);
        wr8(r->es,cursor.destination,pixel);video_chunky_advance(&cursor);r->di=cursor.destination;r->cx=(uint16_t)cursor.remaining;
    } while(cursor.remaining);
    set_al(r,video_all_planes()); platform_out(r->dx,1,(uint8_t)r->ax); r->ds=ds;
    return UGH_OK;
}

EXPORT int c_WaitNextVerticalRetrace(Regs *r) {
    int first=video_retrace_level(0,0);
    int status=call(r,first ? G(WaitVerticalRetraceActive) : G(WaitVerticalRetraceInactive),G(WaitVerticalRetraceActive));
    if(status) return status;
    return video_retrace_level(0,1) ? c_WaitVerticalRetraceActive(r) : c_WaitVerticalRetraceInactive(r);
}

EXPORT int c_WaitRetraceCount(Regs *r) {
    push(r,r->dx);
    do {
        int st=call(r,G(WaitNextVerticalRetrace),G(WaitRetraceCount)+4);
        if(st) return st;
        r->cx=video_wait_decrement(r->cx);
    } while(r->cx);
    r->dx=pop(r); return UGH_OK;
}

EXPORT int c_WaitThroughVerticalRetrace(Regs *r) {
    int first=video_retrace_level(1,0);
    int status=call(r,first ? G(WaitVerticalRetraceActive) : G(WaitVerticalRetraceInactive),G(WaitVerticalRetraceInactive));
    if(status) return status;
    return video_retrace_level(1,1) ? c_WaitVerticalRetraceActive(r) : c_WaitVerticalRetraceInactive(r);
}

EXPORT int c_WaitVerticalRetraceActive(Regs *r) {
    int st=platform_service_point_at(SERVICE_RETRACE,r->cs,G(WaitVerticalRetraceActive),r);
    return st?st:retrace(r,video_retrace_level(0,1));
}

EXPORT int c_WaitVerticalRetraceInactive(Regs *r) { return retrace(r,video_retrace_level(0,0)); }

EXPORT int c_WaitForInputOrRetraceTimeout(Regs *r) {
    push(r,r->dx);VideoTimeout wait={0};uint16_t reply=0;
    for(;;) {
        VideoWaitAction action=video_timeout_next(&wait,reply);int status=0;
        switch(action) {
        case VIDEO_WAIT_INITIAL_SCAN:status=call(r,G(PollKeyboardScanChange),G(loc_449B));break;
        case VIDEO_WAIT_SERVICE:status=platform_service_point_at(SERVICE_IO,r->cs,G(loc_449B),r);break;
        case VIDEO_WAIT_SCAN:
            status=call(r,G(PollKeyboardScanChange),G(loc_449B)+3);if(status) return status;
            logic(r,r->ax>>8,8);reply=r->ax>>8;break;
        case VIDEO_WAIT_SAMPLE:
            push(r,r->cx);status=call(r,G(SampleJoystickAxesAndButtons),G(loc_449B)+14);if(status) return status;
            r->cx=pop(r);reply=!(r->flags&ZF);break;
        case VIDEO_WAIT_RETRACE:status=call(r,G(WaitNextVerticalRetrace),G(loc_449B)+23);break;
        case VIDEO_WAIT_COUNT:r->cx=video_wait_decrement(r->cx);reply=r->cx;break;
        case VIDEO_WAIT_DONE_DEFAULT:r->ax=0x39;logic(r,r->cx,16);r->dx=pop(r);return UGH_OK;
        default:logic(r,r->cx,16);r->dx=pop(r);return UGH_OK;
        }
        if(status) return status;
    }
}
EXPORT int c_InstallDosCriticalErrorFailHandler(Regs *r) {
    uint16_t ds=r->ds; r->ds=r->cs; r->ax=0x2524; r->dx=G(FailDosCriticalError);
    int status=platform_interrupt(0x21,r); r->ds=ds; return status;
}

EXPORT int c_FailDosCriticalError(Regs *r) {
    flag(r,IF,1);
    set_al(r,video_critical_error_result());
    return UGH_OK;
}

