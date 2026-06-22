"""
FinFlow Airflow DAG — orchestrates the full pipeline.

Tasks:
1. fetch_crypto_prices    → CoinGecko API → local file
2. fetch_stock_prices     → yfinance → local file
3. update_redis_cache     → cache latest prices in Redis
4. load_to_snowflake      → bulk load JSONL files to Snowflake RAW schema
5. run_dbt_transformations → dbt run (staging → marts)
6. run_dbt_tests          → dbt test (data quality checks)
7. alert_on_anomalies     → check for price spikes > 20%

Install Airflow:
    source ~/myenv/bin/activate
    pip install apache-airflow
    airflow db init
    airflow webserver --port 8080  (terminal 1)
    airflow scheduler              (terminal 2)
    Then open: http://localhost:8080
"""
import json
import logging
import os
import sys
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from airflow.utils.dates import days_ago

log = logging.getLogger(__name__)

FINFLOW_HOME = os.path.expanduser("~/finflow")
sys.path.insert(0, FINFLOW_HOME)

default_args = {
    "owner": "sayantani",
    "retries": 3,
    "retry_delay": timedelta(minutes=2),
    "retry_exponential_backoff": True,   # 2m, 4m, 8m — backs off on repeated failure
    "email_on_failure": False,
    "depends_on_past": False,
}

with DAG(
    dag_id="finflow_market_pipeline",
    default_args=default_args,
    description="Real-time financial market data pipeline",
    schedule_interval="*/5 * * * *",  # every 5 minutes during market hours
    start_date=days_ago(1),
    catchup=False,
    max_active_runs=1,               # prevent overlapping runs
    tags=["finflow", "market-data", "production"],
) as dag:

    def task_fetch_crypto(**context):
        from ingestion.crypto_producer import fetch_prices, normalize, save_local
        raw = fetch_prices()
        records = normalize(raw)
        path = save_local(records)
        # Push to XCom so downstream tasks can use it
        context["ti"].xcom_push(key="crypto_records", value=records)
        context["ti"].xcom_push(key="crypto_file_path", value=path)
        log.info(f"Fetched {len(records)} crypto prices")

    def task_fetch_stocks(**context):
        from ingestion.stock_producer import fetch_prices, save_local
        records = fetch_prices()
        path = save_local(records)
        context["ti"].xcom_push(key="stock_records", value=records)
        log.info(f"Fetched {len(records)} stock prices")

    def task_update_redis(**context):
        from cache.redis_manager import cache_all_prices, health_check
        if not health_check():
            log.warning("Redis unavailable — skipping cache update")
            return
        crypto = context["ti"].xcom_pull(key="crypto_records", task_ids="fetch_crypto_prices") or []
        stocks = context["ti"].xcom_pull(key="stock_records", task_ids="fetch_stock_prices") or []
        cache_all_prices(crypto + stocks)

    def task_check_anomalies(**context):
        """Flag assets with >20% price change — potential data quality issue or market event."""
        crypto = context["ti"].xcom_pull(key="crypto_records", task_ids="fetch_crypto_prices") or []
        anomalies = [
            r for r in crypto
            if r.get("change_24h_pct") and abs(r["change_24h_pct"]) > 20
        ]
        if anomalies:
            log.warning(f"ANOMALY DETECTED: {[f'{a[\"symbol\"]} {a[\"change_24h_pct\"]:+.1f}%' for a in anomalies]}")
        return "load_to_snowflake"  # always continue — anomaly is informational

    fetch_crypto = PythonOperator(
        task_id="fetch_crypto_prices",
        python_callable=task_fetch_crypto,
    )

    fetch_stocks = PythonOperator(
        task_id="fetch_stock_prices",
        python_callable=task_fetch_stocks,
    )

    update_redis = PythonOperator(
        task_id="update_redis_cache",
        python_callable=task_update_redis,
    )

    check_anomalies = BranchPythonOperator(
        task_id="check_anomalies",
        python_callable=task_check_anomalies,
    )

    load_snowflake = BashOperator(
        task_id="load_to_snowflake",
        bash_command=f"cd {FINFLOW_HOME} && source ~/myenv/bin/activate && python -m consumers.snowflake_loader",
    )

    run_dbt = BashOperator(
        task_id="run_dbt_transformations",
        bash_command=f"cd {FINFLOW_HOME}/dbt && dbt run --profiles-dir .",
    )

    run_dbt_tests = BashOperator(
        task_id="run_dbt_tests",
        bash_command=f"cd {FINFLOW_HOME}/dbt && dbt test --profiles-dir .",
    )

    done = EmptyOperator(task_id="pipeline_complete")

    # Dependency graph
    [fetch_crypto, fetch_stocks] >> update_redis >> check_anomalies
    check_anomalies >> load_snowflake >> run_dbt >> run_dbt_tests >> done
