import socket
import tkinter as tk

class ServerGUI:
    def __init__(self):
        pass

    def send_message(self):
        message = self.entry.get()
        self.conn.send(message.encode())
        self.entry.delete(0, tk.END)

    def close_connection(self):
        self.conn.close()
        self.server_socket.close()
        self.root.destroy()

    def accept_connection(self):
        self.conn, addr = self.server_socket.accept()
        self.label.configure(text=f"Connected to: {addr}")

    def start_server(self):
        # Create a TCP/IP socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('localhost', 12345))
        self.server_socket.listen(1)

        # GUI setup
        self.root = tk.Tk()
        self.root.title("Server")
        self.label = tk.Label(self.root, text="Waiting for connection...")
        self.label.pack()
        self.entry = tk.Entry(self.root)
        self.entry.pack()
        self.send_button = tk.Button(self.root, text="Send", command=self.send_message)
        self.send_button.pack()
        self.close_button = tk.Button(self.root, text="Close Connection", command=self.close_connection)
        self.close_button.pack()

        # Accept connections
        self.accept_connection()

        # Start the GUI event loop
        self.root.mainloop()

# Instantiate and start the server
server = ServerGUI()
server.start_server()