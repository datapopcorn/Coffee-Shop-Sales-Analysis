# config incremental strategy
{{
    config(
        materialized='incremental',
        incremental_strategy='merge',
        unique_key='transaction_id',
        partition_by={
            'field': 'transaction_date',
            'data_type': 'date'
        },
        on_schema_change='fail'
    )
}}
with transactions as (
    select * from {{ ref('stg_transactions') }}
    {% if is_incremental() %}
    where date(created_at) >= (select max(transaction_date) from {{ this }})
    {% endif %}
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
        transactions.created_at,
        transactions.updated_at,
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
        created_at,
        updated_at,
        transaction_date
    from transactions_join_payment_methods
    union all
    select
        transaction_id,
        null as customer_id,
        payment_method as payment_method_name,
        location,
        total_spent,
        null as created_at,
        null as updated_at,
        transaction_date
    from transactions_static
)
select * from transactions_union_static