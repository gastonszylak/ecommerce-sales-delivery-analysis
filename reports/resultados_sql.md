# Resultados de las consultas SQL

Generado por `src/run_sql.py` a partir de `sql/analysis.sql`.

## 01_kpis_generales

|   pedidos |   clientes |   facturacion_brl |   ticket_promedio_brl |   pct_entregas_tarde |   nota_promedio |
|----------:|-----------:|------------------:|----------------------:|---------------------:|----------------:|
|     97910 |      94707 |       1.34495e+07 |                137.37 |                  6.8 |             4.1 |

## 02_ventas_mensuales_mom

| order_month   |   pedidos |      facturacion |   crecimiento_mom_pct |
|:--------------|----------:|-----------------:|----------------------:|
| 2017-01       |       787 | 120098           |                 nan   |
| 2017-02       |      1718 | 244959           |                 104   |
| 2017-03       |      2617 | 368341           |                  50.4 |
| 2017-04       |      2377 | 353843           |                  -3.9 |
| 2017-05       |      3640 | 503159           |                  42.2 |
| 2017-06       |      3205 | 429917           |                 -14.6 |
| 2017-07       |      3946 | 492287           |                  14.5 |
| 2017-08       |      4272 | 568246           |                  15.4 |
| 2017-09       |      4227 | 621416           |                   9.4 |
| 2017-10       |      4547 | 660180           |                   6.2 |
| 2017-11       |      7423 |      1.00386e+06 |                  52.1 |
| 2017-12       |      5620 | 742184           |                 -26.1 |
| 2018-01       |      7187 | 945456           |                  27.4 |
| 2018-02       |      6625 | 837895           |                 -11.4 |
| 2018-03       |      7168 | 981051           |                  17.1 |
| 2018-04       |      6919 | 993593           |                   1.3 |
| 2018-05       |      6833 | 992872           |                  -0.1 |
| 2018-06       |      6145 | 863266           |                 -13.1 |
| 2018-07       |      6233 | 878044           |                   1.7 |
| 2018-08       |      6421 | 848860           |                  -3.3 |

## 03_pareto_categorias

| category              |      facturacion |   pct_acumulado |
|:----------------------|-----------------:|----------------:|
| health_beauty         |      1.25399e+06 |             9.3 |
| watches_gifts         |      1.20164e+06 |            18.1 |
| bed_bath_table        |      1.03651e+06 |            25.8 |
| sports_leisure        | 984715           |            33.1 |
| computers_accessories | 910555           |            39.8 |
| furniture_decor       | 723882           |            45.1 |
| cool_stuff            | 634180           |            49.8 |
| housewares            | 630962           |            54.5 |
| auto                  | 590887           |            58.8 |
| garden_tools          | 483897           |            62.4 |
| toys                  | 479482           |            65.9 |
| baby                  | 410135           |            69   |
| perfumery             | 393436           |            71.9 |
| telephony             | 323108           |            74.3 |
| office_furniture      | 272660           |            76.3 |

## 04_atraso_vs_satisfaccion

| entrega            |   pedidos |   nota_promedio |   pct_resenas_negativas |
|:-------------------|----------:|----------------:|------------------------:|
| Entregado a tiempo |     89672 |            4.28 |                     9.5 |
| Entregado tarde    |      6531 |            2.26 |                    62.9 |

## 05_nota_por_dias_de_atraso

| tramo                   |   pedidos |   nota_promedio |
|:------------------------|----------:|----------------:|
| 0. A tiempo             |     89672 |            4.28 |
| 1. 1-3 días tarde       |      1869 |            3.28 |
| 2. 4-7 días tarde       |      1802 |            2.09 |
| 3. 8-14 días tarde      |      1478 |            1.67 |
| 4. Más de 14 días tarde |      1382 |            1.72 |

## 06_atraso_por_estado

| estado   |   pedidos_entregados |   pct_tarde |   dias_entrega_promedio |
|:---------|---------------------:|------------:|------------------------:|
| AL       |                  396 |        21.5 |                    24.5 |
| MA       |                  713 |        17.5 |                    21.5 |
| SE       |                  332 |        15.4 |                    21.4 |
| PI       |                  475 |        13.9 |                    19.4 |
| CE       |                 1273 |        13.8 |                    21.2 |
| BA       |                 3253 |        12.2 |                    19.3 |
| RJ       |                12310 |        12.1 |                    15.3 |
| PA       |                  942 |        11.3 |                    23.8 |
| ES       |                 1992 |        10.7 |                    15.8 |
| PB       |                  516 |        10.5 |                    20.4 |

## 07_despacho_tardio_del_vendedor

| despacho                   |   pedidos |   pct_pedidos |   pct_llega_tarde_al_cliente |
|:---------------------------|----------:|--------------:|-----------------------------:|
| Vendedor despachó a tiempo |     87621 |          91.1 |                          5.4 |
| Vendedor despachó tarde    |      8581 |           8.9 |                         21.1 |

## 08_concentracion_atrasos_vendedores

|   vendedores_activos |   vendedores_que_explican_50pct_atrasos |   pct_de_vendedores |
|---------------------:|----------------------------------------:|--------------------:|
|                 2934 |                                      98 |                 3.3 |

## 09_recompra_segun_primer_pedido

| experiencia            |   clientes |   pct_volvio_a_comprar |
|:-----------------------|-----------:|-----------------------:|
| Primer pedido a tiempo |      86641 |                   3.12 |
| Primer pedido tarde    |       6342 |                   2.55 |

## 10_atraso_mensual

| order_month   |   pedidos_entregados |   pct_tarde |
|:--------------|---------------------:|------------:|
| 2017-01       |                  750 |         2.9 |
| 2017-02       |                 1653 |         3   |
| 2017-03       |                 2546 |         4.6 |
| 2017-04       |                 2303 |         6.6 |
| 2017-05       |                 3545 |         3   |
| 2017-06       |                 3135 |         3   |
| 2017-07       |                 3872 |         2.8 |
| 2017-08       |                 4193 |         2.9 |
| 2017-09       |                 4150 |         4.4 |
| 2017-10       |                 4478 |         4.2 |
| 2017-11       |                 7288 |        12.4 |
| 2017-12       |                 5513 |         7.5 |
| 2018-01       |                 7069 |         5.7 |
| 2018-02       |                 6555 |        14.1 |
| 2018-03       |                 7003 |        19   |
| 2018-04       |                 6798 |         4.5 |
| 2018-05       |                 6749 |         6.6 |
| 2018-06       |                 6096 |         1.2 |
| 2018-07       |                 6156 |         3.4 |
| 2018-08       |                 6351 |         6.2 |
