import struct
class Boot:
    def __init__(s,path):
        s.b=bytearray(open(path,'rb').read())
        b=s.b
        shoff,=struct.unpack_from('<I',b,0x20);shn,=struct.unpack_from('<H',b,0x30);si,=struct.unpack_from('<H',b,0x32)
        s.sh=[list(struct.unpack_from('<10I',b,shoff+40*i)) for i in range(shn)]
        st=s.sh[si][4]
        s.names=[b[st+x[0]:b.index(b'\0',st+x[0])].decode() for x in s.sh]
        s.rels=[]
        for n,x in zip(s.names,s.sh):
            if x[1]==9 or x[1]==0x700000a0:
                for k in range(x[5]//8):
                    off,info=struct.unpack_from('<II',b,x[4]+8*k)
                    s.rels.append((off,info&0xff,n))
    def w(s,a): return struct.unpack_from('<I',s.b,a+0x54)[0]
    def setw(s,a,v): struct.pack_into('<I',s.b,a+0x54,v)

def s16(x): return x-0x10000 if x&0x8000 else x
def build_refs(B):
    """returns dict target-> list of ('w',addr) or ('hl',hiaddr,loaddr)"""
    refs={}
    his={}  # reg -> (addr,imm) last HI16
    pend=[]
    for off,t,n in B.rels:
        if t==2:
            refs.setdefault(B.w(off),[]).append(('w',off))
        elif t==5:
            ins=B.w(off); rt=(ins>>16)&31
            his[rt]=(off,ins&0xffff)
        elif t==6:
            ins=B.w(off); rs=(ins>>21)&31
            if rs in his:
                ha,hi=his[rs]
                tgt=((hi<<16)+s16(ins&0xffff))&0xffffffff
                refs.setdefault(tgt,[]).append(('hl',ha,off))
            else:
                refs.setdefault(None,[]).append(('lo?',off))
    return refs
