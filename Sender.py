'''The Sender Program'''

import sys, socket, packet, pickle, select, random, os.path

def sender():
    '''The main function'''
    #This section receives the parameters from the terminal and checks them
    ##The 2 Sender ports
    senderInPort = setPortNumber("SenderIn Socket")
    senderOutPort = setPortNumber("SenderOut Socket")
    
    ##The connecting port
    channelSenderInPortNumber = setPortNumber("ChannelSenderIn Socket")
    channelSenderInAddress = ('127.0.0.1', channelSenderInPortNumber)  
    
    ##A file name
    fileName = input("Please enter a file name: ")
    
    ##Tests file name
    try: 
        os.path.isfile(fileName)
    except:
        sys.exit("Target File Does Not Exist. Program Aborted.")    
    
    #This section creates the 4 sockets and binds them
    try:
        senderInSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        senderOutSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print('Sockets Created Successfully')
    except socket.error as msg :
        print('Failed To Create Sockets')
        print(msg)
        sys.exit("Program Aborted.")  
            
    try:
        senderInSocket.bind(('127.0.0.1', senderInPort))
        senderOutSocket.bind(('127.0.0.1', senderOutPort))
        print('Sockets Binded Successfully')
    except socket.error as msg:
        print('Failed To Bind Sockets')
        print(msg)
        sys.exit("Program Aborted.")    
            
    #This section deals with the connecting socket
    try:
        senderOutSocket.connect(channelSenderInAddress)
        print("Remote Socket Connected Successfully")
    except socket.error as msg:
        print('Failed To Connect Remote Socket')
        print(msg)
        senderInSocket.close()
        senderOutSocket.close()        
        sys.exit("Program Aborted.")
    
    ##The two local variables initialised    
    nextVariable = 0
    exitFlag = False  
    
    theFile = open(fileName, "rb")
    packetBuffer = []
    theInput = [senderInSocket]
    totalPacketsSent = 0
    print("Sender Program Running...")
    
    while not exitFlag:
        ##Reads in 512 bytes of user data
        packetData = theFile.read(512)
        ##Total number of bytes added to the packet
        bytesAdded = len(packetData)  
        if bytesAdded == 0:
            ##Creates an empty packet
            packetToBeSent = packet.Packet()
            packetToBeSent.setType("dataPacket")
            packetToBeSent.setSeqno(nextVariable)
            packetToBeSent.setDataLen(0)
            packetToBeSent.setData(bytes())
            exitFlag = True
            packetBuffer.append(packetToBeSent)
        else:
            ##Creates the data packet
            packetToBeSent = packet.Packet()
            packetToBeSent.setType("dataPacket")
            packetToBeSent.setSeqno(nextVariable)
            packetToBeSent.setDataLen(bytesAdded)
            packetToBeSent.setData(packetData)  
            packetBuffer.append(packetToBeSent)
        
        ##The inner loop    
        while len(packetBuffer) > 0:
            ##Serializes data
            packetToSend = pickle.dumps(packetBuffer[0])
            try:
                senderOutSocket.sendto(packetToSend, channelSenderInAddress)
                print("Packet Sent Successfully")
            except socket.error as msg:
                ##This occurs when the last acknowledgement packet from the
                ##last acknowledgement packet from the receiver is dropped
                ##hence, a deadlock occurrs
                print("The total packets sent are: " + str(totalPacketsSent))
                senderInSocket.close()
                senderOutSocket.close()
                senderInSocket.close()
                senderOutSocket.close()                
                sys.exit("Program Closed")
            totalPacketsSent += 1
            inputready, junk1, junk2 = select.select(theInput,[],[], 1.0)
            if len(inputready) == 0:
                print("Resending Packet")
                continue
            else:
                for item in inputready:
                    ##Receives the data and informs terminal
                    receivedData = senderInSocket.recvfrom(1024)
                    data = pickle.loads(receivedData[0])
                    address = receivedData[1]
                    print("Packet received from Channel") 
                    print("Sender Address: " + str(address))
                    
                    ##Checks the magicno field
                    if data.magicno != 0x497E:
                        print("MagicNo is Different!")
                        print("Dropping Packet")
                        continue
                    else:
                        print("MagicNo is as expected")
                    
                    ##Checks the packet type    
                    packetType = data.packetType
                    if str(packetType) != 'acknowledgementPacket':
                        print("Not acknowledgement packet!")
                        print("Dropping packet")
                        continue
                    else:
                        print("Packet type is correct")
                        
                    ##Checks the datalen field
                    dataLen = data.dataLen
                    if dataLen != 0:
                        print("Wrong data length!")
                        print("Dropping packet")
                        continue
                    else:
                        print("Datalen is correct")
                        
                    ##Checks the seqno field
                    seqNo = data.seqno
                    if seqNo != nextVariable:
                        print("SeqNo differs from next!")
                        print("Dropping packet")
                        continue
                    else:
                        print("SeqNo is the same as next")
                        nextVariable = 1 - nextVariable
                        del packetBuffer[0]
                        break
                       
    print("The total packets sent are: " + str(totalPacketsSent))
    senderInSocket.close()
    senderOutSocket.close()
    
def setPortNumber(socket):
    '''Prompts user to enter a port number for a specified socket.'''
    while True:
        try:
            portNumber = int(input("Enter a port number for the "\
                             + socket + ": "))
            if not ((portNumber >= 1024) and (portNumber <= 64000)):
                raise ValueError
        except ValueError:
            print("Invalid port number.Must be in range between 1024 and 64000.")
            continue
        break
    return portNumber

sender()