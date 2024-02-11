import socket
import ssl

# SET VARIABLES
hostname = 'example.com'
context = ssl.create_default_context()

with socket.create_connection((hostname, 443)) as sock:
    print("here")
    with context.wrap_socket(sock, server_hostname=hostname) as ssock:
        print(ssock.version())