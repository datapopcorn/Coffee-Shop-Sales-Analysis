with source_customers as (
select 
    customer_id,
    name,
    email,
    created_at,
    updated_at
    from {{ source('coffee_shop_analysis', 'customers') }}
)
select distinct * from source_customers

