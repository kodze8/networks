from argparse import Namespace, ArgumentParser

import socket
import threading


class client:
    def __init__(self, address, port):
        self.running = True
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((address, port))
        self.nameAccepted = False
        self.name = ""
        print("Welcome to Chat Client. Enter your login: ")

        self.receiveThread = threading.Thread(target=self.receiveMsg)
        self.sendThread = threading.Thread(target=self.sendMsg)
        self.receiveThread.start()
        self.sendThread.start()

    def receiveMsg(self):
        buffer = ""
        while self.running:
            try:
                data = self.client_socket.recv(1024)
                if not data:
                    self.close()
                    break

                buffer += data.decode('utf-8')

                # process complete messages (ending with newline)
                # in response to error about delay
                while '\n' in buffer:
                    message, buffer = buffer.split('\n', 1)
                    message = message.strip()

                    if not message:
                        continue

                    if message.startswith("HELLO "):
                        username = message.split(" ", 1)[1]
                        self.nameAccepted = True
                        print(f"Successfully logged in as {username}!")

                    elif message.startswith("IN-USE"):
                        print(f"Cannot log in as {self.name}. That username is already in use.")
                        print(f"Enter different username:")

                    elif message.startswith("INVALID-CHARACTER"):
                        print(f"Cannot log in as {self.name}. That username contains disallowed characters.")

                    elif message.startswith("BUSY"):
                        print(f"Cannot log in. The server is full!")

                    elif message.startswith("LIST-OK"):
                        names = message.split(" ", 1)[1].split(",")
                        name_builder = "\n".join(names)
                        print(f"There are {len(names)} online users:\n{name_builder}")

                    elif message.startswith("SEND-OK"):
                        print(f"The message was sent successfully")

                    elif message.startswith("BAD-DEST-USER"):
                        print(f"The destination user does not exist")

                    # elif message.startswith("DELIVERY"):
                    #     lst = message.split(" ")
                    #     sender = lst[1]
                    #     msg = " ".join(lst[2:])
                    #     print(f"From {sender}: {msg}")

                    elif message.startswith("DELIVERY"):
                        parts = message.split(' ', 2)
                        if len(parts) == 3:
                            sender, msg = parts[1], parts[2]
                            print(f"From {sender}: {msg}")

                    elif message.startswith("BAD-RQST-HDR"):
                        print(f"Error: Unknown issue in previous message header.")

                    elif message.startswith("BAD-RQST-BODY"):
                        print(f"Error: Unknown issue in previous message body.")

                    else:
                        print(f"Unknown message: {message}")

            except Exception as e:
                print(f"Error receiving message: {e}")
                self.close()
                break

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

            elif message == "!quit":
                self.close()

            elif not self.nameAccepted:
                forbidden_chars = set('!@#$%^&* ')

                if any(char in forbidden_chars for char in message):
                    print(f"Cannot log in as {message}. That username contains disallowed characters.")
                else:
                    self.name = message
                    self.client_socket.send(f"HELLO-FROM {message}\n".encode('utf-8'))

    def close(self):
        if not self.running:
            return
        self.running = False
        # try catch added so threads are dead
        try:
            self.client_socket.shutdown(socket.SHUT_RDWR)
        except (OSError, socket.error):
            print("Error Occurred")

        self.client_socket.close()


def parse_arguments() -> Namespace:
    """
    Parse command line arguments for the chat client.
    The two valid options are:
        --address: The host to connect to. Default is "0.0.0.0"
        --port: The port to connect to. Default is 5378
    :return: The parsed arguments in a Namespace object.
    """

    parser: ArgumentParser = ArgumentParser(
        prog="python -m a1_chat_client",
        description="A1 Chat Client assignment for the VU Computer Networks course.",
        epilog="Authors: Your group name"
    )
    parser.add_argument("-a", "--address",
                        type=str, help="Set server address", default="0.0.0.0")
    parser.add_argument("-p", "--port",
                        type=int, help="Set server port", default=5378)
    return parser.parse_args()


# Execute using `python -m a1_chat_client`
def main() -> None:
    args: Namespace = parse_arguments()
    port: int = args.port
    host: str = args.address

    # TODO: Your implementation here
    _ = client(host, port)


if __name__ == "__main__":
    main()
