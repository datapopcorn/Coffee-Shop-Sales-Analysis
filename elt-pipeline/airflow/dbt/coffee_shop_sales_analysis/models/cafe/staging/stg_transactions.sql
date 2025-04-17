with source_transactions as (
select 
    transaction_id,
    customer_id,
    payment_method_id,
    total_spent,
    location,
    status,
    created_at,
    updated_at
from {{ source('coffee_shop_analysis', 'transactions') }}
)
select distinct * from source_transactions
