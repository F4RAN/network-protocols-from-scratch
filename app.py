import dns
from http import HTTP
request = HTTP()
res = request.get("http://example.com")
print(res.body)