from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryCreateEmptyDatasetOperator
from airflow.providers.google.cloud.transfers.gcs_to_gcs import GCSToGCSOperator
from airflow.operators.dummy import DummyOperator
from airflow.utils import timezone
from airflow.contrib.operators.bigquery_operator import BigQueryOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook

with DAG(
    "etl",
    start_date=timezone.datetime(2024, 5, 4),
    schedule_interval="@daily",
    tags=["madt_final_project_shamir"],
) as dag:

    # Dummy start task
    start = DummyOperator(
        task_id='start',
        dag=dag,
    )

    # Task to load data into Google Cloud Storage
    upload_file_customer_to_warehouse = GCSToGCSOperator(
        task_id="upload_file_customer_to_warehouse",
        source_bucket="rawdata-madt-finalproject",
        source_objects=["customer.csv"],
        destination_bucket="storage-madt-finalproject",
        destination_object="customer.csv",
        gcp_conn_id='my_gcp_conn'
    )

    upload_file_invoice_to_warehouse = GCSToGCSOperator(
        task_id="upload_file_invoice_to_warehouse",
        source_bucket="rawdata-madt-finalproject",
        source_objects=["invoice.csv"],
        destination_bucket="storage-madt-finalproject",
        destination_object="invoice.csv",
        gcp_conn_id='my_gcp_conn'
    )

    upload_file_invoice_trans_to_warehouse = GCSToGCSOperator(
        task_id="upload_file_invoice_trans_to_warehouse",
        source_bucket="rawdata-madt-finalproject",
        source_objects=["invoice_trans.csv"],
        destination_bucket="storage-madt-finalproject",
        destination_object="invoice_trans.csv",
        gcp_conn_id='my_gcp_conn'
    )

    upload_file_invoice_type_to_warehouse = GCSToGCSOperator(
        task_id="upload_file_invoice_type_to_warehouse",
        source_bucket="rawdata-madt-finalproject",
        source_objects=["invoice_type.csv"],
        destination_bucket="storage-madt-finalproject",
        destination_object="invoice_type.csv",
        gcp_conn_id='my_gcp_conn'
    )

    upload_file_product_to_warehouse = GCSToGCSOperator(
        task_id="upload_file_product_to_warehouse",
        source_bucket="rawdata-madt-finalproject",
        source_objects=["product.csv"],
        destination_bucket="storage-madt-finalproject",
        destination_object="product.csv",
        gcp_conn_id='my_gcp_conn'
    )

    upload_file_reorder_to_warehouse = GCSToGCSOperator(
        task_id="upload_file_reorder_to_warehouse",
        source_bucket="rawdata-madt-finalproject",
        source_objects=["reorder.csv"],
        destination_bucket="storage-madt-finalproject",
        destination_object="reorder.csv",
        gcp_conn_id='my_gcp_conn'
    )

    upload_file_store_to_warehouse = GCSToGCSOperator(
        task_id="upload_file_store_to_warehouse",
        source_bucket="rawdata-madt-finalproject",
        source_objects=["store.csv"],
        destination_bucket="storage-madt-finalproject",
        destination_object="store.csv",
        gcp_conn_id='my_gcp_conn'
    )

    upload_file_zoning_to_warehouse = GCSToGCSOperator(
        task_id="upload_file_zoning_to_warehouse",
        source_bucket="rawdata-madt-finalproject",
        source_objects=["zoning.csv"],
        destination_bucket="storage-madt-finalproject",
        destination_object="zoning.csv",
        gcp_conn_id='my_gcp_conn'
    )

    upload_file_fact_to_warehouse = GCSToGCSOperator(
        task_id="upload_file_fact_to_warehouse",
        source_bucket="rawdata-madt-finalproject",
        source_objects=["fact.csv"],
        destination_bucket="storage-madt-finalproject",
        destination_object="fact.csv",
        gcp_conn_id='my_gcp_conn'
    )
#------------------------------------------------------------------------------------------------------#

    create_dataset = BigQueryCreateEmptyDatasetOperator(
        task_id='create_dataset',
        dataset_id='finalproject_data',
        gcp_conn_id='my_gcp_conn',
    )

#-----------------------------------------------------------------------------------------------------#

    gcs_to_bq_customer = GCSToBigQueryOperator(
        task_id="gcs_to_bq_customer",
        bucket='storage-madt-finalproject',
        source_objects=['customer.csv'],
        destination_project_dataset_table='finalproject_data.customer',
        write_disposition='WRITE_TRUNCATE',
        create_disposition='CREATE_IF_NEEDED',
        gcp_conn_id='my_gcp_conn'
    )

    gcs_to_bq_invoice = GCSToBigQueryOperator(
        task_id="gcs_to_bq_invoice",
        bucket='storage-madt-finalproject',
        source_objects=['invoice.csv'],
        destination_project_dataset_table='finalproject_data.invoice',
        write_disposition='WRITE_TRUNCATE',
        create_disposition='CREATE_IF_NEEDED',
        gcp_conn_id='my_gcp_conn'
    )

    gcs_to_bq_invoice_trans = GCSToBigQueryOperator(
        task_id="gcs_to_bq_invoice_trans",
        bucket='storage-madt-finalproject',
        source_objects=['invoice_trans.csv'],
        destination_project_dataset_table='finalproject_data.invoice_trans',
        write_disposition='WRITE_TRUNCATE',
        create_disposition='CREATE_IF_NEEDED',
        gcp_conn_id='my_gcp_conn'
    )

    gcs_to_bq_invoice_type = GCSToBigQueryOperator(
        task_id="gcs_to_bq_invoice_type",
        bucket='storage-madt-finalproject',
        source_objects=['invoice_type.csv'],
        destination_project_dataset_table='finalproject_data.invoice_type',
        write_disposition='WRITE_TRUNCATE',
        create_disposition='CREATE_IF_NEEDED',
        gcp_conn_id='my_gcp_conn'
    )

    gcs_to_bq_product = GCSToBigQueryOperator(
        task_id="gcs_to_bq_product",
        bucket='storage-madt-finalproject',
        source_objects=['product.csv'],
        destination_project_dataset_table='finalproject_data.product',
        write_disposition='WRITE_TRUNCATE',
        create_disposition='CREATE_IF_NEEDED',
        gcp_conn_id='my_gcp_conn'
    )

    gcs_to_bq_reorder = GCSToBigQueryOperator(
        task_id="gcs_to_bq_reorder",
        bucket='storage-madt-finalproject',
        source_objects=['reorder.csv'],
        destination_project_dataset_table='finalproject_data.reorder',
        write_disposition='WRITE_TRUNCATE',
        create_disposition='CREATE_IF_NEEDED',
        gcp_conn_id='my_gcp_conn'
    )

    gcs_to_bq_store = GCSToBigQueryOperator(
        task_id="gcs_to_bq_store",
        bucket='storage-madt-finalproject',
        source_objects=['store.csv'],
        destination_project_dataset_table='finalproject_data.store',
        write_disposition='WRITE_TRUNCATE',
        create_disposition='CREATE_IF_NEEDED',
        gcp_conn_id='my_gcp_conn'
    )

    gcs_to_bq_zoning = GCSToBigQueryOperator(
        task_id="gcs_to_bq_zoning",
        bucket='storage-madt-finalproject',
        source_objects=['zoning.csv'],
        destination_project_dataset_table='finalproject_data.zoning',
        write_disposition='WRITE_TRUNCATE',
        create_disposition='CREATE_IF_NEEDED',
        gcp_conn_id='my_gcp_conn'
    )

    gcs_to_bq_fact = GCSToBigQueryOperator(
        task_id="gcs_to_bq_fact",
        bucket='storage-madt-finalproject',
        source_objects=['fact.csv'],
        destination_project_dataset_table='finalproject_data.fact',
        write_disposition='WRITE_TRUNCATE',
        create_disposition='CREATE_IF_NEEDED',
        gcp_conn_id='my_gcp_conn'
    )

    # Dummy end task
    end = DummyOperator(
        task_id='end',
        dag=dag,
    )

    # Defining the task dependencies
    start >> [
        upload_file_customer_to_warehouse,
        upload_file_invoice_to_warehouse,
        upload_file_invoice_trans_to_warehouse,
        upload_file_invoice_type_to_warehouse,
        upload_file_product_to_warehouse,
        upload_file_reorder_to_warehouse,
        upload_file_store_to_warehouse,
        upload_file_zoning_to_warehouse,
        upload_file_fact_to_warehouse
    ] >> create_dataset >> [
        gcs_to_bq_customer,
        gcs_to_bq_invoice,
        gcs_to_bq_invoice_trans,
        gcs_to_bq_invoice_type,
        gcs_to_bq_product,
        gcs_to_bq_reorder,
        gcs_to_bq_store,
        gcs_to_bq_zoning,
        gcs_to_bq_fact
    ] >> end
