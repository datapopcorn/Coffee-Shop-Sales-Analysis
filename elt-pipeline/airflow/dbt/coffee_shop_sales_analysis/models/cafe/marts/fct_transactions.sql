with transactions as (
    select * from {{ ref('stg_transactions') }}
),
transactions_static as (
    select * from {{ ref('stg_transactions_static') }}
),
payment_methods as (
    select * from {{ ref('dim_payment_methods') }}
),

transactions_join_payment_methods as (
    select 
        transactions.transaction_id,
        transactions.customer_id,   
        transactions.payment_method_id,
        transactions.total_spent,
        transactions.location,
        date(transactions.created_at) as transaction_date,
        payment_methods.name as payment_method_name
    from transactions
    left join payment_methods on transactions.payment_method_id = payment_methods.payment_method_id
),

transactions_union_static as (
    select
        transaction_id,
        customer_id,
        payment_method_name,
        location,
        total_spent,
        transaction_date
    from transactions_join_payment_methods
    union all
    select
        transaction_id,
        null as customer_id,
        payment_method as payment_method_name,
        location,
        total_spent,
        transaction_date
    from transactions_static
)
select * from transactions_union_static