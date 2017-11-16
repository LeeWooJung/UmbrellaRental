## Client

from socket import*
from threading import*
import _thread

def server_msg(socket): # 메시지를 client에게 보여줌
    try:
        while True:
            msg = socket.recv(1024).decode("utf8")
            print(msg) # 서버를 통해 msg를 받아옴


    except Exception as e: # 예외처리
        sock.close() # 예외일 때 socket 닫음
        print("ERROR!! Quit Program....................")
        os._exit(0)


# input IP address, Port Number, UserID 

## In Linux change input to raw_input

server_ip = input("Enter IP address! : ")
server_port = int(input("Enter the Port Number! : "))
userid = input("Enter your ID! : ")

# Create Socket

clientSocket = socket(AF_INET,SOCK_STREAM)
clientSocket.connect((server_ip,server_port)) # ip와 port에 맞는 것에 connect!
clientSocket.send(userid.encode("utf8"))

print("Write")



while True: # 메시지 입력
    userMsg = input("Input lowercase Letter : ")
    clientSocket.send(userMsg.encode("utf8"))
    if userMsg == '/q':
        quit()
    _thread.start_new_thread(server_msg,(clientSocket,))
clientSocket.close()
