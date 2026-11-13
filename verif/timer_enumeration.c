static unsigned long checks,handle_checks,fragment_checks;
static void seed(unsigned count) {
    for(unsigned i=0;i<152;i++) words[i]=(uint16_t)(i*719+15);
    wr16(DATA_SEG,D(LastActiveTimerSlotOffset),(uint16_t)((count-1)*2));
    for(unsigned i=0;i<16;i++) {
        wr16(DATA_SEG,D(TimerSlotOffsetByHandle)+i*2,i<count ? (uint16_t)(i*2) : 32768);
        wr16(DATA_SEG,D(TimerHandleBySlot)+i*2,(uint16_t)(i*2));
    }
}
static void handles(void) {
    for(unsigned count=1;count<=16;count++) {
        seed(count);TimerState state;project(&state);
        for(unsigned handle=0;handle<65536;handle++) {
            int expected=!(handle&1) && handle<count*2 ? (int)(handle/2) : -1;
            CHECK(timer_handle_slot(&state,(uint16_t)handle)==expected,"all handles canonical map");
            handle_checks++;
        }
        for(unsigned handle=0;handle<32;handle+=2) for(unsigned mapping=0;mapping<65536;mapping++) {
            state.by_handle[handle/2]=(uint16_t)mapping;
            int expected=!(mapping&1) && mapping<count*2 ? (int)(mapping/2) : -1;
            CHECK(timer_handle_slot(&state,(uint16_t)handle)==expected,"all mapping values");
            handle_checks++;
        }
    }
}
static void operations(void) {
    static const uint32_t values[]={0,1,65535,65536,65537,2147483647u,2147483648u,4294967295u};
    for(unsigned count=1;count<=16;count++) for(unsigned h=0;h<count;h++)
        for(unsigned v=0;v<8;v++) {
            seed(count);TimerState state;project(&state);
            Regs old={0};old.ds=DATA_SEG;old.ax=(uint16_t)(h*2);
            old.bx=(uint16_t)values[v];old.cx=(uint16_t)(values[v]>>16);
            timer_set_interval(&state,old.ax,values[v]);
            CHECK(l1_SetTimerCallbackInterval(&old)==0,"setter status");compare(&state,0);checks++;
            if(count>=2) {
                seed(count);project(&state);old.ax=(uint16_t)(h*2);
                uint16_t result=timer_remove(&state,old.ax);
                CHECK(l1_RemoveTimerCallback(&old)==0 && old.ax==result,"remove status and identity");
                compare(&state,0);checks++;
            }
            if(count<16) {
                seed(count);project(&state);
                /* Every possible free-search stopping position, including holes. */
                for(unsigned j=h+1;j<=count;j++) {
                    wr16(DATA_SEG,D(TimerSlotOffsetByHandle)+j*2,0);state.by_handle[j]=0;
                }
                wr16(DATA_SEG,D(TimerSlotOffsetByHandle)+h*2,32768);state.by_handle[h]=32768;
                old.ax=S(TickAdlxPlayback);old.dx=SOUND_SEG;
                old.bx=(uint16_t)values[v];old.cx=(uint16_t)(values[v]>>16);
                int result=timer_register(&state,TIMER_ADLX_PLAYBACK,values[v]);
                CHECK(l1_RegisterTimerCallback(&old)==0 && old.ax==result,"registration identity");
                CHECK(timer_callback(state.slots[count].target)==TIMER_ADLX_PLAYBACK,"registered typed callback");
                compare(&state,1);checks++;
            }
        }
    for(unsigned count=1;count<=4;count++) for(unsigned mask=0;mask<(1u<<count);mask++)
        for(unsigned v=0;v<8;v++) for(unsigned q=0;q<8;q++) {
            seed(count);
            for(unsigned i=0;i<count;i++) {
                wr16(DATA_SEG,D(TimerRemainingLowBySlot)+i*2,(uint16_t)values[v]);
                wr16(DATA_SEG,D(TimerRemainingHighBySlot)+i*2,(uint16_t)(values[v]>>16));
                wr16(DATA_SEG,D(TimerCallbackDueBySlot)+i*2,mask&(1u<<i) ? 32769 : 1);
            }
            wr16(DATA_SEG,D(NextPitQuantumLow),(uint16_t)values[q]);
            wr16(DATA_SEG,D(NextPitQuantumHigh),(uint16_t)(values[q]>>16));
            TimerState state;project(&state);Regs old={0};old.ds=DATA_SEG;
            TimerTickScratch scratch=timer_account_tick(&state);
            CHECK(l1_account(&old)==0 && old.ax==scratch.low && old.dx==scratch.high,"tick scratch");
            compare(&state,0);checks++;
            for(unsigned i=count;i;i--) {
                TimerCallback callback;
                int due=!!(rd16(DATA_SEG,D(TimerCallbackDueBySlot)+(i-1)*2)&32768);
                CHECK(timer_take_due(&state,i-1,&callback)==due,"due selection");
                if(due) wr16(DATA_SEG,D(TimerCallbackDueBySlot)+(i-1)*2,0);
            }
            compare(&state,0);
        }
}
static void fragments(void) {
    /* All 4^6 patterns of six callback fragments for three slots, all three
     * removable identities; inactive words fixed. Exercises overlapping writes. */
    for(unsigned pattern=0;pattern<4096;pattern++) for(unsigned h=0;h<3;h++) {
        seed(3);unsigned value=pattern;
        for(unsigned word=0;word<6;word++) {
            wr16(DATA_SEG,D(TimerCallbackOffsetBySlot)+word*2,(uint16_t)(value%4));value/=4;
        }
        TimerState state;project(&state);Regs old={0};old.ds=DATA_SEG;old.ax=(uint16_t)(h*2);
        uint16_t result=timer_remove(&state,old.ax);
        CHECK(l1_RemoveTimerCallback(&old)==0 && old.ax==result,"fragment remove");
        compare(&state,0);fragment_checks++;
    }
}
int main(void) {
    handles();operations();fragments();
    printf("{\"handle_classifications\":%lu,\"operation_cases\":%lu,\"fragment_cases\":%lu}\n",
           handle_checks,checks,fragment_checks);
    return 0;
}
