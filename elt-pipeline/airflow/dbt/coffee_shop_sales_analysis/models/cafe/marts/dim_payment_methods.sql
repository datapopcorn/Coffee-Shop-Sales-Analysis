with payment_methods as (
    select * from {{ ref('stg_payment_methods') }}
)
select * from payment_methods