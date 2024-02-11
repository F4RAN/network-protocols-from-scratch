from http_modules.http import HTTP

request = HTTP()
# Get Request
get_res = request.get("http://jsonplaceholder.typicode.com/todos/1", headers={"Accept": "application/json"})
print(get_res.json)

# Post Request post_res = request.post("http://jsonplaceholder.typicode.com/posts", headers={"Content-Type":
# "application/json"}, data={"title": "foo", "body": "bar", "userId": 1}) print(post_res.json)

# Put Request
# put_res = request.put("http://jsonplaceholder.typicode.com/posts/1", headers={"Content-Type": "application/json"},
#                       data={"title": "foo"})
# print(put_res.json)

# Patch Request
# patch_res = request.patch("http://jsonplaceholder.typicode.com/posts/1", headers={"Content-Type": "application/json"},
#                           data={"title": "foo"})
# print(patch_res.json)




# Delete Request
# delete_res = request.delete("http://jsonplaceholder.typicode.com/posts/1")
# print(delete_res.json)
