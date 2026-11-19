"""번역 JSON → 빌드 데이터 적용"""
import os,re,json,glob,struct
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W=lambda p:os.path.join(ROOT,p)
TAG=re.compile(r'\{([0-9a-f]*)\}')

def from_tagged(s,enc):
    out=bytearray();pos=0
    for m in TAG.finditer(s):
        out+=enc(s[pos:m.start()]).replace(b'\n',b'\x0a'); out+=bytes.fromhex(m.group(1)); pos=m.end()
    out+=enc(s[pos:]).replace(b'\n',b'\x0a')
    return bytes(out)

def msg_patch(enc,log):
    def f(blocks):
        n=0
        for p in sorted(glob.glob(W('work/trans/msg/b*.json'))):
            b=int(os.path.basename(p)[1:3])
            for e in json.load(open(p,encoding='utf-8')):
                if e['ko'] and e['ko']!=e['jp']:
                    blocks[b][e['id']]=from_tagged(e['ko'],enc); n+=1
        log.append(f'msg {n}')
    return f

def boot_patch(B,K,enc,refs,patch_hl,log):
    J=json.load(open(W('work/trans/boot/all.json'),encoding='utf-8'))
    if os.path.exists(W('work/trans/boot/extra.json')): J+=json.load(open(W('work/trans/boot/extra.json'),encoding='utf-8'))
    J+=MANUAL
    inpl=rel=skip=0
    hiuse={}
    for t,L in refs.items():
        for r in L:
            if r[0]=='hl': hiuse.setdefault(r[1],set()).add(t)
    def safe(a): return all(r[0]=='w' or hiuse[r[1]]=={a} for r in refs[a])
    for e in J:
        ko=e.get('ko')
        if not ko: continue
        fo=int(e['off'],16); a=fo-0x54
        data=enc(ko,adig=bool(re.search(r'[0-9%]',e['jp'])))
        if len(data)<=e['cap']:
            old=len(B.b[fo:fo+e['cap']+1])
            B.b[fo:fo+e['cap']+1]=data+b'\0'*(e['cap']+1-len(data)); inpl+=1
        elif e['ref'] and a in refs and safe(a):
            na=K.put(data+b'\0')
            for r in refs[a]:
                if r[0]=='hl': patch_hl(B,r[1],r[2],na)
                else: B.setw(r[1],na)
            rel+=1
        else:
            # 잘라서 넣기 (2바이트 경계)
            d=data[:e['cap']]
            i=0;cut=0
            while i<len(d):
                step=2 if d[i]>=0x81 and d[i]!=0x20 and not (0xa1<=d[i]<=0xdf) else 1
                if i+step>len(d): break
                i+=step; cut=i
            B.b[fo:fo+e['cap']+1]=d[:cut]+b'\0'*(e['cap']+1-cut); skip+=1
    log.append(f'boot inplace {inpl} reloc {rel} trunc {skip}')

MANUAL=[{'off':'2c3c20','jp':'%s家','cap':7,'ref':True,'ko':'%s가'},{'off':'2e1e64','jp':'金銭','cap':7,'ref':True,'ko':'금전'}]
NAMES={'general':('SCES',0,80,[(0,9),(9,9)]),
 'castle':('SCES',0x139a0,0x5e,[(0,9)]),
 'item':('SCEF',0x1518,0x14,[(0,17)]),
 'rank':('SCEF',0x3070,0xc,[(0,11)]),
 'province':('SCEF',0x3c28,0xf,[(0,9)]),
 'title':('SCEF',0x3e80,0xe,[(0,13)])}
LIMIT={'general':0x139a0,'castle':0x17600,'item':0x3070,'rank':0x3c28,'province':0x3e80,'title':0x40b0}
def names_patch(enc,log):
    SD=W('work/iso/PSP_GAME/USRDIR/SDATA1')
    files={}
    for k in range(11):
        for pre in ('SCES','SCEF'):
            fn='%s%02d.NB8'%(pre,k); files[fn]=bytearray(open(os.path.join(SD,fn),'rb').read())
    cnt=0
    for name,(pre,st,stride,fields) in NAMES.items():
        J=json.load(open(W(f'work/trans/names/{name}.json'),encoding='utf-8'))
        dic={}
        for e in J:
            if not e['ko']: continue
            jp=e['jp'].split(' ') ; ko=e['ko'].split(' ')
            if len(fields)==2:
                if len(jp)==2 and len(ko)>=2: dic[tuple(jp)]=(ko[0],' '.join(ko[1:]))
            else: dic[(e['jp'],)]=(e['ko'],)
        for k in range(11):
            d=files['%s%02d.NB8'%(pre,k)]
            a=st
            while a+stride<=min(len(d),LIMIT[name]+ (stride if name=='general' else 0)):
                key=[]
                for o,l in fields:
                    s=bytes(d[a+o:a+o+l]).split(b'\0')[0]
                    try: key.append(s.decode('cp932'))
                    except: key=None;break
                if key and tuple(key) in dic:
                    for fi,((o,l),v) in enumerate(zip(fields,dic[tuple(key)])):
                        b=enc(v)[:l-1]
                        if name=='general' and fi==0 and len(b)<=l-2: b+=b' '
                        d[a+o:a+o+l]=b+b'\0'*(l-len(b))
                    cnt+=1
                a+=stride
                if name=='general' and a>=0x139a0: break
    out=[]
    os.makedirs(W('work/build/SDATA1'),exist_ok=True)
    for fn,d in files.items():
        p=W('work/build/SDATA1/'+fn); open(p,'wb').write(d)
        out.append(('/PSP_GAME/USRDIR/SDATA1/'+fn,p))
    log.append(f'names {cnt}')
    return out
