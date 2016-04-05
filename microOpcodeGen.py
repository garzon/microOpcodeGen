from microOp import *
    
# DEFINE YOUR MICRO-OPS BELOW ======================

# some helper functions
def sendIR():
    '''sendIR:
    T1:
    (PC) --MC=00--> AB;
    (M) --CRDX=0--> DB --GI=0--> IR;
    (PC)+1 --PINC=0--> PC;
    '''
    callInThisBeat(['mxc0', 'mxc1', 'crdx', 'gi', 'pinc'])

def getOpHelper():
    '''
    getOPs:
    T0:
    sendIR();
    MPLD = 0;
    '''
    # T0:
    mpld()
    sendIR()

def sendAddrH():
    '''sendAddrH:
    T1:
    (PC) --MC=00--> AB;
    (M) --CRDX=0--> DB --GA1=0--> ADRH;
    (PC)+1 --PINC=0--> PC;
    '''
    callInThisBeat(['mxc0', 'mxc1', 'crdx', 'ga1', 'pinc'])
    
def sendAddrL():
    '''sendAddrL:
    T1:
    (PC) --MC=00--> AB;
    (M) --CRDX=0--> DB --GA2=0--> ADRL;
    (PC)+1 --PINC=0--> PC;
    '''
    callInThisBeat(['mxc0', 'mxc1', 'crdx', 'ga2', 'pinc'])
    
def calcRel8():
    '''
    T1:
    (PCH) --MB=01, OB=0--> DB --GA1=0--> ADRH;
    T2:
    (PCL) --MB=10, OB=0--> DB --GC=0--> ACT;
    T3: 
    (ACT)+1 --S=110--> ALU --MB=00, OB=0--> DB --GC=0--> ACT;
    T4:
    (PC) --MC=00--> AB;
    (M) --CRDX=0--> DB --GT=0--> TMP;
    (PC)+1 --PINC=0--> PC;
    T5:
    ACT+TMP --S=000--> ALU --MB=00, OB=0--> DB --GA2=0--> ADRL;
    '''
    callInThisBeat(['mxb1', 'ob', 'ga1'])
    callInThisBeat(['mxb0', 'ob', 'gc'])
    callInThisBeat(['s0', 'mxb1', 'mxb0', 'ob', 'gc'])
    callInThisBeat(['mxc0', 'mxc1', 'crdx', 'gt', 'pinc'])
    callInThisBeat(['s2', 's1', 's0', 'mxb1', 'mxb0', 'ob', 'ga2'])
    
def sendAddr():
    sendAddrH()
    sendAddrL()
    
def getOpAtLast(f):
    def wrapper():
        f()
        getOpHelper()
    wrapper.__name__ = f.__name__
    return wrapper
    
# MICRO-OP BEGIN
@asm_instruction
def getOp():
    getOpHelper()
    
@asm_instruction
@getOpAtLast
def LD():
    '''(007)LD Ai, addr:
    T1, T2: sendAddr();
    T3:
    (ADR) --MC=01--> AB;
    (MEM) --CRDX=0--> DB --WRE=0--> Ai;'''
    sendAddr()
    callInThisBeat(['mxc1', 'crdx', 'wre'])
    
@asm_instruction
@getOpAtLast
def ST():
    '''(00F)ST Ai, addr:
    T1, T2: sendAddr();
    T3:
    (ADR) --MC=01--> AB;
    (Ai) --MB=11, OB=0--> DB --CWRX=0--> M;'''
    sendAddr()
    callInThisBeat(['mxc1', 'ob', 'cwrx'])

@asm_instruction
@getOpAtLast
def MOV_A_data8():
    '''MOV Ai, #data8
    T1: 
    (PC) --MC=00--> AB;
    (M) --CRDX=0--> DB --WRE=0--> Ai;
    (PC)+1 --PINC=0--> PC;'''
    callInThisBeat(['mxc0', 'mxc1', 'crdx', 'wre', 'pinc'])
    
@asm_instruction
@getOpAtLast
def MOV_A_atA():
    '''MOV Ai, @Aj
    T1:
    (Aj) --MB=11, OB=0--> DB --GA2=0--> ADRL;
    7EH --AHS=0--> ADRH;
    T2: sendIR();
    T3:
    (ADR) --MC=01--> AB; (M) --CRDX=0--> DB --WRE=0--> (Ai);
    '''
    callInThisBeat(['ob', 'ga2', 'ahs'])
    sendIR()
    callInThisBeat(['mxc1', 'crdx', 'wre'])

@asm_instruction
@getOpAtLast
def MOV_atA_A():
    '''MOV @Aj, Ai
    T1:
    (Aj) --MB=11, OB=0--> DB --GA2=0--> ADRL;
    7EH --AHS=0--> ADRH;
    T2: sendIR();
    T3:
    (ADR) --MC=01--> AB; 
    (Ai) --MB=11, OB=0--> DB --CWRX=0--> (M);
    '''
    callInThisBeat(['ob', 'ga2', 'ahs'])
    sendIR()
    callInThisBeat(['mxc1', 'ob', 'cwrx'])

@asm_instruction
@getOpAtLast
def ADD_A_A():
    '''ADD Ai, Aj
    T1:
    (Rj) --MB=11, OB=0--> DB --GC=0--> (ACT);
    T2: sendIR();
    T3: 
    (Ri) --MB=11, OB=0--> DB --GT=0--> (TMP);
    T4:
    (TMP)+(ACT) --S=000--> ALU --MB=00, OB=0--> DB --WRE=0--> (Ri)
    COUT --CP=0, ZP=0--> CY;
    '''
    callInThisBeat(['ob', 'gc'])
    sendIR()
    callInThisBeat(['ob', 'gt'])
    callInThisBeat(['s2', 's1', 's0', 'mxb1', 'mxb0', 'ob', 'wre', 'cp', 'zp'])
    
@asm_instruction
@getOpAtLast
def SUB_A_A():
    '''SUB Ai, Aj
    T1:
    (Rj) --MB=11, OB=0--> DB --GT=0--> (TMP);
    T2: sendIR();
    T3: 
    (Ri) --MB=11, OB=0--> DB --GC=0--> (ACT);
    T4:
    (ACT)-(TMP) --S=001--> ALU --MB=00, OB=0--> DB --WRE=0--> (Ri)
    COUT --CP=0, ZP=0--> CY;
    '''
    callInThisBeat(['ob', 'gt'])
    sendIR()
    callInThisBeat(['ob', 'gc'])
    callInThisBeat(['s2', 's1', 'mxb1', 'mxb0', 'ob', 'wre', 'cp', 'zp'])
    
@asm_instruction
@getOpAtLast
def JMP_addr():
    '''JMP addr
    T1, T2: sendAddr
    T3:
    (ADR) --MC=01--> AB;
    AB --PLD210=101--> PC;
    '''
    sendAddr()
    callInThisBeat(['mxc1', 'pld1'])
    
@asm_instruction
@getOpAtLast
def JC_rel8():
    '''JC rel8
    T1, T2, T3, T4, T5: calcRel8()
    T6:
    (ADR) --MC=01--> AB;
    AB --PLD210=001--> PC;
    '''
    calcRel8()
    callInThisBeat(['mxc1', 'pld2', 'pld1'])
    
@asm_instruction
@getOpAtLast
def CALL_addr():
    '''CALL addr
    T1, T2: sendAddr
    T3:
    (SP) --MC=10--> AB;
    (PCH) --MB=01, OB=0--> DB --CWRX=0--> M;
    (SP)-1 --SSP=01--> SP;
    T4:
    (SP) --MC=10--> AB;
    (PCL) --MB=10, OB=0--> DB --CWRX=0--> M;
    (SP)-1 --SSP=01--> SP;
    T5:
    (ADR) --MC=01--> AB --PLD210=101--> PC;'''
    sendAddr()
    callInThisBeat(['mxc0', 'mxb1', 'cwrx', 'ssp0', 'ob'])
    callInThisBeat(['mxc0', 'mxb0', 'cwrx', 'ssp0', 'ob'])
    callInThisBeat(['mxc1', 'pld1'])
    
@asm_instruction
@getOpAtLast
def RET():
    '''RET
    T1: (SP)+1 --SSP=10--> SP;
    T2:
    (SP) --MC=10--> AB;
    (M) --CRDX=0--> DB --GA2=0--> ADRL;
    (SP)+1 --SSP=10--> SP;
    T3:
    (SP) --MC=10--> AB;
    (M) --CRDX=0--> DB --GA1=0--> ADRH;
    T4:
    (ADR) --MC=01--> AB --PLD210=101--> PC;'''
    callInThisBeat(['ssp1'])
    callInThisBeat(['mxc0', 'crdx', 'ga2', 'ssp1'])
    callInThisBeat(['mxc0', 'crdx', 'ga1'])
    callInThisBeat(['mxc1', 'pld1'])
    
@asm_instruction
@getOpAtLast
def PUSH():
    '''PUSH Ai
    T1:
    (SP) --MC=10--> AB;
    (Ai) --MB=11, OB=0--> DB --CWRX=0--> M;
    (SP)-1 --SSP=01--> SP;
    '''
    callInThisBeat(['mxc0', 'ob', 'cwrx', 'ssp0'])
    
@asm_instruction
@getOpAtLast
def POP():
    '''POP Ai
    T1:
    (SP)+1 --SSP=10--> SP;
    T2:
    (SP) --MC=10--> AB;
    (M) --CRDX=0--> DB --WRE=0--> (Ai);
    '''
    callInThisBeat(['ssp1'])
    callInThisBeat(['mxc0', 'crdx', 'wre'])
    
@asm_instruction
@getOpAtLast
def SUB_A_atA():
    '''SUB Ai, @Aj
    T1:
    (Aj) --MB=11, OB=0--> DB --GA2=0--> ADRL;
    7EH --AHS=0--> ADRH;
    T2:
    (ADR) --MC=01--> AB;
    (M) --CRDX=0--> DB --GT=0--> TMP;
    T3: sendIR();
    T4:
    (Ai) --MB=11, OB=0--> DB --GC=0--> ACT;
    T5:
    ACT-TMP --S=001--> ALU --MB=00, OB=0--> DB --WRE=0--> (Ai);
    COUT --CP=0, ZP=0--> CY;
    '''
    callInThisBeat(['ob', 'ga2', 'ahs'])
    callInThisBeat(['mxc1', 'crdx', 'gt'])
    sendIR()
    callInThisBeat(['ob', 'gc'])
    callInThisBeat(['s2', 's1', 'mxb1', 'mxb0', 'ob', 'wre', 'cp', 'zp'])
    
@asm_instruction
@getOpAtLast
def XOR_A_data8():
    '''XOR Ai, #data8
    T1:
    (PC) --MC=00--> AB;
    (M) --CRDX=0--> DB --GT=0--> TMP;
    (PC)+1 --PINC=0--> PC;
    T2:
    (Ai) --MB=11, OB=0--> DB --GC=0--> ACT;
    T3:
    ACT xor TMP --S=101--> ALU --MB=00, OB=0--> DB --WRE=0--> (Ai);
    '''
    callInThisBeat(['mxc0', 'mxc1', 'crdx', 'gt', 'pinc'])
    callInThisBeat(['ob', 'gc'])
    callInThisBeat(['s1', 'mxb0', 'mxb1', 'ob', 'wre'])
    
@asm_instruction
@getOpAtLast
def NEG_addr():
    '''NEG addr
    T1, T2: sendAddr()
    T3:
    (ADR) --MC=01--> AB;
    (M) --CRDX=0--> DB --GT=0--> TMP;
    T4:
    (ADR) --MC=01--> AB;
    -TMP --S=100--> ALU --MB=00, OB=0--> DB --CWRX=0--> M;
    '''
    sendAddr()
    callInThisBeat(['mxc1', 'crdx', 'gt'])
    callInThisBeat(['mxc1', 's1', 's0', 'mxb0', 'mxb1', 'ob', 'cwrx'])
    
@asm_instruction
@getOpAtLast
def JLS_rel8():
    '''JLS rel8
    T1, T2, T3, T4, T5: calcRel8()
    T6:
    (ADR) --MC=01--> AB;
    AB --PLD210=000--> PC;
    '''
    calcRel8()
    callInThisBeat(['mxc1', 'pld2', 'pld1', 'pld0'])
    
@asm_instruction
@getOpAtLast
def JNZ_rel8():
    '''JNZ rel8
    T1, T2, T3, T4, T5: calcRel8()
    T6:
    (ADR) --MC=01--> AB;
    AB --PLD210=010--> PC;
    '''
    calcRel8()
    callInThisBeat(['mxc1', 'pld2', 'pld0'])
    
@asm_instruction
@getOpAtLast
def LSR():
    '''LSR Ai
    T1:
    (Ai) --MB=11, OB=0--> DB --GC=0--> ACT;
    T2:
    ACT>>>1 --S=010--> ALU --MB=00, OB=0--> DB --WRE=0--> (Ai);
    '''
    callInThisBeat(['ob', 'gc'])
    callInThisBeat(['s2', 's0', 'mxb1', 'mxb0', 'ob', 'wre'])
    
@asm_instruction
@getOpAtLast
def JNKB_rel8():
    '''JNKB rel8
    T1, T2, T3, T4, T5: calcRel8()
    T6:
    (ADR) --MC=01--> AB;
    AB --PLD210=011--> PC;
    '''
    calcRel8()
    callInThisBeat(['mxc1', 'pld2'])
    
@asm_instruction
@getOpAtLast
def JNPB_rel8():
    '''JNPB rel8
    T1, T2, T3, T4, T5: calcRel8()
    T6:
    (ADR) --MC=01--> AB;
    AB --PLD210=100--> PC;
    '''
    calcRel8()
    callInThisBeat(['mxc1', 'pld1', 'pld0'])
    
@asm_instruction
@getOpAtLast
def CMP_A_A():
    '''CMP Ai, Aj
    T1:
    (Rj) --MB=11, OB=0--> DB --GT=0--> (TMP);
    T2: sendIR();
    T3: 
    (Ri) --MB=11, OB=0--> DB --GC=0--> (ACT);
    T4:
    (ACT)-(TMP) --S=001--> ALU;
    COUT --CP=0, ZP=0--> CY;
    '''
    callInThisBeat(['ob', 'gt'])
    sendIR()
    callInThisBeat(['ob', 'gc'])
    callInThisBeat(['s2', 's1', 'cp', 'zp'])
    
@asm_instruction
@getOpAtLast
def INIT():
    '''INIT
    T1:
    7FFFH --SSP=11--> SP;
    '''
    callInThisBeat(['ssp0', 'ssp1'])
    
# list your asm instructions
getOp(7)
LD(8)
ST(8)
MOV_A_data8(8)
MOV_A_atA(8)
MOV_atA_A(8)
ADD_A_A(8)
SUB_A_A(8)
JMP_addr(8)
JC_rel8(8)
CALL_addr(8)
RET(8)
PUSH(8)
POP(8)
SUB_A_atA(8)
XOR_A_data8(8)
NEG_addr(8)
JLS_rel8(8)
JNZ_rel8(8)
LSR(8)

JNKB_rel8(8)
JNPB_rel8(8)
CMP_A_A(8)
INIT(8)
    
print '================================================'

# print the final bytes of the micro programs
genOpcode = [i.encode('hex') for i in genOpcode]
print 'Generated bytes of micro program:'
print len(genOpcode), genOpcode

print 'In .m19 format:'
genOpcode = convertToM19(genOpcode)
print genOpcode
    
print 'Saving to ../genCode.m19'
with open('../genCode.m19','wb') as f:
    f.write(genOpcode)