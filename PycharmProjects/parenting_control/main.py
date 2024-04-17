import scapy.all
from collections import Counter
from scapy.all import sniff, IP, Ether
import socket
import threading

ip_list = set()  # Use a set for faster membership checks


def get_all_ip():
    with open("websites.txt", "r") as file:
        for line in file:
            url = line.split(",")[0]
            try:
                ip_add = socket.gethostbyname(url)
                ip_list.add(str(ip_add))
            except socket.gaierror as e:
                print(f"Error resolving IP for {url}: {e}")

get_all_ip()  # Preload IP addresses

def process_packet(packet):
    try:
        key = tuple(sorted([packet[IP].src, packet[IP].dst]))
        packet_counts.update([key])
        #print(packet.summary())

        ip_address = packet[IP].dst

        if ip_address not in ip_list:
            packet[Ether].dst = "00:0c:29:3e:be:f0"
            scapy.all.sendp(packet)
    except Exception as e:
        print(f"Error processing packet: {e}")

def custom_action(packet_batch):
    # Process the entire batch of packets using threads
    threads = []
    for packet in packet_batch:
        thread = threading.Thread(target=process_packet, args=(packet,))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

## Create a Packet Counter
packet_counts = Counter()

## Setup sniff, filtering for IP traffic
sniff(filter="ip and src 172.16.13.229", prn=custom_action, count=1000000)

## Print out packet count per A <--> Z address pair
#print("\n".join(f"{f'{key[0]} <--> {key[1]}'}: {count}" for key, count in packet_counts.items()))