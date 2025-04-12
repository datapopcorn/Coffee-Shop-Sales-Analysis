# flake8: noqa
import humanize
from typing import Any
import os

import dlt
from dlt.common import pendulum
from dlt.sources.credentials import ConnectionStringCredentials

from dlt.sources.sql_database import sql_database, sql_table, Table

from sqlalchemy.sql.sqltypes import TypeEngine
import sqlalchemy as sa


def load_select_tables_from_database() -> None:
    """Use the sql_database source to reflect an entire database schema and load select tables from it.

    This example sources data from the public Rfam MySQL database.
    """
    # Create a pipeline
    pipeline = dlt.pipeline(pipeline_name="load_coffee_sales_data", destination='filesystem', dataset_name="coffee_sales")

    # Credentials for the sample database.
    # Note: It is recommended to configure credentials in `.dlt/secrets.toml` under `sources.sql_database.credentials`
    #credentials = ConnectionStringCredentials(
    #    "mysql+pymysql://rfamro@mysql-rfam-public.ebi.ac.uk:4497/Rfam"
    #)
    
    # To pass the credentials from `secrets.toml`, comment out the above credentials.
    # And the credentials will be automatically read from `secrets.toml`.

    # Configure the source to load a few select tables incrementally
    source_transactions = sql_database().with_resources("transactions")
    source_items = sql_database().with_resources("items")
    source_transaction_items = sql_database().with_resources("transaction_items")
    source_customers = sql_database().with_resources("customers")
    source_payment_methods = sql_database().with_resources("payment_methods")
    source_transactions_static = sql_database().with_resources("transactions_static")
    # Add incremental config to the resources. "updated" is a timestamp column in these tables that gets used as a cursor
    #source_1.transactions.apply_hints(incremental=dlt.sources.incremental("updated"))
    #source_1.clan.apply_hints(incremental=dlt.sources.incremental("updated"))

    # Run the pipeline. The merge write disposition merges existing rows in the destination by primary key
    #info = pipeline.run(source_1, write_disposition="merge")
    info_transactions = pipeline.run(source_transactions, write_disposition="replace")
    info_items = pipeline.run(source_items, write_disposition="replace")
    info_transaction_items = pipeline.run(source_transaction_items, write_disposition="replace")
    info_customers = pipeline.run(source_customers, write_disposition="replace")
    info_payment_methods = pipeline.run(source_payment_methods, write_disposition="replace")
    info_transactions_static = pipeline.run(source_transactions_static, write_disposition="replace")
    print(info_transactions)
    print(info_items)
    print(info_transaction_items)
    print(info_customers)
    print(info_payment_methods)
    print(info_transactions_static)



def load_entire_database() -> None:
    """Use the sql_database source to completely load all tables in a database"""
    pipeline = dlt.pipeline(pipeline_name="load_coffee_sales_data", destination='filesystem', dataset_name="coffee_sales")

    # By default the sql_database source reflects all tables in the schema
    # The database credentials are sourced from the `.dlt/secrets.toml` configuration
    source = sql_database()

    # Run the pipeline. For a large db this may take a while
    info = pipeline.run(source, write_disposition="replace")
    print(humanize.precisedelta(pipeline.last_trace.finished_at - pipeline.last_trace.started_at))
    print(info)



if __name__ == "__main__":
    # Load selected tables with different settings
    load_select_tables_from_database()

    # load a table and select columns
    # select_columns()

    # load_entire_database()
    # select_with_end_value_and_row_order()

    # Load tables with the standalone table resource
    #  load_standalone_table_resource()

    # Load all tables from the database.
    # Warning: The sample database is very large
    # load_entire_database()
