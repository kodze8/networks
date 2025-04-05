import socket
import threading
import statics
import os

RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
RESET = "\033[0m"



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
                response = message.decode('utf-8')
                if response.startswith("HELLO "):
                    username = response.split(" ", 1)[1]
                    print(f"Successfully logged in as {username}!")

                elif response == "IN-USE":
                    print(f"Cannot log in as {username}. That username is already in use.")

                elif response == "BUSY":
                    print("Cannot log in. The server is full!")

                elif response == "BAD-RQST-BODY":
                    print(f"Cannot log in as {username}. That username contains disallowed characters.")
                # Others need to be implemented.
                else:
                    print(f"{YELLOW}{message.decode('utf-8')}")

    def sendMsg(self):
        while self.running:
            if self.running:
                message = input()
            else:
                break
            self.client_socket.send(message.encode('utf-8'))

    def close(self):
        if not self.running:
            return
        self.running = False
        self.client_socket.close()
        os._exit(1)


c = client()
