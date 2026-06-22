-- Daily aggregated summary per symbol — pre-aggregated for fast dashboard queries
{{ config(materialized='table') }}

select
    ingested_date                       as price_date,
    symbol,
    asset_type,
    min(price_usd)                      as day_low_usd,
    max(price_usd)                      as day_high_usd,
    avg(price_usd)                      as day_avg_usd,
    first_value(price_usd) ignore nulls over (
        partition by symbol, ingested_date
        order by ingested_at
    )                                   as open_price_usd,
    last_value(price_usd) ignore nulls over (
        partition by symbol, ingested_date
        order by ingested_at
        rows between unbounded preceding and unbounded following
    )                                   as close_price_usd,
    sum(volume_usd)                     as total_volume_usd,
    count(*)                            as observation_count,
    sum(case when is_extreme_move then 1 else 0 end) as extreme_move_count
from {{ ref('fact_price_movements') }}
group by price_date, symbol, asset_type
