import socket
import sys

class GameClient:
    # Initialize variables
    def __init__(self, server_addr, server_port):
        # Stores server address
        self.server_addr = server_addr
        # Stores server port number
        self.server_port = int(server_port)
        # Client socket
        self.client_socket = None

    # Connects to the server
    def connect(self):
        try:
            self.client_socket = socket.socket()
            self.client_socket.connect((self.server_addr, self.server_port))
        except socket.error as emsg:
            print("Socket error:", emsg)
            sys.exit(1)

    # 1. User Authentication
    def authenticate(self):
        auth = False
        # Repeats authentication process until user successfully sign in
        while not auth:
            try:
                # Get username / password
                username = input("Please input your user name:\n")
                password = input("Please input your password:\n")
            except Exception as error:
                print("An exception occured:", error)
            # Communicates with server
            auth_msg = f"/login {username} {password}"
            self.client_socket.send(auth_msg.encode())
            rcved_auth_msg = self.client_socket.recv(1024).decode()
            print(rcved_auth_msg)
            auth_msg_key = rcved_auth_msg.split()[0]
            if auth_msg_key == "1001":
                auth = True

    # Dealing the guess by users
    def guess(self, client_msg):
        guess_key = ""
        guess_input_length = 0
        client_guess = ""
        choices = ["true", "false"]
        # Handles exception when user inputs its guess incorrectly
        while guess_key != "/guess" or guess_input_length != 2 or client_guess not in choices:
            guess_input = input("")
            # Update guess_key, client_guess, guess_input_length
            guess_key = guess_input.split()[0]
            guess_input_length = len(guess_input.split())
            if guess_input_length >= 2:
                client_guess = guess_input.split()[1]
            if guess_key != "/guess" or guess_input_length != 2 or client_guess not in choices:
                print("4002 Unrecognized message")
        # Communicates with server
        guess_msg = f"{guess_input} {client_msg.split()[1]}"
        self.client_socket.send(guess_msg.encode())
        rcved_result_msg = self.client_socket.recv(1024).decode()
        print(rcved_result_msg)

    def main(self):
        # Client starts to connect to the server
        try:
            self.connect()
            self.authenticate()
            # After authentication success
            while True:
                try:
                    # Get input from client
                    client_msg = input("")
                    # Extract the keyword (/list, /enter, /guess, ...) from the client input
                    client_msg_key = client_msg.split()[0]
                except Exception as error:
                    print(error)

                # 2. In the Game Hall
                # 1) list
                if client_msg_key == "/list":
                    self.client_socket.send(client_msg.encode())
                    rcved_msg = self.client_socket.recv(1024).decode()
                    print(rcved_msg)
                # 2) enter
                elif client_msg_key == "/enter":
                    self.client_socket.send(client_msg.encode())
                    rcved_msg = self.client_socket.recv(1024).decode()
                    print(rcved_msg)

                    rcved_msg_key = rcved_msg.split()[0]
                    # First player to enter a room
                    if rcved_msg_key == "3011":
                        rcved_msg = self.client_socket.recv(1024).decode()
                        print(rcved_msg)
                        # When another player enters room, start a game
                        if rcved_msg.split()[0] == "3012":
                            self.guess(client_msg=client_msg)
                    # Two players entered a room, start a game
                    elif rcved_msg_key == "3012":
                        self.guess(client_msg=client_msg)
                    # Room is full
                    else:
                        continue
                
                # 4. Exit from the System
                elif client_msg_key == "/exit":
                    self.client_socket.send(client_msg.encode())
                    rcved_msg = self.client_socket.recv(1024).decode()
                    print(rcved_msg)
                    self.client_socket.close()
                    break

                else:
                    self.client_socket.send(client_msg.encode())
                    rcved_msg = self.client_socket.recv(1024).decode()
                    print(rcved_msg)

        except socket.error as emsg:
            print("Socket error:", emsg)
        finally:
            self.client_socket.close()

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python3 GameClient.py <Server_addr> <Server_port>")
        sys.exit(1)

    server_addr = sys.argv[1]
    server_port = sys.argv[2]

    client = GameClient(server_addr, server_port)
    client.main()