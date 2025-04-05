import re
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

    def validate(self, firstMsg):
        pattern = r"^HELLO-FROM [A-Za-z]+\s*$"
        format_validated = bool(re.match(pattern, firstMsg))

        if not format_validated:
            return False, "Invalid Format"

        name = firstMsg.split(" ")[1]

        if self.clientNames.__contains__(name):
            return False, "Name is taken"
        else:
            self.clientNames.add(name)
            return True, f"Hello {name}"

    def broadcast(self, msg, sender):
        for client in self.clients:
            if client is not sender:
                client.send(msg)

    def handleClient(self, client_socket):
        firstMsg = client_socket.recv(1024).decode('utf-8')
        validated = self.validate(firstMsg)

        if not validated[0]:
            client_socket.close()
            return
        client_socket.send(validated[1].encode('utf-8'))
        self.clients.append(client_socket)
        self.handleTexting(client_socket)

    def handleTexting(self, client_socket):
        while True:
            msg = client_socket.recv(1024)
            if not msg:
                break
            self.broadcast(msg, client_socket)


if __name__ == '__main__':
    server = server()
