from http_modules.response import Response


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
        chunk_count = (remaining_bytes // chunk_size) + 1 if remaining_bytes // chunk_size != 0 else 0
        for i in range(chunk_count):
            # print(f"Remaining bytes: {remaining_bytes}")
            chunk = self.s.recv(chunk_size)
            response += chunk

        self.s.close()
        res.parse_body(response)
        return res