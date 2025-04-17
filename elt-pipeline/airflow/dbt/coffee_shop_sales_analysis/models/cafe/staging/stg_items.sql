with source_items as (
select 
    item_id, 
    name, 
    description, 
    unit_price, 
    created_at, 
    updated_at 
from {{ source('coffee_shop_analysis', 'items') }}
)
select distinct * from source_items
