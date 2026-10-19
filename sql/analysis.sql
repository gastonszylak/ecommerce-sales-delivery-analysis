-- =====================================================================
-- Análisis SQL — E-commerce Olist (ene-2017 a ago-2018)
-- Motor: SQLite (sintaxis estándar; compatible con MySQL 8 / SQL Server
-- salvo funciones de fecha). Tablas: orders, order_items, sellers.
-- Cada consulta empieza con "-- name:" para que src/run_sql.py la ejecute.
-- =====================================================================

-- name: 01_kpis_generales
SELECT
    COUNT(*)                                             AS pedidos,
    COUNT(DISTINCT customer_unique_id)                   AS clientes,
    ROUND(SUM(product_value), 0)                         AS facturacion_brl,
    ROUND(AVG(product_value), 2)                         AS ticket_promedio_brl,
    ROUND(100.0 * AVG(is_late), 1)                       AS pct_entregas_tarde,
    ROUND(AVG(review_score), 2)                          AS nota_promedio
FROM orders
WHERE order_status NOT IN ('canceled', 'unavailable');

-- name: 02_ventas_mensuales_mom
WITH mensual AS (
    SELECT order_month,
           COUNT(*)                   AS pedidos,
           ROUND(SUM(product_value),0) AS facturacion
    FROM orders
    WHERE order_status NOT IN ('canceled', 'unavailable')
    GROUP BY order_month
)
SELECT order_month,
       pedidos,
       facturacion,
       ROUND(100.0 * (facturacion - LAG(facturacion) OVER (ORDER BY order_month))
             / LAG(facturacion) OVER (ORDER BY order_month), 1) AS crecimiento_mom_pct
FROM mensual
ORDER BY order_month;

-- name: 03_pareto_categorias
WITH cat AS (
    SELECT category, ROUND(SUM(price), 0) AS facturacion
    FROM order_items
    GROUP BY category
)
SELECT category,
       facturacion,
       ROUND(100.0 * SUM(facturacion) OVER (ORDER BY facturacion DESC)
             / SUM(facturacion) OVER (), 1) AS pct_acumulado
FROM cat
ORDER BY facturacion DESC
LIMIT 15;

-- name: 04_atraso_vs_satisfaccion
SELECT CASE WHEN is_late = 1 THEN 'Entregado tarde' ELSE 'Entregado a tiempo' END AS entrega,
       COUNT(*)                                                  AS pedidos,
       ROUND(AVG(review_score), 2)                               AS nota_promedio,
       ROUND(100.0 * AVG(CASE WHEN review_score <= 2 THEN 1.0 ELSE 0 END), 1) AS pct_resenas_negativas
FROM orders
WHERE is_delivered = 1 AND review_score IS NOT NULL
GROUP BY is_late;

-- name: 05_nota_por_dias_de_atraso
SELECT CASE
           WHEN days_late <= 0  THEN '0. A tiempo'
           WHEN days_late <= 3  THEN '1. 1-3 días tarde'
           WHEN days_late <= 7  THEN '2. 4-7 días tarde'
           WHEN days_late <= 14 THEN '3. 8-14 días tarde'
           ELSE                      '4. Más de 14 días tarde'
       END                          AS tramo,
       COUNT(*)                     AS pedidos,
       ROUND(AVG(review_score), 2)  AS nota_promedio
FROM orders
WHERE is_delivered = 1 AND review_score IS NOT NULL
GROUP BY tramo
ORDER BY tramo;

-- name: 06_atraso_por_estado
SELECT customer_state                    AS estado,
       COUNT(*)                          AS pedidos_entregados,
       ROUND(100.0 * AVG(is_late), 1)    AS pct_tarde,
       ROUND(AVG(delivery_days), 1)      AS dias_entrega_promedio
FROM orders
WHERE is_delivered = 1
GROUP BY customer_state
HAVING COUNT(*) >= 300
ORDER BY pct_tarde DESC
LIMIT 10;

-- name: 07_despacho_tardio_del_vendedor
SELECT CASE WHEN seller_late_handoff = 1 THEN 'Vendedor despachó tarde'
            ELSE 'Vendedor despachó a tiempo' END     AS despacho,
       COUNT(*)                                       AS pedidos,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct_pedidos,
       ROUND(100.0 * AVG(is_late), 1)                 AS pct_llega_tarde_al_cliente
FROM orders
WHERE is_delivered = 1 AND seller_late_handoff IS NOT NULL
GROUP BY seller_late_handoff;

-- name: 08_concentracion_atrasos_vendedores
WITH pedido_vendedor AS (          -- vendedor principal de cada pedido
    SELECT order_id, MIN(seller_id) AS seller_id
    FROM order_items
    GROUP BY order_id
),
por_vendedor AS (
    SELECT pv.seller_id,
           COUNT(*)        AS pedidos,
           SUM(o.is_late)  AS pedidos_tarde
    FROM pedido_vendedor pv
    JOIN orders o ON o.order_id = pv.order_id
    WHERE o.is_delivered = 1
    GROUP BY pv.seller_id
),
ranking AS (
    SELECT *,
           ROW_NUMBER() OVER (ORDER BY pedidos_tarde DESC)                         AS rk,
           1.0 * SUM(pedidos_tarde) OVER (ORDER BY pedidos_tarde DESC
                 ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
               / SUM(pedidos_tarde) OVER ()                                         AS share_acum
    FROM por_vendedor
)
SELECT (SELECT COUNT(*) FROM por_vendedor)                        AS vendedores_activos,
       MIN(CASE WHEN share_acum >= 0.5 THEN rk END)               AS vendedores_que_explican_50pct_atrasos,
       ROUND(100.0 * MIN(CASE WHEN share_acum >= 0.5 THEN rk END)
             / (SELECT COUNT(*) FROM por_vendedor), 1)            AS pct_de_vendedores
FROM ranking;

-- name: 09_recompra_segun_primer_pedido
SELECT CASE WHEN is_late = 1 THEN 'Primer pedido tarde' ELSE 'Primer pedido a tiempo' END AS experiencia,
       COUNT(*)                                          AS clientes,
       ROUND(100.0 * AVG(customer_repurchased), 2)       AS pct_volvio_a_comprar
FROM orders
WHERE customer_order_seq = 1 AND is_delivered = 1
GROUP BY is_late;

-- name: 10_atraso_mensual
SELECT order_month,
       COUNT(*)                        AS pedidos_entregados,
       ROUND(100.0 * AVG(is_late), 1)  AS pct_tarde
FROM orders
WHERE is_delivered = 1
GROUP BY order_month
ORDER BY order_month;
