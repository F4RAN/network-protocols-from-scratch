import socket
import os
import struct
from OpenSSL import crypto
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

# Session ID
session_id = os.urandom(32)
session_id_length = struct.pack(">B", 0x20)

# Cipher suites u can see from https://www.iana.org/assignments/tls-parameters/tls-parameters.xhtml#tls-parameters-4
cipher_suites = [0xc02b, 0xc02f, 0xcca9, 0xcca8, 0xc024, 0xc028,
                 0x009e, 0x0067, 0xc014, 0x0039, 0xc009, 0xc013,
                 0xc01f, 0x006b, 0xc00a, 0x0033, 0x009c, 0x009d,
                 0xc00f, 0xc005, 0x0035, 0x0000]
length = f'>{len(cipher_suites)}H'
cipher_suites_bytes = struct.pack(length, *cipher_suites)

# Cipher suites length - 2 bytes
cipher_suites_length = struct.pack(">H", len(cipher_suites) * 2)

# Compression methods length - 1 byte
compression_methods_length = struct.pack(">B", 1)

# Compression methods - null only
compression_methods = struct.pack(">B", 0x00)

# Total length --> Length does not include the same level fields ( then we don't calculate the length of the length
# field, content type, version in outer header) Then everything in handshake make total length
# +3 is for Length of the Length field

total_length = len(handshake_type) + len(version) + len(random) + len(session_id_length) + len(session_id) + len(
    cipher_suites_length) + len(cipher_suites_bytes) + len(compression_methods_length) + len(compression_methods) + 3

# Length in handshake is total length - 4 because handshake length is 3 bytes and 1 byte for handshake type
length_in_handshake = total_length - 4
handshake_length = struct.pack(">L", length_in_handshake)  # 8 Bytes or 4 Words
handshake_length = handshake_length[-3:]  # 3 Words or 6 Bytes ==> OR handshake_length[1:4]
# Handshake header
header = struct.pack(">B", 0x16)  # Handshake
header += struct.pack(">H", 0x0301)  # TLS 1.0

header += struct.pack(">H", total_length)

# Assemble full client hello
full_client_hello = header + handshake_type + handshake_length + version + random + session_id_length + session_id + \
                    cipher_suites_length + cipher_suites_bytes + compression_methods_length + compression_methods

# Send client hello
sock.send(full_client_hello)


server_hello = sock.recv(2048)
tls_remaining = sock.recv(2048)

# Parse server hello
handshake_type = server_hello[:1]
version = server_hello[1:3]
length = server_hello[3:5]
random = server_hello[5:37]
session_id_length = server_hello[37:38]
session_id = server_hello[38:70]
cipher_suite = server_hello[70:72]
compression_method = server_hello[72:73]
print(f"Handshake type: {handshake_type.hex()}")
print(f"Version: {version.hex()}")
print(f"Length: {length.hex()}")
print(f"Random: {random.hex()}")
print(f"Session ID length: {session_id_length.hex()}")
print(f"Session ID: {session_id.hex()}")
print(f"Cipher suite: {cipher_suite.hex()}")
print(f"Compression method: {compression_method.hex()}")

# Extract certificate
# handshake_type = tls_remaining[:1]
# length = tls_remaining[1:4]
# tls_remaining = tls_remaining[4:]
# print(f"Handshake type: {handshake_type.hex()}")
# print(f"Length: {length.hex()}")
# # Parse certificate
# certificates = []
# while len(tls_remaining) > 0:
#     certificate_type = tls_remaining[:1]
#     length = struct.unpack(">H", tls_remaining[1:3])[0]
#     certificate = tls_remaining[3:3 + length]
#     certificates.append(certificate)
#     tls_remaining = tls_remaining[3 + length:]
#
# print(f"Certificates: {len(certificates)}")
# for certificate in certificates:
#     x509 = crypto.load_certificate(crypto.FILETYPE_ASN1, certificate)
#     print(f"Subject: {x509.get_subject().CN}")
#     print(f"Issuer: {x509.get_issuer().CN}")
#     print(f"Serial: {x509.get_serial_number()}")
#     print(f"Version: {x509.get_version()}")
#     print(f"Signature: {x509.get_signature_algorithm()}")




