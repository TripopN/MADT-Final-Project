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
    cleaned_file_path = f"/tmp/cleaned_{source_object}"

    try:
        gcs_hook.download(source_bucket, source_object, local_file_path)

        # Clean the CSV file by removing null characters
        with open(local_file_path, 'r', encoding='utf-8') as infile:
            with open(cleaned_file_path, 'w', encoding='utf-8') as outfile:
                for line in infile:
                    cleaned_line = line.replace('\x00', '')  # Remove null characters
                    outfile.write(cleaned_line)

        # Upload the cleaned CSV to the destination GCS bucket
        gcs_hook.upload(destination_bucket, source_object, cleaned_file_path)
    finally:
        # Cleanup temporary files
        if os.path.exists(local_file_path):
            os.remove(local_file_path)
        if os.path.exists(cleaned_file_path):
            os.remove(cleaned_file_path)

# Define schemas for each table
schemas = {
    'customer.csv': [
        {"name": "CustomerID", "type": "STRING"},
        {"name": "Customer", "type": "STRING"},
        {"name": "Country", "type": "STRING"},
        {"name": "Customer_Category", "type": "STRING"},
        {"name": "provinceId", "type": "STRING"},
        {"name": "Latitude", "type": "FLOAT"},
        {"name": "Longitude", "type": "FLOAT"}
    ],
    'invoice.csv': [
        {"name": "InvoiceNo", "type": "STRING"},
        {"name": "CustomerID", "type": "STRING"},
        {"name": "InvoiceDate", "type": "DATE"}
    ],
    'product.csv': [
        {"name": "ProductId", "type": "STRING"},
        {"name": "lenstype", "type": "STRING"},
        {"name": "Part_Description", "type": "STRING"},
        {"name": "Material_Type", "type": "STRING"},
        {"name": "Lens_Type", "type": "STRING"},
        {"name": "price", "type": "FLOAT"}
    ],
    'reorder.csv': [
        {"name": "reorder_cause_id", "type": "STRING"},
        {"name": "cause", "type": "STRING"}
    ],
    'zone.csv': [
        {"name": "zoneId", "type": "STRING"},
        {"name": "zone_name", "type": "STRING"},
        {"name": "regionId", "type": "STRING"}
    ],
    'region.csv': [
        {"name": "regionId", "type": "STRING"},
        {"name": "region_name", "type": "STRING"}
    ],
    'transaction.csv': [
        {"name": "InvoiceNo", "type": "STRING"},
        {"name": "ProductId", "type": "STRING"},
        {"name": "Quantity", "type": "INT64"},
        {"name": "TypeId", "type": "STRING"},
        {"name": "Reorder_Cause_ID", "type": "STRING"}
    ],
    'SalesPerson.csv': [
        {"name": "sales_id", "type": "STRING"},
        {"name": "saleperson_name", "type": "STRING"},
        {"name": "average_round_trip_hours", "type": "FLOAT"}
    ],
    'CustomerSales.csv': [
        {"name": "CustomerID", "type": "STRING"},
        {"name": "sales_id", "type": "STRING"}
    ],
    'province.csv':[
        {"name": "provinceId", "type":"STRING"},
        {"name": "province_name", "type":"STRING"},
        {"name": "regionId", "type":"STRING"},
        {"name": "province_name_eng", "type":"STRING"},
        {"name": "zoneId", "type":"STRING"}
    ],
    'invoice_type.csv':[
        {"name": "typeId", "type":"STRING"},
        {"name": "type_name", "type":"STRING"}
    ]
}

with DAG(
    "etl_data_pipeline_v2",
    start_date=timezone.datetime(2024, 5, 4),
    schedule_interval=None,
    tags=["madt_final_project_shamir"],
    catchup=False
) as dag:

    start = DummyOperator(task_id='start')

    files = [
        'customer.csv', 'invoice.csv', 'product.csv', 'reorder.csv','invoice_type.csv',
        'zone.csv','province.csv', 'region.csv', 'transaction.csv', 'SalesPerson.csv', 'CustomerSales.csv'
    ]

    # Task group to clean and transfer CSV files from raw bucket to storage bucket
    with TaskGroup("clean_and_transfer_csv_files") as clean_and_transfer_group:
        clean_and_transfer_tasks = [
            PythonOperator(
                task_id=f"clean_and_transfer_{file.split('.')[0]}",
                python_callable=clean_and_transfer_csv,
                op_args=[
                    'rawdata-madt-finalproject',
                    file,
                    'storage-madt-finalproject',
                    'my-gcp-conn'
                ],
                retries=3,
                retry_delay=datetime.timedelta(minutes=2)
            ) for file in files
        ]

    create_dataset = BigQueryCreateEmptyDatasetOperator(
        task_id='create_dataset',
        dataset_id='finalproject_data',
        gcp_conn_id='my-gcp-conn',
    )

    # Task group for GCS to BigQuery transfers
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
                skip_leading_rows=1,
                retries=3,
                retry_delay=datetime.timedelta(minutes=5),
                ignore_unknown_values=True,
                schema_fields=schemas[file]
            ) for file in files
        ]

    end = DummyOperator(task_id='end')

    start >> clean_and_transfer_group >> create_dataset >> gcs_to_bq_group >> end
