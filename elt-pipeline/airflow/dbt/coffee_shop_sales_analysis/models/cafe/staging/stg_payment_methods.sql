with source_payment_methods as (
select 
    payment_method_id,
    name,
    is_active,
    created_at
from {{ source('coffee_shop_analysis', 'payment_methods') }}
)
select distinct * from source_payment_methods