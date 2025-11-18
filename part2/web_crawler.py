### This file crawls the top 100 sites using Selenium ###

import csv
import time
import os
import json
from playwright.sync_api import sync_playwright

    
### STEP 1: READ IN THE TOP 100 SITES ###

# 1,google.com
# 2,facebook.com
# 3,amazonaws.com

top100_arr = [0] * 1000000

with open("top-1m.csv", "r") as top100_file:
    i = 0
    website = csv.reader(top100_file, delimiter=",")
    for row in website:
        top100_arr[i] = row[1]
        i += 1

# now, top100_arr is an array of the top 100 sites
# top100_arr = ["google.com" , "facebook.com" , ...]

### STEP 2: VISIT EACH SITE AND COLLECT HAR FILES  ###

# collect HTTP traffic in HAR files, store in top100_harfiles
success_count = 0

bad_domains = ["nflxso.net", "vimeo.com", "ui.com", 
               "spotify.com", "akamaized.net", "tiktokcdn-us.com",
               "2mdn.net", "spo-msedge.net", "a2z.com",
               "miit.gov.cn", "b-msedge.net", "cdninstagram.com",
               "bytefcdn-ttpeu.com", "azureedge.net", "tiktokcdn.com",
               "doubleclick.net", "mail.ru", "root-servers.net", "netflix.com",
               "pinterest.com"]

os.mkdir("top100_harfiles")

with sync_playwright() as p:
    # launches chromium browser in headless mode
    browser = p.chromium.launch()
    for i in range(1000000):
        context = None
        full_addr = "https://" + top100_arr[i]
        try:
            # skip domains that cause program to hang
            if top100_arr[i] in bad_domains:
                print(f"Skipping bad domain: {top100_arr[i]}")
                continue
            if i % 5 == 0 and i > 0:
                    browser.close()
                    browser = p.chromium.launch()

            try:
                # starts recording HTTP traffic
                context = browser.new_context(record_har_path=f"top100_harfiles/{top100_arr[i]}.har", ignore_https_errors=True)
                # open page within the active context
                page = context.new_page()
                # set navigation timeout
                page.set_default_navigation_timeout(10000)
                # navigate to site and check if its user facing
                resource_response = page.goto(f"{full_addr}", timeout=10000)
                content_type = resource_response.headers.get("content-type","")
                if "text/html" not in content_type:
                    continue
                success_count += 1
                print(f"{top100_arr[i]} was a success! Currently {success_count} Successes")
            except Exception:
                print(f"{top100_arr[i]} error -> moving on")
            finally:
                if context:
                    try:
                        context.close()
                    except:
                        pass

            if success_count == 100:
                browser.close()
                break
        except Exception:
            print(f"{top100_arr[i]} error -> moving on")
            if context:
                try:
                     context.close()
                except:
                     pass
    
# close browser
print("Done!")


