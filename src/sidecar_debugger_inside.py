"""
This script handles connection on a port. It should be used for debugging the sidecar by routing the socat to this port
instead of the actual program.
Pass the port as a CLI argument to the program.
"""

import socket
import sys

# Define the port number to listen on
port = int(sys.argv[-1])

# Create a socket object
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to a specific address and port
server_address = ("0.0.0.0", port)
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)

# Wait for a connection
connection, client_address = sock.accept()

while True:
    try:
        # Read from the socket
        message = connection.recv(2048).decode().strip()
        if message == "listen":
            # Read from stdin
            input_data = input()
            connection.send(input_data.encode("utf-8"))
        else:
            print(message, flush=True)
    except Exception:
        break

# Clean up the connection
connection.close()
