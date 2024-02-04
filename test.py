import dns.resolver

domain = "www.google.com"

# Create the DNS resolver object
my_resolver = dns.resolver.Resolver() 

# Use Google public DNS server 
my_resolver.nameservers = ["8.8.8.8"]

try:
    # Resolve A record to get IP 
    answers = my_resolver.resolve(domain, 'A')  
    for data in answers:
        print(f'{domain} IP address is: {data}')

except dns.exception.DNSException as error:
    print(f"DNS query failed: {error}")

