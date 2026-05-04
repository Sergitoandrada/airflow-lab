{{ config(materialized='table') }}

SELECT
    producto,
    SUM(cantidad)   AS total_cantidad,
    SUM(total)      AS total_vendido,
    COUNT(*)        AS num_ventas
FROM ventas_demo
GROUP BY producto
ORDER BY total_vendido DESC
