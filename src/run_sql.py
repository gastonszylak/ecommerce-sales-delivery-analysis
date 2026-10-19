"""
Carga las tablas limpias en una base SQLite y ejecuta las consultas de sql/analysis.sql.
Los resultados se guardan en reports/resultados_sql.md.

Uso:  python src/run_sql.py
"""
import re
import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"
DB = ROOT / "data" / "olist.db"

BOOL_COLS = ["is_delivered", "is_late", "seller_late_handoff", "customer_repurchased"]


def build_db() -> sqlite3.Connection:
    DB.unlink(missing_ok=True)
    con = sqlite3.connect(DB)
    orders = pd.read_csv(PROC / "orders.csv")
    for c in BOOL_COLS:  # True/False/NaN -> 1/0/NULL
        orders[c] = orders[c].map({True: 1, False: 0, "True": 1, "False": 0})
    orders.to_sql("orders", con, index=False)
    pd.read_csv(PROC / "order_items.csv").to_sql("order_items", con, index=False)
    pd.read_csv(PROC / "sellers.csv").to_sql("sellers", con, index=False)
    return con


def main() -> None:
    con = build_db()
    sql = (ROOT / "sql" / "analysis.sql").read_text(encoding="utf-8")
    blocks = re.split(r"^-- name: (\S+)\s*$", sql, flags=re.M)[1:]
    out = ["# Resultados de las consultas SQL\n",
           "Generado por `src/run_sql.py` a partir de `sql/analysis.sql`.\n"]
    for name, query in zip(blocks[::2], blocks[1::2]):
        df = pd.read_sql_query(query, con)
        out.append(f"## {name}\n\n{df.to_markdown(index=False)}\n")
        print(f"\n== {name}\n{df.to_string(index=False)}")
    (ROOT / "reports" / "resultados_sql.md").write_text("\n".join(out), encoding="utf-8")
    con.close()


if __name__ == "__main__":
    main()
