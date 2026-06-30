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


# ── Key distinctions ───────────────────────────────────────────────────────────
# Iterable  — has __iter__()  — can be looped (list, str, file)
# Iterator  — has __next__() — stateful, one-directional
# Generator — iterator created with yield (or generator expression)
#
# DE relevance: pd.read_csv(filepath, chunksize=N) returns a generator of
# DataFrames — same lazy pattern as read_in_chunks above.
