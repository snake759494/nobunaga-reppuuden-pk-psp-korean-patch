"""자동 줄바꿈 창(시나리오 설명 등): 단어 단위로 다시 줄바꿈. python tools/rewrap.py 35 18"""
import json,re,sys
TAG=re.compile(r'(\{[0-9a-f]*\})')
def tw(h):
    b=bytes.fromhex(h);n=0;i=0
    while i<len(b):
        if b[i]==0x1b: i+=2; continue
        if 0x30<=b[i]<0x7f: n+=1
        i+=1
    return n*0.5
def w(s):
    t=0
    for m in re.finditer(r'\{([0-9a-f]*)\}|.',s,re.S):
        if m.group(1) is not None: t+=tw(m.group(1))
        else:
            c=m.group(0); t+=0.5 if c==' ' or ord(c)<0x80 and c not in '.,!?()' else 1
    return t
def wrap(text,lim):
    words=text.replace('\n',' ').split(' ');out=[];cur=''
    for wd in words:
        if not wd: continue
        t=(cur+' '+wd) if cur else wd
        if w(t)<=lim: cur=t
        else:
            if cur: out.append(cur)
            while w(wd)>lim:
                k=1
                while w(wd[:k+1])<=lim: k+=1
                out.append(wd[:k]); wd=wd[k:]
            cur=wd
    if cur: out.append(cur)
    return '\n'.join(out)
b=int(sys.argv[1]); lim=float(sys.argv[2])
p='work/trans/msg/b%02d.json'%b; J=json.load(open(p,encoding='utf-8')); n=0
for e in J:
    ko=e['ko']
    if not ko or ko==e['jp']: continue
    if all(w(l)<=lim for l in ko.split('\n')): continue
    parts=re.split(r'(\{05[0-9a-f]*\})',ko)
    e['ko']=''.join(x if x.startswith('{05') or not x.strip() else wrap(x,lim) for x in parts); n+=1
json.dump(J,open(p,'w',encoding='utf-8'),ensure_ascii=False,indent=0); print('rewrapped',n)
