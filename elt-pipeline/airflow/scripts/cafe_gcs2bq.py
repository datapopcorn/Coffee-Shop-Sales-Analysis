# flake8: noqa
import os
from typing import Iterator

import dlt
from dlt.sources import TDataItems
from dlt.sources.filesystem import readers


def read_parquet_chunked(**context) -> None:
    write_disposition = context.get('params', {}).get('write_disposition', 'append')
    print(write_disposition)
    pipeline = dlt.pipeline(
        pipeline_name="standard_filesystem",
        destination='bigquery',
        dataset_name="coffee_shop_analysis",
    )
    # When using the readers resource, you can specify a filter to select only the files you
    # want to load including a glob pattern. If you use a recursive glob pattern, the filenames
    # will include the path to the file inside the bucket_url.

    # PARQUET reading
    parquet_reader1 = readers(file_glob="coffee_sales/items/*.parquet").read_parquet()
    parquet_reader1.apply_hints(incremental=dlt.sources.incremental("updated_at", primary_key="item_id"))
    parquet_reader2 = readers(file_glob="coffee_sales/transactions/*.parquet").read_parquet()
    parquet_reader2.apply_hints(incremental=dlt.sources.incremental("updated_at", primary_key="transaction_id"))
    parquet_reader3 = readers(file_glob="coffee_sales/transaction_items/*.parquet").read_parquet()
    parquet_reader3.apply_hints(incremental=dlt.sources.incremental("created_at"), primary_key=("transaction_id", "item_id"))
    parquet_reader4 = readers(file_glob="coffee_sales/customers/*.parquet").read_parquet()
    parquet_reader4.apply_hints(incremental=dlt.sources.incremental("updated_at"), primary_key="customer_id")
    parquet_reader5 = readers(file_glob="coffee_sales/payment_methods/*.parquet").read_parquet()
    parquet_reader5.apply_hints(incremental=dlt.sources.incremental("created_at"), primary_key="payment_method_id")
    parquet_reader6 = readers(file_glob="coffee_sales/transactions_static/*.parquet").read_parquet()
    parquet_reader6.apply_hints(incremental=dlt.sources.incremental("transaction_date"), primary_key="transaction_id")
    # load both folders together to specified tables
    load_info = pipeline.run(
        [
            #jsonl_reader.with_name("items")
            parquet_reader1.with_name("items"),
            parquet_reader2.with_name("transactions"),
            parquet_reader3.with_name("transaction_items"),
            parquet_reader4.with_name("customers"),
            parquet_reader5.with_name("payment_methods"),
            parquet_reader6.with_name("transactions_static")
        ],
        write_disposition=write_disposition
    )
    print(load_info)
    print(pipeline.last_trace.last_normalize_info)


if __name__ == "__main__":
    read_parquet_chunked()