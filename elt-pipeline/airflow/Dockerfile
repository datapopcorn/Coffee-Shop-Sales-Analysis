FROM apache/airflow:2.10.5

USER root

# install necessary packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3-pip \
    python3-venv \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# set the working directory
WORKDIR /opt/airflow

# install Python dependencies
RUN uv pip install dlt[filesystem,sql-database]>=1.9.0 
RUN uv pip install dbt-core>=1.9.4 
RUN uv pip install dbt-bigquery==1.9.1
RUN uv pip install dlt[bigquery,gs]>=1.9.0
# create necessary directories and set permissions
RUN mkdir -p /tmp/.cache/uv && \
    mkdir -p /home/airflow/.cache/uv && \
    chown -R airflow:root /tmp/ && \
    chown -R airflow:root /home/airflow && \
    chown -R airflow:root /opt/airflow && \
    chmod -R 777 /tmp/ && \
    chmod -R 777 /home/airflow && \
    chmod -R 777 /opt/airflow

USER airflow
