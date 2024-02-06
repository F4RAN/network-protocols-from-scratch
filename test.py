import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("google.com", 80))
get_request = f"GET / HTTP/1.1\r\nHost: google.com\r\nUser-Agent: curl/8.4.0\r\nAccept: */*\r\n\r\n"
s.sendall(get_request.encode())
response = s.recv(1024)
print(response)
s.close()
