import socket


def getHost(ip):
    """
    This method returns the 'True Host' name for a
    given IP address
    """
    try:
        data = socket.gethostbyaddr(ip)
        host = repr(data[0])
        return host
    except Exception:
        # fail gracefully
        return False


url = "www.zeev.herzliya.org.il"
def get_ip(url):
    ip_add = socket.gethostbyname(url)
    print(ip_add)
    file = open("websites.txt", 'a')
    file.write((str(url) + "," + str(getHost(ip_add))) + " \n")
    file.close()



get_ip(url)