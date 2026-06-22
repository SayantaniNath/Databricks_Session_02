"""
Exercise 4 — Average price per coin (Pandas warm-up)
-----------------------------------------------------

GOAL:
    Write a function `average_price_per_coin(path)` that:
      1. Reads the JSONL file at `path`
      2. Returns a DICT where each key is a coin name and each value is the
         AVERAGE of its price_usd values across the file.

EXAMPLE:
    For sample.jsonl (3 coins, 2 records each), you should get something like:
        {
          "bitcoin":  67506.785,
          "ethereum": 3182.75,
          "solana":   149.985,
        }

WHY THIS EXERCISE:
    You're about to start Kaggle Pandas. In Pandas, this is literally one line:
        df.groupby("coin")["price_usd"].mean()
    But that line will feel like magic if you've never built it by hand.
    Today you build it by hand. Tomorrow Pandas will feel obvious.

APPROACH (try first — peek only if stuck):
    Two clean approaches. Pick whichever clicks for you:

    APPROACH A — collect lists, then average:
        Build a dict like  {"bitcoin": [67123.45, 67890.12], "ethereum": [...]}
        Then loop through it and replace each list with sum(lst) / len(lst).

    APPROACH B — track running sum and count:
        Build two dicts: totals = {"bitcoin": 138013.57, ...}
                         counts = {"bitcoin": 2, ...}
        Then at the end, divide totals[coin] / counts[coin] for each coin.

HINTS:
    - `dict.setdefault(key, default_value)` is handy: returns the existing value
      if the key is present, else inserts default_value and returns it.
      Example:  totals.setdefault("bitcoin", 0)
    - You already know how to read the file from Exercises 1 and 2 — same pattern.

WHEN DONE:
    Print the result. Run with:
        python practice_04.py
"""

# Your code below. Type it yourself. Take your time.

import json
def average_price_per_coin(path):
    totals = {}
    counts = {}
    with open(path, "r") as f:
        for line in f:
            record = json.loads(line)
            coin = record["coin"]
            price = record["price_usd"]
            if coin in totals :
                totals[coin] += price
            else :
                totals[coin] = price
            if coin in counts :
                counts[coin] += 1
            else :
                counts[coin] = 1
    averages = {}
    for coin in totals:
        averages[coin] = totals[coin] / counts[coin]
    return averages

if __name__ == "__main__":
    sample_path = "/Users/sayantaninath/Downloads/finflow/data/raw/crypto/sample.jsonl"
    print(average_price_per_coin(sample_path))
              

