"""번역 검증: python tools/tcheck.py work/trans/msg/b05.json  (또는 여러 파일)"""
import json,re,sys
TAG=re.compile(r'\{([0-9a-f]*)\}')
STEM={*range(45,62),*range(69,81),*range(116,133),*range(140,153),*range(165,177),178,179,180,*range(199,205),208,217}
KANA=re.compile(r'[\u3040-\u30fa\u30fc-\u30ff\u4e00-\u9fff]')
def ops(s):
    st=[];disp=[]
    for h in TAG.findall(s):
        if len(h)%2: return None,None
        b=bytes.fromhex(h);i=0
        while i<len(b):
            if b[i]==1 and i+3<len(b) and b[i+1]==0x43:
                v=b[i+2]|b[i+3]<<8; disp.append(('C',v)); i+=4
            elif b[i]==2 and i+2<len(b) and b[i+1] in (1,2,3):
                disp.append(('V',b[i+2])); i+=3
            else: st.append(b[i]); i+=1
    return st,disp
def width(line):
    return sum(0.5 if c==' ' else 1 for c in TAG.sub('',line))
def check(e):
    jp,ko=e['jp'],e['ko']
    if ko is None: return 'ko 없음'
    sj,dj=ops(jp); sk,dk=ops(ko)
    if sk is None: return '태그 hex 오류'
    if sj!=sk: return '구조 태그 불일치'
    a=sorted(dj); b=sorted(dk)
    for x in b:
        if x in a: a.remove(x)
        else: return f'원문에 없는 표시태그 {x}'
    left=[x for x in a if not (x[0]=='C' and x[1] in STEM)]
    if left: return f'빠진 표시태그 {left}'
    if KANA.search(TAG.sub('',ko)): return '일본어 문자 잔존'
    for ln in TAG.sub('',ko).split('\n'):
        if width(ln)>e.get('maxw',99)+0.01: return f'줄폭 초과({width(ln)}>{e["maxw"]}): {ln}'
    return None
if __name__=='__main__':
    bad=0
    for f in sys.argv[1:]:
        for e in json.load(open(f,encoding='utf-8')):
            r=check(e)
            if r: bad+=1; print(f, e['id'], r)
    print('오류', bad)
