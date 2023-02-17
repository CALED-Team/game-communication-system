"""
This script handles connection on a port. It should be used for debugging the sidecar by routing the socat to this port
instead of the actual program.
Pass the port as a CLI argument to the program.
"""

import socket
import sys

# Define the port number to listen on
port = int(sys.argv[-1])

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(("localhost", port))

print("Connected to inside debugger")

while True:
    try:
        # Read from stdin
        input_data = input("> ").strip()
        if input_data != "listen":
            # Write to the socket
            client_socket.send(input_data.encode("utf-8"))
        else:
            # Read from the socket
            client_socket.send(input_data.encode("utf-8"))
            message = client_socket.recv(2048)
            print(message.decode(), flush=True)
    except Exception:
        break

# Clean up the connection
client_socket.close()
