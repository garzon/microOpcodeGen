genOpcode = []

defaultOpcode = '\xff\x9f\xff\xff'
currentOpcode = defaultOpcode

opList = ['mpld', 'mxc1', 'mxc0', 'ssp1', 'ssp0', 'pinc', 'pld2', 'pld1', 'pld0', 's2', 's1', 's0', 'cp', 'zp', 'mxb1', 'mxb0', 'ob', 'ga2', 'ahs', 'ga1', 'gi', 'gt', 'gc', 'crdx', 'cwrx', 'wre'][::-1]

currentBeats = 0

def bitAnd(a, b):
   return ''.join([chr(ord(c)&ord(d)) for c, d in zip(a,b)])

def xor(a, b):
   return ''.join([chr(ord(c)^ord(d)) for c, d in zip(a,b)])
   
def globalVarInPlaceXor(globalVarName, xor_op):
    global defaultOpcode
    assert(xor(xor(bitAnd(globals()[globalVarName], xor_op), xor_op), defaultOpcode) != '\x00\x00\x00\x00')
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
    
for i, opName in enumerate(opList):
    globals()[opName] = (lambda i: lambda: globalVarInPlaceXor('currentOpcode', genRightShiftString(i)))(i)

def nextBeat():
    global currentOpcode, defaultOpcode, genOpcode, currentBeats
    genOpcode.append(currentOpcode)
    currentOpcode = defaultOpcode
    currentBeats += 1
    
def endOfInstruction():
    global currentBeats, currentOpcode, defaultOpcode
    currentBeats = 0
    currentOpcode = defaultOpcode
    
def reserve(num=1):
    global currentOpcode, defaultOpcode, genOpcode
    assert(num >= 0)
    currentOpcode = defaultOpcode
    for i in xrange(num):
        nextBeat()
    
def asm_instruction(f):
    def wrapper(opLen = None):
        global currentBeats, genOpcode
        currentBeats = 0
        f()
        opcodeDump = f.__name__ + ':\r\n'
        for i in xrange(len(genOpcode)-currentBeats, len(genOpcode)):
            opcodeDump += genOpcode[i].encode('hex') + ' '
        print opcodeDump
        if opLen is not None:
            reserve(opLen - currentBeats)
        endOfInstruction()
    wrapper.__name__ = f.__name__
    return wrapper
    
def callInThisBeat(varList):
    for i in varList:
        globals()[i]()
    nextBeat()
    
def convertToM19(opcodeList):
    res = ''
    n = len(opcodeList)
    for i in xrange(0, n, 4):
        numToPrint = min(4, n-i)
        res += 'S1'
        recordLen = numToPrint*4+3
        res += "%02X" % recordLen
        res += "%04X" % i
        checksum = (0xff - recordLen) & 0xff
        checksum = (checksum - ((i>>8) & 0xff)) & 0xff
        checksum = (checksum - (i & 0xff)) & 0xff
        for j in xrange(numToPrint):
            res += opcodeList[i+j].upper()
            for k in xrange(0, 8, 2):
                checksum = (checksum - int(opcodeList[i+j][k:k+2], 16)) & 0xff
        res += "%02X" % checksum
        res += '\r\n'
    return res + 'S9030000FC\r\n'