import tkinter as tk
import socket
from tcp_by_size import send_with_size, recv_by_size


class CommandClient:
    def __init__(self):
        self.cli_s = socket.socket()
        self.cli_s.connect(("127.0.0.1", 33445))
        self.commands = [
            {"label": "Time manager", "action": "TMNAGE", "inputs": [""]},
            {"label": "Set timer for a break", "action": "ABREAK", "inputs": ["section time", "break time"]},
            {"label": "Website blocking", "action": "DLTUSR", "inputs": ["website address"]},
            {"label": "Send a message to your kid", "action": "CUSLST", "inputs": ["message"]},
            {"label": "Exit", "action": "RULIVE", "inputs": []}
        ]

    def execute_command(self, command_data, input_entries, result_label):
        action = command_data["action"]
        inputs = input_entries
        data = "PAREN" + action

        for input_entry in inputs:
            data += "|" + input_entry.get()

        send_with_size(self.cli_s, data.encode())
        response = recv_by_size(self.cli_s).decode()
        response = response[7:]
        result_label.config(text="Output:\n" + response)

    def create_command_window(self, command_data):
        command_window = tk.Toplevel(self.root)
        command_window.title(command_data["label"])

        input_entries = []
        for input_label in command_data["inputs"]:
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
        user_window = tk.Toplevel(self.root)
        user_window.title("Create User")

        input_entries = []
        for input_label in self.commands[1]["inputs"]:
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

        self.execute_command(self.commands[1], input_entries, result_label)

    def handle_login(self):
        name = self.name_entry.get()
        password = self.password_entry.get()
        user_id = self.id_entry.get()

        if "--" in name:
            response = "no"
        else:
            login_data = f"LOGINN|{name}|{password}|{user_id}"
            send_with_size(self.cli_s, login_data.encode())
            response = recv_by_size(self.cli_s).decode()
            response = response[8:]

        if response == "yes":
            self.login_window.destroy()
            self.create_child_selection_window()
        else:
            self.login_error_label.config(text="Invalid login, please try again")

    def create_child_selection_window(self):
        self.root = tk.Tk()
        self.root.title("Select Child")

        selected_child = tk.StringVar()
        selected_child.set("")  # Default value

        children = ["Child1", "Child2", "Child3"]

        for child in children:
            tk.Radiobutton(self.root, text=child, variable=selected_child, value=child).pack()

        confirm_button = tk.Button(self.root, text="Confirm", command=lambda: self.open_main_window(selected_child.get()))
        confirm_button.pack()

        self.root.mainloop()

    def open_main_window(self, selected_child_name):
        self.root.destroy()
        self.create_main_window(selected_child_name)

    def create_main_window(self, selected_child_name):
        self.root = tk.Tk()
        self.root.title("Commands")

        for command_data in self.commands:
            tk.Button(self.root, text=command_data["label"], command=lambda cmd=command_data: self.create_command_window(cmd)).pack()

        print("Selected Child:", selected_child_name)

        self.root.mainloop()

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

        self.login_error_label = tk.Label(self.login_window, text="")
        self.login_error_label.pack()

        self.login_window.mainloop()


def login():
    client = CommandClient()
    client.run()


if __name__ == '__main__':
    login()
