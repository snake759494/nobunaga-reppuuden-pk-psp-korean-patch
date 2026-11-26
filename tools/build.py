import sys,os,struct,json,shutil,re
sys.path.insert(0,os.path.dirname(__file__))
from elf import Boot,build_refs,s16
from stub import make_stub
import msg, kfont
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W=lambda p:os.path.join(ROOT,p)
ORIG_ISO=W('Nobunaga no Yabou - Reppuuden with Power Up Kit (Japan) (v1.02).iso')
OUT_ISO=W('Nobunaga no Yabou - Reppuuden with Power Up Kit (Korean).iso')
KBASE=0xcbd000           # extension area (old memsz 0xcbc800, libc vars live just past it)
STUB_AT=0x2c0a3c         # module offset (file 0x2c0a90) - fatal error strings area
STUB_END=0x2c0b54
PATH_STR=b'disc0:/PSP_GAME/USRDIR/KOR.BIN\0'
IO_OPEN,IO_READ,IO_CLOSE=0x2b0910,0x2b08d0,0x2b08e8
DCACHE_WBINV=0x2b0ac0   # UtilsForUser sceKernelDcacheWritebackInvalidateAll 스텁
ENTRY=0x1eec8
MODSTART_PTR=0x2b1190

class KorBin:
    def __init__(s): s.data=bytearray()
    def put(s,b,align=4):
        while len(s.data)%align: s.data.append(0)
        a=KBASE+len(s.data); s.data+=b; return a

def patch_hl(B,hi,lo,tgt):
    h=B.w(hi); l=B.w(lo)
    B.setw(hi,(h&0xffff0000)|(((tgt+0x8000)>>16)&0xffff))
    B.setw(lo,(l&0xffff0000)|(tgt&0xffff))

def enc_factory():
    cmap=json.load(open(W('work/build/charmap.json'),encoding='utf-8'))
    punct={',':0x8143,'.':0x8144,'!':0x8149,'?':0x8148,'~':0x8160,'…':0x8163,'·':0x8145,
           '(':0x8169,')':0x816a,':':0x8146,'-':0x815b,'"':0x8168,"'":0x8166,'×':0x817e}
    def enc(s,adig=False):
        out=bytearray()
        # printf format specifiers (e.g. %-21s) must stay raw ASCII
        parts=re.split(r'(%[-+ #0-9.]*[a-zA-Z%])',s)
        if len(parts)>1:
            for k,p in enumerate(parts):
                out+=p.encode('ascii') if k%2 else enc(p,adig)
            return bytes(out)
        for ch in s:
            if ch in cmap: c=cmap[ch]; out+=bytes([c>>8,c&255])
            elif ch==' ': out.append(0x20)
            elif ch in punct: c=punct[ch]; out+=bytes([c>>8,c&255])
            elif '0'<=ch<='9' and not adig: out+=chr(0xff10+ord(ch)-48).encode('cp932')
            elif ord(ch)<0x20 or 0x80<=ord(ch)<0x100: out.append(ord(ch))
            else: out+=ch.encode('cp932')
        return bytes(out)
    return enc

def build(msg_patch=None,test=False):
    kfont.build()
    B=Boot(W('work/iso/PSP_GAME/SYSDIR/BOOT.BIN'))
    K=KorBin()
    codes=open(W('work/build/font_codes.bin'),'rb').read()
    bits=open(W('work/build/font_bits.bin'),'rb').read()
    n=len(codes)//2
    ca=K.put(codes); ba=K.put(bits)
    patch_hl(B,0x2b07f8,0x2b0818,ca); patch_hl(B,0x2b07fc,0x2b081c,ba)
    assert n<0x8000
    B.setw(0x2b07e4,(B.w(0x2b07e4)&0xffff0000)|n)
    enc=enc_factory(); LOG=[]
    import apply
    apply.boot_patch(B,K,enc,build_refs(B),patch_hl,LOG)
    import josa; josa.install(B,K,enc,LOG)
    if msg_patch is None: msg_patch=apply.msg_patch(enc,LOG)
    global EXTRA_FILES
    EXTRA_FILES=apply.names_patch(enc,LOG)+IMG_FILES()
    # ---- message
    m=open(W('work/iso/PSP_GAME/USRDIR/MDATA1/MESSAGE.NB8'),'rb').read()
    blocks=msg.blocks(m,bytes(B.b))
    if msg_patch: msg_patch(blocks)
    newm,tab,b0size,maxblk=msg.pack(blocks)
    for i,v in enumerate(tab): struct.pack_into('<I',B.b,msg.BOOT_TAB+4*i,v)
    # block0 resident size param (addiu a1,zero,0x2e19 @0x68458)
    B.setw(0x68458,(B.w(0x68458)&0xffff0000)|b0size)
    # message buffer -> extension area (after KOR data)
    kdata_end=KBASE+len(K.data)
    mbuf=(kdata_end+63)&~63
    bufsize=((b0size+3)&~3)+maxblk+0x100
    relocate_msgbuf(B,mbuf)
    memsz=mbuf+bufsize
    memsz=(memsz+0xff)&~0xff
    # ---- stub & entry
    path_off=STUB_AT
    stub_code_at=STUB_AT+len(PATH_STR); stub_code_at=(stub_code_at+3)&~3
    code=make_stub(stub_code_at,path_off,KBASE,len(K.data),IO_OPEN,IO_READ,IO_CLOSE,ENTRY,DCACHE_WBINV)
    assert stub_code_at+len(code)<=STUB_END,(hex(stub_code_at+len(code)))
    B.b[STUB_AT+0x54:STUB_AT+0x54+len(PATH_STR)]=PATH_STR
    B.b[stub_code_at+0x54:stub_code_at+0x54+len(code)]=code
    B.setw(MODSTART_PTR,stub_code_at)
    struct.pack_into('<I',B.b,0x18,stub_code_at)
    phoff=struct.unpack_from('<I',B.b,0x1c)[0]
    struct.pack_into('<I',B.b,phoff+20,memsz)
    os.makedirs(W('work/build'),exist_ok=True)
    open(W('work/build/BOOT.BIN'),'wb').write(B.b)
    open(W('work/build/KOR.BIN'),'wb').write(K.data)
    open(W('work/build/MESSAGE.NB8'),'wb').write(newm)
    print(LOG);print('kor',len(K.data),'memsz',hex(memsz),'b0',hex(b0size),'maxblk',hex(maxblk))
    make_iso()

MSGBUF_OLD=0xbe322c
def relocate_msgbuf(B,new):
    refs=build_refs(B)
    cnt=0
    for r in refs.get(MSGBUF_OLD,[]):
        if r[0]=='hl': patch_hl(B,r[1],r[2],new); cnt+=1
        else: B.setw(r[1],new); cnt+=1
    assert cnt>=10,cnt
    # check no other references fall inside old buffer (offset accesses)
    return cnt

def make_iso():
    import isobuild
    tmp=OUT_ISO+'.tmp'
    iso=isobuild.Iso(ORIG_ISO,tmp)
    boot=open(W('work/build/BOOT.BIN'),'rb').read()
    iso.replace('/PSP_GAME/SYSDIR/EBOOT.BIN',boot)
    iso.replace('/PSP_GAME/SYSDIR/BOOT.BIN',boot)
    iso.replace('/PSP_GAME/USRDIR/MDATA1/MESSAGE.NB8',open(W('work/build/MESSAGE.NB8'),'rb').read())
    for p,f in getattr(sys.modules[__name__],'EXTRA_FILES',[]):
        iso.replace(p,open(f,'rb').read())
    iso.add('/PSP_GAME/USRDIR','KOR.BIN',open(W('work/build/KOR.BIN'),'rb').read())
    iso.close()
    os.replace(tmp,OUT_ISO)

def IMG_FILES():
    p=W('work/build/img.json')
    L=[tuple(x) for x in json.load(open(p))] if os.path.exists(p) else []
    for n in ('NOBUNAGA.PMF','OPENING.PMF'):   # 한글 자막 입힌 영상
        mv=W('work/trans/movie/'+n)
        if os.path.exists(mv): L.append(('/PSP_GAME/USRDIR/MOVIE/'+n,mv))
    return L
if __name__=='__main__': build()
