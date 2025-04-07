import os
import socket
import threading

import statics

RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
RESET = "\033[0m"
WHITE = "\033[97m"


class client:

    def __init__(self):
        self.running = True
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((statics.SERVER_IP, statics.PORT))

        threading.Thread(target=self.receiveMsg).start()
        threading.Thread(target=self.sendMsg).start()

    def receiveMsg(self):
        while self.running:
            message = self.client_socket.recv(1024)
            if not message:
                self.close()
            else:
                response = message.decode('utf-8').strip()

                if response.startswith("HELLO "):
                    username = response.split(" ", 1)[1]
                    print(f"{WHITE}Successfully logged in as {username}!")

                elif response.startswith("IN-USE"):
                    username = response.split(" ", 1)[1]
                    print(f"{RED}Cannot log in as {username}. That username is already in use.")
                    print(f"{BLUE}Enter different username:")

                elif response.startswith("INVALID-CHARACTER"):
                    username = response.split(" ", 1)[1]
                    print(f"{RED}Cannot log in as {username}. That username contains invalid characters.")
                    print(f"{BLUE}Enter different username:")

                elif response.startswith("BUSY"):
                    print(f"{RED}Cannot log in. The server is full!")

                elif response.startswith("LIST-OK"):
                    names = response.strip("LIST-OK ").split(", ")
                    name_builder = "\n".join(names)
                    print(f"{BLUE}There are {len(names)} online users:\n{name_builder}")

                elif response.startswith("SEND-OK"):
                    print(f"{WHITE}The message was sent successfully")

                elif response.startswith("BAD-DEST-USER"):
                    print(f"{RED}The destination user does not exist")

                elif response.startswith("DELIVERY"):
                    lst = response.split(" ")
                    sender = lst[1]
                    msg = " ".join(lst[2:])
                    print(f"{BLUE}From {sender}: {msg}")

                elif response.startswith("BAD-RQST-HDR"):
                    print(f"{RED}Error: Unknown issue in previous message header.")

                elif response.startswith("BAD-RQST-BODY"):
                    print(f"{RED}Error: Unknown issue in previous message body.")

                else:
                    print(f"{BLUE}{message.decode('utf-8')}")

    def sendMsg(self):
        while self.running:
            if self.running:
                message = input()
            else:
                break

            if message.startswith("@"):
                name = message.strip("@").split(" ")[0]
                msg = " ".join(message.split(" ")[1:])
                self.client_socket.send(f"SEND {name} {msg}\n".encode('utf-8'))
            elif message == "!who":
                self.client_socket.send("LIST\n".encode('utf-8'))
            else:
                self.client_socket.send(message.encode('utf-8'))

    def close(self):
        if not self.running:
            return
        self.running = False
        self.client_socket.close()
        os._exit(1)


if __name__ == '__main__':
    c = client()
