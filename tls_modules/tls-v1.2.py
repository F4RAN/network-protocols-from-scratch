import hashlib
import hmac
import re
import socket
import os
import ssl
import struct
from math import ceil
from random import randrange

from Crypto.Cipher import AES
from OpenSSL import crypto

# Generate a random 32 byte string for the client hello random field
from cipher_suites import CipherSuites

url = "example.org"
client_hello_random = os.urandom(32)

# Specify the TLS version - we will use TLS 1.2
tls_version = 0x0303

# Create a socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to server
sock.connect((url, 443))

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

# Receive in loop
server_hello = b""
while True:
    chunk = sock.recv(2048)
    server_hello += chunk
    if len(chunk) < 2048:
        break

# Extract TLS records
matches = re.finditer(b'\x16\x03\x03', server_hello)
positions = [match.start() for match in matches]
server_hello_parts = []
for i in range(len(positions)):
    start = positions[i]
    if i < len(positions) - 1:
        end = positions[i + 1]
    else:
        end = len(server_hello) - 1
    server_hello_parts.append(server_hello[start:end])

print(server_hello_parts[0][:10], server_hello_parts[1][:10], server_hello_parts[2][:10], server_hello_parts[3][:10])

# Extract TLS records
# \x16\x03\x03 is the record header for a TLS handshake
tls_remaining = server_hello
certificates = b""
while len(tls_remaining) > 0:
    index = tls_remaining.index(b"\x16\x03\x03")
    tls_remaining = tls_remaining[index:]
    ht = tls_remaining[5]
    print(ht)
    if ht == 0x02:
        # Its server hello
        length = tls_remaining[6:9]
        version = tls_remaining[9:11]
        server_hello_random = tls_remaining[11:43]
        session_id_length = tls_remaining[43:44]
        session_id = tls_remaining[44:76]
        cipher_suite = tls_remaining[76:78]
        compression_method = tls_remaining[78:79]
        tls_remaining = tls_remaining[79:]
        print(
            f"Server hello: {version.hex()} {server_hello_random.hex()} {session_id_length.hex()} {session_id.hex()} {cipher_suite.hex()} {compression_method.hex()}")
        continue
    if ht == 0x0b:
        # Its certificate
        length = struct.unpack(">I", b"\x00" + tls_remaining[6:9])[0]
        certificates = tls_remaining[9:9 + length]
        tls_remaining = tls_remaining[9 + length:]
        continue
    elif ht == 0x0c:
        # Its server key exchange
        length = struct.unpack(">I", b"\x00" + tls_remaining[6:9])[0]
        server_key_exchange = tls_remaining[9:9 + length]  # Deffie-Hellman Server Params
        tls_remaining = tls_remaining[9 + length:]
        continue
    elif ht == 0x0e:
        # Its server hello done
        length = struct.unpack(">I", b"\x00" + tls_remaining[6:9])[0]
        server_hello_done = tls_remaining[9:9 + length]
        tls_remaining = tls_remaining[9 + length:]
        print(tls_remaining)
        continue
    elif not ht:
        print("No more records")
        break
    else:
        print("Unknown record")
        break

# Extract certificate
certificates_remaining = certificates[3:]
certificates_list = []
while len(certificates_remaining) > 0:
    length = struct.unpack(">I", b"\x00" + certificates_remaining[:3])[0]
    certificate = certificates_remaining[3:3 + length]
    certificates_list.append(certificate)
    certificates_remaining = certificates_remaining[3 + length:]

# Load cert bytes into an X.509 object
hostname = url if url.startswith("www.") else "www." + url
prev_cert = ""
for index, c in enumerate(certificates_list):
    cert = crypto.load_certificate(crypto.FILETYPE_ASN1, c)
    # Print some details from the cert
    print(f"Issuer: {cert.get_issuer()}")
    print(f"Subject: {cert.get_subject()}")
    print(f"Serial Number: {cert.get_serial_number()}")
    print(f"Version: {cert.get_version()}")
    print(f"Validity Start: {cert.get_notBefore()}")
    print(f"Validity End: {cert.get_notAfter()}")
    # Validate hostname matches
    if index == 0:
        common_name = cert.get_subject().commonName
        if common_name != hostname:
            print(f"Common name {common_name} does not match hostname {hostname}")
            exit(1)
    else:
        # Validate issuer matches previous cert subject
        issuer = prev_cert.get_issuer()
        subject = cert.get_subject()
        if issuer != subject:
            print(f"Issuer {issuer} does not match subject {subject}")
            exit(1)
    prev_cert = cert

p_len = int.from_bytes(server_key_exchange[:2], 'big')
p = int.from_bytes(server_key_exchange[2:2 + p_len], 'big')
server_key_exchange = server_key_exchange[2 + p_len:]
g_len = int.from_bytes(server_key_exchange[:2], 'big')
g = int.from_bytes(server_key_exchange[2:2 + g_len], 'big')
server_key_exchange = server_key_exchange[2 + g_len:]
pub_key_len = int.from_bytes(server_key_exchange[:2], 'big')
pub_key = int.from_bytes(server_key_exchange[2:2 + pub_key_len], 'big')
# print(f"Deffie-Hellman Server Params: p={p}, g={g}, pub_key={pub_key}")

# Private key
priv_key = randrange(0, p)
public_key = pow(g, priv_key, p)
pre_master_secret = pow(pub_key, priv_key, p)
# convert to bytes
pre_master_secret = pre_master_secret.to_bytes((pre_master_secret.bit_length() + 7) // 8, 'big')
print(f"Pre-master secret: {pre_master_secret}")

# Randoms
c_random = client_hello_random
s_random = server_hello_random


# TLS PRF
# PRF stands for "Pseudorandom Function". In the context of TLS, it is used to derive keys from secret seed material.
# The TLS-PRF takes in a secret, a label, and a seed value. It then generates pseudorandom output by mixing the inputs,
# usually with HMAC-SHA256 or a similar cryptographic hash.
def TLS_PRF(secret, label, seed, output_size):
    # Concatenate label and seed
    label_seed = label + seed
    # Generate output sized for keys
    output_bytes = ceil(output_size / 8)  # Number of key bits /
    # Initialize output
    derived_output = b""
    # MixSecret iterates hash multiple times
    A = hmac.new(secret, msg=label_seed, digestmod=hashlib.sha256)
    # hmac = HMAC-SHA256 in Py
    i = 1
    while len(derived_output) < output_bytes:
        A.update(A.digest())
        derived_output += A.digest()

        i += 1

        # Truncate to needed key size
    return derived_output[:output_bytes]


print(f"Pre master secret: {pre_master_secret.hex()}")
print(f"Client random: {c_random.hex()}")
print(f"Server random: {s_random.hex()}")
master_secret = TLS_PRF(pre_master_secret, b"master secret", s_random + c_random, 48)

# Generate key block
key_block = TLS_PRF(master_secret, b"key expansion", s_random + c_random, 104)

print(f"Master secret: {master_secret}")
print(f"Key block: {key_block}")


chosen_cipher = cipher_suite
key = key_block[:13].ljust(16, b"\x00")
iv = os.urandom(16)

# Encrypt using AES CBC mode
cipher_params = CipherSuites[int.from_bytes(chosen_cipher, 'big')]

aes_ctx = AES.new(key, cipher_params['mode'], iv)

# Prepare the message
msg = b"GET / HTTP/1.1\r\nHost: " + url.encode() + b"\r\n\r\n"
# Pad the message
msg += b"\x00" * (16 - len(msg) % 16)
# Encrypt the message
ciphertext = aes_ctx.encrypt(msg)
print(f"Encrypted message: {ciphertext.hex()}")

# prepare record
record = b"\x17" + b"\x03\x03" + struct.pack(">H", len(ciphertext) + 16) + iv + ciphertext

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((url, 443))
sock.send(record)
a = sock.recv(512)
print(a)
sock.close()

# Decrypt the msg
aes_ctx = AES.new(key, cipher_params['mode'], iv)
plaintext = aes_ctx.decrypt(ciphertext)
print(f"Decrypted message: {plaintext.decode()}")