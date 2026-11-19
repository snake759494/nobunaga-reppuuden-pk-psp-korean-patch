import struct,json,os,sys
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SD=os.path.join(ROOT,'work/iso/PSP_GAME/USRDIR/SDATA1')
def dstr(b):
    b=b.split(b'\0')[0]
    try: return b.decode('cp932')
    except: return None
def valid(t): return t and all(ord(c)>=0x3000 or c in 'ヶ' for c in t)
# table specs: (file prefix, start, stride, field_off, field_len(capacity incl null), count)
TABLES={
 'general':('SCES',0,80,[(0,9),(9,9)],None),
 'castle':('SCES',0x139a0,0x5e,[(0,9)],None),
 'item':('SCEF',0x1518,0x14,[(0,17)],None),
 'rank':('SCEF',0x3070,0xc,[(0,11)],None),
 'province':('SCEF',0x3c28,0xf,[(0,9)],None),
 'title':('SCEF',0x3e80,0xe,[(0,13)],None),
}
def scan(name):
    pre,st,stride,fields,_=TABLES[name]
    res={}
    for k in range(11):
        d=open(os.path.join(SD,'%s%02d.NB8'%(pre,k)),'rb').read()
        i=0
        while st+stride*(i+1)<=len(d):
            a=st+stride*i
            vals=[dstr(d[a+o:a+o+l]) for o,l in fields]
            if name=='general':
                if valid(vals[0]) and valid(vals[1]): res.setdefault(i,set()).add(tuple(vals))
                elif i>1300: break
            else:
                if all(valid(v) for v in vals): res.setdefault(i,set()).add(tuple(vals))
                elif not any(vals) or vals[0]=='' : pass
                else:
                    if name!='castle': break
            i+=1
            if name=='castle' and a>0x17500: break
            if name=='item' and a>=0x3070: break
            if name=='rank' and a>=0x3c28: break
            if name=='province' and a>=0x3e80: break
            if name=='title' and a>=0x40b0: break
    return res
if __name__=='__main__':
    for n in TABLES:
        r=scan(n)
        print(n,len(r),sum(len(v) for v in r.values()))
