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
    num_of_game_rooms = 10
    game_rooms = [0 for _ in range(num_of_game_rooms)]
    while len(connected_sockets) < 3:
        try:
            connectionSocket, addr = serverSocket.accept()
        except socket.error as emsg:
            print("socket error:", emsg)

        print("addr:", addr)

        rcved_msg = connectionSocket.recv(1024).decode().split()
        # authentication
        if rcved_msg[0] == "/login":
            username = rcved_msg[1]
            password = rcved_msg[2]
            if username not in userdict or userdict[username] != password:
                msg = "1002 Authentication failed"
                connectionSocket.send(msg.encode())
                connectionSocket.close()
            else:
                msg = "1001 Authentication successful"
                connectionSocket.send(msg.encode())
                connected_sockets.append(connectionSocket)
        
        # In the Game Hall
        elif rcved_msg[0] == "/list":
            str_list = [str(num) for num in game_rooms]
            msg = f"3001 {num_of_game_rooms} {' '.join(str_list)}"
            connectionSocket.send(msg.encode())

        
        print("Connected Sockets #:", len(connected_sockets))
        

    serverSocket.close()
    return

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python3 GameServer.py <Server_port>")
        sys.exit(1)
    main(sys.argv)
