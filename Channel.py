'''The Channel Program'''

import sys, socket, packet, pickle, select, random

def channel():
    '''The main function'''
    
    HOST = '127.0.0.1'
    #This section recieves the parameters from the terminal
    ##The 4 Channel ports
    channelSenderInPort = setPortNumber("ChannelSenderIn Socket")
    channelSenderOutPort = setPortNumber("ChannelSenderOut Socket")
    channelReceiverInPort = setPortNumber("ChannelReceiverIn Socket")
    channelReceiverOutPort = setPortNumber("ChannelReceiverOut Socket")
    
    ##The 2 connecting ports
    senderInPortNumber = setPortNumber("SenderIn Socket")
    senderInAddress = (HOST, senderInPortNumber)
    ReceiverInPortNumber = setPortNumber("ReceiverIn Socket")
    ReceiverInAddress = (HOST, ReceiverInPortNumber)
    
    ##The packet loss rate
    packetLossRate = setPacketLossRate()
    
    #This section creates the 4 sockets and binds them
    try :
        channelSenderInSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        channelSenderOutSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        channelReceiverInSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        channelReceiverOutSocket =  socket.socket(socket.AF_INET,socket.SOCK_DGRAM)      
        print('Sockets Created Successfully')
    except socket.error as msg :
        print('Failed To Create Sockets')
        print(msg)
        sys.exit("Program Aborted.")    
    
    try:
        channelSenderInSocket.bind((HOST, channelSenderInPort))
        channelSenderOutSocket.bind((HOST, channelSenderOutPort))
        channelReceiverInSocket.bind((HOST, channelReceiverInPort))
        channelReceiverOutSocket.bind((HOST, channelReceiverOutPort))
        print('Sockets Binded Successfully')
    except socket.error as msg:
        print('Failed To Bind Sockets')
        print(msg)
        sys.exit("Program Aborted.")
        
        
    #This section deals with the connecting sockets
    try:
        channelSenderOutSocket.connect(senderInAddress)
        channelReceiverOutSocket.connect(ReceiverInAddress)
        print("Remote Sockets Connected Successfully")
    except socket.error as msg:
        print('Failed To Connect Remote Sockets')
        print(msg)
        sys.exit("Program Aborted.")
    
    
    #This section deals with the sending and receiving of packets
    ##These are the types of input select is looking for
    theInput = [channelSenderInSocket, channelReceiverInSocket, sys.stdin]
    
    ##The Expected MagicNo
    
    running = 1
    while running:
        print("Channel Program Running...   (Type Anything To Exit Program)")
        print('')
        inputready, outputready, exceptready = select.select(theInput,[],[])
        for item in inputready:
            
            ##This deals with data recieved from the Sender
            if item == channelSenderInSocket:
                ##Recieves the data and informs terminal
                recievedData = channelSenderInSocket.recvfrom(1024)
                data = pickle.loads(recievedData[0])
                address = recievedData[1]
                print("Packet recieved from Sender") 
                print("Sender Address: " + str(address))
                
                ##Checks the magicno field
                if data.magicno != 0x497E:
                    print("MagicNo is Different!")
                    print("Dropping Packet")
                    break
                else:
                    print("MagicNo is as expected")
                
                ##Applys the packet loss rate
                randomNumber = random.random()
                print("Your random number is: " + str(randomNumber))
                if randomNumber < packetLossRate:
                    print("Dropping Packet")
                    break
                
                ##Sends the data to the Receiver
                packetToSend = pickle.dumps(data)
                try:
                    channelReceiverOutSocket.sendto(packetToSend, ReceiverInAddress)
                    print("Packet Sent to Receiver")
                except socket.error as msg:
                    ##This occurs when the last acknowledgement packet from the
                    ##last acknowledgement packet from the receiver is dropped
                    ##hence, a deadlock occurrs                    
                    channelSenderInSocket.close()
                    channelSenderOutSocket.close()
                    channelReceiverInSocket.close()
                    channelReceiverOutSocket.close()                    
                    sys.exit("Program Closed")                   

                
            ##This deals with data sent from the Receiver    
            elif item == channelReceiverInSocket:
                ##Recieves the packet and informs terminal
                recievedData = channelReceiverInSocket.recvfrom(1024)
                data = pickle.loads(recievedData[0])
                address = recievedData[1]
                print("Packet recieved from Receiver")
                print("Receiver Address: " + str(address))
                
                ##Checks the magicno field
                if data.magicno != 0x497E:
                    print("MagicNo is Different!")
                    print("Dropping Packet")
                    break
                else:
                    print("MagicNo is as expected")  
                    
                ##Applys the packet loss rate
                randomNumber = random.random()
                print("Your random number is: " + str(randomNumber))
                if randomNumber < packetLossRate:
                    print("Dropping Packet")
                    break                
                
                ##Sends the packet to the sender
                packetToSend = pickle.dumps(data)
                try:
                    channelSenderOutSocket.sendto(packetToSend, senderInAddress)
                    print("Packet Sent to Sender") 
                except socket.error as msg:
                    ##This occurs when the last acknowledgement packet from the
                    ##last acknowledgement packet from the receiver is dropped
                    ##hence, a deadlock occurrs                    
                    channelSenderInSocket.close()
                    channelSenderOutSocket.close()
                    channelReceiverInSocket.close()
                    channelReceiverOutSocket.close()                    
                    sys.exit("Program Closed")                   

            ##This terminates the program
            elif item == sys.stdin:
                print("Closing Program")
                junk = sys.stdin.readline()
                running = 0
    
    #This section closes the sockets once the program finishes    
    channelSenderInSocket.close()
    channelSenderOutSocket.close()
    channelReceiverInSocket.close()
    channelReceiverOutSocket.close()

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

def setPacketLossRate():
    '''Prompts user to enter a packet loss rate between 0 and 1.'''
    while True:
        try:
            lossRate = float(input("Enter a packet loss rate between 0 and 1: "))
            if not ((lossRate >= 0) and (lossRate < 1)):
                raise ValueError
        except ValueError:
            print("Invalid packet loss rate.")
            continue
        break
    return lossRate
        
channel()