import multiprocessing
import arp
import spoofing

def print_cube(num):
    """
    function to print cube of given num
    """
    for i in range(1000):
        print("Cube: {}".format(num * num * num))


def print_square(num):
    """
    function to print square of given num
    """
    for i in range(1000):
        print("Square: {}".format(num * num))

def arp1():
    arp.main()

def spoof1():
    spoofing.main()

if __name__ == "__main__":
    # creating processes
    p1 = multiprocessing.Process(target=arp1, args=())
    p2 = multiprocessing.Process(target=spoof1, args=())

    # starting process 1
    p1.start()
    # starting process 2
    p2.start()

    for i in range(10):
        print("n")
    # wait until process 1 is finished
    p1.join()
    # wait until process 2 is finished
    p2.join()

    # both processes finished
    print("Done!")