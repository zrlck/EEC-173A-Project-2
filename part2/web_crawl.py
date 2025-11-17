### This file crawls the top 100 sites using Selenium ###

import csv
import time
import os
import json
from browsermobproxy import Server
from selenium import webdriver

# intialize proxy
server = Server(r"C:\Users\klsnyder\EEC173A\EEC-173A-Project-2\part2\browsermob-proxy-2.1.4\bin\browsermob-proxy.bat", options={'port':8081})
server.start()
proxy = server.create_proxy()

# set up selenium
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--proxy-server={}".format(proxy.proxy))
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--headless')
driver = webdriver.Chrome(options=chrome_options)
driver.set_page_load_timeout(10)

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

for i in range(1000000):
    full_addr = "https://" + top100_arr[i]
    try:
        proxy.new_har(f"{top100_arr[i]}", options={'captureHeaders': True,'captureContent': True, 'captureCookies': True})
        har_directory = os.path.join("top100_harfiles", f"{top100_arr[i]}.har")
        driver.get(full_addr)
        time.sleep(0.8)
        with open(har_directory, "w") as f:
            f.write(json.dumps(proxy.har))
        success_count += 1
        if success_count == 100:
            break
    except Exception:
        print(f"{top100_arr[i]} error -> moving on")

# close all processes
print("Done!")
server.stop()
driver.quit()    

