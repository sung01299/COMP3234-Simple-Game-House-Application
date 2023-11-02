import os
import socket
import sys
import time
from _thread import *
import threading

print_lock = threading.Lock()
connected_sockets = []
num_of_game_rooms = 10
game_rooms = [[] for _ in range(num_of_game_rooms)]
inputs_by_rooms = [{} for _ in range(num_of_game_rooms)]


def threaded(connectionSocket):
    userdict = {}

    with open("userinfo.txt") as txt:
        for line in txt:
            key, val = line.split(":")
            userdict[key] = val.strip()

    while True:
        rcved_msg = connectionSocket.recv(1024).decode().split()
        print("RCVED:", rcved_msg)
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
            str_list = [str(len(num)) for num in game_rooms]
            msg = f"3001 {num_of_game_rooms} {' '.join(str_list)}"
            connectionSocket.send(msg.encode())

        # enter
        elif rcved_msg[0] == "/enter":
            if len(game_rooms[int(rcved_msg[1]) - 1]) == 0:
                game_rooms[int(rcved_msg[1]) - 1].append(connectionSocket)
                msg = "3011 Wait"
                connectionSocket.send(msg.encode())
            elif len(game_rooms[int(rcved_msg[1]) - 1]) == 1:
                game_rooms[int(rcved_msg[1]) - 1].append(connectionSocket)
                msg = "3012 Game started. Please guess true or false"
                for s in game_rooms[int(rcved_msg[1]) - 1]:
                    s.send(msg.encode())
            else:
                msg = "3013 The room is full"
                connectionSocket.send(msg.encode())

        # guess
        elif rcved_msg[0] == "/guess":
            server_choice = "true"
            if len(inputs_by_rooms[int(rcved_msg[2]) - 1]) < 2: 
                inputs_by_rooms[int(rcved_msg[2])-1][connectionSocket] = rcved_msg[1]
            if len(inputs_by_rooms[int(rcved_msg[2]) - 1]) == 2:
                # Game Tied
                if len(set(inputs_by_rooms[int(rcved_msg[2]) - 1].values())) == 1:
                    msg = "3023 The result is tie"
                    for s in inputs_by_rooms[int(rcved_msg[2]) - 1].keys():
                        s.send(msg.encode())
                # Game finished
                else:
                    win_msg = "3021 You are the winner"
                    loss_msg = "3022 You lost this game"
                    for s, val in inputs_by_rooms[int(rcved_msg[2])-1].items():
                        if val == server_choice:
                            s.send(win_msg.encode())
                        else:
                            s.send(loss_msg.encode())
                game_rooms[int(rcved_msg[2]) - 1] = []
                inputs_by_rooms[int(rcved_msg[2]) - 1] = {}

            print(inputs_by_rooms)

        # exit
        elif rcved_msg[0] == "/exit":
            msg = "4001 Bye bye"
            connectionSocket.send(msg.encode())
            break

        else:
            msg = "4002 Unrecognized message"
            connectionSocket.send(msg.encode())

        print("Connected Sockets #:", len(connected_sockets))


def main(argv):
    # Store user info
    # userdict = {}
    # with open("userinfo.txt") as txt:
    #     for line in txt:
    #         key, val = line.split(":")
    #         userdict[key] = val.strip()

    serverPort = int(argv[1])
    try:
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serverSocket.bind(("", serverPort))
    except socket.error as emsg:
        print("Socket error:", emsg)

    serverSocket.listen(5)

    print("Hello world")

    while True:
        try:
            connectionSocket, addr = serverSocket.accept()
        except socket.error as emsg:
            print("socket error:", emsg)
        start_new_thread(threaded, (connectionSocket,))
        print("addr:", addr)
    serverSocket.close()
    return


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python3 GameServer.py <Server_port>")
        sys.exit(1)
    main(sys.argv)
