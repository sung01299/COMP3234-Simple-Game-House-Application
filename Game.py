import os
import socket
import sys
import time
import random
from _thread import *
import threading

class GameServer:
    def __init__(self, num_of_rooms, file_path):
        self.thrd_lock = threading.Lock()
        self.connected_sockets = []
        self.connected_users = []
        self.num_of_rooms = num_of_rooms
        self.file_path = file_path
        self.room_list = [[] for _ in range(num_of_rooms)]
        self.guess_by_room = [{} for _ in range(num_of_rooms)]
        self.user_info = {}

    def getUserInfo(self):
        with open(self.file_path) as txt:
            for line in txt:
                username, pw = line.split(":")
                self.user_info[username] = pw.strip()

    def threaded(self, client_socket):
        while True:
            rcved_msg = client_socket.recv(1024).decode().split()
            print("RCVED:", rcved_msg)
            # authentication
            if rcved_msg[0] == "/login":
                username = rcved_msg[1]
                password = rcved_msg[2]
                if username not in self.user_info or username in self.connected_users or self.user_info[username] != password:
                    msg = "1002 Authentication failed"
                    client_socket.send(msg.encode())
                else:
                    msg = "1001 Authentication successful"
                    client_socket.send(msg.encode())
                    self.connected_sockets.append(client_socket)
                    self.connected_users.append(username)

            # In the Game Hall
            elif rcved_msg[0] == "/list":
                self.thrd_lock.acquire()
                str_list = [str(len(num)) for num in self.room_list]
                msg = f"3001 {self.num_of_rooms} {' '.join(str_list)}"
                client_socket.send(msg.encode())
                self.thrd_lock.release()

            # enter
            elif rcved_msg[0] == "/enter":
                self.thrd_lock.acquire()
                if len(self.room_list[int(rcved_msg[1]) - 1]) == 0:
                    self.room_list[int(rcved_msg[1]) - 1].append(client_socket)
                    msg = "3011 Wait"
                    client_socket.send(msg.encode())
                elif len(self.room_list[int(rcved_msg[1]) - 1]) == 1:
                    self.room_list[int(rcved_msg[1]) - 1].append(client_socket)
                    msg = "3012 Game started. Please guess true or false"
                    for s in self.room_list[int(rcved_msg[1]) - 1]:
                        s.send(msg.encode())
                else:
                    msg = "3013 The room is full"
                    client_socket.send(msg.encode())
                self.thrd_lock.release()

            # guess
            elif rcved_msg[0] == "/guess":
                choices_list = ["true", "false"]
                server_choice = random.choice(choices_list)

                self.thrd_lock.acquire()
                if len(self.guess_by_room[int(rcved_msg[2]) - 1]) < 2: 
                    self.guess_by_room[int(rcved_msg[2])-1][client_socket] = rcved_msg[1]
                self.thrd_lock.release()
                self.thrd_lock.acquire()
                if len(self.guess_by_room[int(rcved_msg[2]) - 1]) == 2:
                    # Game Tied
                    if len(set(self.guess_by_room[int(rcved_msg[2]) - 1].values())) == 1:
                        msg = "3023 The result is tie"
                        for s in self.guess_by_room[int(rcved_msg[2]) - 1].keys():
                            s.send(msg.encode())
                    # Game finished
                    else:
                        win_msg = "3021 You are the winner"
                        loss_msg = "3022 You lost this game"
                        for s, val in self.guess_by_room[int(rcved_msg[2])-1].items():
                            if val == server_choice:
                                s.send(win_msg.encode())
                            else:
                                s.send(loss_msg.encode())
                    self.room_list[int(rcved_msg[2]) - 1] = []
                    self.guess_by_room[int(rcved_msg[2]) - 1] = {}
                self.thrd_lock.release()

                print(self.guess_by_room)

            # exit
            elif rcved_msg[0] == "/exit":
                msg = "4001 Bye bye"
                client_socket.send(msg.encode())
                break

            else:
                msg = "4002 Unrecognized message"
                client_socket.send(msg.encode())

            print("Connected Sockets #:", len(self.connected_sockets))


    def main(self, server_port):
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.bind(("", server_port))
        except socket.error as emsg:
            print("Socket error:", emsg)

        server_socket.listen(5)

        print("Hello world")

        while True:
            try:
                client_socket, addr = server_socket.accept()
            except socket.error as emsg:
                print("socket error:", emsg)
            start_new_thread(self.threaded, (client_socket,))
            print("addr:", addr)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python3 GameServer.py <Server_port> <UserInfo_path>")
        sys.exit(1)
    
    server_port = int(sys.argv[1])
    file_path = sys.argv[2]
    game_server = GameServer(num_of_rooms=10, file_path=file_path)
    game_server.getUserInfo()
    game_server.main(server_port)
