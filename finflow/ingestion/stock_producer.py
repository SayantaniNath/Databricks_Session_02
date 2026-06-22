"""
Stock price producer — yfinance → local file → Kafka (optional).

Install: pip install yfinance

Run:
    source ~/myenv/bin/activate
    pip install yfinance
    cd ~/finflow
    python -m ingestion.stock_producer
"""
import json
import logging
import os
import sys
import time
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
log = logging.getLogger("stock_producer")

SYMBOLS = ["AAPL", "GOOGL", "MSFT", "AMZN", "NVDA", "META", "JPM", "GS"]
FETCH_INTERVAL_SECONDS = 300  # 5 minutes — stocks don't need 1-min refresh


def fetch_prices() -> list:
    import yfinance as yf
    records = []
    ingested_at = datetime.now(timezone.utc).isoformat()
    tickers = yf.Tickers(" ".join(SYMBOLS))
    for symbol in SYMBOLS:
        try:
            info = tickers.tickers[symbol].fast_info
            records.append({
                "symbol": symbol,
                "asset_type": "STOCK",
                "price_usd": info.last_price,
                "open_usd": info.open,
                "day_high_usd": info.day_high,
                "day_low_usd": info.day_low,
                "volume": info.three_month_average_volume,
                "market_cap_usd": info.market_cap,
                "exchange": info.exchange,
                "ingested_at": ingested_at,
                "source": "yfinance",
            })
        except Exception as e:
            log.warning(f"Could not fetch {symbol}: {e}")
    return records


def save_local(records: list) -> str:
    date_str = datetime.now().strftime("%Y%m%d")
    out_dir = f"{config.raw_data_dir}/stocks"
    os.makedirs(out_dir, exist_ok=True)
    path = f"{out_dir}/stocks_{date_str}.jsonl"
    with open(path, "a") as f:
        for record in records:
            f.write(json.dumps(record) + "\n")
    log.info(f"Saved {len(records)} records → {path}")
    return path


def produce_to_kafka(records: list):
    from kafka import KafkaProducer
    producer = KafkaProducer(
        bootstrap_servers=config.kafka.bootstrap_servers,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        key_serializer=lambda k: k.encode("utf-8"),
        acks="all",
        retries=5,
    )
    for record in records:
        producer.send(config.kafka.stocks_topic, key=record["symbol"], value=record)
    producer.flush()
    log.info(f"Produced {len(records)} records → {config.kafka.stocks_topic}")
    producer.close()


def run():
    log.info(f"Starting stock producer | symbols={SYMBOLS} | interval={FETCH_INTERVAL_SECONDS}s")
    while True:
        try:
            records = fetch_prices()
            if records:
                save_local(records)
                if config.use_kafka:
                    produce_to_kafka(records)
                log.info(f"Prices: {' | '.join(f'{r[chr(115)+chr(121)+chr(109)+chr(98)+chr(111)+chr(108)]}=${r[chr(112)+chr(114)+chr(105)+chr(99)+chr(101)+chr(95)+chr(117)+chr(115)+chr(100)]:,.2f}' for r in records if r['price_usd'])}")
        except Exception as e:
            log.error(f"Error fetching stocks: {e}", exc_info=True)
        time.sleep(FETCH_INTERVAL_SECONDS)


if __name__ == "__main__":
    run()
