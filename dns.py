# Based on RFC 1034, RFC 1035: https://www.ietf.org/rfc/rfc1034.txt, https://www.ietf.org/rfc/rfc1035.txt

import socket
import random
import struct


def resolve(domain, dns_server_ip="8.8.8.8", dns_server_port=53):
    try:
        # DNS header
        # Google public DNS server IP and port
        transaction_id = random.randint(0, 65535)  # 16 bit identifier to match request and response
        flags = 0x0100  # Flags specifying standard query
        questions = 0x0001  # Number of questions in packet
        # Query parameters
        query_type = '\01'  # Type A = IPv4 address record: RFC 3.2.2 ==> 0x001
        query_class = '\01'  # IN = Internet class: RFC 3.2.4 ==> 0x001

        # Domain name encoding
        """
        Example:
        b'5O \x01\x00 \x00\x01 \x00\x00 \x00\x00 \x00\x00 \x03www\x06google\x03com\x00\x00\x01\x00\x01'

            50 - This is the transaction ID: hex(transaction_id) then split to two 2 bytes segment
            \x01\x00 - The DNS flags, 0x0100 indicates standard query
            \x00\x01 - Number of questions is 1
            3x \x00\x00 - Answer RRs, Authority RRs, Additional RRs
            \x03www\x06google\x03com - The encoded domain name www.google.com ( \x03,\x06 and \x03 Represent the length of each 
                                       label in the domain name as per the DNS format specifications.)
            \x00 - Terminating null byte 
            \x00 - Terminating null byte 
                1 ) The first null byte terminates the domain name string. This is required as per DNS format to mark the end of
                 the domain name. ( If we have many domains, first one \x00 repeat end of each domain )
                2 ) The second null byte provides padding and alignment before specifying the query type and class.
            A - Query type A for IPv4 address
            \x00 - Padding byte
            IN - Query class IN for internet
        """

        segments = domain.split('.')
        query = ''.join(chr(len(s)) + s for s in segments) + '\0'  # Length prefix + data
        query += '\0' + query_type + '\0' + query_class  # Type and class with padding

        # Construct DNS packet header

        dns_query_packet = struct.pack('!HHHHHH', transaction_id, flags, questions, 0, 0, 0)
        """
        !: Applies big-endian packing across all fields. \x85\xa8 => [(Smaller in First Byte)\x85,(Bigger in Second Byte)\xa8]
        H: Indicates a 2-byte unsigned short integer
        0,0,0:Answer RRs,Authority RRs,Additional RRs

        """
        # Full packet = header + question section
        dns_query_packet += bytes(query, 'utf-8')
        # Create UDP socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        s.settimeout(10)
        # Send the dns_query_packet to the DNS server
        try:
            s.sendto(dns_query_packet, (dns_server_ip, dns_server_port))

            # Allow 512 bytes in response buffer
            buffer_size = 512

            # Receive response packet from DNS server
            dns_response, address = s.recvfrom(buffer_size)
        except socket.timeout:
            Exception("Timeout")
            exit(1)

        # Extract response record
        # Parse header
        """
        Example:
        b'B\x8a \x81\x80 \x00 \x01 \x00\x01\x00\x00\x00\x00 \x03www\x06google\x03com\x00 \x00\x01 \x00\x01 \xc0\x0c \x00\x01 \x00\x01 \x00\x00\x00< \x00\x04\xd8\xef&x'
        [0:2]: ID: B81 ==> ASCII B = HEX 42      
                                 2nd Byte    1st Byte
        [2:4]: Flags: 0x8180 => (1000 0001) (1000 0000)
            1st byte:
            1 000000 - Response (QR) bit 
            0 000    - Opcode: Standard query
            0 - Z bits   
            2nd byte:
            1 0000000 - Recursion Desired (RD)
            1 0000001 - Authoritative Answer (AA)  
            0 0000 - Reply code: 0 (No error)
        [4] in Response question count is 0
        [5] in Response answer count is 1
        [6:11]: Unused bytes (should be 0)
        """
        id = struct.unpack('!H', dns_response[:2])[0]
        flags = struct.unpack('!H', dns_response[2:4])[0]
        qdcount = dns_response[4]
        ancount = dns_response[5]

        # Parse question section
        """
        end_index: go ahead to find end \x00 domain delimiter
        qname_part: is domain part
        after_domain: is after domain part
        after_domain[0]: is separator between domains part and other options
        after_domain[1:3]: qtype = A = \x00 \x01
        after_domain[3:5]: qclass = IN = \x00 \x01                    
        """
        start_of_domain_index = 12  # Skip header
        end_index = dns_response[start_of_domain_index:].index(b'\x00')
        end_of_domain_index = start_of_domain_index + end_index
        qname_part = dns_response[start_of_domain_index:end_of_domain_index]
        qname = qname_part
        after_domain = dns_response[end_of_domain_index:]
        qtype, qclass = struct.unpack('!HH', after_domain[1:5])
        answers_index = end_of_domain_index + 5
        question = {
            'qname': qname,
            'qtype': qtype,
            'qclass': qclass
        }
        # Parse answer RRs
        """
        after_domain[5:7]: name = \xc0\x0c = Pointer to offset 12 to reuse/refer to that name again instead of reencoding 
                            the full domain name.
        after_domain[7:9]: rtype = 1 for A record, 2 for NS record etc
        after_domain[9:11]: rclass = 1 for Internet (IN), other values indicate things like CHAOS or Hesiod
        after_domain[11:15] ttl = Time-to-live in seconds, provides caching guidance to the clients
        after_domain[15:17] rdlen = Length of the resource data section
        after_domain[17:21] rdata = each hex byte show one section of ip we must convert them to integer
        """
        answers = dns_response[answers_index:]
        name, rtype, rclass, ttl, rdlen = struct.unpack('!HHHLH', answers[0:12])
        rdata = answers[12:12 + rdlen]
        ip = str(int(rdata[0])) + '.' + str(int(rdata[1])) + '.' + str(int(rdata[2])) + '.' + str(int(rdata[3]))
        answer = {
            'name': name,
            'rtype': rtype,
            'rclass': rclass,
            'ttl': ttl,
            'rdlen': rdlen,
            'rdata': rdata
        }
        # Construct final result
        result = {
            "id": id, "flags": flags,
            "questions": questions,
            "answers": answers
        }

        # Close socket
        s.close()
        return ip
    except Exception as e:
        print(e)
        return None
