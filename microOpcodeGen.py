from microOp import *
    
# DEFINE YOUR MICRO-OPS BELOW ======================
def getOp():
    # T0:
    mxc0()
    mxc1()
    crdx()
    gi()
    pinc()
    gc()
    mpld()
    
    # T1:
    nextBeat()
    
    # T1 ~ T6: empty
    reserve(6)
    
# list your asm instructions
getOp()
    
# print the final bytes of the micro programs
print [i.encode('hex') for i in genOpcode]
    