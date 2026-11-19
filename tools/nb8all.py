import glob,os,sys,struct
sys.path.insert(0,os.path.dirname(__file__))
import nb8
from PIL import Image
def subs(d):
    out=[];i=0
    while True:
        i=d.find(b'\x10\0\0\0',i)
        if i<0: break
        if i%4==0 and d[i+4:i+8] in (b'\x08\0\0\0',b'\x09\0\0\0'):
            r=nb8.parse(d[i:])
            if r and r[2]: out.append((i,r))
        i+=4
    return out
def img(r):
    typ,pal,imgs=r; o,x,y,w,h,px=imgs[0]
    W=w*4 if typ==8 else w*2
    if typ==8:
        a=bytearray()
        for b in px[:W*h//2]: a+=bytes((b&15,b>>4))
    else: a=px[:W*h]
    if not(0<W<=1024 and 0<h<=1024) or len(a)<W*h: return None
    im=Image.new('P',(W,h)); im.putdata(list(a)); im.putpalette([v for c in pal for v in c[:3]]+[0]*(768-3*len(pal)))
    return im.convert('RGB')
if __name__=='__main__':
    out=sys.argv[1]; os.makedirs(out,exist_ok=True)
    for f in sys.argv[2:]:
        d=open(f,'rb').read(); ims=[]
        for i,r in subs(d):
            im=img(r)
            if im: ims.append((i,im))
        if not ims: continue
        Wd=1024;x=y=rh=0;pos=[]
        for i,im in ims:
            if x+im.width>Wd: x=0;y+=rh+3;rh=0
            pos.append((im,x,y));x+=im.width+3;rh=max(rh,im.height)
        S=Image.new('RGB',(Wd,min(y+rh,4000)),(255,0,255))
        for im,x,yy in pos: S.paste(im,(x,yy))
        S.save(os.path.join(out,os.path.basename(f)+'.png')); print(os.path.basename(f),len(ims),S.size)
