import tkinter as tk
import socket
from tcp_by_size import send_with_size, recv_by_size
from zlib import decompress
from socket import socket as socki
import pygame
import sqlite3
from tkinter import ttk

WIDTH = 1900
HEIGHT = 1000


class CommandClient:
    def __init__(self):
        # Establishes a socket connection to the server
        self.names = []
        self.server_socket = socket.socket()
        self.server_socket.connect(("127.0.0.1", 33445))

        # Dictionary to store child accounts
        self.children = {}
        self.current_child = ""
        self.user_id = 0

        self.create_commands = [{"label": "Create new customer", "action": "PARENINSPAR", "inputs": ["name", "password", "email", "address", "phone"]},
                                {"label": "Create new child account", "action": "PARENINSKID", "inputs": ["child name", "parent name", "parent id", "birthday date"]}]
        self.commands = [
            {"label": "Time manager", "action": "PARENTMNAGE", "inputs": [""]},
            {"label": "Set timer for a break", "action": "PARENABREAK", "inputs": ["section time", "break time"]},
            {"label": "Website blocking", "action": "PARENBLOCKW", "inputs": ["website address"]},
            {"label": "Send a message to your kid", "action": "PARENMESSAG", "inputs": ["message"]},
            {"label": "Share screen", "action": "SHARESCREEN", "inputs": []}
        ]

    def execute_command(self, command_data, input_entries, result_label):
        action = command_data["action"]
        if action == "SHARESCREEN":
            self.share_screen()  # Initiates screen sharing
        else:
            if action == "PARENINSPAR" or action == "PARENINSKID":
                inputs = input_entries
                data = action

            else:
                inputs = input_entries
                data = action + self.children[self.current_child]

            for input_entry in inputs:
                data += "|" + input_entry.get()  # Constructs data string with inputs

            send_with_size(self.server_socket, data.encode())  # Sends data to the server
            response = recv_by_size(self.server_socket).decode()  # Receives response from the server
            response = response[7:]
            result_label.config(text="Output:\n" + response)  # Displays the response

    def create_command_window(self, command_data):
        if command_data["label"] == "Time manager":
            root = tk.Tk()
            root.geometry("470x340")
            app = ActiveAppScreenTimeApp(root)
            root.mainloop()
            pass
        command_window = tk.Toplevel(self.root)
        command_window.title(command_data["label"])

        input_entries = []
        for input_label in command_data["inputs"]:
            # Labels for input fields
            tk.Label(command_window, text=input_label + ":").pack()
            entry = tk.Entry(command_window)
            entry.pack()
            input_entries.append(entry)

        result_label = tk.Label(command_window, text="Output:")
        result_label.pack()

        submit_button = tk.Button(command_window, text="Submit",
                                  command=lambda: self.execute_command(command_data, input_entries, result_label))
        submit_button.pack()

    def create_user_window(self):
        user_window = tk.Toplevel()
        user_window.title("Create User")

        input_entries = []
        for input_label in self.create_commands[0]["inputs"]:
            # Labels and entry fields for user creation
            tk.Label(user_window, text=input_label + ":").pack()
            entry = tk.Entry(user_window)
            entry.pack()
            input_entries.append(entry)

        result_label = tk.Label(user_window, text="Output:")
        result_label.pack()

        submit_button = tk.Button(user_window, text="Create", command=lambda: self.create_new_user(input_entries, result_label))
        submit_button.pack()

    def create_new_user(self, input_entries, result_label):
        user_name = input_entries[0].get()

        if "--" in user_name:
            result_label.config(text="Invalid name, names cannot contain '--'")
            return

        self.execute_command(self.create_commands[0], input_entries, result_label)

    def create_child_account_window(self):
        user_window = tk.Toplevel()
        user_window.title("Create child account")

        input_entries = []
        for input_label in self.create_commands[1]["inputs"]:
            # Labels and entry fields for user creation
            tk.Label(user_window, text=input_label + ":").pack()
            entry = tk.Entry(user_window)
            entry.pack()
            input_entries.append(entry)

        result_label = tk.Label(user_window, text="Output:")
        result_label.pack()

        submit_button = tk.Button(user_window, text="Create", command=lambda: self.create_child_account(input_entries, result_label))
        submit_button.pack()

    def create_child_account(self, input_entries, result_label):
        user_name = input_entries[0].get()

        if "--" in user_name:
            result_label.config(text="Invalid name, names cannot contain '--'")
            return

        self.execute_command(self.create_commands[1], input_entries, result_label)

    def handle_login(self):
        name = self.name_entry.get()
        password = self.password_entry.get()
        user_id = self.id_entry.get()

        if "--" in name:
            response = "no"
        else:
            if name and password and user_id:  # Check if any field is empty
                login_data = f"PARENLOGINN|{name}|{password}|{user_id}"
                send_with_size(self.server_socket, login_data.encode())
                response = recv_by_size(self.server_socket).decode()
                response = response[8:]
            else:
                self.login_error_label.config(text="You need to fill all the fields")  # Display error message
                return  # Return without attempting login

        if response == "yes":
            self.user_id = user_id
            self.login_window.destroy()
            self.create_child_selection_window()
        else:
            self.login_error_label.config(text="Invalid login, please try again")

    # Method to create a window for selecting a child account
    def create_child_selection_window(self):
        self.master = tk.Tk()
        self.master.title("Select Child")

        self.names = []

        # Retrieves child accounts from the server
        send_with_size(self.server_socket, "PARENGETKID|" + str(self.user_id))
        children = recv_by_size(self.server_socket).decode()
        children = children[2:-2]
        children = children.split(",")

        for child in children:
            self.children[child[1:]] = child[0]
            child = child[1:]
            self.names.append(child)

        self.listbox = tk.Listbox(self.master)
        self.listbox.pack(pady=10)

        for name in self.names:
            self.listbox.insert(tk.END, name)

        self.select_button = tk.Button(self.master, text="Select", command=self.print_selection)
        self.select_button.pack()

        self.master.mainloop()

    def print_selection(self):  # Method to handle selection of a child account
        selected_index = self.listbox.curselection()
        if selected_index:
            index = selected_index[0]
            selected_name = self.listbox.get(index)
            self.current_child = selected_name
            print(self.current_child)
            self.open_main_window(selected_name)

    def open_main_window(self, selected_child_name):
        self.master.destroy()
        self.create_main_window(selected_child_name)

    def create_main_window(self, selected_child_name):
        self.root = tk.Tk()
        self.root.title("Commands")

        for command_data in self.commands:
            tk.Button(self.root, text=command_data["label"], command=lambda cmd=command_data: self.create_command_window(cmd)).pack()

        print("Selected Child:", selected_child_name)

        self.root.mainloop()

    def recvall(self, conn, length):
        """
            Retrieve all pixels.

            This method is responsible for receiving all pixel data from a socket connection.
            It ensures that all data is received by repeatedly calling recv() until the
            specified length of data is received.

            Args:
                conn (socket): The socket connection to receive data from.
                length (int): The expected length of the data to receive.

            Returns:
                bytes: The concatenated pixel data received from the socket.
            """

        buf = b''  # Initialize an empty buffer to store received data
        while len(buf) < length:
            data = conn.recv(length - len(buf))  # Receive data from the socket
            if not data:
                return data   # If no data is received, return an empty byte string
            buf += data  # Append the received data to the buffer
        return buf

    def share_screen(self, host='192.168.68.117', port=5000):
        """
            Share screen with a remote host.

            This method initiates the screen sharing functionality by connecting
            to a remote host and continuously sending screen data.
            """

        # Initialize Pygame and set up the display
        pygame.init()
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        clock = pygame.time.Clock()
        watching = True

        # Initialize a socket connection to the remote host
        sock = socki()
        sock.connect((host, port))
        try:
            # Continuously loop while screen sharing is active
            while watching:
                # Check for events such as quitting the screen sharing
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        watching = False
                        break

                # Retrieve the size of the pixel data
                size_len = int.from_bytes(sock.recv(1), byteorder='big')
                # Receive the pixel data of the specified size
                size = int.from_bytes(sock.recv(size_len), byteorder='big')
                # Receive all pixel data using recvall method
                pixels = decompress(self.recvall(sock, size))

                # Create the Surface from raw pixels
                img = pygame.image.fromstring(pixels, (WIDTH, HEIGHT), 'RGB')

                # Display the picture
                screen.blit(img, (200, 100))
                pygame.display.flip()
                clock.tick(60)
        finally:
            sock.close()
            pygame.quit()  # Properly quit Pygame when exiting the screen sharing

    def run(self):
        self.login_window = tk.Tk()
        self.login_window.title("Login")

        tk.Label(self.login_window, text="Name:").pack()
        self.name_entry = tk.Entry(self.login_window)
        self.name_entry.pack()

        tk.Label(self.login_window, text="Password:").pack()
        self.password_entry = tk.Entry(self.login_window, show="*")
        self.password_entry.pack()

        tk.Label(self.login_window, text="ID:").pack()
        self.id_entry = tk.Entry(self.login_window)
        self.id_entry.pack()

        login_button = tk.Button(self.login_window, text="Login", command=self.handle_login)
        login_button.pack()

        create_user_button = tk.Button(self.login_window, text="Create User", command=self.create_user_window)
        create_user_button.pack()

        create_child_button = tk.Button(self.login_window, text="Create child account", command=self.create_child_account_window)
        create_child_button.pack()

        self.login_error_label = tk.Label(self.login_window, text="")
        self.login_error_label.pack()

        self.login_window.mainloop()



class ActiveAppScreenTimeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Active App Screen Time")

        self.label_title = tk.Label(root, text="Active App Screen Time", font=("Helvetica", 16))
        self.label_title.pack(pady=(10, 5))

        self.scrollbar = ttk.Scrollbar(root)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas = tk.Canvas(root, yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar.config(command=self.canvas.yview)

        self.scrollable_frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.retrieve_screen_time()

        self.scrollable_frame.bind("<Configure>", self.on_frame_configure)

    def retrieve_screen_time(self):
        conn = sqlite3.connect('screen_time.db')
        c = conn.cursor()

        c.execute("SELECT app, SUM(time) FROM ScreenTime GROUP BY app")
        screen_time_data = c.fetchall()

        for app, time in screen_time_data:
            self.create_app_frame(app, time)

        conn.close()

    def create_app_frame(self, app, total_time_seconds):
        total_hours = int(total_time_seconds) // 3600
        total_minutes = int((total_time_seconds % 3600) // 60)
        total_seconds = int(total_time_seconds % 60)
        time_str = f"{total_hours:02d}:{total_minutes:02d}:{total_seconds:02d}"

        app_frame = tk.Frame(self.scrollable_frame, borderwidth=2, relief="groove", padx=10, pady=5)
        app_frame.pack(pady=5, fill=tk.X)

        app_label = tk.Label(app_frame, text=f"App: {app}", font=("Helvetica", 12))
        app_label.pack(anchor="w")

        time_label = tk.Label(app_frame, text=f"Time: {time_str}", font=("Helvetica", 12))
        time_label.pack(anchor="w")

    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

def login():
    client = CommandClient()
    client.run()


if __name__ == '__main__':
    login()
