"""
Central config for FinFlow pipeline.
All settings read from environment variables with safe defaults.
Copy .env.example to .env and fill in secrets — never commit .env.
"""
import os
from dataclasses import dataclass, field


@dataclass
class KafkaConfig:
    bootstrap_servers: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    crypto_topic: str = "finflow.crypto.prices"
    stocks_topic: str = "finflow.stocks.prices"
    consumer_group: str = "finflow-raw-consumers"


@dataclass
class RedisConfig:
    host: str = os.getenv("REDIS_HOST", "localhost")
    port: int = 6379
    # Live prices expire fast — stale price data is dangerous in finance
    price_ttl_seconds: int = 60
    # Aggregates (daily summary) can live longer
    summary_ttl_seconds: int = 3600


@dataclass
class SnowflakeConfig:
    account: str = os.getenv("SNOWFLAKE_ACCOUNT", "")
    user: str = os.getenv("SNOWFLAKE_USER", "")
    password: str = os.getenv("SNOWFLAKE_PASSWORD", "")
    database: str = "FINFLOW"
    warehouse: str = "FINFLOW_WH"
    raw_schema: str = "RAW"
    staging_schema: str = "STAGING"
    marts_schema: str = "MARTS"


@dataclass
class Config:
    kafka: KafkaConfig = field(default_factory=KafkaConfig)
    redis: RedisConfig = field(default_factory=RedisConfig)
    snowflake: SnowflakeConfig = field(default_factory=SnowflakeConfig)
    raw_data_dir: str = os.path.expanduser("~/finflow/data/raw")
    # Toggle integrations — start with both off, enable as you set them up
    use_kafka: bool = os.getenv("USE_KAFKA", "false").lower() == "true"
    use_redis: bool = os.getenv("USE_REDIS", "false").lower() == "true"
    use_s3: bool = os.getenv("USE_S3", "false").lower() == "true"
    s3_bucket: str = os.getenv("S3_BUCKET", "finflow-raw-data")


config = Config()
