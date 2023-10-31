import os
import socket
import sys

def main(argv):
    try:
        sock = socket.socket()
        sock.connect((argv[1], int(argv[2])))
    except socket.error as emsg:
        print("Socket error:", emsg)
        sys.exit(1)
    print("Connection established. My socket address is", sock.getsockname())

    # authentication
    try:
        username = input("Please input your user name:\n")
        password = input("Please input your password:\n")
    except:
        print("Username/PW ERROR!!")

    userinfo = [username, password]
    sock.send(str(userinfo).encode())
    authmsg = sock.recv(1024).decode('utf-8')
    print(authmsg)


    
    return

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python3 GameClient.py <Server_addr> <Server_port>")
        sys.exit(1)
    main(sys.argv)