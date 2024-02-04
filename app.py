import dns

ip = dns.resolve("www.gmail.com", dns_server_ip="1.1.1.1", dns_server_port=53)
print(ip)