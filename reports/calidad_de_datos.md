# Reporte de calidad de datos

## Fuentes

- `olist_orders_dataset.csv`: 99,441 filas, 8 columnas
- `olist_customers_dataset.csv`: 99,441 filas, 5 columnas
- `olist_order_items_dataset.csv`: 112,650 filas, 7 columnas
- `olist_order_payments_dataset.csv`: 103,886 filas, 5 columnas
- `olist_order_reviews_dataset.csv`: 100,000 filas, 7 columnas
- `olist_products_dataset.csv`: 32,951 filas, 9 columnas
- `olist_sellers_dataset.csv`: 3,095 filas, 4 columnas
- `product_category_name_translation.csv`: 71 filas, 2 columnas

## Validaciones y decisiones

- Pedidos con `order_id` duplicado: 0
- Pedidos con fecha de entrega anterior a la compra: 0
- Pedidos 'delivered' sin fecha de entrega (excluidos de métricas logísticas): 8
- Reseñas asociadas a pedidos con más de una reseña: 1114 (se conserva la más reciente)
- Período de análisis: ene-2017 a ago-2018 (meses completos). Se excluyen 349 pedidos de meses incompletos
- Productos sin categoría: 610 (se etiquetan como 'sin_categoria')

## Salida

- `orders.csv`: 99,092 pedidos (1 fila por pedido)
- `order_items.csv`: 112,279 ítems
- `sellers.csv`: 3,095 vendedores
