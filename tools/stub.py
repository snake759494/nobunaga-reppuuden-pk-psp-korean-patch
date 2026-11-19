import struct
from mips import *
def make_stub(S,path_off,kbase,ksize,io_open,io_read,io_close,entry):
    c=[]
    c+=[addiu('sp','sp',-32),sw('ra',28,'sp'),sw('a0',24,'sp'),sw('a1',20,'sp'),sw('s0',16,'sp'),sw('s1',12,'sp')]
    c+=[bal(1),NOP]
    L1=S+4*len(c)              # ra points here
    c+=li32('t0',L1)+[subu('s0','ra','t0')]          # s0=module base
    c+=li32('t0',path_off)+[addu('a0','s0','t0'),addiu('a1','zero',1),addiu('a2','zero',0)]
    c+=li32('t0',io_open)+[addu('t9','s0','t0'),jalr('t9'),NOP]
    c+=[move('s1','v0')]
    br=len(c); c+=[0,NOP]      # bltz v0, done
    c+=[move('a0','s1')]+li32('t0',kbase)+[addu('a1','s0','t0')]+li32('a2',ksize)
    c+=li32('t0',io_read)+[addu('t9','s0','t0'),jalr('t9'),NOP]
    c+=[move('a0','s1')]+li32('t0',io_close)+[addu('t9','s0','t0'),jalr('t9'),NOP]
    done=len(c)
    c[br]=bltz('v0',done-br-1)
    c+=li32('t0',entry)+[addu('t9','s0','t0'),lw('a0',24,'sp'),lw('a1',20,'sp'),lw('s1',12,'sp'),lw('s0',16,'sp'),lw('ra',28,'sp'),jr('t9'),addiu('sp','sp',32)]
    return b''.join(struct.pack('<I',x) for x in c)
