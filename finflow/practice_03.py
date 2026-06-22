"""
Exercise 3 — Fetch one coin's price from CoinGecko
---------------------------------------------------

GOAL:
    Write a function `fetch_price(coin_id)` that:
      1. Calls the CoinGecko "simple price" API for that coin (in USD)
      2. Returns the price as a number (float)

THE API:
    URL:    https://api.coingecko.com/api/v3/simple/price
    Params: ids=<coin_id>   (e.g. "bitcoin")
            vs_currencies=usd

    Example response (JSON):
        {"bitcoin": {"usd": 67234.12}}

    So for the request:
        GET https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd

STEPS:
    1. import requests
    2. Build a `params` dict with "ids" and "vs_currencies" keys
    3. Call requests.get(url, params=params, timeout=10)
    4. Convert the response to a Python dict with response.json()
    5. Reach into the dict with data[coin_id]["usd"] to get the price
    6. Return that number

HINTS:
    - timeout=10 means "wait up to 10 seconds, then give up"
    - response.json() turns the JSON body into a dict (like json.loads did)
    - The outer key is whatever coin_id you passed in

HOW TO RUN:
    Use your venv's python so `requests` is available:
        ~/myenv/bin/python practice_03.py
"""

# Your code below. Type it yourself — peek at hints only if stuck.

import requests
"""import json -- json is not needed here since requests has a built-in .json() method"""

def fetch_price(coin_id):
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids" : coin_id,
        "vs_currencies" : "usd"
    }
    response = requests.get(url, params=params, timeout=10)
    data = response.json()
    return data[coin_id]["usd"]

print(fetch_price("bitcoin"))
