# Based on RFC 2606, RFC 1035: https://datatracker.ietf.org/doc/html/rfc2616

import socket
import dns


class Response:
    def __init__(self, header, body):
        self.header = header
        self.body = body
        self.status = ""
        self.status_message = ""
        self.headers = {}
        self.parse_header()

    def parse_header(self):
        self.header = self.header.decode()
        self.header = self.header.split("\r\n")
        self.status = self.header[0].split(" ")[1]
        self.status_message = self.header[0].split(" ")[2]
        self.headers = {}
        self.body = ""
        for i in range(1, len(self.header)):
            if self.header[i] == "":
                break
            else:
                self.headers[self.header[i].split(": ")[0]] = self.header[i].split(": ")[1]

    def parse_body(self, body):
        if self.headers["Content-Type"].find("text/html") != -1:
            self.body = body.decode()
        else:
            self.body = body


class Request:
    def __init__(self, socket):
        self.s = socket

    def send(self, request):
        chunk_size = 1024
        self.s.send(request.encode())
        response = b""
        chunk = self.s.recv(chunk_size)
        header = b""
        header_counter = 0
        while chunk:
            header_counter += 1
            if chunk.find("\r\n\r\n".encode()) != -1:
                header += chunk.split("\r\n\r\n".encode())[0]
                response += chunk.split("\r\n\r\n".encode())[1]
                break
            header += chunk
            chunk = self.s.recv(chunk_size)

        res = Response(header, response)
        total_length = int(res.headers["Content-Length"])
        remaining_bytes = total_length - len(response)
        chunk_count = remaining_bytes // chunk_size + 1
        for i in range(chunk_count):
            chunk = self.s.recv(chunk_size)
            response += chunk
        self.s.close()
        res.parse_body(response)
        return res


class HTTP:
    def get(self, host, headers=""):
        if host.startswith("http://"):
            host = host[7:]
        else:
            Exception("Invalid URL")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ip = self.resolve(host)
        s.connect((ip, 80))
        get_request = f"GET / HTTP/1.1\r\n" \
                      f"Host: {host}\r\n" \
                      f"User-Agent: f4ran-browser/1.0.0\r\n" \
                      f"Accept: */*\r\n" \
                      f"\r\n"
        request = Request(s)
        response = request.send(get_request)

        return response


    def resolve(self, host):
        self.ip = dns.resolve(host)
        return self.ip
