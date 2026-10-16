"""A PlayStation disc image (.chd, or .bin / .cue with 2352-byte sectors): files of its ISO 9660
file system, and a .bin/.cue copy of it with some files replaced in place (their own sectors; a
file may grow up to the next file's first sector, its directory record follows).

Sectors are mode 2 form 1 (2048 bytes of data): a replaced sector keeps its header and subheader
and gets its EDC and ECC computed again.

From GranTurismo1-OverlayCheat (same author, GPL-3.0); files may grow within their room.
"""
import os
import re
import struct

from . import chd

SECTOR = chd.SECTOR


def _edc_table():
    t = []
    for i in range(256):
        c = i
        for _ in range(8):
            c = (c >> 1) ^ (0xD8018001 if c & 1 else 0)
        t.append(c)
    return t


_EDC_TABLE = _edc_table()


def edc(data):
    """CD-ROM EDC: CRC-32 with the polynomial 0xD8018001 (reflected), table driven."""
    crc = 0
    t = _EDC_TABLE
    for b in data:
        crc = t[(crc ^ b) & 0xFF] ^ (crc >> 8)
    return crc


def make_sector(original, data):
    """Mode 2 form 1 sector with the header and subheader of `original` and 2048 bytes of data."""
    s = bytearray(original[:24]) + bytearray(data.ljust(2048, b'\0')) + bytearray(SECTOR - 2072)
    struct.pack_into('<I', s, 2072, edc(s[16:2072]))
    chd.ecc_generate(s)
    return bytes(s)


class _Bin:
    """Raw image (first data track of a .bin, 2352-byte sectors)."""

    def __init__(self, path):
        self.f = open(path, 'rb')
        self.frames = os.path.getsize(path) // SECTOR

    def sector(self, lba):
        self.f.seek(lba * SECTOR)
        return self.f.read(SECTOR)


def bin_of_cue(cue):
    """The .bin a .cue names (first FILE line), next to the .cue."""
    text = open(cue, 'r', errors='replace').read()
    m = re.search(r'FILE\s+"([^"]+)"', text) or re.search(r'FILE\s+(\S+)', text)
    if not m:
        raise ValueError('%s: no FILE line' % cue)
    return os.path.join(os.path.dirname(os.path.abspath(cue)), m.group(1))


class Disc:
    def __init__(self, path):
        low = path.lower()
        if low.endswith('.chd'):
            self.c = chd.Chd(path)
        else:
            if low.endswith('.cue'):
                path = bin_of_cue(path)
            self.c = _Bin(path)
        self.path = path
        self.files = {}
        pvd = self.user_data(16)
        if pvd[1:6] != b'CD001':
            raise ValueError('%s: no ISO 9660 file system' % path)
        root = pvd[156:190]
        self._walk(struct.unpack_from('<I', root, 2)[0], struct.unpack_from('<I', root, 10)[0], '')

    def user_data(self, lba):
        s = self.c.sector(lba)
        if s[15] == 2:
            return s[24:24 + 2048]
        return s[16:16 + 2048]

    def _read(self, lba, count):
        return b''.join(self.user_data(lba + i) for i in range(count))

    def _walk(self, lba, size, path):
        d = self._read(lba, (size + 2047) // 2048)
        o = 0
        while o < len(d):
            n = d[o]
            if n == 0:
                o = (o // 2048 + 1) * 2048
                continue
            e_lba, = struct.unpack_from('<I', d, o + 2)
            e_size, = struct.unpack_from('<I', d, o + 10)
            flags, nl = d[o + 25], d[o + 32]
            name = d[o + 33:o + 33 + nl]
            if name not in (b'\0', b'\1'):
                nm = name.decode('ascii').split(';')[0]
                full = path + '/' + nm
                if flags & 2:
                    self._walk(e_lba, e_size, full)
                else:
                    self.files[full.lstrip('/')] = (e_lba, e_size, lba + (o // 2048), o % 2048)
            o += n

    @property
    def frames(self):
        return self.c.frames

    def read(self, name):
        lba, size = self.files[name][:2]
        return self._read(lba, (size + 2047) // 2048)[:size]

    def room(self, name):
        """Bytes a file can grow to without moving anything: up to the next file's first sector."""
        lba = self.files[name][0]
        after = min((f[0] for f in self.files.values() if f[0] > lba), default=self.frames)
        return (after - lba) * 2048

    def write_bin(self, path, replace, progress=None):
        """Write the .bin (raw 2352-byte sectors) and its .cue; replace = {file name: new bytes},
        each within its room (room())."""
        sectors = {}
        records = {}
        for name, data in replace.items():
            lba, size, dlba, doff = self.files[name]
            if len(data) > self.room(name):
                raise ValueError('%s: %d bytes, room for %d' % (name, len(data), self.room(name)))
            for i in range((len(data) + 2047) // 2048):
                sectors[lba + i] = data[i * 2048:(i + 1) * 2048].ljust(2048, b'\0')
            if len(data) != size:
                records.setdefault(dlba, []).append((doff, len(data)))
        for dlba, recs in records.items():
            d = bytearray(sectors.get(dlba) or self.user_data(dlba))
            for off, n in recs:
                struct.pack_into('<I', d, off + 10, n)
                struct.pack_into('>I', d, off + 14, n)
            sectors[dlba] = bytes(d)
        total = self.frames
        # written under a temporary name and renamed once complete: a half-written image never
        # looks like a finished one
        part = path + '.part'
        with open(part, 'wb') as f:
            for lba in range(total):
                raw = self.c.sector(lba)
                if lba in sectors:
                    raw = make_sector(raw, sectors[lba])
                f.write(raw)
                if progress and lba % 10000 == 0:
                    progress(lba, total)
        os.replace(part, path)
        base = os.path.basename(path)
        with open(os.path.splitext(path)[0] + '.cue', 'w', newline='\r\n') as f:
            f.write('FILE "%s" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n' % base)
