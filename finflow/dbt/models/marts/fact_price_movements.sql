-- Fact table: one row per price observation
-- Kimball-style: surrogate key + FK to dim_symbols + measures
{{ config(materialized='incremental', unique_key='price_key', cluster_by=['ingested_date']) }}

with crypto as (
    select
        price_key,
        symbol,
        asset_type,
        price_usd,
        change_24h_pct,
        volume_24h_usd  as volume_usd,
        market_cap_usd,
        ingested_at,
        is_price_invalid,
        is_extreme_move
    from {{ ref('stg_crypto_prices') }}
    where not is_price_invalid
),

stocks as (
    select
        price_key,
        symbol,
        asset_type,
        price_usd,
        null            as change_24h_pct,
        null            as volume_usd,
        market_cap_usd,
        ingested_at,
        is_price_invalid,
        false           as is_extreme_move
    from {{ ref('stg_stock_prices') }}
    where not is_price_invalid
),

combined as (
    select * from crypto
    union all
    select * from stocks
),

with_derived as (
    select
        price_key,
        symbol,
        asset_type,
        price_usd,
        change_24h_pct,
        volume_usd,
        market_cap_usd,
        ingested_at,
        cast(ingested_at as date)  as ingested_date,
        -- Price movement vs previous record for same symbol
        lag(price_usd) over (
            partition by symbol
            order by ingested_at
        )                          as prev_price_usd,
        price_usd - lag(price_usd) over (
            partition by symbol order by ingested_at
        )                          as price_delta_usd,
        is_extreme_move
    from combined
    {% if is_incremental() %}
        where ingested_at > (select max(ingested_at) from {{ this }})
    {% endif %}
)

select * from with_derived
