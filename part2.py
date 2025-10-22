# Lab 1 Part 2

# TODO: Need to change error handling: can't just close listener on part a

import threading
import socket
import sys
import struct
import random

# Constants
DEBUG = True

MAX_PORT = 65535
MIN_PORT = 1024
BANNED_PORT = 41201
PARTA_HEADER = (12, 0, 1, )
PARTA_PAYLOAD = b"hello world\0"

# Global list of active sockets for cleanup
sockets = []
sockets_lock = threading.Lock()

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

    # will need to handle clean up
    processed_clients = []

    # Start with a UDP port that the clients will connect to
    listener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    with sockets_lock:
        sockets.append(listener)

    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind(('', port))

    # Listen for keyboard interrups to exit
    try:
        # Listen for clients and spawn new threads for them
        while True:
            data, addr = listener.recvfrom(1024)
            print(f"Connected by {addr}") 

            # Run part a first since it is a UDP connection accessed by all clients at the
            # start. Spawn a thread to handle individual clients on separate servers
            # later down the line.

            if addr not in processed_clients:
                processed_clients.append(addr)
                thread = threading.Thread(target=server_loop, args=(listener, addr, data), daemon=True)
                thread.start()
    except KeyboardInterrupt:
        print()
        print("Server terminated by user")
        sys.exit()
    finally:
        with sockets_lock:
            for s in sockets:
                s.close()
        print("All sockets closed")
        

def server_loop(listener, addr, data):
    """Runs the main server loop consisting of parts a-d. This is the work
    done by each thread.

    Params:
        - listener, initial udp port to send response on
        - addr: client address to send to
        - data: initial data from client
    """
    num, udp_port, secretA, len1, sid = part_a(listener, data, addr)
    tcp_port, secretB = part_b(num, udp_port, secretA, len1, sid)
    num2, len2, c, secretC, tcp_sock = part_c(tcp_port, secretB) 
    part_d(num2, len2, c, secretC, tcp_sock, sid)
    print(f"Finished connection from {addr}")
    return

def part_a(listener, data, addr):
    """Carry out the logic of part A. Once data is recived from client,
    sends a response to the client containing information for part B.
    If socket is closed by server, exits thread gracefully.

    Params:
        - listener: udp socket to listen and send response on
        - data: data recieved from client when contact is made
        - addr: client address

    Returns:
        - num_packets: number of packets to send
        - udp_port: udp port to connect to
        - secretA: secret from part a
        - length: length of payload to send
        - sid: client last 3 digits of student number
    """
    try:
        if DEBUG:
            print(f"Recieved {data} from {addr}")

        if len(data) != 24:
            return
            # listener.close() dont need to close the udp socket because the server is listening

        # Check header against expected, close listner if it's wrong
        payload, sid = validate_packet(data, 12, 0, 1, None)
        if not payload:
            if DEBUG:
                print("Header check failed")
            # listener.close()
            return

        payload = data[12:]
        print(payload)

        if payload != PARTA_PAYLOAD:
            if DEBUG:
                print("Payload check failed")
            # listener.close()
            return

        #generate response
        num = random.randint(1, 100)
        len1 = random.randint(1, 64)

        # TODO
        udp_port = random.randint(MIN_PORT, MAX_PORT)  # check that this is a valid port to bind to
        secretA = random.randint(1, 4096)

        response_header = generate_header(16, 0, 2)
        response_payload = struct.pack("!IIII", num, len1, udp_port, secretA)
        print(response_payload)
        to_send = response_header + response_payload
        listener.sendto(to_send, addr)

        return (num, udp_port, secretA, len1, sid)
    except OSError as e:
        if DEBUG:
            print(f"OSError: {e}. Thread shutting down.")
        
        sys.exit()

def part_b(num, udp_port, secretA, len1, sid):
    """Carry out the logic of part B by sending acks for num_packets 
    packets of zeroed payloads sent by the client. If socket is closed by server, 
    exits thread gracefully.

    Params:
        - num: number of packets to recieve
        - udp_port: udp port to connect to
        - secretA: secret from part a
        - len1: length of payload to recieve
        - sid: client last 3 digits of student number from part a

    Returns:
        - tcp_port: port to create to in part c
        - secretB: secret from part b
    """
    try:
        print(f"Part B beginning...")
        udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Add sockets to global list
        with sockets_lock:
            sockets.append(udp_sock)

        udp_sock.settimeout(1)

        udp_sock.bind(('', udp_port)) # need to error handle this
        i = 0
        while i < num:
            data, addr = udp_sock.recvfrom(1024)  # wait for packet

            if random.random() < 0.2:
                if DEBUG:
                    print(f"Dropping packet {i} to simulate loss")
                continue
            packet, _ = validate_packet(data, len1 + 4, secretA, 1, sid)
            if not packet:
                if DEBUG:
                    print("Packet validation failed")

                # Remove socket from global list
                with sockets_lock:
                    sockets.remove(udp_sock)
                
                udp_sock.close()

                sys.exit()
            #check packet_id
            packet_id = struct.unpack("!I", packet[:4])[0]
            if packet_id > i:
                if DEBUG:
                    print(f"Packet ID mismatch: expected {i}, got {packet_id}")
                with sockets_lock:
                    sockets.remove(udp_sock)
                udp_sock.close()
                sys.exit()
            elif packet_id < i:
                if DEBUG:
                    print(f"Duplicate packet {packet_id} received, ignoring.")
                continue
            # Send ack
            print(f"Sending ack for packet {i}")
            ack_header = generate_header(4, secretA, 2)
            ack_payload = struct.pack("!I", i)
            udp_sock.sendto(ack_header + ack_payload, addr)
            i += 1

        tcp_port = random.randint(MIN_PORT, MAX_PORT)
        secretB = random.randint(1, 4096)
        payload = struct.pack("!II", tcp_port, secretB)
        header = generate_header(8, secretA, 2)
        udp_sock.sendto(header + payload, addr)
        with sockets_lock:
            sockets.remove(udp_sock)
        udp_sock.close()
        print("Closing connection")
        return tcp_port, secretB
    except OSError as e:
        if DEBUG:
            print(f"OSError: {e}. Thread shutting down.")
        
        sys.exit()

def part_c(tcp_port, secretB):
    """Carry out the logic for part C by creating a host on tcp_port and sending
    information once the client connects. If socket is closed by server, exits thread gracefully.

    Params:
        - tcp_port: port to connect to
        - secretB: secret from part b

    Returns:
        - num2: number of packets to send for part d
        - len2: length of payload to send for part d
        - c: character that is sent num2 times in payload for part d
        - secretC: secret from part c
        - conn: socket to send data over for part d
    """
    try:
        print("Part C beginning...")
        tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_sock.settimeout(3)
        with sockets_lock:
            sockets.append(tcp_sock)

        # Bind and listen for client
        tcp_sock.bind(('', tcp_port))
        tcp_sock.listen(1)
        conn, addr = tcp_sock.accept() # we may need to add and close conn bc its also a socket
        tcp_sock.settimeout(None)

        with sockets_lock:
            sockets.append(conn)

        if DEBUG:
            print(f"Connected to {addr}")
        
        # Generate random ints and send to client
        num2 = random.randint(1,16)
        len2 = random.randint(1,16)
        secretC = random.randint(1, 4096)
        c = chr(random.randint(95,122))
        payload = struct.pack("!III", num2, len2, secretC)
        print(payload)
        payload += bytes(str(c), 'utf-8') + b"\0\0\0"
        header = generate_header(13, secretB, 2)
        conn.send(header + payload)

        with sockets_lock:
            sockets.remove(tcp_sock)

        tcp_sock.close()

        return num2, len2, c, secretC, conn
    except socket.timeout as e:
        print(f"Socket timed out: {e}")
        with sockets_lock:
            sockets.remove(tcp_sock)
            sockets.remove(conn)

        tcp_sock.close()
        conn.close()
        sys.exit()
    except OSError as e:
        if DEBUG:
            print(f"OSError: {e}. Thread shutting down.")
        
        sys.exit()


def part_d(num2, len2, c, secretC, sock, sid):
    """Carry out the logic for part D by recieving num2 packets of len2 consisting of character c.
    If socket is closed by server, exits thread gracefully.

    Params:
        - num2: number of packets to send
        - len2: length of payload to send
        - c: character that is sent num2 times in payload
        - secretC: secret from part c
        - tcp_sock: socket to send data over
        - sid: client last 3 digits of student number from part a
    """
    try:
        print("Part D beginning...")
        for i in range(num2):
            data = sock.recv(12 + len2 + ((-1 * len2) % 4))
            payload, _ = validate_packet(data, len2, secretC, 1, sid)
            if not payload:
                if DEBUG:
                    print("Packet validation failed")
                with sockets_lock:
                    print(sockets)
                    sockets.remove(sock)
                sock.close()
                return
            expected_payload = c.encode() * len2
            if payload != expected_payload:
                if DEBUG:
                    print("Payload mismatch")
                with sockets_lock:
                    sockets.remove(sock)
                sock.close()
                return
        header = generate_header(0, secretC, 2)
        payload = struct.pack("!I", random.randint(1, 100))
        sock.send(header + payload)
        print("Closing connection")

        sock.close()
        return
    
    except OSError as e:
        if DEBUG:
            print(f"OSError: {e}. Thread shutting down.")
        
        sys.exit()

def get_header(data):
    """
    Gets and returns the header data in a tuple of
    (payload_len, secret, step, sid)
    """
    header_data = data[:12]

    # Handle header
    return struct.unpack("!IIHH", header_data)

def generate_header(payload_len, secret, step, sid=758):
    """Packs the header into network order.

    Params:
        - payload_len: length of payload being sent
        - secret: secret to include in header
        - step: step number
        - sid: student number to use

    Returns:
        - header formatted in network order consisting of 4 bytes for
          payload length, 4 bytes for the secret, and 2 bytes each for the step
          and last 4 digits of Solden's student number.
    """
    return struct.pack('!IIHH', int(payload_len), int(secret), int(step), sid)

def validate_packet(data, expected_payload_len, expected_secret, expected_step, expected_sid):
    """
    Validates a packet's header and payload against expected values.
    data: The full packet data
    expected_payload_len: Expected length of the payload
    expected_secret: Expected secret value, optional
    expected_step: Expected step value, optional
    expected_sid: Expected student ID value, optional
    1: Check header length
    2: Check that header length matches payload length ( within 4 padded bytes )
    3: optionally check secret, step, sid
    Returns payload if valid, None otherwise.
    """
    header = get_header(data)
    payload_len, secret, step, sid = header

    # 1: Check header length
    if len(data) < 12:
        if DEBUG:
            print("Invalid packet: Header too short")
        return None

    # 2: Check that header length matches payload length ( within 4 padded bytes ) ( this is wrong )
    actual_payload_len = len(data) - 12
    aligned_bytes = expected_payload_len + ((-1 * expected_payload_len) % 4)
    if actual_payload_len != aligned_bytes:
        if DEBUG:
            print("Invalid packet: Payload length mismatch")
        return None

    # 3: optionally check secret, step, sid
    if expected_secret is not None and secret != expected_secret:
        if DEBUG:
            print("Invalid packet: Secret mismatch")
        return None

    if expected_step is not None and step != expected_step:
        if DEBUG:
            print("Invalid packet: Step mismatch")
        return None

    if expected_sid is not None and sid != expected_sid:
        if DEBUG:
            print("Invalid packet: SID mismatch")
        return None

    return data[12:12 + payload_len], sid


if __name__ == "__main__":
    main(sys.argv[0:])
