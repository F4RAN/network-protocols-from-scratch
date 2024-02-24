# based on RFC 8446: https://datatracker.ietf.org/doc/html/rfc8446
import os
import socket
import struct
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey


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
ext_type = struct.pack(">H", 0x0000)
ext_length = struct.pack(">H", 0x000e)
srv_name_list_length = struct.pack(">H", 0x000c)
srv_name_type = struct.pack(">B", 0x00)
srv_name_length = struct.pack(">H", 0x0009)
srv_name = b"yahoo.com"


# ec_point_formats
# ext2_type = struct.pack(">H", 0x000b)
# ext2_length = struct.pack(">H", 0x0004)
# ec_point_formats_length = struct.pack(">B", 0x03)
# ec_point_formats = b'\x00' + struct.pack(">H", 0x0102)

# supported_groups
ext3_type = struct.pack(">H", 0x000a)
supported_groups = struct.pack(f'>H', 0x001d) + struct.pack(f'>H', 0x0017) + struct.pack(f'>H', 0x001e) + struct.pack(f'>H', 0x0019) + \
                   struct.pack(f'>H', 0x0018) + struct.pack(f'>H', 0x0100) + struct.pack(f'>H', 0x0101) + \
                   struct.pack(f'>H', 0x0102) + struct.pack(f'>H', 0x0103) + struct.pack(f'>H', 0x0104)

ext3_length = struct.pack(">H", len(supported_groups) + 2)
supported_groups_length = struct.pack(">H", len(supported_groups))

# signature_algorithms
ext4_type = struct.pack(">H", 0x000d)
ext4_length = struct.pack(">H", 0x0024)
signature_algorithms_length = struct.pack(">H", 0x0022)
signature_algorithms = struct.pack(f'>H', 0x0403) + struct.pack(f'>H', 0x0503) + struct.pack(f'>H', 0x0603) + \
                        struct.pack(f'>H', 0x0807) + struct.pack(f'>H', 0x0808) + struct.pack(f'>H', 0x081a) + \
                        struct.pack(f'>H', 0x081b) + struct.pack(f'>H', 0x081c) + struct.pack(f'>H', 0x0809) + \
                        struct.pack(f'>H', 0x080a) + struct.pack(f'>H', 0x080b) + struct.pack(f'>H', 0x0804) + \
                        struct.pack(f'>H', 0x0805) + struct.pack(f'>H', 0x0806) + struct.pack(f'>H', 0x0401) + \
                        struct.pack(f'>H', 0x0501) + struct.pack(f'>H', 0x0601)

# supported_versions
ext5_type = struct.pack(">H", 0x002b)
ext5_length = struct.pack(">H", 0x0003)
supported_versions_length = struct.pack(">B", 0x02)
supported_versions = struct.pack(">H", 0x0304)

# psk_key_exchange_modes
ext6_type = struct.pack(">H", 0x002d)
ext6_length = struct.pack(">H", 0x0002)
psk_key_exchange_modes_length = struct.pack(">B", 0x01)
psk_key_exchange_modes = struct.pack(">B", 0x01)


# key_share
ext7_type = struct.pack(">H", 0x0033)
ext7_length = struct.pack(">H", 0x0026)
key_share_length = struct.pack(">H", 0x0024)
private_key = X25519PrivateKey.generate()
public_key = private_key.public_key()
ks_group = struct.pack(">H", 0x001d) + struct.pack(">H", len(public_key.public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw))) + public_key.public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
key_exchange = private_key.exchange(public_key)
key_exchange_length = struct.pack(">H", len(key_exchange))


extensions_length = len(ext_type) + len(ext_length) + len(srv_name_list_length) + len(srv_name_type) + len(srv_name_length) + len(srv_name) + \
                    len(ext3_type) + len(ext3_length) + len(supported_groups_length) + len(supported_groups) + \
                    len(ext4_type) + len(ext4_length) + len(signature_algorithms_length) + len(signature_algorithms) + \
                    len(ext5_type) + len(ext5_length) + len(supported_versions_length) + len(supported_versions) + \
                    len(ext6_type) + len(ext6_length) + len(psk_key_exchange_modes_length) + len(psk_key_exchange_modes) + \
                    len(ext7_type) + len(ext7_length) + len(key_share_length) + len(ks_group)
                    # + len(key_exchange_length) + len(key_exchange)
print(extensions_length)
# extensions_length = 0x002b
handshake_length = handshake_body_length + extensions_length
header += struct.pack(">H", handshake_length + 14)  # Length of the handshake message
extensions_length = struct.pack(">H", extensions_length + 12)
handshake_length = handshake_length + 10 # Length of the handshake message
handshake = handshake_type + struct.pack(">I", handshake_length)[1:] + version + random + session_id_length + cs_length + cipher_suites_bytes + compression_methods_length + compression_methods + extensions_length + \
            ext_type + ext_length + srv_name_list_length + srv_name_type + srv_name_length + srv_name + \
            ext3_type + ext3_length + supported_groups_length + supported_groups + \
            b"\x00\x23\x00\x00" + b"\x00\x16\x00\x00" + b"\x00\x17\x00\x00" + \
            ext4_type + ext4_length + signature_algorithms_length + signature_algorithms + \
            ext5_type + ext5_length + supported_versions_length + supported_versions + \
            ext6_type + ext6_length + psk_key_exchange_modes_length + psk_key_exchange_modes + \
            ext7_type + ext7_length + key_share_length + ks_group
            # + key_exchange_length + key_exchange
# print(key_exchange.hex(), key_exchange_length.hex(), len(key_exchange))
print(ext5_type.hex(), ext5_length.hex(), key_share_length.hex(), ks_group.hex(), key_exchange_length.hex(), key_exchange.hex())
# Preparing the message
message = header + handshake
# Sending the message to the server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.connect(("yahoo.com", 443))
print(server.getpeername())
server.send(message)
response = server.recv(1024)
print(response)
response2 = server.recv(1024)
print(response2)
