import dns
from http import HTTP
request = HTTP()
res = request.get("http://jsonplaceholder.typicode.com/todos/1", headers={"Accept": "application/json"})
print(res.json)