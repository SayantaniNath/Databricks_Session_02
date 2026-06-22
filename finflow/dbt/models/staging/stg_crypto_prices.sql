-- Staging layer: clean and type-cast raw crypto records
-- Source: RAW.CRYPTO_PRICES (loaded from JSONL files)
-- No business logic here — just cleaning and renaming

{{ config(materialized='incremental', unique_key='price_key') }}

with source as (
    select * from {{ source('raw', 'crypto_prices') }}
    {% if is_incremental() %}
        -- Only process new records since last run
        where ingested_at > (select max(ingested_at) from {{ this }})
    {% endif %}
),

cleaned as (
    select
        {{ dbt_utils.generate_surrogate_key(['symbol', 'ingested_at']) }} as price_key,
        upper(trim(symbol))          as symbol,
        upper(trim(asset_type))      as asset_type,
        try_to_decimal(price_usd, 18, 8)          as price_usd,
        try_to_decimal(change_24h_pct, 10, 4)     as change_24h_pct,
        try_to_decimal(volume_24h_usd, 20, 2)     as volume_24h_usd,
        try_to_decimal(market_cap_usd, 20, 2)     as market_cap_usd,
        try_to_timestamp_ntz(ingested_at)         as ingested_at,
        lower(trim(source))          as source,
        -- Data quality flags
        case when price_usd <= 0 or price_usd is null then true else false end as is_price_invalid,
        case when abs(change_24h_pct) > 50 then true else false end            as is_extreme_move
    from source
    where symbol is not null
      and price_usd is not null
)

select * from cleaned
