## SERVER

from socket import*
from threading import*
import _thread

CL_list = [] # Client List

class Client(): # Client Class
    def __init__(self,conn,addr,userid):
        self.conn = conn    # connection with client
        self.addr = addr    # client's address
        self.id = userid    # client's id

def msg_client(client):
    global CL_list
    try:
        while True:
            msg = client.conn.recv(1024).decode("utf8")
            if msg[:2] == '/q':
                client.conn.close()
                CL_list.remove(client)
                return 0
            else:
                client.conn.send(('UPPER CASE OF LETTER : ').encode("utf8"))
                msg = msg.upper()
                client.conn.send(msg.encode("utf8"))
    except Exception as e:
        print(e)
        client.conn.close()
        print("Error....Quit the program...\n")

server_ip = '115.145.246.68' # Server's IP Address. You Have to check server's IP address
server_port = 50007
serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.bind((server_ip,server_port))
serverSocket.listen(9)
print(' SERVER STARTED  ')

while True:
    connectionSocket, addr = serverSocket.accept()  # 클라이언트의 요청 수락
    userid = connectionSocket.recv(1024).decode("utf8")
    client = Client(connectionSocket, addr, userid)
    CL_list.append(client)
    _thread.start_new_thread(msg_client,(client,)) # 스레드 설정, 시작
connectionSocket.close()

