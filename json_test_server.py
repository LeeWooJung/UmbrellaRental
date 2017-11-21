from socket import*


server_ip = "localhost"
server_port = 50007

serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.bind((server_ip,server_port))
serverSocket.listen(2)
print('SERVER STARTED')

value = 1
value = str(value)
while True:
    connectionSocket, addr = serverSocket.accept()
    byteSize = connectionSocket.recv(1024).decode("utf8")
    print('Received byteSize = ', byteSize)
    connectionSocket.send(value.encode("utf8"))
connectionSocket.close()
