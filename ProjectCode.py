import socket
import threading
import select
import errno
import sys
import time
import os
from tqdm import tqdm

class App:
    # Class attributes
    IP = socket.gethostbyname(socket.gethostname())  # Get the IP address of the local machine
    PORT = 9876  # Default port number
    Transfer = 55000  # Transfer port number

    def __init__(self, setting):
        # Initialize instance attributes
        self.IP = socket.gethostbyname(socket.gethostname())  # Get the IP address of the local machine
        self.PORT = 9876  # Default port number
        self.Transfer = 4456  # Transfer port number
        self.setting = setting  # Host or join setting
        self.cancel = ["quit", "kill", "stop", "terminate"]  # List of commands to cancel operations
        self.query = ["ask"]  # List of commands for querying information
        self.send = ["send", "transfer"]  # List of commands for sending files
        self.files = {}  # Dictionary to store file information

    # Host mode for managing connections
    def host_mode(self):
        host = socket.gethostbyname(socket.gethostname())  # Get the IP address of the local machine
        port = 59000  # Port number for hosting

        # Initialize server socket
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((host, port))  # Bind server to the specified host and port
        server.listen()  # Start listening for incoming connections
        storage = {}  # Dictionary to store client connections
        users = []  # List of connected users
        clients = []  # List of client sockets

        # Function to broadcast messages to all connected clients
        def broadcast(message):
            for x in storage:
                storage[x].send(message)

        # Function to query file information
        def query():
            print("Query call")
            report = ""
            for x in self.files:
                report = report + "Name: " + x + "  Owner: " + self.files[x] + "\n"
            broadcast(report.encode('utf-8'))

        # Function to handle file requests from clients
        def fileRequest(name):
            if name in storage:
                print("File found.\n File list: " + self.files.keys() + "\n")
                storage[name].send("Are you willing to share your file?".encode('utf-8'))
                response = storage[name].recv(1024).decode('utf-8')
            else:
                broadcast("File not found\n".encode('utf-8'))

        # Function to register file ownership
        def register(name, sender):
            print("Register call")
            self.files.update({name: sender})

        # Function to deregister file ownership
        def deregister(name, sender):
            print(name, sender)
            print("Deregister call")
            print(self.files[name])
            if sender == self.files[name]:
                del self.files[name]

        # Function to send private messages to clients
        def privatemessage(name, pm, requestee):
            if name in storage:
                storage[name].send(pm.encode('utf-8'))
            else:
                storage[requestee].send("User not available".encode('utf-8'))

        # Function to handle client connections
        def handle_client(client):
            while True:
                try:
                    message = client.recv(1024).decode('utf-8')
                    contents = message.split("_")
                    # Handle different commands received from clients
                    if contents[1] in self.query:
                        contents[0] = contents[0].replace(":", "")
                        response = client.recv(1024).decode('utf-8')
                        search = response.split("_")
                        query()
                    elif contents[1] == "request":
                        client.send('Enter the name of the request target: '.encode('utf-8'))
                        response = client.recv(1024).decode('utf-8')
                        target = response.split("_")
                        fileRequest(target[1])
                    elif contents[1] == "private":
                        client.send('Who would you like to send a Private Message to?'.encode('utf-8'))
                        response = client.recv(1024).decode('utf-8')
                        target = response.split("_")
                        client.send('What would you like to say?'.encode('utf-8'))
                        pmess = client.recv(1024).decode('utf-8')
                        pm = pmess.split("_")
                        privatemessage(target[1], pm[1], contents[0])
                    elif contents[1] in self.cancel:
                        client.send('shutdown'.encode('utf-8'))
                    elif contents[1] == "register":
                        client.send("What is the filename?".encode('utf-8'))
                        response = client.recv(1024).decode('utf-8')
                        contents[0] = contents[0].replace(":", "")
                        fileinfo = response.split("_")
                        if fileinfo[1] == "":
                            print("Invalid response")
                        register(fileinfo[1], contents[0])
                    elif contents[1] == "deregister":
                        client.send("What is the filename?".encode('utf-8'))
                        response = client.recv(1024).decode('utf-8')
                        contents[0] = contents[0].replace(":", "")
                        fileinfo = response.split("_")
                        if fileinfo[1] == "":
                            print("Invalid response")
                        deregister(fileinfo[1], contents[0])
                    else:
                        message = contents[0] + " " + contents[1]
                        broadcast(message.encode('utf-8'))
                except:
                    index = clients.index(client)
                    clients.remove(client)
                    client.close()
                    user = users[index]
                    del storage[user]
                    broadcast(f'{user} has disconnected!'.encode('utf-8'))
                    users.remove(user)
                    break

        # Function to receive incoming connections
        def receive():
            while True:
                print('Server is active [+]')
                client, address = server.accept()  # Accept incoming connection
                print(f'Connection active with {str(address)}')
                client.send('alias?'.encode('utf-8'))  # Request client's username
                user = client.recv(1024).decode('utf-8')  # Receive client's username
                users.append(user)  # Add username to list of connected users
                clients.append(client)  # Add client socket to list of clients
                storage.update({user: client})  # Update storage with client information
                print(str(f"The username of this client is {user}"))
                broadcast(f"User [{user}] has connected".encode('utf-8'))  # Broadcast user connection
                client.send("\nConnection live!".encode('utf-8'))  # Notify client of successful connection
                # Start a new thread to handle client communication
                thread = threading.Thread(target=handle_client, args=(client,))
                thread.start()

        receive()  # Start receiving incoming connections

    # Client mode for connecting to a host
    def client_mode(self):
        IP = socket.gethostbyname(socket.gethostname())  # Get the IP address of the local machine
        user = input('Create a username: ')  # Get user's username
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create client socket
        client.connect((IP, 59000))  # Connect to host

        # Function to receive messages from the server
        def client_receive():
            while True:
                try:
                    message = client.recv(1024).decode('utf-8')  # Receive message from server
                    if message == "alias?":
                        client.send(user.encode('utf-8'))  # Send user's username to server
                    elif message == "shutdown":
                        sys.exit()  # Shutdown client
                    else:
                        print(message)  # Print message from server
                except:
                    print("Error")
                    client.close()  # Close client socket
                    break

        # Function to send messages to the server
        def client_send():
            while True:
                text = input("")  # Get user input
                message = f'{user}:_{text}'  # Format message
                client.send(message.encode('utf-8'))  # Send message to server

        receive_thread = threading.Thread(target=client_receive)  # Create thread for receiving messages
        receive_thread.start()  # Start receiving thread

        send_thread = threading.Thread(target=client_send)  # Create thread for sending messages
        send_thread.start()  # Start sending thread

    # Function to receive files
    def get_file(self, sender):
        data = sender.recv(1024).decode("utf-8")  # Receive file metadata
        contents = data.split("_")
        name = contents[0]  # Extract file name
        size = int(contents[1])  # Extract file size

        with open(f"recv_{name}", "w") as f:  # Open file for writing
            while True:
                data = sender.recv(2048).decode("utf-8")  # Receive file data
                if not data:
                    break
                f.write(data)  # Write data to file

    # Function to send files
    def send_file(self, target):
        while True:
            name = input("\nInput file name: \n")  # Get file name from user
            if name in self.files:
                print("File found.")
                break
            else:
                print("File not found.\nFile list: ", list(self.files.keys()))

        size = os.path.getsize(name)  # Get file size
        data = f"{name}_{size}"  # File metadata
        target.send(data.encode("utf-8"))  # Send file metadata to target

        with open(name, "r") as f:  # Open file for reading
            while True:
                data = f.read(2048)  # Read file data
                if not data:
                    break
                target.send(data.encode("utf-8"))  # Send file data to target

    # Function to handle data transfer protocol
    def data_protocol(self):
        if self.setting == "host":
            receiver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create receiver socket
            receiver.bind(('', self.Transfer))  # Bind receiver to specified port
            print("Host IP:", self.IP)
            receiver.listen()  # Start listening for incoming connections
            print("Awaiting Sender Connection...")

            sender, address = receiver.accept()  # Accept incoming connection
            print(f"Sender connected from {address[0]}:{address[1]}")
            self.get_file(sender)  # Receive file from sender

            sender.close()  # Close sender socket
            receiver.close()  # Close receiver socket
            time.sleep(10)  # Pause execution for 10 seconds

        if self.setting == "client":
            sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create sender socket
            sender.connect((self.IP, self.Transfer))  # Connect to receiver

            self.send_file(sender)  # Send file to receiver

            sender.close()  # Close sender socket
            time.sleep(10)  # Pause execution for 10 seconds

    # Function to list available files
    def fileList(self):
        all_files = os.listdir()  # Get list of all files in current directory
        txt_files = filter(lambda x: x[-4:] == '.txt', all_files)  # Filter text files
        for x in txt_files:
            self.files.update({x: os.path.getsize(x)})  # Add file information to dictionary

    # Function to start the application
    def Startup(self, x):
        options = ["host", "join", "quit"]  # List of options
        fileshare = input("Send/receive files? [yes/no]\n").lower().strip()  # Prompt user for file sharing

        if x in options:
            if x == "host" and fileshare == "yes":
                self.setting = "host"
                self.data_protocol()
                self.host_mode()
            elif x == "join" and fileshare == "yes":
                self.fileList()
                self.setting = "client"
                self.data_protocol()
                self.client_mode()
            if x == "host" and fileshare == "no":
                self.setting = "host"
                self.host_mode()
            elif x == "join" and fileshare == "no":
                self.setting = "client"
                self.client_mode()
            elif x == "quit":
                return
        else:
            y = input("Host a connection or join a connect? [host/join/quit]\n").lower().strip()
            self.Startup(y)

startup = input("Host a connection or join a connection? [host/join/quit]\n").lower().strip()
creation = App("created")  # Create App instance
creation.Startup(startup)  # Start the application
