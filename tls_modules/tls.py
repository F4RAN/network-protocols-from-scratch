import socket
import os
import struct

# Generate a random 32 byte string for the client hello random field
client_hello_random = os.urandom(32)

# Specify the TLS version - we will use TLS 1.2
tls_version = 0x0303

# Create a socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to server
sock.connect(("example.com", 443))

# Handshake type - client hello
handshake_type = struct.pack(">B", 0x01)

# Version - TLS 1.2
version = struct.pack(">H", tls_version)

# ClientHello random
random = client_hello_random

# Session ID - empty
session_id_length = struct.pack(">B", 0x00)

# Cipher suites u can see from https://www.iana.org/assignments/tls-parameters/tls-parameters.xhtml#tls-parameters-4
cipher_suites = [0xc02b, 0xc02f]  # TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256, TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256
length = f'>{len(cipher_suites)}H'
cipher_suites_bytes = struct.pack(length, *cipher_suites)

# Cipher suites length - 2 bytes
cipher_suites_length = struct.pack(">H", len(cipher_suites) * 2)

# Compression methods length - 1 byte
compression_methods_length = struct.pack(">B", 1)

# Compression methods - null only
compression_methods = struct.pack(">B", 0x00)

# Handshake length
length_in_handshake = len(handshake_type) + len(version) + len(random) + len(session_id_length) + len(
    cipher_suites_length) + len(cipher_suites_bytes) + len(compression_methods_length) + len(compression_methods)
handshake_length = struct.pack(">H", length_in_handshake)
# Handshake header
header = struct.pack(">B", 0x16)  # Handshake
header += struct.pack(">B", 0x03)  # TLS 1.2
total_length = length_in_handshake + 4
reserve = b""
if total_length < 0xFF:
    print("here")
    reserve += struct.pack(">H", 0x0000)
elif total_length < 0xFFFF:
    reserve += struct.pack(">B", 0x00)

total_length_bytes = struct.pack(">H", total_length)

print(reserve, total_length_bytes)

header += struct.pack(">H", total_length)


# Assemble full client hello
full_client_hello = header + handshake_type + handshake_length + version + random + session_id_length + \
                    cipher_suites_length + cipher_suites_bytes + compression_methods_length + compression_methods


# Send client hello
sock.send(full_client_hello)
# Receive server hello
server_hello = sock.recv(1024)
