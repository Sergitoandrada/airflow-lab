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


## pubñicación Linkedin

🏗️ Construí una Enterprise Data Platform completa desde cero — 100% local, 100% open source

Durante los últimos días monté un laboratorio de Data Engineering completo sobre Docker + WSL Ubuntu. El resultado es una plataforma enterprise real con 7 capas de arquitectura funcionando en simultáneo.

📐 La arquitectura completa:

1️⃣ Ingesta en tiempo real
Apache Kafka recibe eventos desde cualquier fuente (CSV, APIs, IoT, apps). Kafka UI permite monitorear los topics en vivo.

2️⃣ Almacenamiento operacional
PostgreSQL almacena los datos procesados. pgAdmin permite administración visual completa.

3️⃣ Transformación y modelado
dbt transforma los datos con SQL puro. Genera documentación automática y lineage graph de los modelos.

4️⃣ Data Lake (S3 compatible)
MinIO almacena los archivos en buckets organizados:
- `raw-data` → datos crudos
- `data-lake` → almacenamiento general
- `analytics` → datos procesados
- `backups` → respaldos

5️⃣ Consumo y visualización
Apache Superset y Grafana exponen dashboards para usuarios de negocio, analistas y científicos de datos.

6️⃣ Orquestación y automatización
Apache Airflow orquesta todo el flujo: extracción, transformación, carga, scheduling, monitoreo y alertas.

7️⃣ Monitoreo y observabilidad
Prometheus recolecta métricas. Grafana visualiza infraestructura, contenedores, pipelines y alertas en tiempo real.

🔧 Infraestructura base
Docker + Portainer + WSL Ubuntu — stack completo corriendo localmente.

*¿Por qué construirlo así?

Antes de usar plataformas que abstraen todo (Microsoft Fabric, Databricks, AWS Glue), entender cada capa por separado marca la diferencia entre operar una herramienta y entender una arquitectura.

Problemas reales resueltos:
- Redes Docker aisladas entre stacks → conectividad manual
- Hostname resolution en Kafka desde WSL
- Permisos en volúmenes montados desde Windows
- Migración de base de datos Airflow corrupta

🛠️ Stack completo:
Kafka · PostgreSQL · dbt · MinIO · Airflow · Superset · Grafana · Prometheus · Docker · Portainer · pgAdmin

Integraciones futuras planeadas:
MLflow · Spark · Elasticsearch · ClickHouse · n8n




✅ Stack completo 100% local · Open Source · Escalable · Modular · Listo para producción
