import socket
import threading
import json

class ChildData:
    def __init__(self, name, parent_socket):
        self.name = name
        self.parent_socket = parent_socket

class ParentServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected_children = {}

    def start_server(self):
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen()
            print(f"Server listening on {self.host}:{self.port}")
            while True:
                client_socket, address = self.server_socket.accept()
                threading.Thread(target=self.handle_client, args=(client_socket,)).start()
        except Exception as e:
            print(f"Error starting the server: {e}")

    def handle_client(self, client_socket):
        try:
            data = client_socket.recv(1024)
            request = json.loads(data.decode('utf-8'))
            if request['type'] == 'parent_login':
                self.handle_parent_login(client_socket, request)
            elif request['type'] == 'child_registration':
                self.handle_child_registration(client_socket, request)
            else:
                print("Invalid request type from client")
        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            client_socket.close()

    def handle_parent_login(self, client_socket, request):
        # Implement parent login logic
        pass

    def handle_child_registration(self, client_socket, request):
        child_name = request['child_name']
        if child_name not in self.connected_children:
            self.connected_children[child_name] = ChildData(child_name, client_socket)
            print(f"Child '{child_name}' connected.")
        else:
            print(f"Child '{child_name}' already connected.")

# Example Usage:
host = '127.0.0.1'
port = 5555

parent_server = ParentServer(host, port)
parent_server.start_server()