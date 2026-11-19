"""메뉴 이미지 한글화: python tools/img.py"""
import os,sys,json,random
sys.path.insert(0,os.path.dirname(__file__))
from PIL import Image,ImageDraw,ImageFont,ImageFilter
import nb8
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W=lambda p:os.path.join(ROOT,p)
U='work/iso/PSP_GAME/USRDIR/'
SC=['노부나가 원복','노부나가 가독 계승','오케하자마 전투','노부나가 포위망','데도리가와 전투','혼노지의 변',
    '시즈가타케 전투','고마키·나가쿠테','규슈 정벌','오다와라 정벌','제왕의 싸움']
SCD=['1546년 3월','1551년 3월','1560년 5월','1570년 9월','1577년 9월','1582년 3월','1583년 4월',
     '1584년 3월','1586년 1월','1589년 11월','1570년 9월']
JOBS={
 'MDATA1/KANKYOU.NB8':(96,24,[['있음']*2+['없음']*2,['스테레오']*2+['모노럴']*2,['표시']*2+['비표시']*2,
                             ['초급']*2+['상급']*2,['등장']*2+['미등장']*2],'center',14),
 'IDATA1/NEWDYOU.NB8':(224,24,[['가상 시작'],['모반 시작'],['후계 시작']],'center',14),
 'IDATA1/NEWGAME.NB8':(232,24,[[t,t] for t in ['데이터 불러오기','일반 플레이 모드','쇼트 플레이 모드',
    '신다이묘 플레이 모드','신무장·신가보 등록 관리','이마가와의 야망 ~튜토리얼~','역사 이벤트 모음','BGM 모드']],'center',14),
 'IDATA1/SCENARIO.NB8':(256,24,[[('시나리오%d'%i,SCD[i],SC[i])]*2 for i in range(11)],'scen',12),
}
CMD=[(0,'출성개발군단공작관위위임'),(1,'정보건설개발동맹조적은거'),(2,'조략파견건설혼인사면혼약'),
 (3,'외교소집내응포섭헌상상벌'),(4,'조정가문모반권고참언추방'),(5,'성국유언공물등용'),(6,'가문성변심단교구입'),(7,'군단무장암살원군매각')]
G='PSP_GRP.NB8'
TITLE=['데이터 불러오기','일반 플레이 모드','쇼트 플레이 모드','신다이묘 플레이 모드','신무장·신가보 작성','용어 사전']
def rows(cw,ch,col,texts,fs=14):
    return [(col*cw,r*ch,cw,ch,t,'full',fs) for r,t in enumerate(texts) if t]
TL=['승리와 패배 조건','무장의 신분과 병력','성과 지배 범위','내정 계획','군단 규모','중규모 야전','중규모 공성전','해전','무장 랭킹','신가보 등록','쇼트 플레이 모드']
TR=['위신','무장의 개성','개발 지형','병과','소규모 야전','대규모 야전','대규모 공성전','합전 종료 조건','신무장 등록','에디터 기능','신다이묘 플레이 모드']
TM=['전략 화면','토지 개발','인사','대외 공작','군단 편성','군의','합전 화면','합전','전후 처리']
MD1=['신무장 등록','신가보 등록','등록 데이터 불러오기','등록 데이터 불러오기']
OTHER=[('TDATA1/TMENU.NB8',0,rows(264,24,0,['이마가와의 야망 ~게임의 흐름~']*2+['열풍 용어집 ~게임의 키워드~']*2)),
 ('TDATA1/TMENU.NB8',0x31c0,rows(72,24,0,TM,12)+rows(72,24,1,TM,12)),
 ('EDATA/MDMAIN.NB8',0,rows(224,24,0,MD1)),('EDATA/MDMAIN.NB8',0x2a40,rows(224,24,0,MD1)),
 ('EDATA/MDMAIN.NB8',0x5480,rows(224,24,0,['신무장 작성','신무장 변경','신무장 삭제'])),('EDATA/MDMAIN.NB8',0x7440,rows(224,24,0,['신무장 작성','신무장 변경','신무장 삭제'])),
 ('EDATA/MDMAIN.NB8',0x9400,rows(224,24,0,['신가보 작성','신가보 변경','신가보 삭제'])),('EDATA/MDMAIN.NB8',0xb3c0,rows(224,24,0,['신가보 작성','신가보 변경','신가보 삭제'])),
 ('EDATA/EDCOMMON.NB8',0,[(0,0,32,16,'결정','full',12),(32,0,32,16,'취소','full',12)]),
 ('EDATA/EDCOMMON.NB8',0x240,[(0,0,32,16,'결정','full',12),(32,0,32,16,'취소','full',12)]),
]+[('CDATA1/COMMON.NB8',o,[(i*16,0,16,16,c,('iconl' if o==0x2b00 else 'icond'),12) for i,c in enumerate(t)]) for o,t in
   ((0x2700,'약상'),(0x2b00,'미완'),(0x4dc0,'농상건등외'),(0x5380,'보기철수'),(0x6140,'혼동'),(0x6280,'정전휘지'))]+[('TDATA1/TPCMENU.NB8',o,rows(136,16,0,TL,12)+rows(136,16,1,TL,12)+rows(136,16,2,TR,12)+rows(136,16,3,TR,12)) for o in (0,0xc000)]
OTHER+=[('EDATA/%s.NB8'%f,o,[(0,0,32,16,'결정','fulld',12),(32,0,32,16,'취소','fulld',12)]) for f,o1,o2 in (('DED',0x12360,0x125a0),('KED',0x13bf0,0x13e30),('SED',0x13240,0x13480)) for o in (o1,o2)]
OTHER+=[('WDATA1/WARMARK.NB8',0x4320,[(0,0,16,16,'공','iconl',12),(16,0,16,16,'공','iconl',12)]),
 ('WDATA1/WARMARK.NB8',0x6d60,[(0,0,16,16,'수','icond',12),(16,0,16,16,'수','icond',12)]),
 ('WDATA1/WJINKEI.NB8',0x0,[(0,0,16,16,'방','icond',12)]),('WDATA1/WJINKEI.NB8',0x28a0,[(0,0,16,16,'이','icond',12)]),
 ('WDATA1/WJINKEI.NB8',0x2960,[(0,0,16,16,'공','icond',12)]),
 ('MDATA1/MIDMAP.NB8',0xdc40,[(0,0,16,16,'장','icond',12),(16,0,16,16,'완','icond',12)])]

# 신무장·신가보 편집 화면 라벨 (EDATA/BEPAGE*, KED)
def _lab(f,offs,texts,lws,h=20):
    return [('EDATA/%s.NB8'%f,o,[(0,0,lw,h,t,'flat',12)]) for o,t,lw in zip(offs,texts,lws)]
_BTN=['결정','취소','결정','취소','다음','뒤로','다음','뒤로']
_B8=[0x11e80+0x140*i for i in range(8)]
for _f in ('BEPAGE1A','BEPAGE1B','BEPAGE2','BEPAGE3','BEPAGE4','BEPAGE5'):
    OTHER+=_lab(_f,_B8,_BTN,[32]*8,16)
_P1=['이름','친부','얼굴 변경','수명','성별','출생']
OTHER+=_lab('BEPAGE1A',[0x12880,0x12f78,0x13670,0x13a48,0x13e20,0x141f8,0x145d0,0x14cc8,0x153c0,0x15798,0x15b70,0x15f48],_P1*2,[34,34,92,34,34,34]*2)
OTHER+=_lab('BEPAGE1B',[0x12880,0x12f78,0x13350,0x13728,0x13b00,0x141f8,0x145d0,0x149a8],['이름','수명','훈공','사관']*2,[34]*8)
OTHER+=_lab('BEPAGE2',[0x12880+i*0x2e8 for i in range(4)]+[0x13420+i*0x298 for i in range(4)]+[0x13e80+i*0x2e8 for i in range(4)]+[0x14a20+i*0x298 for i in range(4)],
            ['정치','전투','지휘','지모','보병','기마','철포','수군']*2,[34]*16)
OTHER+=_lab('BEPAGE3',[0x12880+i*0x298 for i in range(18)],['농업','상업','건설','등용','외교','삼단','포락','기돌','기철']*2,[34]*18)
OTHER+=_lab('BEPAGE4',[0x12880+i*0x298 for i in range(24)],['닌자','다인','검호','승려','학익','어린','안행','언월','형액','장사','봉시','방원']*2,[34]*24)
OTHER+=_lab('BEPAGE5',[0x12880,0x12c58,0x12f40,0x13228,0x13650,0x13c08,0x13f40,0x143b8,0x14970,0x14d48,0x15030,0x15318,0x15740,0x15cf8,0x16030,0x164a8],
            ['말투','상성','의리','최대의리','사고형태','위신','기독교관','상락지향']*2,[34,34,34,66,66,34,66,66]*2)
OTHER+=_lab('BEPAGE6',[0x137c0,0x13eb8,0x145b0,0x14988],['이름','친부','성별','출생'],[34]*4)
OTHER+=_lab('KED',[0,0x5b8,0x800,0xb38,0x1230,0x16a8,0x1a80,0x1e58,0x2410,0x2658,0x2990,0x3088,0x3500,0x38d8],
            ['이름','CG변경','등급','소지','종류','능력상승','병과상승']*2,[34,52,34,34,34,66,66]*2)
PSPJOBS=[
 ('MDATA1/KANKYOU.NB8',0x5a40,(64,24,[['짧게','짧게','보통','보통','길게','길게','관전'],['관전','선택','선택','직할','직할','안 봄','안 봄']],'c',14)),
 (G,0x61780,[(c*232,r*24,232,24,t,'full',14) for r,t in enumerate(TITLE) for c in (0,1)]),
 (G,0x8ce60,[(288,0,96,24,'없음','c',14),(226,0,62,24,'','c',14),(192,24,96,24,'모노럴','c',14),(288,24,96,24,'모노럴','c',14)]+
   [(c*96,r*24,96,24,t,'c',14) for r,(a,b) in ((2,('표시','비표시')),(3,('초급','상급')),(4,('등장','미등장'))) for c,t in enumerate((a,a,b,b))]),
 (G,0xa6560,[(c*256,r*24,256,24,('%d.'%(r+1),SCD[r].replace('  ',' '),SC[r]),'scen',12) for r in range(11) for c in (0,1)]),
]
FONT=W('SeoulHangangM.ttf')
GAL=[('Galmuri14.ttf',15),('Galmuri11.ttf',12),('Galmuri9.ttf',10),('Galmuri7.ttf',8)]
def gfont(text,cw,ch,bold=False,pad=4):
    """갈무리체를 원래 픽셀 크기로만 사용(확대·축소 없음). 칸에 들어가는 가장 큰 것."""
    for f,px in GAL:
        if px>ch-2: continue
        if bold and f=='Galmuri11.ttf': f='Galmuri11-Bold.ttf'
        F=ImageFont.truetype(W(f),px)
        if ImageDraw.Draw(Image.new('L',(1,1))).textlength(text,font=F)<=cw-pad: return F
    return F
def newdraw(w,h):
    im=Image.new('L',(w,h),0); dr=ImageDraw.Draw(im); dr.fontmode='1'; return im,dr
def lum(c): return 0.3*c[0]+0.59*c[1]+0.11*c[2]
FILES={}
def getf(rel):
    if rel not in FILES: FILES[rel]=bytearray(open(W(U+rel),'rb').read())
    return FILES[rel]
def grid2cells(cw,ch,grid,mode,fs):
    return [(c*cw,r*ch,cw,ch,t,mode,fs) for r,row in enumerate(grid) for c,t in enumerate(row) if t]
def process(rel,spec,sub=0):
    cells=grid2cells(*spec) if isinstance(spec,tuple) else spec
    d=getf(rel)
    typ,pal,imgs=nb8.parse(bytes(d[sub:]))
    o,x,y,w,h,px=imgs[0]; o+=sub
    Wd=w*4 if typ==8 else w*2
    if typ==8:
        a=[]
        for b in px[:Wd*h//2]: a+= [b&15,b>>4]
    else: a=list(px[:Wd*h])
    P=[a[i*Wd:(i+1)*Wd] for i in range(h)]
    pal3=[c[:3] for c in pal]
    L=[lum(c) for c in pal3]
    rnd=random.Random(1)
    TH=45
    for x0,y0,cw,ch,txt,mode,fs in cells:
            dk=(mode=='fulld')
            if dk: mode='full'
            TH=22 if mode=='scen' and sub else (15 if mode=='full' else 45)
            font=gfont(' '.join(txt).replace('  ',' ') if mode=='scen' else txt,cw,ch,pad=10 if mode=='scen' else 4)
            if mode in ('icond','iconl'):
                icon(P,L,rnd,x0,y0,txt,mode=='icond'); continue
            if mode=='glyph':
                glyph(P,pal3,L,x0,y0,txt); continue
            if mode=='flat':
                flatlab(P,L,x0,y0,cw,ch,txt,font); continue
            m_=2 if ch<=16 else 3
            inner=[(xx,yy) for yy in range(y0+m_,y0+ch-m_) for xx in range(x0+m_,x0+cw-m_)]
            ls=sorted(L[P[yy][xx]] for xx,yy in inner); med=ls[len(ls)//2]
            txtpix=[(xx,yy) for xx,yy in inner if (L[P[yy][xx]]<med-40 if (med>150 or dk) else L[P[yy][xx]]>med+TH)]
            if not txtpix: continue
            from collections import Counter
            tcol=Counter(P[yy][xx] for xx,yy in txtpix).most_common(1)[0][0]
            if mode=='full':
                cc=Counter(P[yy][xx] for xx,yy in txtpix); tcol=max((v for v in cc if cc[v]>=8),key=lambda v:(-L[v] if (med>150 or dk) else L[v]))
            ts=set(txtpix); mask=set()
            if mode=='full':
                mask={(xx,yy) for xx,yy in inner}
                band=[(xx,yy) for yy in ((y0+1,y0+ch-2) if ch<=16 else (y0+3,y0+4,y0+ch-5,y0+ch-4)) for xx in range(x0+3,x0+cw-3)]
                mask={(xx,yy) for yy in range(y0+(2 if ch<=16 else 3),y0+ch-2) for xx in range(x0+2,x0+cw-2)} if ch<=16 else mask
                for xx,yy in mask:
                    sx,sy=rnd.choice(band); P[yy][xx]=P[sy][sx]
                mask=set()
            for xx,yy in ([] if mode=='full' else txtpix):
                for dx in (-1,0,1,2):
                    for dy in (-1,0,1,2):
                        q=(xx+dx,yy+dy)
                        if x0+2<=q[0]<x0+cw-2 and y0+2<=q[1]<y0+ch-2: mask.add(q)
            clean=[(xx,yy) for xx,yy in inner if (xx,yy) not in mask]
            byrow={}
            for xx,yy in clean: byrow.setdefault(yy,[]).append((xx,yy))
            for xx,yy in mask:
                cand=byrow.get(yy) or clean
                sx,sy=rnd.choice(cand); P[yy][xx]=P[sy][sx]
            shadow=min(range(len(pal3)),key=lambda i:L[i] if i else 999)
            # render
            im,dr=newdraw(cw,ch)
            if mode=='scen':
                t=' '.join(txt).replace('  ',' ')
                tw=dr.textlength(t,font=font)
                dr.text((max(4,(cw-tw)//2),ch//2),t,font=font,fill=255,anchor='lm')
                assert tw<cw-8,(t,tw)
            else:
                dr.text((cw//2,ch//2),txt,font=font,fill=255,anchor='mm')
            A=im.load()
            for yy in range(ch):
                for xx in range(cw):
                    v=A[xx,yy]
                    if False:
                        for qx,qy in ((xx+1,yy+1),):
                            if qx<cw and qy<ch and A[qx,qy]<128: P[y0+qy][x0+qx]=shadow
            for yy in range(ch):
                for xx in range(cw):
                    if A[xx,yy]>=128: P[y0+yy][x0+xx]=tcol
    flat=[v for row in P for v in row]
    if typ==8:
        nb=bytes((flat[i]|(flat[i+1]<<4)) for i in range(0,len(flat),2))
    else: nb=bytes(flat)
    d[o+12:o+12+len(nb)]=nb
    im=Image.new('P',(Wd,h)); im.putdata(flat); im.putpalette([v for c in pal3 for v in c]+[0]*(768-3*len(pal3)))
    im.save(W('work/img/ko_%s_%x.png'%(os.path.basename(rel),sub)))
def flatlab(P,L,x0,y0,cw,ch,txt,font):
    from collections import Counter
    m=2
    reg=[P[y][x] for y in range(y0+m,y0+ch-m) for x in range(x0+m,x0+cw-m)]
    cnt=Counter(reg); med=sorted(L[v] for v in reg)[len(reg)//2]
    edge=Counter(P[y][x] for y in (y0+m,y0+ch-m-1) for x in range(x0+m,x0+cw-m))
    bg=max(edge,key=lambda v:edge[v])
    tc=min(cnt,key=lambda v:L[v])
    for y in range(y0+m,y0+ch-m):
        for x in range(x0+m,x0+cw-1): P[y][x]=bg
    im,dr=newdraw(cw,ch); dr.text((cw//2,ch//2),txt,font=font,fill=255,anchor='mm'); A=im.load()
    for y in range(ch):
        for x in range(cw):
            if A[x,y]>=128: P[y0+y][x0+x]=tc
def cmd_cells():
    d=getf(G); typ,pal,imgs=nb8.parse(bytes(d[0xa3520:])); o,x,y,w,h,px=imgs[0]
    Wd=w*4; a=[]
    for b in px[:Wd*h//2]: a+=[b&15,b>>4]
    cells=[]
    POS={7:list(range(0,160,16)),5:[8,41,64,80,96,112,128,144],6:[0,16,40,64,80,96,112,128,144]}
    for col,txt in CMD:
        ys=POS.get(col,list(range(0,192,16)))
        assert len(ys)==len(txt),(col,ys,txt)
        cells+=[(col*16,y0,16,16,t,'glyph',14) for y0,t in zip(ys,txt)]
    return cells
def icon(P,L,rnd,x0,y0,t,dark):
    cellc=[P[y0+j][x0+i] for j in range(16) for i in range(16)]
    col=min(cellc,key=lambda v:L[v]) if dark else max(cellc,key=lambda v:L[v])
    from collections import Counter
    ring=[P[y0+j][x0+i] for j in range(1,15) for i in range(1,15)]
    dk=min(set(ring),key=lambda v:L[v])
    bgc=[v for v,_ in Counter(ring).most_common(4) if v!=col and (v!=dk or dark)] or [v for v,_ in Counter(ring).most_common(3) if v!=col]
    for j in range(1,15):
        for i in range(1,15): P[y0+j][x0+i]=bgc[0]
    im,dr=newdraw(16,16)
    dr.text((8,8),t,font=ImageFont.truetype(W('Galmuri11.ttf'),12),fill=255,anchor='mm'); A=im.load()
    for j in range(16):
        for i in range(16):
            if A[i,j]>=128: P[y0+j][x0+i]=col
def glyph(P,pal3,L,x0,y0,ch):
    # 16x16 cell: clear to bg(index of P[y0][x0] corner) and draw bold gold glyph with black outline
    bg=0
    old=[P[y0+j][x0+i] for j in range(16) for i in range(16)]
    from collections import Counter
    cnt=Counter(v for v in old if v!=bg)
    dark=min(range(len(pal3)),key=lambda i:L[i] if i!=bg else 999)
    br=sorted([v for v in cnt if v!=dark],key=lambda i:-L[i])
    hi=br[0] if br else dark; mid=br[len(br)//2] if br else hi
    im,dr=newdraw(16,16)
    f=ImageFont.truetype(W('Galmuri11-Bold.ttf'),12)
    dr.text((8,8),ch,font=f,fill=255,anchor='mm'); A=im.load()
    for j in range(16):
        for i in range(16): P[y0+j][x0+i]=bg
    for j in range(16):
        for i in range(16):
            if A[i,j]>=110:
                for dj in (-1,0,1):
                    for di in (-1,0,1):
                        pass
    for j in range(16):
        for i in range(16):
            if A[i,j]>=110: P[y0+j][x0+i]=hi
def title(sub=0x40040,text='노부나가의 야망 · 열풍전 with 파워업키트',cy=214,fs=15):
    d=getf(G); typ,pal,imgs=nb8.parse(bytes(d[sub:])); o,x,y,w,h,px=imgs[0]; o+=sub+12
    Wd=w*2; L=[lum(c) for c in pal]
    hi=max(range(len(pal)),key=lambda i:L[i]); dk=min(range(len(pal)),key=lambda i:L[i])
    im,dr=newdraw(Wd,h)
    dr.text((Wd//2,cy),text,font=ImageFont.truetype(W('Galmuri14.ttf'),fs),fill=255,anchor='mm')
    A=im.load(); ol=im.filter(ImageFilter.MaxFilter(5)).load()
    for j in range(h):
        for i in range(Wd):
            if A[i,j]>=128: d[o+j*Wd+i]=hi
if __name__=='__main__':
    title()
    for k,v in JOBS.items(): process(k,v)
    for k,sub,v in PSPJOBS: process(k,v,sub)
    process(G,cmd_cells(),0xa3520)
    process('MDATA1/MAINWIN.NB8',cmd_cells(),0x7ac0)
    process('MDATA1/MAINWIN.NB8',cmd_cells(),0xab00)
    for k,sub,v in OTHER: process(k,v,sub)
    res=[]
    for rel,d in FILES.items():
        out=W('work/build/img/'+os.path.basename(rel)); os.makedirs(os.path.dirname(out),exist_ok=True)
        open(out,'wb').write(d); res.append(('/PSP_GAME/USRDIR/'+rel,out))
    json.dump(res,open(W('work/build/img.json'),'w'))
    print(res)
