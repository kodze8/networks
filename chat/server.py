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
        client_socket.send("Welcome to Chat Client. Enter your login:".encode('utf-8'))
        username = client_socket.recv(1024).decode('utf-8')
        if any(char in "!@#$%^&*" for char in username):
            client_socket.send(f"IN-USE\n")
        elif self.clientNames.__contains__(username):
            client_socket.send(f"IN-USE\n")
        elif len(self.clientNames) > self.maxUser:
            client_socket.send(f"BUSY\n")
        else:
            self.clientNames.add(username)
            self.clients[username] = client_socket
            client_socket.send(f"HELLO {username}\n".encode('utf-8'))
            return True, username
        return False, username

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
                names = ", ".join(self.clientNames);
                client_socket.send(f"LIST-OK {names}\n".encode('utf-8'))
            elif msg.startswith("SEND"):
                address = msg.split(" ")[1]
                letter = " ".join(msg.split(" ")[1:])
                if self.clientNames.__contains__(address):
                    self.clients[address].send(f"DELIVERY {username} {letter}\n".encode('utf-8'))
                    client_socket.send("SEND-OK\n".encode('utf-8'))
                else:
                    client_socket.send("BAD-DEST-USER\n".encode('utf-8'))
            elif msg == "!quit":
                client_socket.close()

            else:
                client_socket.send("BAD-RQST-HDR\n".encode('utf-8'))


if __name__ == '__main__':
    server = server()
