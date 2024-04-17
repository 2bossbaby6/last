import scapy.all
from collections import Counter
from scapy.all import sniff
from scapy.all import DNS, DNSQR, IP, sr1, UDP
import socket
import dns.resolver, dns.reversename


ip_list = []  # an ip list of all the ip adresses of websites I want to block
queue = []

def get_all_ip():  # at the start of the run this will get al the ip adresses of the sites we want to block
    file = open("websites.txt", "r")
    for line in file:
        url = line.split(",")[0]
        ip_add = socket.gethostbyname(url)
        ip_list.append(str(ip_add))

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


def get_ip(url):
    ip_add = socket.gethostbyname(url)
    print(ip_add)
    file = open("websites.txt", 'w')
    file.write(str(url) + " , " + str(getHost(ip_add)) + "\n")
    file.close()


def get_domain_name(ip_address):
    try:
        hostname = socket.gethostbyaddr(ip_address)[0]
        return hostname
    except socket.herror:
        return "No domain name found"


## Create a Packet Counter
packet_counts = Counter()


## Define our Custom Action function
def custom_action(packet, q):
    get_all_ip()
    for p in packet:
        # Create tuple of Src/Dst in sorted order
        key = tuple(sorted([packet[0][1].src, packet[0][1].dst]))
        packet_counts.update([key])


        #name = scapy.all.sr1(IP(dst="8.8.8.8") / UDP() / DNS(rd=1, qd=DNSQR(qname="211.196.59.69.in-addr.arpa", qtype='PTR')))
        #print(str(name))
        ip_address = (packet[0][1].dst)
        #domain_name = get_domain_name(ip_address)
        #addrs = dns.reversename.from_address(str(ip_address))
        #print(str(dns.resolver.resolve(addrs, "PTR")[0]))
        #print(f"The domain name for {ip_address} is {addrs}")

        #domain_name = socket.gethostbyaddr(ip_address)[0]

        #print(getHost(ip_address))

        packet.dst = "00:0c:29:3e:be:f0"

        if ip_address not in ip_list:  # getHost(ip_address) == '022.co.il':
            scapy.all.sendp(packet, verbose=0)
            q.put(ip_address)
            return(packet)
            #return f"Packet #{sum(packet_counts.values())}: {packet[0][1].src} ==> {packet[0][1].dst}"


def main(q):
    ## Setup sniff, filtering for IP traffic
    sniff(filter="ip and src 172.16.13.122", lfilter=lambda packet: custom_action(packet, q))
    print("niff")
    ## Print out packet count per A <--> Z address pair
     #print("\n".join(f"{f'{key[0]} <--> {key[1]}'}: {count}" for key, count in packet_counts.items()))



