import socket
import threading
import statics


class server:

    def __init__(self, address=statics.SERVER_IP, port=statics.PORT):
        self.maxUser = 5
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((address, port))
        self.server.listen(5)
        print("Server is Listening...")
        self.clients = {}
        self.clientNames = set()
        self.running = True
        threading.Thread(target=self.serverListening, daemon=True).start()
        self.acceptClients()

    def serverListening(self):
        while self.running:
            msg = input()
            if msg == "exit":
                for username in self.clientNames:
                    self.clients[username].send("System shut down!".encode('utf-8'))
                    self.clients[username].close()
                self.server.close()
                self.running = False

    def acceptClients(self):
        while self.running:
            try:
                client_socket, client_IP = self.server.accept()
                threading.Thread(target=self.handleClient, args=(client_socket,), daemon=True).start()
            except OSError:
                # This happens when server socket is shutdown
                break

    def handleClient(self, client_socket):
        successLogIn = self.loginClient(client_socket)
        if not successLogIn[0]:
            client_socket.close()
            return
        self.handleTexting(client_socket, successLogIn[1])

    def loginClient(self, client_socket):
        client_socket.send(f"Welcome to Chat Client. Enter your login:".encode('utf-8'))
        trying = True
        while trying:
            try:
                username = client_socket.recv(1024).decode('utf-8').strip()
                if username == "!quit":
                    client_socket.close()
                    trying = False
                elif any(char in "!@#$%^&*" for char in username):  # EXTRA PROTOCOL
                    client_socket.send(f"INVALID-CHARACTER {username}\n".encode('utf-8'))  # PROTOCOL Modified
                elif self.clientNames.__contains__(username):
                    client_socket.send(f"IN-USE {username}\n".encode('utf-8'))  # PROTOCOL Modified
                elif len(self.clientNames) >= self.maxUser:
                    client_socket.send(f"BUSY\n".encode('utf-8'))
                    trying = False
                else:
                    self.clientNames.add(username)
                    self.clients[username] = client_socket
                    client_socket.send(f"HELLO {username}\n".encode('utf-8'))
                    return True, username
            except:
                trying = False
        return False, ""

    def handleTexting(self, client_socket, username):
        active = True
        while active and self.running:
            try:
                msg = client_socket.recv(1024).decode('utf-8').strip()
                if msg == "LIST":
                    names = ", ".join(self.clientNames)
                    client_socket.send(f"LIST-OK {names}\n".encode('utf-8'))
                elif msg.startswith("SEND"):
                    address = msg.split(" ")[1]
                    letter = " ".join(msg.split(" ")[2:])
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
                    active = False
                else:
                    client_socket.send("BAD-RQST-HDR\n".encode('utf-8'))
            except:
                self.running = False


if __name__ == '__main__':
    server = server()
