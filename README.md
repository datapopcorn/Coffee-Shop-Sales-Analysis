# ☕ Coffee Shop Sales Analysis

## 📌 Problem Description

This project aims to simulate and analyze sales data from a fictional coffee shop. The goal is to build an end-to-end **batch data pipeline** that processes transactional data, stores it in a data lake, moves it to a data warehouse, performs analytical transformations, and ultimately powers a **dashboard** with two insightful tiles:

- Distribution of items sold
- Temporal trends of customer purchases

This pipeline simulates a real-world analytics scenario, enabling us to apply data engineering concepts learned during the ZooCamp course.

---

## 📦 Dataset Overview

The dataset used in this project is based on [Cafe Sales Dirty Data](https://www.kaggle.com/datasets/ahmedmohamed2003/cafe-sales-dirty-data-for-cleaning-training) from Kaggle. It serves as historical static transactional data for initial loading.

To simulate real-world ongoing data generation, a FastAPI service is built to emulate new coffee shop sales transactions, which are stored in a PostgreSQL OLTP database. These are batch-synced to the data lake and warehouse periodically.

---

## 🛠️ Tech Stack

| Category               | Tool/Service         | Description                                                                |
| ---------------------- | -------------------- | -------------------------------------------------------------------------- |
| Data Source (OLTP)     | FastAPI + PostgreSQL | FastAPI simulates real-time sales and stores them in a PostgreSQL database |
| Batch Orchestration    | Apache Airflow       | Schedules and orchestrates the entire data flow                            |
| Data Loading Tool      | dlt                  | Loads data from PostgreSQL ➔ GCS ➔ BigQuery                                |
| Transformations        | dbt                  | Cleans and enriches data in BigQuery                                       |
| Data Lake              | Google Cloud Storage | Stores raw data in cloud object storage                                    |
| Data Warehouse         | BigQuery             | Stores cleaned and transformed data                                        |
| Infrastructure as Code | Terraform            | Provisions GCS buckets and BigQuery datasets                               |
| Containerization       | Docker               | Packages services for easy development and deployment                      |

---

## 🔄 Pipeline Overview

### 🗃️ Historical Data Load (Initial)

1. The Kaggle dataset is stored as a seed file at `dbt/seeds/cafe_old/cafe_sales_static.csv`
2. Use `dbt seed` to load the dataset into the BigQuery staging dataset
3. Trigger `dbt run` to transform the seeded data into analytics-ready tables

### 📋 New Transactional Data (FastAPI ➔ OLTP ➔ DWH)

1. FastAPI writes sales transactions to PostgreSQL
2. Airflow triggers a dlt job to export data to GCS in parquet format
3. dlt then loads data from GCS to BigQuery
4. dbt performs data transformations and prepares final tables

---

## 🧩 DAG & Scripts Breakdown

### DAG: `cafe_data_pipeline`

Scheduled to run **hourly**, this DAG defines a classic ETL sequence:

1. `postgres_to_gcs`: Calls `cafe_postgres2gcs.py` to extract data from PostgreSQL and dump it as Parquet into GCS
2. `gcs_to_bq`: Calls `cafe_gcs2bq.py` to load Parquet data into BigQuery with incremental logic per table
3. `run_dbt_transformations`: Triggers `cafe_transformation_dbt.py` which runs dbt in a virtual environment inside Airflow, applying all transformation models (excluding those tagged with `static`)

All Python scripts are located in `elt-pipeline/airflow/scripts/`

---


---

## 🚀 How to Run

### 1. Clone the repository

```bash
git clone https://github.com/datapopcorn/Coffee-Shop-Sales-Analysis.git
cd Coffee-Shop-Sales-Analysis
```

### 2. 🔐 Credentials & Environment Setup

#### 🔑 GCP Credentials
Place your GCP service account JSON key at:
- `streamlit_app/keys/my_creds.json`
- `elt-pipeline/airflow/dbt/coffee_shop_sales_analysis/keys/my_creds.json`
- `terraform/keys/my_creds.json`

Set `GOOGLE_APPLICATION_CREDENTIALS` as needed in your environment variables.

#### 📁 Environment Variables

##### FastAPI `.env` (located in `app/.env`):
```env
# Database
POSTGRES_HOST=postgres-cafe
POSTGRES_PORT=5432
POSTGRES_DB=coffee_db
POSTGRES_USER=coffee_user
POSTGRES_PASSWORD=coffee_pass

# CSV File Path
CSV_FILE_PATH=/app/data/cafe_sales_kaggle.csv

# API Port
API_PORT=8000

# Database URL
DATABASE_URL=postgresql://coffee_user:coffee_pass@postgres-cafe:5432/coffee_db
```

##### Airflow `.env` (located in `elt-pipeline/airflow/.env`):
```env
AIRFLOW_UID=501
```

##### DLT `secrets.toml` (located in `elt-pipeline/dlt/.dlt/secrets.toml`):
```toml
[sources.postgres]
credentials.user = "coffee_user"
credentials.password = "coffee_pass"
credentials.database = "coffee_db"
credentials.host = "postgres-cafe"
credentials.port = 5432

[destination.bigquery]
credentials = """
{
  "type": "service_account",
  "project_id": "your_project_id",
  "private_key_id": "your_private_key_id",
  "private_key": "your_private_key",
  "client_email": "your_client_email",
  "client_id": "your_client_id",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "your_cert_url"
}
"""
[runtime]
log_level = "INFO"
```
```


### 3. Provision Infrastructure with Terraform

```bash
cd terraform
terraform init
terraform apply
```

### 4. Start FastAPI + PostgreSQL

```bash
cd app
docker compose up -d
```

#### 🧪 Load Sample Data (Optional)

To run the following commands, enter the FastAPI container:

```bash
docker exec -it app-app-api-1 bash
```

Then inside the container:

```bash
make load       # Load demo JSON data
make truncate   # Clean all tables
make reset      # Truncate and reload demo data
```

### 5. Start Airflow Services

```bash
cd elt-pipeline/airflow
docker compose up -d
```

Access Airflow UI at: [http://localhost:8080](http://localhost:8080)

### 6. Trigger DAGs

- DAG: `cafe_data_pipeline`

Can be triggered manually or via schedule.

### 7. Run dbt Transformation (optional CLI)

To run `dbt` manually, first enter the Airflow container:

```bash
docker exec -it --user airflow airflow-airflow-webserver-1 bash
cd /opt/airflow/dbt/coffee_shop_sales_analysis
dbt seed  # (for loading seed data)
dbt run
```

### 8. Launch Streamlit Dashboard

```bash
cd streamlit_app
docker compose up -d
```

Access the dashboard at: [http://localhost:8501](http://localhost:8501)

---

## 📊 Dashboard Overview

The dashboard is built using **Streamlit** and showcases interactive visualizations based on the transformed BigQuery dataset.

- **Tile 1 – Item Quantity Pie Chart**: Visualizes the distribution of total quantity sold per item category, offering insights into the most popular products (e.g., Coffee, Cake, Tea, etc.). This chart is helpful for understanding customer preferences.


- **Tile 2 – Monthly Sales Line Chart**: Tracks the monthly total sales volume across the dataset’s time range. This chart helps identify seasonality, business growth or dips over time.


Each chart includes labels, legends, and dynamic layout for better clarity and data storytelling.

---

## 🤝 Peer Review Checklist

- Problem clearly described ✅
- Cloud infrastructure with IaC (Terraform) ✅
- End-to-end batch pipeline using Airflow + dlt ✅
- Data warehouse with proper partitioning and transformation via dbt ✅
- Dashboard with 2 tiles ✅
- Reproducible with clear steps ✅

---

## 🧠 Summary

This project demonstrates a modern batch data pipeline using FastAPI, Airflow, dlt, dbt, and BigQuery. With cloud-native storage and transformation, it provides insights into coffee shop sales through a reproducible, modular, and scalable architecture.

---

## 🔗 References

- [Cafe Sales Dirty Data - Kaggle](https://www.kaggle.com/datasets/ahmedmohamed2003/cafe-sales-dirty-data-for-cleaning-training)
- [dbt Documentation](https://docs.getdbt.com/)
- [Apache Airflow](https://airflow.apache.org/)
- [dlt Docs](https://docs.dlt.dev/)
- [Terraform Docs](https://developer.hashicorp.com/terraform/docs)
- [Streamlit](https://docs.streamlit.io/)
