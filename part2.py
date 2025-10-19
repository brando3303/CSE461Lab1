# Lab 1 Part 2

import threading
import socket
import sys
import struct

DEBUG = True
MAX_PORT = 65535
MIN_PORT = 1024
BANNED_PORT = 41201

def main(args):
    if (len(args) != 3):
        print(f"Usage: {args[0]} host port")

    host = args[1]
    port = int(args[2])

    if port == BANNED_PORT:
        print("Cannot run server on port 41201")
        sys.exit()
    
    if port < MIN_PORT or port > MAX_PORT:
        print("Invalid port")
        sys.exit()
    
    # Run the server
    server(host, port)

def server(host, port):
    """
    Runs the main server, listening for connections and spawning
    new threads for each new client to handle the server logic. 
    """

    # Start with a UDP port that the clients will connect to
    listener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind(('', port))

    # Need to change this to exit gracefully

    # Accept new connections and spawn new threads for them
    while True:
        data, addr = listener.recvfrom(1024)
        print(f"Connected by {addr}") 

        # Run part a first since it is a UDP connection accessed by all clients at the
        # start. Spawn a thread to handle individual clients on separate servers
        # later down the line.
        part_a(listener, data, addr)
        
        thread = threading.Thread(target=server_loop, args=(data, addr), daemon=True)
        thread.start()
        

def server_loop(addr):
    # Run the logic of the server loop
    
    print(f"Finished connection from {addr}")
    return

def part_a(listener, data, addr):
    # Part a
    if DEBUG:
        print(f"Recieved {data} from {addr}")

    if len(data) != 24:
        listener.close()
    
    return

def part_b():
    # Part b
    return

def part_c():
    # Part b
    return

def part_d():
    # Part b
    return

if __name__ == "__main__":
    main(sys.argv[0:])
