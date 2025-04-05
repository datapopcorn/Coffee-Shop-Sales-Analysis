# Coffee-Shop-Sales-Analysis
End to End data pipeline for coffee shop analysis

Goal: build a data pipeline that use dlt to load on-prem postgres coffee shop data transaction data to GCS, use airflow as orchestration tool move data to datawarehouse(BigQuery) periodically, dbt as transformation layer to transform data to star schema for analyze in downstream analysis use case in Superset. Finally, dockerize this whole process with docker and use IaC tool Terraform to make it the infra reusable.

 
