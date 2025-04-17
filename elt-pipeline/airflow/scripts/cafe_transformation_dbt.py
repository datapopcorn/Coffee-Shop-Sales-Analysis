import dlt

def run_dbt_transformations() -> None:

    pipeline = dlt.pipeline(
        pipeline_name="coffee_shop_data_transformation",
        destination='bigquery',
        dataset_name="coffee_shop_analysis_dbt",
    )
    venv = dlt.dbt.get_venv(pipeline, venv_path="/home/airflow/.local")
    # add dbt runner
    dbt = dlt.dbt.package(pipeline, package_location="/opt/airflow/dbt/coffee_shop_sales_analysis", venv=venv)

    models = dbt.run(cmd_params=["--exclude", "tag:static"])
    # On success, print the outcome
    print(f"Running {len(models)} models")
    for m in models:
        print(
            f"Model {m.model_name} materialized" +
            f" in {m.time}" +
            f" with status {m.status}" +
            f" and message {m.message}"
        )

if __name__ == "__main__":
    run_dbt_transformations()