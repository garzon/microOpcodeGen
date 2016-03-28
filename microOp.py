genOpcode = []

defaultOpcode = '\xfe\x7f\xff\xff'
currentOpcode = defaultOpcode

def xor(a, b):
   return ''.join([chr(ord(c)^ord(d)) for c, d in zip(a,b)])
   
def globalVarInPlaceXor(globalVarName, xor_op):
    globals()[globalVarName] = xor(globals()[globalVarName], xor_op)
    return None

def b32(i):
    c1 = chr(i & 0xff)
    c2 = chr((i >> 8) & 0xff)
    c3 = chr((i >> 16) & 0xff)
    c4 = chr((i >> 24) & 0xff)
    return c4 + c3 + c2 + c1
   
def genRightShiftString(num):
    return b32(1 << num)

opList = ['cwrx', 'crdx', 'mpld', 'mxc1', 'mxc0', 'ssp1', 'ssp0', 'pinc', 'pld2', 'pld1', 'pld0', 'mxa', 's2', 's1', 's0', 'mxe', 'cp', 'zp', 'mxb1', 'mxb0', 'ob', 'ga2', 'ahs', 'ga1', 'gi', 'gt', 'gc', 'rrc', 'ga', 'wre'][::-1]
    
for i, opName in enumerate(opList):
    globals()[opName] = (lambda i: lambda: globalVarInPlaceXor('currentOpcode', genRightShiftString(i)))(i)

def nextBeat():
    global currentOpcode, defaultOpcode, genOpcode
    genOpcode.append(currentOpcode)
    currentOpcode = defaultOpcode
    
def reserve(num=1):
    global currentOpcode, defaultOpcode, genOpcode
    currentOpcode = defaultOpcode
    for i in xrange(num):
        nextBeat()
    