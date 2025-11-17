# this is our DNS client that will select our root, our TLD, and our authoritative DNS servers to resolve our domain
# which will send DNS queries over UDP, may include retries and timeouts, and parse DNS responses (working on it today)

import socket
import time

from dns_tools import build_dns_header as build_dns_query, parse_dns_header, skip_questions, parse_dns_answers, goto_next_serverip

# included list of root servers that we will use to start our DNS resolution process
root_servers = ["198.41.0.4","170.247.170.2","192.33.4.12","199.7.91.13","192.203.230.10","192.5.5.241","192.112.36.4","198.97.190.53","192.36.148.17","192.58.128.30","193.0.14.129","199.7.83.42","202.12.27.33"]

def send_dns_query(ip_server, server_query, timeout = 5):
    # create the UDP socket (this is for the client side)
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.settimeout(timeout)

    try: # trying to send and receive data
        time_start = time.time() # start timer

        udp_socket.sendto(server_query, (ip_server, 53)) # DNS query to the server on port 53 (standard DNS port)
        dns_response, dont_care = udp_socket.recvfrom(4096) # i'm trying 4KB, but may lower it later if needed

        time_end = time.time() # end timer
        udp_socket.close() # close the socket after we're done with it
        return dns_response, (time_end - time_start) # return the DNS response and the total time taken for the query

    except socket.timeout: # i included a timeout exception to handle cases where the server doesn't respond
        udp_socket.close()
        return None, None  # retry with next server


def query_dns_server(ip_server, nameof_domain):
    dns_query = build_dns_query(nameof_domain) # build the DNS query for the domain name (raw bytes)
    dns_response, timeof_query = send_dns_query(ip_server, dns_query) # send the DNS query to the server and get the response

    if dns_response is None:
        return None, None, None, None, None # server didn't respond, return Nones for ALL values

    # parse header (i'm allocating 12 bytes fro this)
    infof_header = parse_dns_header(dns_response)
    qdcount = infof_header['qdcount']
    ancount = infof_header['ancount']
    nscount = infof_header['nscount']
    arcount = infof_header['arcount']
    # this block will help us parse the DNS response furthe by skipping the question section and then parsing the answer section

    # skip questions section
    offset = 12 # becuase header is 12 bytes
    offset = skip_questions(dns_response, offset, qdcount)

    # parse answers section
    answer_section, authority_section, additional_section, after_offset = parse_dns_answers(dns_response, offset, ancount, nscount, arcount) # not using after_offset for now, we will implement it later in case we need it

    return infof_header, answer_section, authority_section, additional_section, timeof_query # will use them for dns_tools


# will work on next fnc tomorrow

def iteration_dns_resolver(nameof_domain):
    next_ip_tld_server = None

    for ip_root in root_servers:
        # calling our query_dns_server function to send query to root server
        root_header, root_answers, root_authority, root_additional, root_time = query_dns_server(ip_root, nameof_domain)

        if root_header is None:
            continue  # server didn't respond, try next

        # check next ip server to go to (has to be TLD server)
        next_ip_tld_server = goto_next_serverip(root_authority, root_additional)

        if next_ip_tld_server is not None:
            break # found a TLD server, break out of the loop

    if next_ip_tld_server is None:
        return None

    # query to TLD server, then get the authoritative server, then query to authoritative server
    headerof_tld, answersof_tld, authorityof_tld, additionalof_tld, timeof_tld = query_dns_server(next_ip_tld_server, nameof_domain)

    if headerof_tld is None:
        return None

    authoritative_ip = goto_next_serverip(authorityof_tld, additionalof_tld)

    if authoritative_ip is None:
        return None

    headerof_auth, answersof_auth, authorityof_auth, additionalof_auth, timeof_auth = query_dns_server(authoritative_ip, nameof_domain)

    if headerof_auth is None:
        return None

    # final answers from authoritative server
    ip_final = None
    for answer in answersof_auth: # iterate through each answer record (i just need to finish this part)
        if answer['type'] == 1: # record type A (this comes from the IPv4 address record)
            ip_final = ".".join(str(b) for b in answer['data'])  # decode A record bytes
            break
        if answer['type'] == 5: # CNAME record
            cname = answer['data']
            return iteration_dns_resolver(cname) 

    return ip_final, root_time # finished dns_clent, now need to work on html_tools so that we can fetch webpages using this resolver
