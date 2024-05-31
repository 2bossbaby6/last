import socket
import json
import time
from tcp_by_size import send_with_size, recv_by_size
import threading
import tkinter as tk
from socket import socket as socki
from threading import Thread
from zlib import compress

from mss import mss
import sqlite3
import pygetwindow as gw

DEBUG = True
child_name = "idan"
child_id = "0"
class Child:
    def __init__(self, child_name, child_id):
        self.child_name = child_name
        self.child_id = child_id
        self.server_socket = socket.socket()
        self.server_socket.connect(("172.16.14.209", 33445))
        self.connected_to_server = False

    def login_to_server(self):
        data = "CHILDLOGINN|" + str(self.child_name) + "|" + str(self.child_id)
        send_with_size(self.server_socket, data.encode())
        data = recv_by_size(self.server_socket).decode()
        print(data)
        fields = data.split("|")
        if fields[1] == "yes":
            thread1 = threading.Thread(target=self.handle_child, args=())
            thread1.start()
        else:
            print("error connecting")

    def handle_child(self):
        while True:
            data = recv_by_size(self.server_socket)
            if data == "":
                print("Error: Seens Client DC")
                break
            data = data.decode()
            action = data[:6]
            data = data[7:]
            fields = data.split("|")

            if DEBUG:
                print("Got client request " + action + " -- " + str(fields))
#
            if action == "ABREAK":
                session_time, break_time = fields[0], fields[1]
                client_thread = threading.Thread(target=self.a_break, args=(int(session_time), int(break_time)))
                client_thread.start()

            elif action == "MESSAG":
                message = fields[0]
                self.display_text(message)

            elif action == "TMNANG":
                pass

    def a_break(self, session_time, break_time):
        while True:
            # Session time
            print(f"Session time started. You have {session_time} seconds to use the computer freely.")
            time.sleep(session_time)

            # Break time
            print(f"Break time started. Computer will be locked for {break_time} seconds.")
            self.lock_screen(break_time)
            time.sleep(break_time)

    def lock_screen(self, break_time):
        # Create a fullscreen window that prevents user interaction
        root = tk.Tk()
        root.attributes('-fullscreen', True)
        root.attributes('-topmost', True)  # Make window stay on top

        # Remove minimize, maximize, and close buttons
        root.overrideredirect(True)

        # Label to show break time message
        label = tk.Label(root, text=f"Break Time - Computer Locked for {break_time} seconds", font=("Helvetica", 24))
        label.pack(expand=True)

        # After break_time seconds, destroy the window
        root.after(break_time * 1000, root.destroy)

        root.mainloop()

    def center_window(self, window, width, height):
        # Get screen width and height
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()

        # Calculate position x and y for the window to be centered
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        # Set window position
        window.geometry(f'{width}x{height}+{x}+{y}')

    def display_text(self, text):
        # Create a Tkinter window
        window = tk.Tk()
        window.title("Text Display")

        # Get screen width and height
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()

        # Set text font and size
        text_font = ('Helvetica', 12)

        # Create a label to display the text
        label = tk.Label(window, text=text, font=text_font, wraplength=screen_width)
        label.pack(padx=20, pady=20)

        # Calculate suitable window size based on text length
        text_length = len(text)
        window_width = min(text_length * 10, screen_width - 100)
        window_height = min((text_length // 50 + 1) * 25, screen_height - 100)

        # Increase the window size
        window_width *= 4
        window_height *= 4

        self.center_window(window, window_width, window_height)

        # Start the Tkinter event loop
        window.mainloop()


# Example Usage:
#
# child = Child(child_name)
# child.connect_to_server()
#
# if not child.connected_to_server:
#     print("Failed to connect to the server. Exiting.")
#     exit()
#
# child.register_on_server()
# child.run_background_monitoring()

WIDTH = 1900
HEIGHT = 1000


def retreive_screenshot(conn):
    """
       Retrieve screenshot and send it over a socket connection.

       This function captures the screen, compresses the image, and sends it
       over the provided socket connection.
       """

    with mss() as sct:
        # The region to capture
        rect = {'top': 0, 'left': 0, 'width': WIDTH, 'height': HEIGHT}

        while 'recording':
            # Capture the screen
            img = sct.grab(rect)
            # Tweak the compression level here (0-9)
            pixels = compress(img.rgb, 6)

            # Send the size of the pixels length
            size = len(pixels)
            size_len = (size.bit_length() + 7) // 8
            conn.send(bytes([size_len]))

            # Send the actual pixels length
            size_bytes = size.to_bytes(size_len, 'big')
            conn.send(size_bytes)

            # Send pixels
            conn.sendall(pixels)


def share_sceen(host='0.0.0.0', port=4000):
    sock = socki()
    sock.bind((host, port))
    try:
        sock.listen(5)
        print('Server started.')

        while 'connected':
            conn, addr = sock.accept()
            print('Client connected IP:', addr)
            thread = Thread(target=retreive_screenshot, args=(conn,))
            thread.start()
    finally:
        sock.close()

def record_screen_time():
    conn = sqlite3.connect('screen_time.db')
    c = conn.cursor()

    # Create table if not exists
    c.execute('''CREATE TABLE IF NOT EXISTS ScreenTime
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                 app TEXT NOT NULL, 
                 time INTEGER NOT NULL)''')

    active_apps = {}  # Dictionary to store start time of each active app

    while True:
        current_active_app = gw.getActiveWindowTitle()
        current_time = int(time.time())

        if current_active_app:
            if current_active_app not in active_apps:
                active_apps[current_active_app] = current_time
                # If there isn't a row for this app, add one
                c.execute("INSERT INTO ScreenTime (app, time) VALUES (?, ?)", (current_active_app, 0))
                conn.commit()
            else:
                # Calculate the screen time and update the database
                time_diff = current_time - active_apps[current_active_app]

                # Update the time for the existing row in the database
                c.execute("UPDATE ScreenTime SET time = time + ? WHERE app = ?", (time_diff, current_active_app))
                conn.commit()

                # Update the start time for the active app
                active_apps[current_active_app] = current_time

        time.sleep(1)  # Record every second

    conn.close()


def record_screen_time():
    conn = sqlite3.connect('screen_time.db')
    c = conn.cursor()

    # Create table if not exists
    c.execute('''CREATE TABLE IF NOT EXISTS ScreenTime
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                 app TEXT NOT NULL, 
                 time INTEGER NOT NULL)''')

    active_apps = {}  # Dictionary to store start time of each active app

    while True:
        current_active_app = gw.getActiveWindowTitle()
        current_time = int(time.time())

        if current_active_app:
            if current_active_app not in active_apps:
                active_apps[current_active_app] = current_time
                # If there isn't a row for this app, add one
                c.execute("INSERT INTO ScreenTime (app, time) VALUES (?, ?)", (current_active_app, 0))
                conn.commit()
            else:
                # Calculate the screen time and update the database
                time_diff = current_time - active_apps[current_active_app]

                # Update the time for the existing row in the database
                c.execute("UPDATE ScreenTime SET time = time + ? WHERE app = ?", (time_diff, current_active_app))
                conn.commit()

                # Update the start time for the active app
                active_apps[current_active_app] = current_time

        time.sleep(1)  # Record every second

    conn.close()

if __name__ == '__main__':
    child_name = "idan"
    child_id = "0"
    share_screen_thread = threading.Thread(target=share_sceen, args=())
    share_screen_thread.start()
    screen_time_thread = threading.Thread(target=record_screen_time, args=())
    screen_time_thread.start()
    child_instance = Child(child_name, child_id)
    child_instance.login_to_server()