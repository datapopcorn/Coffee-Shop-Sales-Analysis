with items as (
    select * from {{ ref('stg_items') }}
)
select * from items