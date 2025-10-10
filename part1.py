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
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    addrinfo = socket.getaddrinfo(host, port, socket.AF_INET)
    for addr in addrinfo:
        try:
            s.connect(addr[4])
            break
        except socket.error as e:
            print(f"Error: {e}")
    
    payload = bytes("hello world\0", "utf-8")
    header = get_header(len(payload), 0, 1)
    to_send = header + payload
    s.send(to_send)
    if DEBUG:
        print(f"Sent {len(to_send)} bytes. Payload: {len(payload)}B, Header: {len(header)}B")

    data = s.recv(28)
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

    s.connect((host, udp_port))
    s.settimeout(0.5)
    
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
                s.send(to_send)
                if DEBUG:
                    print(f"Sent packet {i}. Payload: {len(payload)}B, Header: {len(header)}B, Total: {len(to_send)}B")
                data = s.recv(16)
                if DEBUG:
                    print(f"Recieved {len(data)} bytes")
                data = data[12:]
                break
            except socket.timeout as e:
                if DEBUG:
                    print(f"Timed out on packet {i}: {e}")
                continue
    
    s.settimeout(None)
    data = s.recv(20)
    data = data[12:]
    unpacked = struct.unpack("!II", data)
    tcp_port, secretB = unpacked

    print(f"Part B complete. SecretB: {secretB}")
    print()

    end_time = time.perf_counter()
    print(f"Time elapsed: {end_time - start_time:.4f}")
    
def get_header(payload_len, secret, step):
    return struct.pack('!IIHH', int(payload_len), int(secret), int(step), 758)

if __name__ == "__main__":
    main(sys.argv[0:], DEBUG)
