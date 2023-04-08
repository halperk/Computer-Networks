import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((socket.gethostname(), 1234))

# msg = sock.recv(1024)
# print(msg.decode("utf-8"))

full_msg = ""
while True:
    msg = sock.recv(8)
    if len(msg) <= 0:
        break
    else:
        full_msg += msg.decode("utf-8")

print(full_msg)