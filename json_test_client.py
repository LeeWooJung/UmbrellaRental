import sys
import json
from collections import OrderedDict # 파이썬의 딕셔너리 자료형은 키값의 ABC순으로 자동으로 정렬, 따라서 자동정렬을 원하지 않을 시 사용하는 함수.
from socket import*
from threading import*
import _thread


# for test python Dictionary

hashcode = OrderedDict()
hashcode = {
    'id' : 152353,
    'name' : ' customer ',
    'history': [
        {'date': '2017-11-19', 'item': 'iPhone'},
        {'date': '2017-11-18', 'item': 'Galaxy'},
        ]
    }

## QR code to Hash Code decoding


# If hashcode decoding is correct
hashcode_decoding = input('input hashcode_decoding value:')
hashcode_decoding = int(hashcode_decoding)

# JSON encoding USING json.dump()
json_hashcode = json.dumps(hashcode, indent = "\t") # ident = "\t" 의 역할 : tab문자로 들여쓰기를 함으로써 가독성 향상

# jsonString의 바이트 크기 계산
byteSize = sys.getsizeof(json_hashcode)
print('byteSize of jsonString is(Will send byteSize to the Server) : ', byteSize)
print('')

# JSON decoding USING json.loads()
# dict = json.loads(json_hashcode)

# Check Dictionary data
#print(dict['name'])
#for i in dict['history']:
#    print(i['date'],i['item'])

# Set Server IP & Server Port

server_ip = "localhost"
server_port = 50007

# change 'byteSize' from 'int' to 'string'
byteSize = str(byteSize)


while (hashcode_decoding == 1):
    # Create Socket

    clientSocket = socket(AF_INET,SOCK_STREAM) # TCP 통신
    clientSocket.connect((server_ip,server_port)) # 서버 연결

    # Let Server Know how large size of data
    clientSocket.send(byteSize.encode("utf8"))
    
    # To receive server_msg 
    Server_MSG = clientSocket.recv(1024).decode("utf8")

    # change 'Server_MSG' from 'string' to 'int'
    Server_MSG = int(Server_MSG)
    
    if Server_MSG == 1: # if The HASH CODE mathes with server HASH CODE
        print('MATCHES')g
        
    else: # if The HASH CODE doesn't matches with server HASH CODE
        print('NOT MATCHES')
        print(Server_MSG)

    # If hashcode decoding is correct
    hashcode_decoding = input('input hashcode_decoding value:')
    hashcode_decoding = int(hashcode_decoding)
    
        
        
    























