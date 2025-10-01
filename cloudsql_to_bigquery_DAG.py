from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
from airflow.utils.dates import days_ago
import psycopg2
import csv
import os
from google.cloud import storage
import requests

PROJECT_ID = "gcloud-flow-123"
DB_NAME = "sales"
DB_USER = "etl_user"
DB_PASS = "xxxxxx"
DB_HOST = "xxxxxx"  # Cloud SQL public IP
BUCKET = f"{PROJECT_ID}-etl-bucket"
BQ_DATASET = "sales_dw"
TABLES = ["customers", "products", "sales_orders"]

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
}

# Optional: diagnostic task to print Composer egress IP
def print_egress_ip():
    ip = requests.get("https://ifconfig.me").text.strip()
    print(f"🌍 Public egress IP used by Composer: {ip}")

# Export table as CSV
def export_table_to_gcs_csv(table_name, bucket_name):
    # Connect to Cloud SQL Postgres
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST,
        sslmode="require"
    )
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {table_name}")
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]

    local_file = f"/tmp/{table_name}.csv"
    with open(local_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(columns)  # write header
        writer.writerows(rows)    # write data

    # Upload to GCS
    client = storage.Client(project=PROJECT_ID)
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(f"raw/{table_name}.csv")
    blob.upload_from_filename(local_file)

    cur.close()
    conn.close()
    os.remove(local_file)

with DAG(
    "cloudsql_to_bq_etl_csv",
    default_args=default_args,
    schedule_interval="@daily",
    start_date=days_ago(1),
    catchup=False,
) as dag:

    # Diagnostic task (optional)
    check_ip = PythonOperator(
        task_id="print_egress_ip",
        python_callable=print_egress_ip,
    )

    # Step 1: Export tables to GCS as CSV
    export_tasks = []
    for table in TABLES:
        export_tasks.append(
            PythonOperator(
                task_id=f"export_{table}_csv",
                python_callable=export_table_to_gcs_csv,
                op_args=[table, BUCKET],
            )
        )

    # Step 2: Load CSV into BigQuery
    load_tasks = []
    for table in TABLES:
        load_tasks.append(
            GCSToBigQueryOperator(
                task_id=f"load_{table}_bq",
                bucket=BUCKET,
                source_objects=[f"raw/{table}.csv"],
                destination_project_dataset_table=f"{PROJECT_ID}.{BQ_DATASET}.{table}",
                source_format="CSV",
                skip_leading_rows=1,  # skip header
                autodetect=True,
                write_disposition="WRITE_TRUNCATE",
            )
        )

    # Step 3: Transform sales_orders into sales_agg
    transform_sales = BigQueryInsertJobOperator(
        task_id="transform_sales",
        configuration={
            "query": {
                "query": f"""
                CREATE OR REPLACE TABLE `{PROJECT_ID}.{BQ_DATASET}.sales_agg` AS
                SELECT 
                    p.category,
                    p.product_id,
                    p.name AS product_name,
                    SUM(s.quantity * p.price) AS total_revenue,
                    COUNT(s.order_id) AS total_orders
                FROM `{PROJECT_ID}.{BQ_DATASET}.sales_orders` s
                JOIN `{PROJECT_ID}.{BQ_DATASET}.products` p
                ON s.product_id = p.product_id
                GROUP BY p.category, p.product_id, p.name
                """,
                "useLegacySql": False,
            }
        },
    )

    # Dependencies
    check_ip >> export_tasks  # optional IP check
    for export_task, load_task in zip(export_tasks, load_tasks):
        export_task >> load_task
    for load_task in load_tasks:
        load_task >> transform_sales
