# Based on RFC 2606: https://datatracker.ietf.org/doc/html/rfc2616
import json
import socket
import dns


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

# Repetitive in all http requests
# Decorator to set up common HTTP request initialization steps
def INITIATE_HTTP(func):
    # Wrapper accepts original func arguments
    def wrapper(*args, **kwargs):
        # Set empty headers dict if not passed
        if kwargs.get("headers") is None:
            kwargs["headers"] = ""

        # Convert headers dict to HTTP format
        else:
            headers = [f"{k}: {v}\r\n" for k, v in kwargs["headers"].items()]
            kwargs["headers"] = "".join(headers)

        # Get host and path from request URL
        # vitalize.dev/hello/world
        # host: vitalize.dev
        # path: /hello/world
        host, path_params = args[0].make_host_from_url(args[1])

        # Resolve host to IP address
        ip = args[0].resolve(host)

        # Create socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Call the wrapped HTTP method
        return func(args[0], host, s, ip, path_params, **kwargs)
    return wrapper

"""
User-Agent - An HTTP header used to identify details about the client user agent like browser name and version. 
    This helps servers identify client capabilities.

Host - The domain name or IP address of the server that is being requested by the client.

Accept - An HTTP header specifying content-types the client can understand like json, xml, html etc. 
    Helps server determine best format to return.

Authorization – Contains client credentials like username/password or tokens to gain access to protected resources.

Cookie - Holds stateful session data that server can set with Set-Cookie header.
    Sent back by client in subsequent requests.

Content-Type – Media type of the request/response body like application/json, text/html etc. 
    to allow correct parsing.

Cache-Control – Directives like max-age, no-cache that specify how responses can be cached to improve performance.

HTTP Request: Message sent from client to server containing method, headers, body - 
    formatted according to HTTP standards. Methods like GET, POST define requested operation.

HTTP Response: Message sent back from server to client in response to a request. 
    Contains status code, headers and body of requested content or error messages.

Methods:
GET - The HTTP request method used to retrieve a representation of a resource.
POST – Submit data to be processed to an identified resource. Often used to submit HTML form data to backend server.
PUT – Upload/update a representation of a resource. Completely replaces existing resource.
DELETE – Deletes the specified resource.
OPTIONS – Used to describe communication options for target resource. Mainly used to retrieve supported methods, CORS settings etc.,
PATCH – Apply partial modifications to a resource. Added later with RFC 5789.


"""
class HTTP:
    def __init__(self):
        self.user_agent = "f4ran-browser/1.0.0"

    @INITIATE_HTTP
    def get(self, host, s, ip, path_params, headers):
        s.connect((ip, 80))
        get_request = f"GET /{path_params} HTTP/1.1\r\n" \
                      f"Host: {host}\r\n" \
                      f"User-Agent: {self.user_agent}\r\n" \ 
                      f"Accept: */*\r\n" \
                      f"{headers if headers else ''}"  \
                      f"\r\n"
        request = Request(s)
        response = request.send(get_request)
        return response

    @INITIATE_HTTP
    def post(self, host, s, ip, path_params, data, headers):
        s.connect((ip, 80))
        data_string = json.dumps(data)
        post_request = f"POST /{path_params} HTTP/1.1\r\n" \
                       f"Host: {host}\r\n" \
                       f"User-Agent: {self.user_agent}\r\n" \
                       f"Accept: */*\r\n" \
                       f"Content-Length: {len(data_string)}\r\n" \
                       f"{headers}" \
                       f"\r\n" \
                       f"{data_string if data else ''}"
        print(post_request)
        request = Request(s)
        response = request.send(post_request)
        return response

    @INITIATE_HTTP
    def put(self, host, s, ip, path_params, data, headers):
        s.connect((ip, 80))
        data_string = json.dumps(data)
        put_request = f"PUT /{path_params} HTTP/1.1\r\n" \
                      f"Host: {host}\r\n" \
                      f"User-Agent: {self.user_agent}\r\n" \
                      f"Accept: */*\r\n" \
                      f"Content-Length: {len(data_string)}\r\n" \
                      f"{headers}" \
                      f"\r\n" \
                      f"{data_string if data else ''}"
        request = Request(s)
        response = request.send(put_request)
        return response

    @INITIATE_HTTP
    def patch(self, host, s, ip, path_params, data, headers):
        s.connect((ip, 80))
        data_string = json.dumps(data)
        patch_request = f"PATCH /{path_params} HTTP/1.1\r\n" \
                        f"Host: {host}\r\n" \
                        f"User-Agent: {self.user_agent}\r\n" \
                        f"Accept: */*\r\n" \
                        f"Content-Length: {len(data_string)}\r\n" \
                        f"{headers}" \
                        f"\r\n" \
                        f"{data_string if data else ''}"
        request = Request(s)
        response = request.send(patch_request)
        return response

    @INITIATE_HTTP
    def delete(self, host, s, ip, path_params, headers):
        s.connect((ip, 80))
        delete_request = f"DELETE /{path_params} HTTP/1.1\r\n" \
                         f"Host: {host}\r\n" \
                         f"User-Agent: {self.user_agent}\r\n" \
                         f"Accept: */*\r\n" \
                         f"{headers}" \
                         f"\r\n"
        request = Request(s)
        response = request.send(delete_request)
        return response

    def resolve(self, host):
        self.ip = dns.resolve(host)
        return self.ip

    def make_host_from_url(self, host):
        if host.startswith("http://"):
            host = host[7:]
            path_params = ""
            if host.find("/") != -1:
                parsed_url = host.split("/")
                if len(parsed_url) > 0:
                    host = parsed_url[0]
                    path_params = "/".join(parsed_url[1:])
            return host, path_params
        else:
            Exception("Invalid URL")
            exit(1)

    def __str__(self):
        return f"HTTP client"

    def __repr__(self):
        return f"HTTP client"
