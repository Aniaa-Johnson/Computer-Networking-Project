import socket
import threading
import json

class Peer:
    def __init__(self, name, address):
        self.name = name
        self.address = address

class P2PChatApp:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.peers = []
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Server listening on {self.host}:{self.port}")

    def accept_connections(self):
        while True:
            client_socket, client_address = self.server_socket.accept()
            print(f"Connection established with {client_address}")
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()

    def handle_client(self, client_socket):
        while True:
            try:
                data = client_socket.recv(1024)
                if not data:
                    break
                message = json.loads(data.decode())
                message_type = message['type']

                if message_type == 'REGISTER':
                    self.register_peer(message['name'], message['address'])
                    client_socket.send(json.dumps({'type': 'ACKNOWLEDGE'}).encode())
                elif message_type == 'DEREGISTER':
                    self.deregister_peer(message['name'])
                    client_socket.send(json.dumps({'type': 'ACKNOWLEDGE'}).encode())
                elif message_type == 'SEND':
                    sender = message['sender']
                    recipient = message['recipient']
                    msg = message['message']
                    self.send_message(sender, recipient, msg)
                    client_socket.send(json.dumps({'type': 'ACKNOWLEDGE'}).encode())
                elif message_type == 'REQUEST_DOWNLOAD':
                    resource_name = message['resource_name']
                    self.request_download(client_socket, resource_name)
                elif message_type == 'GET_DATA':
                    resource_name = message['resource_name']
                    self.get_data(client_socket, resource_name)
                elif message_type == 'LIST_RESOURCES':
                    self.list_resources(client_socket)
                elif message_type == 'SEARCH_INDEX':
                    keyword = message['keyword']
                    self.search_index(client_socket, keyword)

            except Exception as e:
                client_socket.send(json.dumps({'type': 'ERROR', 'message': str(e)}).encode())
                print(f"Error: {e}")
                break

        client_socket.close()

    def register_peer(self, name, address):
        peer = Peer(name, address)
        self.peers.append(peer)
        print(f"Peer {name} joined the network.")

    def deregister_peer(self, name):
        self.peers = [peer for peer in self.peers if peer.name != name]
        print(f"Peer {name} left the network.")

    def send_message(self, sender, recipient, message):
        recipient_peer = next((peer for peer in self.peers if peer.name == recipient), None)
        if recipient_peer:
            try:
                recipient_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                recipient_socket.connect((recipient_peer.address[0], recipient_peer.address[1]))
                data = json.dumps({'type': 'SEND', 'sender': sender, 'message': message})
                recipient_socket.send(data.encode())
                print(f"Message sent from {sender} to {recipient}: {message}")
            except Exception as e:
                print(f"Error sending message to {recipient}: {e}")
        else:
            print(f"Recipient {recipient} not found.")

    def request_download(self, client_socket, resource_name):
        # Simulated response for request_download
        client_socket.send(json.dumps({'type': 'ACKNOWLEDGE', 'message': f'Request to download {resource_name} received.'}).encode())

    def get_data(self, client_socket, resource_name):
        # Simulated response for get_data
        client_socket.send(json.dumps({'type': 'ACKNOWLEDGE', 'message': f'Data for {resource_name} sent.'}).encode())

    def list_resources(self, client_socket):
        # Simulated response for list_resources
        resources = ['Resource1', 'Resource2', 'Resource3']
        client_socket.send(json.dumps({'type': 'LIST_RESOURCES', 'resources': resources}).encode())

    def search_index(self, client_socket, keyword):
        # Simulated response for search_index
        results = ['Resource1', 'Resource2']
        client_socket.send(json.dumps({'type': 'SEARCH_RESULTS', 'results': results}).encode())

    def start(self):
        threading.Thread(target=self.accept_connections).start()


if __name__ == "__main__":
    # Initialize the P2P chat app
    app = P2PChatApp('0.0.0.0', 8888)
    app.start()

