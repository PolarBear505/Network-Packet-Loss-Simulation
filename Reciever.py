'''Receiver Program'''

import sys, socket, os.path, pickle, packet

def receiver():
    '''Program that receives UDP.'''
    
    HOST = '127.0.0.1'
    inPort = setPortNumber("ReceiverIn Socket")
    outPort = setPortNumber("ReceiverOut Socket")
    channelInPort = setPortNumber("ChannelReceiverIn Socket")
    destination = input("Enter destination file: ")
    
    channelInAddress = (HOST, channelInPort)
    
    if os.path.isfile(destination):
        sys.exit("Destination file already exists. Program aborted.")
    else:
        #This section creates the two sockets and binds them
        try:
            inSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            outSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            print('Sockets Created Successfully')
        except socket.error as msg :
            print('Failed To Create Sockets')
            print(msg)
            sys.exit("Program Aborted.")    
            
        try:
            inSocket.bind((HOST, inPort))
            outSocket.bind((HOST, outPort))
            print('Sockets Binded Successfully')
        except socket.error as msg:
            print('Failed To Bind Sockets')
            print(msg)
            sys.exit("Program Aborted.")     
         
        #This section deals with the connecting socket   
        try:
            outSocket.connect(channelInAddress)
            print("Remote Socket Connected Successfully")
        except socket.error as msg:
            print('Failed To Connect Remote Socket')
            print(msg)
            sys.exit("Program Aborted.")
            
        
        print("Receiver Program Running...")
        file = open(destination, 'a')
        expected = 0
        while(1):
            inPacket = inSocket.recvfrom(1024)
            print("Packet Received")
            data = pickle.loads(inPacket[0])
            ##We subtract 33 here as the byte header in python is 33 bytes
            print("Received " + str(sys.getsizeof(data.data)-33) + " bytes of data")
            if data.magicno == 0x497E and data.packetType == 'dataPacket':      
                if data.seqno != expected:
                    outData = packet.Packet()
                    outData.setType('acknowledgementPacket')
                    outData.setSeqno(data.seqno)
                    outPacket = pickle.dumps(outData)
                    try:
                        outSocket.sendto(outPacket, (HOST, channelInPort))
                        print("Packet sent but not written")
                    except socket.error as msg:
                        print('Failed To Send Packet')
                        print(msg)
                        sys.exit("Program Aborted.")                           
                else:
                    expected = 1 - expected
                    outData = packet.Packet()
                    outData.setType('acknowledgementPacket')
                    outData.setSeqno(data.seqno)
                    outPacket = pickle.dumps(outData)
                    try:
                        outSocket.sendto(outPacket, (HOST, channelInPort))
                        print("Packet sent")
                    except socket.error as msg: 
                        print('Failed To Send Packet')
                        print(msg)
                        sys.exit("Program Aborted.")  
                    if data.dataLen > 0: #if there is data to be written
                        print("Writing")
                        string = data.data.decode()
                        file.write(string)
                    else:
                        file.close()
                        inSocket.close()
                        outSocket.close()
                        sys.exit("Data transfer complete.")
                        
def setPortNumber(socket):
    '''Prompts user to enter a port number for a specified socket.'''
    while True:
        try:
            portNumber = int(input("Enter a port number for the "\
                             + socket + ": "))
            if not ((portNumber >= 1024) and (portNumber <= 64000)):
                raise ValueError
        except ValueError:
            print("Invalid port number. Must be in range between 1024 and 64000.")
            continue
        break
    return portNumber

receiver()