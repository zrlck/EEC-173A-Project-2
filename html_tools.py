# third part of the project, htlm_tools which will fetch webpages using our DNS resolver
import socket
import time

from dns_client import iteration_dns_resolver

def build_and_get_http(server_host, server_path = "/"):
    # build the HTTP GET request
    request_server_lines = f"GET {server_path} HTTP/1.1\r\nHost: {server_host}\r\nUser-Agent: MyDNSClient/1.0\r\nConnection: close\r\n\r\n"
    return request_server_lines.encode() # return as bytes

def custom_dns_get_http(server_domain, server_path = "/"):
    ip_address = iteration_dns_resolver(server_domain) # use our DNS resolver to get the IP address
    if ip_address is None:
        print ("Not able to resolve domain.") # rising error message if domain cannot be resolved
        return None, None, None
    print(f"DNS resolved {server_domain} to {ip_address}") # this is just for info purpose

    # now the important part is to create a TCP socket and connect to the server
    http_tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    http_tcp_socket.settimeout(10) # set timeout for socket operations, i will change this later if needed

    # now we measure RTT for TCP connection
    time_start = time.time() # start timer

    try:
        http_tcp_socket.connect((ip_address, 80)) # connect to server on port 80 whici is standard HTTP port
        http_request = f"GET {server_path} HTTP/1.1\r\nHost: {server_domain}\r\nUser-Agent: MyDNSClient/1.0\r\nConnection: close\r\n\r\n".encode () # build HTTP GET request
        http_tcp_socket.sendall(http_request) # send the HTTP GET request to the server

        # now we will receive the HTTP response from the server
        http_response_onchunks = [] # list to hold chunks of response
        while True:
            chunk_data = http_tcp_socket.recv(4096) # receive data in 4KB chunks
            if not chunk_data:
                break # no more data
            http_response_onchunks.append(chunk_data)

        time_end = time.time() # end timer

        # this block from the time start to time end is the RTT for TCP connection and data transfer

        # now we close the socket 
        http_tcp_socket.close()

        # for full response we join all chunks
        full_http_response = b''.join(http_response_onchunks)
        http_response_time = time_end - time_start # total time taken for HTTP request and response

        return full_http_response, http_response_time, ip_address # return the full HTTP response, time taken, and IP address
    
    except Exception as e: # i am rising a general exception to catch any errors during socket operations 
        print(f"Error during HTTP communication: {e}")
        http_tcp_socket.close()
        return None, None, ip_address