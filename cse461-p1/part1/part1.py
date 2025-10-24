# Lab 1 Part 1
# Group Members:
# Brandon Bailey (@bbailey9)
# Solden Stoll (@solden)

import socket
import sys
import struct
import time

# Constants
DEBUG = False

MAX_TIMEOUTS = 10

def get_header(payload_len, secret, step):
    """Packs the header into network order.

    Params:
        - payload_len: length of payload being sent
        - secret: secret to include in header
        - step: step number

    Returns:
        - header formatted in network order consisting of 4 bytes for
          payload length, 4 bytes for the secret, and 2 bytes each for the step
          and last 4 digits of Solden's student number.
    """
    return struct.pack('!IIHH', int(payload_len), int(secret), int(step), 758)

def partA(host, port):
    """Carry out the logic of part A by connecting to host on port and sending hello world.

    Params:
        - host: host to connect to
        - port: udp port to connect to

    Returns:
        - udp_port: udp port to connect to
        - udp_sock: udp socket to connect with
        - num_packets: number of packets to send
        - length: length of payload to send
        - secretA: secret from part a
    """
    print(f"Part A beginning...")
    print(f"Connecting to: {host}:{port}")
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.settimeout(3)

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

    try:
        data = udp_sock.recv(28)
    except socket.timeout as e:
        print(f"Server did not respond: {e}")
        sys.exit(1)

    if DEBUG:
        print(f"Recieved {len(data)} bytes")
    unpacked = struct.unpack("!4I", data[12:])
    num_packets, length, udp_port, secretA = unpacked
    if DEBUG:
        print(unpacked)

    print(f"Part A complete. SecretA: {secretA}")
    print()

    return udp_port, udp_sock, num_packets, length, secretA

def partB(host, udp_port, udp_sock, num_packets, length, secretA):
    """Carry out the logic of part B by sending num_packets of zeroed payloads.

    Params:
        - host: host to connect to
        - udp_port: udp port to connect to
        - udp_sock: udp socket to connect with
        - num_packets: number of packets to send
        - length: length of payload to send
        - secretA: secret from part a

    Returns:
        - tcp_port: port to connect to in part c
        - secretB: secret from part b
    """
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
        timeout_count = 0
        while True:
            # If we timeout too many times, exit
            if timeout_count > MAX_TIMEOUTS:
                sys.exit(1)
                udp_sock.close()
            
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
                timeout_count += 1
                if DEBUG:
                    print(f"Timed out on packet {i} after {timeout_count} attempts: {e}")
                continue

    udp_sock.settimeout(None)
    data = udp_sock.recv(20)
    data = data[12:]
    unpacked = struct.unpack("!II", data)
    tcp_port, secretB = unpacked

    print("Closing connection")
    udp_sock.close()

    print(f"Part B complete. SecretB: {secretB}")
    print()

    return tcp_port, secretB

def partC(host, tcp_port):
    """Carry out the logic for part C by connecting to host on tcp_port and receiving information.

    Params:
        - host: host to connect to
        - tcp_port: port to connect to

    Returns:
        - num2: number of packets to send for part d
        - len2: length of payload to send for part d
        - tcp_sock: socket to send data over for part d
        - c: character that is sent num2 times in payload for part d
        - secretC: secret from part c
    """
    print(f"Part C beginning...")
    print(f"Connecting to {host}:{tcp_port}")

    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Try to connect:
    try:
        tcp_sock.connect((host, tcp_port))
    except socket.error as e:
        print(f"Could not connect to {host}:{tcp_port}: {e}")
        tcp_sock.close()
        sys.exit(1)

    print(f"Connected")

    # Try to recieve
    try:
        data = tcp_sock.recv(12 + 16)
    except socket.error as e:
        print(f"Error recieving from port: {e}")
        tcp_sock.close()
        sys.exit(1)

    unpacked = struct.unpack("!IIIcccc", data[12:])
    num2, len2, secretC, c = unpacked[:4]
    if DEBUG:
        print(f"Received: {unpacked}")

    print(f"Part C complete. SecretC: {secretC}")
    print()

    return tcp_sock, num2, len2, secretC, c

def partD(num2, len2, tcp_sock, c, secretC):
    """Carry out the logic for part D by sending num2 packets of len2 consisting of character c.

    Params:
        - num2: number of packets to send
        - len2: length of payload to send
        - tcp_sock: socket to send data over
        - c: character that is sent num2 times in payload
        - secretC: secret from part c

    Returns:
        - secretD: secret from part d
    """
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

    # Try to recieve
    try:
        data = tcp_sock.recv(12 + 4)
    except socket.error as e:
        print(f"Error recieving from port: {e}")
        tcp_sock.close()
        sys.exit(1)

    unpacked = struct.unpack("!I", data[12:])
    secretD = unpacked[0]
    if DEBUG:
        print(f"Received: {unpacked}")

    print("Closing socket")
    tcp_sock.close()

    print(f"Part D complete. SecretD: {secretD}")
    print()

    return secretD

def main(args):
    """Carry out each part sequentially and print a summary of total time and secrets.

    Params:
        - args: command-line args
        - DEBUG: enable debug prints
    """
    start_time = time.perf_counter()

    if len(args) != 3:
        return

    host = args[1]
    port = args[2]

    # Part a
    udp_port, udp_sock, num_packets, length, secretA = partA(host, port)

    # Part b
    tcp_port, secretB = partB(host, udp_port, udp_sock, num_packets, length, secretA)

    # Part c
    tcp_sock, num2, len2, secretC, c = partC(host, tcp_port)

    # Part d
    secretD = partD(num2, len2, tcp_sock, c, secretC)

    end_time = time.perf_counter()
    print("Part 1 Complete")
    print("Summary:")
    print(f"A: {secretA}")
    print(f"B: {secretB}")
    print(f"C: {secretC}")
    print(f"D: {secretD}")
    print()

    print(f"Time elapsed: {end_time - start_time:.4f}s")

if __name__ == "__main__":
    main(sys.argv[0:])
