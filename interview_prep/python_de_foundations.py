# Python DE Foundations — Topic 1: Generators & Iterators
# Exercises practiced: 2026-06-30

# ── Exercise 1 ── Basic generator ─────────────────────────────────────────────
# Write a generator that yields the square of every integer from 1 to n.
# Print the first 4 values using next().

def squares(n):
    i = 1
    while i <= n:
        yield i * i
        i += 1

g = squares(4)
print(next(g))  # 1
print(next(g))  # 4
print(next(g))  # 9
print(next(g))  # 16


# ── Exercise 2 ── Generator expression ────────────────────────────────────────
# Sum all even numbers in range(1_000_000) using a generator expression (one line).

numbers = range(1_000_000)
result = sum(i for i in numbers if i % 2 == 0)
print(result)  # 249999500000


# ── Exercise 3 ── Chunked file reader (DE core) ────────────────────────────────
# Generator that yields chunksize lines at a time from a file.
# Loop over it and print how many lines are in each chunk.

import itertools

def read_in_chunks(filepath, chunksize):
    with open(filepath) as f:
        while True:
            chunk = list(itertools.islice(f, chunksize))
            if not chunk:
                break
            yield chunk

# Usage (needs a real file):
# for c in read_in_chunks('myfile.txt', 10000):
#     print(len(c))


# ── Exercise 4 ── Spot the bug ─────────────────────────────────────────────────
# Bug: return exits after the first even number. Fix: replace return with yield.

def evens_up_to(n):
    for i in range(n):
        if i % 2 == 0:
            yield i          # was: return i

for val in evens_up_to(10):
    print(val)  # 0 2 4 6 8


# ══════════════════════════════════════════════════════════════════════════════
# Topic 2: Memory-Efficient Patterns
# Exercises practiced: 2026-06-30
# ══════════════════════════════════════════════════════════════════════════════

import pandas as pd

# ── Exercise 1 ── Chunked aggregation ─────────────────────────────────────────
# Read 10M-row sales.csv in chunks of 50,000. Compute total revenue per country
# across all chunks. Print top 3 countries by revenue.

results = []
for chunk in pd.read_csv('sales.csv', chunksize=50_000):
    results.append(chunk.groupby('country')['revenue'].sum())

top3 = pd.concat(results).groupby(level=0).sum().nlargest(3)
print(top3)

# Pattern: chunk → partial aggregate → collect → combine (same as MapReduce)
# level=0 = group by index (country became the index after groupby+sum on Series)
# Alternative: .sort_values(ascending=False).head(3)


# ── Exercise 2 ── dtype downcast ──────────────────────────────────────────────
# Downcast each column to the most memory-efficient dtype.
# customer_id: int, max 99999 → int32 (int16 only holds to 32,767)
# age: int, 0–120         → int8  (holds -128 to 127)
# country: string, 50 unique values → category
# score: float, 2 decimals → float32

df = pd.read_csv('customers.csv')
df['customer_id'] = df['customer_id'].astype('int32')
df['age']         = df['age'].astype('int8')
df['country']     = df['country'].astype('category')
df['score']       = df['score'].astype('float32')
print(df.memory_usage(deep=True).sum())

# category dtype: stores integer codes + one lookup table instead of repeating
# the full string per row — big savings for low-cardinality string columns.


# ── Exercise 3 ── Parquet read/write ──────────────────────────────────────────
# Read only 3 columns from a 200-column Parquet file (column pruning).
# Save a DataFrame back to Parquet with Snappy compression.

df = pd.read_parquet('transactions.parquet', columns=['user_id', 'amount', 'transaction_date'])
df.to_parquet('transactions.parquet', index=False, compression='snappy')

# Parquet reads only the needed columns off disk (columnar format).
# CSV would read all 200 columns and discard 197.
# In Spark, Parquet also enables predicate pushdown — filters hit storage
# before data reaches the executor.


# ── Key distinctions ───────────────────────────────────────────────────────────
# Iterable  — has __iter__()  — can be looped (list, str, file)
# Iterator  — has __next__() — stateful, one-directional
# Generator — iterator created with yield (or generator expression)
#
# DE relevance: pd.read_csv(filepath, chunksize=N) returns a generator of
# DataFrames — same lazy pattern as read_in_chunks above.
