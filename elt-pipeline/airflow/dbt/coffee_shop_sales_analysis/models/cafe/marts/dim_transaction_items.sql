with transaction_items as (
    select 
        transaction_id,
        item_id,
        quantity,
        unit_price,
        subtotal,
        created_at
    from {{ ref('stg_transaction_items') }}
),
transaction_items_static_with_item_id as (
    select
        tx_s.transaction_id,
        i.item_id,
        tx_s.quantity,
        tx_s.unit_price,
        tx_s.total_spent,
        timestamp(tx_s.transaction_date) as created_at
    from {{ ref('stg_transactions_static') }} tx_s
    left join {{ ref('stg_items') }} i 
    on 
    tx_s.item_name = i.name
)
select
  *
from
  transaction_items
UNION ALL
select
  *
from
  transaction_items_static_with_item_id
