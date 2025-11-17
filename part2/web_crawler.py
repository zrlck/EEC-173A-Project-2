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
        #print(row)
        top100_arr[i] = row[1]
        #print(f"#{i+1} site is: {top100_arr[i]}")
        i += 1
        # if row[0] == "1000000":
        #     break

# now, top100_arr is an array of the top 100 sites
# top100_arr = ["google.com" , "facebook.com" , ...]

### STEP 2: VISIT EACH SITE AND COLLECT HAR FILES  ###

# collect HTTP traffic in HAR files, store in top100_harfiles
success_count = 0

with sync_playwright() as p:
    # launches chromium browser in headless mode
    browser = p.chromium.launch()
    for i in range(1000000):
        full_addr = "https://" + top100_arr[i]
        try:
                # starts recording HTTP traffic
                context = browser.new_context(record_har_path=f"top100_harfiles/{top100_arr[i]}.har", ignore_https_errors=True)
                # open page within the active context
                page = context.new_page()
                # navigate to site
                page.goto(f"{full_addr}", timeout=10000)

                context.close()

                success_count += 1
                print(f"{top100_arr[i]} was a success! Currently {success_count} Successes")
                if success_count == 5:
                    break
        except Exception:
            print(f"{top100_arr[i]} error -> moving on")
    browser.close()
# close browser
print("Done!")


