"""
Exercise 1 — Find the highest crypto price
-------------------------------------------

GOAL:
    Write a function `highest_price(path)` that:
      1. Opens the JSONL file at `path`
      2. Reads each line (each line is a JSON object)
      3. Returns the SINGLE record (a dict) with the largest "price_usd"

SAMPLE DATA:
    ~/Downloads/finflow/data/raw/crypto/sample.jsonl
    Each line looks like:
      {"coin": "bitcoin", "symbol": "btc", "price_usd": 67123.45, "fetched_at": "..."}

HINTS (read only when stuck — try first!):
    - You'll need the `json` module: `import json`
    - To turn one line of text into a dict: `json.loads(line)`
    - Track the best record as you loop. Start with `best = None`.
    - Don't worry about edge cases (empty file, etc.) — keep it simple.

WHEN DONE:
    Call your function at the bottom and `print(...)` the result.
    Run with: python practice_01.py
"""

# Your code starts below this line.
# Take your time — type it yourself. I'm right here if you get stuck.

import json


def highest_price(path):

    best = None
    with open(path, "r") as f:
        for line in f:
            record = json.loads(line)
            if best is None or record["price_usd"] > best["price_usd"]:
                best = record
    return best

if __name__ == "__main__":
    sample_path = "/Users/sayantaninath/Downloads/finflow/data/raw/crypto/sample.jsonl"
    print(highest_price(sample_path))