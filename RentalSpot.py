# -*- coding: utf8-*-

import io
import picamera
import zbar
import sys
import json
import threading
import time
import serial
from PIL import Image
from collections import OrderedDict
from socket import*
from threading import*


## 적외선 감지 with Arduino #########################################
#
# To setup Arduino environment visit
# https://spellfoundry.com/sleepy-pi/setting-arduino-ide-raspbian/
#
# ser = serial.Serial('/dev/ttyACM0',9600)
# while True:
#   print ser.readline()
####################################################################

## QR code to Hash Code decoding

def ScanQRcode():

    # 적외선 센서가 완료될 시 input입력 제거.
    start = input('[System] : if you want scan QR code, then input 1(other then, quit program):')
    if start == 1:
        # File Stream for image
        stream = io.BytesIO()
        
        # capture QR code from picamera to stream
        with picamera.PiCamera() as camera:
            camera.start_preview() # start capture
            time.sleep(3)
            camera.capture(stream, format = 'jpeg')
            camera.stop_preview() # end capture
            
        # use image by PIL
        stream.seek(0)
        pil = Image.open(stream).convert('L')
        
        # raw = img.tosting() is not available. use that instead
        raw = str(pil.tobytes())
        width, height = pil.size
        image = zbar.Image(width, height, 'Y800', raw)
    
        # Scan QR code
        scanner = zbar.ImageScanner()
        scanner.parse_config('enable')
        scanner.scan(image)
    
        ret = False
        
        for symbol in image:
            ret = symbol.data.decode("ascii")
        
        # delete image buffer
        del(image)
        return ret
    else:
        quit()       


while True:
    
    # 현재 라즈베리파이가 갖고있는 spotID
    # userID, umbID는 QR코드가 완성되는 즉시 QR코드에서 읽어올 것임.
    spotID = 3001

    #################################### QR코드 스캔 ########################################
    
    print ("[System] : QRcode Reading Start")
    hashCode = ScanQRcode()

    # If hashcode decoding is correct

    ############################## 유저에게서 받은 QR코드라면 UserUmb = 0 #########################
    ############################## 우산에게서 받은 QR코드라면 UserUmb = 1 #########################
    ######################### QR코드가 제대로 읽히지 않았다면 UserUmb = 2 #########################
    
    if hashCode != False:
        print ("[System] : QRcode Reading Completed")

        ################ QR코드의 앞 1바이트 읽었을 때 0 이면 유저 ##########################
        ################ QR코드의 앞 1바이트 읽었을 때 1 이면 우산 ##########################
        
        ################################# QR코드 포맷이 완성되었을 때 ##########################
        if hashCode[0] == '0':
            print ("[System] : This QRcode is from User, start Rental")
            UserUmb = 0
            userID = hashCode[1:5]
            hashCode = hashCode[5:]
           
        elif hashCode[0] == '1':
            print ("[System] : This QRcode is from Umbrella, start Receiving")
            UserUmb = 1
            umbID = hashCode[1:5]
            hashCode = hashCode[5:]
        
        #########################################################################################
        
        
    else:
        UserUmb = 2
        print ("[System] : QRcode can NOT decoded")
    print("did")
    quit()
    
    # Set Server IP & Server Port
    
    server_ip = "115.145.179.193" #115.145.179.193
    server_port = 9395 # port 9395

    #####################################################################
    ###                         대여 시나리오                         ###
    #####################################################################    
    
    while (UserUmb == 0):
        print ("[System] : Rental Senario START!")
        # Create Socket
    
        clientSocket = socket(AF_INET,SOCK_STREAM) 
        clientSocket.connect((server_ip,server_port))

            
        ####################### 대여소 최초 연결 #############################

        print ("[Rental Spot -> Main Server] : first connection")
        # R2S identification
        identification = 0x10
        R2S_RentalIden = { "command" : identification,
                           "spotID" : spotID
                           }
        R2S_RentalIden = json.dumps(OrderedDict(R2S_RentalIden))
            
        # to get bytesize of identification
        sizeofID = len(R2S_RentalIden.encode("utf8"))
        sizeofID = str(sizeofID)
        sizeofID = sizeofID.rjust(8,'0')
        
            
        # send size of ID to a server
        clientSocket.send(sizeofID.encode("utf8"))
        time.sleep(0.5)
            
        
        # R2S_RentalIden transmit
        print ("[Rental Spot -> Main Server] : Send identification")
        clientSocket.send(R2S_RentalIden.encode("utf8"))
        
                
        # if identification is completed
        # receive ACK from the server
            
        ACKsize = clientSocket.recv(8).decode("utf8")
        ACKsize = int(ACKsize)
            
        ACK = clientSocket.recv(ACKsize).decode("utf8")
        ACK = json.loads(ACK)
        ID = ACK["ID"]
        ACK = ACK["command"]
        
            
        # if ACK is completed
            
        if(ACK == 0xFF):
            print("[Main Server -> Rental Spot] : Receive ACK")

            ############################## QR코드로 읽은 해시코드 전송 ###########################
            
            command = 0x11
            R2S_SendHash = {"command" : command,
                            "spotID" : spotID,
                            "userID" : userID,
                            "hashCode" : hashCode,
                            }

            # JSON encoding USING json.dump()
            R2S_SendHash = json.dumps(OrderedDict(R2S_SendHash))
    
            # jsonString
            size = len(R2S_SendHash.encode("utf8"))
            size = str(size)
            size = size.rjust(8,'0')
            
            clientSocket.send(size)
            time.sleep(0.5)
                
            # To send hashcode
            print ("[Rental Spot -> Main Server] : Send Hashcode to Main Server decoded from QRcode")
            clientSocket.send(R2S_SendHash.encode("utf8"))


            ############################# 해싱코드 확인 후 대여해줘야할 우산 전달(만약 아닐시 우산 번호에 -1) #####################
            
            # receive hash_verify follwing receive hash_verfiysize
            hash_verify_size = clientSocket.recv(8).decode("utf8")
            hash_verify_size = int(hash_verify_size)
                
            hash_verify = clientSocket.recv(hash_verify_size).decode("utf8")        
            hash_verify = json.loads(hash_verify)

            S2R_VerifyCom = hash_verify["command"]
            check = hash_verify["umbID"]
               
            # if hash_verfiy is correct & check is not -1
            if ((S2R_VerifyCom == 0x12) & (check != -1)): 
                print("[System] : hashCode MATCHES")

                ########################## 대여 #########################
                print("[System] : Rental")

                ########################## 대여 확인 ##########################
                print("[System] : Rental Confirm")
        
                ########################## 대여 확인 후 현 대여소 상태 업데이트 ################################
                command = 0x13
                R2S_RentConfirm = {"command" : command,
                                   "spotID" : spotID,
                                   "status" : 1,
                                   "umbStorage" : 0
                                   }
                R2S_RentConfirm = json.dumps(OrderedDict(R2S_RentConfirm))

                size = len(R2S_RentConfirm.encode("utf8"))
                size = str(size)
                size = size.rjust(8,'0')

                clientSocket.send(size)
                time.sleep(0.5)

                clientSocket.send(R2S_RentConfirm.encode("utf8"))
                print ("[Rental Spot -> Main Server] : Rental Spot information UPdate")
                time.sleep(0.5)

                ######################## 연결 종료 선언 ###########################
                command = 0xF0
                
                FINsize = clientSocket.recv(8).decode("utf8")
                FINsize = int(FINsize)
                
                FIN = clientSocket.recv(FINsize).decode("utf8")
                FIN = json.loads(FIN)
                
                FIN = FIN["command"]
                if(FIN == command):
                    print("[Main Server -> Rental Spot]: Receive FIN")
                    print("[System]: quit connection")
                    clientSocket.close()
                
            elif ((S2R_VerifyCom == 0x12) & (check == -1)):
                print ("[System] : hashCode NOT MATCHES ")
                
            else: # if The HASH CODE doesn't matches with server HASH CODE
                print ("[System] : unknown Error ")
        else:
            print ("[System] : Server NOT send ACK")
                
        UserUmb = 2

    #####################################################################
    ###                         반납 시나리오                         ###
    #####################################################################
    while (UserUmb == 1):
        print ("[System] : Receiving Umbrella START!")
        
        # Create Socket
        clientSocket = socket(AF_INET,SOCK_STREAM)
        clientSocket.connect((server_ip,server_port))

        ####################### 대여소 최초 연결 #############################
        print ("[Rental Spot -> MainServer] : first connection")
        
        # R2S identification
        identification = 0x10
        R2S_RentalIden = { "command" : identification,
                           "spotID" : spotID
                           }
        R2S_RentalIden = json.dumps(OrderedDict(R2S_RentalIden))
            
        # to get bytesize of identification
        sizeofID = len(R2S_RentalIden.encode("utf8"))
        sizeofID = str(sizeofID)
        sizeofID = sizeofID.rjust(8,'0')
        
            
        # send size of ID to a server
        clientSocket.send(sizeofID.encode("utf8"))
        time.sleep(0.5)
            
        
        # R2S_RentalIden transmit
        clientSocket.send(R2S_RentalIden.encode("utf8"))
        print ("[Rental Spot -> Main Server] : Send identification")
        
                
        # if identification is completed
        # receive ACK from the server
            
        ACKsize = clientSocket.recv(8).decode("utf8")
        ACKsize = int(ACKsize)
            
        ACK = clientSocket.recv(ACKsize).decode("utf8")
        ACK = json.loads(ACK)
        ID = ACK["ID"]
        ACK = ACK["ACK"]

        # if ACK is completed
            
        if(ACK == 0xFF):
            print("[Main Server -> Rental Spot] : Receive ACK")

            ############################# 우산 반납 코드 서버에 전송 ######################
            command = 0x21
            R2S_ReturnUmbrellaCode = {"command" : command,
                                      "spotID" : spotID,
                                      "userID" : userID,
                                      "umbID" : umbID
                                      }

            R2S_ReturnUmbrellaCode = json.dumps(OrderedDict(R2S_ReturnUmbrellaCode))
            
            size = len(R2S_ReturnUmbrellaCode.encode("utf8"))
            size = str(size)
            size = size.rjust(8,'0')
            
            clientSocket.send(size)
            time.sleep(0.5)

            clientSocket.send(R2S_ReturnUmbrellaCode.encode("utf8"))
            print("[Rental Spot -> Main Server] : Send Umbrella QRcode to Main Server")

            ############################# 우산 코드 인증 및 확인 ###########################
            command = 0x22
            VerifySize = clientSocket.recv(8).decode("utf8")
            VerifySize = int(VerifySize)

            Verify = clientSocket.recv(Verifysize).decode("utf8")
            Verify = json.loads(Verify)

            # 우산코드 인증이 확인 된다면 (만약 아닐 시에 우산번호: -1)
            if ((Verify["command"] == command) & (Verify["umbID"] != -1)) :

                print ("[Main Server -> Rental Spot] : Umbrella Verified")
                print ("[System] : open the door, detect umbrella, close the door")

            elif ((Verify["command"] == command) & (Verify["umbID"] == -1)):

                print ("[System] : This is not our umbrella")

            else:

                print ("[System] : Something Error")

            ########################### 반납 최종 확인 및 최신화 #############################

            command = 0x23
            R2S_ReturnConfirm = {"command" : command,
                                 "spotID" : spotID,
                                 "umbID" : umbID,
                                 "status" : 1,
                                 "returnPlace" : spotID,
                                 "umbStorage" : 5
                                 }
            R2S_ReturnConfirm = json.dumps(OrderedDict(R2S_ReturnConfirm))
            size = len(R2S_ReturnConfirm.encode("utf8"))
            size = str(size)
            size = size.rjust(8,'0')

            clientSocket.send(size)
            time.sleep(0.5)

            clientSocket.send(R2S_ReturnConfirm.encode("utf8"))
            print ("[Rental Spot -> Main Server] : Return Comfirm and Update Status of Rental Spot")
            time.sleep(0.5)

            ######################## 연결 종료 선언 ###########################
            
            command = 0xF0
                
            FINsize = clientSocket.recv(8).decode("utf8")
            FINsize = int(FINsize)
                
            FIN = clientSocket.recv(FINsize).decode("utf8")
            FIN = json.loads(FIN)
                
            FIN = FIN["command"]
            if(FIN == command):
                print("[Main Server -> Rental Spot]: Receive FIN")
                print("[System]: quit connection")
                clientSocket.close()

        else:
            print ("[System] : Server NOT send ACK")
        UserUmb = 2