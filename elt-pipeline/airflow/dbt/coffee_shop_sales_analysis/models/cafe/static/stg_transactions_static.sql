{{
    config(
        materialized='incremental',
        unique_key='transaction_id',
        incremental_strategy='merge'
    )
}}

with source_transactions_static as (
    select 
        `Transaction ID` as transaction_id,
        `Item` as item_name,
        cast(`Quantity` as int64) as quantity,
        cast(`Price Per Unit` as float64) as unit_price,
        cast(`Total Spent` as float64) as total_spent,
        `Location` as location,
        `Payment Method` as payment_method,
        date(`Transaction Date`) as transaction_date
    from {{ ref('cafe_sales_static') }}
    where `Transaction ID` is not null
    and `Transaction ID` != 'ERROR'
    and `Transaction ID` != 'UNKNOWN'
    and `Item` is not null
    and `Item` != 'ERROR'
    and `Item` != 'UNKNOWN'
    and `Quantity` is not null
    and `Quantity` != 'ERROR'
    and `Quantity` != 'UNKNOWN'
    and `Price Per Unit` is not null
    and `Price Per Unit` != 'ERROR'
    and `Price Per Unit` != 'UNKNOWN'
    and `Total Spent` is not null
    and `Total Spent` != 'ERROR'
    and `Total Spent` != 'UNKNOWN'
    and `Location` is not null
    and `Location` != 'ERROR'
    and `Location` != 'UNKNOWN'
    and `Payment Method` is not null
    and `Payment Method` != 'ERROR'
    and `Payment Method` != 'UNKNOWN'
    and `Transaction Date` is not null
    and `Transaction Date` != 'ERROR'
    and `Transaction Date` != 'UNKNOWN'
    {% if is_incremental() %}
    and date(`Transaction Date`) > (select max(transaction_date) from {{ this }})
    {% endif %}
)
select distinct * from source_transactions_static