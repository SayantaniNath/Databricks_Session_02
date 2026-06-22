"""
Generates two JSONL files for the salting exercise:
  - transactions_skewed.jsonl  (~50,000 rows, 80% are merchant_id=MEGACORP)
  - merchants.jsonl             (5 merchants — small lookup table)

Run once:  python generate_skewed_data.py
"""
import json
import random
import os

random.seed(42)

# --- merchants (small lookup table) ---
merchants = [
    {"merchant_id": "MEGACORP",  "name": "MegaCorp Global",   "category": "retail"},
    {"merchant_id": "SMALLBIZ",  "name": "Small Biz Co",      "category": "food"},
    {"merchant_id": "TECHCO",    "name": "TechCo Ltd",        "category": "electronics"},
    {"merchant_id": "FASTFOOD",  "name": "FastFood Inc",      "category": "food"},
    {"merchant_id": "LUXESHOP",  "name": "LuxeShop",         "category": "fashion"},
]

# --- transactions (skewed: 80% MEGACORP) ---
# Distribution mimics a real hot-key problem
weights = [0.80, 0.05, 0.07, 0.05, 0.03]
merchant_ids = [m["merchant_id"] for m in merchants]

out_dir = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(out_dir, "transactions_skewed.jsonl"), "w") as f:
    for i in range(50_000):
        merchant = random.choices(merchant_ids, weights=weights, k=1)[0]
        # json.dumps() converts the Python dict to a JSON text string.
        # Files can only store text, not Python objects.
        # Without this, writing the dict directly would produce Python's repr
        # (single quotes, not valid JSON) which PySpark cannot parse.
        # Flow: Python dict → json.dumps() → text string → written to file
        #       PySpark reads the text back and parses it into a DataFrame.
        # The "\n" at the end makes it JSONL: one JSON object per line.
        f.write(json.dumps({
            "txn_id":      f"TXN{i:07d}",
            "merchant_id": merchant,
            "amount":      round(random.uniform(1.0, 5000.0), 2),
            "currency":    random.choice(["USD", "EUR", "GBP"]),
            "status":      random.choice(["completed", "pending", "failed"]),
        }) + "\n")

with open(os.path.join(out_dir, "merchants.jsonl"), "w") as f:
    for m in merchants:
        f.write(json.dumps(m) + "\n")

print("Done.")
print(f"  transactions_skewed.jsonl — 50,000 rows (80% MEGACORP)")
print(f"  merchants.jsonl           — 5 rows")
