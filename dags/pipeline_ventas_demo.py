from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import psycopg2

def insertar_postgres():
    conn = psycopg2.connect(
        host="postgres_lab",   # nombre del contenedor, no IP
        port=5432,
        database="labdb",
        user="admin",
        password="admin123"
    )
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO ventas_demo (fecha, cliente, producto, cantidad, total)
        VALUES ('2026-04-30', 'Cliente Airflow', 'Hierro', 25, 95000);
    """)
    conn.commit()
    cursor.close()
    conn.close()

default_args = {
    "owner": "sergio",
    "start_date": datetime(2026, 4, 1),
}

with DAG(
    dag_id="pipeline_ventas_demo",
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
) as dag:
    tarea = PythonOperator(
        task_id="insert_postgres",
        python_callable=insertar_postgres
    )
