/*
 * Gran Turismo 2 (PS1, PAL SCES-12380) - overlay cheat menu.
 *
 * Resident code, copied to 0x8000F000 by the start-up stub of SCES_123.80 (src/stub.S), which
 * then calls cheat_boot. cheat_boot changes three places of the game's resident code (the same
 * in every overlay: menus, races, licences):
 *
 *   pad_hook   in place of the game's pad update callback (once per vertical blank): reads
 *              port 1, runs the menu while SELECT is held (or once opened with L1 + R1 + L2 +
 *              R2, until START) and hides the pad from the game meanwhile, then calls the
 *              game's update;
 *   draw_hook  the two calls that draw a frame's ordering table: once the GPU has drawn it,
 *              draws the menu over it with GP0 writes (TILE primitives, 5x7 font from font.py).
 *
 * The race overlay of GT2.OVL is patched on the disc: the store of the lap clock jumps to
 * tick_store (src/start.S), which skips it in a licence test while FREEZE TIMER is on, once
 * the clock has left 0 (a licence never ends otherwise).
 *
 * Copyright (C) 2026 soaresden - GPL-3.0-or-later.
 */
#include "font.h"
#include "game.h"

typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;

#define MAGIC 0x32544743u            /* "CGT2": the state is initialised */
#define SHOW 8                       /* polls with SELECT held before the menu appears */
#define TAPLEN 2                     /* polls of SELECT given back to the game after a short tap */

/* pad bits once inverted (1 = pressed) */
#define B_SELECT 0x0001
#define B_START 0x0008
#define B_UP 0x0010
#define B_RIGHT 0x0020
#define B_DOWN 0x0040
#define B_LEFT 0x0080
#define B_L2 0x0100
#define B_R2 0x0200
#define B_L1 0x0400
#define B_R1 0x0800
#define B_TRIANGLE 0x1000
#define B_CIRCLE 0x2000
#define B_CROSS 0x4000
#define B_SQUARE 0x8000
#define B_SHOULDERS (B_L1 | B_R1 | B_L2 | B_R2)

/* the state, at STATE (outside the block): tick_store reads `freeze` at STATE + 4 */
struct g {
    u32 magic;
    u8 freeze;                                   /* FREEZE TIMER on */
    u8 line;                                     /* 0 = FREEZE TIMER, 1 = MONEY */
    u8 step;                                     /* money step = 10^step */
    u8 pad_;
    u32 prev;                                    /* buttons of the previous poll */
    u8 hold;                                     /* polls with SELECT held (max 255) */
    u8 used;                                     /* another button pressed during this hold */
    u8 tap;                                      /* polls of SELECT still to give the game */
    u8 rep;                                      /* auto-repeat of LEFT / RIGHT */
    u8 vis;                                      /* menu shown */
    u8 shx, shy;                                 /* font pixel = 1 << shx by 1 << shy */
    u8 open;                                     /* opened with L1 + R1 + L2 + R2 (stays) */
};
/* the base address in a register that GCC cannot rebuild (it would redo lui/ori each time) */
static inline struct g *G_(void)
{
    struct g *g;
    __asm__("" : "=r"(g) : "0"(STATE));
    return g;
}
#define G G_()

#define GP0 (*(volatile u32 *)0x1F801810)
#define GPUSTAT (*(volatile u32 *)0x1F801814)
#define DMA2_CHCR (*(volatile u32 *)0x1F8010A8)

void pad_hook(void);
void draw_hook(void *ot);

/* ---------------------------------------------------------------- boot */

static u32 jal(void *f)
{
    return 0x0C000000 | (((u32)f >> 2) & 0x03FFFFFF);
}

/* returns 0 when the game is not the expected one (nothing changed) */
int cheat_boot(void)
{
    struct g *g = G;
    u32 *lui = (u32 *)PAD_LUI, *addiu = (u32 *)PAD_ADDIU;
    u32 *d0 = (u32 *)DRAW_SITE0, *d1 = (u32 *)DRAW_SITE1;
    u32 a = (u32)pad_hook;

    if (*lui != PAD_LUI_WORD || *addiu != PAD_ADDIU_WORD || *d0 != DRAW_WORD || *d1 != DRAW_WORD)
        return 0;
    if (g->magic != MAGIC) {
        g->magic = MAGIC;
        g->freeze = g->line = 0;
        g->step = 3;
    }
    g->prev = 0;
    g->hold = g->used = g->tap = g->rep = g->vis = g->open = 0;
    /* lui $v0, %hi(pad_hook) / addiu $v0, $v0, %lo(pad_hook) */
    *lui = 0x3C020000 | (((a + 0x8000) >> 16) & 0xFFFF);
    *addiu = 0x24420000 | (a & 0xFFFF);
    *d0 = *d1 = jal(draw_hook);
    return 1;
}

/* ---------------------------------------------------------------- input */

static u32 pow10(int n)
{
    u32 v = 1;
    while (n--)
        v *= 10;
    return v;
}

static void menu(struct g *g, u32 b, u32 pr)
{
    volatile u32 *m = (volatile u32 *)MONEY;
    u32 v = *m, step;

    if (pr & (B_UP | B_DOWN))
        g->line ^= 1;
    if (!g->line) {
        if (pr & (B_LEFT | B_RIGHT | B_CROSS | B_CIRCLE))
            g->freeze ^= 1;
        return;
    }
    if ((pr & B_R1) && g->step < 7)
        g->step++;
    if ((pr & B_L1) && g->step)
        g->step--;
    if (v > MONEY_MAX)
        v = MONEY_MAX;
    if (pr & B_TRIANGLE)
        v = MONEY_MAX;
    if (pr & B_SQUARE)
        v = 0;
    if (b & (B_LEFT | B_RIGHT)) {
        if (pr & (B_LEFT | B_RIGHT))
            g->rep = 0;
        else if (++g->rep < 10)                   /* held: repeat every other poll after 10 */
            goto done;
        else
            g->rep = 8;
        step = pow10(g->step);
        if (b & B_RIGHT)
            v = v > MONEY_MAX - step ? MONEY_MAX : v + step;
        else
            v = v < step ? 0 : v - step;
    }
done:
    if (v != *m)
        *m = v;
}

void pad_hook(void)
{
    struct g *g = G;
    u8 *p = (u8 *)PAD_BUF;
    u32 b, pr;

    if ((p[1] & 0xF0) == 0x80)                    /* multitap: its slot A */
        p += 2;
    if (p[0]) {                                   /* no pad on port 1 */
        g->hold = g->vis = g->open = 0;
        goto game;
    }
    /* libpad does not always refresh the buffer between two calls (Beetle PSX / mednafen: not
       every vertical blank): the low nibble of the type byte (which the game does not read, it
       takes the type from the high one) is set once read; still set means the same data as
       last time, already handled (and masked) */
    if ((p[1] & 0x0F) == 0x0F)
        goto game;
    p[1] |= 0x0F;
    b = ~(p[2] | p[3] << 8) & 0xFFFF;
    pr = b & ~g->prev;
    g->prev = b;
    /* L1 + R1 + L2 + R2 together: the menu opens and stays (for emulators where SELECT is the
       hotkey button, Batocera / RetroArch: while it is held, the game gets no input); START or
       the same buttons again close it */
    if ((b & B_SHOULDERS) == B_SHOULDERS && (pr & B_SHOULDERS)) {
        g->open ^= 1;
        g->vis = g->open;
        p[2] = p[3] = 0xFF;
        goto game;
    }
    if (g->open) {
        /* the shoulders that opened it are still held, not new presses: no step change */
        if (pr & B_START)
            g->open = g->vis = 0;
        else
            menu(g, b, pr);
        p[2] = p[3] = 0xFF;                       /* the game sees no button */
        goto game;
    }
    if (b & B_SELECT) {
        if (g->hold < 255)
            g->hold++;
        if (b & ~B_SELECT)
            g->used = 1;
        if (g->hold >= SHOW) {
            g->vis = 1;
            menu(g, b, pr);
        }
        p[2] = p[3] = 0xFF;                       /* the game sees no button */
        goto game;
    }
    if (g->hold && !g->used && g->hold < SHOW)    /* a short tap: SELECT is the game's */
        g->tap = TAPLEN;
    g->hold = g->used = g->vis = 0;
    if (g->tap) {
        g->tap--;
        p[2] &= ~B_SELECT;
    }
game:
    ((void (*)(void))PAD_UPDATE)();
}

/* ---------------------------------------------------------------- drawing */

static void gp0(u32 w)
{
    while (!(GPUSTAT & 0x04000000))
        ;
    GP0 = w;
}

static void rect(struct g *g, int x, int y, int w, int h, u32 cmd)
{
    gp0(cmd);
    GP0 = (u32)(y << g->shy) << 16 | (u32)(x << g->shx);
    GP0 = (u32)(h << g->shy) << 16 | (u32)(w << g->shx);
}

static int text(struct g *g, int x, int y, const u8 *str, u32 col)
{
    for (; *str != 0xFF; str++, x += 6) {
        const u8 *f = FONT + *str * 5;
        int c, r;
        for (c = 0; c < 5; c++)
            for (r = 0; r < 7; r++)
                if (f[c] >> r & 1)
                    rect(g, x + c, y + r, 1, 1, col);
    }
    return x + 6;
}

static void number(struct g *g, int x, int y, u32 v, u32 col, int plus)
{
    u8 buf[16];
    int i = 15, n = 0;

    buf[15] = 0xFF;
    do {
        if (n == 3) {
            buf[--i] = G_COMMA;
            n = 0;
        }
        buf[--i] = v % 10;
        v /= 10;
        n++;
    } while (v);
    if (plus)
        buf[--i] = G_PLUS;
    text(g, x, y, buf + i, col);
}

#define WHITE 0x60FFFFFF
#define GREY 0x60A0A0A0
#define YELLOW 0x6000FFFF                         /* GPU colours are 0xBBGGRR */
#define CYAN 0x60FFE040
#define PW 116                                    /* panel, in font pixels */
#define PH 41

void draw_hook(void *ot)
{
    struct g *g = G;
    u32 stat, c1, c2;
    int x, y, n;

    ((void (*)(void *))DRAW_OT)(ot);
    if (!g->vis)
        return;
    /* the frame is drawn (the DMA of the ordering table is over): the menu goes over it */
    for (n = 0; (DMA2_CHCR & 0x01000000) && n < 0x200000; n++)
        ;
    stat = GPUSTAT;
    g->shx = (stat >> 18) & 1;                    /* 512 / 640 wide: 2 GPU pixels per font pixel */
    g->shy = (stat >> 19) & 1;                    /* 480 lines */
    x = (stat & 0x10000) ? 368 : (stat >> 17) & 1 ? 320 : 256;   /* width in font pixels */
    x = (x - PW) / 2;
    y = 30;

    gp0(0xE1000000 | (stat & 0x79F) | 0x400);     /* semi-transparency 0 (B/2 + F/2), draw everywhere */
    gp0(0xE6000000);                              /* no mask bit */
    rect(g, x, y, PW, PH, 0x62000000);            /* half-dark panel */

    c1 = g->line ? WHITE : YELLOW;
    c2 = g->line ? YELLOW : WHITE;
    text(g, x + 10, y + 3, S_TITLE, CYAN);
    text(g, x + 4, y + 12 + 9 * g->line, S_ARROW, YELLOW);
    text(g, text(g, x + 10, y + 12, S_FREEZE, c1), y + 12, g->freeze ? S_ON : S_OFF, c1);
    number(g, text(g, x + 10, y + 21, S_MONEY, c2), y + 21, *(volatile u32 *)MONEY, c2, 0);
    number(g, text(g, x + 10, y + 30, S_STEP, GREY), y + 30, pow10(g->step), GREY, 1);

    gp0(0xE1000000 | (stat & 0x7FF) | ((stat >> 4) & 0x800));   /* the game's draw mode again */
    gp0(0xE6000000 | ((stat >> 11) & 3));
}
