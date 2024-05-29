import socket
import tkinter as tk
from tkinter import messagebox
import json
import threading
import pygame
import os

names = []


class GameRequestAppClient:
    def __init__(self):
        self.client_name = None
        self.send_button = None
        self.name_list = None
        self.names = None
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # connecting to the server
        self.server_socket.connect(("localhost", 8080))

        self.root = tk.Tk()
        self.root.title("Game Request")

        self.create_widgets()

    def create_widgets(self):
        self.name_list = tk.Listbox(self.root)
        self.client_name = get_user_name()
        print(self.client_name)
        self.server_socket.send(self.client_name.encode())  # Send the client's name to the server
        self.name_list.pack()  # the lobby names list

        # crating a thread for running the client
        client_thread = threading.Thread(target=self.run_client, args=())
        client_thread.start()

        self.send_button = tk.Button(self.root, text="Send Request", command=self.send_request)
        self.send_button.pack()  # a button that sends a request to player he is choosing from the list

    def update_names_list(self):
        names_len = ''
        self.name_list.delete(0, tk.END)  # Clear the existing list

        finish = False
        while not finish:
            data = self.server_socket.recv(1).decode()
            if data == ',':  # when , is showing it means i got all length
                finish = True
            else:
                names_len += data
        data = self.server_socket.recv(int(names_len)).decode()  # receiving the names list
        names = json.loads(data)  # a command that convert the data received to a list
        self.name_list.delete(0, tk.END)  # deleting all the names in the list so can bring the new one
        for name2 in names:
            if name2 != self.client_name:  # I don't want the client's name to appear in the list
                self.name_list.insert(tk.END, name2)  # adding the name to the list

    def send_request(self):
        selected_index = self.name_list.curselection()  # getting the name the client chose
        if selected_index:  # if a name was peaked from the lobby
            req = "req" + self.name_list.get(selected_index) + '+' + self.client_name + '+'
                            # the name that the client selected        the client's name

            self.server_socket.send(req.encode())

        else:
            messagebox.showwarning("No Name Selected", "Please select a name from the list.")

    def run_client(self):
        while True:
            data = self.server_socket.recv(3).decode()  # protocol
            print(str(data))

            if data == 'ans':
                response = self.server_socket.recv(3).decode()
                print(str(response))
                if response == 'yes':  # client aggregated to a game
                    from_name_length = ''
                    got_length = False
                    while not got_length:
                        data = self.server_socket.recv(1).decode()
                        if data != ',':  # when data == ',' got length
                            from_name_length += data
                        else:
                            got_length = True
                    print(str(from_name_length))
                    from_name = self.server_socket.recv(int(from_name_length)).decode()  # opponent's name
                    print(str(from_name))
                    res = "res" + self.client_name + "+" + from_name + "+" + "yes"  # creating response
                    print(str(res))
                    self.server_socket.send(res.encode())
                    self.update_names_list()  # removing the client form the lobby
                    pong_game(2, self.server_socket)  # starting the game
                    print("hello")
                    name = 1
                    print("print")
                elif response == 'noo':
                    messagebox.showinfo('message', 'opponent disagreed')
            elif data == 'nam':  # update names list
                self.update_names_list()

            elif data == 'req':  # request to play
                from_name_length = ''
                got_length = False
                while not got_length:
                    data = self.server_socket.recv(1).decode()
                    if data != ',':  # when data == ',' got length
                        from_name_length += data
                    else:
                        got_length = True
                print(str(from_name_length))
                from_name = self.server_socket.recv(int(from_name_length)).decode()  # opponent's name
                print(str(from_name))
                response = messagebox.askyesno("Game Request", f"Do you want to play a game with {from_name}?")
                if response:  # if the response is positive
                    response_to_send = 'ans' + from_name + '+' + self.client_name + '+' + 'yes'
                    print(str(response_to_send))
                    self.server_socket.send(response_to_send.encode())  # send the response
                    self.update_names_list()  # remove the client from the lobby

                    pong_game(1, self.server_socket)  # starting the game

                else:
                    response_to_send = 'ans' + '+' + from_name + '+' + 'noo'  # negative response
                    print(str(response_to_send))
                    self.server_socket.send(response_to_send.encode())

    def run(self):
        self.root.mainloop()


def get_user_name():
    def store_name():
        nonlocal name
        name = name_entry.get()
        root.quit()  # Close the tkinter window

    root = tk.Tk()
    root.title("Enter Your Name")

    # Create a label and an entry widget for the name
    name_label = tk.Label(root, text="Enter Your Name:")
    name_label.pack()

    name_entry = tk.Entry(root)
    name_entry.pack()

    # Create a button to store the name
    store_button = tk.Button(root, text="Store Name", command=store_name)
    store_button.pack()

    # Initialize the name variable
    name = None

    root.mainloop()

    root.destroy()

    # The tkinter window is closed, and the entered name is stored in the "name" variable
    return name


# game settings
pygame.init()

WIDTH, HEIGHT = 700, 500  # screen size

FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

PADDLE_WIDTH, PADDLE_HEIGHT = 20, 100  # paddle size
BALL_RADIUS = 7

WINNING_SCORE = 10


class Paddle:
    COLOR = WHITE
    VEL = 4

    def __init__(self, x, y, width, height):
        self.x = self.original_x = x  # Initialize paddle's x-coordinate and original x-coordinate
        self.y = self.original_y = y  # Initialize paddle's y-coordinate and original y-coordinate
        self.width = width
        self.height = height

    def draw(self, win):
        pygame.draw.rect(win, self.COLOR, (self.x, self.y, self.width, self.height))

    def move(self, up=True):
        if up:
            self.y -= self.VEL  # move 2 down
        else:
            self.y += self.VEL  # move 2 up

    def reset(self):
        self.x = self.original_x  # reset x values to original
        self.y = self.original_y  # reset y values to original


class Ball:
    MAX_VEL = 5
    COLOR = WHITE

    def __init__(self, x, y, radius):
        self.x = self.original_x = x  # Initialize ball's x-coordinate and original x-coordinate
        self.y = self.original_y = y  # Initialize ball's y-coordinate and original y-coordinate
        self.radius = radius
        self.x_vel = self.MAX_VEL
        self.y_vel = 0

    def draw(self, win):
        pygame.draw.circle(win, self.COLOR, (self.x, self.y), self.radius)

    def move(self):
        self.x += self.x_vel
        self.y += self.y_vel

    def reset(self):
        self.x = self.original_x
        self.y = self.original_y
        self.y_vel = 0
        self.x_vel *= -1


def draw(win, paddles, ball, left_score, right_score):
    win.fill(BLACK)

    SCORE_FONT = pygame.font.SysFont("comicsans", 50)
    left_score_text = SCORE_FONT.render(f"{left_score}", 1, WHITE)
    right_score_text = SCORE_FONT.render(f"{right_score}", 1, WHITE)
    win.blit(left_score_text, (WIDTH // 4 - left_score_text.get_width() // 2, 20))
    win.blit(right_score_text, (WIDTH * (3 / 4) -
                                right_score_text.get_width() // 2, 20))

    for paddle in paddles:
        paddle.draw(win)

    for i in range(10, HEIGHT, HEIGHT // 20):
        if i % 2 == 1:
            continue
        pygame.draw.rect(win, WHITE, (WIDTH // 2 - 5, i, 10, HEIGHT // 20))

    ball.draw(win)
    pygame.display.update()


# Function to handle ball collisions with paddles
def handle_collision(ball, left_paddle, right_paddle):
    # Handle collisions with top and bottom walls
    if ball.y + ball.radius >= HEIGHT:   # Check if ball hits the bottom wall
        ball.y_vel *= -1  # Reverse the vertical velocity to bounce the ball
    elif ball.y - ball.radius <= 0:  # Check if ball hits the top wall
        ball.y_vel *= -1  # Reverse the vertical velocity to bounce the ball

    # Handle collisions with paddles
    if ball.x_vel < 0:   # If the ball is moving left (towards the left paddle)
        if ball.y >= left_paddle.y and ball.y <= left_paddle.y + left_paddle.height:
            # Check if the ball is within the vertical range of the left paddle
            if ball.x - ball.radius <= left_paddle.x + left_paddle.width:
                # Check if the ball hits the left paddle
                ball.x_vel *= -1  # Reverse the horizontal velocity to bounce the ball

                middle_y = left_paddle.y + left_paddle.height / 2  # Calculate the middle of the left paddle
                # Calculate the vertical distance between the ball and the middle of the paddle
                difference_in_y = middle_y - ball.y
                # Calculate a reduction factor based on the paddle's height and the ball's maximum velocity
                reduction_factor = (left_paddle.height / 2) / ball.MAX_VEL
                # Calculate the new vertical velocity for the ball based on the reduction factor
                y_vel = difference_in_y / reduction_factor
                ball.y_vel = -1 * y_vel  # Set the ball's vertical velocity

    else:  # If the ball is moving right (towards the right paddle)
        # Check if the ball is within the vertical range of the right paddle
        if ball.y >= right_paddle.y and ball.y <= right_paddle.y + right_paddle.height:
            # Check if the ball hits the right paddle
            if ball.x + ball.radius >= right_paddle.x:
                ball.x_vel *= -1  # Reverse the horizontal velocity to bounce the ball

                middle_y = right_paddle.y + right_paddle.height / 2  # Calculate the middle of the right paddle
                # Calculate the vertical distance between the ball and the middle of the paddle
                difference_in_y = middle_y - ball.y
                # Calculate a reduction factor based on the paddle's height and the ball's maximum velocity
                reduction_factor = (right_paddle.height / 2) / ball.MAX_VEL
                # Calculate the new vertical velocity for the ball based on the reduction factor
                y_vel = difference_in_y / reduction_factor
                ball.y_vel = -1 * y_vel  # Set the ball's vertical velocity


# Function to handle movement of player 1's paddle
def handle_paddle1_movement(keys, left_paddle, server_socket):
    # Move the left paddle up if 'W' key is pressed
    if keys[pygame.K_w] and left_paddle.y - left_paddle.VEL >= 0:
        left_paddle.move(up=True)
        server_socket.send("mv1u".encode())
    # Move the left paddle down if 'S' key is pressed
    if keys[pygame.K_s] and left_paddle.y + left_paddle.VEL + left_paddle.height <= HEIGHT:
        left_paddle.move(up=False)
        server_socket.send("mv1d".encode())


# Function to handle movement of player 2's paddle
def handle_paddle2_movement(keys, right_paddle, server_socket):
    # Move the right paddle up if 'UP' arrow key is pressed and within bounds
    if keys[pygame.K_UP] and right_paddle.y - right_paddle.VEL >= 0:
        right_paddle.move(up=True)
        server_socket.send("mv2u".encode())
    # Move the right paddle down if 'DOWN' arrow key is pressed and within bounds
    if keys[pygame.K_DOWN] and right_paddle.y + right_paddle.VEL + right_paddle.height <= HEIGHT:
        right_paddle.move(up=False)
        server_socket.send("mv2d".encode())


def receive_opponent_paddle_position(server_socket, opponent_paddle):
    game_over = False
    while not game_over:
        res = server_socket.recv(4).decode()
        if res != "":
            if res == "movu":
                opponent_paddle.move(up=True)
            if res == "movd":
                opponent_paddle.move(up=False)
            if res == "endg":
                game_over = True


os.environ['SDL_VIDEO_WINDOW_POS'] = '400,0'  # Set window position


def pong_game(player_number, server_socket):
    global win_text
    pygame.init()
    WIN = pygame.display.set_mode((WIDTH, HEIGHT))
    SCORE_FONT = pygame.font.SysFont("comicsans", 50)
    run = True
    pygame.display.set_caption("Pong2")
    clock = pygame.time.Clock()  # Create a clock to control the game's frame rate

    # paddle/ball(x,y,width, height)
    left_paddle = Paddle(10, HEIGHT // 2 - PADDLE_HEIGHT //
                         2, PADDLE_WIDTH, PADDLE_HEIGHT)
    right_paddle = Paddle(WIDTH - 10 - PADDLE_WIDTH, HEIGHT //
                          2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
    ball = Ball(WIDTH // 2, HEIGHT // 2, BALL_RADIUS)

    left_score = 0
    right_score = 0
    # creating a thread that receives the opponent paddle position
    if player_number == 1:
        threading.Thread(target=receive_opponent_paddle_position, args=(server_socket, right_paddle)).start()
    elif player_number == 2:
        threading.Thread(target=receive_opponent_paddle_position, args=(server_socket, left_paddle)).start()

    # Main game loop
    while run:
        clock.tick(FPS)
        draw(WIN, [left_paddle, right_paddle], ball, left_score, right_score)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                server_socket.send("endg".encode())
                break
            elif event.type == pygame.VIDEORESIZE:
                # Ignore resize events
                pass
            elif event.type == pygame.VIDEOEXPOSE:
                # Ignore expose events
                pass

        keys = pygame.key.get_pressed()
        # Handle paddle movement based on player number
        if player_number == 1:
            handle_paddle1_movement(keys, left_paddle, server_socket)
        if player_number == 2:
            handle_paddle2_movement(keys, right_paddle, server_socket)

        ball.move()
        handle_collision(ball, left_paddle, right_paddle)

        if ball.x < 0:
            right_score += 1
            ball.reset()
        elif ball.x > WIDTH:
            left_score += 1
            ball.reset()

        # Check for scoring conditions
        won = False
        if left_score >= WINNING_SCORE:
            won = True
            win_text = "Left Player Won!"
        elif right_score >= WINNING_SCORE:
            won = True
            win_text = "Right Player Won!"

        # Check for winning conditions
        if won:
            text = SCORE_FONT.render(win_text, 1, WHITE)
            WIN.blit(text, (WIDTH // 2 - text.get_width() //
                            2, HEIGHT // 2 - text.get_height() // 2))
            pygame.display.update()
            pygame.time.delay(5000)
            server_socket.send("endg".encode())
            run = False
            pygame.quit()

    pygame.quit()


if __name__ == "__main__":
    client = GameRequestAppClient()
    client.run()

