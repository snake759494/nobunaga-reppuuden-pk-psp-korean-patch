import capstone,sys,re
d=open('work/iso/PSP_GAME/SYSDIR/BOOT.BIN','rb').read()
TEXT=d[0x54:0x54+0x2b08b0]
md=capstone.Cs(capstone.CS_ARCH_MIPS,capstone.CS_MODE_MIPS32+capstone.CS_MODE_LITTLE_ENDIAN)
def dis(a,n):
    for i in md.disasm(TEXT[a:a+4*n],a): print('%06x: %s %s'%(i.address,i.mnemonic,i.op_str))
if __name__=='__main__':
    if sys.argv[1]=='imm':
        import struct
        vals=[int(x,0) for x in sys.argv[2:]]
        for a in range(0,len(TEXT),4):
            w=struct.unpack_from('<I',TEXT,a)[0]
            if (w&0xffff) in vals and (w>>26) in (8,9,10,11,12,13,15): print(hex(a),hex(w))
    else: dis(int(sys.argv[1],16),int(sys.argv[2]))
