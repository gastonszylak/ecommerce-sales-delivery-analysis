"""
Exporta las tablas que consume el tablero de Power BI (data/powerbi/).
Booleanos como 1/0 (más simples de sumar en DAX) y tramos de atraso con su orden.

Uso:  python src/export_powerbi.py   (después de src/clean.py)
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"
OUT = ROOT / "data" / "powerbi"
OUT.mkdir(parents=True, exist_ok=True)

BUCKETS = ["A tiempo", "1-3 días tarde", "4-7 días tarde", "8-14 días tarde", "+14 días tarde"]


def to_int(s: pd.Series) -> pd.Series:
    return s.map({True: 1, False: 0, "True": 1, "False": 0}).astype("Int64")


def main() -> None:
    o = pd.read_csv(PROC / "orders.csv")
    o["valid"] = (~o.order_status.isin(["canceled", "unavailable"])).astype(int)
    for c in ["is_delivered", "is_late", "seller_late_handoff", "customer_repurchased"]:
        o[c] = to_int(o[c])
    o["delay_bucket"] = pd.cut(o.days_late, [-999, 0, 3, 7, 14, 999], labels=BUCKETS).astype(str).replace("nan", "")
    o["delay_bucket_order"] = o.delay_bucket.map({b: i for i, b in enumerate(BUCKETS)}).astype("Int64")
    o["first_order"] = (o.customer_order_seq == 1).astype(int)
    cols = ["order_id", "customer_unique_id", "customer_state", "order_status", "valid", "order_date",
            "product_value", "freight_value", "payment_type", "is_delivered", "delivery_days", "days_late",
            "is_late", "delay_bucket", "delay_bucket_order", "seller_late_handoff", "review_score",
            "first_order", "customer_repurchased"]
    o[cols].to_csv(OUT / "pbi_orders.csv", index=False)

    it = pd.read_csv(PROC / "order_items.csv")
    it[["order_id", "seller_id", "category", "price", "freight_value"]].to_csv(OUT / "pbi_order_items.csv", index=False)
    print(f"pbi_orders.csv: {len(o):,} filas | pbi_order_items.csv: {len(it):,} filas")


if __name__ == "__main__":
    main()
