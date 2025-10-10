# Lab 1 Part 1a
import socket
import sys
import struct

def main(args):
    if len(args) != 3:
        return
    
    host = args[1]
    port = args[2]

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

    data = b""
    while True:
        chunk = s.recv(4096)
        if not chunk:
            break  # connection closed
        data += chunk
    
    print(data.decode("utf-8"))
    

def get_header(payload_len, secret, step):
    return struct.pack('!IIHH', int(payload_len), int(secret), int(step), 758)

if __name__ == "__main__":
    main(sys.argv[0:])
