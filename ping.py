import socket

address=("192.168.0.139",10000)
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.connect(address)
server.send(b"ping")
print(server.recv(30))