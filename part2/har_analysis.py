import json
import pprint
import os
from urllib.parse import urlparse
from collections import Counter


har_directory = "top100_harfiles"
cookies_list = list()
request_urls = list()

# top10_cookies = [0] * 10

# IDENTIFY TOP 10 THIRD PARTY DOMAINS

for har_file in os.listdir(har_directory):
    harfile_SLD = har_file.replace(".har", "")
    with open(os.path.join(har_directory,har_file), "r", encoding="utf-8") as f:
        data = json.load(f)

    entries = data["log"]["entries"]
    
    for entry in entries:
        request_url = entry["request"]["url"]
        parsed = urlparse(request_url)
        if not parsed.netloc.endswith(harfile_SLD):
            request_urls.append(f"{parsed.netloc}")

# IDENTIFY TOP 10 COOKIES

for har_file in os.listdir(har_directory):
    with open(os.path.join(har_directory,har_file), "r", encoding="utf-8") as f:
        data = json.load(f)

    entries = data["log"]["entries"]
    
    for entry in entries:
        try:
            request_cookies = entry["request"]["cookies"]
            response_cookies = entry["response"]["cookies"]
        except Exception:
            print("cookie retrieval failed")
            continue
        for cookie in request_cookies + response_cookies:
            # only collect third-party domains
            harfile_SLD = har_file.replace(".har", "")
            if cookie.get("domain","").endswith(harfile_SLD):
                continue
            cookies_list.append(cookie["name"])

# store and print the top 10 cookies in an array

# type cast cookies set to list

# cookies_list = list(cookies_set)

cookie_counter = Counter(cookies_list)
domain_counter = Counter(request_urls)

top10_domains = Counter.most_common(domain_counter, 10)
top10_cookies = Counter.most_common(cookie_counter, 10)

# top10_cookies = list(cookies_set)[:10]
print("\nTop 10 Domains:\n")
pprint.pprint(top10_domains)
print("\nTop 10 Cookies:\n")
pprint.pprint(top10_cookies)

