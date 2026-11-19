import struct,sys,os
from PIL import Image
def rgb(c):
    return ((c&31)<<3,((c>>5)&31)<<3,((c>>10)&31)<<3,255 if c&0x8000 else 0)
def parse(d):
    hs,typ,po,z,st=struct.unpack_from('<IIIHH',d,0)
    if hs!=0x10 or typ not in(8,9): return None
    n,_=struct.unpack_from('<HH',d,16)
    pal=[rgb(c) for c in struct.unpack_from('<%dH'%n,d,20)]
    o=8+po; imgs=[]
    while o+12<=len(d):
        sz,x,y,w,h=struct.unpack_from('<IHHHH',d,o)
        if sz==0: break
        imgs.append((o,x,y,w,h,d[o+12:o+sz])); o+=sz
    return typ,pal,imgs
def topng(d,out):
    r=parse(d)
    if not r: return 0
    typ,pal,imgs=r
    for k,(o,x,y,w,h,px) in enumerate(imgs):
        if typ==8:
            W=w*4; a=bytearray()
            for b in px[:W*h//2]: a+=bytes((b&15,b>>4))
        else:
            W=w*2; a=px[:W*h]
        if W*h==0 or W>4096 or h>4096: continue
        im=Image.new('P',(W,h)); im.putdata(list(a)[:W*h])
        im.putpalette([v for c in pal for v in c[:3]]+[0]*(768-3*len(pal)))
        im.save('%s_%02d.png'%(out,k))
    return len(imgs)
if __name__=='__main__':
    for p in sys.argv[2:]:
        b=os.path.basename(p); print(b,topng(open(p,'rb').read(),os.path.join(sys.argv[1],b)))
