# using a main file to fetch tmz.com using our custom DNS resolver and HTTP client, though about combining everything in one file but it would be messy

from html_tools import custom_dns_get_http

def main():
    server_domain = "tmz.com"
    server_path = "/"

    # run our custom DNS + HTTP client
    http_response, http_rtt, resolved_ip = custom_dns_get_http(server_domain, server_path)

    if http_response is None:
        print("TMZ could not be fetched (DNS or HTTP failed).")
        return

    print(f"Resolved {server_domain} to IP: {resolved_ip}")
    print(f"HTTP RTT: {http_rtt:.6f} seconds")

    # print only part of the HTML so the terminal doesn't overflow, this is just for demo purposes
    try:
        decoded = http_response.decode(errors="ignore")
        print("\n--- HTML Response (first 500 chars) ---\n")
        print(decoded[:500])
        print("\nEnd")
    except: # using it for exeptions in handling decoding errors
        print("Couln't resolve fetch.")

if __name__ == "__main__":
    main()
