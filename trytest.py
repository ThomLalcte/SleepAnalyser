import threading
import socket

def cringe(client: socket):
    client.send(b"amoung ous")
    client.close()

s = socket.socket()
s.bind(("localhost",100))
s.listen(0)
client, addr = s.accept()
t2 = threading.Thread(cringe(client.dup()))
del client
t2.start()
for i in "CRINGEEEEEEEEEEEEEEEE":
    print(i)