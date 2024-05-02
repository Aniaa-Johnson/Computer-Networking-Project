import socket
import json

def send_message(host, port, message):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    data = json.dumps(message)
    client_socket.send(data.encode())
    response = client_socket.recv(1024).decode()
    print("Response:", response)
    client_socket.close()

if __name__ == "__main__":
    host = 'localhost'  # Change this to the server's IP address if running on a different machine
    port = 8888  # Change this to the server's port if it's different
    
    # Example usage
    send_message(host, port, {'type': 'REGISTER', 'name': 'Alice', 'address': (host, port)})
    send_message(host, port, {'type': 'REGISTER', 'name': 'Bob', 'address': (host, port)})
    send_message(host, port, {'type': 'SEND', 'sender': 'Alice', 'recipient': 'Bob', 'message': 'Hello, Bob!'})

