# Lab 1 Part 2

import threading
import sys

DEBUG = True

def main(args):
    server(args[1], args[2])

def server(host, port):
    # Run the main server logic here

    # Need to change this to exit gracefully
    while True:
        # Create listening loop
        thread = threading.Thread(target=server_loop, daemon=True)
        thread.start()
        


def server_loop():
    # Run the logic of the server loop
    return

def part_a():
    # Part a
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
    main(sys.argv[0:], DEBUG)
