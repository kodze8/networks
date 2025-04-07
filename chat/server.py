import socket
import threading
import statics


class server:

    def __init__(self):
        self.maxUser = 5
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((statics.SERVER_IP, statics.PORT))
        self.server.listen(5)
        print("Server is Listening...")
        self.clients = {}
        self.clientNames = set()
        self.acceptClients()

    def acceptClients(self):
        while True:
            client_socket, client_IP = self.server.accept()
            threading.Thread(target=self.handleClient, args=(client_socket,)).start()

    def loginClient(self, client_socket):
        client_socket.send(f"Welcome to Chat Client. Enter your login:".encode('utf-8'))

        trying = True
        while trying:
            username = client_socket.recv(1024).decode('utf-8')
            if username == "!quit":
                client_socket.close()
                trying = False
            elif any(char in "!@#$%^&*" for char in username):  # EXTRA PROTOCOL
                client_socket.send(f"INVALID-CHARACTER {username}\n".encode('utf-8'))  # PROTOCOL Modified
            elif self.clientNames.__contains__(username):
                print("here")
                client_socket.send(f"IN-USE {username}\n".encode('utf-8'))  # PROTOCOL Modified
            elif len(self.clientNames) > self.maxUser:
                print("here2")
                client_socket.send(f"BUSY\n".encode('utf-8'))
                trying = False
            else:
                self.clientNames.add(username)
                self.clients[username] = client_socket
                client_socket.send(f"HELLO {username}\n".encode('utf-8'))
                return True, username
        return False, ""

    def handleClient(self, client_socket):
        successLogIn = self.loginClient(client_socket)
        if not successLogIn[0]:
            client_socket.close()
            return
        self.handleTexting(client_socket, successLogIn[1])

    def handleTexting(self, client_socket, username):
        while True:
            msg = client_socket.recv(1024).decode('utf-8').strip()
            if msg == "LIST":
                names = ", ".join(self.clientNames)
                client_socket.send(f"LIST-OK {names}\n".encode('utf-8'))
            elif msg.startswith("SEND"):
                address = msg.split(" ")[1]
                letter = " ".join(msg.split(" ")[2:])
                print(letter)
                if address == username:
                    client_socket.send("You can not text yourself!".encode('utf-8'))
                elif letter == "":
                    client_socket.send("You can not send blank message!".encode('utf-8'))
                elif self.clientNames.__contains__(address):
                    self.clients[address].send(f"DELIVERY {username} {letter}\n".encode('utf-8'))
                    client_socket.send("SEND-OK\n".encode('utf-8'))
                else:
                    client_socket.send("BAD-DEST-USER\n".encode('utf-8'))
            elif msg.startswith("!quit"):
                self.clientNames.remove(username)
                self.clients.pop(username)
                client_socket.close()
            else:
                client_socket.send("BAD-RQST-HDR\n".encode('utf-8'))


if __name__ == '__main__':
    server = server()
