# Based on RFC 2606, RFC 1035: https://datatracker.ietf.org/doc/html/rfc2616

import socket
import dns


class HTTP:
    def get(self, host, headers=""):
        if host.startswith("http://"):
            host = host[7:]
        else:
            Exception("Invalid URL")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ip = self.resolve(host)
        print(ip)
        s.connect((ip, 80))
        get_request = f"GET / HTTP/1.1\r\n" \
                      f"Host: {host}\r\n" \
                      f"User-Agent: f4ran-browser/1.0.0\r\n" \
                      f"Accept: */*\r\n" \
                      f"\r\n"
        print(get_request)
        s.send(get_request.encode())
        response = s.recv(1024)
        print(response)
        s.close()

    def resolve(self, host):
        self.ip = dns.resolve(host)
        return self.ip

    def __str__(self):
        return f"HTTP(url={self.url}, method={self.method}, headers={self.headers}, body={self.body})"

    def __repr__(self):
        return self.__str__()
