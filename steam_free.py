#!/usr/bin/python3
import sys
import time
import json
import requests

# config
asf = "localhost:1242"
bot_name = "ASF"

def divide_chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]

def get_free():
    data = requests.get(
        "http://api.steampowered.com/ISteamApps/GetAppList/v0001/", timeout=60).json()

    for gc in divide_chunks(data['applist']['apps']['app'], 512):
        retry = 0
        appids = ""
        price_data = None
        for g in gc:
            appids += str(g['appid']) + ','

        while (not price_data):
            if (retry == 3):
                print("failed to download data after 3 retries", flush=True)
                sys.exit(1)
            elif (retry >= 1):
                print("retrying download", flush=True)

            try:
                price_data = json.loads(requests.get(f"https://store.steampowered.com/api/appdetails?appids={appids}&filters=price_overview", timeout=60).text)
            except (json.JSONDecodeError, requests.RequestException) as e:
                print(e)
                price_data = None
                retry += 1
                time.sleep(10)

        for g in appids.split(",")[:-1]:
            if not price_data[g]['success'] == True:
                continue
            if len(price_data[g]['data']) == 0:
                continue

            if price_data[g]['data']['price_overview']['discount_percent'] == 100:
                tree = requests.get(f"https://store.steampowered.com/api/appdetails?appids={g}", timeout=60).json()[g]['data']
                name = tree['name']
                print(f"Found free game {name} {g}", flush=True)
                if asf:
                    print("Adding to Steam library")
                    for package in tree['package_groups'][0]['subs']:
                        if '100' in package['percent_savings_text']:
                            g = package['packageid']

                    r = requests.post(f"http://{asf}/api/command", json={'Command': f"!addlicense {bot_name} {g}"})
                    print(f"ASF: {r.json()['Result']}", flush=True)

get_free()
