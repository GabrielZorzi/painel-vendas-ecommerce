from pathlib import Path

import pandas as pd

from painel_vendas_ecommerce.pipeline import save_tables


def test_save_tables_writes_one_csv_per_table(tmp_path: Path) -> None:
    tables = {
        "fact_orders": pd.DataFrame(
            {"order_id": ["o1"], "purchase_date": pd.to_datetime(["2017-03-10"])}
        ),
        "fact_order_items": pd.DataFrame({"order_id": ["o1"], "price": [10.0]}),
    }

    paths = save_tables(tables, out_dir=tmp_path / "processed")

    assert sorted(p.name for p in paths) == ["fact_order_items.csv", "fact_orders.csv"]
    saved = pd.read_csv(tmp_path / "processed" / "fact_orders.csv")
    assert saved.loc[0, "purchase_date"] == "2017-03-10"
