import os
import socket
import sys

def main(argv):
    try:
        client_socket = socket.socket()
        client_socket.connect((argv[1], int(argv[2])))
    except socket.error as emsg:
        print("Socket error:", emsg)
        sys.exit(1)
    print("Connection established. My socket address is", client_socket.getsockname())

    # authentication
    auth = False
    while auth == False:
        try:
            username = input("Please input your user name:\n")
            password = input("Please input your password:\n")
        except:
            print("Username/PW ERROR!!")

        auth_msg = f"/login {username} {password}"
        client_socket.send(auth_msg.encode())
        rcved_authmsg = client_socket.recv(1024).decode()
        print(rcved_authmsg)
        auth_msg_key = rcved_authmsg.split()[0]
        if auth_msg_key == "1001":
            auth = True

    while True:
        client_msg = input("")
        client_msg_key = client_msg.split()[0]
        # exit
        if client_msg_key == "/exit":
            client_socket.send(client_msg.encode())
            rcved_msg = client_socket.recv(1024).decode()
            print(rcved_msg)
            break

        # list
        elif client_msg_key == "/list":
            client_socket.send(client_msg.encode())
            rcved_msg = client_socket.recv(1024).decode()
            print(rcved_msg)

        # enter
        elif client_msg_key == "/enter":
            client_socket.send(client_msg.encode())
            rcved_msg = client_socket.recv(1024).decode()

            print(rcved_msg)

            rcved_msg_key = rcved_msg.split()[0]
            # Wait
            if rcved_msg_key == "3011":
                rcved_msg = client_socket.recv(1024).decode()
                print(rcved_msg)
                if rcved_msg.split()[0] == "3012":
                    guess_input = input("")
                    guess_msg = f"{guess_input} {client_msg.split()[1]}"
                    print(guess_msg)
                    client_socket.send(guess_msg.encode())
                    rcved_result_msg = client_socket.recv(1024).decode()
                    print(rcved_result_msg)
            # Game started
            elif rcved_msg_key == "3012":
                guess_input = input("")
                guess_msg = f"{guess_input} {client_msg.split()[1]}"
                print(guess_msg)
                client_socket.send(guess_msg.encode())
                rcved_result_msg = client_socket.recv(1024).decode()
                print(rcved_result_msg)
            # Room Full
            else:
                continue

        # Unrecognized message
        else:
            client_socket.send(client_msg.encode())
            rcved_msg = client_socket.recv(1024).decode()
            print(rcved_msg)

        print("SENT:", client_msg)

    return


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python3 GameClient.py <Server_addr> <Server_port>")
        sys.exit(1)
    main(sys.argv)
