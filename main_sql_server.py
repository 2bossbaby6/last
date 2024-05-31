import socket
import SQL_ORM
import json
import queue, threading, time, random
from tcp_by_size import send_with_size, recv_by_size
from socket import socket as socki
import re

DEBUG = True
exit_all = False

parents_list = {}
children_list = {}


def handel_client(client_socket, tid, db):
    global exit_all

    print("New Client num " + str(tid))

    while not exit_all:
        try:
            data = recv_by_size(client_socket)
            if data == "":
                print("Error: Seens Client DC")
                break

            data = data.decode()
            if data[0:5] == "PAREN":
                to_send = parent_action(data[5:], db, client_socket)  # send to the parent part
                send_with_size(client_socket, to_send.encode())

            elif data[0:5] == "CHILD":
                to_send = child_action(data[5:], db, client_socket)  # send to the child part
                send_with_size(client_socket, to_send.encode())

        except socket.error as err:
            if err.errno == 10054:
                # 'Connection reset by peer'
                print("Error %d Client is Gone. %s reset by peer." % (err.errno, str(client_socket)))
                break
            else:
                print("%d General Sock Error Client %s disconnected" % (err.errno, str(client_socket)))
                break

        except Exception as err:
            print("General Error:" + str(err))
            break
    client_socket.close()


def child_action(data, db, client_socket):
    """
       check what client ask and fill to send with the answer
    """
    to_send = "Not Set Yet"
    action = data[:6]
    data = data[7:]
    fields = data.split('|')
    instance = SQL_ORM.CustomerChildORM()

    if DEBUG:
        print("Got client request " + action + " -- " + str(fields))

    if action == "UPDUSR":
        usr = SQL_ORM.CustomerChildORM.update_customer(instance, fields[0], fields[1], fields[2],
                                                       fields[3], fields[4], fields[5])
        if usr:
            to_send = "UPDUSRR|" + "Success"
        else:
            to_send = "UPDUSRR|" + "Error"

    elif action == "INSKID":  # Insert new child to db
        customer = SQL_ORM.CustomerChildORM.insert_new_child(instance, fields[0], fields[1], fields[2], fields[3])
        to_send = "INSKID|your id is: " + customer

    elif action == "LOGINN":
        child_name, child_id = fields[0], fields[1]
        children_list[child_id] = client_socket
        login = SQL_ORM.CustomerChildORM.child_login(instance, child_name, child_id)
        to_send = "LOGGINN|" + login

    else:
        print("Got unknown action from client " + action)
        to_send = "ERR___R|001|" + "unknown action"

    return to_send



# Function to perform actions based on client requests
def parent_action(data, db, client_socket):
    """
    check what client ask and fill to send with the answer
    """
    to_send = "Not Set Yet"
    action = data[:6]
    child_id = ""
    if action == "LOGINN" or action == "INSPAR" or action == "GETKID" or action == "INSKID":
        data = data[7:]
    else:
        child_id = data[6]
        data = data[8:]
    fields = data.split('|')
    instance = SQL_ORM.CustomerChildORM()

    if DEBUG:
        print("Got client request " + action + " -- " + str(fields))

    if action == "UPDUSR":
        usr = SQL_ORM.CustomerChildORM.update_customer(instance, fields[0], fields[1], fields[2],
                                                       fields[3], fields[4], fields[5])
        if usr:
            to_send = "UPDUSRR|" + "Success"
        else:
            to_send = "UPDUSRR|" + "Error"

    elif action == "INSPAR":  # Insert new parent to data base
        customer = SQL_ORM.CustomerChildORM.insert_new_customer(instance, fields[0], fields[1], fields[2],
                                                                fields[3], fields[4])
        to_send = "INSPAR|your id is: " + customer

    elif action == "INSKID":  # Insert new child to db
        customer = SQL_ORM.CustomerChildORM.insert_new_child(instance, fields[0], fields[1], fields[2], fields[3])
        to_send = "INSKID|your id is: " + customer

    elif action == "ABREAK":  # create a break for the child

        section_time, break_time = fields[0], fields[1]

        to_send = "ABREAK|" + "A break was set"
        send_to_kid = "ABREAK|" + str(section_time) + "|" + str(break_time)
        send_with_size(children_list[child_id], send_to_kid)

    elif action == "MESSAG":  # get message
        message = fields[0]
        to_send = "MESSAG|" + str(message)
        send_with_size(children_list[child_id], to_send)

    elif action == "TMNAGE":  # screen time
        to_send = "TMNAGE"
        child_socket = children_list[child_id]
        send_with_size(child_socket, to_send)
        screentime_data = recv_by_size(child_socket)


    elif action == "BLOCKW":  # block website
        url = fields[0]
        to_send = str(url)
        if is_legal_url(url):
            sock = socki()
            sock.connect(("127.0.0.1", 5000))
            send_with_size(sock, to_send)
            sock.close()
            to_send = "BLOCKW|" + "website is now on the blocking list"
        else:
            to_send = "BLOCKW|" + "website's url was incorrect, try again"

    elif action == "GETKID":
        parent_id = fields[0]
        names_of_children = SQL_ORM.CustomerChildORM.get_children(instance, parent_id)
        to_send = str(names_of_children)

    elif action == "RULIVE":
        to_send = "RULIVER|" + "yes i am a live server"
    elif action == "LOGINN":
        user_name, user_password, user_id = fields[0], fields[1], fields[2]
        parents_list[user_id] = client_socket
        login = SQL_ORM.CustomerChildORM.parent_login(instance, user_name, user_password, user_id)
        to_send = "LOGGINN|" + login

    else:
        print("Got unknown action from client " + action)
        to_send = "ERR___R|001|" + "unknown action"

    return to_send


def is_legal_url(url):
    # Regular expression pattern for basic URL format
    url_pattern = re.compile(r'^(http|https)://[a-zA-Z0-9\-\\.]+\.[a-zA-Z]{2,}(\S*)?$')

    # Check if the URL matches the pattern
    if re.match(url_pattern, url):
        return True
    else:
        return False


# Function to manage the queue
def q_manager(q, tid):
    global exit_all

    print("manager start:" + str(tid))
    while not exit_all:
        item = q.get()
        print("manager got somthing:" + str(item))
        # do some work with it(item)
        q.task_done()
        time.sleep(0.3)
    print("Manager say Bye")


def main():
    global exit_all

    exit_all = False
    db = SQL_ORM.CustomerChildORM()

    s = socket.socket()

    q = queue.Queue()

    q.put("Hi for start")

    manager = threading.Thread(target=q_manager, args=(q, 0))

    s.bind(("0.0.0.0", 33445))

    s.listen(4)
    print("after listen")

    threads = []
    i = 1
    while True:
        client_socket, addr = s.accept()
        t = threading.Thread(target=handel_client, args=(client_socket, i, db))
        t.start()
        i += 1
        threads.append(t)

    exit_all = True
    for t in threads:
        t.join()
    manager.join()

    s.close()


if __name__ == "__main__":
    main()
