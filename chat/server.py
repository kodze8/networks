import socket
import threading
import statics


class server:

    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((statics.SERVER_IP, statics.PORT))
        self.server.listen(5)
        print("Server is Listening...")
        self.clients = []
        self.clientNames = set()
        self.acceptClients()

    def acceptClients(self):
        while True:
            client_socket, client_IP = self.server.accept()
            threading.Thread(target=self.handleClient, args=(client_socket,)).start()

    def loginClient(self, client_socket):
        client_socket.send("Welcome to Chat Client. Enter your login:".encode('utf-8'))
        username = client_socket.recv(1024).decode('utf-8')
        validated = self.validate(username)
        if validated:
            self.clientNames.add(username)
            client_socket.send(f"HELLO {username}\n".encode('utf-8'))
        return validated

    def handleClient(self, client_socket):
        successLogIn = self.loginClient(client_socket)
        if not successLogIn:
            client_socket.close()
            return
        self.clients.append(client_socket)
        self.handleTexting(client_socket)

    def validate(self, firstMsg):
        if self.clientNames.__contains__(firstMsg):
            return False
        return True

    def broadcast(self, msg, sender):
        for client in self.clients:
            if client is not sender:
                client.send(msg)

    def handleTexting(self, client_socket):
        while True:
            msg = client_socket.recv(1024)
            if not msg:
                break
            self.broadcast(msg, client_socket)


if __name__ == '__main__':
    server = server()
