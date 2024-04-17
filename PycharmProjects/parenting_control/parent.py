import socket
import json
import time
import arp
import spoofing
import html_sql_client
from scapy.all import sniff
import multiprocessing
from multiprocessing import Queue
import threading



class Parent:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.connected_children = {}

    def connect_to_server(self):
        # Implement server connection logic
        pass

    def login(self):
        # Implement login logic
        lient_thread = threading.Thread(target=html_sql_client.login)
        lient_thread.start()

    def add_child(self, child_name):
        # Implement adding child logic
        pass

    def show_connected_children(self):
        # Display connected children
        pass

    def parental_control_menu(self, child_name):
        # Implement parental control menu logic
        pass

    def remind_to_take_break(self, child_name):
        print(f"\nReminder for {child_name}: It's time for an eye break from the computer.")
        print("Leave your computer and come back in about five minutes.")
        time.sleep(300)  # Wait for 5 minutes

    def set_screen_time_limits(self, child_name):
        # Implement screen time limits logic
        pass

    def restrict_websites(self, child_name):
        # Implement website restriction logic
        pass

    def configure_arp_spoofing(self):
        q = Queue()
        client_thread = multiprocessing.Process(target=arp1, args=())
        client_thread2 = multiprocessing.Process(target=spoof1, args=(q,))
        client_thread.start()
        client_thread2.start()
        print(str(q.get()))



    def view_child_screen_time(self, child_name):
        # Implement screen time view logic
        pass

    def take_control_of_child_screen(self, child_name):
        # Implement taking control of child's screen logic (Optional)
        pass


def arp1():
    arp.main()

def spoof1(q):
    spoofing.main(q)
    print(str(q))


if __name__ == "__main__":
    par = Parent("ma", "ta")
    par.configure_arp_spoofing()
    par.login()


# Example Usage:
