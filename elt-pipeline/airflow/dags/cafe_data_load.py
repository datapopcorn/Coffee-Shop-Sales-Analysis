from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
import sys
import os

# Add the scripts directory to the Python path
sys.path.append('/opt/airflow/scripts')

from cafe_postgres2gcs import load_select_tables_from_database
from cafe_gcs2bq import read_parquet_chunked
from cafe_transformation_dbt import run_dbt_transformations
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'cafe_data_pipeline',
    default_args=default_args,
    description='DAG to run cafe data pipeline every 1 hour',
    schedule_interval='@hourly',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['cafe', 'data-pipeline'],
) as dag:

    # start the pipeline
    start_pipeline = DummyOperator(task_id='start_pipeline')

    # Define the task to run the pipeline
    postgres_to_gcs = PythonOperator(
        task_id='postgres_to_gcs',
        python_callable=load_select_tables_from_database
    )

    gcs_to_bq = PythonOperator(
        task_id='gcs_to_bq',
        python_callable=read_parquet_chunked
    )

    run_dbt_transformations = PythonOperator(
        task_id='run_dbt_transformations',
        python_callable=run_dbt_transformations
    )

    # end the pipeline
    end_pipeline = DummyOperator(task_id='end_pipeline')
    
# set the order of the tasks
start_pipeline >> postgres_to_gcs >> gcs_to_bq >> run_dbt_transformations >> end_pipeline
