"""
Kafka consumer — reads from finflow topics → saves to local files or S3.

Run:
    source ~/myenv/bin/activate
    cd ~/finflow
    USE_KAFKA=true python -m consumers.raw_consumer
"""
import json
import logging
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
log = logging.getLogger("raw_consumer")

TOPICS = [config.kafka.crypto_topic, config.kafka.stocks_topic]
BATCH_SIZE = 100  # write to disk every 100 messages — reduces I/O


def save_batch_local(records: list, topic: str):
    date_str = datetime.now().strftime("%Y%m%d_%H")
    asset_type = "crypto" if "crypto" in topic else "stocks"
    out_dir = f"{config.raw_data_dir}/{asset_type}/kafka"
    os.makedirs(out_dir, exist_ok=True)
    path = f"{out_dir}/{asset_type}_kafka_{date_str}.jsonl"
    with open(path, "a") as f:
        for record in records:
            f.write(json.dumps(record) + "\n")
    log.info(f"Flushed {len(records)} records → {path}")


def upload_to_s3(records: list, topic: str):
    """Upload batch to S3 as partitioned JSONL — enables Glue/Athena queries."""
    import boto3
    s3 = boto3.client("s3")
    now = datetime.now()
    asset_type = "crypto" if "crypto" in topic else "stocks"
    key = f"raw/{asset_type}/year={now.year}/month={now.month:02d}/day={now.day:02d}/{now.strftime('%H%M%S')}.jsonl"
    body = "\n".join(json.dumps(r) for r in records)
    s3.put_object(Bucket=config.s3_bucket, Key=key, Body=body)
    log.info(f"Uploaded {len(records)} records → s3://{config.s3_bucket}/{key}")


def consume():
    from kafka import KafkaConsumer, TopicPartition
    consumer = KafkaConsumer(
        *TOPICS,
        bootstrap_servers=config.kafka.bootstrap_servers,
        group_id=config.kafka.consumer_group,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        auto_offset_reset="earliest",
        enable_auto_commit=False,   # manual commit — don't lose messages on crash
        max_poll_records=BATCH_SIZE,
        session_timeout_ms=30000,
    )
    log.info(f"Consumer started | topics={TOPICS} | group={config.kafka.consumer_group}")
    batch = []
    current_topic = None
    try:
        for message in consumer:
            batch.append(message.value)
            current_topic = message.topic
            if len(batch) >= BATCH_SIZE:
                save_batch_local(batch, current_topic)
                if config.use_s3:
                    upload_to_s3(batch, current_topic)
                consumer.commit()  # only commit after successful write
                batch = []
    except KeyboardInterrupt:
        log.info("Shutting down consumer...")
        if batch:
            save_batch_local(batch, current_topic or TOPICS[0])
            consumer.commit()
    finally:
        consumer.close()


if __name__ == "__main__":
    consume()
