#simple echo server saveur thomas

import socket
import sys

data = [1,2,3,4,5]

s = socket.socket()
ip:str = "localhost"
port:int = 555   
s.bind((ip, port ))
s.listen(0)

while True:
    try:
        client, addr = s.accept()
        size = int.from_bytes(client.recv(4),"big")
        content = client.recv(size)
        client_name = client.getpeername()
        print("server recived: {}".format(int.from_bytes(content,"big")))
        client.send(content)
    except TimeoutError:
        print("Client timed-out")
    except ConnectionResetError:
        print("Client badly closed socket")
        