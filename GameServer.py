import socket
import sys
import random
from _thread import *
import threading


class GameServer:
    # Initialize variables
    def __init__(self, num_of_rooms, file_path):
        # Handles thread lock
        self.thrd_lock = threading.Lock()
        # Path of a txt file containing username and password of clients
        self.file_path = file_path
        # Stores client states, 0: in the game hall, 1: waiting in a room, 2: playing a game
        self.connected_sockets = {}
        # Number of rooms
        self.num_of_rooms = num_of_rooms
        # Stores which clients are waiting / playing in each game rooms
        self.room_list = [[] for _ in range(num_of_rooms)]
        # Stores the guess made by clients in each game rooms
        self.guess_by_room = [{} for _ in range(num_of_rooms)]
        # Stores username, password inputted by clients
        self.user_info = {}

    # Reads username / password from UserInfo.txt and stores them into user_info dictionary
    def getUserInfo(self):
        with open(self.file_path) as txt:
            for line in txt:
                username, pw = line.split(":")
                self.user_info[username] = pw.strip()

    # Client thread
    def client_thrd(self, client_socket):
        try:
            while True:
                # Receive messages from client
                rcved_msg = client_socket.recv(1024).decode().split()
                if rcved_msg:
                    # 1. User Authentication
                    if rcved_msg[0] == "/login":
                        username = rcved_msg[1]
                        password = rcved_msg[2]
                        # Authentication failed
                        # Username does not exist or incorrect password
                        if username not in self.user_info or self.user_info[username] != password:
                            msg = "1002 Authentication failed"
                            client_socket.send(msg.encode())
                        # Authentication successful
                        else:
                            msg = "1001 Authentication successful"
                            client_socket.send(msg.encode())
                            # Client state: In the game hall
                            self.connected_sockets[client_socket] = 0

                    # 2. In the Game Hall
                    # 1) list
                    elif rcved_msg[0] == "/list":
                        self.thrd_lock.acquire()
                        # Convert a list to string format
                        str_list = [str(len(num)) for num in self.room_list]
                        # Message to be sent to client
                        msg = f"3001 {self.num_of_rooms} {' '.join(str_list)}"
                        client_socket.send(msg.encode())
                        self.thrd_lock.release()

                    # 2) enter
                    elif rcved_msg[0] == "/enter":
                        room_number = int(rcved_msg[1]) - 1
                        # Room does not exist
                        if room_number >= self.num_of_rooms:
                            msg = "4002 Unrecognized message"
                            client_socket.send(msg.encode())
                        else:
                            self.thrd_lock.acquire()
                            # First player to enter a room
                            if len(self.room_list[room_number]) == 0:
                                self.room_list[room_number].append(client_socket)
                                msg = "3011 Wait"
                                client_socket.send(msg.encode())
                                # Client state: Waiting in a room
                                self.connected_sockets[client_socket] = 1
                            # Two players entered a room
                            elif len(self.room_list[room_number]) == 1:
                                self.room_list[room_number].append(client_socket)
                                msg = "3012 Game started. Please guess true or false"
                                for client in self.room_list[room_number]:
                                    client.send(msg.encode())
                                    # Client state: Playing a game
                                    self.connected_sockets[client] = 2
                            # Room is full
                            else:
                                msg = "3013 The room is full"
                                client_socket.send(msg.encode())
                            self.thrd_lock.release()

                    # 3. Playing a Game
                    elif rcved_msg[0] == "/guess":
                        # Room number client is playing
                        room_number = int(rcved_msg[2]) - 1
                        # Server generates random choice between true and false
                        choices_list = ["true", "false"]
                        server_choice = random.choice(choices_list)
                        # One player sent its choice(guess), still waiting for another to send
                        self.thrd_lock.acquire()
                        if len(self.guess_by_room[room_number]) < 2: 
                            self.guess_by_room[room_number][client_socket] = rcved_msg[1]
                        self.thrd_lock.release()

                        self.thrd_lock.acquire()
                        # Both players sent their choice(guess)
                        if len(self.guess_by_room[room_number]) == 2:
                            # Game Tied
                            if len(set(self.guess_by_room[room_number].values())) == 1:
                                msg = "3023 The result is tie"
                                for client in self.guess_by_room[room_number].keys():
                                    client.send(msg.encode())
                            # Game Not Tied
                            else:
                                win_msg = "3021 You are the winner"
                                loss_msg = "3022 You lost this game"
                                for client, client_guess in self.guess_by_room[room_number].items():
                                    # Winner
                                    if client_guess == server_choice:
                                        client.send(win_msg.encode())
                                    # Loser
                                    else:
                                        client.send(loss_msg.encode())
                                    # Client state: In the game hall
                                    self.connected_sockets[client] = 0
                            # Reset room_list, guess_by_room
                            self.room_list[room_number] = []
                            self.guess_by_room[room_number] = {}
                        self.thrd_lock.release()

                    # 4. Exit from the System
                    elif rcved_msg[0] == "/exit":
                        msg = "4001 Bye bye\nClient ends"
                        client_socket.send(msg.encode())
                        self.connected_sockets.pop(client_socket, None)
                        break

                    # 5. Dealing with incorrect message format
                    else:
                        msg = "4002 Unrecognized message"
                        client_socket.send(msg.encode())

                else:
                    client_socket.close()
        except ConnectionResetError:
            print("Client connection was reset.")
            for index, room in enumerate(self.room_list):
                if client_socket in room:
                    room_num = index
                    break
            self.room_list[room_num].remove(client_socket)
        except ConnectionAbortedError:
            print("Client connection was aborted.")
        except socket.error as emsg:
            print("Socket error:", emsg)
        finally:
            # Handle exception when one player is disconnected while two players were playing
            if self.connected_sockets[client_socket] == 2:
                for index, room in enumerate(self.room_list):
                    if client_socket in room:
                        room_num = index
                        break
                self.room_list[room_num].remove(client_socket)
                msg = "3021 You are the winner"
                self.room_list[room_num][0].send(msg.encode())
                self.connected_sockets[self.room_list[room_num][0]] = 0
                self.room_list[room_num] = []
                self.guess_by_room[room_num] = {}
            
            # Reset the connected_sockets
            self.connected_sockets.pop(client_socket, None)

    def main(self, server_port):
        # Start the server
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.bind(("", server_port))
            server_socket.listen(5)
            # Creates a new socket and a new thread
            print("The server is ready to connect...")
            while True:
                try:
                    client_socket, addr = server_socket.accept()
                except socket.error as emsg:
                    print("socket error:", emsg)
                # Starts a new thread that handles client socket
                else:
                    start_new_thread(self.client_thrd, (client_socket,))

        except socket.error as emsg:
            print("Socket error:", emsg)
        finally:
            server_socket.close()

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python3 GameServer.py <Server_port> <UserInfo_path>")
        sys.exit(1)
    
    server_port = int(sys.argv[1])
    file_path = sys.argv[2]
    game_server = GameServer(num_of_rooms=10, file_path=file_path)
    game_server.getUserInfo()
    game_server.main(server_port)
