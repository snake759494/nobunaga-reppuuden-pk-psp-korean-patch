import sys,os,re,json,struct
sys.path.insert(0,os.path.dirname(__file__))
from msg import isk,HK
from elf import Boot,build_refs
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S,E=0x2b8000,0x3093c4
FONT=(0x2c3bd0,0x2daac0)
def d2(s):
    o='';k=0
    while k<len(s):
        c=s[k]
        if isk(c): o+=s[k:k+2].decode('cp932');k+=2
        elif 0xa1<=c<=0xdf: o+=HK[c];k+=1
        elif c==10: o+='\n';k+=1
        else: o+=chr(c);k+=1
    return o
def scan(b):
    out=[];i=S
    while i<E:
        if FONT[0]<=i<FONT[1]: i=FONT[1];continue
        if b[i]==0: i+=1;continue
        j=b.index(b'\0',i); s=b[i:j]
        ok=True;k=0;jp=0;asc=0
        while k<len(s):
            c=s[k]
            if isk(c):
                if k+1>=len(s) or not (0x40<=s[k+1]<=0xfc and s[k+1]!=0x7f): ok=False;break
                try: s[k:k+2].decode('cp932')
                except: ok=False;break
                jp+=1;k+=2
            elif 0xa1<=c<=0xdf: jp+=1;k+=1
            elif 0x20<=c<0x7f or c==10: asc+=1;k+=1
            else: ok=False;break
        if ok and jp>=1:
            out.append((i,s))
        i=j+1
    return out
def plausible(t):
    # reject binary noise: ascii letters mixed with few jp chars
    core=re.sub(r'%[0-9]*[dsxc]|%%','',t)
    asc=[c for c in core if ord(c)<0x80 and c not in ' \n:.,()-+/0123456789!?=<>[]']
    jp=[c for c in core if ord(c)>=0x3000]
    if len(jp)==1 and len(core)<=2 and not ('一'<=jp[0]<='鿿'): return False
    if asc and len(asc)>=len(jp): return False
    if any(0xe000<=ord(c)<=0xf8ff for c in core): return False
    return True
if __name__=='__main__':
    b=open(os.path.join(ROOT,'work/iso/PSP_GAME/SYSDIR/BOOT.BIN'),'rb').read()
    B=Boot(os.path.join(ROOT,'work/iso/PSP_GAME/SYSDIR/BOOT.BIN'))
    R=build_refs(B)
    L=scan(b)
    res=[]
    for idx,(o,s) in enumerate(L):
        t=d2(s)
        # capacity: bytes until next non-zero byte (in-place), minus terminator
        e=o+len(s)
        while e<E and b[e]==0: e+=1
        cap=e-o-1
        res.append({'off':'%06x'%o,'jp':t,'cap':cap,'ref':(o-0x54) in R,'ko':'' if plausible(t) else None})
    json.dump(res,open(os.path.join(ROOT,'work/trans/boot/all.json'),'w',encoding='utf-8'),ensure_ascii=False,indent=0)
    print(len(res),sum(1 for r in res if r['ko']==''),sum(1 for r in res if r['ko']=='' and r['ref']))
