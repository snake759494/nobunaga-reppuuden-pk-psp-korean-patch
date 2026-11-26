"""PMF(PSMF) 영상 다시 묶기: python tools/pmf.py 원본.PMF 새영상.h264 출력.PMF

원본의 팩 배치(팩 헤더·음성·시스템 헤더)는 그대로 두고 영상 PES만 다시 채운다.
- GOP(IDR)마다 원본 GOP의 팩 범위 안에 새 GOP를 넣고, 남는 칸은 패딩 스트림(0xBE)으로 채운다.
- GOP 첫 팩의 private stream 2(0xBF) 표(프레임 크기·참조 여부·앞 4프레임이 끝나는 팩)를 새로 계산한다.
  실기 PSP의 동영상 라이브러리는 이 표로 액세스 유닛을 자르므로 틀리면 멈춘다.
- PTS/DTS는 원본처럼 GOP 첫 프레임과, 직전 PTS에서 16프레임 이상 지나 처음 시작하는 프레임의 PES에 붙인다.
새 영상은 원본과 프레임 수·IDR 위치가 같아야 한다(B프레임 없음)."""
import struct, sys, bisect

AUD = b'\0\0\0\1\x09'

def packs(d):
    """[(pack_off, [(sid, start, total_len)])]"""
    out = []
    for off in range(2048, len(d) - 2047, 2048):
        pk = d[off:off + 2048]
        assert pk[:4] == b'\0\0\1\xba', hex(off)
        i = 14 + (pk[13] & 7); L = []
        while i < 2048 and pk[i:i + 3] == b'\0\0\1':
            n = struct.unpack('>H', pk[i + 4:i + 6])[0]
            L.append((pk[i + 3], i, 6 + n)); i += 6 + n
        assert i == 2048, (hex(off), i)
        out.append((off, L))
    return out

def es_of(d):
    es = bytearray()
    for off, L in packs(d):
        for sid, i, n in L:
            if sid == 0xe0:
                hl = d[off + i + 8]; es += d[off + i + 9 + hl:off + i + n]
    return bytes(es)

def frames(es):
    a = []; j = es.find(AUD)
    assert j == 0
    while j >= 0: a.append(j); j = es.find(AUD, j + 1)
    return [es[x:y] for x, y in zip(a, a[1:] + [len(es)])]

def nal_types(f):
    t = []; j = f.find(b'\0\0\1')
    while j >= 0: t.append(f[j + 3]); j = f.find(b'\0\0\1', j + 3)
    return t

def is_idr(f): return any(b & 0x1f == 5 for b in nal_types(f))
def is_ref(f): return any((b & 0x1f) in (1, 5) and (b >> 5) & 3 for b in nal_types(f))

def gop_starts(d):
    """0xBF 표의 프레임 수로 GOP 시작 프레임 번호"""
    r = [0]
    for off, L in packs(d):
        for sid, i, n in L:
            if sid == 0xbf: r.append(r[-1] + struct.unpack('>H', d[off + i + 6 + 16:off + i + 6 + 18])[0])
    return r[:-1]

def ts(pfx, v):
    return bytes([pfx << 4 | ((v >> 29) & 0xe) | 1, (v >> 22) & 0xff, ((v >> 14) & 0xfe) | 1, (v >> 7) & 0xff, ((v << 1) & 0xfe) | 1])

def remux(orig, newes):
    d = bytearray(orig); P = packs(orig)
    oF = frames(es_of(orig)); nF = frames(newes)
    assert len(oF) == len(nF), (len(oF), len(nF))
    # 원본 PTS PES 헤더(확장 포함) 견본, PTS 시작값
    tmpl = None
    for off, L in P:
        for sid, i, n in L:
            if sid == 0xe0 and orig[off + i + 7] & 0x80:
                hl = orig[off + i + 8]; tmpl = bytes(orig[off + i + 6:off + i + 9 + hl]); break
        if tmpl: break
    h = tmpl[3:8]; pts0 = ((h[0] >> 1) & 7) << 30 | h[1] << 22 | (h[2] >> 1) << 15 | h[3] << 7 | h[4] >> 1
    ext = tmpl[13:]
    # GOP 시작 팩 = 0xBF 있는 팩
    gp = [k for k, (off, L) in enumerate(P) if any(s == 0xbf for s, _, _ in L)]
    oI = gop_starts(orig)
    for k in oI: assert is_idr(nF[k]), ('GOP 시작이 IDR 아님', k)
    bounds = oI + [len(oF)]

    for g, pk0 in enumerate(gp):
        pk1 = gp[g + 1] if g + 1 < len(gp) else len(P)
        f0, f1 = bounds[g], bounds[g + 1]
        data = b''.join(nF[f0:f1])
        starts = []; s = 0
        for k in range(f0, f1): starts.append(s); s += len(nF[k])
        pos = 0; endpk = {}; nxtpts = 0
        for q in range(pk0, pk1):
            off, L = P[q]
            for sid, i, n in L:
                if sid != 0xe0: continue
                a = off + i
                # 이 PES 안에서 시작하는 첫 프레임
                hdr = b'\x81\x00\x00'
                cap = n - 6 - len(hdr)
                k = bisect.bisect_left(starts, pos)
                if k < len(starts) and starts[k] < pos + (n - 6 - (len(tmpl) if k == 0 else 13)) and k >= nxtpts and pos < len(data):
                    nxtpts = k + 16
                    p = pts0 + (f0 + k) * 3003
                    e = ext if k == 0 else b''   # GOP 첫 프레임만 P-STD 확장
                    hdr = bytes([0x81, 0xc1 if e else 0xc0, 10 + len(e)]) + ts(3, p) + ts(1, p - 3003) + e
                    cap = n - 6 - len(hdr)
                take = min(cap, len(data) - pos)
                if take <= 0:          # 통째로 패딩
                    d[a:a + n] = b'\0\0\1\xbe' + struct.pack('>H', n - 6) + b'\xff' * (n - 6); continue
                left = cap - take
                if 0 < left < 6:       # 헤더 스터핑으로 흡수
                    hdr = hdr[:2] + bytes([hdr[2] + left]) + hdr[3:] + b'\xff' * left; left = 0
                pes = b'\0\0\1\xe0' + struct.pack('>H', len(hdr) + take) + hdr + data[pos:pos + take]
                if left: pes += b'\0\0\1\xbe' + struct.pack('>H', left - 6) + b'\xff' * (left - 6)
                assert len(pes) == n
                d[a:a + n] = pes
                for kk in range(f0, f1):
                    e = starts[kk - f0] + len(nF[kk]) - 1
                    if pos <= e < pos + take: endpk[kk - f0] = q
                pos += take
        assert pos == len(data), ('GOP %d 넘침: %d > %d' % (g, len(data), pos))
        # 0xBF 표
        off, L = P[pk0]
        sid, i, n = [x for x in L if x[0] == 0xbf][0]
        a = off + i + 6
        old = bytes(d[a:a + n - 6])
        nfr = f1 - f0
        rel = [endpk[k] - pk0 for k in range(4)] if g else [0, 0, 0, 0]
        tbl = old[:2] + struct.pack('>4H', *rel) + old[10:14]
        body = struct.pack('>H', nfr) + b''.join(struct.pack('>HH', 0x80 if is_ref(nF[k]) else 0, len(nF[k])) for k in range(f0, f1))
        tbl += struct.pack('>H', len(body)) + body
        assert len(tbl) <= n - 6, ('표 길이', g)
        tbl += b'\xff' * (n - 6 - len(tbl)) if len(tbl) < len(old) and old[len(tbl):] == b'\xff' * (len(old) - len(tbl)) else b'\0' * (n - 6 - len(tbl))
        d[a:a + n - 6] = tbl
    return bytes(d)

if __name__ == '__main__':
    o = open(sys.argv[1], 'rb').read()
    es = open(sys.argv[2], 'rb').read() if sys.argv[2] != '-' else es_of(o)
    r = remux(o, es)
    open(sys.argv[3], 'wb').write(r)
    print('같음' if r == o else '다름', len(r))
