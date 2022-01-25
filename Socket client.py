#simple echo server saveur thomas

import socket

data = [1,2,3,4,5]
recv = []
s = socket.socket()
ip:str = "localhost"
port:int = 555
s.connect((ip,port))

#on envoie la grosseur des données qu'on va envoyer
s.send(int.to_bytes(len(data),4,"big"))
print("sending: {}".format(data))

for i in data:
    s.send(int.to_bytes(i,1,"big"))

for i in range(len(data)):
    recv+= [int.from_bytes(s.recv(1),"big")]

print("recived: {}".format(recv))
