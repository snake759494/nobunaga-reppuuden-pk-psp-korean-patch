R={n:i for i,n in enumerate('zero at v0 v1 a0 a1 a2 a3 t0 t1 t2 t3 t4 t5 t6 t7 s0 s1 s2 s3 s4 s5 s6 s7 t8 t9 k0 k1 gp sp fp ra'.split())}
def I(op,rs,rt,imm): return (op<<26)|(R[rs]<<21)|(R[rt]<<16)|(imm&0xffff)
def addiu(rt,rs,imm): return I(9,rs,rt,imm)
def ori(rt,rs,imm): return I(13,rs,rt,imm)
def lui(rt,imm): return I(15,'zero',rt,imm)
def sw(rt,off,base): return I(43,base,rt,off)
def lw(rt,off,base): return I(35,base,rt,off)
def addu(rd,rs,rt): return (R[rs]<<21)|(R[rt]<<16)|(R[rd]<<11)|0x21
def subu(rd,rs,rt): return (R[rs]<<21)|(R[rt]<<16)|(R[rd]<<11)|0x23
def jr(rs): return (R[rs]<<21)|8
def jalr(rs,rd='ra'): return (R[rs]<<21)|(R[rd]<<11)|9
def bal(off): return (1<<26)|(17<<16)|(off&0xffff)
def bltz(rs,off): return (1<<26)|(R[rs]<<21)|(off&0xffff)
def move(rd,rs): return addu(rd,rs,'zero')
NOP=0
def li32(rt,v): return [lui(rt,(v>>16)&0xffff),ori(rt,rt,v&0xffff)]
