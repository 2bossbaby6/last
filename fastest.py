import concurrent.futures
from scapy.all import sniff, IP, Ether, sendp
from collections import Counter
import socket

ip_list = set()  # Use a set for faster membership checks
packet_counts = Counter()

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

        ip_address = packet[IP].dst

        if ip_address not in ip_list:
            packet[Ether].dst = "00:0c:29:3e:be:f0"
            return packet
    except Exception as e:
        print(f"Error processing packet: {e}")

# Adjust the batch size based on experimentation
BATCH_SIZE = 100

def custom_action(packet_batch):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(process_packet, packet_batch))

    # Send packets in batches
    for packet in results:
        if packet is not None:
            sendp(packet)

# Setup sniff, filtering for IP traffic
sniff(filter="ip and src 172.16.13.229", prn=custom_action, count=1000000)

# Print out packet count per A <--> Z address pair
#print("\n".join(f"{f'{key[0]} <--> {key[1]}'}: {count}" for key, count in packet_counts.items()))