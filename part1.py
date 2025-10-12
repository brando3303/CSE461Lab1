# Lab 1 Part 1
import socket
import sys
import struct
import time

DEBUG = False

def main(args, DEBUG=False):
    start_time = time.perf_counter()

    if len(args) != 3:
        return
    
    host = args[1]
    port = args[2]

    # Part a
    print(f"Part A beginning...")
    print(f"Connecting to: {host}:{port}")
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    addrinfo = socket.getaddrinfo(host, port, socket.AF_INET)
    for addr in addrinfo:
        try:
            udp_sock.connect(addr[4])
            break
        except socket.error as e:
            print(f"Error: {e}")
    
    print(f"Connected")
    
    payload = bytes("hello world\0", "utf-8")
    header = get_header(len(payload), 0, 1)
    to_send = header + payload
    udp_sock.send(to_send)
    if DEBUG:
        print(f"Sent {len(to_send)} bytes. Payload: {len(payload)}B, Header: {len(header)}B")

    data = udp_sock.recv(28)
    if DEBUG:
        print(f"Recieved {len(data)} bytes")
    unpacked = struct.unpack("!4I", data[12:])
    num_packets, length, udp_port, secretA = unpacked
    if DEBUG:
        print(unpacked)
    
    print(f"Part A complete. SecretA: {secretA}")
    print()

    # Part b
    print(f"Part B beginning...")
    print(f"Connecting to {host}:{udp_port}")

    udp_sock.connect((host, udp_port))
    udp_sock.settimeout(0.5)

    print(f"Connected")
    
    total_bytes = length + ((-1 * length) % 4)
    for i in range(num_packets):
        payload = struct.pack("!I", i)
        for _ in range(total_bytes):
            payload += b"\0"
        header = get_header(length + 4, secretA, 1)
        to_send = header + payload

        # Send until we get ack from server
        while True:
            try:
                udp_sock.send(to_send)
                if DEBUG:
                    print(f"Sent packet {i}. Payload: {len(payload)}B, Header: {len(header)}B, Total: {len(to_send)}B")
                data = udp_sock.recv(16)
                if DEBUG:
                    print(f"Recieved {len(data)} bytes")
                data = data[12:]
                break
            except socket.timeout as e:
                if DEBUG:
                    print(f"Timed out on packet {i}: {e}")
                continue
    
    udp_sock.settimeout(None)
    data = udp_sock.recv(20)
    data = data[12:]
    unpacked = struct.unpack("!II", data)
    tcp_port, secretB = unpacked

    print(f"Part B complete. SecretB: {secretB}")
    print()

    # Part c
    print(f"Part C beginning...")
    print(f"Connecting to {host}:{tcp_port}")

    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_sock.connect((host, tcp_port))

    print(f"Connected")

    data = tcp_sock.recv(12 + 16)
    unpacked = struct.unpack("!IIIcccc", data[12:])
    num2, len2, secretC, c = unpacked[:4]
    if DEBUG:
        print(f"Received: {unpacked}")

    print(f"Part C complete. SecretC: {secretC}")
    print()

    # Part d
    print(f"Part D beginning...")

    # Word aligned length, does not contribute to length in header
    payload = b''
    for _ in range(len2):
        payload += c
    for _ in range ((-1 * len2) % 4):
        payload += b"\0"
    header = get_header(len2, secretC, 1)
    to_send = header + payload

    for i in range(num2):
        tcp_sock.send(to_send)
        if DEBUG:
            print(f"Sent packet {i}. Payload: {len(payload)}B, Header: {len(header)}B, Total: {len(to_send)}B")
    
    data = tcp_sock.recv(12 + 4)
    unpacked = struct.unpack("!I", data[12:])
    secretD = unpacked[0]
    if DEBUG:
        print(f"Received: {unpacked}")

    print(f"Part D complete. SecretD: {secretD}")
    print()

    end_time = time.perf_counter()
    print("Part 1 Completed")
    print("Summary:")
    print(f"  SecretA: {secretA}")
    print(f"  SecretB: {secretB}")
    print(f"  SecretC: {secretC}")
    print(f"  SecretD: {secretD}")
    print()

    print(f"Time elapsed: {end_time - start_time:.4f}s")
    
def get_header(payload_len, secret, step):
    return struct.pack('!IIHH', int(payload_len), int(secret), int(step), 758)

if __name__ == "__main__":
    main(sys.argv[0:], DEBUG)
