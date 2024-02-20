# based on RFC 8446: https://datatracker.ietf.org/doc/html/rfc8446
import os
import socket
import struct
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization

# Initial TLS Header
header = struct.pack(">B", 0x16)  # Handshake
header += struct.pack(">H", 0x0304)  # TLS 1.3
# +3 is for Length of the Length field
header_length = len(header)
# Handshake Header
handshake_type = struct.pack(">B", 0x01)  # Client Hello
# +3 for Length of the handshake message
version = struct.pack(">H", 0x0304)  # TLS 1.3
random = os.urandom(32)  # client random nonce
session_id_length = struct.pack(">B", 0x00)  # 0 length session id
# 5 important symmetric cipher suites
cipher_suites = [0x1301, 0x1302, 0x1303, 0x1304, 0x1305]
cs_length = struct.pack(">H", len(cipher_suites) * 2)
cipher_suites_bytes = struct.pack(f'>{len(cipher_suites)}H', *cipher_suites)
compression_methods_length = struct.pack(">B", 0x01)
compression_methods = struct.pack(">B", 0x00)
handshake_body_length = len(handshake_type) + len(version) + len(random) + len(session_id_length) + len(cs_length) + len(cipher_suites_bytes) + len(compression_methods) + len(compression_methods_length) + 3
# Extensions
extension_length = struct.pack(">H", 0x002b)
# server_name example.org
ext_type = struct.pack(">H", 0x0000)
ext_length = struct.pack(">H", 0x0010)
srv_name_list_length = struct.pack(">H", 0x000e)
srv_name_type = struct.pack(">B", 0x00)
srv_name_length = struct.pack(">H", 0x000b)
srv_name = b"example.org"

# ec_point_formats
# ext2_type = struct.pack(">H", 0x000b)
# ext2_length = struct.pack(">H", 0x0004)
# ec_point_formats_length = struct.pack(">B", 0x03)
# ec_point_formats = b'\x00' + struct.pack(">H", 0x0102)

# supported_groups
ext3_type = struct.pack(">H", 0x000a)
ext3_length = struct.pack(">H", 0x0022)
supported_groups_length = struct.pack(">H", 0x0020)
supported_groups = struct.pack(f'>H', 0x001d) + struct.pack(f'>H', 0x0017) + struct.pack(f'>H', 0x0019) + \
                   struct.pack(f'>H', 0x0018) + struct.pack(f'>H', 0x0100) + struct.pack(f'>H', 0x0101) + \
                   struct.pack(f'>H', 0x0102) + struct.pack(f'>H', 0x0103) + struct.pack(f'>H', 0x0104)

# key_share
ext4_type = struct.pack(">H", 0x0033)
ext4_length = struct.pack(">H", 0x0047)
key_share_length = struct.pack(">H", 0x0045)
# key_share_entry
ks_group = struct.pack(">H", 0x0017)
key_exchange_length = struct.pack(">H", 0x0041)
private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())
public_key = private_key.public_key()
key_exchange = struct.pack(">B", 0x04) + public_key.public_bytes(encoding=serialization.Encoding.X962,
                                                                 format=serialization.PublicFormat.UncompressedPoint)
extentions_length = len(ext_type) + len(ext_length) + len(srv_name_list_length) + len(srv_name_type) + len(srv_name_length) + len(srv_name) + \
                    len(ext3_type) + len(ext3_length) + len(supported_groups_length) + len(supported_groups) + \
                    len(ext4_type) + len(ext4_length) + len(key_share_length) + len(ks_group) + len(key_exchange_length) + len(key_exchange)
handshake_length = handshake_body_length + extentions_length
header += struct.pack(">H", handshake_length - 6)  # Length of the handshake message
handshake_length = handshake_length - 6 - 5  # Length of the handshake message
handshake = handshake_type + struct.pack(">I", handshake_length)[1:] + version + random + session_id_length + cs_length + cipher_suites_bytes + compression_methods_length + compression_methods + extension_length + \
            ext_type + ext_length + srv_name_list_length + srv_name_type + srv_name_length + srv_name + \
            ext3_type + ext3_length + supported_groups_length + supported_groups + \
            ext4_type + ext4_length + key_share_length + ks_group + key_exchange_length + key_exchange
# Preparing the message
print(header.hex())
print(handshake.hex())
message = header + handshake
# Sending the message to the server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.connect(("example.org", 443))
server.send(message)
response = server.recv(1024)
print(response)
response2 = server.recv(1024)
print(response2)
