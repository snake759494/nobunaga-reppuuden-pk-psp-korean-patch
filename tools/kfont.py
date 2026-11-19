"""Build extended 16x16 font: original 2529 glyphs + all KS X 1001 hangul (2350)
   + extra punctuation glyphs. Writes work/build/font_codes.bin, font_bits.bin, charmap.json"""
import struct,json,os
from PIL import Image,ImageDraw,ImageFont
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOOT=os.path.join(ROOT,'work/iso/PSP_GAME/SYSDIR/BOOT.BIN')
B=0x54; N0=2529; CODES0=0x2d977c+B; BITS0=0x2c5b5c+B
EXTRA='슌숑쌰쎼쑈쓩'
def hangul_list():
    out=[]
    for hi in range(0xb0,0xc9):
        for lo in range(0xa1,0xff):
            out.append(bytes([hi,lo]).decode('euc-kr'))
    return out+[c for c in EXTRA if c not in out]
def cand_codes():
    for lead in list(range(0x88,0xa0))+list(range(0xe0,0xfd)):
        for tr in list(range(0x40,0x7f))+list(range(0x80,0xfd)):
            c=(lead<<8)|tr
            if c<0x889f: continue
            yield c
def render(ch,font,yoff):
    g=Image.new('L',(16,16),0);d=ImageDraw.Draw(g);d.fontmode='1'
    bb=font.getbbox(ch); w=bb[2]-bb[0]
    d.text(((16-w)//2-bb[0],yoff),ch,font=font,fill=255)
    g=g.point(lambda v:255 if v>=110 else 0)
    bits=bytearray(32)
    for y in range(16):
        for x in range(16):
            if g.getpixel((x,y)): bits[y*2+x//8]|=0x80>>(x%8)
    return bytes(bits)
def build():
    b=open(BOOT,'rb').read()
    codes=[struct.unpack_from('<H',b,CODES0+2*i)[0] for i in range(N0)]
    glyph={c:b[BITS0+32*i:BITS0+32*i+32] for i,c in enumerate(codes)}
    font=ImageFont.truetype(os.path.join(ROOT,'Galmuri14.ttf'),15)
    # vertical offset: fit '한' '읽' 'ㅎ' into 16 rows
    tops=[font.getbbox(c)[1] for c in '가힣읽뷁햏']; bots=[font.getbbox(c)[3] for c in '가힣읽뷁햏']
    yoff=(16-(max(bots)-min(tops)))//2-min(tops)
    cmap={}
    it=iter(c for c in cand_codes() if c not in glyph)
    for ch in hangul_list():
        c=next(it); glyph[c]=render(ch,font,yoff); cmap[ch]=c
    # Korean punctuation (replace/add full-width forms)
    fb=font
    for ch,c,dx in [(',',0x8143,-3),("'",0x8166,0),('"',0x8168,0)]:
        if c in glyph: continue
        g=Image.new('L',(16,16),0);d=ImageDraw.Draw(g);d.fontmode='1'
        bb=fb.getbbox(ch); w=bb[2]-bb[0]
        d.text(((16-w)//2-bb[0]+dx,yoff),ch,font=fb,fill=255)
        g=g.point(lambda v:255 if v>=100 else 0)
        bits=bytearray(32)
        for y in range(16):
            for x in range(16):
                if g.getpixel((x,y)): bits[y*2+x//8]|=0x80>>(x%8)
        glyph[c]=bytes(bits)
    os.makedirs(os.path.join(ROOT,'work/build'),exist_ok=True)
    ks=sorted(glyph)
    open(os.path.join(ROOT,'work/build/font_codes.bin'),'wb').write(b''.join(struct.pack('<H',c) for c in ks))
    open(os.path.join(ROOT,'work/build/font_bits.bin'),'wb').write(b''.join(glyph[c] for c in ks))
    json.dump(cmap,open(os.path.join(ROOT,'work/build/charmap.json'),'w',encoding='utf-8'),ensure_ascii=False)
    return len(ks)
if __name__=='__main__': print(build())
