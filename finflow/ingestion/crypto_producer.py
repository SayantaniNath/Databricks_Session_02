"""
============================================================================
Crypto price producer — CoinGecko API → local file → Kafka (optional).
============================================================================

WHAT THIS SCRIPT DOES (the big picture):
    1. Hits CoinGecko's free public REST API every 60 seconds and asks for
       the current price + 24h stats of six cryptocurrencies.
    2. Reshapes the nested JSON response into a flat list of records
       (one dict per coin), tagged with timestamp and source.
    3. Appends each batch as JSONL to a date-partitioned file on disk.
    4. Optionally publishes the same records to a Kafka topic so
       downstream consumers can react in real time.
    5. Sleeps and repeats, with retry logic for rate limits / network errors.

This pattern — fetch → normalize → fan-out (file + queue) — is the
standard shape of a streaming "producer" in a data-engineering pipeline.

Run directly:
    source ~/myenv/bin/activate
    cd ~/finflow
    python -m ingestion.crypto_producer

Enable Kafka:
    USE_KAFKA=true python -m ingestion.crypto_producer
============================================================================
"""

# ===========================================================================
# IMPORTS
# ===========================================================================
import json        # convert Python dicts <-> JSON text (for API parsing & file writing)
import logging     # structured logging — better than print() for long-running services
import os          # filesystem helpers (paths, mkdir, environment variables)
import sys         # access to sys.path so we can tweak Python's import search list
import time        # time.sleep() to pause between fetches

# `datetime` represents an instant in time; `timezone.utc` lets us tag it
# as UTC. We use UTC everywhere because servers run in many timezones and
# UTC is the one unambiguous "now".
from datetime import datetime, timezone

# `requests` is the de-facto standard HTTP client for Python.
# It's a third-party library (installed via pip), much friendlier than
# the built-in urllib. requirements.txt should list it.
import requests

# --- Make `from config import config` work even though this file lives
#     in a SUBdirectory (ingestion/) of the project.
#
# __file__               = absolute path to THIS .py file
# os.path.dirname(...)   = strip the filename, keep the directory
# Calling dirname twice  = go UP one level (from ingestion/ to finflow/)
# sys.path.insert(0, p)  = put that path at the FRONT of Python's import
#                         search list, so `import config` finds finflow/config.py.
#
# Without this, `python -m ingestion.crypto_producer` would not be able to
# `import config`, because Python only auto-searches the current dir and
# installed packages — not arbitrary parent directories.
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import config  # finflow/config.py exports a singleton `config` object

# --- Configure the logging system.
# Replaces ad-hoc print() with timestamped, leveled log lines like:
#   2026-05-15 13:42:01,123 INFO [crypto_producer] Fetched: BITCOIN=$80,358.00 | ...
logging.basicConfig(
    level=logging.INFO,                                          # show INFO and above (hide DEBUG)
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",   # time | level | logger-name | message
)
# Get (or create) a logger named "crypto_producer". Using a named logger
# (instead of the root logger) makes it easy to filter or route this
# service's logs separately later.
log = logging.getLogger("crypto_producer")


# ===========================================================================
# MODULE-LEVEL CONSTANTS
# ===========================================================================
# ALL_CAPS = convention for "this is a constant, don't reassign it".
# Defining these at module scope (not inside a function) makes them easy
# to find, edit, and reuse across functions.

# The CoinGecko endpoint we'll be hitting. "Simple price" is the cheapest,
# fastest endpoint in their API — perfect for a "what's the price right now?" poll.
COINGECKO_URL = "https://api.coingecko.com/api/v3/simple/price"

# Which coins to fetch. These strings are CoinGecko's internal IDs (full
# names like "bitcoin"), NOT ticker symbols like "BTC".
SYMBOLS = ["bitcoin", "ethereum", "solana", "ripple", "cardano", "polkadot"]

# How long to wait between polls. 60s respects CoinGecko's free-tier
# rate limit (~10–50 req/min depending on time of day) with comfortable margin.
FETCH_INTERVAL_SECONDS = 60


# ===========================================================================
# fetch_prices()  —  Step 1: EXTRACT
# ===========================================================================
# Calls the CoinGecko API and returns the raw nested dict, e.g.
#   {"bitcoin": {"usd": 80358, "usd_24h_change": 0.85, ...}, "ethereum": {...}}
# ---------------------------------------------------------------------------

def fetch_prices() -> dict:
    # `requests.get(url, params=..., timeout=...)` builds the HTTPS request,
    # sends it, and returns a Response object.
    response = requests.get(
        COINGECKO_URL,
        # `params=` is a dict of query-string parameters. `requests` will
        # URL-encode them and append them as `?ids=...&vs_currencies=...`.
        # The values must be strings, so booleans are written as "true".
        params={
            "ids": ",".join(SYMBOLS),         # "bitcoin,ethereum,solana,ripple,cardano,polkadot"
            "vs_currencies": "usd",           # price in US dollars
            "include_24hr_change": "true",    # add "usd_24h_change" field
            "include_24hr_vol": "true",       # add "usd_24h_vol" field (24h trading volume)
            "include_market_cap": "true",     # add "usd_market_cap" field
        },
        # `timeout=10` says: if we don't get a response in 10 seconds, raise
        # a Timeout exception. WITHOUT this, a dead network can hang forever.
        # Always set a timeout on production HTTP calls.
        timeout=10,
    )

    # If the response was an error status (4xx/5xx), raise an exception.
    # Without this line, requests would happily return a "404 Not Found"
    # body and you'd get a confusing JSON parse error later.
    response.raise_for_status()

    # `.json()` parses the response body (JSON text) into a Python dict.
    # Equivalent to `json.loads(response.text)`, just shorter.
    return response.json()


# ===========================================================================
# normalize()  —  Step 2: TRANSFORM
# ===========================================================================
# Flattens the nested response into one tidy dict per coin. Each output
# record is the shape we want to write to disk / send to Kafka / load
# into Snowflake — independent of the API's natural shape.
# ---------------------------------------------------------------------------

def normalize(raw: dict) -> list:
    """Flatten CoinGecko response into flat records — one row per symbol."""

    # One timestamp for the whole batch (NOT one per coin):
    #   - Every record in this poll was ingested at the same moment.
    #   - Makes it trivial to later ask "show me the 13:42 batch".
    #   - Tiny perf win — we compute it once, not N times.
    # `isoformat()` -> "2026-05-15T13:42:01.123456+00:00"
    ingested_at = datetime.now(timezone.utc).isoformat()

    records = []

    # `raw.items()` yields (key, value) pairs from the dict, e.g.
    #     ("bitcoin", {"usd": 80358, "usd_24h_change": 0.85, ...})
    # The `for symbol, data in ...` syntax UNPACKS each pair into two vars.
    for symbol, data in raw.items():
        records.append({
            # Uppercase the coin id: "bitcoin" -> "BITCOIN".
            "symbol": symbol.upper(),

            # Add a constant field marking the asset class. Useful when
            # this stream gets merged with stocks/forex/etc. downstream.
            "asset_type": "CRYPTO",

            # `data.get("usd")` pulls 80358 from the inner dict.
            # `.get(key)` returns None if the key is missing — safer than
            # `data["usd"]`, which raises KeyError. APIs occasionally omit
            # fields and we'd rather write a row with None than crash.
            "price_usd": data.get("usd"),

            # Renaming on the way out: API says "usd_24h_change", our
            # warehouse columns prefer "change_24h_pct". Renaming during
            # normalize() decouples our schema from the vendor's naming.
            "change_24h_pct": data.get("usd_24h_change"),
            "volume_24h_usd": data.get("usd_24h_vol"),
            "market_cap_usd": data.get("usd_market_cap"),

            # Same timestamp on every record (computed above the loop).
            "ingested_at": ingested_at,

            # Tag the source so downstream systems can tell where each
            # record came from when this stream gets merged with others.
            "source": "coingecko",
        })
    return records


# ===========================================================================
# save_local()  —  Step 3a: LOAD (to disk)
# ===========================================================================
# Append the batch to a date-partitioned JSONL file. Why JSONL?
#   - One JSON object per line, separated by '\n'.
#   - Trivially appendable — no need to re-read/re-write the whole file.
#   - Streamable — readers can parse line-by-line without loading all of it.
#   - Standard in data engineering (Spark, BigQuery, Snowflake all read it).
# ---------------------------------------------------------------------------

def save_local(records: list) -> str:
    """Append records to a date-partitioned JSONL file."""

    # Date string like "20260515". We use it in the FILENAME so each day's
    # data lives in its own file. This is "date partitioning" — a basic
    # but very effective pattern for organizing event data.
    date_str = datetime.now().strftime("%Y%m%d")

    # f-strings substitute the config value into the path:
    #   /Users/sayantaninath/finflow/data/raw/crypto
    out_dir = f"{config.raw_data_dir}/crypto"

    # `exist_ok=True` means: if the directory already exists, don't error.
    # Without it, the second call would raise FileExistsError.
    os.makedirs(out_dir, exist_ok=True)

    # Full path:  .../crypto/crypto_20260515.jsonl
    path = f"{out_dir}/crypto_{date_str}.jsonl"

    # `open(path, "a")` opens the file in APPEND mode:
    #   "a"  -> append (create if missing, never truncate)
    #   "w"  -> write  (truncate to empty first — would lose earlier rows!)
    #   "r"  -> read
    # The `with ... as f:` guarantees the file is flushed and closed cleanly.
    with open(path, "a") as f:
        for record in records:
            # Serialize the dict to a JSON string and add a newline so the
            # next record starts on its own line — that's the JSONL contract.
            f.write(json.dumps(record) + "\n")

    # Log how many rows we wrote and where. f-strings make formatted
    # logging easy to read.
    log.info(f"Saved {len(records)} records → {path}")

    return path


# ===========================================================================
# produce_to_kafka()  —  Step 3b: LOAD (to streaming queue)
# ===========================================================================
# Publishes the same records to a Kafka topic so other services (consumers)
# can react to prices in real time. Kafka is a distributed log — you write
# events to a topic, and many consumers can read them independently.
# ---------------------------------------------------------------------------

def produce_to_kafka(records: list):
    """Produce records to Kafka. Key = symbol for ordered partitioning."""

    # Import HERE (inside the function), not at the top, so the script
    # still runs when the `kafka` library isn't installed — as long as
    # USE_KAFKA stays false. Top-level imports run unconditionally.
    from kafka import KafkaProducer

    producer = KafkaProducer(
        # Comma-separated list of one or more broker addresses (e.g.
        # "broker1:9092,broker2:9092"). The client uses these for the
        # initial connection, then learns about the rest of the cluster.
        bootstrap_servers=config.kafka.bootstrap_servers,

        # value_serializer & key_serializer turn Python objects into bytes
        # before sending. Kafka itself only knows bytes. Here:
        #   value = the record dict -> JSON string -> UTF-8 bytes
        #   key   = the symbol string         -> UTF-8 bytes
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        key_serializer=lambda k: k.encode("utf-8"),

        # acks="all" = wait for ALL in-sync replicas to confirm before
        # considering the write successful. Strongest durability — no data
        # loss even if a broker dies right after our send. "1" = only the
        # leader needs to ack (faster, slightly riskier). "0" = fire and
        # forget (fastest, no durability guarantee).
        acks="all",

        # Retry up to 5 times on transient errors (e.g. leader election).
        retries=5,

        # max_in_flight_requests_per_connection=1 means: don't send the
        # next batch on this TCP connection until the previous one is
        # confirmed. Combined with retries, this PRESERVES per-key order —
        # otherwise a retried message could land AFTER a later one.
        max_in_flight_requests_per_connection=1,
    )

    for record in records:
        # producer.send() is asynchronous — it queues the message into an
        # internal buffer and returns immediately. Actual network I/O
        # happens in a background thread.
        producer.send(
            config.kafka.crypto_topic,   # which topic to write to
            key=record["symbol"],        # all "BITCOIN" rows go to the SAME partition,
                                         # so consumers see them in order
            value=record,                # the actual payload
        )

    # producer.flush() blocks until every queued message has been sent
    # (or failed). Without this we might return before the data is on
    # the wire, then close the connection and lose those messages.
    producer.flush()

    log.info(f"Produced {len(records)} records → Kafka topic: {config.kafka.crypto_topic}")

    # Close the producer cleanly. Without this, the background thread
    # could keep the process alive (or leak resources if reused).
    producer.close()


# ===========================================================================
# run()  —  the main loop
# ===========================================================================
# Polls the API forever. Each iteration: fetch -> normalize -> save -> log,
# then sleep. Errors are logged but DON'T kill the loop — robustness matters
# for a long-running ingestion service.
# ---------------------------------------------------------------------------

def run():
    log.info(f"Starting crypto producer | Kafka={config.use_kafka} | interval={FETCH_INTERVAL_SECONDS}s")

    # Infinite loop. The service runs until killed (Ctrl-C, kill signal,
    # container restart). For a real production setup you'd also handle
    # SIGTERM to exit gracefully, but this is fine for development.
    while True:
        try:
            # The four steps of one tick of the pipeline:
            raw = fetch_prices()                       # 1. EXTRACT from API
            records = normalize(raw)                   # 2. TRANSFORM to flat records
            save_local(records)                        # 3a. LOAD to disk

            # Only push to Kafka if the env var USE_KAFKA=true was set.
            # Lets us develop locally without a Kafka cluster.
            if config.use_kafka:
                produce_to_kafka(records)              # 3b. LOAD to Kafka

            # List comprehensions — concise way to build a list:
            #   [expr for item in iterable]
            symbols = [r["symbol"] for r in records]
            # Build a human-friendly summary like "BITCOIN=$80,358.00".
            # In the f-string:
            #   :,        -> thousands separator (80358 -> 80,358)
            #   .2f       -> 2 decimal places  (80358 -> 80358.00)
            prices = [f"{r['symbol']}=${r['price_usd']:,.2f}" for r in records]
            # " | ".join(...) glues the strings together with " | " between them.
            log.info(f"Fetched: {' | '.join(prices)}")

        # ----- Handle specific, expected error cases first --------------
        # Exception handling in Python is "first match wins" — listing
        # specific exceptions before broad ones means we get targeted
        # behavior for known cases and a safety net for everything else.

        except requests.exceptions.HTTPError as e:
            # CoinGecko returns HTTP 429 ("Too Many Requests") when you
            # exceed the free-tier rate limit. Politely sleep longer
            # before continuing, then `continue` to skip the normal sleep.
            if e.response.status_code == 429:
                log.warning("Rate limited by CoinGecko — sleeping 120s")
                time.sleep(120)
                continue
            # Any other HTTP error (500, 503, etc.) — just log it. The
            # loop will retry on the next iteration after the normal sleep.
            log.error(f"HTTP error: {e}")

        except requests.exceptions.ConnectionError as e:
            # Network issues — DNS failures, broken connections, etc.
            # Likely transient, so just log and try again next tick.
            log.error(f"Network error — will retry: {e}")

        # ----- Catch-all so unexpected errors don't kill the service ----
        except Exception as e:
            # `exc_info=True` tells the logger to include the FULL traceback
            # (the multi-line "where did this come from" stack info), which
            # is essential for diagnosing surprising errors after the fact.
            log.error(f"Unexpected error: {e}", exc_info=True)

        # Sleep regardless of success or failure (except the 429 case which
        # `continue`'d earlier). This is the "rate limiter" — guarantees we
        # don't hammer the API on errors or run faster than intended.
        time.sleep(FETCH_INTERVAL_SECONDS)


# ===========================================================================
# ENTRY POINT
# ===========================================================================
# `if __name__ == "__main__":` is the idiom for "only run this when this
# file is the script being executed". If another module does
# `from ingestion.crypto_producer import normalize`, this block is SKIPPED,
# meaning fetch_prices/normalize/save_local etc. can be imported and reused
# elsewhere (e.g. unit tests) without accidentally starting the polling loop.
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    run()
