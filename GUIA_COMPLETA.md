# Guia Data Engineering Lab

## Arquitectura
CSV → Airflow → PostgreSQL → dbt → Grafana
                                   ↑
                         Prometheus (metricas)
                         MinIO (data lake)

## Puertos
- Airflow:    http://localhost:8081  (admin/sergio546119)
- pgAdmin:    http://localhost:8080
- MinIO:      http://localhost:9001  (admin/admin123456)
- Grafana:    http://localhost:3000  (admin/admin)
- Prometheus: http://localhost:9090

## Redes Docker
- airflow-lab_default    → interna de Airflow
- portainer_default      → PostgreSQL principal
- minio-lab_default      → MinIO
- monitoring-lab_default → Prometheus + Grafana

## Regla de oro
Cada stack levanta su propia red.
Si dos contenedores no se ven, conectarlos:
  docker network connect RED_DESTINO CONTENEDOR

## Conectividad critica
airflow_scheduler → portainer_default      (para ver postgres_lab)
airflow_scheduler → minio-lab_default      (para ver minio_lab)
postgres_lab      → monitoring-lab_default (para que Grafana lo vea)

## Problemas frecuentes y soluciones

### IP hardcodeada en DAG
MAL:  host="172.18.0.2"
BIEN: host="postgres_lab"

### Permission denied en dbt desde Airflow
Copiar proyecto a /tmp antes de ejecutar:
  cp -r /opt/airflow/dbt /tmp/dbt_run && chmod -R 777 /tmp/dbt_run

### MinIO invalid hostname
Usar IP directa en lugar de hostname:
  Minio("172.23.0.2:9000", ...)

### DAG pausado al crear
  airflow dags unpause NOMBRE_DAG

### DB Airflow con migracion rota
  docker-compose down -v
  docker-compose up -d

### Redes se pierden al reiniciar
Declarar redes externas en docker-compose.yml:
  networks:
    portainer_default:
      external: true
    minio-lab_default:
      external: true

## Pipeline principal
DAG: pipeline_csv_postgres
Tasks:
  1. cargar_csv    → lee CSV e inserta en ventas_demo
  2. ejecutar_dbt  → crea tabla ventas_por_producto
  3. subir_minio   → archiva CSV en bucket rawdata

## dbt
Proyecto: /usr/app/laboratorio_dbt
Modelos:  /usr/app/laboratorio_dbt/models/
Ejecutar: dbt run --models NOMBRE_MODELO
Perfil:   ~/.dbt/profiles.yml

## Comandos utiles Airflow
# Ver DAGs
docker exec -it airflow_scheduler airflow dags list

# Despausar DAG
docker exec -it airflow_scheduler airflow dags unpause NOMBRE_DAG

# Triggerear DAG
docker exec -it airflow_scheduler airflow dags trigger NOMBRE_DAG

# Ver logs de task
docker exec -it airflow_scheduler bash -c "cat '/opt/airflow/logs/dag_id=DAGID/run_id=RUNID/task_id=TASKID/attempt=1.log'"

## Alertas Prometheus
Archivo: ~/monitoring-lab/alerts.yml
Reglas actuales:
  - PostgresDown: avisa si postgres_lab cae

## Dashboard Grafana
Nombre: Dashboard Lab
Paneles:
  1. Ventas por Producto (Bar chart)
     SELECT producto, SUM(total) AS total_vendido
     FROM ventas_demo
     GROUP BY producto
     ORDER BY total_vendido DESC

  2. Total Vendido (Stat/KPI)
     SELECT SUM(total) AS total_vendido
     FROM ventas_demo

  3. Evolucion de Ventas (Time series)
     SELECT fecha AS time, SUM(total) AS total
     FROM ventas_demo
     GROUP BY fecha
     ORDER BY fecha

  4. Estado de Servicios (Stat - Prometheus)
     Query: up

## Stack completo levantado
docker ps debe mostrar:
  airflow_scheduler
  airflow_webserver
  airflow_postgres
  postgres_lab
  dbt_lab
  minio_lab
  grafana_lab
  prometheus_lab
  pgadmin_lab
  kafka_lab
  zookeeper_lab
  superset_lab
  portainer_lab
