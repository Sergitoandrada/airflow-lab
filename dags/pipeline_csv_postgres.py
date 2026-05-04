from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime
import csv
import urllib3
from minio import Minio

def cargar_csv():
    hook = PostgresHook(postgres_conn_id="postgres_lab")
    conn = hook.get_conn()
    cursor = conn.cursor()
    with open('/opt/airflow/dags/ventas_demo.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cursor.execute("INSERT INTO ventas_demo (fecha, cliente, producto, cantidad, total) VALUES (%s, %s, %s, %s, %s)", (row['fecha'], row['cliente'], row['producto'], row['cantidad'], row['total']))
    conn.commit()
    cursor.close()
    conn.close()
    print("CSV cargado correctamente")

def subir_minio():
    http = urllib3.PoolManager(timeout=urllib3.Timeout.DEFAULT_TIMEOUT, retries=urllib3.Retry(total=5))
    client = Minio("172.23.0.2:9000", access_key="admin", secret_key="admin123456", secure=False, http_client=http)
    bucket = "rawdata"
    if not client.bucket_exists(bucket):
        client.make_bucket(bucket)
    client.fput_object(bucket, "ventas_demo.csv", "/opt/airflow/dags/ventas_demo.csv")
    print("Subido a MinIO OK")

with DAG(dag_id="pipeline_csv_postgres", start_date=datetime(2026, 4, 1), schedule_interval=None, catchup=False) as dag:
    t1 = PythonOperator(task_id="cargar_csv", python_callable=cargar_csv)
    t2 = BashOperator(task_id="ejecutar_dbt", bash_command="cp -r /opt/airflow/dbt /tmp/dbt_run && chmod -R 777 /tmp/dbt_run && cd /tmp/dbt_run && dbt run --models ventas_por_producto --profiles-dir /opt/airflow/dbt --log-path /tmp/dbt_logs --target-path /tmp/dbt_run/target", env={"HOME": "/home/airflow"}, append_env=True)
    t3 = PythonOperator(task_id="subir_minio", python_callable=subir_minio)
    t1 >> t2 >> t3
