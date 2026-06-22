-- Staging: clean raw stock price records
{{ config(materialized='incremental', unique_key='price_key') }}

with source as (
    select * from {{ source('raw', 'stock_prices') }}
    {% if is_incremental() %}
        where ingested_at > (select max(ingested_at) from {{ this }})
    {% endif %}
),

cleaned as (
    select
        {{ dbt_utils.generate_surrogate_key(['symbol', 'ingested_at']) }} as price_key,
        upper(trim(symbol))                               as symbol,
        upper(trim(asset_type))                           as asset_type,
        try_to_decimal(price_usd, 18, 4)                  as price_usd,
        try_to_decimal(open_usd, 18, 4)                   as open_usd,
        try_to_decimal(day_high_usd, 18, 4)               as day_high_usd,
        try_to_decimal(day_low_usd, 18, 4)                as day_low_usd,
        try_to_number(volume)                             as volume,
        try_to_decimal(market_cap_usd, 20, 2)             as market_cap_usd,
        upper(trim(exchange))                             as exchange,
        try_to_timestamp_ntz(ingested_at)                 as ingested_at,
        lower(trim(source))                               as source,
        case when price_usd <= 0 or price_usd is null then true else false end as is_price_invalid
    from source
    where symbol is not null
      and price_usd is not null
)

select * from cleaned
