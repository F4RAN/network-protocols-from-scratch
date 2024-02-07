
from http import HTTP
request = HTTP()
# Get Request
# get_res = request.get("http://jsonplaceholder.typicode.com/todos/1", headers={"Accept": "application/json"})
# print(get_res.json)

# Post Request
post_res = request.post("http://jsonplaceholder.typicode.com/posts", headers={"Content-Type": "application/json"}, data={"title": "foo", "body": "bar", "userId": 1})
print(post_res.json)
