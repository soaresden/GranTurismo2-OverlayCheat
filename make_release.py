"""Make the patches of a release (needs gt2cheat/payload.py: python build.py).

    python make_release.py --src "Gran Turismo 2 (Europe) (Disc 2).chd"

patch/Gran Turismo 2 (Europe) (Disc 2) [Overlay Cheat].ppf: the changed bytes only (SCES_123.80,
GT2.OVL and the directory sector), and the .xdelta (xdelta3); both are made from build/orig.bin
and build/cheat.bin (written there, not published) and checked: applied to orig.bin, each gives
cheat.bin.
"""
import argparse
import glob
import hashlib
import os
import shutil
import subprocess
import sys
import zlib

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
from gt2cheat import disc, game, patcher, payload, ppf  # noqa: E402

STEM = 'Gran Turismo 2 (Europe) (Disc 2) [Overlay Cheat]'
CHUNK = 4096                    # sectors compared at a time


def tool(pattern):
    for d in (os.path.join(ROOT, 'tools', 'xdelta'), r'D:\DOCS\Documents\GitHub\Resident Evil 1 Hotkey\tools\xdelta'):
        hits = glob.glob(os.path.join(d, pattern))
        if hits:
            return hits[0]
    return shutil.which('xdelta3')


def hashes(path):
    h, c = hashlib.sha1(), 0
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1 << 22), b''):
            h.update(b)
            c = zlib.crc32(b, c)
    return h.hexdigest(), '%08X' % (c & 0xFFFFFFFF), os.path.getsize(path)


def changes(orig, new):
    """[(offset, old, new)] of the sectors that differ."""
    out = []
    n = disc.SECTOR * CHUNK
    with open(orig, 'rb') as a, open(new, 'rb') as b:
        off = 0
        while True:
            x, y = a.read(n), b.read(n)
            if not x:
                break
            if x != y:
                for k in range(0, len(x), disc.SECTOR):
                    if x[k:k + disc.SECTOR] != y[k:k + disc.SECTOR]:
                        out.append((off + k, x[k:k + disc.SECTOR], y[k:k + disc.SECTOR]))
            off += len(x)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--src', required=True, help='stock Simulation disc (.chd, .cue, .bin)')
    a = ap.parse_args()
    d = disc.Disc(a.src)
    files = {game.EXE: patcher.patch_exe(d.read(game.EXE)), game.OVL: patcher.patch_ovl(d.read(game.OVL))}
    build = os.path.join(ROOT, 'build')
    os.makedirs(build, exist_ok=True)
    os.makedirs(os.path.join(ROOT, 'patch'), exist_ok=True)
    prog = lambda i, n: print('\r  %3d %%' % (100 * i // n), end='', flush=True)
    orig_bin, cheat_bin = os.path.join(build, 'orig.bin'), os.path.join(build, 'cheat.bin')
    d.write_bin(orig_bin, {}, prog)
    d.write_bin(cheat_bin, files, prog)
    o, c = hashes(orig_bin), hashes(cheat_bin)
    print('\rorig.bin  sha1 %s crc32 %s %d bytes\ncheat.bin sha1 %s crc32 %s %d bytes' % (o + c))
    ch = changes(orig_bin, cheat_bin)
    pp = ppf.make(ch, 'Gran Turismo 2 PAL - overlay cheat v%08X' % payload.VERSION)
    ppf_path = os.path.join(ROOT, 'patch', STEM + '.ppf')
    open(ppf_path, 'wb').write(pp)
    tmp = os.path.join(build, 'ppf_test.bin')
    shutil.copyfile(orig_bin, tmp)
    with open(tmp, 'r+b') as f:
        ppf.apply(pp, f)
    if hashes(tmp) != c:
        sys.exit('the PPF does not give cheat.bin')
    os.remove(tmp)
    print('PPF: %s (%d bytes, %d sectors), checked' % (ppf_path, len(pp), len(ch)))
    x = tool('xdelta3*.exe')
    if not x:
        print('xdelta3 not found: no .xdelta')
        return
    xd = os.path.join(ROOT, 'patch', STEM + '.xdelta')
    if os.path.exists(xd):
        os.remove(xd)
    subprocess.run([x, '-e', '-9', '-s', 'orig.bin', 'cheat.bin', xd], cwd=build, check=True)
    back = os.path.join(build, 'xdelta_test.bin')
    if os.path.exists(back):
        os.remove(back)
    subprocess.run([x, '-d', '-s', 'orig.bin', xd, 'xdelta_test.bin'], cwd=build, check=True)
    if hashes(back) != c:
        sys.exit('the xdelta does not give cheat.bin')
    os.remove(back)
    print('xdelta: %s (%d bytes), checked' % (xd, os.path.getsize(xd)))


if __name__ == '__main__':
    main()
