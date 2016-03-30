from microOp import *
    
# DEFINE YOUR MICRO-OPS BELOW ======================

# some helper functions
def getOpHelper():
    '''
    getOPs:
    T0:
    (PC) --MC=00--> AB;
    (M) --CRDX=0--> DB --GI=0--> IR;
    (PC)+1 --PINC=0--> PC;
    MPLD = 0;
    '''
    # T0:
    callInThisBeat(['mxc0', 'mxc1', 'crdx', 'gi', 'pinc', 'mpld'])


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

    
def sendAddr():
    sendAddrH()
    sendAddrL()

def sendIR():
    mxc0()
    mxc1()
    crdx()
    gi()
    
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
    T1, T2: sendAddr;
    T3:
    (ADR) --MC=01--> AB;
    (MEM) --CRDX=0--> DB --WRE=0--> Ai;
    E0 3F FF D7
    E8 3F FF BF
    E8 3F FE FF
    1110 1010 0111 1111 1111 1111 1111 1110 = EA 7F FF FE'''
    sendAddr()
    callInThisBeat(['mxc1', 'crdx', 'wre'])
    
@asm_instruction
@getOpAtLast
def ST():
    '''(00F)ST Ai, addr:
    T1, T2: sendAddr;
    T3:
    (ADR) --MC=01--> AB;
    (Ai) --MA=0,S=011--> ALU --MB=00--> DB --CWRX=0--> M;
    E0 3F FF D7
    E8 3F FF BF
    E8 3F FE FF
    1101 1010 0111 1001 1111 0011 1111 1111 = DA 79 F3 FF'''
    sendAddr()
    callInThisBeat(['mxc1', 'mxa', 's2', 'mxb1', 'mxb0', 'cwrx'])

@asm_instruction
@getOpAtLast
def MOV_R_data8():
    '''
    T1: 
    (PC) --MC=00--> AB;
    (M) --CRDX=0--> DB --WRE=0--> Ri;
    (PC)+1 --PINC=0--> PC;'''
    callInThisBeat(['mxc0', 'mxc1', 'crdx', 'wre', 'pinc'])
    
@asm_instruction
@getOpAtLast
def MOV_R_atR():
    '''
    T1:
    (Rj) --MA=0, S=011--> ALU --MB=00--> DB --GA2=0--> ADRL;
    7EH --AHS=0--> ADRH;
    T2:
    (ADR) --MC=01--> AB; (M) --CRDX=0--> DB --GT=0--> (TMP);
    T3:
    (PC) --MC=00--> AB; (M) --CRDX=0--> DB --GI=0--> IR;
    (PC)+1 --PINC=0--> PC;
    T4:
    (TMP) --MA=1, S=011--> ALU --MB=00--> DB --WRE=0--> (Ri);
    '''
    callInThisBeat(['s2', 'mxa', 'mxb1', 'mxb0', 'ga2', 'ahs'])
    callInThisBeat(['mxc1', 'crdx', 'gt'])
    callInThisBeat(['mxc0', 'mxc1', 'crdx', 'gi', 'pinc'])
    callInThisBeat(['s2', 'mxb0' ,'mxb1', 'wre'])

@asm_instruction
@getOpAtLast
def MOV_atR_R():
    '''
    T1:
    (Ri) --MA=0, S=011--> ALU --MB=00--> DB --GT=0--> (TMP);
    T2:
    (PC) --MC=00--> AB; (M) --CRDX=0--> DB --GI=0--> IR;
    (PC)+1 --PINC=0--> PC;
    T3:
    (Rj) --MA=0, S=011--> ALU --MB=00--> DB --GA2=0--> ADRL;
    7EH --AHS=0--> ADRH;
    T4:
    (ADR) --MC=01--> AB; 
    (TMP) --MA=1, S=011--> ALU --MB=00--> DB --CWRX=0--> (M);
    '''
    callInThisBeat(['mxa', 's2', 'mxb1', 'mxb0', 'gt'])
    callInThisBeat(['mxc0', 'mxc1', 'crdx', 'gi', 'pinc'])
    callInThisBeat(['mxa', 's2', 'mxb1', 'mxb0', 'ga2', 'ahs'])
    callInThisBeat(['mxc1', 's2', 'mxb1', 'mxb0', 'cwrx'])

@asm_instruction
@getOpAtLast
def ADD_R_R():
    '''
    T1:
    (Rj) --MA=0, S=011--> ALU --MB=00--> DB --GA=0--> (A);
    (PC) --MC=00--> AB;
    T2:
    (M) --CRDX=0--> DB --GI=0--> IR;
    (PC)+1 --PINC=0--> (PC);
    (A) --GC=O--> ACT;
    T3:
    (Ri)+ACT --MA=0, S=000--> ALU --MB=00--> DB --WRE=0--> (Ri)
    '''
    callInThisBeat(['mxa','s2','mxb1','mxb0','ga','mxc1','mxc0'])
    callInThisBeat(['crdx','gi','pinc','gc'])
    callInThisBeat(['mxa','s2','s1','s0','mxb1','mxb0','wre'])
    
@asm_instruction
@getOpAtLast
def SUB_R_R():
    '''
    T1:
    (Rj) --MA=0, S=011--> ALU --MB=00--> DB --GA=0--> (A);
    (PC) --MC=00--> AB;
    T2:
    (M) --CRDX=0--> DB --GI=0--> IR;
    (PC)+1 --PINC=0--> (PC);
    (A) --GC=O--> ACT;
    T3:
    (Ri)-ACT --MA=0, S=110--> ALU --MB=00--> DB --WRE=0--> (Ri)
    '''
    callInThisBeat(['mxa','s2','mxb1','mxb0','ga','mxc1','mxc0'])
    callInThisBeat(['crdx','gi','pinc','gc'])
    callInThisBeat(['mxa','s0','mxb1','mxb0','wre'])
    
@asm_instruction
@getOpAtLast
def JMP_addr():
    '''
    T1, T2: sendAddr
    T3:
    (ADR) --MC=01--> AB;
    AB --PLD210=101--> PC;
    '''
    sendAddr()
    callInThisBeat(['mxc1', 'pld1'])
    
@asm_instruction
@getOpAtLast
def CALL_addr():
    '''
    T1, T2: sendAddr
    T3:
    (SP) --MC=10--> AB;
    (PCH) --MB=01--> DB --CWRX=0--> M;
    (SP)-1 --SSP=01--> SP;
    T4:
    (SP) --MC=10--> AB;
    (PCL) --MB=10--> DB --CWRX=0--> M;
    (SP)-1 --SSP=01--> SP;
    T5:
    (ADR) --MC=01--> AB --PLD210=101--> PC;'''
    sendAddr()
    callInThisBeat(['mxc0', 'mxb1', 'cwrx', 'ssp1'])
    callInThisBeat(['mxc0', 'mxb0', 'cwrx', 'ssp1'])
    callInThisBeat(['mxc1', 'pld1'])
    
@asm_instruction
@getOpAtLast
def RET():
    pass
    
# list your asm instructions
getOp(7)
LD(8)
ST(8)
MOV_R_data8(8)
MOV_R_atR(8)
MOV_atR_R(8)
ADD_R_R(8)
SUB_R_R(8)
JMP_addr(8)
'''
JC_rel8(8)
CALL_addr(8)
RET(8)
PUSH_R(8)
POP_R(8)
SUB_R_atR(8)
XOR_R_data(8)
NEG_addr(8)
JLS_rel8(8)
JNZ_rel8(8)
LSR_R(8)'''
    
    
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