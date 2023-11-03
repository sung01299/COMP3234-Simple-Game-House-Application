import socket
import sys

class GameClient:
    def __init__(self, server_addr, server_port):
        self.server_addr = server_addr
        self.server_port = int(server_port)
        self.client_socket = None

    def connect(self):
        try:
            self.client_socket = socket.socket()
            self.client_socket.connect((self.server_addr, self.server_port))
        except socket.error as emsg:
            print("Socket error:", emsg)
            sys.exit(1)

    def authenticate(self):
        auth = False
        while not auth:
            try:
                username = input("Please input your user name:\n")
                password = input("Please input your password:\n")
            except Exception as error:
                print("An exception occured:", error)

            auth_msg = f"/login {username} {password}"
            self.client_socket.send(auth_msg.encode())
            rcved_authmsg = self.client_socket.recv(1024).decode()
            print(rcved_authmsg)
            auth_msg_key = rcved_authmsg.split()[0]
            if auth_msg_key == "1001":
                auth = True

    def guess(self, client_msg):
        guess_input = input("")
        guess_msg = f"{guess_input} {client_msg.split()[1]}"
        print(guess_msg)
        self.client_socket.send(guess_msg.encode())
        rcved_result_msg = self.client_socket.recv(1024).decode()
        print(rcved_result_msg)


    def run(self):
        self.connect()
        self.authenticate()

        while True:
            client_msg = input("")
            client_msg_key = client_msg.split()[0]

            if client_msg_key == "/exit":
                self.client_socket.send(client_msg.encode())
                rcved_msg = self.client_socket.recv(1024).decode()
                print(rcved_msg)
                break

            elif client_msg_key == "/list":
                self.client_socket.send(client_msg.encode())
                rcved_msg = self.client_socket.recv(1024).decode()
                print(rcved_msg)

            elif client_msg_key == "/enter":
                self.client_socket.send(client_msg.encode())
                rcved_msg = self.client_socket.recv(1024).decode()
                print(rcved_msg)

                rcved_msg_key = rcved_msg.split()[0]
                if rcved_msg_key == "3011":
                    rcved_msg = self.client_socket.recv(1024).decode()
                    print(rcved_msg)
                    if rcved_msg.split()[0] == "3012":
                        self.guess(client_msg=client_msg)
                elif rcved_msg_key == "3012":
                    self.guess(client_msg=client_msg)
                else:
                    continue

            else:
                self.client_socket.send(client_msg.encode())
                rcved_msg = self.client_socket.recv(1024).decode()
                print(rcved_msg)

            # print(rcved_msg)
            print("SENT:", client_msg)

        self.client_socket.close()

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python3 GameClient.py <Server_addr> <Server_port>")
        sys.exit(1)

    server_addr = sys.argv[1]
    server_port = sys.argv[2]

    client = GameClient(server_addr, server_port)
    client.run()