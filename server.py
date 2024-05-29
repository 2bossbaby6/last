import socket
import threading
import tkinter as tk
from tkinter import messagebox
import json

names = []  # List to store the connected clients' names
connections = {}  # a dictionary that have a clients name and socket
names2 = []


class GameRequestAppServer:
    def __init__(self):
        self.clients = None
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # opening the server
        self.server_socket.bind(("localhost", 8080))
        self.server_socket.listen(5)
        print("Server started and listening on port 8080...")

    def send_updated_names_to_clients(self, client_socket):  # a function to send the names list without the players
        # name when they enter the game
        names_json = json.dumps(names)
        names_len = str(len(names_json)) + ','
        client_socket.send(names_len.encode())  # sending the list's length
        client_socket.send(names_json.encode())  # sending the list to the client

    def send_names_to_clients(self, client_socket):  # sending the names list to the client
        client_socket.send('nam'.encode())  # the protocol
        names_json = json.dumps(names)
        names_len = str(len(names_json)) + ','
        client_socket.send(names_len.encode())  # sending the list's length
        client_socket.send(names_json.encode())  # sending the list to the client

    def handle_client(self, client_socket, client_address):
        global name
        try:
            name = client_socket.recv(1024).decode()  # receiving the client's name
            names.append(name)  # Add the connected client's name to the list
            connections[name] = client_socket  # adding the client to the connections dictionary
            names2.append(name)  # Add the connected client's name to the backup list
            for client in self.clients:
                self.send_names_to_clients(client)  # sending the names list to all the  clients after i added a new
                # client
            print(f"{name} connected. Total connected clients: {len(names)}")

            while True:
                data = client_socket.recv(3).decode()  # receiving the protocol
                if data == "":
                    break
                selected_name = ""  # the name of the opponent
                finish = False
                while not finish:  # receiving the selected name
                    data2 = client_socket.recv(1).decode()
                    if data2 == '+':
                        finish = True
                    elif data == ' ':
                        data = data
                    else:
                        selected_name += data2

                from_name = ""  # the user sent the request
                finish = False
                while not finish:  # receiving the from name
                    data2 = client_socket.recv(1).decode()
                    if data2 == '+':
                        finish = True
                    else:
                        from_name += data2

                if data == 'req':  # protocol name for request
                    request = 'req' + str(len(from_name)) + ',' + from_name  # creating a message to send to the
                    # opponent
                    connections[selected_name].send(request.encode())  # sending the message to the opponent
                    print(f"Game request by {from_name} to {selected_name}!")

                if data == 'ans':  # protocol for answer
                    response = client_socket.recv(3).decode()  # receiving if the answer is yes or no
                    if response == "yes":
                        ans = 'ansyes' + str(len(from_name)) + ',' + from_name  # creating a message for the opponent
                        connections[selected_name].send(ans.encode())  # sending the message to the opponent
                        print(f"Game request accepted by {from_name}!")
                        names.remove(from_name)  # removing the names of the two players so
                        names.remove(selected_name)  # I can delete them from the lobby
                        pong_game2(client_socket, selected_name, 1)  # starting the game for the first player
                        names.append(from_name)  # after the game ends return the player to the lobby
                        print("fromname: " + from_name)
                        for client in self.clients:  # send the new lobby list to all the players
                            self.send_names_to_clients(client)

                    elif response == "noo":
                        connections[selected_name].send('ansnoo'.encode())  # sending to the opponent the request was
                        # declined
                        print(f"Game request rejected by {selected_name}!")

                if data == "res":  # protocol for did agree for game
                    res = client_socket.recv(3).decode()  # receiving yes or no
                    if res == "yes":
                        for client in self.clients:  # sending the new lobby to all the players
                            if client == connections[selected_name]:  # if it's the player who is in the game
                                self.send_updated_names_to_clients(client)  # send him a different message without the nam
                            elif client == connections[from_name]:   # if it's the player who is in the game
                                self.send_updated_names_to_clients(client)  # send him a different message without the nam
                            else:   # if it's the player who is not in the game
                                self.send_names_to_clients(client)  # send him the protocol message
                        pong_game2(client_socket, from_name, 2)  # start the game for player 2
                        names.append(name)  # return the player to the lobby after the game ends
                        print("name: "+name)
                        for client in self.clients:  # send the new lobby list to all the players
                            self.send_names_to_clients(client)


            names.remove(name)  # Remove the disconnected client's name from the list
            print(f"{name} disconnected. Total connected clients: {len(names)}")
            self.send_names_to_clients(client_socket)

        except ConnectionResetError:
            names.remove(name)  # Remove the disconnected client's name from the list
            print(f"{name} disconnected. Total connected clients: {len(names)}")
            self.send_names_to_clients(client_socket)
        except Exception as e:
            print(f"Error occurred for {name}: {str(e)}")
            names.remove(name)  # Remove the disconnected client's name from the list
            self.send_names_to_clients(client_socket)

    def run(self):
        self.clients = []  # List to store client sockets and addresses

        while True:
            client_socket, client_address = self.server_socket.accept()  # getting a new client
            print(f"Connection received from: {client_address}")
            self.clients.append(client_socket)
            # open a new thread for him
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address))
            client_thread.start()


def pong_game2(client_socket, opponent_name, client_number):   # the game for the second player
    game_on = True
    while game_on:
        res = client_socket.recv(4).decode()  # the protocol
        if res == "endg":  # end the game
            client_socket.send("endg".encode())
            game_on = False

        elif res == "mv1u":  # move player 1 up
            if client_number == 1:
                connections[opponent_name].send("movu".encode())
            elif client_number == 2:
                client_socket.send("movu".encode())

        elif res == "mv2u":  # move player 2 up
            if client_number == 2:
                connections[opponent_name].send("movu".encode())
            elif client_number == 1:
                client_socket.send("movu".encode())

        elif res == "mv1d":  # move player 1 down
            if client_number == 1:
                connections[opponent_name].send("movd".encode())
            elif client_number == 2:
                client_socket.send("movd".encode())

        elif res == "mv2d":  # move player 2 down
            if client_number == 2:
                connections[opponent_name].send("movd".encode())
            elif client_number == 1:
                client_socket.send("movd".encode())





if __name__ == "__main__":
    server = GameRequestAppServer()
    server.run()  # starting the game

