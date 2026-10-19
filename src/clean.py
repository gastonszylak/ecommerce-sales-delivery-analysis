"""
Limpieza y preparación de datos — E-commerce Olist.

Lee las 8 tablas crudas de data/raw/, valida calidad, construye las tablas
analíticas y las guarda en data/processed/ (insumo para SQL, notebook y Power BI).

Uso:  python src/clean.py
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)

# Meses completos: el dataset tiene meses con muy pocos pedidos al inicio (2016)
# y al final (sept-oct 2018) que distorsionan tendencias.
PERIOD_START = "2017-01-01"
PERIOD_END = "2018-08-31 23:59:59"

DATE_COLS = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
]

quality_log: list[str] = []


def log(msg: str) -> None:
    print(msg)
    quality_log.append(msg)


def load() -> dict[str, pd.DataFrame]:
    files = {
        "orders": "olist_orders_dataset.csv",
        "customers": "olist_customers_dataset.csv",
        "items": "olist_order_items_dataset.csv",
        "payments": "olist_order_payments_dataset.csv",
        "reviews": "olist_order_reviews_dataset.csv",
        "products": "olist_products_dataset.csv",
        "sellers": "olist_sellers_dataset.csv",
        "translation": "product_category_name_translation.csv",
    }
    dfs = {k: pd.read_csv(RAW / f) for k, f in files.items()}
    for k, df in dfs.items():
        log(f"- `{files[k]}`: {len(df):,} filas, {df.shape[1]} columnas")
    return dfs


def build_orders(d: dict[str, pd.DataFrame]) -> pd.DataFrame:
    o = d["orders"].copy()
    for c in DATE_COLS:
        o[c] = pd.to_datetime(o[c], errors="coerce")

    # Duplicados de clave
    dup = o.order_id.duplicated().sum()
    log(f"- Pedidos con `order_id` duplicado: {dup}")

    # Inconsistencias de fechas: entrega antes que la compra
    bad = (o.order_delivered_customer_date < o.order_purchase_timestamp).sum()
    log(f"- Pedidos con fecha de entrega anterior a la compra: {bad}")

    # Pedidos 'delivered' sin fecha de entrega -> no se pueden medir
    no_date = ((o.order_status == "delivered") & o.order_delivered_customer_date.isna()).sum()
    log(f"- Pedidos 'delivered' sin fecha de entrega (excluidos de métricas logísticas): {no_date}")

    # Cliente único (customer_id cambia en cada pedido; customer_unique_id identifica a la persona)
    o = o.merge(
        d["customers"][["customer_id", "customer_unique_id", "customer_city", "customer_state"]],
        on="customer_id",
        how="left",
    )

    # Ingresos por pedido desde los ítems
    it = d["items"].groupby("order_id").agg(
        items=("order_item_id", "count"),
        product_value=("price", "sum"),
        freight_value=("freight_value", "sum"),
        shipping_limit_date=("shipping_limit_date", "max"),
        sellers=("seller_id", "nunique"),
    )
    it["shipping_limit_date"] = pd.to_datetime(it["shipping_limit_date"])
    o = o.join(it, on="order_id")

    # Reseña: algunos pedidos tienen más de una -> se toma la más reciente
    rv = d["reviews"].copy()
    rv["review_answer_timestamp"] = pd.to_datetime(rv["review_answer_timestamp"])
    multi = rv.order_id.duplicated(keep=False).sum()
    log(f"- Reseñas asociadas a pedidos con más de una reseña: {multi} (se conserva la más reciente)")
    rv = rv.sort_values("review_answer_timestamp").drop_duplicates("order_id", keep="last")
    o = o.merge(rv[["order_id", "review_score"]], on="order_id", how="left")

    # Método de pago principal (el de mayor monto)
    pay = d["payments"].sort_values("payment_value").drop_duplicates("order_id", keep="last")
    o = o.merge(pay[["order_id", "payment_type", "payment_installments"]], on="order_id", how="left")

    # Métricas logísticas (solo pedidos entregados con fecha)
    delivered = (o.order_status == "delivered") & o.order_delivered_customer_date.notna()
    o["is_delivered"] = delivered
    o["delivery_days"] = (
        (o.order_delivered_customer_date - o.order_purchase_timestamp).dt.total_seconds() / 86400
    ).where(delivered).round(2)
    o["estimated_days"] = (
        (o.order_estimated_delivery_date - o.order_purchase_timestamp).dt.total_seconds() / 86400
    ).round(2)
    # Atraso = se entregó un día calendario posterior a la fecha estimada
    o["days_late"] = (
        (o.order_delivered_customer_date.dt.normalize() - o.order_estimated_delivery_date).dt.days
    ).where(delivered)
    o["is_late"] = (o["days_late"] > 0).where(delivered)
    # Responsabilidad del vendedor: despachó al correo después del límite pactado
    o["seller_late_handoff"] = (o.order_delivered_carrier_date > o.shipping_limit_date).where(
        delivered & o.order_delivered_carrier_date.notna()
    )

    # Recompra: ¿el cliente volvió a comprar después de este pedido?
    o = o.sort_values("order_purchase_timestamp")
    o["customer_order_seq"] = o.groupby("customer_unique_id").cumcount() + 1
    total = o.groupby("customer_unique_id").order_id.transform("count")
    o["customer_repurchased"] = total > 1

    # Período de análisis
    before = len(o)
    o = o[(o.order_purchase_timestamp >= PERIOD_START) & (o.order_purchase_timestamp <= PERIOD_END)]
    log(
        f"- Período de análisis: ene-2017 a ago-2018 (meses completos). "
        f"Se excluyen {before - len(o):,} pedidos de meses incompletos"
    )

    o["order_date"] = o.order_purchase_timestamp.dt.date
    o["order_month"] = o.order_purchase_timestamp.dt.to_period("M").astype(str)
    o["review_bucket"] = pd.cut(
        o.review_score, [0, 2, 3, 5], labels=["Negativa (1-2)", "Neutra (3)", "Positiva (4-5)"]
    ).astype(str).replace("nan", "Sin reseña")
    return o


def build_items(d: dict[str, pd.DataFrame], orders: pd.DataFrame) -> pd.DataFrame:
    p = d["products"].merge(d["translation"], on="product_category_name", how="left")
    nulls = p.product_category_name.isna().sum()
    log(f"- Productos sin categoría: {nulls} (se etiquetan como 'sin_categoria')")
    p["category"] = (
        p.product_category_name_english.fillna(p.product_category_name).fillna("sin_categoria")
    )
    it = d["items"].merge(p[["product_id", "category"]], on="product_id", how="left")
    it = it[it.order_id.isin(orders.order_id)]
    return it[["order_id", "order_item_id", "product_id", "seller_id", "category", "price", "freight_value"]]


def main() -> None:
    log("## Fuentes\n")
    d = load()
    log("\n## Validaciones y decisiones\n")
    orders = build_orders(d)
    items = build_items(d, orders)
    sellers = d["sellers"][["seller_id", "seller_city", "seller_state"]]

    cols = [
        "order_id", "customer_unique_id", "customer_city", "customer_state", "order_status",
        "order_purchase_timestamp", "order_date", "order_month", "items", "product_value",
        "freight_value", "payment_type", "payment_installments", "is_delivered", "delivery_days",
        "estimated_days", "days_late", "is_late", "seller_late_handoff", "review_score",
        "review_bucket", "customer_order_seq", "customer_repurchased",
    ]
    orders[cols].to_csv(OUT / "orders.csv", index=False)
    items.to_csv(OUT / "order_items.csv", index=False)
    sellers.to_csv(OUT / "sellers.csv", index=False)

    log("\n## Salida\n")
    log(f"- `orders.csv`: {len(orders):,} pedidos (1 fila por pedido)")
    log(f"- `order_items.csv`: {len(items):,} ítems")
    log(f"- `sellers.csv`: {len(sellers):,} vendedores")

    (ROOT / "reports").mkdir(exist_ok=True)
    (ROOT / "reports" / "calidad_de_datos.md").write_text(
        "# Reporte de calidad de datos\n\n" + "\n".join(quality_log) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
