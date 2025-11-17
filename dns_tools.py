# here we will create a DNS header for 12 bytes (will work on it today)
import struct 

def build_dns_header(domain_of_site): # in here we will build the DNS header
    # will chose a random ID for the DNS query
    random_id = 0x1234 # i will change htis later to be random

    # Flags set to standard query
    flags = 0x0100

    qdcount = 1 # we have one question
    ancount = 0 # no answers in query
    nscount = 0 # no authority records in query
    arcount = 0 # no additional records in query

    dns_header = struct.pack('>HHHHHH', random_id, flags, qdcount, ancount, nscount, arcount)

    # here we will convert the domain into DNS labels
    split_parts = domain_of_site.split('.')
    query_name = b''

    # this block will create the query name in DNS format
    for part in split_parts:
        query_name += struct.pack('B', len(part)) + part.encode()
    query_name += b'\x00' # null byte to end the query name

    # now we record A type and IN class
    question_type = struct.pack('>HH', 1, 1) # type A

    return dns_header + query_name + question_type # returning both the header and the question section


def parse_dns_header(data_of_site): # this block will parse the DNS header
    query_id, flags, qdcount, ancount, nscount, arcount = struct.unpack('>HHHHHH', data_of_site[:12]) # unpacking the first 12 bytes
    return {"id": query_id, "flags": flags, "qdcount": qdcount, "ancount": ancount, "nscount": nscount, "arcount": arcount}


# working on it today too

def skip_questions(data_of_site, offset, qdcount): # this block will skip the question section
    for dont_care in range(qdcount):
        offset = name_skip(data_of_site, offset)
        offset += 4 # skip type and class (2 bytes each)
    return offset # later used by name_skip


def name_skip(data_of_site, offset): # this block will skip over a domain name
    while True:
        length_of_label = data_of_site[offset]

        # pointer support (IMPORTANT)
        if (length_of_label & 0xC0) == 0xC0:
            return offset + 2

        if length_of_label == 0:
            return offset + 1 # to make sure we move past the null byte

        offset += 1 + length_of_label


def parse_dns_answers(data_of_site, offset, ancount, nscount, arcount): # we are parsing the answer, authority, and additional sections
    answer_section = [] 
    authority_section = []
    additional_section = []
    # so we have three sections to parse, and we will loop through all records

    total_records = ancount + nscount + arcount # making total records to parse

    for i in range(total_records): # loop through each record
        start_offset = offset
        offset = name_skip(data_of_site, offset)

        rtype, rclass, rttl, rdlength = struct.unpack('>HHIH', data_of_site[offset:offset+10])
        offset += 10 # move past type, class, ttl, rdlength

        rdata = data_of_site[offset:offset+rdlength]
        offset += rdlength

        record = {'name_offset': start_offset, 'type': rtype, 'class': rclass, 'ttl': rttl, 'rdlength': rdlength, 'data': rdata}

        # recording the record in the appropriate section based on its index
        if i < ancount:
            answer_section.append(record)
        elif i < ancount + nscount:
            authority_section.append(record)
        else:
            additional_section.append(record)
        # the statement i previously wrote is checking which section we are in based on the index i, this is really important to separate the records correctly

    return answer_section, authority_section, additional_section, offset # now return the sections and the new offset


def decode_resource_data(full_data, resource_data, record_type): # now we will decode the resource data based on its type
    if record_type == 1: # A record
        return '.'.join(str(b) for b in resource_data)
    
    if record_type == 2: # NS record
        return decode_domain_name(full_data, resource_data)
    
    if record_type == 5: # CNAME record
        return decode_domain_name(full_data, resource_data)
    
    return resource_data # if default


def decode_domain_name(full_data, resource_data): # this block will decode domain names from resource data
    # pointer for compressed names
    if (resource_data[0] & 0xC0) == 0xC0:
        offset = ((resource_data[0] & 0x3F) << 8) | resource_data[1]
        return name_read(full_data, offset)
    return "" # safety fallback


def name_read(full_data, offset): #
    labels = []
    while True:
        length_of_label = full_data[offset]

        if length_of_label == 0:
            break

        # now for pointer if (length_of_label & 0xC0) == 0xC0:
        if (length_of_label & 0xC0) == 0xC0:
            pointer_offset = ((length_of_label & 0x3F) << 8) | full_data[offset + 1]
            labels.append(name_read(full_data, pointer_offset))
            return '.'.join(labels)
        
        offset += 1
        labels.append(full_data[offset:offset + length_of_label].decode())
        offset += length_of_label

    return '.'.join(labels)


# now pick the next server ip from authority and additional sections
def goto_next_serverip(authority_section, additional_section):
    ns_domains = None

    for record in authority_section:
        if record['type'] == 2: # NS record
            ns_domains = record['data']  # raw, but matches your variable usage
            break

    if ns_domains is None:
        return None
    
    for record in additional_section:
        if record['type'] == 1: # A record
            return ".".join(str(b) for b in record['data']) # decode A record bytes and return IP
    
    return None # going to return None if no IP found
