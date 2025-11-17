# using a main file to fetch tmz.com using our custom DNS resolver and HTTP client, though about combining everything in one file but it would be messy
# it takes care of dns_client, dns_tools, and html_tools
from html_tools import custom_dns_get_http

def main():
    server_domain = "tmz.com"
    server_path = "/"

    # run our custom DNS + HTTP client
    http_response, http_rtt, resolved_ip, dns_rtt = custom_dns_get_http(server_domain, server_path)

    if http_response is None: # making sure we got a response
        print("TMZ could not be fetched (DNS or HTTP failed).")
        return

    print(f"Resolved {server_domain} to IP: {resolved_ip}")
    print(f"DNS RTT: {dns_rtt:.6f} seconds")
    print(f"HTTP RTT: {http_rtt:.6f} seconds")

    # print only part of the HTML so the terminal doesn't overflow, this is just for demo purposes i am doing 500 characters
    try:
        decoded = http_response.decode(errors="ignore")
        print("\nHTML Response (first 500 characters)\n")
        print(decoded[:500])
        print("\nEnd")

        with open("tmz_fetched.html", "w", encoding="utf-8") as f:
            f.write(decoded)
    except: # i am using it for exeptions in handling decoding errors
        print("Couldn't resolve fetch.")

if __name__ == "__main__":
    main()
