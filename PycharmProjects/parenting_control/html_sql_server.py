import socket
import SQL_ORM
import json
from github import Github
from github import Auth

import queue, threading, time, random
from tcp_by_size import send_with_size, recv_by_size

DEBUG = True
exit_all = False

parents_list = []
children_list = []


def handel_client(sock, tid, db):
    global exit_all

    print("New Client num " + str(tid))

    while not exit_all:
        try:
            data = recv_by_size(sock)
            if data == "":
                print("Error: Seens Client DC")
                break

            data = data.decode()
            if data[0:4] == "PAREN":
                to_send = parent_action(data[5:], db)  # send to the parent part
                send_with_size(sock, to_send.encode())
            elif data[0:4] == "CHILD":
                to_send = child_action(data.decode(), db)  # send to the parent part
                send_with_size(sock, to_send.encode())

        except socket.error as err:
            if err.errno == 10054:
                # 'Connection reset by peer'
                print("Error %d Client is Gone. %s reset by peer." % (err.errno, str(sock)))
                break
            else:
                print("%d General Sock Error Client %s disconnected" % (err.errno, str(sock)))
                break

        except Exception as err:
            print("General Error:" + str(err))
            break
    sock.close()


# Function to perform actions based on client requests
def parent_action(data, db):
    """
    check what client ask and fill to send with the answer
    """
    to_send = "Not Set Yet"
    action = data[:6]
    data = data[7:]
    fields = data.split('|')
    instance = SQL_ORM.CustomerOrderORM()

    if DEBUG:
        print("Got client request " + action + " -- " + str(fields))

    if action == "TMANGE":
        usr = SQL_ORM.CustomerOrderORM.update_customer(instance, fields[0], fields[1], fields[2],
                               fields[3], fields[4], fields[5])
        if usr:
            to_send = "TMANGER|" + "Success"
        else:
            to_send = "TMANGER|" + "Error"

    elif action == "ABREAK":

        section_time, break_time = fields[0], fields[1]

        to_send = "ABREAK|" + "A break was set"

    elif action == "DLTUSR":
        customer = SQL_ORM.CustomerOrderORM.delete_customer(instance, fields[0])
        to_send = "DLTUSR|" + customer

    elif action == "CUSLST":
        customers_list = SQL_ORM.CustomerOrderORM.get_customers(instance)
        to_send = "CUSLST|" + str(customers_list)

    elif action == "ORDERP":
        customer_id, product_name = fields[0], fields[1]
        order = SQL_ORM.CustomerOrderORM.order_product(instance, customer_id, product_name)
        to_send = "ORDERP|" + order

    elif action == "CNLORD":
        order_id = fields[0]
        order_cancel = SQL_ORM.CustomerOrderORM.cancel_order(instance, order_id)
        to_send = "CNLORD|" + order_cancel

    elif action == "WHOORD":
        customers_who_ordered_names = SQL_ORM.CustomerOrderORM.get_customers_who_ordered(instance)
        to_send = "WHOORDR|" + str(customers_who_ordered_names)
    elif action == "PROORD":
        names_of_products_that_have_been_ordered = SQL_ORM.CustomerOrderORM.get_products_that_have_been_ordered(instance)
        to_send = "PROORD|" + str(names_of_products_that_have_been_ordered)

    elif action == "UPDORD":
        order_id, new_product_name = fields[0], fields[1]
        update_order = SQL_ORM.CustomerOrderORM.update_order(instance, order_id, new_product_name)
        to_send = "UPDORD|" + update_order

    elif action == "RULIVE":
        to_send = "RULIVER|" + "yes i am a live server"
    elif action == "LOGINN":
        user_name, user_password, user_id = fields[0], fields[1], fields[2]
        login = SQL_ORM.CustomerOrderORM.login(instance, user_name, user_password, user_id)
        to_send = "LOGGINN|" + login

    else:
        print("Got unknown action from client " + action)
        to_send = "ERR___R|001|" + "unknown action"

    return to_send


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
    db = SQL_ORM.CustomerOrderORM()

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
        cli_s, addr = s.accept()
        t = threading.Thread(target=handel_client, args=(cli_s, i, db))
        t.start()
        i += 1
        threads.append(t)

    exit_all = True
    for t in threads:
        t.join()
    manager.join()

    s.close()


if __name__ == "__main__":
    g = Github('xyAAAXcXACZYBx2YybC1zAzCxAYxc1Cxyz2AByb2')
    main()
