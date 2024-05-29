import socket
import tkinter as tk
from tkinter import CENTER

class ClientGUI:
    def __init__(self):
        pass

    def receive_message(self):
        message = self.conn.recv(1024).decode()
        self.message_label.configure(text=message)

    def on_closing(self):
        self.root.withdraw()  # Hide the window instead of closing it

    def start_client(self):
        # Create a TCP/IP socket
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect(('localhost', 12345))

        # GUI setup
        self.root = tk.Tk()
        self.root.title("Client")

        # Set window size and position
        window_width = 400
        window_height = 200
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x_coordinate = int((screen_width - window_width) / 2)
        y_coordinate = int((screen_height - window_height) / 2)
        self.root.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")

        # Message label with larger font size
        self.message_label = tk.Label(self.root, text="", wraplength=380, font=("Arial", 14))
        self.message_label.pack(pady=20)

        # Start listening for messages
        self.receive_message()

        # Bind the closing event to on_closing function
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Start the GUI event loop
        self.root.mainloop()

# Instantiate and start the client
client = ClientGUI()
client.start_client()