import os
import socket
import sys

def main(argv):
    # Store user info
    userdict = {}
    with open("userinfo.txt") as txt:
        for line in txt:
            key, val = line.split(":")
            userdict[key] = val.strip()


    serverPort = int(argv[1])
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.bind(("", serverPort))

    serverSocket.listen(5)

    print("Hello world")

    connected_sockets = []
    while len(connected_sockets) < 3:
        try:
            connectionSocket, addr = serverSocket.accept()
        except socket.error as emsg:
            print("socket error:", emsg)

        print("addr:", addr)

        # receive authentication info from client
        userinfo = eval(connectionSocket.recv(4096).decode('utf-8'))
        if userinfo[0] not in userdict or userdict[userinfo[0]] != userinfo[1]:
            msg = "1002 Authentication failed"
            connectionSocket.send(msg.encode())
            connectionSocket.close()
        else:
            msg = "1001 Authentication successful"
            connectionSocket.send(msg.encode())
            connected_sockets.append(connectionSocket)
        
        print("Connected Sockets #: ", len(connected_sockets))
        

    serverSocket.close()
    return

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python3 GameServer.py <Server_port>")
        sys.exit(1)
    main(sys.argv)
