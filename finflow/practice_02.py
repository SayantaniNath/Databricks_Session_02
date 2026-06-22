"""
Exercise 2 — Filter records by date
------------------------------------

GOAL:
    Write a function `records_on_date(path, date_str)` that:
      1. Opens the JSONL file at `path`
      2. Reads each line (each line is a JSON object)
      3. Returns a LIST of records whose "fetched_at" starts with `date_str`

EXAMPLE:
    records_on_date(sample_path, "2026-05-15")
    → returns 3 records (the 3 with fetched_at starting "2026-05-15...")

SAMPLE DATA (same file as Exercise 1):
    ~/Downloads/finflow/data/raw/crypto/sample.jsonl
    Each line:
      {"coin": "...", "symbol": "...", "price_usd": ..., "fetched_at": "2026-05-15T10:00:00Z"}

HINTS (try first — only peek if stuck):
    - Start with an empty list: `results = []`
    - For each record, check if record["fetched_at"].startswith(date_str)
    - If it matches, append the record to your list
    - Return the list at the end

WHEN DONE:
    Test both dates and print the results:
      python practice_02.py
"""

# Your code starts below.
# Don't rush. Type it yourself.

import json

def records_on_date(path, date_str):
    results = []
    with open(path, "r") as f:
        for line in f:
            record = json.loads(line)
            if record["fetched_at"].startswith(date_str):
                results.append(record)
    return results

if __name__ == "__main__":
    sample_path = "/Users/sayantaninath/Downloads/finflow/data/raw/crypto/sample.jsonl"
    print(records_on_date(sample_path, "2026-05-15"))
    print(records_on_date(sample_path, "2026-05-16"))
