import json


class Response:
    def __init__(self, header, body):
        self.header = header
        self.body = body
        self.json = {}
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
        elif self.headers["Content-Type"].find("application/json") != -1:
            self.body = body.decode()
            self.json = json.loads(self.body)
        else:
            self.body = body