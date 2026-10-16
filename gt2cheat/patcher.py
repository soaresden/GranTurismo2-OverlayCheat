"""Patch Gran Turismo 2 (PAL SCES-12380) with the overlay cheat: SCES_123.80 (start-up stub and
resident block, entry point) and GT2.OVL (the lap clock store of the race overlay). Every word
changed is checked first: on another game or version, nothing is written.
"""
import gzip
import struct
import zlib

from . import game, payload


class PatchError(Exception):
    pass


def _j(addr):
    return 0x08000000 | ((addr >> 2) & 0x03FFFFFF)


def _word(data, base, addr):
    return struct.unpack_from('<I', data, addr - base)[0]


def patch_exe(exe):
    """SCES_123.80 with the stub and the block in its overlay area and its entry on the stub."""
    if exe[:8] != b'PS-X EXE':
        raise PatchError('%s: not a PlayStation executable' % game.EXE)
    pc, _, taddr, tsize = struct.unpack_from('<IIII', exe, 0x10)
    if pc == game.STUB_ADDR:
        raise PatchError('%s: already patched' % game.EXE)
    if pc != game.GAME_ENTRY or taddr != game.TEXT_ADDR:
        raise PatchError('%s: not the expected Gran Turismo 2 PAL executable' % game.EXE)
    text = bytearray(exe[0x800:])
    for addr, want in ((game.PAD_LUI, game.PAD_LUI_WORD), (game.PAD_ADDIU, game.PAD_ADDIU_WORD),
                       (game.DRAW_SITES[0], game.DRAW_WORD), (game.DRAW_SITES[1], game.DRAW_WORD)):
        if _word(text, taddr, addr) != want:
            raise PatchError('%s: 0x%08X is not the expected code' % (game.EXE, addr))
    code = payload.STUB + payload.BLOCK
    o = game.STUB_ADDR - taddr
    if any(text[o:o + len(code)]):
        raise PatchError('%s: the room for the cheat is not free' % game.EXE)
    text[o:o + len(code)] = code
    head = bytearray(exe[:0x800])
    struct.pack_into('<I', head, 0x10, game.STUB_ADDR)
    return bytes(head) + bytes(text)


def _regz(original, data):
    """data gzipped with the original's header (name, time), as the disc's files are."""
    flg = original[3]
    end = 10
    if flg & 4:
        end += 2 + struct.unpack_from('<H', original, 10)[0]
    if flg & 8:
        end = original.index(b'\0', end) + 1
    c = zlib.compressobj(9, zlib.DEFLATED, -15)
    body = c.compress(data) + c.flush()
    head = bytearray(original[:end])
    head[3] = flg & 8
    return bytes(head) + body + struct.pack('<II', zlib.crc32(data) & 0xFFFFFFFF, len(data) & 0xFFFFFFFF)


def patch_ovl(ovl):
    """GT2.OVL with the race overlay's clock store jumping to tick_store."""
    head, = struct.unpack_from('<I', ovl, 0)
    n = head // 8
    if head % 8 or not 1 <= n <= 16:
        raise PatchError('%s: unexpected table' % game.OVL)
    toc = [struct.unpack_from('<II', ovl, 8 * i) for i in range(n)]
    off, size = toc[0]
    race = bytearray(gzip.decompress(ovl[off:off + size]))
    at = game.TICK_STORE - game.TEXT_ADDR
    words = struct.unpack_from('<II', race, at)
    target = _j(payload.SYMBOLS['tick_store'])
    if words == (target, 0):
        raise PatchError('%s: already patched' % game.OVL)
    if words != game.TICK_WORDS:
        raise PatchError('%s: the race overlay is not the expected one' % game.OVL)
    struct.pack_into('<II', race, at, target, 0)
    parts = [_regz(ovl[off:off + size], bytes(race))] + [ovl[o:o + s] for o, s in toc[1:]]
    out = bytearray(head)
    table = []
    for p in parts:
        table.append((len(out), len(p)))
        out += p
        out += b'\0' * (-len(out) % 4)
    for i, (o, s) in enumerate(table):
        struct.pack_into('<II', out, 8 * i, o, s)
    # the original ends with its last entry (no padding after it)
    last_o, last_s = table[-1]
    return bytes(out[:last_o + last_s])


def patch_disc(src, dst, progress=None):
    from . import disc
    d = disc.Disc(src)
    for name in (game.EXE, game.OVL):
        if name not in d.files:
            raise PatchError('%s not on the disc: not the Gran Turismo 2 Simulation disc' % name)
    files = {game.EXE: patch_exe(d.read(game.EXE)), game.OVL: patch_ovl(d.read(game.OVL))}
    for name, data in files.items():
        if len(data) > d.room(name):
            raise PatchError('%s: %d bytes, room for %d' % (name, len(data), d.room(name)))
    d.write_bin(dst, files, progress)
    return files
