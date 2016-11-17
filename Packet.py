class Packet:
    '''The packet class'''
    def __init__(self):
        self.magicno = 0x497E
        self.packetType = None
        self.seqno = None
        self.dataLen = 0
        self.data = None    
           
    def setType(self, packetType):
            if (packetType == 'dataPacket') or (packetType == 'acknowledgementPacket'):
                self.packetType = packetType                               
            else:
                print("Error: packet type Error.\n")
                self.reset()
    
    def setSeqno(self, seqno):
        try:
            self.seqno = seqno
        except TypeError:
            print("Error: invalid seqno\n")
            self.reset()
            
    def setDataLen(self, dataLen):
        try:
            if (int(dataLen) >= 0) and (int(dataLen) <= 512):
                self.dataLen = dataLen
            else:
                raise ValueError            
        except ValueError:
            print("Error: invalid dataLen\n")
            self.reset()
            
    def setData(self, data):
        self.data = data
        
    def reset(self):
        self.packetType = None
        self.seqno = None
        self.dataLen = None
        self.data = None   