from scapy.all import sniff, Ether, IP, IPv6, TCP, UDP, ICMP
from src.network.traffic_analyzer import analyse_packet

SHOW_PAYLOADS = False

def format_payload(raw_data, length=16):
    result = []
    for i in range(0, len(raw_data), length):
        chunk = raw_data[i:i + length]
        hex_chunk = ' '.join(f"{b:02x}" for b in chunk)
        ascii_chunk = ''.join((chr(b) if 32 <= b <= 126 else '.') for b in chunk)
        result.append(f"{i:04x}  {hex_chunk:<{length*3}}  {ascii_chunk}")
    return "\n".join(result)

def packet_callback(packet):

    # Forward packet to analyzer
    analyse_packet(packet)

    if Ether in packet:
        eth = packet[Ether]
        print("\n=== Ethernet Frame ===")
        print(f"Destination: {eth.dst}, Source: {eth.src}, Protocol: {eth.type}")

        # IPv4
        if IP in packet:
            ip = packet[IP]
            print("\n--- IPv4 Packet ---")
            print(f"Version: {ip.version}, Header Length: {ip.ihl * 4} bytes, TTL: {ip.ttl}")
            print(f"Protocol: {ip.proto}, Source: {ip.src}, Target: {ip.dst}")

            if TCP in packet:
                tcp = packet[TCP]
                print("\n>>> TCP Segment <<<")
                print(f"Source Port: {tcp.sport}, Destination Port: {tcp.dport}")
                print(f"Sequence: {tcp.seq}, Acknowledgment: {tcp.ack}, Flags: {tcp.flags}")
                if SHOW_PAYLOADS and tcp.payload:
                    print("\nPayload:")
                    print(format_payload(bytes(tcp.payload)))

            elif UDP in packet:
                udp = packet[UDP]
                print("\n>>> UDP Segment <<<")
                print(f"Src Port: {udp.sport}, Dst Port: {udp.dport}, Length: {udp.len}")
                if SHOW_PAYLOADS and udp.payload:
                    print("\nPayload:")
                    print(format_payload(bytes(udp.payload)))

            elif ICMP in packet:
                icmp = packet[ICMP]
                print("\n>>> ICMP Packet <<<")
                print(f"Type: {icmp.type}, Code: {icmp.code}, Checksum: {icmp.chksum}")

        # IPv6
        elif IPv6 in packet:
            ipv6 = packet[IPv6]
            print("\n--- IPv6 Packet ---")
            print(f"Source: {ipv6.src}, Destination: {ipv6.dst}, Next Header: {ipv6.nh}, Hop Limit: {ipv6.hlim}")

        else:
            print("\n(No IP layer found)")

def main():
    try:
        sniff(filter="tcp or udp or icmp", prn=packet_callback, store=False)
    except KeyboardInterrupt:
        print("\n[!] Stopping packet sniffer.")

if __name__ == "__main__":
    main()