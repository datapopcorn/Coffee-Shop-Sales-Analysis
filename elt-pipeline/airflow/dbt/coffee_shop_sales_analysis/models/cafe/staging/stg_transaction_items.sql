with source_transaction_items as (
select 
    transaction_id,
    item_id,
    quantity,
    unit_price,
    subtotal,
    created_at
from {{ source('coffee_shop_analysis', 'transaction_items') }}
)
select distinct * from source_transaction_items