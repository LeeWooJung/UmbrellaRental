from socket import*
import sys
import time
import json
from collections import OrderedDict


server_ip = "localhost"
server_port = 50007

serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.bind((server_ip,server_port))
serverSocket.listen(2)
print('SERVER STARTED')


while True:
    hash_verify = 1
    hash_verify = str(hash_verify)

    spotID = 2
    umbID = 3

    connectionSocket, addr = serverSocket.accept()
    
    
    # get size of identification
    identification_size = connectionSocket.recv(64).decode("utf8")
    identification_size = int(identification_size)
    
    # JSON decoding Using json.loads()
    identification = connectionSocket.recv(identification_size).decode("utf8")
    
    identification = json.loads(identification)
    identification = identification["identification"]
    print "identification signal received", identification
        
    if(identification == 0x10):
        print "identification completed"
        
        # Sending ACK to RaspberryPi
        ACK = {"ACK" : 0xFF}
        
        # get size of ACK
        ACKsize = sys.getsizeof(ACK)
        ACKsize = str(ACKsize)
        ACKsize = ACKsize.rjust(8,'0')
        connectionSocket.send(ACKsize.encode("utf8"))
        time.sleep(0.5)
        
        ACK = json.dumps(ACK)
        connectionSocket.send(ACK.encode("utf8"))
        time.sleep(0.5)
        
        # get size of Hash
        Hashsize = connectionSocket.recv(64).decode("utf8")
        Hashsize = int(Hashsize)

        print " Received Hashsize is :",Hashsize
        
        hashCode = connectionSocket.recv(Hashsize).decode("utf8")
        hashCode = json.loads(hashCode)
        hashCode = hashCode["hashCode"]
        print " Receivd Hash is : ",hashCode
        
    # if Hash is correct send value
    hash_verify = json.dumps(hash_verify)
    
    # first send size of value
    hash_verify_size = sys.getsizeof(hash_verify)
    hash_verify_size = str(hash_verify_size)
    hash_verify_size = hash_verify_size.rjust(8,'0')
    
    connectionSocket.send(hash_verify_size)
    time.sleep(0.5)
    
    connectionSocket.send(hash_verify.encode("utf8"))
    time.sleep(0.5)
    
    # first send size of spotID
    
    spotID = { "spotID" : 2}
    spotID = json.dumps(spotID)
    
    spotID_size = sys.getsizeof(spotID)
    spotID_size = str(spotID_size)
    spotID_size = spotID_size.rjust(8,'0')
    
    connectionSocket.send(spotID_size.encode("utf8"))
    time.sleep(0.5)
    
    connectionSocket.send(spotID.encode("utf8"))
    time.sleep(0.5)


    # first send size of umbID
    
    umbID = { "umbID" : 3}
    umbID = json.dumps(umbID)
    
    umbID_size = sys.getsizeof(umbID)
    umbID_size = str(umbID_size)
    umbID_size = umbID_size.rjust(8,'0')
    
    connectionSocket.send(umbID_size.encode("utf8"))
    time.sleep(0.5)
    
    connectionSocket.send(umbID.encode("utf8"))
    
    connectionSocket.close()
