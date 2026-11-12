/* JUDGE: -mh -2
 * BIND: g_0236 0664:0236
 * BIND: g_0256 0664:0256
 * BIND: g_025C 0664:025C
 * BIND: g_026A 0664:026A
 * BIND: fn_0664_1331 0664:1331
 * BIND: fn_0664_20B9 0664:20B9
 * BIND: fn_0664_1A65 0664:1A65
 * BIND: g_0014 0664:0014
 * BIND: g_0238 0664:0238
 * BIND: g_023A 0664:023A
 * BIND: g_023E 0664:023E
 * OMF: F_LUDIV@ 0000:039D
 * BIND: g_000E 0664:000E
 * BIND: g_024E 0664:024E
 * BIND: g_0252 0664:0252
 * BIND: g_026E 0664:026E
 * BIND: g_0270 0664:0270
 * BIND: fn_0664_112B 0664:112B
 * BIND: fn_0664_205C 0664:205C
 * BIND: fn_0664_1C39 0664:1C39
 * BIND: fn_0664_1A89 0664:1A89
 * BIND: fn_0664_1E97 0664:1E97
 * BIND: fn_013B_001E 013B:001E
 * BIND: fn_013B_001F 013B:001F
 * BIND: fn_013B_001D 013B:001D
 * BIND: fn_013B_001C 013B:001C
 * OMF: F_PCMP@ 0000:0372
 * BIND: g_0212 0664:0212
 * BIND: g_0216 0664:0216
 * BIND: g_022E 0664:022E
 * BIND: g_0242 0664:0242
 * BIND: g_0246 0664:0246
 * BIND: g_0248 0664:0248
 * BIND: g_024A 0664:024A
 * BIND: g_024C 0664:024C
 * BIND: g_0258 0664:0258
 * BIND: g_025A 0664:025A
 * BIND: g_0266 0664:0266
 * BIND: g_026C 0664:026C
 * BIND: g_0274 0664:0274
 * BIND: g_0278 0664:0278
 * BIND: g_032C 0664:032C
 * BIND: g_03E0 0664:03E0
 * BIND: fn_0664_134E 0664:134E
 * BIND: fn_0664_1A37 0664:1A37
 * BIND: fn_0664_1211 0664:1211
 * BIND: fn_0664_14B1 0664:14B1
 * BIND: fn_013B_0020 013B:0020
 * BIND: fn_0664_1377 0664:1377
 * BIND: fn_0664_1503 0664:1503
 * BIND: g_021C 0664:021C
 * BIND: g_025E 0664:025E
 * OMF: F_PADD@ 0000:04ED
 * OMF: F_PINA@ 0000:054D
 * OMF: F_PADA@ 0000:0465
 * OMF: F_LXLSH@ 0000:0444
 * BIND: memset 0000:106B
 * BIND: g_0262 0664:0262
 * OMF: F_LXMUL@ 0000:035B
 * DATA: 1A37
 * All 23 C functions in one translation unit. See inventory.json for stubs and tables.
 */
int g_0000 = 0;
int g_0002 = 0;
extern int far g_0236, g_0256, g_025C, g_026A;
extern void far fn_0664_1331(void);
extern void far fn_0664_20B9(void);
extern void far fn_0664_1A65(void);

struct s_0014 {
    unsigned long f00;
    unsigned f04;
    unsigned char far *f06;
    unsigned f0A, f0C;
    unsigned f0E;
    unsigned char far *f10;
    unsigned f14, f16, f18, f1A;
    unsigned f1C;
    unsigned long f1E;
    unsigned f22, f24, f26, f28;
};
extern struct s_0014 far g_0014[];
extern unsigned far g_0238;
extern unsigned long far g_023A, g_023E;
/* Borland long-division helper is compiler emitted, not called in C. */

extern int far g_000E, g_026E, g_0270;
extern unsigned char huge * far g_024E;
extern unsigned long far g_0252;
extern void far fn_0664_112B(void);
extern int far fn_0664_205C(void);
extern void far fn_0664_1C39(unsigned);
extern int far fn_0664_1A89(void);
extern void far fn_0664_1E97(void);
extern void far fn_013B_001E(void), far fn_013B_001F(void);
extern unsigned char huge *far fn_013B_001D(unsigned long,unsigned long,unsigned long);
extern unsigned long far fn_013B_001C(unsigned long);
void fn_008A(void);
void fn_1768(int);
void fn_14BB(int);
int fn_0AA9(int, unsigned char far *, int);
int fn_0CFC(int,int);
int fn_1128(int);

extern unsigned far g_0216, g_022E, g_0258, g_025A, g_026C, g_0274;
extern unsigned far g_0246, g_0248, g_024A, g_024C;
extern unsigned long far g_0242;
extern unsigned char far * far g_0212, * far g_0266;
extern void far fn_0664_134E(void), far fn_0664_1A37(void);
extern void far fn_0664_1211(int,unsigned), far fn_0664_14B1(int);
extern void far fn_013B_0020(unsigned long, void far *, void far *);
struct s_0278 {
    unsigned char f00[12];
    unsigned f0C, f0E, f10, f12;
};
extern struct s_0278 far g_0278[], far g_032C[], far g_03E0[];
struct s_chunk {
    unsigned char tag[4];
    unsigned long size;
    unsigned f08;
    unsigned char f0A, f0B;
    unsigned f0C, f0E;
};

extern void far fn_0664_1377(int,void far *), far fn_0664_1503(int,unsigned);
extern unsigned char far * far g_021C, * far g_025E;

int fn_09CA(unsigned);
int fn_0176(unsigned, unsigned char huge *, unsigned, unsigned, unsigned);

extern void far *far memset(void far *,int,unsigned);
extern unsigned char far * far g_0262;

/* @0878:0003 */
int fn_0003(unsigned bits)
{
    int result = 0;
    int i;
    if (g_0000 && g_026A)
        fn_008A();
    fn_0664_112B();
    if ((bits & 2) && fn_0664_205C()) {
        result |= 2;
        for (i = 0; i < 9; i++) {
            fn_013B_001F();
            fn_013B_001E();
        }
        fn_0664_1C39(8000);
    }
    if ((bits & 1) && fn_0664_1A89())
        result |= 1;
    g_026A = result;
    g_0000 = 1;
    return result;
}

/* @0878:008A */
void fn_008A(void)
{
    if (g_0002 && !g_026A)
        return;
    g_0236 = 1;
    fn_0664_1331();
    if (g_026A & 2)
        fn_0664_20B9();
    if (g_026A & 1)
        fn_0664_1A65();
    g_026A = 0;
    g_0002 = 1;
}

/* @0878:00F5 */
unsigned long fn_00F5(unsigned long a, unsigned long b, unsigned long c)
{
    unsigned char huge *p;
    if ((p = fn_013B_001D(a,b,c)) == 0)
        return -1L;
    g_024E = p;
    g_0252 = fn_013B_001C(b);
    return g_0252;
}

/* @0878:0176 */
int fn_0176(unsigned x, unsigned char huge *p, unsigned volume, unsigned count, unsigned step)
{
    unsigned long length;
    unsigned rate;
    unsigned mode;
    unsigned char huge *start = p;
    if (!(g_026A & 2))
        return -1;
    if (x >= 8)
        return -1;
    if (*p++ != 'F' || *p++ != 'O' || *p++ != 'R' || *p++ != 'M')
        return -1;
    length = *p;
    p++;
    length = (length << 8) + *p;
    p++;
    length = (length << 8) + *p;
    p++;
    length = (length << 8) + *p;
    p++;
    while (*p++ != 'V' || *p++ != 'H' || *p++ != 'D' || *p++ != 'R')
        if (p > start + length)
            return -1;
    rate = (p[16] << 8) + p[17];
    if (p[19])
        mode = 3;
    else
        mode = 2;
    while (*p++ != 'B' || *p++ != 'O' || *p++ != 'D' || *p++ != 'Y')
        if (p > start + length)
            return -1;
    length = *p;
    p++;
    length = (length << 8) + *p;
    p++;
    length = (length << 8) + *p;
    p++;
    length = (length << 8) + *p;
    p++;
    if (length > 64000UL)
        return -1;
    fn_09CA(x);
    if (volume > 255)
        volume = 255;
    length &= 0xfffe;
    g_0014[x].f28 = 0;
    if (!count)
        g_0014[x].f28 |= 2;
    else
        g_0014[x].f04 = count;
    g_0014[x].f1C = volume;
    g_0014[x].f06 = (unsigned char far *)p;
    g_0014[x].f10 = (unsigned char far *)((unsigned long)p & 0xffff0000UL);
    g_0014[x].f0A = length;
    g_0014[x].f0C = mode;
    g_0014[x].f18 = mode & 1;
    g_0014[x].f26 = step;
    g_0014[x].f14 = length >> 1;
    if (mode & 2)
        g_0014[x].f1A = 127;
    else
        g_0014[x].f1A = 0;
    g_0014[x].f0E = rate;
    while (g_000E)
        ;
    g_026E++;
    g_0270 |= 1 << x;
    return 1;
}

/* @0878:0691 */
int fn_0691(unsigned x, unsigned char far *p, unsigned a, unsigned b)
{
    if (x < 8)
        return -1;
    fn_1768(x);
    if (fn_0AA9(x,p,b)) {
        g_0014[x].f1C = a;
        return 1;
    } else
        return -1;
}

/* @0878:06E4 */
int fn_06E4(unsigned x, unsigned index, unsigned a, unsigned b, unsigned c)
{
    unsigned char huge *p;
    if (x >= 12)
        return -1;
    p = g_024E + *(unsigned long huge *)g_024E + index * 12 + 8;
    if (p > g_024E + g_0252)
        return -1;
    p = g_024E + *(unsigned long huge *)p;
    if (p[0] == 'F' && p[1] == 'O' && p[2] == 'R' && p[3] == 'M' &&
        p[8] == '8' && p[9] == 'S' && p[10] == 'V' && p[11] == 'X')
        return fn_0176(x,p,a,b,c);
    else if (p[0] == 'A' && p[1] == 'D' && p[2] == 'L' && p[3] == 'X' &&
        p[8] == 'A' && p[9] == 'H' && p[10] == 'D' && p[11] == 'R')
        return fn_0691(x,(unsigned char far *)p,a,b);
    else
        return -1;
}

/* @0878:096B */
void fn_096B(void)
{
    int i;
    if ((g_026A & 2) && g_026E)
        fn_0664_1E97();
    if (g_026A & 1)
        for (i = 8; i < 12; i++)
            fn_0CFC(i,g_0014[i].f1C);
}

/* @0878:09CA */
int fn_09CA(unsigned x)
{
    if (x > 12)
        return -1;
    if (g_026A & 2) {
        if (x < 8) {
            if (!(g_0270 & (1 << x)))
                return -1;
            g_0014[x].f04 = 0;
            while (g_000E)
                ;
            if (g_0270 & (1 << x)) {
                g_0270 &= ~(1 << x);
                --g_026E;
            }
        } else
            fn_1768(x);
    }
    return 1;
}

/* @0878:0A70 */
unsigned long fn_0A70(unsigned long x)
{
    unsigned long y = x;
    ((unsigned char *)&y)[0] = ((unsigned char *)&x)[3];
    ((unsigned char *)&y)[1] = ((unsigned char *)&x)[2];
    ((unsigned char *)&y)[2] = ((unsigned char *)&x)[1];
    ((unsigned char *)&y)[3] = ((unsigned char *)&x)[0];
    return y;
}

/* @0878:0AA9 */
int fn_0AA9(int x, unsigned char far *p, int n)
{
    struct s_chunk far *a, far *b, far *c, far *d;
    if (!(g_026A & 1))
        return -1;
    if (x > 12 || x < 8)
        return -1;
    a = (struct s_chunk far *)p;
    p += 8;
    if (a->tag[0] != 'A' || a->tag[1] != 'D' || a->tag[2] != 'L' || a->tag[3] != 'X')
        return -1;
    b = (struct s_chunk far *)p;
    p += 8;
    if (b->tag[0] != 'A' || b->tag[1] != 'H' || b->tag[2] != 'D' || b->tag[3] != 'R')
        return -1;
    p += (unsigned)fn_0A70(b->size);
    c = (struct s_chunk far *)p;
    p += 8;
    if (c->tag[0] != 'I' || c->tag[1] != 'M' || c->tag[2] != 'A' || c->tag[3] != 'P')
        return -1;
    p += (unsigned)fn_0A70(c->size);
    d = (struct s_chunk far *)p;
    p += 8;
    if (d->tag[0] != 'T' || d->tag[1] != 'R' || d->tag[2] != 'C' || d->tag[3] != 'K')
        return -1;
    if (x != 12 && b->f0A > 9 - g_026C)
        return -1;
    if (x == 12) {
        g_0266 = (unsigned char far *)c + 8;
        g_0238 = b->f0E;
    }
    g_0014[x].f26 = 0x100;
    g_0014[x].f0A = fn_0A70(a->size) + (-34);
    g_0014[x].f22 = b->f0A;
    g_0014[x].f10 = p;
    g_0014[x].f06 = p;
    g_0014[x].f28 = 4;
    if (!n)
        g_0014[x].f28 |= 2;
    else
        g_0014[x].f04 = n;
    return 1;
}

/* @0878:0CFC */
int fn_0CFC(int x, int n)
{
    int i;
    unsigned old = g_0236;
    if (!(g_026A & 1))
        return -1;
    g_0274 = x;
    if (n & 0xff00)
        n = 255;
    if (x > 12 || x < 8 || !(g_0014[x].f28 & 4) || (g_0014[x].f28 & 1))
        return -1;
    g_0236 = 1;
    g_0014[x].f1C = n;
    if (x < 12) {
        fn_1768(x);
        g_026C += g_0014[x].f22;
        if (g_026C > 9) {
            g_026C -= g_0014[x].f22;
            return -1;
        }
        g_0014[x].f24 = 9 - g_026C;
    }
    for (i = g_0014[x].f24; i < g_0014[x].f24 + g_0014[x].f22; i++) {
        if (i < g_022E) {
            g_032C[i].f12 = g_0278[i].f12;
            fn_013B_0020(12, &g_0278[i], &g_032C[i]);
            g_032C[i].f0C = g_025A;
            g_032C[i].f0E = g_0278[i].f0E;
        }
        fn_0664_1211(i,0);
        fn_0664_14B1(i);
        g_0278[i].f0C = n;
    }
    g_0014[x].f28 |= 1;
    g_0014[x].f1E = g_023A + 3;
    g_0236 = old;
    return 1;
}

/* @0878:0F2D */
int fn_0F2D(int x)
{
    if (x > 12 || !(g_0014[x].f28 & 4))
        return -1;
    g_0014[x].f10 = g_0014[x].f06;
    return 1;
}

/* @0878:0F88 */
int fn_0F88(unsigned char far *p, int n, int a)
{
    if (!(g_026A & 1))
        return -1;
    fn_0664_1331();
    if (fn_0AA9(12,p,0) < 0)
        return -1;
    g_0256 = 1;
    if (!n) {
        fn_0CFC(12,a);
        fn_1128(a);
    } else {
        fn_0CFC(12,0);
        g_024A = 0;
        g_024C = a;
        g_0246 = 0;
        g_0248 = n;
        fn_0664_134E();
    }
    g_025A = a;
    g_023E = g_023A;
    return 1;
}

/* @0878:1059 */
int fn_1059(int n)
{
    int i;
    if (!(g_026A & 1))
        return -1;
    for (i = 8; i < 12; i++)
        fn_1768(i);
    if (!g_0256)
        return -1;
    fn_0664_1331();
    if (!n)
        g_0256 = 0;
    else {
        g_024C = 0;
        g_024A = g_025A;
        g_0246 = 0;
        g_0248 = n;
        fn_0664_134E();
        while (g_0258)
            ;
        g_0256 = 0;
        fn_0664_1331();
        g_0274 = 0;
        fn_0664_1A37();
    }
    return 1;
}

/* @0878:1128 */
int fn_1128(int n)
{
    int i;
    unsigned old = g_0274;
    if (!(g_026A & 1))
        return -1;
    if (!g_0256)
        return -1;
    g_025A = n;
    g_0274 = 12;
    for (i = 0; i < g_022E; i++)
        fn_0664_1211(i,n);
    g_0274 = old;
    return 1;
}

/* @0878:11AD */
int fn_11AD(unsigned a, unsigned b)
{
    unsigned char far *p = g_0212;
    unsigned long total = 0;
    unsigned long threshold;
    unsigned char code, op;
    unsigned char far * far *out = &g_025E;
    unsigned long delta;
    int i, j;
    if (!(g_026A & 1))
        return -1;
    if (!g_0256)
        return -1;
    memset(g_03E0,0,180);
    for (j = 0; j < g_022E; j++)
        g_03E0[j].f0C = g_025A;
    threshold = (unsigned long)a * g_0238;
    for (i = 0; i < 2; i++) {
        g_0242 = total;
        while (total < threshold) {
            code = *p++;
            op = code & 0xf0;
            if (p >= g_0212 + g_0216)
                return -1;
            switch (op) {
            case 0:
                delta = (((unsigned long)code << 8) + *p) << 7;
                p++;
                total += delta;
                break;
            case 0x10:
                if (!i)
                    g_03E0[code & 15].f12 = *(unsigned far *)p;
                p += 2;
                break;
            case 0x20:
                if (!i)
                    g_03E0[code & 15].f12 &= 0xdfff;
                break;
            case 0x30:
                if (!i)
                    g_03E0[code & 15].f0E = *p;
                p++;
                break;
            case 0x40:
                if (!i) {
                    fn_013B_0020(12,p,&g_03E0[code & 15]);
                    g_03E0[code & 15].f10 = 12;
                }
                p += 11;
                break;
            case 0x60:
                p += 2;
                break;
            case 0x70:
                p += *p;
                p++;
                break;
            default:
                delta = code & 0x7f;
                total += delta;
            }
        }
        *out = p;
        out = &g_0262;
        g_0242 = total - g_0242;
        threshold = (unsigned long)b * g_0238;
    }
    g_025C = 1;
    return 1;
}

/* @0878:1491 */
int fn_1491(void)
{
    if (g_0256)
        g_025C = 0;
    return 1;
}

/* @0878:14BB */
void fn_14BB(int x)
{
    int i, n, begin, end, k, tmp;
    n = g_0014[x].f22;
    begin = 9 - g_026C;
    end = begin + n;
    g_0014[x].f28 = 0;
    g_026C -= n;
    for (k = 8; k < 12; k++)
        if (k != x && (g_0014[k].f28 & 4) && g_0014[k].f24 < g_0014[x].f24)
            g_0014[k].f24 += n;
    if (g_0014[x].f24 > begin)
        for (i = g_0014[x].f24 + n - 1; i >= end; i--) {
            fn_013B_0020(12,&g_0278[i-n],&g_0278[i]);
            g_0278[i].f0C = g_0278[i-n].f0C;
            g_0278[i].f0E = g_0278[i-n].f0E;
            g_0278[i].f12 = g_0278[i-n].f12;
            g_0278[i].f10 = g_0278[i-n].f10;
            g_0274 = g_0278[i].f10;
            tmp = g_0278[i].f12;
            fn_0664_14B1(i);
            fn_0664_1377(i,&g_0278[i]);
            fn_0664_1503(i,tmp);
        }
    for (i = begin; i < end; i++) {
        if (i < g_022E) {
            g_0278[i].f0C = g_025A;
            g_0278[i].f0E = g_032C[i].f0E;
            g_0274 = 12;
            g_0278[i].f10 = 12;
            tmp = g_032C[i].f12;
            fn_0664_14B1(i);
            fn_0664_1377(i,&g_032C[i]);
            fn_0664_1503(i,g_032C[i].f12);
        } else {
            fn_0664_14B1(i);
            fn_0664_1211(i,0);
        }
    }
}

/* @0878:1768 */
void fn_1768(int x)
{
    int i;
    unsigned old = g_0236;
    if (!(g_026A & 1))
        return;
    if (x < 8 || x >= 12 || !(g_0014[x].f28 & 4) || !(g_0014[x].f28 & 1))
        return;
    {
        g_0236 = 1;
        g_0014[x].f28 = 0;
        g_0014[x].f10 = g_0014[x].f06;
        for (i = 0; i < g_0014[x].f22; i++)
            fn_0664_14B1(g_0014[x].f24 + i);
        fn_14BB(x);
        g_0236 = old;
    }
}

/* @0878:1852 */
int fn_1852(unsigned char far *p, int n, int a)
{
    int x = 8;
    int oldest = 8;
    if (!(g_026A & 1))
        return -1;
    for (; x < 12; x++)
        if (!(g_0014[x].f28 & 1)) {
            if (fn_0691(x,p,n,a) >= 0)
                fn_0CFC(x,n);
            return x;
        }
    for (x = 8; x < 12; x++)
        if (g_0014[x].f00 < g_0014[oldest].f00)
            oldest = x;
    x = oldest;
    fn_1768(x);
    if (!(g_0014[x].f28 & 1))
        if (fn_0691(x,p,n,a) >= 0)
            if (fn_0CFC(x,n) >= 0)
                return x;
    return -1;
}

/* @0878:1943 */
void fn_1943(void)
{
    int i;
    if (!(g_026A & 1))
        return;
    g_021C = g_025E;
    g_023E += g_0242;
    for (i = 0; i < g_022E; i++) {
        if (i < 9 - g_026C) {
            fn_013B_0020(20,&g_03E0[i],&g_0278[i]);
            fn_0664_1377(i,&g_0278[i]);
            fn_0664_1503(i,g_0278[i].f12);
        } else
            fn_013B_0020(20,&g_03E0[i],&g_032C[i]);
        fn_0664_1211(i,g_0278[i].f0C);
    }
}

/* @0878:1A50 */
unsigned long fn_1A50(void)
{
    return (g_023A - g_023E) / g_0238;
}


/* @0878:1A8E */
unsigned fn_1A8E(void)
{
    unsigned long total = 0;
    unsigned char code;
    unsigned char far *p, far *end;
    unsigned amount;
    if (!(g_026A & 1))
        return 0;
    if (!g_0256 || !g_0238)
        return 0;
    p = g_0212;
    end = p + g_0216;
    while (p < end) {
        code = *p++;
        switch (code >> 4) {
        case 0:
            amount = ((code << 8) + *p) << 7;
            p++;
            total += amount;
            break;
        case 1:
            p += 2;
            break;
        case 2:
            break;
        case 3:
            p++;
            break;
        case 4:
            p += 11;
            break;
        case 6:
            p += 2;
            break;
        case 7:
            p += *p;
            p++;
            break;
        default:
            amount = code & 0x7f;
            total += amount;
        }
    }
    return total / g_0238;
}


