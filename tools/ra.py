"""Reverse-engineering helpers: the code of SCES_123.80 / an overlay, references to addresses
(lui + addiu / lw / sw pairs), disassembly around an address, callers of a function (jal).

    python tools/ra.py refs <code.bin> <base> <addr> [<addr> ...]
    python tools/ra.py dis <code.bin> <base> <addr> [count]
    python tools/ra.py calls <code.bin> <base> <func>
"""
import struct
import sys

import capstone

MD = capstone.Cs(capstone.CS_ARCH_MIPS, capstone.CS_MODE_MIPS32 + capstone.CS_MODE_LITTLE_ENDIAN)


def words(code):
    return struct.unpack('<%dI' % (len(code) // 4), code[:len(code) // 4 * 4])


def refs(code, base, targets):
    """(pc, target, text) of each instruction that forms one of the targets with an earlier lui
    of the same register (within 32 instructions)."""
    w = words(code)
    out = []
    lui = {}
    for i, ins in enumerate(w):
        op = ins >> 26
        rs, rt = (ins >> 21) & 31, (ins >> 16) & 31
        imm = ins & 0xFFFF
        simm = imm - 0x10000 if imm & 0x8000 else imm
        if op == 0x0F:
            lui[rt] = (i, imm << 16)
            continue
        if rs in lui and i - lui[rs][0] < 32 and op in (0x09, 0x20, 0x21, 0x23, 0x24, 0x25, 0x28, 0x29, 0x2B, 0x0D):
            v = (lui[rs][1] + (imm if op == 0x0D else simm)) & 0xFFFFFFFF
            for t in targets:
                if t - 0x400 <= v <= t + 0x400:
                    out.append((base + 4 * i, v, dis1(code, base, base + 4 * i)))
    return out


def dis1(code, base, pc):
    o = pc - base
    for ins in MD.disasm(code[o:o + 4], pc):
        return '%s %s' % (ins.mnemonic, ins.op_str)
    return '.word 0x%08x' % struct.unpack_from('<I', code, o)[0]


def dis(code, base, pc, n=40):
    o = pc - base
    lines = []
    for k in range(n):
        q = o + 4 * k
        if q < 0 or q + 4 > len(code):
            break
        lines.append('%08x: %08x  %s' % (pc + 4 * k, struct.unpack_from('<I', code, q)[0], dis1(code, base, pc + 4 * k)))
    return '\n'.join(lines)


def calls(code, base, func):
    w = words(code)
    want = 0x0C000000 | ((func & 0x0FFFFFFF) >> 2)
    return [base + 4 * i for i, ins in enumerate(w) if ins == want]


def load(path):
    d = open(path, 'rb').read()
    if d[:8] == b'PS-X EXE':
        return d[0x800:], struct.unpack_from('<I', d, 0x18)[0]
    return d, None


if __name__ == '__main__':
    cmd, path = sys.argv[1], sys.argv[2]
    code, b = load(path)
    base = int(sys.argv[3], 16)
    if cmd == 'refs':
        for pc, v, t in refs(code, base, [int(a, 16) for a in sys.argv[4:]]):
            print('%08x -> %08x  %s' % (pc, v, t))
    elif cmd == 'dis':
        print(dis(code, base, int(sys.argv[4], 16), int(sys.argv[5]) if len(sys.argv) > 5 else 40))
    elif cmd == 'calls':
        for pc in calls(code, base, int(sys.argv[4], 16)):
            print('%08x' % pc)
