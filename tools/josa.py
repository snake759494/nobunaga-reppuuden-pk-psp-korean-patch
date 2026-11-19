"""런타임 조사 선택: 메시지 확장 함수(0x65620) 뒤에 버퍼를 훑어
'이(가)' 같은 표기를 앞 글자 받침에 맞춰 하나로 바꾼다."""
import os, json, struct
from mips import R

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPAND = 0x65620          # 메시지 확장 함수
CALLSITE = 0x66b3c        # jal EXPAND (R_MIPS_26 재배치 있음)
G_BUF = 0xbf0000 - 0x6dd4  # 출력 버퍼 시작 포인터
G_END = 0xbf0000 - 0x6dc8  # 출력 쓰기 포인터
G_CNT = 0xbf0000 - 0x6dc0  # 출력 바이트 수

# (표기, 받침 있음, 받침 없음, ㄹ받침이면 '없음' 쪽)
PATS = [('(으)로', '으로', '로', 1),
        ('은(는)', '은', '는', 0), ('(은)는', '은', '는', 0),
        ('을(를)', '을', '를', 0), ('를(을)', '을', '를', 0),
        ('이(가)', '이', '가', 0), ('(이)가', '이', '가', 0),
        ('와(과)', '과', '와', 0), ('과(와)', '과', '와', 0),
        ('(이)', '이', '', 0)]


class Asm:
    def __init__(s): s.c = []; s.lab = {}; s.fix = []
    def L(s, n): s.lab[n] = len(s.c)
    def e(s, w): s.c.append(w)
    def I(s, op, rs, rt, imm): s.e((op << 26) | (R[rs] << 21) | (R[rt] << 16) | (imm & 0xffff))
    def Rr(s, rd, rs, rt, fn): s.e((R[rs] << 21) | (R[rt] << 16) | (R[rd] << 11) | fn)
    def addiu(s, rt, rs, i): s.I(9, rs, rt, i)
    def ori(s, rt, rs, i): s.I(13, rs, rt, i)
    def andi(s, rt, rs, i): s.I(12, rs, rt, i)
    def sltiu(s, rt, rs, i): s.I(11, rs, rt, i)
    def lui(s, rt, i): s.I(15, 'zero', rt, i)
    def lw(s, rt, o, b): s.I(35, b, rt, o)
    def sw(s, rt, o, b): s.I(43, b, rt, o)
    def lbu(s, rt, o, b): s.I(36, b, rt, o)
    def sb(s, rt, o, b): s.I(40, b, rt, o)
    def addu(s, d, a, b): s.Rr(d, a, b, 0x21)
    def subu(s, d, a, b): s.Rr(d, a, b, 0x23)
    def sltu(s, d, a, b): s.Rr(d, a, b, 0x2b)
    def sll(s, d, t, sa): s.e((R[t] << 16) | (R[d] << 11) | (sa << 6))
    def or_(s, d, a, b): s.Rr(d, a, b, 0x25)
    def jr(s, r): s.e((R[r] << 21) | 8)
    def jalr(s, r): s.e((R[r] << 21) | (31 << 11) | 9)
    def move(s, d, r): s.addu(d, r, 'zero')
    def nop(s): s.e(0)
    def li(s, r, v): s.lui(r, (v >> 16) & 0xffff); s.ori(r, r, v & 0xffff)
    def br(s, op, rs, rt, lab):
        s.fix.append((len(s.c), lab)); s.I(op, rs, rt, 0); s.nop()
    def beq(s, a, b, l): s.br(4, a, b, l)
    def bne(s, a, b, l): s.br(5, a, b, l)
    def beqz(s, a, l): s.br(4, a, 'zero', l)
    def bnez(s, a, l): s.br(5, a, 'zero', l)
    def b(s, l): s.br(4, 'zero', 'zero', l)
    def bal(s): s.e((1 << 26) | (17 << 16) | 1); s.nop()   # ra = 다음다음 명령
    def balL(s, l): s.fix.append((len(s.c), l)); s.e((1 << 26) | (17 << 16)); s.nop()
    def bltz_(s, r, l): s.fix.append((len(s.c), l)); s.e((1 << 26) | (R[r] << 21)); s.nop()
    def out(s):
        for i, l in s.fix:
            off = s.lab[l] - i - 1
            s.c[i] = (s.c[i] & 0xffff0000) | (off & 0xffff)
        return b''.join(struct.pack('<I', x) for x in s.c)


def tables(enc):
    cmap = json.load(open(os.path.join(ROOT, 'work/build/charmap.json'), encoding='utf-8'))
    tab = bytearray([3]) * 0x7f00
    for ch, code in cmap.items():
        if len(ch) == 1 and '가' <= ch <= '힣' and 0x8100 <= code < 0x10000:
            j = (ord(ch) - 0xac00) % 28
            tab[code - 0x8100] = 0 if j == 0 else (2 if j == 8 else 1)
    pat = bytearray()
    for p, a, b, r in PATS:
        pb, ab, bb = enc(p), enc(a), enc(b)
        assert len(pb) <= 12 and len(ab) <= 8 and len(bb) <= 8
        rec = bytes([len(pb), len(ab), len(bb), r]) + pb.ljust(12, b'\0') + ab.ljust(8, b'\0') + bb.ljust(8, b'\0')
        pat += rec
    pat += b'\0' * 32
    return bytes(tab), bytes(pat)


VSPRINTF = 0x10984
VS_CALLS = [0x148c40, 0x2ac4e4, 0x2ae9d4]


def proc(a):
    """a0=시작, v1=끝, t7=패턴표, t8=받침표 → a1=새 끝 (나머지는 0으로 채움). ra로 복귀"""
    a.L('proc')
    a.move('a1', 'a0'); a.move('a3', 'a0'); a.addiu('a2', 'zero', 3)
    a.L('loop')
    a.sltu('t0', 'a0', 'v1'); a.beqz('t0', 'end')
    a.lbu('t0', 0, 'a0')
    a.addiu('t1', 'zero', 3); a.beq('a2', 't1', 'copy')
    a.move('t2', 't7')
    a.L('ploop')
    a.lbu('t3', 0, 't2'); a.beqz('t3', 'copy')
    a.addu('t4', 'a0', 't3'); a.sltu('t4', 'v1', 't4'); a.bnez('t4', 'nextp')
    a.move('t4', 'zero')
    a.L('cmp')
    a.addu('t5', 'a0', 't4'); a.lbu('t5', 0, 't5')
    a.addu('t6', 't2', 't4'); a.lbu('t6', 4, 't6')
    a.bne('t5', 't6', 'nextp')
    a.addiu('t4', 't4', 1); a.bne('t4', 't3', 'cmp')
    a.addiu('t9', 't2', 16); a.lbu('t1', 1, 't2')
    a.addiu('t4', 'zero', 1); a.beq('a2', 't4', 'write')
    a.beqz('a2', 'useb')
    a.lbu('t4', 3, 't2'); a.beqz('t4', 'write')
    a.L('useb')
    a.addiu('t9', 't2', 24); a.lbu('t1', 2, 't2')
    a.L('write')
    a.move('a1', 'a3'); a.addu('a0', 'a0', 't3')
    a.L('wl')
    a.beqz('t1', 'aw')
    a.lbu('t5', 0, 't9'); a.sb('t5', 0, 'a1')
    a.addiu('a1', 'a1', 1); a.addiu('t9', 't9', 1); a.addiu('t1', 't1', -1)
    a.b('wl')
    a.L('aw')
    a.addiu('a2', 'zero', 3); a.move('a3', 'a1'); a.b('loop')
    a.L('nextp')
    a.addiu('t2', 't2', 32); a.b('ploop')
    a.L('copy')
    a.addiu('t1', 'zero', 0x20); a.bne('t0', 't1', 'notsp')
    a.sb('t0', 0, 'a1'); a.addiu('a0', 'a0', 1); a.addiu('a1', 'a1', 1); a.b('loop')
    a.L('notsp')
    a.sltiu('t1', 't0', 0x81); a.bnez('t1', 'single')
    a.sltiu('t1', 't0', 0xa0); a.bnez('t1', 'dbl')
    a.sltiu('t1', 't0', 0xe0); a.bnez('t1', 'single')
    a.L('dbl')
    a.addiu('t1', 'a0', 1); a.sltu('t1', 't1', 'v1'); a.beqz('t1', 'single')
    a.lbu('t1', 1, 'a0'); a.sb('t0', 0, 'a1'); a.sb('t1', 1, 'a1')
    a.sll('t2', 't0', 8); a.or_('t2', 't2', 't1'); a.addiu('t2', 't2', -0x8100)
    a.addu('t2', 't8', 't2'); a.lbu('a2', 0, 't2')
    a.addiu('a0', 'a0', 2); a.addiu('a1', 'a1', 2); a.move('a3', 'a1'); a.b('loop')
    a.L('single')
    a.sb('t0', 0, 'a1'); a.addiu('a0', 'a0', 1); a.addiu('a1', 'a1', 1)
    a.addiu('a2', 'zero', 3); a.move('a3', 'a1'); a.b('loop')
    a.L('end')
    a.move('t3', 'a1')
    a.L('zl')
    a.sltu('t0', 't3', 'v1'); a.beqz('t0', 'zd')
    a.sb('zero', 0, 't3'); a.addiu('t3', 't3', 1); a.b('zl')
    a.L('zd')
    a.jr('ra'); a.nop()


def install(B, K, enc, log):
    tab, pat = tables(enc)
    TA = K.put(tab); PA = K.put(pat)
    H = None; HO = None
    for _ in range(2):
        base = H or 0
        a = Asm()
        def getbase(lab):
            a.bal(); a.L(lab)
            a.li('t0', base + 4 * a.lab[lab]); a.subu('s0', 'ra', 't0')
            a.li('t0', TA); a.addu('t8', 's0', 't0')
            a.li('t0', PA); a.addu('t7', 's0', 't0')
        # ---- 메시지 확장 래퍼 (offset 0)
        a.addiu('sp', 'sp', -32); a.sw('ra', 28, 'sp'); a.sw('s0', 24, 'sp')
        a.bal(); a.L('h1')
        a.li('t0', base + 4 * a.lab['h1']); a.subu('s0', 'ra', 't0')
        a.li('t0', EXPAND); a.addu('t9', 's0', 't0'); a.jalr('t9'); a.nop()
        a.sw('v0', 20, 'sp')
        a.li('t0', TA); a.addu('t8', 's0', 't0')
        a.li('t0', PA); a.addu('t7', 's0', 't0')
        a.li('t0', G_BUF); a.addu('t0', 's0', 't0'); a.lw('a0', 0, 't0')
        a.li('t0', G_END); a.addu('t0', 's0', 't0'); a.lw('v1', 0, 't0')
        a.sw('v1', 16, 'sp')
        a.balL('proc')
        a.lw('v1', 16, 'sp'); a.subu('t3', 'v1', 'a1')
        a.li('t0', G_END); a.addu('t0', 's0', 't0'); a.sw('a1', 0, 't0')
        a.li('t0', G_CNT); a.addu('t0', 's0', 't0'); a.lw('t1', 0, 't0'); a.subu('t1', 't1', 't3'); a.sw('t1', 0, 't0')
        a.lw('v0', 20, 'sp'); a.lw('s0', 24, 'sp'); a.lw('ra', 28, 'sp')
        a.jr('ra'); a.addiu('sp', 'sp', 32)
        # ---- vsprintf 래퍼
        a.L('vs')
        a.addiu('sp', 'sp', -32); a.sw('ra', 28, 'sp'); a.sw('s0', 24, 'sp'); a.sw('a0', 20, 'sp')
        a.bal(); a.L('h2')
        a.li('t0', base + 4 * a.lab['h2']); a.subu('s0', 'ra', 't0')
        a.li('t0', VSPRINTF); a.addu('t9', 's0', 't0'); a.jalr('t9'); a.nop()
        a.lw('a0', 20, 'sp')
        a.bltz_('v0', 'vsret')
        a.addu('v1', 'a0', 'v0')
        a.li('t0', TA); a.addu('t8', 's0', 't0')
        a.li('t0', PA); a.addu('t7', 's0', 't0')
        a.balL('proc')
        a.sb('zero', 0, 'a1')
        a.lw('a0', 20, 'sp'); a.subu('v0', 'a1', 'a0')
        a.L('vsret')
        a.lw('s0', 24, 'sp'); a.lw('ra', 28, 'sp')
        a.jr('ra'); a.addiu('sp', 'sp', 32)
        proc(a)
        code = a.out()
        if H is None:
            H = K.put(code); HO = len(K.data) - len(code)
        else:
            K.data[HO:HO + len(code)] = code
    VS = H + 4 * a.lab['vs']
    B.setw(CALLSITE, (3 << 26) | (H >> 2))
    for c in VS_CALLS: B.setw(c, (3 << 26) | (VS >> 2))
    log.append(f'josa hook {H:#x} vs {VS:#x}')
