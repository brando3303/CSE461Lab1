# Lab 1 Part 1
import socket
import sys
import struct

def main(args):
    if len(args) != 3:
        return
    
    host = args[1]
    port = args[2]

    # Part a
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

    data = s.recv(28)
    print(data[12:])
    unpacked = struct.unpack("!4I", data[12:])
    num_packets, length, udp_port, secretA = unpacked
    print(unpacked)

    # Part b
    s.connect((host, udp_port))
    s.settimeout(0.5)
    
    total_bytes = length + (-1 * length % 4)
    for i in range(num_packets):
        payload = struct.pack("!I", i)
        for _ in range(total_bytes):
            payload += b"x\00"
        header = get_header(len(payload), secretA, 1)
        to_send = header + payload

        # Send until we get ack from server
        while True:
            try:
                s.send(to_send)
                data = s.recv(4)
                break
            except socket.timeout as e:
                continue

        unpacked = struct.unpack("!I", data)
        if (unpacked[0] != i):
            print("uh oh")
    
    data = s.recv(8)
    unpacked = struct.unpack("!II", data)
    print(unpacked)
    
def get_header(payload_len, secret, step):
    return struct.pack('!IIHH', int(payload_len), int(secret), int(step), 758)

if __name__ == "__main__":
    main(sys.argv[0:])
