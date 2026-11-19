import struct
BOOT_TAB=0x2dd974   # file offset of block table in BOOT.BIN (64 u32)
def blocks(m,boot):
    t=struct.unpack_from('<64I',boot,BOOT_TAB)
    res=[]
    for i in range(63):
        a,b=t[i],t[i+1]
        d=m[a:b]
        n=struct.unpack_from('<H',d,0)[0]
        offs=list(struct.unpack_from('<%dH'%n,d,2))
        ents=[]
        for k in range(n):
            s=offs[k]; e=offs[k+1] if k+1<n else None
            if e is None:
                e=len(d)
                while e>s and d[e-1]==0: e-=1
            ents.append(d[s:e])
        res.append(ents)
    return res
def isk(c): return 0x81<=c<=0x9f or 0xe0<=c<=0xfc
def tokenize(b):
    """returns list of (kind,bytes) kind 'c' control or 't' text"""
    out=[];i=0;n=len(b)
    def push(k,x):
        if out and out[-1][0]==k: out[-1]=(k,out[-1][1]+x)
        else: out.append((k,x))
    while i<n:
        c=b[i]
        if c==0x01:
            L=2
            if i+1<n and b[i+1] in (0x43,0x4a): L=4
            push('c',b[i:i+L]); i+=L
        elif c==0x02:
            if i+1<n and b[i+1] in (1,2,3):
                if i+2<n and b[i+2]>=0x20 and b[i+2]!=0x02 and not (b[i+2]<0x7f and False):
                    L=3
                    if isk(b[i+2]): L=4
                else: L=2
            else:
                L=2
                if i+1<n and isk(b[i+1]): L=3
            push('c',b[i:i+L]); i+=L
        elif isk(c):
            push('t',b[i:i+2]); i+=2
        elif 0xa1<=c<=0xdf:
            push('t',b[i:i+1]); i+=1
        elif c==0x0a:
            out.append(('n',bytes([10]))); i+=1
        else:
            push('c',b[i:i+1]); i+=1
    return out
def dec(b):
    out='';i=0
    while i<len(b):
        c=b[i]
        if isk(c):
            try: out+=b[i:i+2].decode('cp932')
            except: out+='{%02x%02x}'%(c,b[i+1])
            i+=2
        elif 0xa1<=c<=0xdf:
            out+=chr(0x3041+0) if False else HK.get(c,'?');i+=1
        else: out+='<%02x>'%c;i+=1
    return out
# half-width kana byte -> hiragana (game shows hiragana)
HK={}
for c in range(0xa1,0xe0):
    k=bytes([c]).decode('cp932')
    import unicodedata
    f=unicodedata.normalize('NFKC',k)
    if len(f)==1 and 0x30a1<=ord(f)<=0x30f6: f=chr(ord(f)-0x60)
    HK[c]=f

def pack_block(ents):
    n=len(ents)
    hdr=2+2*n
    offs=[];body=bytearray()
    for e in ents:
        offs.append(hdr+len(body)); body+=e
    assert hdr+len(body)<0x10000
    return struct.pack('<H',n)+b''.join(struct.pack('<H',o) for o in offs)+bytes(body)
def pack(blocks):
    out=bytearray();tab=[];maxblk=0;b0=0
    for i,ents in enumerate(blocks):
        blk=pack_block(ents)
        if i==0: b0=len(blk)
        else: maxblk=max(maxblk,len(blk))
        tab.append(len(out)); out+=blk
        out+=b'\0'*((-len(out))%0x800)
    tab.append(len(out)); tab.append(0xffffff)
    return bytes(out),tab,b0,maxblk


def to_tagged(e):
    out=''
    for k,x in tokenize(e):
        if k=='t': out+=dec(x)
        elif k=='n': out+='\n'
        else: out+='{'+x.hex()+'}'
    return out
def is_pure(tag):
    """display-only tag: sequence of 3-byte vars 02 0[123] X / 02 X or C calls"""
    b=bytes.fromhex(tag)
    i=0
    while i<len(b):
        if b[i]==0x02 and i+2<len(b)+1 and i+1<len(b) and b[i+1] in (1,2,3) and i+2<len(b): i+=3
        elif b[i]==0x01 and i+3<len(b) and b[i+1]==0x43: i+=4
        else: return False
    return True
import re
TAG=re.compile(r'\{([0-9a-f]+)\}')
def tags_of(s): return TAG.findall(s)
def check_tags(jp,ko):
    a=tags_of(jp); b=tags_of(ko)
    sa=[t for t in a if not is_pure(t)]; sb=[t for t in b if not is_pure(t)]
    if sa!=sb: return 'structural tags differ'
    if sorted(a)!=sorted(b): return 'display tags differ'
    # pure tags must stay within same segment
    def segs(s):
        out=[[]]
        for t in tags_of(s):
            if is_pure(t): out[-1].append(t)
            else: out.append([])
        return [sorted(x) for x in out]
    if segs(jp)!=segs(ko): return 'display tag moved across structure'
    return None
def width(line):
    w=0
    for ch in TAG.sub('',line):
        w+=0.5 if ch==' ' else 1
    return w
