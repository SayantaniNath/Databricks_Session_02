"""
Pandas Lesson 1 — Part 6: Reading your FinFlow JSONL into a DataFrame
----------------------------------------------------------------------

Yesterday you wrote ~10 lines of raw Python to read a JSONL file.
Pandas does it in ONE line.

RUN WITH:
    ~/myenv/bin/python ~/Downloads/finflow/practice_pandas_02.py
"""

import pandas as pd

path = "/Users/sayantaninath/Downloads/finflow/data/raw/crypto/sample.jsonl"

# One line. Same file you used for Exercises 1, 2, and 4.
df = pd.read_json(path, lines=True)

print(df)
  # Exercise 1 replay — highest price record
print(df.loc[df["price_usd"].idxmax()])

  # Exercise 2 replay — records on 2026-05-15
print(df[df["fetched_at"].dt.date.astype(str) == "2026-05-15"])

  # Exercise 4 replay — average price per coin
print(df.groupby("coin")["price_usd"].mean())
