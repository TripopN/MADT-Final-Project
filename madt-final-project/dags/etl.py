from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryCreateEmptyDatasetOperator
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator
from airflow.providers.google.cloud.hooks.gcs import GCSHook
from airflow.operators.dummy import DummyOperator
from airflow.utils import timezone
from airflow.utils.task_group import TaskGroup
import datetime
import os

# Function to download, clean, and re-upload CSV files from raw bucket to storage bucket
def clean_and_transfer_csv(source_bucket: str, source_object: str, destination_bucket: str, gcp_conn_id: str):
    gcs_hook = GCSHook(gcp_conn_id=gcp_conn_id)

    # Download the CSV file from source GCS bucket
    local_file_path = f"/tmp/{source_object}"
    gcs_hook.download(source_bucket, source_object, local_file_path)

    # Clean the CSV file by removing null characters
    cleaned_file_path = f"/tmp/cleaned_{source_object}"
    with open(local_file_path, 'r', encoding='utf-8') as infile:
        with open(cleaned_file_path, 'w', encoding='utf-8') as outfile:
            for line in infile:
                cleaned_line = line.replace('\x00', '')  # Remove null characters
                outfile.write(cleaned_line)

    # Upload the cleaned CSV to the destination GCS bucket
    gcs_hook.upload(destination_bucket, source_object, cleaned_file_path)

with DAG(
    "etl_with_cleaning_transfer",
    start_date=timezone.datetime(2024, 5, 4),
    schedule_interval=None,  # Set None for manual runs if appropriate
    tags=["madt_final_project_shamir"],
    catchup=False  # To avoid backfilling DAG runs
) as dag:

    start = DummyOperator(
        task_id='start'
    )

    # List of files to process
    files = [
        'customer.csv', 'invoice.csv', 'transaction.csv', 'invoice_type.csv',
        'product.csv', 'reorder.csv', 'store.csv', 'zoning.csv'
    ]

    # Task group to clean and transfer CSV files from raw bucket to storage bucket
    with TaskGroup("clean_and_transfer_csv_files") as clean_and_transfer_group:
        clean_and_transfer_tasks = [
            PythonOperator(
                task_id=f"clean_and_transfer_{file.split('.')[0]}",
                python_callable=clean_and_transfer_csv,
                op_args=[
                    'rawdata-madt-finalproject',  # Source bucket
                    file,                         # Source file
                    'storage-madt-finalproject',  # Destination bucket
                    'my-gcp-conn'                 # GCP connection ID
                ],
            
            ) for file in files
        ]

    # Create dataset task
    create_dataset = BigQueryCreateEmptyDatasetOperator(
        task_id='create_dataset',
        dataset_id='finalproject_data',
        gcp_conn_id='my-gcp-conn',
    )

    # Task group for GCS to BigQuery transfers (using cleaned files from storage bucket)
    with TaskGroup("gcs_to_bigquery") as gcs_to_bq_group:
        gcs_to_bq_tasks = [
            GCSToBigQueryOperator(
                task_id=f"gcs_to_bq_{file.split('.')[0]}",
                bucket='storage-madt-finalproject',
                source_objects=[file],
                destination_project_dataset_table=f'madt-finalproject.finalproject_data.{file.split(".")[0]}',
                write_disposition='WRITE_TRUNCATE',
                create_disposition='CREATE_IF_NEEDED',
                gcp_conn_id='my-gcp-conn',
                skip_leading_rows =1, #skip the header row during import
                retries=3,  # Add retries
                ignore_unknown_values=True,
                retry_delay=datetime.timedelta(minutes=5)  # Corrected retry delay
            ) for file in files
        ]

    end = DummyOperator(
        task_id='end'
    )

    # Defining task dependencies
    start >> clean_and_transfer_group >> create_dataset >> gcs_to_bq_group >> end